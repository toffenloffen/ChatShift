import unittest
import tempfile
from pathlib import Path
import numpy as np
from audio_cleanup import clean_audio
from settings import save_settings, load_settings


class AudioCleanupTests(unittest.TestCase):
    def test_disabled_is_exact_bypass(self):
        audio = np.random.default_rng(1).normal(0, .1, 16000).astype('float32')
        self.assertIs(clean_audio(audio), audio)

    def test_silence_and_short_buffers_are_finite_and_same_length(self):
        for size in (0, 1, 200, 16000):
            result = clean_audio(np.zeros(size, dtype='float32'), True)
            self.assertGreaterEqual(len(result), size)
            self.assertTrue(np.all(np.isfinite(result)))
            self.assertLess(float(np.max(np.abs(result), initial=0)), 1e-5)

    def test_neural_filter_reduces_stationary_noise(self):
        audio = np.random.default_rng(3).normal(0, .02, 48000).astype('float32')
        output = clean_audio(audio, True, 100, -70)
        self.assertLess(np.std(output[16000:]), np.std(audio[16000:])*.5)
        self.assertGreaterEqual(len(output), len(audio))
        self.assertTrue(np.all(np.isfinite(output)))

    def test_preferences_survive_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'settings.json'
            save_settings('English', False, path, noise_enabled=True,
                          noise_strength=65, noise_threshold=-42)
            result = load_settings(path)
            self.assertTrue(result['noise_enabled'])
            self.assertEqual(result['noise_strength'], 65)
            self.assertEqual(result['noise_threshold'], -42)
