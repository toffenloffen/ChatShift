import threading
import unittest
from contextlib import ExitStack
from unittest.mock import patch, Mock
import among_us_mode as game


class GameTransactionTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(game.win, 'wait_release'))
        self.stack.enter_context(patch.object(game.win, 'check_focus'))
        self.read = self.stack.enter_context(patch.object(game, 'read_field', side_effect=['hei', 'hei', '', 'Hi']))
        self.encode = self.stack.enter_context(patch.object(game, 'encode_keys', return_value=[(72, ()), (73, ())]))
        self.press = self.stack.enter_context(patch.object(game, 'press'))
        self.translate = Mock(return_value='Hi')
        self.cancel = threading.Event()

    def run_game(self, **kwargs):
        return game.run((1, 2, 3), 4, '', self.cancel, translate_fn=self.translate, **kwargs)

    def test_verified_draft_sends_only_after_readback(self):
        result, _ = self.run_game()
        self.assertEqual(result, 'Hi')
        self.assertEqual(self.press.call_args.args[1], 13)
        self.assertEqual(sum(c.args[1] == 13 for c in self.press.call_args_list), 1)

    def test_changed_original_is_not_deleted(self):
        self.read.side_effect = ['hei', 'endret']
        with self.assertRaises(ValueError): self.run_game()
        self.press.assert_not_called()

    def test_long_or_unsupported_translation_preserves_original(self):
        self.translate.return_value = 'x' * 101
        with self.assertRaises(ValueError): self.run_game()
        self.press.assert_not_called()

    def test_failed_clear_never_types_translation_or_sends(self):
        self.read.side_effect = ['hei', 'hei', 'h']
        with self.assertRaises(ValueError): self.run_game()
        self.assertTrue(all(c.args[1] in (35, 8) for c in self.press.call_args_list))

    def test_incomplete_paste_does_not_send(self):
        self.read.side_effect = ['hei', 'hei', '', 'H']
        with self.assertRaises(ValueError): self.run_game()
        self.assertFalse(any(c.args[1] == 13 for c in self.press.call_args_list))

    def test_review_mode_does_not_send(self):
        self.run_game(send=False)
        self.assertFalse(any(c.args[1] == 13 for c in self.press.call_args_list))


class GameOcrTests(unittest.TestCase):
    def test_counter_mismatch_rejects_incomplete_or_caret_text(self):
        try:
            from among_us_ocr import validate_read
        except ImportError:
            self.skipTest('Optional Pillow dependency not installed')
        self.assertEqual(validate_read('hei', '3/100'), 'hei')
        self.assertEqual(validate_read('', '0/100'), '')
        for text, counter in [('hei]', '3/100'), ('hei', '4/100'), ('hei', '3/120'), ('hei', 'unknown')]:
            with self.assertRaises(ValueError): validate_read(text, counter)
