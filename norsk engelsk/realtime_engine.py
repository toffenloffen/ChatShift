"""WebRTC voice via the installed Codex app-server's managed ChatGPT login."""
import asyncio
from fractions import Fraction
import io
import json
import queue
import time
import wave
import numpy as np
from av import AudioFrame
from aiortc import RTCPeerConnection, RTCSessionDescription, AudioStreamTrack, RTCConfiguration
from realtime_backend import Rpc, VoiceError, instructions

# Model used by this installed desktop app's V3 voice-call code.
REALTIME_MODEL = 'gpt-live-1-codex'

LANGUAGES = ('English', 'Arabic', 'Chinese (Simplified)', 'Czech', 'Danish', 'Dutch',
 'Finnish', 'French', 'German', 'Greek', 'Hindi', 'Hungarian', 'Italian', 'Japanese',
 'Korean', 'Norwegian', 'Polish', 'Portuguese', 'Romanian', 'Russian', 'Spanish',
 'Swedish', 'Thai', 'Turkish', 'Ukrainian', 'Vietnamese')


def read_wav(data):
    if len(data) > 12_000_000:
        raise VoiceError('Lydfilen er for stor.')
    try:
        with wave.open(io.BytesIO(data), 'rb') as f:
            rate, count = f.getframerate(), f.getnframes()
            if f.getnchannels() != 1 or f.getsampwidth() != 2 or not 8000 <= rate <= 48000:
                raise VoiceError('Bruk mono WAV, 16-bit PCM, 8–48 kHz.')
            if not .1 <= count / rate <= 30:
                raise VoiceError('Lydfilen må vare mellom 0,1 og 30 sekunder.')
            pcm = f.readframes(count)
            if len(pcm) != count * 2:
                raise VoiceError('Ufullstendig lydfil.')
            return np.frombuffer(pcm, dtype='<i2').copy(), rate
    except (wave.Error, EOFError) as exc:
        raise VoiceError('Ugyldig WAV-fil.') from exc


class InputTrack(AudioStreamTrack):
    """20 ms mono frames, silence until user explicitly submits a recording."""
    def __init__(self):
        super().__init__()
        self.frames = asyncio.Queue(maxsize=1600)
        self.pts = 0
        self.started = None

    def submit(self, samples, rate):
        if self.frames.qsize():
            raise VoiceError('Vent til forrige opptak er sendt.')
        if not 8000 <= rate <= 48000 or samples.ndim != 1 or not .1 <= len(samples)/rate <= 30:
            raise VoiceError('Ugyldig opptak.')
        self.feed(samples, rate)

    def feed(self, samples, rate):
        """Queue complete 20 ms microphone blocks on the owning asyncio loop."""
        if rate != 48000:
            samples = np.interp(np.arange(round(len(samples)*48000/rate))*rate/48000,
                                np.arange(len(samples)), samples).astype(np.int16)
        for start in range(0, len(samples), 960):
            chunk = samples[start:start+960]
            if len(chunk) < 960:
                chunk = np.pad(chunk, (0,960-len(chunk)))
            self.frames.put_nowait(chunk.copy())

    async def recv(self):
        if self.started is None:
            self.started = time.monotonic()
        await asyncio.sleep(max(0, self.started + self.pts/48000 - time.monotonic()))
        try:
            pcm = self.frames.get_nowait()
        except asyncio.QueueEmpty:
            pcm = np.zeros(960, dtype=np.int16)
        frame = AudioFrame.from_ndarray(pcm.reshape(1,-1), format='s16', layout='mono')
        frame.sample_rate = 48000
        frame.pts = self.pts
        frame.time_base = Fraction(1,48000)
        self.pts += 960
        return frame


class VoiceSession:
    def __init__(self, on_event, language='Norwegian', mode='verbatim', target='English', version='v3'):
        if language not in LANGUAGES or target not in LANGUAGES or mode not in ('verbatim','translate','listen'):
            raise VoiceError('Ugyldig språk eller modus.')
        self.on_event, self.language, self.mode, self.target = on_event, language, mode, target
        if version not in ('v1','v2','v3'):raise VoiceError('Ugyldig taleprotokoll.')
        self.version=version
        self.rpc = None
        self.pc = None
        self.thread_id = None
        self.ready = asyncio.Event()
        self.finalized = asyncio.Event()
        self.stopped = False
        self.failure = None
        self.pump = None
        self.track = InputTrack()

    async def start(self):
        try:
            self.rpc = await asyncio.to_thread(Rpc)
            self.on_event('account', {'plan': self.rpc.plan})
            result = await asyncio.to_thread(self.rpc.request, 'thread/start', {
                'cwd': self.rpc.folder.name, 'ephemeral': True, 'sandbox': 'read-only',
                'approvalPolicy': 'never', 'baseInstructions': 'No actions. No tools. Voice test only.',
                'developerInstructions': '', 'environments': [], 'selectedCapabilityRoots': [],
                'serviceName': 'chatshift_realtime_demo'})
            self.thread_id = result['thread']['id']
            self.pc = RTCPeerConnection(RTCConfiguration(iceServers=[]))
            self.pc.addTrack(self.track)
            self.channel = self.pc.createDataChannel('oai-events')
            @self.channel.on('message')
            def receive(raw):
                try:
                    event = json.loads(raw)
                except (ValueError, TypeError):
                    return
                # Credentials and binary audio are never forwarded or logged.
                kind = event.get('type','unknown')
                if kind in ('session.started','session.created'):
                    self.ready.set()
                if kind == 'session.closed':
                    self.finalized.set()
                if kind == 'error':
                    self.failure = str(event.get('error',{}).get('message','Talefeil'))[:500]
                    self.ready.set()
                    self.on_event('error',{'message':self.failure})
                if kind in ('session.started','session.created','session.usage.updated',
                            'input_transcript.added','output_transcript.added','turn.created',
                            'turn.delta','turn.done','session.closed','error'):
                    self.on_event('remote', event)
            @self.pc.on('connectionstatechange')
            async def state():
                self.on_event('connection', {'state': self.pc.connectionState})
                if self.pc.connectionState in ('failed','closed') and not self.stopped:
                    self.failure = 'Taleforbindelsen ble brutt.'
                    self.ready.set()
            @self.pc.on('track')
            def remote_track(track):
                # Drain output, but never play model speech over the user's speakers.
                async def drain():
                    try:
                        while not self.stopped:
                            await track.recv()
                    except Exception:
                        pass
                asyncio.create_task(drain())
            await self.pc.setLocalDescription(await self.pc.createOffer())
            await asyncio.to_thread(self.rpc.request, 'thread/realtime/start', {
                'threadId': self.thread_id, 'outputModality': 'text' if self.version=='v2' else 'audio', 'version': self.version,
                **({'model': REALTIME_MODEL} if self.version == 'v3' else {}),
                'transport': {'type': 'webrtc', 'sdp': self.pc.localDescription.sdp},
                'prompt': instructions(self.language,self.mode,self.target),
                'includeStartupContext': False, 'clientManagedHandoffs': True,
                'flushTranscriptTailOnSessionEnd': False})
            self.pump = asyncio.create_task(self._pump())
            await asyncio.wait_for(self.ready.wait(), timeout=30)
            if self.failure:
                raise VoiceError(self.failure)
            self.on_event('ready', {})
        except Exception:
            await self.close()
            raise

    async def _pump(self):
        while not self.stopped:
            try:
                event = self.rpc.events.get_nowait()
            except queue.Empty:
                await asyncio.sleep(.03)
                continue
            method, params = event.get('method',''), event.get('params',{})
            if method == 'thread/realtime/sdp':
                await self.pc.setRemoteDescription(RTCSessionDescription(sdp=params['sdp'],type='answer'))
            elif method == 'thread/realtime/error':
                self.failure = params.get('message', 'Ukjent talefeil')
                self.ready.set()
                self.on_event('error', {'message':self.failure})
            elif method.endswith('transcript/done') or method.endswith('transcript/delta'):
                self.on_event(method, params)
            elif method == 'connection/closed' and not self.stopped:
                self.failure = 'Codex-forbindelsen ble avsluttet.'
                self.ready.set()
                self.on_event('error', {'message':self.failure})

    async def submit(self, samples, rate):
        if self.stopped or not self.ready.is_set() or self.failure:
            raise VoiceError(self.failure or 'Taleøkten er ikke klar.')
        self.track.submit(samples, rate)

    async def finish_recording(self):
        while self.track.frames.qsize() and not self.stopped:
            await asyncio.sleep(.05)
        if self.stopped:
            return
        await asyncio.sleep(.06)  # Let the last queued RTP frame leave the encoder.
        # V3 produces its own response as audio arrives. Sending an additional
        # text instruction here can make it repeat the entire recording.

    async def finalize(self):
        """Server flushes final words; timeout is a failure limit, not a delay."""
        # Closing immediately cuts off audio still inside the speech recognizer.
        # Supply silence, not more microphone input, to finish the final words.
        # A trimmed Norwegian recording lost its last phrase without this tail.
        self.track.feed(np.zeros(43200, dtype=np.int16), 48000)  # 0.9 seconds
        await self.finish_recording()
        self.channel.send(json.dumps({'type': 'session.close'}))
        await asyncio.wait_for(self.finalized.wait(), timeout=15)
        if self.failure:
            raise VoiceError(self.failure)

    async def close(self):
        if self.stopped:
            return
        self.stopped = True
        if self.pump:
            self.pump.cancel()
        if self.rpc and self.thread_id:
            try:
                await asyncio.to_thread(self.rpc.request,'thread/realtime/stop',{'threadId':self.thread_id},5)
            except Exception:
                pass
        if self.pc:
            await self.pc.close()
        if self.rpc:
            await asyncio.to_thread(self.rpc.close)


async def check_file(path, language='Norwegian', mode='verbatim', target='English', version='v3'):
    from pathlib import Path
    def event(kind, data):
        if kind == 'remote' and data.get('type') in ('output_audio.delta',):
            return
        print(json.dumps({'kind':kind,'data':data},ensure_ascii=False),flush=True)
    session = VoiceSession(event,language,mode,target,version)
    try:
        await session.start()
        samples,rate = read_wav(Path(path).read_bytes())
        await session.submit(samples,rate)
        await session.finish_recording()
        await asyncio.sleep(15)
    finally:
        await session.close()

if __name__ == '__main__':
    import sys
    asyncio.run(check_file(*sys.argv[1:]))
