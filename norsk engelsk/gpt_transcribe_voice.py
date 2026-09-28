"""Opt-in GPT-Transcribe experiment using the current managed ChatGPT login.

Transcribes audio only. No API keys, conversation responses, alternate engines
or retries after access rejection. Account availability is established by tests,
not assumed from the account plan. Audio and returned text remain in memory.
"""
import json
import secrets
import time
import urllib.error
import urllib.request

from audio_recorder import LANGUAGE_CODES
from cloud_voice import (CloudError, CloudTranscriber, NoRedirect,
                         record_http_result, validate_wav)

TRANSCRIBE_URL = 'https://api.openai.com/v1/audio/transcriptions'
MODEL = 'gpt-transcribe'


def multipart(data, language):
    if language not in ('', *LANGUAGE_CODES.values()):
        raise CloudError('Choose a supported spoken language.')
    boundary = 'chatshift-' + secrets.token_hex(16)
    chunks = [f'--{boundary}\r\nContent-Disposition: form-data; name="model"\r\n\r\n{MODEL}\r\n'.encode()]
    if language:
        chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="languages[]"\r\n\r\n{language}\r\n'.encode())
    chunks.extend([
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="speech.wav"\r\nContent-Type: audio/wav\r\n\r\n'.encode(),
        data, f'\r\n--{boundary}--\r\n'.encode()])
    return b''.join(chunks), 'multipart/form-data; boundary=' + boundary


def transcribe(login, data, language, *, cancel=None, opener=None):
    validate_wav(data)
    body, content_type = multipart(data, language)
    if cancel is not None and cancel.is_set():
        raise CloudError('Voice cancelled.')
    token = login.token(refresh=False)
    request = None
    started = time.monotonic()
    plan = login.account.get('planType', 'unknown')

    def record(code, outcome, headers=None):
        record_http_result(code, outcome, started, headers,
                           backend='gpt-transcribe', plan=plan)

    try:
        if cancel is not None and cancel.is_set():
            raise CloudError('Voice cancelled.')
        request = urllib.request.Request(TRANSCRIBE_URL, data=body, method='POST', headers={
            'Authorization': 'Bearer ' + token,
            'Content-Type': content_type, 'Accept': 'application/json',
            'User-Agent': 'ChatShift-Transcription-Test/0.1',
        })
        opener = opener or urllib.request.build_opener(NoRedirect())
        # This is a failure timeout, not a delay before sending or returning.
        with opener.open(request, timeout=30) as response:
            payload = response.read(1_000_001)
        if cancel is not None and cancel.is_set():
            raise CloudError('Voice cancelled.')
        if len(payload) > 1_000_000:
            record(200, 'invalid_response')
            raise CloudError('GPT-Transcribe returned an unexpectedly large response.')
        result = json.loads(payload)
        text = result.get('text') if isinstance(result, dict) else None
        if not isinstance(text, str) or not text.strip():
            record(200, 'no_speech')
            raise CloudError('GPT-Transcribe did not recognize speech. Try another recording.')
        record(200, 'transcribed')
        return text.strip()
    except urllib.error.HTTPError as exc:
        code = exc.code
        challenge = (exc.headers or {}).get('cf-mitigated', '').lower() == 'challenge'
        try:
            record(code, 'security_challenge' if challenge else 'http_rejected', exc.headers)
        finally:
            exc.close()
        if challenge:
            raise CloudError(f'GPT-Transcribe was stopped by a security check (HTTP {code}).') from None
        messages = {
            401: 'GPT-Transcribe sign-in was rejected (401). Sign in to Codex again.',
            403: 'GPT-Transcribe access was rejected (403). The reason is not confirmed.',
            404: 'GPT-Transcribe model or endpoint is unavailable for this request (404).',
            429: 'GPT-Transcribe request limit reached (429). Try again later.',
        }
        raise CloudError(messages.get(code, f'GPT-Transcribe returned HTTP {code}.')) from None
    except (urllib.error.URLError, TimeoutError, OSError):
        record(None, 'network_error')
        raise CloudError('GPT-Transcribe connection failed or timed out.') from None
    except (ValueError, UnicodeError) as exc:
        if isinstance(exc, CloudError):
            raise
        record(200, 'invalid_response')
        raise CloudError('GPT-Transcribe returned an unknown response format.') from None
    finally:
        if request is not None:
            request.remove_header('Authorization')
        token = None


class GPTTranscriber(CloudTranscriber):
    def __init__(self):
        # Do not cache an account during model selection. The inherited recording
        # path opens a fresh CodexLogin for every submitted clip, then closes it.
        self.plan = 'unknown'

    def transcribe(self, audio, language, cancel=None):
        self.plan = 'unknown'
        return super().transcribe(audio, language, cancel=cancel)

    def _transcribe_wav(self, login, data, language, cancel):
        self.plan = login.account.get('planType') or 'unknown'
        return transcribe(login, data, language, cancel=cancel)
