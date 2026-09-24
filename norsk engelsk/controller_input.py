"""Controller polling and portable button-chord edge detection."""
import ctypes as C

BUTTONS = {'D-pad Up': 1, 'D-pad Down': 2, 'D-pad Left': 4, 'D-pad Right': 8,
           'Menu': 16, 'View': 32, 'Left stick click': 64, 'Right stick click': 128,
           'LB': 256, 'RB': 512, 'A': 4096, 'B': 8192, 'X': 16384, 'Y': 32768,
           'LT': 65536, 'RT': 131072}


def validate_chord(value):
    if not isinstance(value, list) or len(value) > 3 or any(x not in BUTTONS for x in value):
        raise ValueError('Choose up to three controller buttons.')
    return sorted(set(value), key=lambda x: list(BUTTONS).index(x))


class ChordEdges:
    """Require a neutral state after activation/reconnection; never repeat a hold."""
    def __init__(self):
        self.reset()

    def reset(self):
        self.armed = False
        self.down = False

    def update(self, pressed, chord):
        if pressed is None:
            was_down = self.down
            self.reset()
            return 'cancel' if was_down else None
        if not self.armed:
            self.armed = not pressed
            return None
        matched = bool(chord) and set(chord) == set(pressed)
        if matched == self.down:
            return None
        self.down = matched
        if not matched and set(pressed) - set(chord):
            self.armed = False
            return 'cancel'
        return 'down' if matched else 'up'


class Gamepad(C.Structure):
    _fields_ = [('buttons', C.c_ushort), ('left_trigger', C.c_ubyte),
                ('right_trigger', C.c_ubyte), ('lx', C.c_short), ('ly', C.c_short),
                ('rx', C.c_short), ('ry', C.c_short)]


class State(C.Structure):
    _fields_ = [('packet', C.c_uint32), ('pad', Gamepad)]


class XInput:
    def __init__(self):
        self.get_state = None
        for name in ('xinput1_4', 'xinput1_3', 'xinput9_1_0'):
            try:
                self.dll = C.WinDLL(name)
                self.get_state = self.dll.XInputGetState
                self.get_state.argtypes = [C.c_uint32, C.POINTER(State)]
                self.get_state.restype = C.c_uint32
                break
            except (OSError, AttributeError):
                pass

    def read(self, index):
        state = State()
        if self.get_state is None or self.get_state(index, C.byref(state)) != 0:
            return None
        mask = state.pad.buttons
        if state.pad.left_trigger > 30:
            mask |= BUTTONS['LT']
        if state.pad.right_trigger > 30:
            mask |= BUTTONS['RT']
        return {name for name, bit in BUTTONS.items() if mask & bit}
