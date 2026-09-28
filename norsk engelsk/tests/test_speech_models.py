import threading
import unittest
from unittest.mock import Mock, patch
import numpy as np
from speech_models import MODELS, ClipRecorder, ClipTranscriber, create_model, get_model
from types import SimpleNamespace


class SpeechModelsTests(unittest.TestCase):
    def test_selector_requires_activation_for_every_option(self):
        import tkinter as tk
        from tkinter import ttk
        from voice_input import VoiceInput
        root = tk.Tk(); root.withdraw()
        voice = VoiceInput.__new__(VoiceInput)
        voice.loading = False
        voice.model_choice = tk.StringVar(root, 'realtime')
        voice.model_label = tk.StringVar(root)
        voice.hint = tk.StringVar(root)
        voice.abort = Mock(); voice.configure = Mock()
        app = SimpleNamespace(root=root, busy=False, voice=voice, preferences_changed=Mock(),
                              speech_model=Mock(), speech_model_key='realtime')
        voice.app = app
        def descendants(widget):
            for child in widget.winfo_children():
                yield child
                yield from descendants(child)
        try:
            for key in ('small', 'medium', 'turbo', 'gpt_transcribe', 'realtime'):
                previous = voice.model_choice.get()
                old = app.speech_model
                VoiceInput.choose_model(voice)
                widgets = list(descendants(root))
                radios = [w for w in widgets if isinstance(w, ttk.Radiobutton)]
                self.assertEqual(len(radios), len(MODELS))
                next(w for w in radios if str(w['value']) == key).invoke()
                self.assertEqual(voice.model_choice.get(), previous)
                with patch('speech_models.create_model', return_value=Mock()) as factory:
                    next(w for w in widgets if isinstance(w, ttk.Button)).invoke()
                    factory.assert_called_once_with(key)
                old.close.assert_called_once()
                self.assertEqual(app.speech_model_key, key)
                self.assertEqual(voice.model_choice.get(), key)
        finally:
            root.destroy()

    def test_switch_closes_previous_engine_and_reuses_only_selected_engine(self):
        choice = Mock(); choice.get.return_value = 'small'
        previous = Mock()
        app = SimpleNamespace(voice=SimpleNamespace(model_choice=choice),
                              speech_model=previous, speech_model_key='realtime')
        current = get_model(app)
        previous.close.assert_called_once()
        self.assertEqual(current.key, 'small')
        self.assertIs(get_model(app), current)
        choice.get.return_value = 'gpt_transcribe'
        with patch.object(current, 'close') as close:
            self.assertEqual(get_model(app).key, 'gpt_transcribe')
            close.assert_called_once()

    def test_each_clip_engine_receives_audio_and_language_without_translation(self):
        for key in ('small', 'medium', 'turbo', 'gpt_transcribe'):
            model = create_model(key)
            self.assertIsInstance(model, ClipTranscriber)
            model.engine = Mock()
            model.engine.transcribe.return_value = 'hei wood'
            clip = Mock()
            samples = np.zeros(16000, dtype=np.float32)
            clip.processed.return_value = samples
            cancel = threading.Event()
            self.assertEqual(model.transcribe(clip, 'Norwegian', cancel), 'hei wood')
            model.engine.transcribe.assert_called_once_with(samples, 'Norwegian', cancel=cancel)

    def test_experimental_selection_loads_only_gpt_transcribe(self):
        model = create_model('gpt_transcribe')
        clip = Mock()
        clip.processed.return_value = np.zeros(16000, dtype=np.float32)
        with patch('gpt_transcribe_voice.GPTTranscriber') as engine, \
             patch('local_voice.LocalTranscriber') as local, \
             patch('cloud_voice.CloudTranscriber') as old_cloud:
            engine.return_value.transcribe.return_value = 'hei wood'
            engine.return_value.plan = 'free'
            self.assertEqual(model.transcribe(clip, 'Norwegian'), 'hei wood')
            engine.assert_called_once_with()
            local.assert_not_called()
            old_cloud.assert_not_called()
            self.assertIn('free', model.account_status)

    def test_noise_filter_output_is_sent_to_recognizer(self):
        clip = ClipRecorder({'enabled': True}, threading.Event())
        clip.audio = np.ones(48000, dtype=np.float32)
        clip.keep_audio = True
        with patch('audio_cleanup.SpeechFilter') as factory:
            factory.return_value.TAIL = 0
            factory.return_value.process.side_effect = lambda frame, enabled: (frame * .25, -12, True)
            samples = clip.processed()
        self.assertAlmostEqual(float(samples[500]), .25, places=4)
        raw, processed = clip.playback()
        self.assertEqual(float(raw[0]), 1.)
        self.assertEqual(float(processed[0]), .25)

    def test_cancel_does_not_load_or_send(self):
        cancel = threading.Event(); cancel.set()
        model = ClipTranscriber('gpt_transcribe')
        with self.assertRaisesRegex(ValueError, 'cancelled'):
            model.transcribe(Mock(), 'English', cancel)
        self.assertIsNone(model.engine)
