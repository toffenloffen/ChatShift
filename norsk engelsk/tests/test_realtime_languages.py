import json
import tempfile
import unittest
from pathlib import Path
from settings import LANGUAGES,load_settings,save_settings

class LanguageTests(unittest.TestCase):
 def test_independent_language_preferences_survive_restart(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'settings.json'
   for language in LANGUAGES:
    save_settings('English',False,p,source_language='Norwegian',voice_source_language=language,voice_target_language=language)
    saved=load_settings(p)
    self.assertEqual((saved['source_language'],saved['target_language']),('Norwegian','English'))
    self.assertEqual((saved['voice_source_language'],saved['voice_target_language']),(language,language))
 def test_old_preferences_remain_available_as_migration_defaults(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'settings.json';p.write_text(json.dumps({'source_language':'French','target_language':'German'}))
   saved=load_settings(p)
   self.assertEqual(saved.get('voice_source_language',saved['source_language']),'French')
   self.assertEqual(saved.get('voice_target_language',saved['target_language']),'German')
 def test_invalid_voice_language_rejected(self):
  with tempfile.TemporaryDirectory() as folder:
   with self.assertRaises(ValueError):save_settings('English',False,Path(folder)/'s.json',voice_source_language='invalid')
