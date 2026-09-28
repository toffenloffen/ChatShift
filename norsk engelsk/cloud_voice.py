"""Experimental desktop dictation bridge. No API key or local speech model."""
from __future__ import annotations

import io
import json
from datetime import datetime, timezone
import queue
import re
import secrets
import subprocess
import threading
import time
import urllib.error
import urllib.request
import wave

from codex_translator import find_codex
from audio_recorder import LANGUAGE_CODES
from app_paths import DATA

TRANSCRIBE_URL = 'https://chatgpt.com/backend-api/transcribe'
DICTATION_TAIL_SAMPLES = 14400  # 0.9 seconds of silence at 16 kHz.
_DIAGNOSTIC_LOCK = threading.Lock()
# Best-effort instruction: the internal service may ignore the prompt field.
# Do not supply expected words or post-process the returned transcript.
TRANSCRIPTION_PROMPT = (
    'Transcribe only what the speaker actually says, verbatim. '
    'Preserve the original words and every language switch, including foreign '
    'words mixed into a sentence. Do not translate any words into the selected '
    'language or another language. Do not paraphrase, correct grammar, replace '
    'words with synonyms, or add words that were not spoken. '
    'The selected language is a recognition hint, not an output translation target.'
)


class CloudError(ValueError):
    pass


def record_http_result(code, outcome, started, headers=None, *, backend='dictation', plan=None):
    """Keep the last 30 HTTP outcomes locally, never audio, text or credentials."""
    entry = {
        'time_utc': datetime.now(timezone.utc).isoformat(),
        'status': code,
        'outcome': outcome,
        'elapsed_ms': round((time.monotonic() - started) * 1000),
    }
    ray = (headers or {}).get('cf-ray', '')
    if re.fullmatch(r'[0-9a-fA-F]{8,32}-[A-Z0-9]{3,6}', ray):
        entry['cf_ray'] = ray
    if backend == 'gpt-transcribe':
        if isinstance(plan, str) and re.fullmatch(r'[a-z_]{1,30}', plan):
            entry['account_plan'] = plan
        filename = 'gpt-transcribe-http.json'
    else:
        filename = 'cloud-voice-http.json'
    path = DATA / '.runtime' / filename
    try:
        with _DIAGNOSTIC_LOCK:
            previous = []
            if path.exists() and path.stat().st_size <= 32_768:
                try:
                    previous = json.loads(path.read_text(encoding='utf-8'))
                    if not isinstance(previous, list):
                        previous = []
                except (ValueError, UnicodeError):
                    pass
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix('.tmp')
            temporary.write_text(json.dumps(previous[-29:] + [entry]), encoding='utf-8')
            temporary.replace(path)
    except OSError:
        pass  # Diagnostics must never interrupt speech recognition.


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class CodexLogin:
    """Own stdio server; credentials remain in memory and never enter logs."""
    def __init__(self):
        self.process = subprocess.Popen(
            [find_codex(), 'app-server', '--stdio', '-c', 'forced_login_method="chatgpt"'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, encoding='utf-8', bufsize=1,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        self.inbox = queue.Queue()
        self.serial = 0
        threading.Thread(target=self._read, daemon=True).start()
        try:
            self.request('initialize', {'clientInfo': {
                'name': 'chatshift_cloud_voice', 'version': '0.1.0'},
                'capabilities': {'experimentalApi': True}})
            self._send({'method': 'initialized', 'params': {}})
            self.account = self.request('account/read', {}).get('account') or {}
            if self.account.get('type') != 'chatgpt':
                raise CloudError('Logg inn i Codex med ChatGPT først. API-nøkkel brukes ikke.')
        except Exception:
            self.close()
            raise

    def _read(self):
        try:
            for line in self.process.stdout:
                self.inbox.put(json.loads(line))
        except (OSError, ValueError):
            pass
        finally:
            self.inbox.put(None)

    def _send(self, data):
        try:
            self.process.stdin.write(json.dumps(data) + '\n')
            self.process.stdin.flush()
        except (OSError, ValueError) as exc:
            raise CloudError('Forbindelsen til Codex ble lukket.') from exc

    def request(self, method, params):
        self.serial += 1
        request_id = self.serial
        self._send({'id': request_id, 'method': method, 'params': params})
        deadline = time.monotonic() + 20
        while True:
            try:
                item = self.inbox.get(timeout=max(0, deadline - time.monotonic()))
            except queue.Empty as exc:
                raise CloudError('Codex svarte ikke innen 20 sekunder.') from exc
            if item is None:
                raise CloudError('Codex-forbindelsen ble avsluttet.')
            if 'method' in item and 'id' in item:
                self._send({'id': item['id'], 'error': {
                    'code': -32601, 'message': 'Dictation client supports no tools.'}})
            elif item.get('id') == request_id:
                if 'error' in item:
                    raise CloudError('Codex støtter ikke innloggingskallet. Oppdater appen.')
                return item['result']

    def token(self, refresh=False):
        result = self.request('getAuthStatus', {'includeToken': True, 'refreshToken': refresh})
        if result.get('authMethod') != 'chatgpt' or not result.get('authToken'):
            raise CloudError('ChatGPT-innlogging mangler. Åpne Codex og logg inn.')
        return result['authToken']

    def close(self):
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=3)
        for pipe in (self.process.stdin, self.process.stdout):
            if pipe:
                pipe.close()


def validate_wav(data):
    if len(data) > 12_000_000:
        raise CloudError('Lydfilen er for stor.')
    try:
        with wave.open(io.BytesIO(data), 'rb') as audio:
            duration = audio.getnframes() / audio.getframerate()
            if audio.getsampwidth() != 2 or audio.getnchannels() != 1:
                raise CloudError('Bruk en mono WAV-fil med 16-bit PCM.')
            if duration < 0.3:
                raise CloudError('Opptaket må vare minst 0,3 sekunder.')
            expected = audio.getnframes() * 2
            if len(audio.readframes(audio.getnframes())) != expected:
                raise CloudError('Lydfilen er ufullstendig.')
            return duration
    except (wave.Error, EOFError, ZeroDivisionError) as exc:
        raise CloudError('Ugyldig WAV-fil.') from exc


def multipart(data, language):
    if language not in ('', *LANGUAGE_CODES.values()):
        raise CloudError('Ugyldig talespråk.')
    boundary = 'chatshift-' + secrets.token_hex(16)
    chunks = [f'--{boundary}\r\nContent-Disposition: form-data; name="prompt"\r\n\r\n{TRANSCRIPTION_PROMPT}\r\n'.encode('utf-8')]
    if language:
        chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="language"\r\n\r\n{language}\r\n'.encode())
    chunks.extend([
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="speech.wav"\r\nContent-Type: audio/wav\r\n\r\n'.encode(),
        data, f'\r\n--{boundary}--\r\n'.encode()])
    return b''.join(chunks), 'multipart/form-data; boundary=' + boundary


def transcribe(login, data, language='no', opener=None, cancel=None):
    validate_wav(data)
    body, content_type = multipart(data, language)
    opener = opener or urllib.request.build_opener(NoRedirect())
    for attempt in range(2):
        if cancel is not None and cancel.is_set():
            raise CloudError('Voice cancelled.')
        token = login.token(refresh=bool(attempt))
        if cancel is not None and cancel.is_set():
            raise CloudError('Voice cancelled.')
        request = urllib.request.Request(TRANSCRIBE_URL, data=body, method='POST', headers={
            'Authorization': 'Bearer ' + token,
            'Content-Type': content_type, 'Accept': 'application/json',
            'User-Agent': 'ChatShift-Cloud-Voice/0.3',
        })
        started = time.monotonic()
        try:
            with opener.open(request, timeout=45) as response:
                payload = response.read(1_000_001)
            if len(payload) > 1_000_000:
                raise CloudError('Uventet stort svar fra taletjenesten.')
            result = json.loads(payload)
            text = result.get('text') if isinstance(result, dict) else None
            if not isinstance(text, str) or not text.strip():
                raise CloudError('Ingen tale ble gjenkjent. Prøv et tydeligere opptak.')
            record_http_result(200, 'transcribed', started)
            return text.strip()
        except urllib.error.HTTPError as exc:
            code = exc.code
            try:
                challenge = (exc.headers or {}).get('cf-mitigated', '').lower() == 'challenge'
                outcome = 'security_challenge' if challenge else 'http_rejected'
                record_http_result(code, outcome, started, exc.headers)
            finally:
                exc.close()
            if challenge:
                raise CloudError(f'Cloud-forbindelsen ble stoppet av en sikkerhetskontroll ({code}).') from None
            if code == 401 and attempt == 0:
                continue
            messages = {
                401: 'ChatGPT-innloggingen ble avvist. Logg inn igjen i Codex.',
                403: 'Cloud-tjenesten avviste forespørselen (403). Årsaken er ikke bekreftet.',
                404: 'Appens interne talekall er ikke tilgjengelig (404).',
                429: 'Talegrensen er nådd (429). Vent før du prøver igjen.',
            }
            raise CloudError(messages.get(code, f'Taletjenesten svarte med HTTP {code}.')) from None
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            record_http_result(None, 'network_error', started)
            raise CloudError('Nettverksfeil eller tidsavbrudd ved talegjenkjenning.') from None
        except (json.JSONDecodeError, UnicodeError) as exc:
            record_http_result(200, 'invalid_response', started)
            raise CloudError('Taletjenesten returnerte et ukjent svarformat.') from None
        finally:
            token = None
            request.remove_header('Authorization')
    raise CloudError('Innloggingen kunne ikke fornyes.')


class CloudTranscriber:
    """ChatGPT-managed dictation, with no persistent credential or model object."""
    def __init__(self):
        login = CodexLogin()
        try:
            self.plan = login.account.get('planType', 'unknown')
        finally:
            login.close()

    def transcribe(self, audio, language, cancel=None):
        import numpy as np
        if language not in LANGUAGE_CODES:
            raise CloudError('Choose a supported spoken language.')
        samples = np.asarray(audio, dtype=np.float32)
        if samples.ndim != 1 or not np.isfinite(samples).all():
            raise CloudError('Invalid microphone audio.')
        if samples.size < 4800:
            raise CloudError('Opptaket må vare minst 0,3 sekunder.')
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes((np.clip(samples, -1, 1) * 32767).astype('<i2').tobytes())
            # Extend only the uploaded file, without recording or sleeping longer.
            # Leave room for the recognizer to finish the last spoken word.
            wav.writeframes(b'\0\0' * DICTATION_TAIL_SAMPLES)
        data = buffer.getvalue()
        validate_wav(data)
        if cancel is not None and cancel.is_set():
            raise CloudError('Voice cancelled.')
        login = CodexLogin()
        try:
            return self._transcribe_wav(login, data, LANGUAGE_CODES[language], cancel)
        finally:
            login.close()

    def _transcribe_wav(self, login, data, language, cancel):
        return transcribe(login, data, language, cancel=cancel)
