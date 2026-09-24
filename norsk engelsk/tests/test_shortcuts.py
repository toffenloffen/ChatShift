import unittest
from shortcuts import validate_binding, binding_label, NUMPAD_ENTER
from windows_input import HotkeyState, mouse_button_event, keyboard_key


class ShortcutTests(unittest.TestCase):
    def test_custom_combination_replaces_old_combination(self):
        state = HotkeyState({'modifiers': [0xA0, 0xA2], 'key': ord('T')})
        state.feed(0xA3, True)
        self.assertEqual(state.feed(13, True), (False, False))
        state.feed(0xA3, False)
        state.feed(0xA0, True)
        state.feed(0xA2, True)
        self.assertEqual(state.feed(ord('T'), True), (True, True))
        self.assertEqual(state.feed(ord('T'), True), (True, False))
        self.assertEqual(state.feed(ord('T'), False), (True, False))

    def test_typing_and_own_injected_keys_are_not_captured(self):
        state = HotkeyState({'modifiers': [0xA2], 'key': ord('T')})
        self.assertEqual(state.feed(ord('T'), True), (False, False))
        state.feed(0xA2, True)
        self.assertEqual(state.feed(ord('T'), True, own=True), (False, False))
        self.assertEqual(state.feed(ord('T'), True, allow=False), (False, False))

    def test_altgr_synthetic_control_matches_custom_binding(self):
        state = HotkeyState({'modifiers': [0xA5], 'key': 112})
        state.feed(0xA2, True)
        state.feed(0xA5, True)
        self.assertEqual(state.feed(112, True), (True, True))

    def test_rebinding_while_held_still_swallows_original_release(self):
        state = HotkeyState({'modifiers': [0xA2], 'key': ord('T')})
        state.feed(0xA2, True)
        state.feed(ord('T'), True)
        state.binding = {'modifiers': [0xA2], 'key': ord('Y')}
        self.assertEqual(state.feed(ord('T'), False), (True, False))

    def test_invalid_bindings_do_not_intercept_normal_typing(self):
        for binding in ({'modifiers': [0x5B], 'key': 76}, {'modifiers': [0xA2], 'key': True},
                        {'modifiers': 'Ctrl', 'key': 65}):
            with self.subTest(binding=binding), self.assertRaises(ValueError):
                validate_binding(binding)

    def test_every_selectable_key_works_alone(self):
        from shortcuts import KEY_NAMES
        for key in KEY_NAMES:
            with self.subTest(key=key):
                state = HotkeyState({'modifiers': [], 'key': key})
                if key == 0xA5:
                    state.feed(0xA2, True)  # AltGr's synthetic Ctrl.
                self.assertEqual(state.feed(key, True), (True, True))
                self.assertEqual(state.feed(key, True), (True, False))
                self.assertEqual(state.feed(key, False), (True, False))

    def test_right_alt_alone_does_not_match_left_alt(self):
        state = HotkeyState({'modifiers': [], 'key': 0xA5})
        self.assertEqual(state.feed(0xA4, True), (False, False))
        state.feed(0xA4, False)
        state.feed(0xA2, True)
        self.assertEqual(state.feed(0xA5, True), (True, True))

    def test_readable_label(self):
        self.assertEqual(binding_label({'modifiers': [0xA0, 0xA2], 'key': 84}), 'Left Ctrl + Left Shift + T')

    def test_numpad_enter_is_distinct_from_main_enter(self):
        self.assertEqual(keyboard_key(13, 0), 13)
        self.assertEqual(keyboard_key(13, 1), NUMPAD_ENTER)
        for configured, other in ((13, NUMPAD_ENTER), (NUMPAD_ENTER, 13)):
            state = HotkeyState({'modifiers': [0xA3], 'key': configured})
            state.feed(0xA3, True)
            self.assertEqual(state.feed(other, True), (False, False))
            self.assertEqual(state.feed(configured, True), (True, True))
            self.assertEqual(state.feed(configured, False), (True, False))
        self.assertEqual(binding_label({'modifiers': [], 'key': NUMPAD_ENTER}), 'Num Enter')

    def test_default_does_not_accept_numpad_enter(self):
        state = HotkeyState()
        state.feed(0xA3, True)
        self.assertEqual(state.feed(NUMPAD_ENTER, True), (False, False))

    def test_no_shortcut_intercepts_neither_enter_nor_mouse(self):
        state = HotkeyState({'modifiers': [], 'key': None})
        state.feed(0xA3, True)
        for key in (13, NUMPAD_ENTER, 121, 4, 5, 6):
            self.assertEqual(state.feed(key, True), (False, False))

    def test_f10_alone_triggers_once_and_keeps_typing_untouched(self):
        binding = validate_binding({'modifiers': [], 'key': 121})
        self.assertEqual(binding_label(binding), 'F10')
        state = HotkeyState(binding)
        self.assertEqual(state.feed(65, True), (False, False))
        self.assertEqual(state.feed(121, True), (True, True))
        self.assertEqual(state.feed(121, True), (True, False))
        self.assertEqual(state.feed(121, False), (True, False))
        self.assertEqual(state.feed(121, True), (True, True))

    def test_mouse_buttons_map_and_repeat_suppression(self):
        self.assertEqual(mouse_button_event(0x0207, 0), (4, True))
        self.assertEqual(mouse_button_event(0x0208, 0), (4, False))
        self.assertEqual(mouse_button_event(0x020B, 1 << 16), (5, True))
        self.assertEqual(mouse_button_event(0x020C, 2 << 16), (6, False))
        self.assertIsNone(mouse_button_event(0x020B, 3 << 16))
        self.assertIsNone(mouse_button_event(0x020A, 0))
        state = HotkeyState({'modifiers': [], 'key': 4})
        self.assertEqual(state.feed(4, True, allow=False), (False, False))
        self.assertEqual(state.feed(4, True), (True, True))
        self.assertEqual(state.feed(4, True), (True, False))
        self.assertEqual(state.feed(4, False), (True, False))
