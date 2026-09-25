import unittest
import threading
import queue
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
from audio_cleanup import SpeechFilter, clean_audio, audio_level
from mic_monitor import MicMonitor

class MonitorTests(unittest.TestCase):
    def test_bypass_is_exact_even_with_old_gate_settings(self):
        audio = np.full(16000, .001, np.float32)
        self.assertIs(clean_audio(audio, enabled=False, threshold=-20, apply_gate=True), audio)

    def test_meter_uses_processed_samples_and_listening_is_opt_in(self):
        for listen in (False, True):
            monitor=MicMonitor.__new__(MicMonitor)
            monitor.stop_event=threading.Event(); monitor.options=(False,listen)
            monitor.levels=queue.SimpleQueue(); monitor.error=None
            writes=[]; closed=[]
            class Input:
                def __init__(self,**kw): pass
                def __enter__(self): return self
                def __exit__(self,*args): closed.append('input')
                def read(self,n):
                    monitor.stop()
                    return np.full((n,1),.1,np.float32),False
            class Output(Input):
                def write(self,a): writes.append(a)
                def __exit__(self,*args): closed.append('output')
            with patch.dict('sys.modules',sounddevice=SimpleNamespace(InputStream=Input,OutputStream=Output)):
                monitor.run(None)
            self.assertIsNone(monitor.error)
            self.assertEqual(len(writes),int(listen))
            incoming,outgoing=monitor.levels.get_nowait()
            self.assertAlmostEqual(incoming,-20,places=4)
            self.assertAlmostEqual(outgoing,incoming,places=4)
            self.assertIn('input',closed)
            if listen: self.assertEqual(writes[0].dtype,np.float32)

    def test_processed_level_is_output_rms_not_input_level(self):
        with patch('audio_cleanup.get_model') as model:
            model.return_value.new_stream.return_value.process_frame.return_value=np.full(512,.001,np.float32)
            f=SpeechFilter(); out,level,_=f.process(np.full(512,.5,np.float32))
            self.assertAlmostEqual(level,audio_level(out))
            self.assertAlmostEqual(level,-60,places=3)

    def test_shared_filter_batch_matches_stream_with_tail(self):
        import soxr
        source=np.random.default_rng(6).normal(0,.02,16000).astype(np.float32)
        up=soxr.resample(source,16000,48000).astype(np.float32)
        frames=np.pad(up,(0,(-len(up)%512)+SpeechFilter.TAIL)).reshape(-1,512)
        processor=SpeechFilter()
        expected=soxr.resample(np.concatenate([processor.process(f)[0] for f in frames]),48000,16000)
        actual=clean_audio(source,True)
        np.testing.assert_allclose(actual,expected,atol=1e-6)

if __name__=='__main__': unittest.main()
