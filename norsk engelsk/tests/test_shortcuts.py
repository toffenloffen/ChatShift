import unittest
from shortcuts import validate_binding, binding_label
from windows_input import HotkeyState


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
        for binding in ({'modifiers': [], 'key': 13}, {'modifiers': [0xA0], 'key': 65},
                        {'modifiers': [0x5B], 'key': 76}, {'modifiers': [0xA2], 'key': True},
                        {'modifiers': 'Ctrl', 'key': 65}):
            with self.subTest(binding=binding), self.assertRaises(ValueError):
                validate_binding(binding)

    def test_readable_label(self):
        self.assertEqual(binding_label({'modifiers': [0xA0, 0xA2], 'key': 84}), 'Left Ctrl + Left Shift + T')
