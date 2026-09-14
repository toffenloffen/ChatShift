"""Manual integration check against our own disposable Windows text field.

Run: python tests/smoke_desktop.py
Uses a fake translator; no network and no messages sent to external services.
"""
import ctypes as C
import json
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time
import tkinter as tk

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import windows_input as win
import direct_mode

ORIGINAL = 'hei, kan dere vente litt?'
ENGLISH = 'Hi, can you wait a moment?'


def child():
    root = tk.Tk()
    root.title('ChatShift – lokalt testfelt (ingen meldinger publiseres)')
    root.geometry('660x160')
    tk.Label(root, text='Automatisk test av høyre Alt+Enter. Dette vinduet lukkes etter testen.').pack(pady=15)
    entry = tk.Entry(root, font=('Segoe UI', 13), width=60)
    entry.pack(padx=20)
    entry.insert(0, ORIGINAL)
    # Tk Entry does not provide the Windows/browser Ctrl+A convention by default.
    def select_all(event):
        entry.selection_range(0, 'end')
        entry.icursor('end')
        return 'break'
    entry.bind('<Control-a>', select_all)
    if '--debug' in sys.argv:
        entry.bind('<KeyPress>', lambda e: print('TEST KEY', e.keysym, e.state, 'selected', entry.selection_present(), file=sys.stderr, flush=True))
    def submitted(event):
        print(json.dumps({'text': entry.get(), 'state': event.state}), flush=True)
        return 'break'
    entry.bind('<Return>', submitted)
    def ready():
        entry.focus_force()
        root.update()
        print(json.dumps({'target': win.focus_snapshot()}), flush=True)
    root.after(200, ready)
    root.after(60000, root.destroy)
    root.mainloop()


def physical_events(events):
    # Marker 0 acts like another keyboard source, so the hook is tested too.
    inputs = (win.INPUT * len(events))(*[
        win.INPUT(1, win.UNION(ki=win.KEYBDINPUT(vk, scan, flags, 0, 0)))
        for vk, scan, flags in events])
    assert win.user32.SendInput(len(inputs), inputs, C.sizeof(win.INPUT)) == len(inputs)


def main():
    translate_fn = lambda text, key: ENGLISH if text == ORIGINAL else 'WRONG SOURCE'
    expected = ENGLISH
    language = sys.argv[sys.argv.index('--language') + 1] if '--language' in sys.argv else 'English'
    if '--codex' in sys.argv:
        from codex_translator import CodexTranslator
        online = CodexTranslator(target_language=language)
        online.translate('Hei.')  # Match app startup warmup.
        translate_fn = online.translate
        # Verify the exact inserted text against the actual returned translation.
        expected = None
    if '--local' in sys.argv:
        from local_translator import LocalTranslator
        local = LocalTranslator()
        translate_fn = local.translate
        expected = local.translate(ORIGINAL)
    owner = tk.Tk()
    owner.withdraw()
    owner.update()
    process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--child'] + (['--debug'] if '--debug' in sys.argv else []),
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8',
                               creationflags=subprocess.CREATE_NO_WINDOW)
    lines = queue.Queue()
    threading.Thread(target=lambda: [lines.put(json.loads(line)) for line in process.stdout], daemon=True).start()
    threading.Thread(target=lambda: [print(line.rstrip(), file=sys.stderr) for line in process.stderr], daemon=True).start()
    try:
        target = tuple(lines.get(timeout=5)['target'])
        assert win.external(target[0])
        key = ord('T') if '--custom' in sys.argv else 13
        if '--custom' in sys.argv:
            win.set_binding({'modifiers': [0xA0, 0xA2], 'key': key})
        assert win.register()
        # AltGr can arrive as left Ctrl + right Alt on Windows.
        alt_down = [(0xA4, 0x38, 0)] if '--left-alt' in sys.argv else [(0xA2, 0x1D, 0), (0xA5, 0x38, 1)]
        alt_up = [(0xA4, 0x38, 2)] if '--left-alt' in sys.argv else [(0xA5, 0x38, 3), (0xA2, 0x1D, 2)]
        if '--right-ctrl' in sys.argv:
            alt_down = [(0xA3, 0x1D, 1)]
            alt_up = [(0xA3, 0x1D, 3)]
        if '--custom' in sys.argv:
            alt_down = [(0xA2, 0x1D, 0), (0xA0, 0x2A, 0)]
            alt_up = [(0xA0, 0x2A, 2), (0xA2, 0x1D, 2)]
        physical_events(alt_down)
        time.sleep(0.05)
        physical_events([(key, 0, 0), (key, 0, 2)])
        time.sleep(0.05)
        physical_events(alt_up)
        deadline = time.monotonic() + 2
        observed = None
        while not observed and time.monotonic() < deadline:
            observed = win.poll_hotkey()
            time.sleep(0.01)
        assert observed == target, ('hotkey target', observed, target)
        time.sleep(0.1)
        assert lines.empty(), 'Original Enter leaked into the text field'
        if '--caret-move' in sys.argv:
            original_translator = translate_fn
            def translate_with_caret_move(text, key):
                physical_events([(0x25, 0, 0), (0x25, 0, 2)])
                time.sleep(0.1)
                return original_translator(text, key)
            translate_fn = translate_with_caret_move
        if '--repeat-hotkey' in sys.argv:
            underlying = translate_fn
            def translate_with_repeat(text, api_key):
                before = win.last_input()
                physical_events(alt_down)
                time.sleep(0.05)
                physical_events([(key, 0, 0), (key, 0, 2)])
                time.sleep(0.05)
                physical_events(alt_up)
                time.sleep(0.1)
                assert win.poll_hotkey() == target
                assert win.last_input() == before, 'Repeated hotkey cancels translation'
                return underlying(text, api_key)
            translate_fn = translate_with_repeat
        completed = queue.Queue()
        clipboard_owner = owner.winfo_id()
        def run_translation():
            try:
                completed.put(direct_mode.run(target, clipboard_owner, 'fake', threading.Event(),
                    translate_fn=translate_fn))
            except Exception as exc:
                completed.put(exc)
        threading.Thread(target=run_translation, daemon=True).start()
        deadline = time.monotonic() + (40 if '--codex' in sys.argv else 5)
        while completed.empty() and time.monotonic() < deadline:
            owner.update()
            time.sleep(0.005)
        outcome = completed.get(timeout=1)
        if isinstance(outcome, Exception):
            raise outcome
        result, elapsed = outcome
        submitted = lines.get(timeout=2)
        if expected is None:
            expected = result
            stem = {'English': 'wait', 'French': 'attend', 'German': 'wart', 'Spanish': 'esper'}[language]
            assert result != ORIGINAL and stem in result.lower(), result
        assert result == expected and submitted['text'] == expected, submitted
        assert not submitted['state'] & 4, 'Ctrl was still pressed during sending'
        physical_events([(0xA2, 0x1D, 0), (13, 0, 0), (13, 0, 2), (0xA2, 0x1D, 2)])
        left = lines.get(timeout=2)
        assert left['state'] & 4, 'Left Ctrl+Enter did not pass through'
        assert win.poll_hotkey() is None
        if '--custom' in sys.argv:
            physical_events([(0xA3, 0x1D, 1), (13, 0, 0), (13, 0, 2), (0xA3, 0x1D, 3)])
            old = lines.get(timeout=2)
            assert old['state'] & 4, 'Old Right Ctrl+Enter shortcut did not pass through'
            assert win.poll_hotkey() is None, 'Old shortcut is still active'
        win.send_enter(target[0], target[1])
        plain = lines.get(timeout=2)
        assert not plain['state'] & 4
        mode = 'ChatGPT via Codex' if '--codex' in sys.argv else ('local model' if '--local' in sys.argv else 'fake translation')
        side = 'left Alt' if '--left-alt' in sys.argv else 'right Alt/AltGr'
        if '--right-ctrl' in sys.argv:
            side = 'right Ctrl'
        if '--custom' in sys.argv:
            side = 'custom Ctrl+Shift+T'
        print(f'PASS: {side} intercepted; {language} replaced and sent; left Ctrl and plain Enter preserved ({elapsed:.2f}s, {mode}).')
        print('Result:', expected)
    finally:
        win.unregister()
        win.set_binding(None)
        if '--codex' in sys.argv:
            online.close()
        process.terminate()
        process.wait(timeout=3)
        owner.destroy()


if __name__ == '__main__':
    child() if '--child' in sys.argv else main()
