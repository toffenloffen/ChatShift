import hashlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from model_setup import download_verified, progress_text


class DownloadTests(unittest.TestCase):
    def run_download(self, body, expected, length=None):
        response = io.BytesIO(body)
        response.headers = {'Content-Length': str(len(body) if length is None else length)}
        progress = []
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'model.bin'
            with patch('model_setup.urllib.request.urlopen', return_value=response):
                download_verified('https://example.test/model', target, expected,
                                  lambda done, total: progress.append((done, total)))
            self.assertEqual(target.read_bytes(), body)
            self.assertFalse(target.with_suffix('.bin.part').exists())
        return progress

    def test_reports_actual_bytes_and_promotes_verified_file(self):
        body = b'a' * 600_000
        progress = self.run_download(body, hashlib.sha256(body).hexdigest())
        self.assertEqual(progress[0], (0, len(body)))
        self.assertEqual(progress[-1], (len(body), len(body)))
        self.assertGreater(len(progress), 3)

    def test_bad_download_does_not_replace_existing_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'model.bin'
            target.write_bytes(b'old')
            response = io.BytesIO(b'bad')
            response.headers = {'Content-Length': '3'}
            with patch('model_setup.urllib.request.urlopen', return_value=response):
                with self.assertRaisesRegex(ValueError, 'integrity'):
                    download_verified('https://example.test/model', target, 'wrong', lambda *a: None)
            self.assertEqual(target.read_bytes(), b'old')
            self.assertFalse(target.with_suffix('.bin.part').exists())

    def test_interrupted_download_is_not_marked_complete(self):
        with self.assertRaisesRegex(ValueError, 'interrupted'):
            self.run_download(b'abc', hashlib.sha256(b'abc').hexdigest(), length=100)

    def test_cached_verified_file_needs_no_network(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'model.bin'
            target.write_bytes(b'cached')
            with patch('model_setup.urllib.request.urlopen') as request:
                download_verified('https://example.test/model', target,
                                  hashlib.sha256(b'cached').hexdigest(), lambda *a: None)
                request.assert_not_called()

    def test_unknown_size_does_not_invent_a_percentage(self):
        text, percent = progress_text(2_000_000, 0)
        self.assertIn('2.0 MB', text)
        self.assertNotIn('%', text)
        self.assertEqual(percent, 0)
        self.assertEqual(progress_text(5_000_000, 10_000_000), ('5.0 / 10.0 MB · 50%', 50))


if __name__ == '__main__':
    unittest.main()
