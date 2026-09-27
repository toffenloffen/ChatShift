import queue
import threading
import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
import numpy as np
from voice_trial import VoiceTrial
from realtime_adapter import LiveRecorder, RealtimeTranscriber


class TrialLiveTests(unittest.TestCase):
    def trial(self):
        trial=VoiceTrial.__new__(VoiceTrial)
        trial.cancel=threading.Event()
        trial.events=queue.Queue()
        trial.stopped_at=time.perf_counter()
        trial.source='Norwegian';trial.target='English'
        trial.model=RealtimeTranscriber()
        trial.app=SimpleNamespace(local=Mock())
        trial.app.local.translate.return_value='Can I join your group?'
        return trial

    def test_existing_stream_transcript_goes_to_luna_once(self):
        trial=self.trial()
        record=LiveRecorder('Norwegian',{},trial.cancel)
        record.text='Kan jeg bli med i gruppa deres?'
        record.raw_chunks=[np.ones(512)];record.filtered_chunks=[np.ones(512)*.5]
        record.done.set()
        trial.process(record)
        trial.app.local.translate.assert_called_once_with(record.text,target_language='English',source_language='Norwegian')
        events=list(trial.events.queue)
        self.assertEqual([v for k,v in events if k=='original'],[record.text])
        self.assertEqual([v for k,v in events if k=='output'],['Can I join your group?'])
        self.assertLess([k for k,v in events].index('timing'),[k for k,v in events].index('output'))
        self.assertEqual(record.raw_chunks,[])

    def test_cancelled_recording_never_displays_or_translates(self):
        trial=self.trial();trial.cancel.set()
        trial.process(Mock())
        trial.app.local.translate.assert_not_called()
        self.assertEqual(list(trial.events.queue),[('released',None)])

    def test_same_voice_languages_bypass_luna(self):
        trial=self.trial();trial.source=trial.target='English'
        record=LiveRecorder('English',{},trial.cancel)
        record.text='Can I join your group?';record.done.set()
        trial.process(record)
        trial.app.local.translate.assert_not_called()
        self.assertEqual([v for k,v in trial.events.queue if k=='output'],[record.text])

    def test_network_error_releases_window_without_translation(self):
        trial=self.trial()
        record=LiveRecorder('Norwegian',{},trial.cancel)
        record.error='Connection lost';record.done.set()
        trial.process(record)
        trial.app.local.translate.assert_not_called()
        self.assertEqual(list(trial.events.queue),[('error','Connection lost'),('released',None)])

if __name__=='__main__':unittest.main()
