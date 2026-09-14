"""Experimental visual adapter for the tested Among Us 16:9 free-chat layout."""
import ctypes as C
from ctypes import wintypes as W
from pathlib import PureWindowsPath
import time
import windows_input as win


def is_among_us(target):
    kernel = win.kernel32
    kernel.OpenProcess.argtypes = [W.DWORD, W.BOOL, W.DWORD]
    kernel.OpenProcess.restype = W.HANDLE
    kernel.QueryFullProcessImageNameW.argtypes = [W.HANDLE, W.DWORD, W.LPWSTR, C.POINTER(W.DWORD)]
    handle = kernel.OpenProcess(0x1000, False, target[1])
    if not handle:
        return False
    try:
        path, size = C.create_unicode_buffer(32768), W.DWORD(32768)
        return bool(kernel.QueryFullProcessImageNameW(handle, 0, path, C.byref(size)) and
                    PureWindowsPath(path.value).name.lower() == 'among us.exe')
    finally:
        kernel.CloseHandle(handle)


def read_field(target):
    try:
        from PIL import ImageGrab
        from among_us_ocr import read_image
    except ImportError as exc:
        raise ValueError('Among Us support needs the optional OCR dependencies. Run setup_ocr.ps1.') from exc
    win.check_focus(target)
    rect = W.RECT()
    if not win.user32.GetWindowRect(target[0], C.byref(rect)):
        raise ValueError('Could not locate the game window.')
    image = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom), all_screens=True)
    win.check_focus(target)
    # The full frame only exists in memory; the OCR reader crops the outgoing field.
    try:
        return read_image(image)
    except ImportError as exc:
        raise ValueError('Among Us support needs the optional OCR dependencies. Run setup_ocr.ps1.') from exc
    finally:
        image.close()


def press(target, vk, cancel, modifiers=()):
    if cancel.is_set():
        raise ValueError('Cancelled. Check the chat field before retrying.')
    win.check_focus(target)
    held = []
    try:
        for modifier in modifiers:
            win.emit([(modifier, 0, 0)])
            held.append(modifier)
        win.emit([(vk, 0, 0)])
        held.append(vk)
        time.sleep(.04)
    finally:
        # Release even if focus changes; never leave injected modifiers held down.
        for key in reversed(held):
            win.emit([(key, 0, 2)])
    time.sleep(.025)


def encode_keys(target, text):
    win.user32.GetKeyboardLayout.argtypes = [W.DWORD]
    win.user32.GetKeyboardLayout.restype = W.HANDLE
    win.user32.VkKeyScanExW.argtypes = [W.WCHAR, W.HANDLE]
    win.user32.VkKeyScanExW.restype = C.c_short
    thread = win.user32.GetWindowThreadProcessId(target[0], None)
    layout = win.user32.GetKeyboardLayout(thread)
    keys = []
    for char in text:
        value = win.user32.VkKeyScanExW(char, layout)
        if value == -1 or value >> 8 & ~7:
            raise ValueError('This translation contains characters the game keyboard adapter cannot type.')
        flags = value >> 8
        modifiers = tuple(key for bit, key in ((1, 0x10), (2, 0x11), (4, 0x12)) if flags & bit)
        keys.append((value & 255, modifiers))
    return keys


def run(target, owner, key, cancel, send=True, translate_fn=None, progress=None):
    def report(text):
        if progress:
            progress(text)
    def check():
        if cancel.is_set():
            raise ValueError('Cancelled. Check the chat field before retrying.')
        win.check_focus(target)
    win.wait_release(target, cancel)
    report('Among Us: reading the chat field locally…')
    original = read_field(target)
    if not original or original.startswith('/'):
        raise ValueError('Write a short message in the Among Us chat field first.')
    start = time.perf_counter()
    report('Among Us: translating… stay in the same chat field')
    translated = translate_fn(original, key)
    if not translated or len(translated) > 100 or any(ord(c) < 32 for c in translated) or translated.startswith('/'):
        raise ValueError('The translation must fit the game’s 100-character chat limit. Shorten your message.')
    keys = encode_keys(target, translated)  # Validate everything before changing the draft.
    check()
    if read_field(target) != original:
        raise ValueError('The game draft changed. Nothing was replaced.')
    report('Among Us: replacing the draft… do not type')
    press(target, 0x23, cancel)  # End, before removing only the known draft length.
    for _ in original:
        press(target, 0x08, cancel)
    time.sleep(.2)  # Let the game render the edited field before OCR readback.
    check()
    if read_field(target) != '':
        raise ValueError('The game draft could not be cleared. Check the field; nothing was sent.')
    for vk, modifiers in keys:
        press(target, vk, cancel, modifiers)
    time.sleep(.2)
    check()
    if read_field(target) != translated:
        raise ValueError('Could not verify the translated game text. Check the field; Enter was not sent.')
    check()
    if send:
        press(target, 0x0D, cancel)
    return translated, time.perf_counter() - start
