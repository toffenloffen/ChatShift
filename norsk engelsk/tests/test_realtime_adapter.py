import unittest,threading
from unittest.mock import Mock,patch
import asyncio
import numpy as np
from realtime_adapter import FrameFeeder,LiveRecorder,RealtimeTranscriber
class AdapterTests(unittest.TestCase):
 def test_warm_connection_reused_with_current_cancel(self):
  model=RealtimeTranscriber();r=LiveRecorder('Norwegian',{},threading.Event());model.pending=r
  cancel=threading.Event()
  self.assertIs(model.recorder('Norwegian',{},cancel),r)
  self.assertIs(r.cancel,cancel);self.assertTrue(r.armed.is_set());self.assertIsNone(model.pending)
 def test_wrong_language_or_expired_connection_is_not_reused(self):
  for expired in (False,True):
   model=RealtimeTranscriber();r=LiveRecorder('Norwegian',{},threading.Event());model.pending=r
   if expired:r.cancel.set()
   chosen=model.recorder('Norwegian' if expired else 'French',{},threading.Event())
   self.assertIsNot(chosen,r);self.assertTrue(r.cancel.is_set())
 def test_warming_does_not_open_microphone(self):
  with patch('realtime_adapter.threading.Thread') as worker:
   r=LiveRecorder('Norwegian',{},threading.Event());r.warm()
   self.assertIsNone(r.stream);self.assertFalse(r.armed.is_set());worker.return_value.start.assert_called_once()
 def test_final_transcript_does_not_wait_for_network_cleanup(self):
  cleanup_started=threading.Event();cleanup_release=threading.Event()
  class Session:
   def __init__(self,event,*args):
    self.event=event;self.failure=None;self.track=Mock()
    self.track.frames.qsize.return_value=0
   async def start(self):pass
   async def finalize(self):
    self.event('remote',{'type':'turn.done','turn':{'role':'user','id':'1','transcript':'Hele setningen'}})
   async def close(self):
    cleanup_started.set()
    await asyncio.to_thread(cleanup_release.wait,3)
    raise RuntimeError('cleanup failure must not invalidate delivered text')
  r=LiveRecorder('Norwegian',{},threading.Event());r.stop_event.set()
  with patch('realtime_adapter.VoiceSession',Session):
   worker=threading.Thread(target=r._work);worker.start()
   try:
    self.assertTrue(cleanup_started.wait(2))
    self.assertTrue(r.done.is_set())
    self.assertEqual(r.result(),'Hele setningen')
   finally:cleanup_release.set();worker.join(4)
  self.assertIsNone(r.error)
 def test_filter_blocks_do_not_add_padding_between_frames(self):
  track=Mock();f=FrameFeeder(track)
  for _ in range(15):f.feed(np.full(512,.25,dtype=np.float32))
  f.finish()
  sent=np.concatenate([call.args[0] for call in track.feed.call_args_list])
  self.assertEqual(len(sent),7680)
  self.assertTrue(np.all(sent==8191))
 def test_partial_final_frame_is_preserved(self):
  track=Mock();f=FrameFeeder(track);f.feed(np.ones(512,dtype=np.float32));f.finish()
  self.assertEqual(len(track.feed.call_args.args[0]),512)
 def test_cancel_never_returns_text(self):
  cancel=threading.Event();r=LiveRecorder('Norwegian',{},cancel)
  r.text='must not insert';r.done.set();cancel.set()
  with self.assertRaises(ValueError):r.result()
 def test_completed_recorder_is_used_without_second_transcription(self):
  r=LiveRecorder('Norwegian',{},threading.Event());r.text='Hei';r.done.set()
  self.assertEqual(RealtimeTranscriber().transcribe(r,'Norwegian'),'Hei')
 def test_failure_surfaces(self):
  r=LiveRecorder('Norwegian',{},threading.Event());r.error='network failed';r.done.set()
  with self.assertRaisesRegex(ValueError,'network failed'):r.result()
if __name__=='__main__':unittest.main()
