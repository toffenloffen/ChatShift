"""User-started paired recording using the same streaming speech filter."""
import threading
import queue
import numpy as np
from audio_cleanup import SpeechFilter, audio_level, get_model

class FilteredRecorder:
    def __init__(self):
        self.full=threading.Event(); self.stop_event=threading.Event()
        self.chunks=[]; self.outputs=[]; self.levels=queue.SimpleQueue()
        self.thread=None; self.error=None

    def start(self, device=None, enabled=False):
        import sounddevice as sd
        if enabled: get_model()
        self.processor=SpeechFilter(); self.enabled=enabled
        self.chunks=[]; self.outputs=[]; self.levels=queue.SimpleQueue()
        self.error=None; self.full.clear(); self.stop_event.clear()
        try:
            self.stream=sd.InputStream(device=device,samplerate=48000,blocksize=512,channels=1,dtype='float32',latency='high')
            self.stream.start()
        except Exception as exc:
            self.processor.close()
            raise ValueError(f'Could not open microphone: {exc}') from exc
        self.thread=threading.Thread(target=self.run,daemon=True); self.thread.start()

    def run(self):
        try:
            while not self.stop_event.is_set() and len(self.chunks)*512 < 30*48000:
                data,overflow=self.stream.read(512)
                if overflow: raise ValueError('Audio buffer overflow. Try closing other microphone tests.')
                raw=data[:,0].copy(); out,level,_=self.processor.process(raw,self.enabled)
                self.chunks.append(raw); self.outputs.append(out)
                self.levels.put((audio_level(raw),level))
        except Exception as exc:
            self.error=str(exc)
        finally:
            self.stream.stop(); self.stream.close(); self.full.set()

    def stop(self):
        import soxr
        self.stop_event.set()
        if self.thread: self.thread.join(timeout=3)
        if self.thread and self.thread.is_alive(): raise ValueError('Microphone is still stopping. Close the test before retrying.')
        try:
            if self.error: raise ValueError(self.error)
            if not self.chunks: raise ValueError('No audio recorded. Try again.')
            if self.enabled:
                for _ in range(SpeechFilter.TAIL//512):
                    self.outputs.append(self.processor.process(np.zeros(512,np.float32),True)[0])
            raw=soxr.resample(np.concatenate(self.chunks),48000,16000).astype(np.float32)
            processed=soxr.resample(np.concatenate(self.outputs),48000,16000).astype(np.float32)
            return raw,processed
        finally: self.processor.close()

    def close(self):
        self.stop_event.set()
        if self.thread: self.thread.join(timeout=3)
        if not self.thread or not self.thread.is_alive():
            if hasattr(self,'processor'): self.processor.close()
        self.chunks.clear(); self.outputs.clear()
