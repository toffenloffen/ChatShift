import queue
import json
import os
import sys
from pathlib import Path
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import winsound
import windows_input as win
import direct_mode
import among_us_mode
from codex_translator import CodexTranslator
from settings import LANGUAGES, load_settings, save_settings, SETTINGS_PATH
from shortcuts import binding_label, validate_binding, MODIFIER_NAMES, NUMPAD_ENTER
from keyboard_preview import KeyboardPreview, MousePreview, ShortcutDraft, highlighted_keys
from help_view import show_help
from voice_input import VoiceInput

BG = '#0c101c'
CARD = '#1b1e2e'
BORDER = '#303449'
TEXT = '#f2f3ff'
MUTED = '#a6acc6'
ACCENT = '#b69aff'


class App:
    def __init__(self, root, prepare=True, show_settings=False):
        self.root = root
        self.show_settings = show_settings
        self.settings_path = SETTINGS_PATH if prepare else None
        saved = load_settings() if prepare else {'target_language': 'English', 'auto_send': True}
        self.language = tk.StringVar(value=saved['target_language'])
        self.source_language = tk.StringVar(value=saved.get('source_language', 'Norwegian'))
        self.auto = tk.BooleanVar(value=saved['auto_send'])
        self.text_enabled = tk.BooleanVar(value=saved.get('text_enabled', True))
        self.binding = saved.get('shortcut')
        win.set_binding(self.binding)
        self.shortcut_text = tk.StringVar(value=binding_label(self.binding))
        self.shortcut_hint = tk.StringVar(value='Also active: Left Alt + Enter or Right Alt (AltGr) + Enter.\nPress once, release, and wait in the same field.'
            if self.binding is None else 'Release the keys and stay in the field. Only this shortcut is active.')
        self.registered = False
        self.busy = False
        self.cancel = threading.Event()
        self.results = queue.Queue()
        self.progress = queue.Queue()
        self.preparation = queue.Queue()
        self.local = None
        self.closing = False
        self.diagnostic_path = Path(__file__).resolve().parent / '.runtime' / 'status.json' if prepare else None
        self.last_diagnostic = 0
        self.status = tk.StringVar(value='Connecting and warming up your translator…')
        self.badge = tk.StringVar(value='CONNECTING')
        self.voice = VoiceInput(self, saved)
        root.title('ChatShift · Chat translator')
        assets = Path(__file__).resolve().parent / 'assets'
        self.app_icon = tk.PhotoImage(file=str(assets / 'chatshift.png'))
        root.iconphoto(True, self.app_icon)
        root.geometry(f'980x{min(930, max(660, root.winfo_screenheight() - 100))}')
        root.minsize(940, 660)
        root.configure(bg=BG)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=BG)
        style.configure('TLabel', background=CARD, foreground=TEXT, font=('Segoe UI', 10))
        style.configure('TRadiobutton', background=CARD, foreground=TEXT,
                        font=('Segoe UI', 10), indicatorbackground=BG,
                        indicatorforeground=ACCENT, focuscolor=CARD)
        style.map('TRadiobutton', background=[('active', CARD)],
                  foreground=[('disabled', MUTED), ('active', TEXT)],
                  indicatorbackground=[('selected', ACCENT), ('active', BORDER)])
        style.configure('Vertical.TScrollbar', background=BORDER, troughcolor=BG,
                        bordercolor=BG, arrowcolor=MUTED, lightcolor=BORDER, darkcolor=BORDER)
        style.configure('TButton', font=('Segoe UI', 11), padding=(18, 11),
                        background=CARD, foreground=TEXT, borderwidth=0)
        style.map('TButton', background=[('active', '#263650')],
                  foreground=[('disabled', '#62728b')])
        style.configure('Accent.TButton', background=ACCENT, foreground=BG,
                        font=('Segoe UI', 11, 'bold'))
        style.map('Accent.TButton', background=[('active', '#a9f4db'), ('disabled', '#355449')],
                  foreground=[('disabled', '#819e93')])
        style.configure('Small.TButton', font=('Segoe UI', 9), padding=(9, 5))
        style.configure('TNotebook', background=CARD, borderwidth=0,
                        bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER)
        style.configure('TNotebook.Tab', background='#252a3e', foreground=MUTED, padding=(18, 7))
        style.map('TNotebook.Tab', background=[('selected', '#3b3157')], foreground=[('selected', '#78f5dd')])
        style.configure('ChatShift.TNotebook.Tab', font=('Segoe UI', 10), padding=(16, 7))
        style.map('ChatShift.TNotebook.Tab',
                  padding=[('selected', (24, 11)), ('!selected', (16, 7))],
                  expand=[('selected', (0, 0, 0, 0)), ('!selected', (0, 0, 0, 0))],
                  font=[('selected', ('Segoe UI', 12, 'bold')), ('!selected', ('Segoe UI', 10))],
                  background=[('selected', '#173b32'), ('!selected', '#252a3e')],
                  foreground=[('selected', '#78f5b0'), ('!selected', MUTED)])
        style.configure('TCheckbutton', background=CARD, foreground=TEXT,
                        font=('Segoe UI', 11), indicatorbackground=BG)
        style.map('TCheckbutton', background=[('active', CARD)],
                  indicatorbackground=[('selected', ACCENT)])
        style.configure('TCombobox', fieldbackground='#203047', background='#203047',
                        foreground=TEXT, arrowcolor=ACCENT, bordercolor=BORDER, padding=9)
        style.map('TCombobox', fieldbackground=[('readonly', '#203047')],
                  foreground=[('readonly', TEXT)], selectbackground=[('readonly', '#203047')],
                  selectforeground=[('readonly', TEXT)])
        root.option_add('*TCombobox*Listbox.background', CARD)
        root.option_add('*TCombobox*Listbox.foreground', TEXT)
        root.option_add('*TCombobox*Listbox.selectBackground', '#304c64')
        root.option_add('*TCombobox*Listbox.font', ('Segoe UI', 11))
        viewport = tk.Canvas(root, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(root, orient='vertical', command=viewport.yview)
        scrollbar.pack(side='right', fill='y')
        viewport.pack(side='left', fill='both', expand=True)
        viewport.configure(yscrollcommand=scrollbar.set)
        shell = tk.Frame(viewport, bg=BG, padx=28, pady=25)
        shell_window = viewport.create_window(0, 0, window=shell, anchor='nw')
        shell.bind('<Configure>', lambda event: viewport.configure(scrollregion=viewport.bbox('all')))
        viewport.bind('<Configure>', lambda event: viewport.itemconfigure(shell_window, width=event.width))
        neon = tk.Canvas(shell, height=6, bg=BG, highlightthickness=0)
        neon.pack(fill='x', pady=(0, 18))
        def draw_neon(event):
            neon.delete('all')
            for x in range(event.width):
                t = x / max(1, event.width - 1)
                rgb = tuple(round(a + (b-a)*t) for a,b in zip((166,115,255),(82,241,219)))
                neon.create_line(x, 2, x, 4, fill='#%02x%02x%02x' % rgb)
        neon.bind('<Configure>', draw_neon)
        header = tk.Frame(shell, bg=BG)
        header.pack(fill='x', pady=(0, 22))
        self.header_icon = tk.PhotoImage(file=str(assets / 'chatshift-header.png'))
        tk.Label(header, image=self.header_icon, bg=BG).pack(side='left', padx=(0, 15))
        heading = tk.Frame(header, bg=BG)
        heading.pack(side='left')
        tk.Label(heading, text='CHATSHIFT', bg=BG, fg=TEXT,
                 font=('Segoe UI', 27, 'bold')).pack(anchor='w')
        tk.Label(heading, text='Your words. More worlds.', bg=BG,
                 fg='#86dcca', font=('Segoe UI', 11)).pack(anchor='w')
        self.ready_indicator = tk.Label(header, textvariable=self.badge, bg=CARD, fg=MUTED,
                 font=('Segoe UI', 9, 'bold'), padx=15, pady=10,
                 highlightthickness=1, highlightbackground=BORDER)
        self.ready_indicator.pack(side='right')
        ttk.Button(header, text='Help & setup', style='Small.TButton',
                   command=lambda: show_help(self.root)).pack(side='right', padx=12)
        body = tk.Frame(shell, bg=BG)
        body.pack(fill='both', expand=True)
        guide = tk.Frame(body, bg=BG, width=235)
        guide.pack(side='left', fill='y', padx=(0, 26))
        guide.pack_propagate(False)
        tk.Label(guide, text='Stay in the\nconversation.', bg=BG, fg=TEXT,
                 font=('Segoe UI', 23, 'bold'), justify='left').pack(anchor='w', pady=(13, 18))
        tk.Label(guide, text='Write where you play.\nChatShift handles the language.', bg=BG,
                 fg=MUTED, font=('Segoe UI', 11), justify='left').pack(anchor='w', pady=(0, 30))
        for number, title, detail in (
            ('01', 'Choose your languages', 'Set the language you write in\nand the language you need.'),
            ('02', 'Write in your chat', 'Open the chat field in your\ngame or another app.'),
            ('03', 'Press your shortcut once', 'Release the keys and wait.\nKeep the same field active.')):
            tk.Label(guide, text=number, bg=BG, fg=ACCENT,
                     font=('Segoe UI', 10, 'bold')).pack(anchor='w')
            tk.Label(guide, text=title, bg=BG, fg=TEXT,
                     font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=(3, 5))
            tk.Label(guide, text=detail, bg=BG, fg=MUTED, justify='left',
                     font=('Segoe UI', 10)).pack(anchor='w', pady=(0, 23))
        tk.Label(guide, text='One shortcut.\nA little less language barrier.', bg=BG,
                 fg=MUTED, font=('Segoe UI', 10), justify='left').pack(side='bottom', anchor='w', pady=15)
        guide.pack_forget()
        outer = tk.Frame(body, bg=BG)
        outer.pack(side='left', fill='both', expand=True)

        def card():
            box = tk.Frame(outer, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
            box.pack(fill='x', pady=(0, 13))
            tk.Frame(box, bg='#49395f', height=2).pack(fill='x')
            inner = tk.Frame(box, bg=CARD)
            inner.pack(fill='both', expand=True, padx=20, pady=12)
            return inner

        def label(parent, text, small=False):
            tk.Label(parent, text=text, bg=CARD, fg=MUTED if small else TEXT,
                     font=('Segoe UI', 10 if small else 12, 'normal' if small else 'bold'),
                     anchor='w', justify='left').pack(anchor='w')

        language_card = card()
        label(language_card, 'Translation languages · From → To')
        language_row = tk.Frame(language_card, bg=CARD)
        language_row.pack(fill='x', pady=(13, 4))
        self.source_picker = ttk.Combobox(language_row, textvariable=self.source_language,
            values=LANGUAGES, state='readonly', font=('Segoe UI', 12), width=18)
        self.source_picker.pack(side='left', fill='x', expand=True)
        self.source_picker.bind('<<ComboboxSelected>>', self.preferences_changed)
        tk.Label(language_row, text=' → ', bg=CARD, fg=ACCENT,
                 font=('Segoe UI', 17)).pack(side='left', padx=10)
        self.language_picker = ttk.Combobox(language_row, textvariable=self.language,
            values=LANGUAGES, state='readonly', font=('Segoe UI', 12), width=18)
        self.language_picker.pack(side='left', fill='x', expand=True)
        self.language_picker.bind('<<ComboboxSelected>>', self.preferences_changed)

        modes_card = card()
        label(modes_card, 'Choose how you chat')
        ttk.Checkbutton(modes_card, text='Text translation', variable=self.text_enabled,
                        command=self.text_mode_changed).pack(anchor='w', pady=(8, 3))
        self.voice_enabled = self.voice.enabled
        ttk.Checkbutton(modes_card, text='Voice input · local AI', variable=self.voice_enabled,
                        command=self.voice.changed).pack(anchor='w')

        shortcut_container = card()
        self.shortcut_tabs = ttk.Notebook(shortcut_container, style='ChatShift.TNotebook')
        self.shortcut_tabs.pack(fill='x')
        shortcut_card = tk.Frame(self.shortcut_tabs, bg=CARD, padx=10, pady=12)
        voice_shortcut_card = tk.Frame(self.shortcut_tabs, bg=CARD, padx=10, pady=12)
        self.shortcut_tabs.add(shortcut_card, text='Text')
        self.shortcut_tabs.add(voice_shortcut_card, text='Voice')
        label(voice_shortcut_card, 'Voice shortcut')
        self.voice.build(voice_shortcut_card)
        ttk.Separator(voice_shortcut_card, orient='horizontal').pack(fill='x', pady=(18, 12))
        test_area = tk.Frame(voice_shortcut_card, bg=CARD)
        test_area.pack(fill='x')
        test_copy = tk.Frame(test_area, bg=CARD)
        test_copy.pack(side='left', fill='x', expand=True)
        tk.Label(test_copy, text='Microphone test', bg=CARD, fg=TEXT,
                 font=('Segoe UI', 11, 'bold')).pack(anchor='w')
        tk.Label(test_copy, text='Try your voice here. Nothing goes to your game.',
                 bg=CARD, fg=MUTED, font=('Segoe UI', 9)).pack(anchor='w', pady=(3, 0))
        ttk.Button(test_area, text='Open test', style='Small.TButton',
                   command=self.open_voice_trial).pack(side='right', padx=(12, 0))
        shortcut_header = tk.Frame(shortcut_card, bg=CARD)
        shortcut_header.pack(fill='x')
        tk.Label(shortcut_header, text='Text shortcut', bg=CARD, fg=TEXT,
                 font=('Segoe UI', 12, 'bold')).pack(side='left')
        self.shortcut_button = ttk.Button(shortcut_header, text='Change shortcut',
            style='Small.TButton', command=self.change_shortcut)
        self.shortcut_button.pack(side='right')
        ttk.Button(shortcut_header, text='How to set up', style='Small.TButton',
                   command=lambda: show_help(self.root, 'Shortcuts')).pack(side='right', padx=8)
        keys = tk.Frame(shortcut_card, bg=CARD)
        keys.pack(anchor='w', pady=(12, 8))
        tk.Label(keys, textvariable=self.shortcut_text, bg='#23334a', fg=TEXT,
                 font=('Segoe UI', 13, 'bold'), padx=12, pady=5, wraplength=500,
                 justify='left').pack(side='left')
        self.shortcut_draft = None
        self.combine_keys = tk.BooleanVar(value=False)
        devices = tk.Frame(shortcut_card, bg=CARD)
        devices.pack(fill='x', pady=(12, 5))
        self.mouse_preview = MousePreview(devices, self.binding,
            on_pick=self.pick_shortcut_key, on_finish=self.save_shortcut_draft)
        self.mouse_preview.pack(side='right', padx=(10, 0))
        self.keyboard_preview = KeyboardPreview(devices, self.binding,
            on_pick=self.pick_shortcut_key, on_finish=self.save_shortcut_draft)
        self.keyboard_preview.pack(side='left', fill='x', expand=True)
        tk.Label(shortcut_card,
            text='Left-click a button in the picture to select it. Click again to remove.\n'
                 'For a combination:\n'
                 '1. Keep the right mouse button held down.\n'
                 '2. Click up to 3 buttons in the picture with the left mouse button, one at a time.\n'
                 '3. Release the right mouse button to save.',
            bg=CARD, fg=MUTED, font=('Segoe UI', 10), wraplength=800,
            justify='left').pack(anchor='w', pady=(3, 5))
        self.draft_hint = tk.StringVar(value='')
        tk.Label(shortcut_card, textvariable=self.draft_hint, bg=CARD, fg=ACCENT,
                 font=('Segoe UI', 10), wraplength=510, justify='left').pack(anchor='w', pady=5)
        draft_actions = tk.Frame(shortcut_card, bg=CARD)
        draft_actions.pack(fill='x', pady=(0, 5))
        self.save_shortcut_button = ttk.Button(draft_actions, text='Save shortcut',
            style='Small.TButton', command=self.save_shortcut_draft, state='disabled')
        ttk.Button(draft_actions, text='Cancel selection', style='Small.TButton',
            command=self.cancel_shortcut_draft).pack(side='left', padx=8)
        self.key_instructions = tk.StringVar(value=self.shortcut_instructions())

        send_card = card()
        ttk.Checkbutton(send_card, text='Send automatically after translating',
                        variable=self.auto, command=self.preferences_changed).pack(anchor='w')

        status_card = card()
        self.status_indicator = tk.Label(status_card, textvariable=self.badge, bg=CARD, fg=MUTED,
                 font=('Segoe UI', 9, 'bold'))
        self.status_indicator.pack(anchor='w')
        self.badge.trace_add('write', self.update_ready_color)
        self.update_ready_color()
        tk.Label(status_card, textvariable=self.status, bg=CARD, fg=TEXT,
                 font=('Segoe UI', 11), wraplength=535, justify='left', anchor='w').pack(
                     anchor='w', fill='x', pady=(7, 0))
        footer = tk.Frame(outer, bg=BG)
        footer.pack(fill='x', pady=(2, 10))
        self.start_button = ttk.Button(footer, text='Run in background', style='Accent.TButton',
                                      command=self.start, state='disabled')
        self.start_button.pack(side='left')
        self.stop_button = ttk.Button(footer, text='Pause', command=self.stop, state='disabled')
        self.stop_button.pack(side='left', padx=10)
        tk.Label(outer, text='Uses your ChatGPT sign-in · Internet required\nMessages go to OpenAI and use your Codex allowance.',
                 bg=BG, fg=MUTED, font=('Segoe UI', 9), justify='left').pack(anchor='w')
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.timer = root.after(25, self.poll)
        self.voice.configure()
        if prepare and self.voice.enabled.get():
            self.voice.prepare()
        if prepare:
            initial_language = self.language.get()
            initial_source = self.source_language.get()
            def load():
                local = None
                try:
                    local = CodexTranslator(target_language=initial_language, source_language=initial_source)
                    local.translate('Hei.')
                    if self.closing:
                        local.close()
                        return
                    self.preparation.put((local, None))
                except Exception as exc:
                    if local:
                        local.close()
                    self.preparation.put((None, str(exc) if isinstance(exc, ValueError) else
                        'Could not start the translator. Restart ChatShift.'))
            threading.Thread(target=load, daemon=True).start()

    def preferences_changed(self, event=None):
        if self.settings_path:
            try:
                save_settings(self.language.get(), self.auto.get(), self.settings_path,
                              shortcut=self.binding, source_language=self.source_language.get(),
                              text_enabled=self.text_enabled.get(), voice_shortcut=self.voice.binding,
                              voice_enabled=self.voice.enabled.get(), voice_mode=self.voice.mode.get(),
                              voice_auto_send=self.voice.auto_send.get())
            except OSError:
                self.status.set('This choice works now, but could not be saved. Check folder permissions.')
                return
        if not self.busy and self.local and self.text_enabled.get():
            self.status.set(f'Next message: {self.source_language.get()} → {self.language.get()}.')

    def text_mode_changed(self):
        self.voice.configure()
        if self.text_enabled.get() or self.voice.enabled.get():
            if self.local:
                self.start(minimize=False)
        else:
            self.stop()
            self.status.set('Text translation is off. Enable it when you want to use your shortcut.')
        self.preferences_changed()

    def shortcut_instructions(self):
        if self.binding is not None and self.binding['key'] is None:
            return 'Click a key or mouse button to choose a shortcut.'
        if self.binding is not None and not self.binding['modifiers']:
            return 'Press the highlighted key once, then release and wait.'
        return 'Hold the marked Ctrl / Alt / Shift keys. Tap the other marked key.'

    def pick_shortcut_key(self, key, combine=False):
        if self.shortcut_draft is None:
            self.shortcut_draft = ShortcutDraft()
            if not combine and not self.combine_keys.get():
                self.shortcut_draft.keys = highlighted_keys(self.binding)
        try:
            self.shortcut_draft.pick(key, combine or self.combine_keys.get())
            self.keyboard_preview.selection = set(self.shortcut_draft.keys)
            self.keyboard_preview.draw()
            self.mouse_preview.selection = set(self.shortcut_draft.keys)
            self.mouse_preview.draw()
            binding = self.shortcut_draft.binding()
        except ValueError as exc:
            self.save_shortcut_button.configure(state='disabled')
            self.draft_hint.set(str(exc))
            return
        self.draft_hint.set('Selected: ' + binding_label(binding) + ' · not saved yet')
        self.save_shortcut_button.configure(state='normal')
        if not combine and not self.combine_keys.get():
            self.save_shortcut_draft()

    def save_shortcut_draft(self):
        if self.shortcut_draft is not None:
            try:
                self.apply_shortcut(self.shortcut_draft.binding())
            except ValueError as exc:
                self.draft_hint.set(str(exc))

    def cancel_shortcut_draft(self):
        self.shortcut_draft = None
        self.keyboard_preview.set_binding(self.binding)
        self.mouse_preview.set_binding(self.binding)
        self.save_shortcut_button.configure(state='disabled')
        self.draft_hint.set('')

    def apply_shortcut(self, binding):
        binding = validate_binding(binding)
        if self.voice.conflicts_with_text(self.voice.binding, binding, use_current=False):
            self.voice.release_shortcut()
        self.binding = binding
        self.cancel.set()
        win.set_binding(self.binding)
        self.shortcut_text.set(binding_label(self.binding))
        self.keyboard_preview.set_binding(self.binding)
        self.mouse_preview.set_binding(self.binding)
        self.key_instructions.set(self.shortcut_instructions())
        self.shortcut_draft = None
        self.save_shortcut_button.configure(state='disabled')
        self.draft_hint.set('Saved: ' + binding_label(self.binding))
        if self.registered:
            # Refresh the hooks after rebinding, including their modifier state.
            win.unregister()
            self.registered = win.register()
            if not self.registered:
                self.badge.set('NEEDS ATTENTION')
                self.status.set('Could not enable the new shortcut. Restart ChatShift.')
                return
        self.shortcut_hint.set('Also active: Left Alt + Enter or Right Alt (AltGr) + Enter.\nPress once, release, and wait in the same field.'
            if self.binding is None else 'Release the keys and stay in the field. Only this shortcut is active.')
        self.preferences_changed()

    def change_shortcut(self):
        dialog = tk.Toplevel(self.root)
        dialog.title('Choose your shortcut')
        dialog.configure(bg=CARD)
        dialog.geometry('540x240')
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        message = tk.StringVar(value='Press a key or combination.\nFor Ctrl, Alt or Shift alone, press and release it.')
        tk.Label(dialog, text='Press your new shortcut', bg=CARD, fg=TEXT,
                 font=('Segoe UI', 17, 'bold')).pack(anchor='w', padx=24, pady=(22, 12))
        tk.Label(dialog, textvariable=message, bg=CARD, fg=MUTED, font=('Segoe UI', 11),
                 wraplength=490, justify='left').pack(anchor='w', padx=24)
        modifiers = set()
        keysyms = {'Control_L': 0xA2, 'Control_R': 0xA3, 'Alt_L': 0xA4,
                   'Alt_R': 0xA5, 'Shift_L': 0xA0, 'Shift_R': 0xA1,
                   'ISO_Level3_Shift': 0xA5}
        def pressed(event):
            if event.keysym == 'Escape':
                dialog.destroy()
                return 'break'
            modifier = keysyms.get(event.keysym, event.keycode)
            if modifier in MODIFIER_NAMES:
                modifiers.add(modifier)
                return 'break'
            try:
                key = NUMPAD_ENTER if event.keysym == 'KP_Enter' else event.keycode
                self.apply_shortcut({'modifiers': sorted(modifiers), 'key': key})
            except ValueError as exc:
                message.set(str(exc))
                return 'break'
            dialog.destroy()
            return 'break'
        def released(event):
            released_key = keysyms.get(event.keysym, event.keycode)
            if released_key in MODIFIER_NAMES and modifiers:
                try:
                    self.apply_shortcut({'modifiers': sorted(modifiers - {released_key}), 'key': released_key})
                    dialog.destroy()
                except ValueError as exc:
                    message.set(str(exc))
            modifiers.discard(released_key)
            return 'break'
        dialog.bind('<KeyPress>', pressed)
        dialog.bind('<KeyRelease>', released)
        buttons = tk.Frame(dialog, bg=CARD)
        buttons.pack(anchor='w', padx=24, pady=22)
        def restore():
            self.apply_shortcut(None)
            dialog.destroy()
        ttk.Button(buttons, text='Restore default', command=restore).pack(side='left')
        ttk.Button(buttons, text='Cancel', command=dialog.destroy).pack(side='left', padx=10)
        dialog.focus_set()

    def update_ready_color(self, *args):
        ready = self.badge.get() == 'READY'
        self.ready_indicator.configure(bg='#15382b' if ready else CARD,
            fg='#72ffa8' if ready else MUTED,
            highlightbackground='#46ce7e' if ready else BORDER)
        self.status_indicator.configure(fg='#72ffa8' if ready else MUTED)

    def open_voice_trial(self):
        try:
            from voice_trial import show_voice_trial
            show_voice_trial(self)
        except ImportError:
            messagebox.showinfo('Voice setup', 'Install the optional voice dependencies from requirements-voice.txt, then try again.')

    def start(self, minimize=True):
        if not self.text_enabled.get() and not self.voice.enabled.get():
            self.badge.set('TEXT OFF')
            self.status.set('Text translation is off. Enable it to use your shortcut.')
            return
        if self.local is None:
            self.status.set('The translator is not ready yet.')
            return
        if not self.registered:
            self.voice.configure()
            self.registered = win.register()
        if not self.registered:
            self.status.set('Could not enable the shortcut. Restart ChatShift.')
            self.badge.set('NEEDS ATTENTION')
            return
        self.stop_button.configure(state='normal')
        self.badge.set('READY')
        modes = []
        if self.text_enabled.get():
            modes.append('Text: ' + binding_label(self.binding))
        if self.voice.enabled.get():
            modes.append('Voice: ' + binding_label(self.voice.binding))
        self.status.set(f'Active: {self.source_language.get()} → {self.language.get()}. ' + ' · '.join(modes))
        if minimize:
            self.root.iconify()

    def stop(self):
        self.voice.abort('Voice cancelled. Shortcuts paused.')
        self.cancel.set()
        if self.registered:
            win.unregister()
            self.registered = False
        self.stop_button.configure(state='disabled')
        self.badge.set('PAUSED')
        self.status.set('Shortcuts are paused. Your keyboard works normally.')

    def trigger(self, target):
        if self.binding is not None and self.binding['key'] is None:
            return
        if self.busy or not self.text_enabled.get() or not self.registered or not win.external(target[0]) or self.local is None:
            return
        self.busy = True
        self.cancel = threading.Event()
        cancel = self.cancel
        send = self.auto.get()
        language = self.language.get()
        source = self.source_language.get()
        owner = self.root.winfo_id()
        started = getattr(target, 'pressed_at', time.perf_counter())
        stages = []
        def progress(message):
            stages.append({'stage': message, 'at_ms': round((time.perf_counter() - started) * 1000, 1)})
            self.progress.put((message, cancel))
        self.badge.set('TRANSLATING')
        self.status.set(f'Translating to {language}… stay in the same text field.')
        def work():
            try:
                adapter = among_us_mode if among_us_mode.is_among_us(target) else direct_mode
                _, elapsed = adapter.run(target, owner, '', cancel, send=send,
                    translate_fn=lambda text, key: self.local.translate(text, key, target_language=language, source_language=source),
                    progress=progress)
                elapsed = time.perf_counter() - started
                stages.append({'stage': 'Enter injected' if send else 'Review ready', 'at_ms': round(elapsed * 1000, 1)})
                result = f'{language} · {elapsed:.2f}s from shortcut · ' + ('Enter sent.' if send else 'Ready for you to review.')
                error = False
            except Exception as exc:
                result = str(exc) if isinstance(exc, ValueError) else 'Unexpected error. Check the chat field before trying again.'
                error = True
            self.last_timing = {'stages': stages, 'total_ms': round((time.perf_counter() - started) * 1000, 1),
                                'success': not error, 'endpoint': 'input injection, not server delivery'}
            self.results.put((result, error, cancel))
            if not error and not cancel.is_set():
                prepare = getattr(self.local, 'prepare_next', None)
                if prepare:
                    prepare()
        threading.Thread(target=work, daemon=True).start()

    def poll(self):
        while True:
            voice_event = win.poll_voice()
            if voice_event is None:
                break
            self.voice.hotkey(*voice_event)
        self.voice.poll()
        try:
            while True:
                message, cancel = self.progress.get_nowait()
                if not cancel.is_set():
                    self.status.set(message)
        except queue.Empty:
            pass
        try:
            local, error = self.preparation.get_nowait()
            self.local = local
            if local:
                self.start_button.configure(state='normal')
                self.start(minimize=not self.show_settings)
            else:
                self.status.set(error)
                self.badge.set('NEEDS ATTENTION')
        except queue.Empty:
            pass
        while True:
            target = win.poll_hotkey()
            if not target:
                break
            self.trigger(target)
        try:
            while True:
                result, error, cancel = self.results.get_nowait()
                self.busy = False
                if not cancel.is_set():
                    self.status.set(result)
                    self.badge.set('NEEDS ATTENTION' if error else 'READY')
                    if error:
                        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except queue.Empty:
            pass
        if self.diagnostic_path and time.monotonic() - self.last_diagnostic > 1:
            self.last_diagnostic = time.monotonic()
            try:
                self.diagnostic_path.parent.mkdir(exist_ok=True)
                temporary = self.diagnostic_path.with_suffix('.tmp')
                temporary.write_text(json.dumps({'pid': os.getpid(), 'updated': time.time(),
                    'active': self.registered, 'model_ready': self.local is not None, 'backend': 'codex-chatgpt',
                    'model': getattr(self.local, 'model', None), 'target_language': self.language.get(),
                    'shortcut': binding_label(self.binding),
                    'voice_shortcut': binding_label(self.voice.binding),
                    'voice_ready': self.voice.model is not None,
                    'voice_enabled': self.voice.enabled.get(), 'voice_mode': self.voice.mode.get(),
                    'voice_recording': self.voice.recording, 'voice_processing': self.voice.processing,
                    'last_timing': getattr(self, 'last_timing', None),
                    'backend_timing': getattr(self.local, 'last_timing', None),
                    'requests': getattr(self.local, 'request_count', 0),
                    'cache_hits': getattr(self.local, 'cache_hits', 0),
                    'reported_input_tokens': getattr(self.local, 'reported_input_tokens', 0),
                    'reported_cached_tokens': getattr(self.local, 'reported_cached_tokens', 0),
                    'reported_output_tokens': getattr(self.local, 'reported_output_tokens', 0),
                    'busy': self.busy, 'status': self.status.get(), **win.diagnostics()}, ensure_ascii=False), encoding='utf-8')
                temporary.replace(self.diagnostic_path)
            except OSError:
                pass
        self.timer = self.root.after(25, self.poll)

    def close(self):
        self.closing = True
        voice = getattr(self, 'voice_trial', None)
        if voice is not None and not voice.closed:
            voice.close()
        self.stop()
        if self.local:
            self.local.close()
        try:
            while True:
                ready, _ = self.preparation.get_nowait()
                if ready:
                    ready.close()
        except queue.Empty:
            pass
        self.root.after_cancel(self.timer)
        self.root.destroy()


if __name__ == '__main__':
    instance = win.acquire_instance()
    if instance:
        try:
            app = App(tk.Tk(), show_settings='--settings' in sys.argv or '--voice-test' in sys.argv)
            if '--voice-test' in sys.argv:
                app.root.after(500, app.open_voice_trial)
            if '--voice-setup' in sys.argv:
                app.shortcut_tabs.select(1)
            app.root.mainloop()
        finally:
            win.kernel32.CloseHandle(instance)
    else:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo('ChatShift is already running', 'Open ChatShift from your taskbar.')
        root.destroy()
