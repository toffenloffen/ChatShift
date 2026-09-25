import queue
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
import numpy as np
from voice_trial import VoiceTrial


class VoiceTrialTests(unittest.TestCase):
    def trial(self, with_text=False):
        trial = VoiceTrial.__new__(VoiceTrial)
        trial.events = queue.Queue()
        trial.cancel = threading.Event()
        trial.session_noise = dict(enabled=False)
        trial.session_text = with_text
        trial.source, trial.target = 'Norwegian', 'English'
        trial.app = SimpleNamespace(local=None, speech_model=Mock())
        return trial

    def test_audio_test_works_without_model_or_translation(self):
        trial = self.trial()
        audio = np.zeros(16000, dtype='float32')
        with patch('voice_trial.LocalTranscriber', side_effect=AssertionError('must not load')):
            trial.process(audio)
        events = list(trial.events.queue)
        self.assertEqual([kind for kind, _ in events], ['audio', 'done', 'released'])
        self.assertIs(events[0][1][0], audio)
        self.assertIs(events[0][1][1], audio)
        trial.app.speech_model.transcribe.assert_not_called()

    def test_disconnected_luna_keeps_audio_and_transcript(self):
        trial = self.trial(True)
        trial.app.speech_model.transcribe.return_value = 'Ikke angrip.'
        trial.process(np.zeros(16000, dtype='float32'))
        events = list(trial.events.queue)
        self.assertEqual([kind for kind, _ in events], ['audio', 'original', 'done', 'released'])
        self.assertEqual(events[1][1], 'Ikke angrip.')

    def test_speech_failure_still_preserves_playback(self):
        trial = self.trial(True)
        trial.app.speech_model.transcribe.side_effect = ValueError('No speech detected.')
        trial.process(np.zeros(16000, dtype='float32'))
        self.assertEqual([kind for kind, _ in trial.events.queue], ['audio', 'error', 'released'])

    def test_processed_recording_produces_transcript_then_translation(self):
        trial = self.trial(True)
        trial.app.local = Mock()
        trial.app.local.translate.return_value = "Do not attack yet."
        trial.app.speech_model.transcribe.return_value = 'Ikke angrip ennå.'
        raw = np.zeros(16000, dtype='float32')
        filtered = np.ones(16000, dtype='float32') * .01
        with patch('audio_cleanup.clean_audio', side_effect=AssertionError('must not filter twice')):
            trial.process(raw, filtered)
        trial.app.speech_model.transcribe.assert_called_once_with(filtered, 'Norwegian')
        trial.app.local.translate.assert_called_once_with('Ikke angrip ennå.', target_language='English', source_language='Norwegian')
        events = list(trial.events.queue)
        self.assertEqual([k for k, _ in events], ['audio', 'original', 'output', 'done', 'released'])

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
