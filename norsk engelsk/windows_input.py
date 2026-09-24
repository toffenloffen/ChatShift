"""Windows input adapter. Tracks modifier state, never records typed characters."""
import ctypes as C
from ctypes import wintypes as W
import os
import queue
import threading
import time
import uuid
from shortcuts import validate_binding, normalize_modifiers, NUMPAD_ENTER

user32 = C.WinDLL('user32', use_last_error=True)
kernel32 = C.WinDLL('kernel32', use_last_error=True)
OWN_INPUT = 0x53505254
user32.GetForegroundWindow.restype = W.HWND
user32.GetWindowThreadProcessId.argtypes = [W.HWND, C.POINTER(W.DWORD)]
user32.IsWindow.argtypes = [W.HWND]
user32.SetForegroundWindow.argtypes = [W.HWND]
user32.GetMessageW.argtypes = [C.POINTER(W.MSG), W.HWND, W.UINT, W.UINT]
user32.PostThreadMessageW.argtypes = [W.DWORD, W.UINT, W.WPARAM, W.LPARAM]


class KEYBDINPUT(C.Structure):
    _fields_ = [('wVk', W.WORD), ('wScan', W.WORD), ('dwFlags', W.DWORD),
                ('time', W.DWORD), ('dwExtraInfo', C.c_size_t)]


class MOUSEINPUT(C.Structure):
    _fields_ = [('dx', W.LONG), ('dy', W.LONG), ('mouseData', W.DWORD),
               ('dwFlags', W.DWORD), ('time', W.DWORD), ('dwExtraInfo', C.c_size_t)]


class UNION(C.Union):
    _fields_ = [('ki', KEYBDINPUT), ('mi', MOUSEINPUT)]


class INPUT(C.Structure):
    _fields_ = [('type', W.DWORD), ('value', UNION)]


class KBDLLHOOKSTRUCT(C.Structure):
    _fields_ = [('vkCode', W.DWORD), ('scanCode', W.DWORD), ('flags', W.DWORD),
                ('time', W.DWORD), ('dwExtraInfo', C.c_size_t)]


class MSLLHOOKSTRUCT(C.Structure):
    _fields_ = [('pt', W.POINT), ('mouseData', W.DWORD), ('flags', W.DWORD),
                ('time', W.DWORD), ('dwExtraInfo', C.c_size_t)]


def mouse_button_event(message, data):
    if message in (0x0207, 0x0208):
        return 4, message == 0x0207
    if message in (0x020B, 0x020C):
        button = (data >> 16) & 0xFFFF
        if button in (1, 2):
            return 4 + button, message == 0x020B
    return None


def keyboard_key(vk, flags):
    return NUMPAD_ENTER if vk == 13 and flags & 0x01 else vk


class GUITHREADINFO(C.Structure):
    _fields_ = [('cbSize', W.DWORD), ('flags', W.DWORD),
                ('hwndActive', W.HWND), ('hwndFocus', W.HWND),
                ('hwndCapture', W.HWND), ('hwndMenuOwner', W.HWND),
                ('hwndMoveSize', W.HWND), ('hwndCaret', W.HWND), ('rcCaret', W.RECT)]


class LASTINPUTINFO(C.Structure):
    _fields_ = [('cbSize', W.UINT), ('dwTime', W.DWORD)]


HOOKPROC = C.WINFUNCTYPE(C.c_ssize_t, C.c_int, W.WPARAM, W.LPARAM)
user32.SetWindowsHookExW.argtypes = [C.c_int, HOOKPROC, W.HINSTANCE, W.DWORD]
user32.SetWindowsHookExW.restype = W.HANDLE
user32.UnhookWindowsHookEx.argtypes = [W.HANDLE]
user32.CallNextHookEx.argtypes = [W.HANDLE, C.c_int, W.WPARAM, W.LPARAM]
user32.CallNextHookEx.restype = C.c_ssize_t
kernel32.GetModuleHandleW.argtypes = [W.LPCWSTR]
kernel32.GetModuleHandleW.restype = W.HMODULE
user32.SendInput.argtypes = [W.UINT, C.POINTER(INPUT), C.c_int]
user32.SendInput.restype = W.UINT
user32.GetGUIThreadInfo.argtypes = [W.DWORD, C.POINTER(GUITHREADINFO)]
user32.GetLastInputInfo.argtypes = [C.POINTER(LASTINPUTINFO)]
user32.OpenClipboard.argtypes = [W.HWND]
user32.GetClipboardData.argtypes = [W.UINT]
user32.GetClipboardData.restype = W.HANDLE
user32.SetClipboardData.argtypes = [W.UINT, W.HANDLE]
user32.SetClipboardData.restype = W.HANDLE
user32.GetClipboardSequenceNumber.restype = W.DWORD
kernel32.GlobalAlloc.argtypes = [W.UINT, C.c_size_t]
kernel32.GlobalAlloc.restype = W.HGLOBAL
kernel32.GlobalLock.argtypes = [W.HGLOBAL]
kernel32.GlobalLock.restype = C.c_void_p
kernel32.GlobalUnlock.argtypes = [W.HGLOBAL]
kernel32.GlobalFree.argtypes = [W.HGLOBAL]
kernel32.GlobalSize.argtypes = [W.HGLOBAL]
kernel32.GlobalSize.restype = C.c_size_t
kernel32.CreateMutexW.argtypes = [C.c_void_p, W.BOOL, W.LPCWSTR]
kernel32.CreateMutexW.restype = W.HANDLE
kernel32.CloseHandle.argtypes = [W.HANDLE]
_hotkeys = queue.Queue()
_hotkey_thread = None
_listener = None
_binding = None
_voice_binding = {'modifiers': [], 'key': None}
_voice_enabled = False
_text_enabled = True
_voice_events = queue.Queue()


def configure_modes(text_enabled, voice_enabled, voice_binding):
    global _text_enabled, _voice_enabled, _voice_binding
    _text_enabled = bool(text_enabled)
    _voice_enabled = bool(voice_enabled)
    _voice_binding = validate_binding(voice_binding)


def poll_voice():
    try:
        return _voice_events.get_nowait()
    except queue.Empty:
        return None


class HotkeyTarget(tuple):
    """Window identity with a monotonic shortcut timestamp, never typed text."""
    def __new__(cls, target):
        value = super().__new__(cls, target)
        value.pressed_at = time.perf_counter()
        return value


def set_binding(binding):
    global _binding
    _binding = validate_binding(binding)
_input_revision = 0
_diagnostics = {'right_alt_enter': 0, 'left_alt_enter': 0, 'right_ctrl_enter': 0, 'left_ctrl_enter': 0, 'intercepted': 0}


def diagnostics():
    return dict(_diagnostics, listener_running=bool(_listener and _listener.is_alive()))


def acquire_instance():
    # Keep the legacy mutex so an older running version cannot capture shortcuts too.
    handle = kernel32.CreateMutexW(None, False, 'Local\\Spillprat.RightCtrlEnter')
    if not handle:
        raise OSError('Could not start ChatShift.')
    if C.get_last_error() == 183:
        kernel32.CloseHandle(handle)
        return None
    return handle


class HotkeyState:
    """Alt + Enter, accepting either side and synthetic left Ctrl for AltGr."""
    MODIFIERS = {0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0x5B, 0x5C}

    def __init__(self, binding=None):
        self.modifiers = set()
        self.swallowed = False
        self.swallowed_key = None
        self.binding = validate_binding(binding)

    def feed(self, vk, down, own=False, allow=True):
        if own:
            return False, False
        if vk in self.MODIFIERS:
            if down:
                self.modifiers.add(vk)
            else:
                self.modifiers.discard(vk)
        if self.swallowed and vk == self.swallowed_key:
            if not down:
                self.swallowed = False
                self.swallowed_key = None
            return True, False
        if self.binding is None:
            matches = vk == 13 and self.modifiers in ({0xA3}, {0xA5}, {0xA2, 0xA5}, {0xA4}, {0xA2, 0xA4})
        else:
            held = normalize_modifiers(self.modifiers)
            if self.binding['key'] in self.MODIFIERS:
                held.discard(self.binding['key'])
            matches = (vk == self.binding['key'] and
                       held == set(self.binding['modifiers']))
        if down and matches and allow:
            self.swallowed = True
            self.swallowed_key = vk
            return True, True
        return False, False


def foreground():
    return user32.GetForegroundWindow()


def identity(hwnd):
    pid = W.DWORD()
    user32.GetWindowThreadProcessId(hwnd, C.byref(pid))
    return pid.value


def external(hwnd):
    return bool(hwnd and user32.IsWindow(hwnd) and identity(hwnd) != os.getpid())


def focus_snapshot():
    hwnd = foreground()
    info = GUITHREADINFO(cbSize=C.sizeof(GUITHREADINFO))
    if not hwnd or not user32.GetGUIThreadInfo(0, C.byref(info)) or not info.hwndFocus:
        raise ValueError('No active text field was found.')
    return hwnd, identity(hwnd), info.hwndFocus


def register():
    global _listener
    if _listener and _listener.is_alive():
        return True
    while poll_hotkey():
        pass
    while poll_voice():
        pass
    ready = queue.Queue()
    def listen():
        global _hotkey_thread
        _hotkey_thread = kernel32.GetCurrentThreadId()
        state = HotkeyState(_binding)
        voice_state = HotkeyState(_voice_binding)
        def voice_feed(key, down, own):
            voice_state.binding = _voice_binding
            if down and not own and key == _voice_binding['key']:
                voice_state.modifiers = {vk for vk in voice_state.MODIFIERS
                                        if user32.GetAsyncKeyState(vk) & 0x8000}
            released = not down and voice_state.swallowed and key == voice_state.swallowed_key
            swallowed, triggered = voice_state.feed(key, down, own=own,
                allow=_voice_enabled and external(foreground()))
            if triggered:
                try:
                    _diagnostics['voice_shortcut_down'] = _diagnostics.get('voice_shortcut_down', 0) + 1
                    if voice_state.modifiers & {0xA4, 0xA5}:
                        emit([(0xE8, 0, 0), (0xE8, 0, 2)])
                    _voice_events.put(('down', HotkeyTarget(focus_snapshot()), last_input()))
                except ValueError:
                    pass
            if released and not own:
                _diagnostics['voice_shortcut_up'] = _diagnostics.get('voice_shortcut_up', 0) + 1
                _voice_events.put(('up', None, last_input()))
            return swallowed
        state.modifiers = {vk for vk in state.MODIFIERS if user32.GetAsyncKeyState(vk) & 0x8000}
        @HOOKPROC
        def callback(code, message, pointer):
            global _input_revision
            if code >= 0:
                event = C.cast(pointer, C.POINTER(KBDLLHOOKSTRUCT)).contents
                state.binding = _binding
                down = message in (0x0100, 0x0104)
                key = keyboard_key(event.vkCode, event.flags)
                if voice_feed(key, down, event.dwExtraInfo == OWN_INPUT):
                    return 1
                candidate = key == (state.binding['key'] if state.binding else 13)
                if candidate and down and event.dwExtraInfo != OWN_INPUT:
                    # Reconcile held modifiers before matching a trigger. A key-up can
                    # be missed when another application changes input capture.
                    state.modifiers = {vk for vk in state.MODIFIERS
                                       if user32.GetAsyncKeyState(vk) & 0x8000}
                    _diagnostics['shortcut_key_seen'] = _diagnostics.get('shortcut_key_seen', 0) + 1
                    _diagnostics['shortcut_modifiers'] = sorted(state.modifiers)
                    _diagnostics['shortcut_external'] = external(foreground())
                if event.vkCode == 13 and down and event.dwExtraInfo != OWN_INPUT:
                    # Only count the requested shortcut and its left-side counterpart.
                    # No typed text or ordinary key events are retained.
                    if 0xA5 in state.modifiers:
                        _diagnostics['right_alt_enter'] += 1
                    elif 0xA4 in state.modifiers:
                        _diagnostics['left_alt_enter'] += 1
                    elif 0xA3 in state.modifiers:
                        _diagnostics['right_ctrl_enter'] += 1
                    elif 0xA2 in state.modifiers:
                        _diagnostics['left_ctrl_enter'] += 1
                swallow, trigger = state.feed(key, down,
                    own=event.dwExtraInfo == OWN_INPUT,
                    allow=_text_enabled and external(foreground()))
                if (down and event.dwExtraInfo != OWN_INPUT and not swallow
                        and event.vkCode not in state.MODIFIERS):
                    # Repeating the shortcut must not cancel a pending translation.
                    # Count other keyboard activity without retaining its contents.
                    _input_revision += 1
                if trigger:
                    _diagnostics['intercepted'] += 1
                    try:
                        # An otherwise-unused key prevents Alt release opening
                        # the application's menu after Enter was suppressed.
                        if state.modifiers & {0xA4, 0xA5}:
                            emit([(0xE8, 0, 0), (0xE8, 0, 2)])
                        _hotkeys.put(HotkeyTarget(focus_snapshot()))
                    except ValueError:
                        _diagnostics['shortcut_focus_failed'] = _diagnostics.get('shortcut_focus_failed', 0) + 1
                        pass
                if swallow:
                    return 1
            return user32.CallNextHookEx(None, code, message, pointer)
        @HOOKPROC
        def mouse_callback(code, message, pointer):
            global _input_revision
            if code >= 0:
                event = C.cast(pointer, C.POINTER(MSLLHOOKSTRUCT)).contents
                button = mouse_button_event(message, event.mouseData)
                if button:
                    vk, down = button
                    if voice_feed(vk, down, event.dwExtraInfo == OWN_INPUT):
                        return 1
                    state.binding = _binding
                    if state.binding and vk == state.binding['key'] and down and event.dwExtraInfo != OWN_INPUT:
                        state.modifiers = {mod for mod in state.MODIFIERS
                                           if user32.GetAsyncKeyState(mod) & 0x8000}
                        _diagnostics['shortcut_key_seen'] = _diagnostics.get('shortcut_key_seen', 0) + 1
                        _diagnostics['shortcut_modifiers'] = sorted(state.modifiers)
                        _diagnostics['shortcut_external'] = external(foreground())
                    swallow, trigger = state.feed(vk, down, own=event.dwExtraInfo == OWN_INPUT,
                        allow=_text_enabled and external(foreground()))
                    if trigger:
                        try:
                            _hotkeys.put(HotkeyTarget(focus_snapshot()))
                            _diagnostics['intercepted'] += 1
                        except ValueError:
                            pass
                    if swallow:
                        return 1
                if message in (0x0201, 0x0204, 0x0207, 0x020B) and event.dwExtraInfo != OWN_INPUT:
                    _input_revision += 1
            return user32.CallNextHookEx(None, code, message, pointer)

        hook = user32.SetWindowsHookExW(13, callback, kernel32.GetModuleHandleW(None), 0)
        mouse_hook = user32.SetWindowsHookExW(14, mouse_callback, kernel32.GetModuleHandleW(None), 0)
        ready.put(bool(hook and mouse_hook))
        if not hook or not mouse_hook:
            if hook:
                user32.UnhookWindowsHookEx(hook)
            if mouse_hook:
                user32.UnhookWindowsHookEx(mouse_hook)
            return
        msg = W.MSG()
        try:
            while user32.GetMessageW(C.byref(msg), None, 0, 0) > 0:
                pass
        finally:
            user32.UnhookWindowsHookEx(hook)
            user32.UnhookWindowsHookEx(mouse_hook)
    _listener = threading.Thread(target=listen, daemon=True)
    _listener.start()
    return ready.get(timeout=3)


def unregister():
    if _hotkey_thread and _listener and _listener.is_alive():
        user32.PostThreadMessageW(_hotkey_thread, 0x0012, 0, 0)
        _listener.join(timeout=1)


def poll_hotkey():
    try:
        return _hotkeys.get_nowait()
    except queue.Empty:
        return None


def check_target(hwnd, pid):
    if foreground() != hwnd or identity(hwnd) != pid or not external(hwnd):
        raise ValueError('The active window changed. Sending was stopped.')
    if any(user32.GetAsyncKeyState(vk) & 0x8000 for vk in (0x10, 0x11, 0x12, 0x5B, 0x5C)):
        raise ValueError('Release the modifier keys before sending.')


def check_focus(target):
    if focus_snapshot() != target:
        raise ValueError('The window or text field changed. Nothing else will be sent.')
    check_target(target[0], target[1])


def last_input():
    return _input_revision


def wait_release(target, cancel, binding=None):
    deadline = time.monotonic() + 3
    current = _binding if binding is None else binding
    trigger_key = (current['key'] if current else 0x0D) or 0x0D
    if trigger_key == NUMPAD_ENTER:
        trigger_key = 13
    while any(user32.GetAsyncKeyState(vk) & 0x8000 for vk in (trigger_key, 0x10, 0x11, 0x12, 0x5B, 0x5C)):
        if cancel.is_set() or focus_snapshot() != target:
            raise ValueError('Cancelled.')
        if time.monotonic() > deadline:
            raise ValueError('Release the shortcut keys and try again.')
        time.sleep(0.015)
    check_focus(target)


def emit(events):
    inputs = (INPUT * len(events))(*[INPUT(1, UNION(ki=KEYBDINPUT(vk, scan, flags, 0, OWN_INPUT)))
                                  for vk, scan, flags in events])
    if user32.SendInput(len(inputs), inputs, C.sizeof(INPUT)) != len(inputs):
        raise ValueError('Windows blocked the keystrokes. Check the text field.')


def shortcut(target, vk):
    check_focus(target)
    emit([(0x11, 0, 0), (vk, 0, 0), (vk, 0, 2), (0x11, 0, 2)])


def send_enter(hwnd, pid):
    check_target(hwnd, pid)
    emit([(0x0D, 0, 0), (0x0D, 0, 2)])


def clipboard_open(owner=0):
    deadline = time.monotonic() + 0.5
    while not user32.OpenClipboard(owner):
        if time.monotonic() > deadline:
            raise ValueError('The clipboard is busy. Try again.')
        time.sleep(0.01)


def clipboard_write(text, owner):
    raw = (text + '\0').encode('utf-16-le')
    handle = kernel32.GlobalAlloc(0x0002, len(raw))
    if not handle:
        raise ValueError('Could not prepare the clipboard.')
    try:
        pointer = kernel32.GlobalLock(handle)
        if not pointer:
            raise ValueError('Could not prepare the clipboard.')
        try:
            C.memmove(pointer, raw, len(raw))
        finally:
            kernel32.GlobalUnlock(handle)
        clipboard_open(owner)
        try:
            if not user32.EmptyClipboard() or not user32.SetClipboardData(13, handle):
                raise ValueError('Could not write to the clipboard.')
            handle = None
        finally:
            user32.CloseClipboard()
    finally:
        if handle:
            kernel32.GlobalFree(handle)


def clipboard_read():
    clipboard_open()
    try:
        handle = user32.GetClipboardData(13)
        if not handle:
            return None
        size = kernel32.GlobalSize(handle)
        if size > 20004:
            raise ValueError('Too much text was selected. Use a chat field with a short message.')
        pointer = kernel32.GlobalLock(handle)
        if not pointer:
            raise ValueError('Could not read the text.')
        try:
            return C.string_at(pointer, size).decode('utf-16-le').split('\0', 1)[0]
        finally:
            kernel32.GlobalUnlock(handle)
    finally:
        user32.CloseClipboard()


def capture(target, owner, cancel, collapse=True, preserve_clipboard=False):
    check_focus(target)
    marker = 'chatshift-' + uuid.uuid4().hex
    if not preserve_clipboard:
        clipboard_write(marker, owner)
    sequence = user32.GetClipboardSequenceNumber()
    shortcut(target, ord('A'))
    time.sleep(0.06)
    if preserve_clipboard:
        # Keep the paste payload available until the target processes Ctrl+V.
        # Only a fresh clipboard update after selection may count as readback;
        # the existing translated clipboard text alone never proves insertion.
        sequence = user32.GetClipboardSequenceNumber()
    shortcut(target, ord('C'))
    deadline = time.monotonic() + 1
    text = None
    while time.monotonic() < deadline:
        if cancel.is_set():
            raise ValueError('Cancelled.')
        check_focus(target)
        if user32.GetClipboardSequenceNumber() != sequence:
            text = clipboard_read()
            if text is not None and text != marker:
                break
        time.sleep(0.02)
    if text is None or text == marker:
        raise ValueError('The field is empty or does not support copying. Nothing was sent.')
    if collapse:
        check_focus(target)
        emit([(0x27, 0, 0), (0x27, 0, 2)])
        # No readback depends on the caret repaint. Input stays ordered and the
        # transaction verifies the draft again after translation.
    return text
