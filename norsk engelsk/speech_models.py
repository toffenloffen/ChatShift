"""Selectable speech engines. Translation remains the existing Luna step."""
import threading
import numpy as np
from audio_recorder import Recorder

MODELS = {
    'realtime': ('GPT-Live · Experimental', 'Streams audio while you speak. ChatGPT account access required.'),
    'gpt_transcribe': ('GPT-Transcribe · Experimental', 'Transcribes recordings after Stop using your ChatGPT sign-in. Account access and usage limits apply.'),
    'small': ('Whisper Small · local', 'Runs on CPU. Downloads model files from Hugging Face on first use.'),
    'medium': ('Whisper Medium · local', 'Runs on CPU. Larger download and higher memory use than Small.'),
    'turbo': ('Whisper Large Turbo · local', 'Runs on CPU. Large download and high memory use; speed depends on your PC.'),
}


class ClipRecorder(Recorder):
    RATE = 48000

    def __init__(self, noise, cancel):
        super().__init__()
        self.noise, self.cancel = dict(noise), cancel
        self.keep_audio = False
        self.raw_chunks, self.filtered_chunks = [], []
        self.timings = {}
        self.audio = None

    def stop(self):
        self.audio = super().stop()
        return self

    def processed(self):
        import soxr
        from audio_cleanup import SpeechFilter
        if self.cancel.is_set():
            raise ValueError('Voice cancelled.')
        raw, self.audio = self.audio, None
        if raw is None:
            raise ValueError('No recording available.')
        if self.noise.get('enabled'):
            processor = SpeechFilter()
            try:
                padded = np.pad(raw, (0, (-len(raw) % 512) + processor.TAIL))
                output = []
                for frame in padded.reshape(-1, 512):
                    if self.cancel.is_set():
                        raise ValueError('Voice cancelled.')
                    output.append(processor.process(frame, True)[0])
                filtered = np.concatenate(output)
            finally:
                processor.close()
        else:
            filtered = raw
        if self.keep_audio:
            self.raw_chunks = [raw]
            self.filtered_chunks = [filtered]
        return soxr.resample(filtered, self.RATE, 16000).astype(np.float32)

    def playback(self):
        raw, filtered = self.raw_chunks, self.filtered_chunks
        self.raw_chunks, self.filtered_chunks = [], []
        return (np.concatenate(raw) if raw else np.empty(0, dtype=np.float32),
                np.concatenate(filtered) if filtered else np.empty(0, dtype=np.float32))

    def close(self):
        super().close()
        if self.cancel.is_set():
            self.audio = None
            self.raw_chunks.clear()
            self.filtered_chunks.clear()


class ClipTranscriber:
    def __init__(self, key):
        self.key = key
        self.engine = None
        self.lock = threading.Lock()
        self.status = ''

    def warm(self, language, noise):
        pass  # Never download model files merely by opening the app.

    def close(self):
        self.engine = None

    def recorder(self, language, noise, cancel):
        return ClipRecorder(noise, cancel)

    @property
    def account_status(self):
        if self.key == 'gpt_transcribe' and self.engine is not None:
            return 'GPT-Transcribe account used: ' + self.engine.plan + ' (reported by Codex).'
        return ''

    def transcribe(self, audio, language, cancel=None):
        try:
            return self._transcribe(audio, language, cancel)
        finally:
            self.status = ''

    def _transcribe(self, audio, language, cancel=None):
        cancel = cancel or threading.Event()
        self.status = 'Cleaning recorded audio…'
        samples = audio.processed()
        with self.lock:
            if cancel.is_set():
                raise ValueError('Voice cancelled.')
            if self.engine is None:
                self.status = ('Loading ' + MODELS[self.key][0] +
                    ('… First use downloads model files; large models can take minutes. Please wait.'
                     if self.key != 'gpt_transcribe' else '…'))
                try:
                    if self.key == 'gpt_transcribe':
                        from gpt_transcribe_voice import GPTTranscriber
                        self.engine = GPTTranscriber()
                    else:
                        from local_voice import LocalTranscriber
                        self.engine = LocalTranscriber(self.key)
                except Exception as exc:
                    raise ValueError(f'Could not load {MODELS[self.key][0]}: {exc}') from exc
            if cancel.is_set():
                raise ValueError('Voice cancelled.')
            self.status = 'Recognizing speech with ' + MODELS[self.key][0] + '…'
            result = self.engine.transcribe(samples, language, cancel=cancel)
            if cancel.is_set():
                raise ValueError('Voice cancelled.')
            return result


def create_model(key):
    if key not in MODELS:
        raise ValueError('Choose a speech model from the list.')
    if key == 'realtime':
        from realtime_adapter import RealtimeTranscriber
        return RealtimeTranscriber()
    return ClipTranscriber(key)


def get_model(app):
    key = app.voice.model_choice.get()
    if getattr(app, 'speech_model_key', None) != key or getattr(app, 'speech_model', None) is None:
        previous = getattr(app, 'speech_model', None)
        if previous:
            previous.close()
        app.speech_model = create_model(key)
        app.speech_model_key = key
    return app.speech_model
