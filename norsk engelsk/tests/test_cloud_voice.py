import io
import json
import unittest
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
        return io.BytesIO(response)


class BackendTests(unittest.TestCase):
    def test_real_audio_body_and_unicode_transcript(self):
        data = wav()
        transport = Opener(json.dumps({'text': ' Hei, vi må vente. '}).encode())
        self.assertEqual(transcribe(Login(), data, opener=transport), 'Hei, vi må vente.')
        request = transport.requests[0]
        self.assertIn(data, request.data)
        self.assertIn(b'name="file"', request.data)
        self.assertIsNone(request.get_header('Authorization'))

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

    def test_unrecognized_responses_fail(self):
        for body in (b'<html>error</html>', b'[]', b'{"text":""}', b'{"text":4}'):
            with self.assertRaises(CloudError):
                transcribe(Login(), wav(), opener=Opener(body))

    def test_bad_audio_never_requests_credentials(self):
        for data in (b'not wav', wav(.1), wav(31), wav()[:-100]):
            login = Login()
            with self.assertRaises(CloudError):
                transcribe(login, data, opener=Opener())
            self.assertEqual(login.refreshes, [])


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
        from cloud_voice import CloudTranscriber
        model = CloudTranscriber.__new__(CloudTranscriber)
        login = Mock()
        with patch('cloud_voice.CodexLogin', return_value=login), patch('cloud_voice.transcribe', side_effect=CloudError('offline')) as request:
            with self.assertRaises(CloudError):
                model.transcribe(np.full(16000, .5, dtype=np.float32), 'English')
        login.close.assert_called_once()
        with wave.open(io.BytesIO(request.call_args.args[1]), 'rb') as audio:
            self.assertEqual(audio.getframerate(), 16000)
            self.assertEqual(audio.getnchannels(), 1)
            self.assertEqual(audio.getnframes(), 16000)

    def test_invalid_audio_never_starts_login(self):
        import numpy as np
        from unittest.mock import patch
        from cloud_voice import CloudTranscriber
        model = CloudTranscriber.__new__(CloudTranscriber)
        with patch('cloud_voice.CodexLogin') as login:
            for audio in (np.full(16000, np.nan), np.zeros((16000, 2)), np.zeros(100)):
                with self.assertRaises(CloudError):
                    model.transcribe(audio, 'English')
        login.assert_not_called()
