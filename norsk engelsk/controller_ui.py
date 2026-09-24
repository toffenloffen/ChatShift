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
        ttk.Checkbutton(parent, text='Enable controller shortcuts', variable=self.enabled,
                        command=self.changed).pack(anchor='w')
        row = ttk.Frame(parent)
        row.pack(fill='x', pady=8)
        ttk.Label(row, text='Controller slot').pack(side='left')
        picker = ttk.Combobox(row, textvariable=self.slot, values=('1', '2', '3', '4'),
                              state='readonly', width=5)
        picker.pack(side='left', padx=8)
        picker.bind('<<ComboboxSelected>>', self.changed)
        ttk.Label(parent, textvariable=self.status).pack(anchor='w')
        for mode in self.bindings:
            ttk.Label(parent, textvariable=self.labels[mode]).pack(anchor='w', pady=3)
        row = ttk.Frame(parent)
        row.pack(fill='x', pady=8)
        for mode in self.bindings:
            ttk.Radiobutton(row, text=mode, value=mode, variable=self.mode,
                            command=self.load_selection).pack(side='left', padx=6)
        grid = ttk.Frame(parent)
        grid.pack(fill='x')
        for index, name in enumerate(BUTTONS):
            ttk.Checkbutton(grid, text=name, variable=self.selected[name]).grid(
                row=index // 4, column=index % 4, sticky='w', padx=8, pady=4)
        ttk.Button(parent, text='Save controller shortcut', command=self.save_binding).pack(anchor='w', pady=10)
        ttk.Label(parent, wraplength=780, justify='left', text=(
            'Choose up to three buttons, then Save. Uncheck all to remove a shortcut.\n'
            'Text: press and release. Voice: uses Hold to talk or Press to start from the Voice tab.\n'
            'Open the game chat first. These buttons also reach the game; choose an unused combination.\n'
            'Rear paddles are not separate XInput buttons. Map them to a keyboard shortcut in Steam Input '
            'or supported controller software, then choose that shortcut in Text or Voice.')).pack(anchor='w')
        self.load_selection()
        self.refresh_labels()

    def load_selection(self):
        for name, var in self.selected.items():
            var.set(name in self.bindings[self.mode.get()])

    def refresh_labels(self):
        for mode, chord in self.bindings.items():
            self.labels[mode].set(mode + ': ' + (' + '.join(chord) or 'No controller shortcut'))

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
