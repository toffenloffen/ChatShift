"""Experimental live speech adapter for the isolated ChatShift test build."""
import asyncio
import queue
import sys
import threading
import time
from pathlib import Path
import numpy as np

from realtime_engine import VoiceSession
from audio_cleanup import SpeechFilter, audio_level


class FrameFeeder:
    def __init__(self, track):
        self.track=track
        self.pending=np.empty(0,dtype=np.int16)

    def feed(self, samples):
        self.pending=np.concatenate((self.pending,(np.clip(samples,-1,1)*32767).astype(np.int16)))
        length=len(self.pending)//960*960
        if length:
            self.track.feed(self.pending[:length],48000)
            self.pending=self.pending[length:]

    def finish(self):
        if self.pending.size:
            self.track.feed(self.pending,48000)
            self.pending=np.empty(0,dtype=np.int16)


class LiveRecorder:
    RATE=48000
    MAX_SECONDS=30

    def __init__(self,language,noise,cancel):
        self.language=language;self.noise=noise;self.cancel=cancel
        self.full=threading.Event();self.stop_event=threading.Event();self.done=threading.Event()
        self.incoming=queue.SimpleQueue();self.levels=queue.SimpleQueue()
        self.chunks=[];self.samples=0;self.overflow=False
        self.stream=None;self.lock=threading.Lock();self.error=None;self.text=''
        self.timings={};self.started_at=time.perf_counter();self.stopped_at=None
        self.armed=threading.Event();self.connected=threading.Event();self.worker=None
        self.idle_deadline=None
        self.keep_audio=False;self.raw_chunks=[];self.filtered_chunks=[]

    def playback(self):
        raw,filtered=self.raw_chunks,self.filtered_chunks
        self.raw_chunks=[];self.filtered_chunks=[]
        return (np.concatenate(raw) if raw else np.empty(0,dtype=np.float32),
                np.concatenate(filtered) if filtered else np.empty(0,dtype=np.float32))

    def warm(self):
        self.idle_deadline=time.perf_counter()+60
        self.worker=threading.Thread(target=self._work,daemon=True)
        self.worker.start()

    def claim(self,cancel):
        with self.lock:
            if self.done.is_set() or self.cancel.is_set() or self.error:return False
            self.cancel=cancel
            self.armed.set()
            self.timings['connection_ready_at_press']=self.connected.is_set()
            return True

    def start(self,device=None):
        self.armed.set()
        import sounddevice as sd
        def capture(data,frames,timestamp,status):
            if self.stop_event.is_set() or self.cancel.is_set():return
            self.overflow |= bool(status)
            remaining=self.RATE*self.MAX_SECONDS-self.samples
            if remaining>0:
                audio=data[:remaining,0].copy();self.incoming.put(audio);self.samples+=len(audio)
            if self.samples>=self.RATE*self.MAX_SECONDS:
                self.full.set();self.stop_event.set()
        try:
            self.stream=sd.InputStream(device=device,samplerate=self.RATE,blocksize=512,
                channels=1,dtype='float32',callback=capture)
            self.stream.start()  # Never wait for network before opening microphone.
        except Exception:
            self.cancel.set()
            self._close_mic()
            raise ValueError('Could not open this microphone. Choose another input.') from None
        if self.worker is None:
            self.worker=threading.Thread(target=self._work,daemon=True)
            self.worker.start()

    def _close_mic(self):
        with self.lock:
            stream,self.stream=self.stream,None
            if stream:
                try:stream.stop()
                finally:stream.close()

    def stop(self):
        self.stopped_at=time.perf_counter()
        self.stop_event.set();self._close_mic()
        if self.overflow or self.samples<self.RATE//3:
            self.cancel.set()
            raise ValueError('Recording interrupted or too short. Try again.')
        return self

    def close(self):
        self.cancel.set();self.stop_event.set();self._close_mic()

    def result(self):
        while not self.done.wait(.05):
            if self.cancel.is_set():raise ValueError('Voice cancelled.')
        if self.error:raise ValueError(self.error)
        if self.cancel.is_set():raise ValueError('Voice cancelled.')
        return self.text

    def _work(self):
        async def run():
            finals={}
            def event(kind,data):
                if kind=='remote' and data.get('type')=='turn.done':
                    turn=data.get('turn',{})
                    if turn.get('role')=='user':finals[turn['id']]=turn.get('transcript','')
            session=VoiceSession(event,self.language,'listen')
            processor=SpeechFilter();feeder=FrameFeeder(session.track)
            enabled=bool(self.noise.get('enabled',False))
            def process(audio):
                if len(audio)<512:audio=np.pad(audio,(0,512-len(audio)))
                out,level,_=processor.process(audio,enabled)
                if self.keep_audio and not self.cancel.is_set():
                    self.raw_chunks.append(audio.copy());self.filtered_chunks.append(out.copy())
                self.levels.put((audio_level(audio),level));feeder.feed(out)
            try:
                startup=asyncio.create_task(session.start())
                while not startup.done():
                    if self.cancel.is_set():
                        startup.cancel();await asyncio.gather(startup,return_exceptions=True);return
                    await asyncio.sleep(.01)
                await startup
                self.timings['connection_ms']=round((time.perf_counter()-self.started_at)*1000,1)
                # Warm only the network and filter; microphone stays closed.
                if enabled:
                    processor.process(np.zeros(512,dtype=np.float32),True)
                self.connected.set()
                while self.idle_deadline is not None and not self.armed.is_set():
                    with self.lock:
                        if time.perf_counter()>=self.idle_deadline and not self.armed.is_set():
                            self.cancel.set()
                    if self.cancel.is_set():return
                    if session.failure:raise ValueError(session.failure)
                    await asyncio.sleep(.01)
                while not self.cancel.is_set():
                    if self.overflow:raise ValueError('Microphone lost audio. Try another input.')
                    if session.failure:raise ValueError(session.failure)
                    while not self.incoming.empty():process(self.incoming.get_nowait())
                    if self.stop_event.is_set():break
                    await asyncio.sleep(.01)
                self._close_mic()
                while not self.incoming.empty():process(self.incoming.get_nowait())
                if self.cancel.is_set():return
                if enabled:
                    for _ in range(processor.TAIL//processor.FRAME):process(np.zeros(512,dtype=np.float32))
                feeder.finish()
                self.timings['queued_audio_ms']=session.track.frames.qsize()*20
                finalize_started=time.perf_counter()
                finalizing=asyncio.create_task(session.finalize())
                while not finalizing.done():
                    if self.cancel.is_set():
                        finalizing.cancel();await asyncio.gather(finalizing,return_exceptions=True);return
                    await asyncio.sleep(.01)
                await finalizing
                self.timings['finalize_ms']=round((time.perf_counter()-finalize_started)*1000,1)
                self.text=' '.join(finals.values()).strip()
                if not self.text:raise ValueError('No speech was recognized. Try again.')
                if self.stopped_at is not None:
                    self.timings['stop_to_transcript_ms']=round((time.perf_counter()-self.stopped_at)*1000,1)
                # Translation can start as soon as the final transcript exists.
                # Network shutdown must never hold the user's text back.
                self.done.set()
            finally:
                self._close_mic();processor.close();await session.close()
                while not self.incoming.empty():self.incoming.get_nowait()
                if self.cancel.is_set():
                    self.raw_chunks.clear();self.filtered_chunks.clear()
        try:asyncio.run(run())
        except Exception as exc:
            if not self.done.is_set():self.error=str(exc)
        finally:self.done.set()


class RealtimeTranscriber:
    def __init__(self):
        self.pending=None

    def warm(self,language,noise):
        self.close()
        self.pending=LiveRecorder(language,dict(noise),threading.Event())
        self.pending.warm()

    def close(self):
        if self.pending:
            self.pending.close();self.pending=None

    def recorder(self,language,noise,cancel):
        record,self.pending=self.pending,None
        if record:
            if record.language==language and record.noise==noise and record.claim(cancel):return record
            record.close()
        return LiveRecorder(language,noise,cancel)

    def transcribe(self,audio,language,cancel=None):
        if isinstance(audio,LiveRecorder):return audio.result()
        # Existing Voice Test sends a complete, already-filtered 16 kHz recording.
        import soxr
        record=LiveRecorder(language,{'enabled':False},cancel or threading.Event())
        up=soxr.resample(np.asarray(audio,dtype=np.float32),16000,48000)
        for start in range(0,len(up),512):record.incoming.put(up[start:start+512])
        record.samples=len(up);record.stop_event.set()
        record._work()
        return record.result()
