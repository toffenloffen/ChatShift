"""Explicit translate-and-send transaction for the currently focused field."""
import time
import windows_input as win
from translator import translate


def run(target, owner, key, cancel, send=True, translate_fn=translate, progress=None):
    def report(message):
        if progress:
            progress(message)

    def check():
        if cancel.is_set():
            raise ValueError('Cancelled. Kontroller tekstfeltet før du prøver igjen.')
        win.check_focus(target)

    win.wait_release(target, cancel)
    check()
    def capture(stage, collapse=True):
        report(stage)
        try:
            return win.capture(target, owner, cancel, collapse=collapse)
        except ValueError as exc:
            raise ValueError(stage + ': ' + str(exc)) from exc

    original = capture('Reading your message')
    if not original.strip() or len(original.strip()) > 1000:
        raise ValueError('Write a message of 1–1000 characters in the chat field first.')
    start = time.perf_counter()
    report('Translating… stay in the same text field')
    translated = translate_fn(original, key)
    check()
    if capture('Checking that your original message is unchanged', collapse=False) != original:
        raise ValueError('The text changed during translation. Nothing was replaced.')
    check()
    report('Inserting the translation')
    win.clipboard_write(translated, owner)
    win.shortcut(target, ord('V'))
    time.sleep(0.16)
    check()
    if capture('Verifying the translated text', collapse=False) != translated:
        raise ValueError('Could not verify the pasted text. Enter was not sent; check the field.')
    check()
    if send:
        win.send_enter(target[0], target[1])
    else:
        win.emit([(0x27, 0, 0), (0x27, 0, 2)])
    return translated, time.perf_counter() - start
