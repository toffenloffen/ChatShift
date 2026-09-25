"""Explicit local microphone test with real input/output meters; no saved audio."""
import contextlib
import queue
import threading
import time
import tkinter as tk
from tkinter import ttk


class MicMonitor:
    def __init__(self, voice, parent):
        self.voice, self.app = voice, voice.app
        self.thread = None
        self.stop_event = threading.Event()
        self.options = (False, False)
        self.reading = (-120., -120.)
        self.levels = queue.SimpleQueue()
        self.error = None
        self.listen = tk.BooleanVar(value=False)
        surface = parent.cget('background')
        row = tk.Frame(parent, bg=surface)
        row.pack(fill='x', pady=6)
        self.button = ttk.Button(row, text='Mic Test', command=self.toggle)
        self.button.pack(side='left')
        self.listen_button = ttk.Checkbutton(row, text='Listen (headphones)', variable=self.listen)
        self.listen_button.pack(side='left', padx=10)
        self.meter = tk.Canvas(parent, height=76, bg=surface, highlightthickness=0)
        self.meter.pack(fill='x')
        self.meter.bind('<Configure>', lambda e: self.draw())
        self.label = ttk.Label(parent, text='Input = microphone. Output = audio sent to speech recognition.')
        self.label.pack(anchor='w')

    def draw(self):
        w = self.meter.winfo_width()
        self.meter.delete('all')
        for i, (name, level, color) in enumerate(zip(('Input', 'Output'), self.reading, ('#7e9fc5', '#3bd9a3'))):
            y = 8+i*34
            self.meter.create_text(4, y+10, text=name, anchor='w', fill='white')
            start, end = 60, max(61, w-80)
            self.meter.create_rectangle(start, y, end, y+20, fill='#2a2e42', outline='')
            x = start + max(0, min(1, (level+90)/90))*(end-start)
            self.meter.create_rectangle(start, y, x, y+20, fill=color, outline='')
            self.meter.create_text(w-5, y+10, text='Silent' if level <= -90 else f'{level:.0f} dBFS', anchor='e', fill='white')

    def toggle(self):
        if self.thread:
            self.stop_event.set()
            self.button.configure(text='Stopping…', state='disabled')
            return
        if self.app.busy:
            self.label.configure(text='Wait for the current recording or translation to finish.')
            return
        self.options = (self.voice.noise_enabled.get(), self.listen.get())
        self.stop_event.clear()
        self.levels = queue.SimpleQueue()
        self.error = None
        self.app.busy = True
        self.voice.device_picker.configure(state='disabled')
        self.button.configure(text='Stop Test')
        self.label.configure(text='Loading filter and starting microphone…')
        device = self.voice.devices.get(self.voice.device.get())
        self.thread = threading.Thread(target=self.run, args=(device,), daemon=True)
        self.thread.start()

    def run(self, device):
        processor = None
        try:
            import numpy as np
            import sounddevice as sd
            from audio_cleanup import SpeechFilter, audio_level, get_model
            if self.options[0]:
                get_model()  # Finish setup before opening the microphone.
            processor = SpeechFilter()
            with contextlib.ExitStack() as stack:
                incoming = stack.enter_context(sd.InputStream(device=device, samplerate=processor.RATE,
                    blocksize=processor.FRAME, channels=1, dtype='float32', latency='high'))
                output = None
                deadline = time.monotonic()+120
                while not self.stop_event.is_set() and time.monotonic()<deadline:
                    data, overflow = incoming.read(processor.FRAME)
                    enabled, listen = self.options
                    out, level, _ = processor.process(data[:, 0], enabled)
                    self.levels.put((audio_level(data[:, 0]), level))
                    if listen and output is None:
                        output = stack.enter_context(sd.OutputStream(samplerate=processor.RATE,
                            blocksize=processor.FRAME, channels=1, dtype='float32', latency='high'))
                    if output is not None:
                        output.write((out if listen else np.zeros_like(out)).reshape(-1, 1))
                    if overflow:
                        raise RuntimeError('Microphone buffer overflow. Stop other audio tests and try again.')
        except Exception as exc:
            self.error = f'Mic Test stopped: {exc}'
        finally:
            if processor:
                processor.close()

    def poll(self):
        if not self.thread:
            return
        self.options = (self.voice.noise_enabled.get(), self.listen.get())
        # Peak of actual per-frame RMS readings since last paint: short claps
        # remain visible, and are never mistaken for speech-detector confidence.
        readings = []
        while not self.levels.empty():
            readings.append(self.levels.get())
        if readings:
            self.reading = tuple(max(r[i] for r in readings) for i in (0, 1))
        if not self.thread.is_alive():
            self.thread = None
            self.app.busy = False
            self.voice.device_picker.configure(state='readonly')
            self.button.configure(text='Mic Test', state='normal')
            self.reading = (-120., -120.)
            self.label.configure(text=self.error or 'Test stopped. No audio was saved.')
        else:
            self.label.configure(text='DeepFilterNet3 on · compare Input and Output' if self.options[0]
                                 else 'Noise suppression off · Output matches Input')
        self.draw()

    def stop(self):
        self.stop_event.set()
