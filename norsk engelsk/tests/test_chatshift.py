import ctypes
import io
import json
import threading
import unittest
from contextlib import ExitStack
from unittest.mock import patch, Mock
import tkinter as tk
import translator
import windows_input as win
import direct_mode
from app import App


def response(text='Can you wait a moment?'):
    return {'status': 'completed', 'output': [{'type': 'message', 'content': [
        {'type': 'output_text', 'text': text}]}]}


class TranslationTests(unittest.TestCase):
    def test_request_and_response(self):
        with patch('urllib.request.urlopen', return_value=io.BytesIO(json.dumps(response()).encode())) as call:
            self.assertEqual(translator.translate('kan dere vente litt?', 'test-key'), 'Can you wait a moment?')
            body = json.loads(call.call_args.args[0].data)
            self.assertFalse(body['store'])
            self.assertEqual(body['input'], 'kan dere vente litt?')

    def test_incomplete_and_refusal_never_sent(self):
        for data in ({'status': 'incomplete', 'output': []}, {'status': 'completed', 'output': []}):
            with self.assertRaises(ValueError):
                translator.extract_translation(data)

    def test_commands_and_empty_input_rejected_without_network(self):
        with patch('urllib.request.urlopen') as network:
            for text in ('', '/quit', 'a' * 1001):
                with self.assertRaises(ValueError):
                    translator.translate(text, 'test-key')
            network.assert_not_called()

    def test_newlines_collapsed_and_commands_rejected(self):
        self.assertEqual(translator.extract_translation(response('Hello\nworld')), 'Hello world')
        with self.assertRaises(ValueError):
            translator.extract_translation(response('/quit'))

    def test_network_failure_is_readable(self):
        with patch('urllib.request.urlopen', side_effect=TimeoutError()):
            with self.assertRaisesRegex(ValueError, 'Sjekk nettet'):
                translator.translate('hei', 'test-key')


class InputTests(unittest.TestCase):
    def test_native_structure_size(self):
        self.assertEqual(ctypes.sizeof(win.INPUT), 40 if ctypes.sizeof(ctypes.c_void_p) == 8 else 28)

    def test_focus_change_blocks_enter(self):
        with patch.object(win, 'foreground', return_value=999), patch.object(win, 'emit') as emit:
            with self.assertRaises(ValueError):
                win.send_enter(123, 456)
            emit.assert_not_called()

    def test_hook_can_be_installed_and_removed(self):
        self.assertTrue(win.register())
        win.unregister()
        self.assertFalse(win._listener.is_alive())

    def test_right_alt_enter_triggers_once_and_swallows_release(self):
        state = win.HotkeyState()
        self.assertEqual(state.feed(0xA5, True), (False, False))
        self.assertEqual(state.feed(13, True), (True, True))
        self.assertEqual(state.feed(13, True), (True, False))
        state.feed(0xA5, False)
        self.assertEqual(state.feed(13, False), (True, False))
        self.assertEqual(state.feed(13, True), (False, False))

    def test_left_ctrl_and_plain_enter_pass_through(self):
        state = win.HotkeyState()
        self.assertEqual(state.feed(13, True), (False, False))
        state.feed(0xA2, True)
        self.assertEqual(state.feed(13, True), (False, False))

    def test_shift_and_windows_combinations_do_not_trigger(self):
        for extra in (0xA3, 0xA0, 0x5B):
            state = win.HotkeyState()
            state.feed(0xA5, True)
            state.feed(extra, True)
            self.assertEqual(state.feed(13, True), (False, False))

    def test_own_injected_enter_does_not_recurse(self):
        state = win.HotkeyState()
        state.feed(0xA5, True)
        self.assertEqual(state.feed(13, True, own=True), (False, False))

    def test_altgr_with_synthetic_left_ctrl_triggers(self):
        state = win.HotkeyState()
        state.feed(0xA2, True)
        state.feed(0xA5, True)
        self.assertEqual(state.feed(13, True), (True, True))

    def test_alt_reported_as_left_side_triggers(self):
        for modifiers in ({0xA4}, {0xA2, 0xA4}):
            state = win.HotkeyState()
            for modifier in modifiers:
                state.feed(modifier, True)
            self.assertEqual(state.feed(13, True), (True, True))
            self.assertEqual(state.feed(13, False), (True, False))

    def test_right_ctrl_triggers(self):
        for modifier in (0xA3,):
            state = win.HotkeyState()
            state.feed(modifier, True)
            self.assertEqual(state.feed(13, True), (True, True))

    def test_stale_clipboard_not_used_when_copy_is_unsupported(self):
        with ExitStack() as stack:
            for name in ('check_focus', 'clipboard_write', 'shortcut'):
                stack.enter_context(patch.object(win, name))
            stack.enter_context(patch.object(win.user32, 'GetClipboardSequenceNumber', return_value=10))
            stack.enter_context(patch.object(win.time, 'monotonic', side_effect=[0, 0, 2]))
            stack.enter_context(patch.object(win.time, 'sleep'))
            read = stack.enter_context(patch.object(win, 'clipboard_read', return_value='stale clipboard'))
            with self.assertRaisesRegex(ValueError, 'does not support copying'):
                win.capture((1, 2, 3), 4, threading.Event())
            read.assert_not_called()

    def test_single_instance_guard(self):
        first = win.acquire_instance()
        self.assertIsNotNone(first)
        try:
            self.assertIsNone(win.acquire_instance())
        finally:
            win.kernel32.CloseHandle(first)


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.calls = {}
        for name in ('wait_release', 'check_focus', 'capture', 'last_input',
                     'clipboard_write', 'shortcut', 'send_enter', 'emit'):
            self.calls[name] = self.stack.enter_context(patch.object(win, name))
        self.stack.enter_context(patch.object(direct_mode.time, 'sleep'))
        self.calls['capture'].side_effect = ['hei', 'hei', 'Hello']
        self.calls['last_input'].return_value = 100
        self.cancel = threading.Event()
        self.translate = Mock(return_value='Hello')

    def run_transaction(self, **kwargs):
        return direct_mode.run((1, 2, 3), 4, 'test-key', self.cancel,
                               translate_fn=self.translate, **kwargs)

    def test_verified_translation_sends_exactly_one_enter(self):
        result, _ = self.run_transaction()
        self.assertEqual(result, 'Hello')
        self.translate.assert_called_once_with('hei', 'test-key')
        self.calls['send_enter'].assert_called_once_with(1, 2)
        self.calls['clipboard_write'].assert_called_once_with('Hello', 4)

    def test_api_error_does_not_replace_or_send(self):
        self.translate.side_effect = ValueError('Nettverksfeil')
        with self.assertRaises(ValueError):
            self.run_transaction()
        self.calls['clipboard_write'].assert_not_called()
        self.calls['send_enter'].assert_not_called()

    def test_changed_draft_is_not_overwritten(self):
        self.calls['capture'].side_effect = ['hei', 'ny melding']
        with self.assertRaisesRegex(ValueError, 'The text changed'):
            self.run_transaction()
        self.calls['clipboard_write'].assert_not_called()
        self.calls['send_enter'].assert_not_called()

    def test_activity_without_a_changed_draft_can_still_send(self):
        self.calls['last_input'].side_effect = [100, 101]
        self.run_transaction()
        self.calls['send_enter'].assert_called_once_with(1, 2)

    def test_rejected_paste_never_sends_original(self):
        self.calls['capture'].side_effect = ['hei', 'hei', 'hei']
        with self.assertRaisesRegex(ValueError, 'Enter was not sent'):
            self.run_transaction()
        self.calls['send_enter'].assert_not_called()

    def test_pause_during_api_cancels_delivery(self):
        def translate_and_cancel(*args):
            self.cancel.set()
            return 'Hello'
        self.translate.side_effect = translate_and_cancel
        with self.assertRaisesRegex(ValueError, 'Cancelled'):
            self.run_transaction()
        self.calls['clipboard_write'].assert_not_called()

    def test_focus_change_during_translation_blocks_replacement(self):
        self.calls['check_focus'].side_effect = [None, ValueError('Fokus endret')]
        with self.assertRaisesRegex(ValueError, 'Fokus endret'):
            self.run_transaction()
        self.calls['clipboard_write'].assert_not_called()
        self.calls['send_enter'].assert_not_called()

    def test_preview_only_never_sends_enter(self):
        self.run_transaction(send=False)
        self.calls['send_enter'].assert_not_called()


class AppTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = App(self.root, prepare=False)

    def tearDown(self):
        self.app.close()
        win.set_binding(None)

    def test_shortcut_dialog_records_keys(self):
        self.root.deiconify()
        self.root.update()
        self.app.change_shortcut()
        self.root.update()
        dialog = next(child for child in self.root.winfo_children() if isinstance(child, tk.Toplevel))
        dialog.focus_force()
        self.root.update()
        dialog.event_generate('<KeyPress>', keysym='Control_L', keycode=0xA2)
        dialog.event_generate('<KeyPress>', keysym='Shift_L', keycode=0xA0)
        dialog.event_generate('<KeyPress>', keysym='T', keycode=84)
        self.root.update()
        self.assertEqual(self.app.binding, {'modifiers': [0xA0, 0xA2], 'key': 84})

    def test_model_must_be_ready_before_enabling_hook(self):
        with patch.object(win, 'register') as register:
            self.app.start()
            register.assert_not_called()
        self.assertIn('not ready', self.app.status.get())

    def test_local_mode_starts_without_api_key(self):
        self.app.local = Mock()
        with patch.object(win, 'register', return_value=True):
            self.app.start()
        self.assertTrue(self.app.registered)
        self.app.registered = False

    def test_ready_model_automatically_activates(self):
        self.app.preparation.put((Mock(), None))
        with patch.object(win, 'register', return_value=True), patch.object(win, 'poll_hotkey', return_value=None):
            self.app.poll()
        self.assertTrue(self.app.registered)
        self.assertIn('Active:', self.app.status.get())
        self.app.registered = False

    def test_repeated_trigger_ignored_while_busy(self):
        self.app.registered = True
        self.app.busy = True
        with patch.object(direct_mode, 'run') as run:
            self.app.trigger((1, 2, 3))
            run.assert_not_called()
        self.app.registered = False


if __name__ == '__main__':
    unittest.main()
