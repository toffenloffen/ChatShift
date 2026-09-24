import threading
import unittest
from unittest.mock import patch
from contextlib import ExitStack
from voice_input import insert_draft
import windows_input as win


class VoiceDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.calls = {name: self.stack.enter_context(patch.object(win, name)) for name in
                      ('wait_release', 'last_input', 'check_focus', 'clipboard_write', 'shortcut', 'capture', 'send_enter')}
        self.stack.enter_context(patch('among_us_mode.is_among_us', return_value=False))
        self.calls['last_input'].return_value = 5
        self.calls['capture'].return_value = 'Hello'
        self.cancel = threading.Event()

    def run_delivery(self, send=False):
        insert_draft((1,2,3), 5, 'Hello', 4, self.cancel, {'modifiers': [], 'key': 120}, send)

    def test_default_is_unsent_and_does_not_select_existing_text(self):
        self.run_delivery()
        self.calls['shortcut'].assert_called_once_with((1,2,3), ord('V'))
        self.calls['capture'].assert_not_called()
        self.calls['send_enter'].assert_not_called()

    def test_changed_input_blocks_insertion(self):
        self.calls['last_input'].return_value = 6
        with self.assertRaises(ValueError):
            self.run_delivery()
        self.calls['clipboard_write'].assert_not_called()
        self.calls['send_enter'].assert_not_called()

    def test_focus_change_blocks_insertion(self):
        self.calls['check_focus'].side_effect = ValueError('focus changed')
        with self.assertRaises(ValueError):
            self.run_delivery()
        self.calls['clipboard_write'].assert_not_called()

    def test_cancel_blocks_insertion(self):
        self.cancel.set()
        with self.assertRaises(ValueError):
            self.run_delivery(True)
        self.calls['send_enter'].assert_not_called()

    def test_auto_send_requires_matching_readback(self):
        self.calls['capture'].return_value = 'old text'
        with self.assertRaises(ValueError):
            self.run_delivery(True)
        self.calls['send_enter'].assert_not_called()

    def test_explicit_auto_send_sends_one_enter_after_verification(self):
        self.run_delivery(True)
        self.calls['send_enter'].assert_called_once_with(1, 2)
