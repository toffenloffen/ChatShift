"""A user-started speech quality test; never sends text or presses game keys."""
import queue
import threading
import time
import tkinter as tk
from tkinter import ttk
from local_voice import LocalTranscriber, Recorder


class VoiceTrial:
    def __init__(self, app):
        self.app = app
        self.closed = False
        self.recording = False
        self.model = None
        self.recorder = Recorder()
        self.events = queue.Queue()
        self.cancel = threading.Event()
        self.owns_busy = False
        self.window = tk.Toplevel(app.root)
        self.window.title('ChatShift · Local voice test')
        self.window.geometry('690x570')
        self.window.configure(bg='#10111b')
        body = ttk.Frame(self.window, padding=20)
        body.pack(fill='both', expand=True)
        ttk.Label(body, text='Try your microphone', font=('Segoe UI', 18, 'bold')).pack(anchor='w')
        ttk.Label(body, text='Record a short sentence, then check what the AI heard.\nThis test does not send anything to your game.').pack(anchor='w', pady=8)
        self.status = tk.StringVar(value='Loading local speech model… First setup downloads the model.')
        ttk.Label(body, textvariable=self.status, wraplength=640).pack(anchor='w', pady=8)
        self.devices = [None]
        names = ['Windows default microphone']
        try:
            from microphones import list_microphones
            choices = list_microphones()
            self.devices, names = list(choices.values()), list(choices)
        except Exception:
            self.status.set('Could not list microphones. Check your audio devices.')
        self.device = ttk.Combobox(body, values=names, state='readonly')
        self.device.current(0)
        self.device.pack(fill='x', pady=8)
        self.button = ttk.Button(body, text='Start recording', command=self.toggle, state='disabled')
        self.button.pack(anchor='w', pady=8)
        ttk.Label(body, text='What the microphone heard').pack(anchor='w')
        self.original = tk.Text(body, height=4, wrap='word', bg='#1b1e2e', fg='#f2f3ff', insertbackground='white')
        self.original.pack(fill='x', pady=5)
        ttk.Label(body, text='Luna translation · review only').pack(anchor='w')
        self.output = tk.Text(body, height=4, wrap='word', bg='#1b1e2e', fg='#f2f3ff', insertbackground='white')
        self.output.pack(fill='x', pady=5)
        ttk.Label(body, text='Audio stays on this PC. Recognized text goes to Luna when languages differ.\nRecording stops automatically after 30 seconds.', wraplength=640).pack(anchor='w', pady=8)
        self.window.protocol('WM_DELETE_WINDOW', self.close)
        self.timer = self.window.after(50, self.poll)
        threading.Thread(target=self.load, daemon=True).start()

    def load(self):
        try:
            model = getattr(self.app, 'speech_model', None) or LocalTranscriber()
            if not self.cancel.is_set():
                self.events.put(('model', model))
        except Exception:
            self.events.put(('error', 'Speech model could not load. Check internet access and free disk space, then reopen this test.'))

    def toggle(self):
        if self.recording:
            self.recording = False
            self.button.configure(state='disabled', text='Processing…')
            try:
                audio = self.recorder.stop()
            except ValueError as exc:
                self.finish(str(exc))
                return
            self.status.set('Recognizing speech on this PC…')
            threading.Thread(target=self.process, args=(audio,), daemon=True).start()
            return
        if self.app.busy:
            self.status.set('Wait for the current translation to finish.')
            return
        self.source = self.app.source_language.get()
        self.target = self.app.language.get()
        if self.source != self.target and self.app.local is None:
            self.status.set('Wait for Luna to be ready, or choose matching languages for dictation only.')
            return
        try:
            self.recorder.start(self.devices[self.device.current()])
        except ValueError as exc:
            self.status.set(str(exc))
            return
        self.app.busy = self.owns_busy = True
        self.recording = True
        self.device.configure(state='disabled')
        self.button.configure(text='Stop recording')
        self.original.delete('1.0', 'end')
        self.output.delete('1.0', 'end')
        self.status.set(f'Listening · {self.source} → {self.target}. Click Stop recording when finished.')

    def process(self, audio):
        started = time.perf_counter()
        try:
            text = self.model.transcribe(audio, self.source)
            if self.cancel.is_set():
                return
            self.events.put(('original', text))
            recognized = time.perf_counter() - started
            translated = text if self.source == self.target else self.app.local.translate(
                text, target_language=self.target, source_language=self.source)
            if not self.cancel.is_set():
                self.events.put(('output', translated))
                self.events.put(('done', f'Ready · recognition {recognized:.1f}s · total {time.perf_counter()-started:.1f}s. Nothing sent.'))
        except Exception as exc:
            self.events.put(('error', str(exc) if isinstance(exc, ValueError) else 'Voice processing failed. Try another short recording.'))
        finally:
            self.events.put(('released', None))

    def finish(self, message):
        self.status.set(message)
        self.device.configure(state='readonly')
        self.button.configure(text='Start recording', state='normal' if self.model else 'disabled')
        if self.owns_busy:
            self.app.busy = self.owns_busy = False

    def poll(self):
        if self.closed:
            return
        if self.recording and self.recorder.full.is_set():
            self.toggle()
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == 'model':
                    self.model = self.app.speech_model = value
                    self.finish('Ready. Click Start recording and speak in your selected source language.')
                elif kind in ('error', 'done'):
                    self.finish(value)
                elif kind in ('original', 'output'):
                    getattr(self, kind).insert('1.0', value)
        except queue.Empty:
            pass
        self.timer = self.window.after(50, self.poll)

    def close(self):
        self.cancel.set()
        self.recorder.close()
        self.recorder.chunks.clear()
        self.closed = True
        self.window.after_cancel(self.timer)
        self.window.destroy()
        # Do not allow another translation to race with an in-flight Luna call.
        if self.owns_busy and not self.recording:
            self.app.root.after(50, self.wait_release)
        elif self.owns_busy:
            self.app.busy = self.owns_busy = False

    def wait_release(self):
        if self.app.closing:
            return
        try:
            while True:
                kind, _ = self.events.get_nowait()
                if kind == 'released':
                    self.app.busy = self.owns_busy = False
                    return
        except queue.Empty:
            pass
        self.app.root.after(100, self.wait_release)


def show_voice_trial(app):
    existing = getattr(app, 'voice_trial', None)
    if existing is not None and not existing.closed:
        existing.window.lift()
        return
    app.voice_trial = VoiceTrial(app)
