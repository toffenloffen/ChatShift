import unittest
from unittest.mock import patch
try:
    import numpy as np
    import sounddevice as sd
except ImportError:
    np = sd = None
from local_voice import Recorder, LANGUAGE_CODES
from settings import LANGUAGES


@unittest.skipIf(sd is None, 'Optional voice dependencies are not installed')
class RecorderTests(unittest.TestCase):
    def test_all_ui_languages_have_speech_codes(self):
        self.assertEqual(set(LANGUAGES), set(LANGUAGE_CODES))

    def test_open_failure_closes_device(self):
        with patch('sounddevice.InputStream') as stream:
            stream.return_value.start.side_effect = RuntimeError('device failed')
            recorder = Recorder()
            with self.assertRaises(ValueError):
                recorder.start()
            stream.return_value.close.assert_called_once()
            self.assertIsNone(recorder.stream)

    def test_recording_is_bounded_and_stop_releases_device(self):
        with patch('sounddevice.InputStream') as stream:
            recorder = Recorder()
            recorder.MAX_SECONDS = 1
            recorder.start()
            callback = stream.call_args.kwargs['callback']
            callback(np.zeros((12000, 1), dtype=np.float32), 12000, None, False)
            with self.assertRaises(sd.CallbackStop):
                callback(np.ones((12000, 1), dtype=np.float32), 12000, None, False)
            self.assertTrue(recorder.full.is_set())
            self.assertEqual(len(recorder.stop()), 16000)
            self.assertEqual(recorder.chunks, [])
            stream.return_value.close.assert_called_once()

    def test_overflow_is_not_silently_transcribed(self):
        with patch('sounddevice.InputStream') as stream:
            recorder = Recorder()
            recorder.start()
            stream.call_args.kwargs['callback'](np.ones((10000, 1)), 10000, None, True)
            with self.assertRaises(ValueError):
                recorder.stop()
            self.assertEqual(recorder.chunks, [])
