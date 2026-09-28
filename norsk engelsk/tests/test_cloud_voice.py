import io
import json
from email.message import Message
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch
import urllib.error
import wave

from cloud_voice import CloudError, transcribe, validate_wav, TRANSCRIBE_URL


def wav(seconds=1):
    out = io.BytesIO()
    with wave.open(out, 'wb') as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(16000)
        audio.writeframes(b'\0\0' * int(seconds * 16000))
    return out.getvalue()


class Login:
    def __init__(self):
        self.refreshes = []

    def token(self, refresh=False):
        self.refreshes.append(refresh)
        return 'test-token'


class Opener:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.requests = []

    def open(self, request, timeout):
        self.requests.append(request)
        assert request.full_url == TRANSCRIBE_URL
        assert request.get_header('Authorization') == 'Bearer test-token'
        response = self.responses.pop(0)
        if isinstance(response, int):
            raise urllib.error.HTTPError(TRANSCRIBE_URL, response, 'rejected', {}, None)
        if isinstance(response, Exception):
            raise response
        return io.BytesIO(response)


class BackendTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.data = Path(directory.name)
        data_patch = patch('cloud_voice.DATA', self.data)
        data_patch.start()
        self.addCleanup(data_patch.stop)

    def diagnostics(self):
        return json.loads((self.data / '.runtime/cloud-voice-http.json').read_text())

    def test_real_audio_body_and_unicode_transcript(self):
        data = wav()
        transport = Opener(json.dumps({'text': ' Hei, vi må vente. '}).encode())
        self.assertEqual(transcribe(Login(), data, opener=transport), 'Hei, vi må vente.')
        request = transport.requests[0]
        self.assertIn(data, request.data)
        self.assertIn(b'name="file"', request.data)
        from cloud_voice import TRANSCRIPTION_PROMPT
        self.assertIn(b'name="prompt"', request.data)
        self.assertIn(TRANSCRIPTION_PROMPT.encode('utf-8'), request.data)
        self.assertIsNone(request.get_header('Authorization'))

    def test_code_switched_transcript_is_returned_without_rewriting(self):
        spoken = 'Jeg trenger wood og stein ved spawn.'
        transport = Opener(json.dumps({'text': spoken}).encode())
        self.assertEqual(transcribe(Login(), wav(), language='no', opener=transport), spoken)
        self.assertIn(b'name="language"\r\n\r\nno\r\n', transport.requests[0].data)

    def test_expired_session_refreshes_once(self):
        login = Login()
        self.assertEqual(transcribe(login, wav(), opener=Opener(401, b'{"text":"hello"}')), 'hello')
        self.assertEqual(login.refreshes, [False, True])

    def test_access_or_quota_rejections_are_not_retried(self):
        for code in (403, 404, 429, 302):
            login = Login()
            with self.assertRaises(CloudError):
                transcribe(login, wav(), opener=Opener(code))
            self.assertEqual(login.refreshes, [False])

    def test_security_challenge_is_distinct_and_does_not_retry_or_leak_data(self):
        headers = Message()
        headers['CF-Mitigated'] = 'challenge'
        headers['CF-Ray'] = '9fa35d5a7a4dc02e-DPS'
        headers['Set-Cookie'] = 'secret-cookie'
        body = io.BytesIO(b'<html>private server response</html>')
        failure = urllib.error.HTTPError(TRANSCRIBE_URL, 403, 'rejected', headers, body)
        transport = Opener(failure)
        login = Login()
        with patch('cloud_voice.time.sleep', side_effect=AssertionError('No added wait')):
            with self.assertRaisesRegex(CloudError, 'sikkerhetskontroll.*403') as error:
                transcribe(login, wav(), opener=transport)
        self.assertNotIn('Gratis', str(error.exception))
        self.assertEqual(login.refreshes, [False])
        self.assertEqual(len(transport.requests), 1)
        self.assertIsNone(transport.requests[0].get_header('Authorization'))
        self.assertTrue(body.closed)
        entries = self.diagnostics()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['outcome'], 'security_challenge')
        self.assertEqual(entries[0]['cf_ray'], '9fa35d5a7a4dc02e-DPS')
        self.assertEqual(set(entries[0]), {'time_utc', 'status', 'outcome', 'elapsed_ms', 'cf_ray'})
        for sensitive in ('test-token', 'secret-cookie', 'private server response'):
            self.assertNotIn(sensitive, json.dumps(entries))

    def test_generic_403_is_not_assumed_to_be_a_challenge_or_free_account(self):
        with self.assertRaises(CloudError) as error:
            transcribe(Login(), wav(), opener=Opener(403))
        self.assertNotIn('sikkerhetskontroll', str(error.exception))
        self.assertNotIn('Gratis', str(error.exception))
        self.assertEqual(self.diagnostics()[0]['outcome'], 'http_rejected')

    def test_success_after_rejection_is_logged_without_transcript(self):
        with self.assertRaises(CloudError):
            transcribe(Login(), wav(), opener=Opener(403))
        private_text = 'private spoken sentence'
        self.assertEqual(transcribe(Login(), wav(), opener=Opener(json.dumps({'text': private_text}).encode())), private_text)
        entries = self.diagnostics()
        self.assertEqual([entry['status'] for entry in entries], [403, 200])
        self.assertEqual(entries[-1]['outcome'], 'transcribed')
        self.assertNotIn(private_text, json.dumps(entries))

    def test_diagnostics_are_bounded_and_bad_ray_header_is_not_saved(self):
        from cloud_voice import record_http_result
        for _ in range(35):
            record_http_result(403, 'http_rejected', time.monotonic(), {'cf-ray': 'private untrusted header'})
        entries = self.diagnostics()
        self.assertEqual(len(entries), 30)
        self.assertFalse(any('cf_ray' in entry for entry in entries))

    def test_damaged_diagnostic_file_does_not_break_recognition(self):
        path = self.data / '.runtime/cloud-voice-http.json'
        path.parent.mkdir()
        for content in ('not-json', '{}', 'null', '[]' * 17000):
            path.write_text(content)
            self.assertEqual(transcribe(Login(), wav(), opener=Opener(b'{"text":"hello"}')), 'hello')
            self.assertEqual(len(self.diagnostics()), 1)

    def test_readonly_diagnostics_do_not_break_recognition(self):
        with patch('cloud_voice.DATA', self.data / 'file'):
            (self.data / 'file').write_text('not a directory')
            self.assertEqual(transcribe(Login(), wav(), opener=Opener(b'{"text":"hello"}')), 'hello')

    def test_unrecognized_responses_fail(self):
        for body in (b'<html>error</html>', b'[]', b'{"text":""}', b'{"text":4}'):
            with self.assertRaises(CloudError):
                transcribe(Login(), wav(), opener=Opener(body))

    def test_bad_audio_never_requests_credentials(self):
        for data in (b'not wav', wav(.1), wav()[:-100]):
            login = Login()
            with self.assertRaises(CloudError):
                transcribe(login, data, opener=Opener())
            self.assertEqual(login.refreshes, [])

    def test_complete_recording_longer_than_30_seconds_is_allowed(self):
        self.assertEqual(validate_wav(wav(40)), 40)


if __name__ == '__main__':
    unittest.main()

class ProductionTests(unittest.TestCase):
    def test_cancel_before_upload_does_not_request_token(self):
        import threading
        event = threading.Event(); event.set()
        login = Login()
        with self.assertRaises(CloudError):
            transcribe(login, wav(), opener=Opener(), cancel=event)
        self.assertEqual(login.refreshes, [])

    def test_pcm_conversion_and_cleanup_on_failure(self):
        import numpy as np
        from unittest.mock import Mock, patch
        from cloud_voice import CloudTranscriber, DICTATION_TAIL_SAMPLES
        model = CloudTranscriber.__new__(CloudTranscriber)
        login = Mock()
        with patch('cloud_voice.CodexLogin', return_value=login), patch('cloud_voice.transcribe', side_effect=CloudError('offline')) as request, patch('cloud_voice.time.sleep', side_effect=AssertionError('No artificial delay')):
            with self.assertRaises(CloudError):
                model.transcribe(np.full(16000, .5, dtype=np.float32), 'English')
        login.close.assert_called_once()
        with wave.open(io.BytesIO(request.call_args.args[1]), 'rb') as audio:
            self.assertEqual(audio.getframerate(), 16000)
            self.assertEqual(audio.getnchannels(), 1)
            self.assertEqual(audio.getnframes(), 16000 + DICTATION_TAIL_SAMPLES)
            original = np.frombuffer(audio.readframes(16000), dtype='<i2')
            np.testing.assert_array_equal(original, np.full(16000, 16383, dtype='<i2'))
            self.assertEqual(audio.readframes(DICTATION_TAIL_SAMPLES), b'\0\0' * 14400)

    def test_invalid_audio_never_starts_login(self):
        import numpy as np
        from unittest.mock import patch
        from cloud_voice import CloudTranscriber
        model = CloudTranscriber.__new__(CloudTranscriber)
        with patch('cloud_voice.CodexLogin') as login:
            for audio in (np.full(16000, np.nan), np.zeros((16000, 2)), np.zeros(100), np.zeros(0), np.zeros(4799)):
                with self.assertRaises(CloudError):
                    model.transcribe(audio, 'English')
        login.assert_not_called()
