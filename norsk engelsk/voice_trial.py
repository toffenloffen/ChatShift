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
        from filtered_recorder import FilteredRecorder
        self.recorder = FilteredRecorder()
        self.events = queue.Queue()
        self.cancel = threading.Event()
        self.owns_busy = False
        self.raw_audio = self.filtered_audio = None
        self.window = tk.Toplevel(app.root)
        self.window.title('ChatShift · Local voice test')
        self.window.geometry('690x800')
        self.window.configure(bg='#10111b')
        body = ttk.Frame(self.window, padding=20)
        body.pack(fill='both', expand=True)
        ttk.Label(body, text='Try your microphone', font=('Segoe UI', 18, 'bold')).pack(anchor='w')
        ttk.Label(body, text='Record a short sentence, then check what the AI heard.\nThis test does not send anything to your game.').pack(anchor='w', pady=8)
        self.status = tk.StringVar(value='Ready. Start recording, speak, then Stop recording to see both texts.')
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
        selected = app.voice.devices.get(app.voice.device.get())
        if selected in self.devices:
            self.device.current(self.devices.index(selected))
        self.device.pack(fill='x', pady=8)
        self.button = ttk.Button(body, text='Start recording', command=self.toggle)
        self.button.pack(anchor='w', pady=8)
        self.level = tk.Canvas(body, height=76, bg='#182334', highlightthickness=0)
        self.level.pack(fill='x', pady=4)
        self.reading = (-120., -120.)
        self.level.bind('<Configure>', lambda e: self.draw_levels())
        self.noise_option = ttk.Checkbutton(body, text='Noise suppression (DeepFilterNet3)', variable=app.voice.noise_enabled, command=app.voice.noise_changed)
        self.noise_option.pack(anchor='w')
        playback = ttk.Frame(body)
        playback.pack(fill='x', pady=8)
        self.play_original = ttk.Button(playback, text='Listen: original', state='disabled', command=lambda: self.play(False))
        self.play_original.pack(side='left')
        self.play_filtered = ttk.Button(playback, text='Listen: processed', state='disabled', command=lambda: self.play(True))
        self.play_filtered.pack(side='left', padx=8)
        ttk.Button(playback, text='Stop playback', command=self.stop_playback).pack(side='left')
        ttk.Label(body, text='What the microphone heard').pack(anchor='w')
        self.original = tk.Text(body, height=4, wrap='word', bg='#1b1e2e', fg='#f2f3ff', insertbackground='white')
        self.original.pack(fill='x', pady=5)
        ttk.Label(body, text='Luna translation · review only').pack(anchor='w')
        self.output = tk.Text(body, height=4, wrap='word', bg='#1b1e2e', fg='#f2f3ff', insertbackground='white')
        self.output.pack(fill='x', pady=5)
        ttk.Label(body, text='Audio stays on this PC. Recognized text goes to Luna when languages differ.\nRecording stops automatically after 30 seconds.', wraplength=640).pack(anchor='w', pady=8)
        self.window.protocol('WM_DELETE_WINDOW', self.close)
        self.timer = self.window.after(50, self.poll)

    def draw_levels(self):
        from mic_monitor import MicMonitor
        # Share only the meter painter, not another test or recording control.
        painter = type('Meter', (), {})()
        painter.meter, painter.reading = self.level, self.reading
        MicMonitor.draw(painter)

    def stop_playback(self):
        import sounddevice as sd
        sd.stop()

    def play(self, filtered):
        import sounddevice as sd
        audio = self.filtered_audio if filtered else self.raw_audio
        if audio is not None and not self.recording:
            try:
                sd.play(audio, Recorder.RATE)
            except Exception:
                self.status.set('Could not play audio. Check your output device.')

    def toggle(self):
        if self.recording:
            self.recording = False
            self.button.configure(state='disabled', text='Processing…')
            try:
                audio, cleaned = self.recorder.stop()
            except ValueError as exc:
                self.finish(str(exc))
                return
            self.status.set('Processing audio on this PC…')
            threading.Thread(target=self.process, args=(audio, cleaned), daemon=True).start()
            return
        monitor = getattr(self.app.voice, 'monitor', None)
        if monitor is not None and monitor.thread is not None:
            monitor.stop()
            self.button.configure(state='disabled')
            self.status.set('Stopping Mic Test before recording...')
            self.window.after(50, self.wait_for_monitor)
            return
        if self.app.busy:
            self.status.set('Wait for the current translation to finish.')
            return
        self.session_noise = self.app.voice.noise_options()
        self.session_text = True
        self.source = self.app.source_language.get()
        self.target = self.app.language.get()
        try:
            self.stop_playback()
            self.recorder.start(self.devices[self.device.current()], self.session_noise['enabled'])
        except ValueError as exc:
            self.status.set(str(exc))
            return
        self.app.busy = self.owns_busy = True
        self.recording = True
        self.device.configure(state='disabled')
        self.noise_option.configure(state='disabled')
        self.play_original.configure(state='disabled')
        self.play_filtered.configure(state='disabled')
        self.raw_audio = self.filtered_audio = None
        self.button.configure(text='Stop recording')
        self.original.delete('1.0', 'end')
        self.output.delete('1.0', 'end')
        self.status.set(f'Listening · {self.source} → {self.target}. Click Stop recording when finished.')

    def wait_for_monitor(self):
        if self.closed:
            return
        monitor = getattr(self.app.voice, 'monitor', None)
        if monitor is not None and monitor.thread is not None:
            self.window.after(50, self.wait_for_monitor)
            return
        self.button.configure(state='normal')
        self.toggle()

    def process(self, audio, cleaned=None):
        started = time.perf_counter()
        try:
            from audio_cleanup import clean_audio
            if cleaned is None:
                cleaned = clean_audio(audio, **self.session_noise)
            if self.cancel.is_set():
                return
            self.events.put(('audio', (audio, cleaned)))
            if not self.session_text:
                state = 'on' if self.session_noise['enabled'] else 'off'
                self.events.put(('done', f'Ready to listen. Noise suppression: {state}. Nothing sent.'))
                return
            self.model = getattr(self.app, 'speech_model', None) or LocalTranscriber()
            text = self.model.transcribe(cleaned, self.source)
            if self.cancel.is_set():
                return
            self.events.put(('original', text))
            recognized = time.perf_counter() - started
            if self.source != self.target and self.app.local is None:
                self.events.put(('done', 'Recording and speech recognition finished. Luna is not connected; translation skipped.'))
                return
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
        self.button.configure(text='Start recording', state='normal')
        self.noise_option.configure(state='normal')
        self.draw_levels()
        if self.raw_audio is not None:
            self.play_original.configure(state='normal')
            self.play_filtered.configure(state='normal')
        if self.owns_busy:
            self.app.busy = self.owns_busy = False

    def poll(self):
        if self.closed:
            return
        readings = []
        while not self.recorder.levels.empty():
            readings.append(self.recorder.levels.get())
        if readings:
            self.reading = tuple(max(r[i] for r in readings) for i in (0, 1))
            self.draw_levels()
        if self.recording and self.recorder.full.is_set():
            self.toggle()
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == 'audio':
                    self.raw_audio, self.filtered_audio = value
                elif kind in ('error', 'done'):
                    self.finish(value)
                elif kind in ('original', 'output'):
                    getattr(self, kind).insert('1.0', value)
        except queue.Empty:
            pass
        self.timer = self.window.after(50, self.poll)

    def close(self):
        self.cancel.set()
        self.stop_playback()
        self.raw_audio = self.filtered_audio = None
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
        existing.window.deiconify()
        existing.window.lift()
        existing.window.focus_force()
        return
    app.voice_trial = VoiceTrial(app)
