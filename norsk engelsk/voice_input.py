"""Cloud dictation lifecycle and guarded, unsent insertion into the user's field."""
import queue
import threading
import time
import tkinter as tk
from tkinter import ttk
import windows_input as win
from keyboard_preview import KeyboardPreview, MousePreview, ShortcutDraft, highlighted_keys
from shortcuts import binding_label, validate_binding


def insert_draft(target, revision, text, owner, cancel, binding, send=False):
    """Insert at the caret. Auto-send requires opt-in and verified readback."""
    if not text.strip() or len(text) > 1000 or any(ord(c) < 32 for c in text):
        raise ValueError('Voice result is empty, too long, or contains unsupported control characters.')

    def check():
        if cancel.is_set() or win.last_input() != revision:
            raise ValueError('Input changed. Voice draft was not inserted.')
        win.check_focus(target)

    win.wait_release(target, cancel, binding=binding)
    check()
    import among_us_mode
    if among_us_mode.is_among_us(target):
        if len(text) > 100:
            raise ValueError('Voice draft exceeds the game chat limit. Say a shorter message.')
        keys = among_us_mode.encode_keys(target, text)
        for vk, modifiers in keys:
            check()
            among_us_mode.press(target, vk, cancel, modifiers)
        if send:
            time.sleep(.2)
            check()
            if among_us_mode.read_field(target) != text:
                raise ValueError('Could not verify the voice draft. Check it and send manually.')
    else:
        win.clipboard_write(text, owner)
        check()
        win.shortcut(target, ord('V'))
        if send:
            time.sleep(.03)
            check()
            if win.capture(target, owner, cancel, collapse=True, preserve_clipboard=True) != text:
                raise ValueError('Could not verify the voice draft. Check it and send manually.')
    if send:
        check()
        win.send_enter(target[0], target[1])


class VoiceInput:
    def __init__(self, app, saved):
        self.app = app
        self.source_language = tk.StringVar(value=saved.get('voice_source_language', app.source_language.get()))
        self.target_language = tk.StringVar(value=saved.get('voice_target_language', app.language.get()))
        self.enabled = tk.BooleanVar(value=saved.get('voice_enabled', False) and saved.get('voice_backend') == 'cloud')
        self.noise_enabled = tk.BooleanVar(value=saved.get('noise_enabled', False))
        self.noise_strength = tk.DoubleVar(value=saved.get('noise_strength', 50))
        self.noise_threshold = tk.DoubleVar(value=saved.get('noise_threshold', -50))
        self.mode = tk.StringVar(value=saved.get('voice_mode', 'hold'))
        self.auto_send = tk.BooleanVar(value=saved.get('voice_auto_send', False))
        self.binding = validate_binding(saved.get('voice_shortcut') or {'modifiers': [], 'key': None})
        self.label = tk.StringVar(value=binding_label(self.binding))
        self.hint = tk.StringVar(value='Open the game chat first. Voice fills the field; you send it yourself.')
        self.events = queue.Queue()
        self.model = None
        from speech_models import MODELS
        selected = saved.get('voice_model', 'realtime')
        self.model_choice = tk.StringVar(value=selected if selected in MODELS else 'realtime')
        self.model_label = tk.StringVar(value=MODELS[self.model_choice.get()][0])
        self.loading = False
        self.recording = False
        self.processing = False
        self.cancel = threading.Event()
        self.recorder = None
        self.draft = None
        self.device = tk.StringVar(value='System default microphone')
        self.devices = {'System default microphone': None}

    def build(self, parent):
        ttk.Button(parent, text='AI models', style='ModelPicker.TButton',
                   command=self.choose_model).pack(anchor='w', pady=(4, 5))
        ttk.Label(parent, textvariable=self.model_label).pack(anchor='w', pady=(0, 8))
        ttk.Radiobutton(parent, text='Push to talk', variable=self.mode, value='hold', command=self.changed).pack(anchor='w')
        ttk.Radiobutton(parent, text='Press to start · press again to stop', variable=self.mode, value='toggle', command=self.changed).pack(anchor='w')
        ttk.Checkbutton(parent, text='Send voice messages automatically', variable=self.auto_send,
                        command=self.changed).pack(anchor='w', pady=5)
        devices = tk.Frame(parent, bg='#1b1e2e')
        devices.pack(fill='x', pady=(12, 5))
        self.devices_frame = devices
        from keyboard_preview import KeyboardMousePreview
        self.keyboard = KeyboardMousePreview(devices, self.binding, self.pick, self.save_draft)
        self.keyboard.pack(side='left', fill='x', expand=True)
        self.mouse = self.keyboard
        tk.Label(parent, text='Voice shortcut', bg='#1b1e2e', fg='#f0f0fa',
                 font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(8, 0))
        tk.Label(parent, textvariable=self.label, bg='#23334a', fg='#f0f0fa',
                 font=('Segoe UI', 13, 'bold'), padx=12, pady=5, wraplength=500,
                 justify='left').pack(anchor='w', pady=(12, 8))
        ttk.Label(parent, text='Click to select. Click again to remove.\nFor a combo: hold right mouse, click each button with left mouse, then release right mouse.',
                  wraplength=600).pack(anchor='w')
        ttk.Label(parent, text='Microphone', font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(12, 0))
        self.device_picker = ttk.Combobox(parent, textvariable=self.device, values=list(self.devices),
                                         state='readonly', postcommand=self.refresh_microphones)
        self.device_picker.pack(fill='x', pady=8)
        self.device_picker.bind('<<ComboboxSelected>>', lambda event: self.abort('Microphone changed.'))
        cleanup = tk.Frame(parent, bg=parent.cget('background'))
        cleanup.pack(fill='x', pady=8)
        ttk.Label(cleanup, text='Choose a speech engine under AI models.\nNoise suppression runs locally before speech recognition.', wraplength=600).pack(anchor='w')
        ttk.Checkbutton(cleanup, text='Noise suppression (DeepFilterNet3)', variable=self.noise_enabled,
                        command=self.noise_changed).pack(anchor='w')
        from mic_monitor import MicMonitor
        self.monitor = MicMonitor(self, cleanup)
        ttk.Label(parent, textvariable=self.hint, wraplength=600).pack(anchor='w', pady=8)

    def choose_model(self):
        from speech_models import MODELS, get_model
        if self.app.busy or self.loading:
            self.hint.set('Finish the current voice task before changing models.')
            return
        window = tk.Toplevel(self.app.root)
        window.title('ChatShift · Voice AI models')
        window.configure(background='#1b1e2e')
        window.transient(self.app.root)
        body = ttk.Frame(window, padding=20, style='Models.TFrame')
        body.pack(fill='both', expand=True)
        choice = tk.StringVar(value=self.model_choice.get())
        ttk.Label(body, text='Voice speech recognition', font=('Segoe UI', 14, 'bold')).pack(anchor='w')
        ttk.Label(body, text='Only the speech engine changes. Text translation stays unchanged.').pack(anchor='w', pady=8)
        for heading, keys in (('Local models', ('small', 'medium', 'turbo')),
                              ('Online models', ('realtime', 'gpt_transcribe'))):
            section = ttk.LabelFrame(body, text=heading, padding=12, style='Models.TLabelframe')
            section.pack(fill='x', pady=8)
            for key in keys:
                label, description = MODELS[key]
                ttk.Radiobutton(section, text=label, variable=choice, value=key).pack(anchor='w', pady=(6, 0))
                ttk.Label(section, text=description, wraplength=510).pack(anchor='w', padx=22)
        ttk.Label(body, text='Local models download on first recording (hundreds of MB to several GB).\nSelecting a local model accepts that download. Local recognition stays on your PC;\nLuna translation still uses your ChatGPT connection.', wraplength=550).pack(anchor='w', pady=16)
        def apply():
            if self.app.busy or self.loading:
                self.hint.set('Finish the current task before changing models.')
                return
            trial = getattr(self.app, 'voice_trial', None)
            if trial is not None and not trial.closed:
                trial.close()
            self.abort('Speech model changed.')
            self.model_choice.set(choice.get())
            self.model_label.set(MODELS[choice.get()][0])
            self.model = get_model(self.app)
            self.app.preferences_changed()
            self.configure()
            self.hint.set('Selected: ' + self.model_label.get())
            window.destroy()
        ttk.Button(body, text='Activate selected model', style='Accent.TButton', command=apply).pack(anchor='e')

    def refresh_microphones(self):
        if self.recording or self.processing or self.app.busy:
            return
        try:
            from microphones import list_microphones
            choices = list_microphones()
            self.devices = choices
            self.device_picker.configure(values=list(choices))
            if self.device.get() not in choices:
                self.device.set(next(iter(choices)))
        except Exception:
            self.hint.set('Could not list microphones. Check Windows audio settings and restart ChatShift.')

    def noise_options(self):
        return dict(enabled=self.noise_enabled.get(), strength=100,
                    threshold=self.noise_threshold.get(), apply_gate=False)

    def languages_changed(self, event=None):
        self.abort('Voice languages changed.')
        self.app.preferences_changed()
        if self.model and not self.app.busy:
            self.model.warm(self.source_language.get(), self.noise_options())
        source, target = self.source_language.get(), self.target_language.get()
        self.hint.set(f'Voice: {source} → {target}.' + (' Transcription only; no translation.' if source == target else ''))

    def noise_changed(self, event=None):
        self.app.preferences_changed()

    def pick(self, key, combine=False):
        if self.draft is None:
            self.draft = ShortcutDraft()
            if not combine:
                self.draft.keys = highlighted_keys(self.binding)
        try:
            self.draft.pick(key, combine)
            for preview in (self.keyboard, self.mouse):
                preview.selection = set(self.draft.keys)
                preview.draw()
            self.draft.binding()
            if not combine:
                self.save_draft()
        except ValueError as exc:
            self.hint.set(str(exc))

    def save_draft(self):
        if self.draft is None:
            return
        try:
            binding = self.draft.binding()
        except ValueError as exc:
            self.draft = None
            self.keyboard.set_binding(self.binding)
            self.mouse.set_binding(self.binding)
            self.hint.set(str(exc))
            return
        moved = self.conflicts_with_text(binding)
        if moved:
            self.app.apply_shortcut({'modifiers': [], 'key': None})
        self.abort('Voice shortcut changed.')
        self.binding = binding
        self.draft = None
        self.label.set(binding_label(binding))
        self.keyboard.set_binding(binding)
        self.mouse.set_binding(binding)
        self.changed()
        self.hint.set('Shortcut moved from Text to Voice.' if moved else '')

    def conflicts_with_text(self, binding, text_binding=None, use_current=True):
        if binding['key'] is None:
            return False
        text = self.app.binding if use_current else text_binding
        if text is None:
            conflict = binding['key'] == 13 and set(binding['modifiers']) in ({0xA3}, {0xA4}, {0xA5})
        else:
            conflict = binding == text
        return conflict

    def release_shortcut(self):
        self.abort('Shortcut moved to Text.')
        self.binding = {'modifiers': [], 'key': None}
        self.draft = None
        self.label.set('No shortcut')
        self.keyboard.set_binding(self.binding)
        self.mouse.set_binding(self.binding)
        self.hint.set('Shortcut moved to Text. Click a button to choose a new voice shortcut.')
        self.configure()

    def configure(self):
        win.configure_modes(self.app.text_enabled.get(),
            self.enabled.get() and self.model is not None and not self.app.closing, self.binding)

    def changed(self):
        self.abort('Voice settings changed.')
        self.configure()
        self.app.preferences_changed()
        if self.enabled.get():
            self.prepare()
        if self.app.local:
            self.app.start(minimize=False)

    def prepare(self):
        if self.model is not None or self.loading:
            return
        self.loading = True
        self.hint.set('Preparing selected speech engine…')
        from speech_models import get_model
        selected_model = get_model(self.app)
        def work():
            try:
                from microphones import list_microphones
                devices = list_microphones()
                model = selected_model
                self.events.put(('ready', (model, devices)))
            except ImportError:
                self.events.put(('load_error', 'Voice setup is incomplete. Run Install ChatShift.cmd, then restart ChatShift.'))
            except Exception:
                self.events.put(('load_error', 'Could not prepare cloud voice. Check Codex sign-in, internet and microphone setup.'))
        threading.Thread(target=work, daemon=True).start()

    def hotkey(self, kind, target, revision, languages=None):
        if kind == 'up':
            if self.recording and self.session_mode == 'hold':
                self.finish_recording()
            return
        if self.recording:
            if self.session_mode == 'toggle':
                self.finish_recording()
            return
        if not self.enabled.get() or self.model is None or self.app.busy or not self.app.registered:
            return
        from audio_recorder import Recorder
        self.target = target
        self.revision = revision
        self.source, self.destination = languages or (self.source_language.get(), self.target_language.get())
        self.session_mode = self.mode.get()
        self.session_send = self.auto_send.get()
        self.session_noise = self.noise_options()
        self.session_binding = dict(self.binding)
        self.owner = self.app.root.winfo_id()
        self.cancel = threading.Event()
        self.recorder = self.model.recorder(self.source, self.session_noise, self.cancel)
        try:
            self.recorder.start(self.devices.get(self.device.get()))
        except ValueError as exc:
            self.hint.set(str(exc))
            self.app.status.set(str(exc))
            return
        self.recording = self.app.busy = True
        self.app.badge.set('LISTENING')
        self.app.status.set('Listening… release the shortcut to finish.' if self.session_mode == 'hold' else 'Listening… press the shortcut again to finish.')
        self.hint.set('Listening · automatic sending ON.' if self.session_send else 'Listening · review before sending.')

    def finish_recording(self):
        self.recording = False
        try:
            audio = self.recorder.stop()
        except ValueError as exc:
            self.app.busy = False
            self.hint.set(str(exc))
            self.app.status.set(str(exc))
            self.app.badge.set('READY')
            return
        self.processing = True
        self.app.badge.set('TRANSCRIBING')
        self.app.status.set('Recognizing speech… stay in the same chat field.')
        cancel = self.cancel
        def work():
            started = time.perf_counter()
            try:
                if cancel.is_set():
                    return
                cleaned = audio  # Streaming recorder already applied DeepFilter.
                if cancel.is_set():
                    return
                text = self.model.transcribe(cleaned, self.source, cancel=cancel)
                transcript_at = time.perf_counter()
                if cancel.is_set():
                    return
                if len(text) > 1000:
                    raise ValueError('Say a shorter message (up to 1000 characters).')
                result = text if self.source == self.destination else self.app.local.translate(
                    text, target_language=self.destination, source_language=self.source)
                if cancel.is_set():
                    return
                insert_draft(self.target, self.revision, result, self.owner, cancel, self.session_binding, self.session_send)
                # Durations only: never persist the recording or its text.
                try:
                    import json
                    from pathlib import Path
                    timing = dict(getattr(audio, 'timings', {}))
                    timing.update(transcription_wait_ms=round((transcript_at-started)*1000,1),
                        translation_and_insert_ms=round((time.perf_counter()-transcript_at)*1000,1),
                        total_after_stop_ms=round((time.perf_counter()-started)*1000,1))
                    (Path(__file__).parent / '.runtime' / 'voice-timing.json').write_text(json.dumps(timing), encoding='utf-8')
                except OSError:
                    pass
                ending = 'Enter sent.' if self.session_send else 'Check the field and send it yourself.'
                self.events.put(('done', f'Voice · {time.perf_counter()-started:.1f}s. {ending}'))
            except Exception as exc:
                if not cancel.is_set():
                    self.events.put(('error', str(exc) if isinstance(exc, ValueError) else 'Voice failed. Check the chat field before retrying.'))
            finally:
                self.events.put(('released', None))
        threading.Thread(target=work, daemon=True).start()

    def abort(self, message):
        if hasattr(self, 'monitor'):
            self.monitor.stop()
        if not self.recording and not self.processing:
            return
        self.cancel.set()
        if self.recorder:
            self.recorder.close()
            self.recorder.chunks.clear()
        self.recording = False
        if not self.processing:
            self.app.busy = False
        self.app.status.set(message)
        self.hint.set(message)
        self.app.badge.set('READY' if self.app.registered else 'PAUSED')

    def poll(self):
        if hasattr(self, 'monitor'):
            self.monitor.poll()
        stage = getattr(self.model, 'status', '')
        if self.processing and not self.cancel.is_set() and stage:
            self.app.status.set(stage)
            self.hint.set(stage)
        if self.recording or self.processing:
            try:
                changed = win.focus_snapshot() != self.target or win.last_input() != self.revision
            except ValueError:
                changed = True
            if changed and not self.cancel.is_set():
                self.abort('Voice cancelled because the field or input changed.')
            if self.recording and self.recorder.full.is_set():
                self.finish_recording()
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == 'ready':
                    self.model, self.devices = value
                    self.app.speech_model = self.model
                    self.model.warm(self.source_language.get(), self.noise_options())
                    self.loading = False
                    self.device_picker.configure(values=list(self.devices))
                    if self.device.get() not in self.devices:
                        self.device.set(next(iter(self.devices)))
                    self.configure()
                    self.hint.set('Choose a voice shortcut first. No voice button is assigned.'
                        if self.binding['key'] is None else
                        'Voice ready · ' + binding_label(self.binding) + '. Open your chat field before speaking.')
                elif kind == 'load_error':
                    self.loading = False
                    self.enabled.set(False)
                    self.configure()
                    self.hint.set(value)
                    self.app.preferences_changed()
                elif kind in ('done', 'error'):
                    if not self.cancel.is_set():
                        self.hint.set(value)
                        self.app.status.set(value)
                        self.app.badge.set('READY' if kind == 'done' else 'NEEDS ATTENTION')
                elif kind == 'released':
                    self.processing = self.app.busy = False
                    if self.enabled.get() and self.app.registered and not getattr(self.app, 'closing', False):
                        self.model.warm(self.source_language.get(), self.noise_options())
        except queue.Empty:
            pass
