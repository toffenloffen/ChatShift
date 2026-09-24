import unittest
from microphones import microphone_choices


class MicrophoneChoicesTests(unittest.TestCase):
    def test_windows_backends_collapse_and_default_gets_full_name(self):
        devices = [
            {'name': 'Microphone (Arctis Nova Pro Wir', 'hostapi': 0, 'max_input_channels': 1},
            {'name': 'Primary Sound Capture Driver', 'hostapi': 1, 'max_input_channels': 1},
            {'name': 'Microphone (Arctis Nova Pro Wireless)', 'hostapi': 1, 'max_input_channels': 1},
            {'name': 'Handset (MX Brio)', 'hostapi': 1, 'max_input_channels': 1},
            {'name': 'Microphone (Arctis Nova Pro Wireless)', 'hostapi': 2, 'max_input_channels': 1},
        ]
        result = microphone_choices(devices, [{'name': name} for name in
            ('MME', 'Windows DirectSound', 'Windows WASAPI')], 0)
        self.assertEqual(result, {'System default · Arctis Nova Pro Wireless': None, 'MX Brio': 3})

    def test_same_named_physical_inputs_are_not_overwritten(self):
        devices = [{'name': 'USB microphone', 'hostapi': 0, 'max_input_channels': 1} for _ in range(2)]
        result = microphone_choices(devices, [{'name': 'ALSA'}], -1)
        self.assertEqual(list(result.values()), [None, 0, 1])

    def test_no_microphone_keeps_default_option(self):
        self.assertEqual(microphone_choices([], [], -1), {'System default microphone': None})
