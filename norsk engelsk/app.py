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
from shortcuts import binding_label, validate_binding, MODIFIER_NAMES

BG = '#0c1220'
CARD = '#151e30'
BORDER = '#28354b'
TEXT = '#eef3fb'
MUTED = '#a6b4cb'
ACCENT = '#87e6c4'


class App:
    def __init__(self, root, prepare=True, show_settings=False):
        self.root = root
        self.show_settings = show_settings
        self.settings_path = SETTINGS_PATH if prepare else None
        saved = load_settings() if prepare else {'target_language': 'English', 'auto_send': True}
        self.language = tk.StringVar(value=saved['target_language'])
        self.auto = tk.BooleanVar(value=saved['auto_send'])
        self.binding = saved.get('shortcut')
        win.set_binding(self.binding)
        self.shortcut_text = tk.StringVar(value=binding_label(self.binding))
        self.shortcut_hint = tk.StringVar(value='Alt + Enter also works. Release the keys and stay in the field.'
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
        root.title('ChatShift · Chat translator')
        root.geometry('680x780')
        root.minsize(640, 760)
        root.configure(bg=BG)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=BG)
        style.configure('TButton', font=('Segoe UI', 11), padding=(18, 11),
                        background=CARD, foreground=TEXT, borderwidth=0)
        style.map('TButton', background=[('active', '#263650')],
                  foreground=[('disabled', '#62728b')])
        style.configure('Accent.TButton', background=ACCENT, foreground=BG,
                        font=('Segoe UI', 11, 'bold'))
        style.map('Accent.TButton', background=[('active', '#a9f4db'), ('disabled', '#355449')],
                  foreground=[('disabled', '#819e93')])
        style.configure('Small.TButton', font=('Segoe UI', 9), padding=(9, 5))
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
        outer = tk.Frame(root, bg=BG)
        outer.pack(fill='both', expand=True, padx=30, pady=25)
        header = tk.Frame(outer, bg=BG)
        header.pack(fill='x', pady=(0, 20))
        tk.Label(header, text='CHATSHIFT', bg=BG, fg=ACCENT,
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        tk.Label(header, text='Your words. More worlds.', bg=BG, fg=TEXT,
                 font=('Segoe UI', 24, 'bold')).pack(anchor='w', pady=(6, 5))
        tk.Label(header, text='Natural translations for the way you chat.', bg=BG,
                 fg=MUTED, font=('Segoe UI', 11)).pack(anchor='w')

        def card():
            box = tk.Frame(outer, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
            box.pack(fill='x', pady=(0, 13))
            inner = tk.Frame(box, bg=CARD)
            inner.pack(fill='both', expand=True, padx=20, pady=17)
            return inner

        def label(parent, text, small=False):
            tk.Label(parent, text=text, bg=CARD, fg=MUTED if small else TEXT,
                     font=('Segoe UI', 10 if small else 12, 'normal' if small else 'bold'),
                     anchor='w', justify='left').pack(anchor='w')

        language_card = card()
        label(language_card, 'Translation language')
        language_row = tk.Frame(language_card, bg=CARD)
        language_row.pack(fill='x', pady=(13, 4))
        tk.Label(language_row, text='Norwegian', bg=CARD, fg=MUTED,
                 font=('Segoe UI', 12)).pack(side='left')
        tk.Label(language_row, text=' → ', bg=CARD, fg=ACCENT,
                 font=('Segoe UI', 17)).pack(side='left', padx=10)
        self.language_picker = ttk.Combobox(language_row, textvariable=self.language,
            values=LANGUAGES, state='readonly', font=('Segoe UI', 12), width=24)
        self.language_picker.pack(side='left', fill='x', expand=True)
        self.language_picker.bind('<<ComboboxSelected>>', self.preferences_changed)
        label(language_card, 'Changes apply to your next message. Saved automatically.', True)

        shortcut_card = card()
        shortcut_header = tk.Frame(shortcut_card, bg=CARD)
        shortcut_header.pack(fill='x')
        tk.Label(shortcut_header, text='Translation shortcut', bg=CARD, fg=TEXT,
                 font=('Segoe UI', 12, 'bold')).pack(side='left')
        self.shortcut_button = ttk.Button(shortcut_header, text='Change shortcut',
            style='Small.TButton', command=self.change_shortcut)
        self.shortcut_button.pack(side='right')
        keys = tk.Frame(shortcut_card, bg=CARD)
        keys.pack(anchor='w', pady=(12, 8))
        tk.Label(keys, textvariable=self.shortcut_text, bg='#23334a', fg=TEXT,
                 font=('Segoe UI', 13, 'bold'), padx=12, pady=5, wraplength=500,
                 justify='left').pack(side='left')
        tk.Label(shortcut_card, textvariable=self.shortcut_hint, bg=CARD, fg=MUTED,
                 font=('Segoe UI', 9), wraplength=535, justify='left').pack(anchor='w')

        send_card = card()
        ttk.Checkbutton(send_card, text='Send automatically after translating',
                        variable=self.auto, command=self.preferences_changed).pack(anchor='w')
        label(send_card, 'Turn off to review the translated text before sending.', True)

        status_card = card()
        tk.Label(status_card, textvariable=self.badge, bg=CARD, fg=ACCENT,
                 font=('Segoe UI', 9, 'bold')).pack(anchor='w')
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
        if prepare:
            initial_language = self.language.get()
            def load():
                local = None
                try:
                    local = CodexTranslator(target_language=initial_language)
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
                              shortcut=self.binding)
            except OSError:
                self.status.set('This choice works now, but could not be saved. Check folder permissions.')
                return
        if not self.busy and self.local:
            self.status.set(f'Next message: Norwegian → {self.language.get()}.')

    def apply_shortcut(self, binding):
        self.binding = validate_binding(binding)
        self.cancel.set()
        win.set_binding(self.binding)
        self.shortcut_text.set(binding_label(self.binding))
        self.shortcut_hint.set('Alt + Enter also works. Release the keys and stay in the field.'
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
        message = tk.StringVar(value='Hold Ctrl or Alt, then press your preferred key.\nLeft and right modifier keys are recognised separately.')
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
                self.apply_shortcut({'modifiers': sorted(modifiers), 'key': event.keycode})
            except ValueError as exc:
                message.set(str(exc))
                return 'break'
            dialog.destroy()
            return 'break'
        def released(event):
            modifiers.discard(keysyms.get(event.keysym, event.keycode))
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

    def start(self, minimize=True):
        if self.local is None:
            self.status.set('The translator is not ready yet.')
            return
        if not self.registered:
            self.registered = win.register()
        if not self.registered:
            self.status.set('Could not enable the shortcut. Restart ChatShift.')
            self.badge.set('NEEDS ATTENTION')
            return
        self.stop_button.configure(state='normal')
        self.badge.set('READY')
        self.status.set(f'Active: Norwegian → {self.language.get()}. Ready for {binding_label(self.binding)}.')
        if minimize:
            self.root.iconify()

    def stop(self):
        self.cancel.set()
        if self.registered:
            win.unregister()
            self.registered = False
        self.stop_button.configure(state='disabled')
        self.badge.set('PAUSED')
        self.status.set('Shortcuts are paused. Your keyboard works normally.')

    def trigger(self, target):
        if self.busy or not self.registered or not win.external(target[0]) or self.local is None:
            return
        self.busy = True
        self.cancel = threading.Event()
        cancel = self.cancel
        send = self.auto.get()
        language = self.language.get()
        owner = self.root.winfo_id()
        self.badge.set('TRANSLATING')
        self.status.set(f'Translating to {language}… stay in the same text field.')
        def work():
            try:
                adapter = among_us_mode if among_us_mode.is_among_us(target) else direct_mode
                _, elapsed = adapter.run(target, owner, '', cancel, send=send,
                    translate_fn=lambda text, key: self.local.translate(text, key, target_language=language),
                    progress=lambda message: self.progress.put((message, cancel)))
                result = f'{language} · {elapsed:.2f}s · ' + ('Sent to the chat field.' if send else 'Ready for you to review.')
                error = False
            except Exception as exc:
                result = str(exc) if isinstance(exc, ValueError) else 'Unexpected error. Check the chat field before trying again.'
                error = True
            self.results.put((result, error, cancel))
        threading.Thread(target=work, daemon=True).start()

    def poll(self):
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
            App(tk.Tk(), show_settings='--settings' in sys.argv).root.mainloop()
        finally:
            win.kernel32.CloseHandle(instance)
    else:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo('ChatShift is already running', 'Open ChatShift from your taskbar.')
        root.destroy()
