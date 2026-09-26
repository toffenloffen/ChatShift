import unittest
from microphones import microphone_choices


class MicrophoneChoicesTests(unittest.TestCase):
    def test_all_windows_backends_remain_selectable_and_default_gets_full_name(self):
        devices = [
            {'name': 'Microphone (Arctis Nova Pro Wir', 'hostapi': 0, 'max_input_channels': 1},
            {'name': 'Primary Sound Capture Driver', 'hostapi': 1, 'max_input_channels': 1},
            {'name': 'Microphone (Arctis Nova Pro Wireless)', 'hostapi': 1, 'max_input_channels': 1},
            {'name': 'Handset (MX Brio)', 'hostapi': 1, 'max_input_channels': 1},
            {'name': 'Microphone (Arctis Nova Pro Wireless)', 'hostapi': 2, 'max_input_channels': 1},
        ]
        result = microphone_choices(devices, [{'name': name} for name in
            ('MME', 'Windows DirectSound', 'Windows WASAPI')], 0)
        self.assertEqual(next(iter(result)), 'System default · Arctis Nova Pro Wireless')
        self.assertEqual(set(result.values()), {None, 0, 2, 3, 4})
        self.assertEqual(result['MX Brio'], 3)
        self.assertIn('Arctis Nova Pro Wireless · Windows WASAPI', result)

    def test_microphone_only_visible_on_wasapi_is_not_hidden_by_directsound(self):
        devices = [
            {'name': 'Laptop microphone', 'hostapi': 0, 'max_input_channels': 1},
            {'name': 'USB headset', 'hostapi': 1, 'max_input_channels': 1},
            {'name': 'Speakers', 'hostapi': 1, 'max_input_channels': 0},
        ]
        result = microphone_choices(devices, [{'name': 'Windows DirectSound'},
                                             {'name': 'Windows WASAPI'}], 0)
        self.assertEqual(result['USB headset'], 1)
        self.assertEqual(result['Laptop microphone'], 0)
        self.assertNotIn('Speakers', result)

    def test_same_named_physical_inputs_are_not_overwritten(self):
        devices = [{'name': 'USB microphone', 'hostapi': 0, 'max_input_channels': 1} for _ in range(2)]
        result = microphone_choices(devices, [{'name': 'ALSA'}], -1)
        self.assertEqual(list(result.values()), [None, 0, 1])

    def test_no_microphone_keeps_default_option(self):
        self.assertEqual(microphone_choices([], [], -1), {'System default microphone': None})
