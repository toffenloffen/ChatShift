import queue
import threading
import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from voice_trial import VoiceTrial

class VoiceTrialTests(unittest.TestCase):
    def trial(self):
        trial = VoiceTrial.__new__(VoiceTrial)
        trial.events = queue.Queue()
        trial.cancel = threading.Event()
        trial.stopped_at = time.perf_counter()
        trial.source, trial.target = 'Norwegian', 'English'
        trial.model = Mock()
        trial.model.transcribe.return_value = 'Ikke angrip.'
        trial.app = SimpleNamespace(local=None)
        return trial

    def test_disconnected_luna_keeps_transcript_and_playback(self):
        trial = self.trial()
        recording = Mock(timings={})
        trial.process(recording)
        self.assertEqual([k for k,v in trial.events.queue], ['original','audio','done','released'])
        recording.playback.assert_called_once()

    def test_failed_recognition_reports_error_without_translation(self):
        trial = self.trial()
        trial.model.transcribe.side_effect = ValueError('No speech detected.')
        trial.app.local = Mock()
        trial.process(Mock())
        self.assertEqual([k for k,v in trial.events.queue], ['error','released'])
        trial.app.local.translate.assert_not_called()

    def test_start_requests_monitor_stop_before_opening_another_microphone(self):
        trial = VoiceTrial.__new__(VoiceTrial)
        trial.recording = False
        trial.app = SimpleNamespace(voice=SimpleNamespace(monitor=Mock(thread=object())), busy=True)
        trial.button = Mock(); trial.status = Mock(); trial.window = Mock()
        trial.recorder = Mock()
        trial.toggle()
        trial.app.voice.monitor.stop.assert_called_once()
        trial.recorder.start.assert_not_called()
        trial.window.after.assert_called_once()
