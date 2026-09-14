import unittest
from local_translator import normalize_chat


class DialectTests(unittest.TestCase):
    def test_user_phrase(self):
        self.assertEqual(normalize_chat('hei tester det hær nå'), 'hei tester det her nå')

    def test_army_is_not_changed(self):
        self.assertEqual(normalize_chat('vi trenger en hær'), 'vi trenger en hær')
