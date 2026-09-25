"""Shared streaming DeepFilterNet3 processing for monitoring and transcription."""
import threading
import numpy as np

_model = None
_model_lock = threading.Lock()


def get_model():
    global _model
    with _model_lock:
        if _model is None:
            from deepfilter_stream import DeepFilterModel
            _model = DeepFilterModel(intra_op_num_threads=1, inter_op_num_threads=1)
    return _model


def audio_level(audio):
    """Actual RMS level in dBFS, measured from samples, not model confidence."""
    return float(20*np.log10(max(1e-6, float(np.sqrt(np.mean(np.asarray(audio, dtype=np.float64)**2))))))


class SpeechFilter:
    RATE = 48000
    FRAME = 512
    # Keep the entire delayed tail for transcription rather than guessing an offset.
    TAIL = 8 * FRAME

    def __init__(self):
        self.stream = None

    def close(self):
        self.stream = None

    def process(self, source, enabled=True, strength=100, threshold=-50):
        source = np.asarray(source, dtype=np.float32).reshape(-1)
        if len(source) != self.FRAME:
            raise ValueError('Incorrect audio frame size.')
        if enabled:
            if self.stream is None:
                self.stream = get_model().new_stream()
            audio = self.stream.process_frame(source)
        else:
            self.stream = None
            audio = source.copy()
        audio = np.clip(audio, -1, 1).astype(np.float32)
        level = audio_level(audio)
        return audio, level, level > -60


def clean_audio(audio, enabled=False, strength=100, threshold=-50, apply_gate=False):
    # Legacy threshold/strength settings intentionally no longer gate speech.
    if not enabled:
        return audio
    source = np.asarray(audio, dtype=np.float32)
    if not source.size:
        return source.copy()
    import soxr
    processor = SpeechFilter()
    try:
        up = soxr.resample(source, 16000, processor.RATE).astype(np.float32)
        padded = np.pad(up, (0, (-len(up) % processor.FRAME)+processor.TAIL))
        filtered = np.concatenate([processor.process(frame)[0]
                                   for frame in padded.reshape(-1, processor.FRAME)])
        # Leading algorithmic delay and trailing samples are retained. Whisper
        # accepts variable lengths; trimming an assumed delay risks losing words.
        return soxr.resample(filtered, processor.RATE, 16000).astype(np.float32)
    except (ImportError, OSError, RuntimeError) as exc:
        raise ValueError('DeepFilterNet is unavailable. Run Install ChatShift.cmd or turn noise suppression off.') from exc
    finally:
        processor.close()
