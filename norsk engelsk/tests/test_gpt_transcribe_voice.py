import io
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import Mock, patch
import urllib.error
import wave

import numpy as np
from audio_recorder import LANGUAGE_CODES
from cloud_voice import CloudError, DICTATION_TAIL_SAMPLES
from gpt_transcribe_voice import GPTTranscriber, TRANSCRIBE_URL, transcribe


def wav():
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(16000)
        output.writeframes(b'\0\0' * 16000)
    return buffer.getvalue()


class TranscribeTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        data = patch('cloud_voice.DATA', self.folder)
        data.start()
        self.addCleanup(data.stop)
        self.login = Mock(account={'planType': 'free'})
        self.login.token.return_value = 'test-secret'
        self.opener = Mock()

    def reply(self, value):
        self.opener.open.return_value = io.BytesIO(json.dumps(value).encode())

    def diagnostics(self):
        return json.loads((self.folder / '.runtime/gpt-transcribe-http.json').read_text())

    def test_all_language_hints_preserve_original_mixed_transcript(self):
        spoken = 'Jeg trenger wood, ikke stone!'
        audio = wav()
        for language in LANGUAGE_CODES.values():
            self.reply({'text': spoken})
            self.assertEqual(transcribe(self.login, audio, language, opener=self.opener), spoken)
            request = self.opener.open.call_args.args[0]
            self.assertEqual(request.full_url, TRANSCRIBE_URL)
            self.assertIn(b'name="model"\r\n\r\ngpt-transcribe\r\n', request.data)
            self.assertIn(f'name="languages[]"\r\n\r\n{language}\r\n'.encode(), request.data)
            self.assertIn(audio, request.data)
            self.assertNotIn(b'name="prompt"', request.data)
            self.assertIsNone(request.get_header('Authorization'))
        entries = self.diagnostics()
        self.assertEqual(entries[-1]['account_plan'], 'free')
        self.assertNotIn(spoken, json.dumps(entries))
        self.assertNotIn('test-secret', json.dumps(entries))
        self.assertFalse((self.folder / '.runtime/cloud-voice-http.json').exists())

    def test_auth_is_chatgpt_only_and_account_rechecked_for_each_clip(self):
        model = GPTTranscriber()
        samples = np.full(16000, .5, dtype=np.float32)
        first = Mock(account={'planType': 'pro'})
        second = Mock(account={'planType': 'free'})
        with patch('cloud_voice.CodexLogin', side_effect=[first, second]), \
             patch('gpt_transcribe_voice.transcribe', return_value='hello') as send:
            for expected in ('pro', 'free'):
                self.assertEqual(model.transcribe(samples, 'English'), 'hello')
                self.assertEqual(model.plan, expected)
            first.close.assert_called_once()
            second.close.assert_called_once()
            self.assertEqual(send.call_args.args[2], 'en')
            with wave.open(io.BytesIO(send.call_args.args[1]), 'rb') as audio:
                self.assertEqual(audio.getnframes(), 16000 + DICTATION_TAIL_SAMPLES)
                self.assertEqual(audio.getframerate(), 16000)
        with patch('cloud_voice.CodexLogin', side_effect=CloudError('no login')):
            with self.assertRaises(CloudError):
                model.transcribe(samples, 'English')
            self.assertEqual(model.plan, 'unknown')

    def test_rejections_do_not_retry_or_switch_engine(self):
        for code in (401, 403, 404, 429, 302):
            self.opener.reset_mock()
            self.login.token.reset_mock()
            failure = urllib.error.HTTPError(TRANSCRIBE_URL, code, 'private', {},
                                            io.BytesIO(b'private error body'))
            self.opener.open.side_effect = failure
            with self.assertRaisesRegex(CloudError, str(code)) as caught:
                transcribe(self.login, wav(), 'no', opener=self.opener)
            self.opener.open.assert_called_once()
            self.login.token.assert_called_once_with(refresh=False)
            self.assertNotIn('private', str(caught.exception))
            self.assertIsNone(self.opener.open.call_args.args[0].get_header('Authorization'))
        self.assertEqual([x['status'] for x in self.diagnostics()], [401, 403, 404, 429, 302])

    def test_cancel_before_and_after_upload_discards_result(self):
        cancel = threading.Event()
        cancel.set()
        with self.assertRaisesRegex(CloudError, 'cancelled'):
            transcribe(self.login, wav(), 'no', opener=self.opener, cancel=cancel)
        self.login.token.assert_not_called()
        self.opener.open.assert_not_called()
        cancel.clear()
        def respond(*args, **kwargs):
            cancel.set()
            return io.BytesIO(b'{"text":"late reply"}')
        self.opener.open.side_effect = respond
        with self.assertRaisesRegex(CloudError, 'cancelled'):
            transcribe(self.login, wav(), 'no', opener=self.opener, cancel=cancel)

    def test_invalid_audio_and_language_do_not_request_credentials(self):
        for audio, language in ((b'bad wav', 'no'), (wav(), 'invalid')):
            with self.assertRaises(CloudError):
                transcribe(self.login, audio, language, opener=self.opener)
        self.login.token.assert_not_called()

    def test_bad_or_empty_reply_returns_clear_error(self):
        for payload in (b'<html>error</html>', b'{"text":""}', b'[]', b'{"text":3}', b'x' * 1000001):
            self.opener.open.return_value = io.BytesIO(payload)
            with self.assertRaises(CloudError):
                transcribe(self.login, wav(), 'no', opener=self.opener)


if __name__ == '__main__':
    unittest.main()
