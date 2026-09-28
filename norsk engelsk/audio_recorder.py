"""Microphone capture only; no local speech model."""
import threading
import queue

LANGUAGE_CODES = dict(zip(
    ('English', 'Arabic', 'Chinese (Simplified)', 'Czech', 'Danish', 'Dutch',
     'Finnish', 'French', 'German', 'Greek', 'Hindi', 'Hungarian', 'Italian',
     'Japanese', 'Korean', 'Norwegian', 'Polish', 'Portuguese', 'Romanian',
     'Russian', 'Spanish', 'Swedish', 'Thai', 'Turkish', 'Ukrainian', 'Vietnamese'),
    ('en','ar','zh','cs','da','nl','fi','fr','de','el','hi','hu','it','ja','ko',
     'no','pl','pt','ro','ru','es','sv','th','tr','uk','vi')))


class Recorder:
    """User-controlled mono recorder. Constructing it never opens a microphone."""
    RATE = 16000
    MAX_SECONDS = None

    def __init__(self):
        self.stream = None
        self.chunks = []
        self.samples = 0
        self.full = threading.Event()
        self.overflow = False
        self.levels = queue.SimpleQueue()

    def start(self, device=None):
        import sounddevice as sd
        self.chunks = []
        self.samples = 0
        self.full.clear()
        self.overflow = False
        self.levels = queue.SimpleQueue()

        def capture(data, frames, timestamp, status):
            self.overflow |= bool(status)
            remaining = (self.RATE * self.MAX_SECONDS - self.samples
                         if self.MAX_SECONDS is not None else len(data))
            if remaining > 0:
                chunk = data[:remaining, 0].copy()
                self.chunks.append(chunk)
                self.samples += len(chunk)
                import numpy as np
                level = float(20*np.log10(max(1e-6, float(np.sqrt(np.mean(chunk**2))))))
                self.levels.put((level, level))
            if self.MAX_SECONDS is not None and self.samples >= self.RATE * self.MAX_SECONDS:
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
