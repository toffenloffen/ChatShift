"""Windows controller bindings; keyboard and mouse shortcuts remain available."""
import json
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import windows_input as win
from controller_input import BUTTONS, XInput, ChordEdges, validate_chord


class ControllerInput:
    def __init__(self, app, persist=True):
        self.app = app
        self.path = Path(__file__).with_name('.controller.json') if persist else None
        saved = {}
        if self.path:
            try:
                saved = json.loads(self.path.read_text(encoding='utf-8'))
                if not isinstance(saved, dict):
                    saved = {}
            except (OSError, ValueError):
                pass
        self.bindings = {}
        for mode in ('Text', 'Voice'):
            try:
                self.bindings[mode] = validate_chord(saved.get(mode, []))
            except (ValueError, TypeError):
                self.bindings[mode] = []
        # A hand-edited conflicting configuration must not activate both modes.
        if (self.bindings['Text'] and self.bindings['Voice'] and
                (set(self.bindings['Text']) <= set(self.bindings['Voice']) or
                 set(self.bindings['Voice']) <= set(self.bindings['Text']))):
            self.bindings['Voice'] = []
        self.enabled = tk.BooleanVar(value=saved.get('enabled') is True)
        slot = saved.get('slot', 1)
        self.slot = tk.StringVar(value=str(slot if type(slot) is int and 1 <= slot <= 4 else 1))
        self.mode = tk.StringVar(value='Text')
        self.status = tk.StringVar(value='Controller not connected')
        self.labels = {m: tk.StringVar() for m in self.bindings}
        self.selected = {name: tk.BooleanVar() for name in BUTTONS}
        self.reader = XInput()
        self.edges = {m: ChordEdges() for m in self.bindings}
        self.targets = {}
        self.voice_owned = False
        self.was_active = False

    def build(self, parent):
        from controller_preview import ControllerPreview
        bg, muted = '#1b1e2e', '#a6acc6'
        header = tk.Frame(parent, bg=bg)
        header.pack(fill='x', pady=(0, 8))
        ttk.Checkbutton(header, text='Enable controller', variable=self.enabled,
                        command=self.changed).pack(side='left')
        picker = ttk.Combobox(header, textvariable=self.slot, values=('1', '2', '3', '4'),
                              state='readonly', width=3)
        picker.pack(side='right')
        picker.bind('<<ComboboxSelected>>', self.changed)
        tk.Label(header, text='Controller ', bg=bg, fg=muted).pack(side='right')
        tk.Label(parent, textvariable=self.status, bg=bg, fg=muted,
                 font=('Segoe UI', 9)).pack(anchor='w', pady=(0, 10))
        modes = tk.Frame(parent, bg=bg)
        modes.pack(fill='x')
        self.mode_buttons = {}
        for mode in self.bindings:
            button = tk.Button(modes, textvariable=self.labels[mode], relief='flat', bd=0,
                               padx=16, pady=10, cursor='hand2',
                               command=lambda m=mode: self.choose_mode(m))
            button.pack(side='left', expand=True, fill='x', padx=3)
            self.mode_buttons[mode] = button
        self.preview = ControllerPreview(parent, self.pick_button)
        self.preview.pack(pady=10)
        self.selection_label = tk.StringVar()
        row = tk.Frame(parent, bg=bg)
        row.pack(fill='x', pady=(0, 8))
        tk.Label(row, textvariable=self.selection_label, bg=bg, fg='#78f5b0',
                 font=('Segoe UI', 11, 'bold')).pack(side='left')
        ttk.Button(row, text='Clear', style='Small.TButton', command=self.clear_binding).pack(side='right')
        tk.Label(parent, text='Click up to 3 buttons. Click again to remove. Saved automatically.',
                 bg=bg, fg=muted, font=('Segoe UI', 9)).pack(anchor='w')
        tk.Label(parent, text='Open game chat first. Buttons also reach the game; choose an unused combination.',
                 bg=bg, fg=muted, font=('Segoe UI', 9), wraplength=760, justify='left').pack(anchor='w', pady=(4, 0))
        self.mode_help = tk.StringVar()
        tk.Label(parent, textvariable=self.mode_help, bg=bg, fg=muted,
                 font=('Segoe UI', 9)).pack(anchor='w', pady=(4, 0))
        self.details = tk.Frame(parent, bg=bg)
        ttk.Button(parent, text='Using rear paddles?', style='Small.TButton',
                   command=self.toggle_details).pack(anchor='w', pady=(8, 0))
        tk.Label(self.details, bg=bg, fg=muted, font=('Segoe UI', 9), wraplength=760,
                 justify='left', text='Map rear paddles to a keyboard shortcut in Steam Input or supported controller software. '
                 'Choose that shortcut in Text or Voice. Rear paddles are not separate buttons in this Windows view.').pack(anchor='w')
        self.load_selection()
        self.refresh_labels()

    def toggle_details(self):
        if self.details.winfo_manager():
            self.details.pack_forget()
        else:
            self.details.pack(fill='x', pady=6)

    def choose_mode(self, mode):
        self.mode.set(mode)
        self.load_selection()
        self.refresh_labels()

    def pick_button(self, name):
        if name.startswith('Rear '):
            self.show_paddle_setup(name)
            return
        if not self.selected[name].get() and sum(v.get() for v in self.selected.values()) >= 3:
            self.selection_label.set('Maximum 3 buttons - remove one first')
            return
        self.selected[name].set(not self.selected[name].get())
        self.save_binding()

    def show_paddle_setup(self, name):
        from shortcuts import binding_label
        mode = self.mode.get()
        binding = self.app.binding if mode == 'Text' else self.app.voice.binding
        dialog = tk.Toplevel(self.app.root)
        dialog.title('Rear paddle setup')
        dialog.configure(bg='#1b1e2e')
        dialog.transient(self.app.root)
        text = (name + ' · ' + mode + '\n\n'
                'This Windows input method cannot read the paddle independently.\n'
                'In Steam Input or supported controller software, map this paddle\n'
                'to the same keyboard shortcut that ChatShift uses.\n\n'
                'Current ' + mode + ' shortcut: ' + binding_label(binding) + '\n\n'
                'Use the button below to choose a keyboard shortcut, then set the\n'
                'same keys in your controller software. This diagram does not\n'
                'change your Steam Input mapping automatically.')
        tk.Label(dialog, text=text, justify='left', bg='#1b1e2e', fg='#f2f3ff',
                 font=('Segoe UI', 10), padx=22, pady=20).pack()
        def choose():
            self.app.shortcut_tabs.select(0 if mode == 'Text' else 1)
            dialog.destroy()
        ttk.Button(dialog, text='Choose ' + mode.lower() + ' keyboard shortcut', command=choose).pack(pady=(0, 10))
        ttk.Button(dialog, text='Close', command=dialog.destroy).pack(pady=(0, 16))

    def clear_binding(self):
        for var in self.selected.values():
            var.set(False)
        self.save_binding()

    def load_selection(self):
        for name, var in self.selected.items():
            var.set(name in self.bindings[self.mode.get()])

    def refresh_labels(self):
        for mode, chord in self.bindings.items():
            self.labels[mode].set(mode + ': ' + (' + '.join(chord) or 'Choose buttons'))
        if hasattr(self, 'preview'):
            self.preview.set_selection(self.bindings[self.mode.get()])
            self.selection_label.set(' + '.join(self.bindings[self.mode.get()]) or 'Click a button on the controller')
            self.mode_help.set('Text: press and release to translate.' if self.mode.get() == 'Text' else
                               'Voice: uses your hold-to-talk or toggle setting in the Voice tab.')
            for mode, button in self.mode_buttons.items():
                active = mode == self.mode.get()
                button.configure(bg='#173b32' if active else '#252a3e',
                                 fg='#78f5b0' if active else '#a6acc6',
                                 activebackground='#245743', activeforeground='#f2f3ff',
                                 font=('Segoe UI', 11, 'bold' if active else 'normal'))

    def save_binding(self):
        try:
            chord = validate_chord([name for name, var in self.selected.items() if var.get()])
        except ValueError as exc:
            self.app.status.set(str(exc))
            return
        mode = self.mode.get()
        other = 'Voice' if mode == 'Text' else 'Text'
        if chord and self.bindings[other] and (set(chord) <= set(self.bindings[other]) or
                                                set(self.bindings[other]) <= set(chord)):
            self.bindings[other] = []
        self.bindings[mode] = chord
        self.refresh_labels()
        self.changed()

    def reset(self):
        for edge in self.edges.values():
            edge.reset()
        self.targets.clear()
        if self.voice_owned:
            self.app.voice.abort('Controller recording cancelled.')
        self.voice_owned = False

    def changed(self, event=None):
        self.reset()
        if self.path:
            try:
                temporary = self.path.with_suffix('.tmp')
                temporary.write_text(json.dumps(dict(self.bindings, enabled=self.enabled.get(),
                                                      slot=int(self.slot.get()))), encoding='utf-8')
                temporary.replace(self.path)
            except OSError:
                self.app.status.set('Controller choice works now, but could not be saved.')

    def poll(self):
        pressed = self.reader.read(int(self.slot.get()) - 1)
        self.status.set('Controller not connected' if pressed is None else
                        'Connected · ' + (' + '.join(n for n in BUTTONS if n in pressed) or 'Ready'))
        active = self.enabled.get() and self.app.registered and not self.app.closing
        if not active or pressed is None:
            self.reset()
            self.was_active = False
            return
        if not self.was_active:
            self.reset()
        self.was_active = True
        try:
            target = win.focus_snapshot()
        except ValueError:
            self.reset()
            return
        if self.voice_owned and not (self.app.voice.recording or self.app.voice.processing):
            self.voice_owned = False
        for mode, edge in self.edges.items():
            event = edge.update(pressed, self.bindings[mode])
            if event == 'cancel':
                self.targets.pop(mode, None)
                if mode == 'Voice' and self.voice_owned:
                    self.app.voice.abort('Controller combination changed. Recording cancelled.')
                    self.voice_owned = False
            elif event == 'down':
                if not win.external(target[0]):
                    continue
                self.targets[mode] = (target, win.last_input())
                if mode == 'Voice' and (self.voice_owned or not self.app.busy):
                    self.app.voice.hotkey('down', target, win.last_input())
                    self.voice_owned = self.app.voice.recording or self.app.voice.processing
            elif event == 'up':
                initial = self.targets.pop(mode, None)
                if mode == 'Voice' and self.voice_owned:
                    self.app.voice.hotkey('up', target, win.last_input())
                elif mode == 'Text' and initial == (target, win.last_input()):
                    self.app.trigger(target, controller=True)
