import unittest
from controller_input import ChordEdges, validate_chord, Gamepad, State
import ctypes
from unittest.mock import Mock, patch
import tkinter as tk
from controller_ui import ControllerInput


class ControllerTests(unittest.TestCase):
    def test_held_at_connection_does_not_trigger(self):
        edge = ChordEdges()
        self.assertIsNone(edge.update({'X'}, ['X']))
        self.assertIsNone(edge.update(set(), ['X']))
        self.assertEqual(edge.update({'X'}, ['X']), 'down')
        self.assertIsNone(edge.update({'X'}, ['X']))
        self.assertEqual(edge.update(set(), ['X']), 'up')

    def test_disconnect_cancels_and_requires_neutral(self):
        edge = ChordEdges()
        edge.update(set(), ['LB', 'X'])
        self.assertEqual(edge.update({'LB', 'X'}, ['LB', 'X']), 'down')
        self.assertEqual(edge.update(None, ['LB', 'X']), 'cancel')
        self.assertIsNone(edge.update({'LB', 'X'}, ['LB', 'X']))

    def test_partial_chord_and_extra_button(self):
        edge = ChordEdges()
        edge.update(set(), ['LB', 'X'])
        self.assertIsNone(edge.update({'LB'}, ['LB', 'X']))
        self.assertEqual(edge.update({'LB', 'X'}, ['LB', 'X']), 'down')
        self.assertEqual(edge.update({'LB', 'X', 'Y'}, ['LB', 'X']), 'cancel')
        self.assertIsNone(edge.update({'LB', 'X'}, ['LB', 'X']))
        edge.update(set(), ['LB', 'X'])
        self.assertEqual(edge.update({'LB', 'X'}, ['LB', 'X']), 'down')
        self.assertEqual(edge.update({'LB'}, ['LB', 'X']), 'up')

    def test_disabled_and_validation(self):
        edge = ChordEdges()
        edge.update(set(), [])
        self.assertIsNone(edge.update({'X'}, []))
        for bad in (None, ['paddle'], ['A', 'B', 'X', 'Y'], 'X'):
            with self.assertRaises(ValueError):
                validate_chord(bad)
        self.assertEqual(validate_chord(['X', 'LB']), ['LB', 'X'])

    def test_xinput_layout(self):
        self.assertEqual(ctypes.sizeof(Gamepad), 12)
        self.assertEqual(ctypes.sizeof(State), 16)


class ControllerDispatchTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = Mock(registered=True, closing=False, busy=False)
        self.app.voice.recording = False
        self.app.voice.processing = False
        self.controller = ControllerInput(self.app, persist=False)
        self.controller.enabled.set(True)
        self.controller.bindings = {'Text': ['LB', 'X'], 'Voice': ['RB']}
        self.reader = self.controller.reader = Mock()
        self.target = patch('controller_ui.win.focus_snapshot', return_value=(123, 456)).start()
        patch('controller_ui.win.external', return_value=True).start()
        patch('controller_ui.win.last_input', return_value=7).start()
        self.step(set())

    def tearDown(self):
        patch.stopall()
        self.root.destroy()

    def step(self, pressed):
        self.reader.read.return_value = pressed
        self.controller.poll()

    def test_text_runs_once_on_release(self):
        self.step({'LB'})
        self.step({'LB', 'X'})
        self.step({'LB', 'X'})
        self.app.trigger.assert_not_called()
        self.step(set())
        self.step(set())
        self.app.trigger.assert_called_once_with((123, 456), controller=True)

    def test_focus_change_blocks_text(self):
        self.step({'LB', 'X'})
        self.target.return_value = (999, 456)
        self.step(set())
        self.app.trigger.assert_not_called()

    def test_paused_or_disconnected_never_translates(self):
        self.step({'LB', 'X'})
        self.step(None)
        self.step(set())
        self.app.trigger.assert_not_called()
        self.app.registered = False
        self.step({'LB', 'X'})
        self.step(set())
        self.app.trigger.assert_not_called()

    def test_voice_disconnect_aborts_without_finish(self):
        def start(*args):
            self.app.voice.recording = True
        self.app.voice.hotkey.side_effect = start
        self.step({'RB'})
        self.step(None)
        self.app.voice.hotkey.assert_called_once_with('down', (123, 456), 7)
        self.app.voice.abort.assert_called()

    def test_gamepad_cannot_stop_keyboard_recording(self):
        self.app.busy = True
        self.app.voice.recording = True
        self.step({'RB'})
        self.step(set())
        self.app.voice.hotkey.assert_not_called()

    def test_visual_selection_saves_and_clear_removes(self):
        frame = tk.Frame(self.root)
        self.controller.build(frame)
        self.controller.clear_binding()
        self.controller.pick_button('LB')
        self.controller.pick_button('X')
        self.assertEqual(self.controller.bindings['Text'], ['LB', 'X'])
        self.assertEqual(self.controller.preview.selection, {'LB', 'X'})
        self.controller.choose_mode('Voice')
        self.assertEqual(self.controller.preview.selection, {'RB'})
        self.controller.clear_binding()
        self.assertEqual(self.controller.bindings['Voice'], [])
        buttons = self.controller.preview.buttons
        front = {name for name in buttons if not name.startswith('Rear ')}
        self.assertEqual(front, set(__import__('controller_input').BUTTONS))
        rear = {name for name in buttons if name.startswith('Rear ')}
        self.assertEqual(len(rear), 4)
        with patch.object(self.controller, 'show_paddle_setup') as setup:
            self.controller.pick_button('Rear R5 (right hand, lower)')
            setup.assert_called_once()
        self.assertEqual(self.controller.bindings['Voice'], [])
