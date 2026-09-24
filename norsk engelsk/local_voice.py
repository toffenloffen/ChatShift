"""Optional CPU speech recognition. Audio stays in memory and on this computer."""
from pathlib import Path
import threading

LANGUAGE_CODES = dict(zip(
    ('English', 'Arabic', 'Chinese (Simplified)', 'Czech', 'Danish', 'Dutch',
     'Finnish', 'French', 'German', 'Greek', 'Hindi', 'Hungarian', 'Italian',
     'Japanese', 'Korean', 'Norwegian', 'Polish', 'Portuguese', 'Romanian',
     'Russian', 'Spanish', 'Swedish', 'Thai', 'Turkish', 'Ukrainian', 'Vietnamese'),
    ('en','ar','zh','cs','da','nl','fi','fr','de','el','hi','hu','it','ja','ko',
     'no','pl','pt','ro','ru','es','sv','th','tr','uk','vi')))
MODEL_DIRECTORY = Path(__file__).resolve().parents[1] / '.models' / 'voice'


class LocalTranscriber:
    def __init__(self):
        from faster_whisper import WhisperModel
        self.model = WhisperModel('small', device='cpu', compute_type='int8',
                                  cpu_threads=4, num_workers=1,
                                  download_root=str(MODEL_DIRECTORY))

    def transcribe(self, audio, language):
        if language not in LANGUAGE_CODES:
            raise ValueError('Choose a supported spoken language.')
        segments, _ = self.model.transcribe(audio, language=LANGUAGE_CODES[language],
            beam_size=3, vad_filter=True, condition_on_previous_text=False,
            vad_parameters={'min_silence_duration_ms': 350})
        text = ' '.join(segment.text.strip() for segment in segments).strip()
        if not text:
            raise ValueError('No speech detected. Check your microphone and try again.')
        return text


class Recorder:
    """Bounded mono recorder. Constructing it never opens a microphone."""
    RATE = 16000
    MAX_SECONDS = 30

    def __init__(self):
        self.stream = None
        self.chunks = []
        self.samples = 0
        self.full = threading.Event()
        self.overflow = False

    def start(self, device=None):
        import sounddevice as sd
        self.chunks = []
        self.samples = 0
        self.full.clear()
        self.overflow = False

        def capture(data, frames, timestamp, status):
            self.overflow |= bool(status)
            remaining = self.RATE * self.MAX_SECONDS - self.samples
            if remaining > 0:
                chunk = data[:remaining, 0].copy()
                self.chunks.append(chunk)
                self.samples += len(chunk)
            if self.samples >= self.RATE * self.MAX_SECONDS:
                self.full.set()
                raise sd.CallbackStop

        try:
            self.stream = sd.InputStream(device=device, samplerate=self.RATE,
                channels=1, dtype='float32', callback=capture)
            self.stream.start()
        except Exception:
            self.close()
            raise ValueError('Could not open this microphone. Check Windows microphone access or choose another input.') from None

    def stop(self):
        import numpy as np
        self.close()
        chunks, self.chunks = self.chunks, []
        if self.overflow:
            raise ValueError('The recording was interrupted. Try again when the computer is less busy.')
        if self.samples < self.RATE // 3 or not chunks:
            raise ValueError('Recording too short. Speak a short sentence and try again.')
        return np.concatenate(chunks)

    def close(self):
        if self.stream is not None:
            stream, self.stream = self.stream, None
            try:
                stream.stop()
            finally:
                stream.close()
