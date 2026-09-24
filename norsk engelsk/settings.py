"""User preferences; never stores messages or credentials."""
import json
from pathlib import Path
from shortcuts import validate_binding

LANGUAGES = ('English', 'Arabic', 'Chinese (Simplified)', 'Czech', 'Danish', 'Dutch',
             'Finnish', 'French', 'German', 'Greek', 'Hindi', 'Hungarian', 'Italian',
             'Japanese', 'Korean', 'Norwegian', 'Polish', 'Portuguese', 'Romanian',
             'Russian', 'Spanish', 'Swedish', 'Thai', 'Turkish', 'Ukrainian', 'Vietnamese')
SETTINGS_PATH = Path(__file__).resolve().parent / '.settings.json'


def load_settings(path=SETTINGS_PATH):
    result = {'source_language': 'Norwegian', 'target_language': 'English', 'auto_send': True}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(data, dict):
            if data.get('source_language') in LANGUAGES:
                result['source_language'] = data['source_language']
            if data.get('target_language') in LANGUAGES:
                result['target_language'] = data['target_language']
            if isinstance(data.get('auto_send'), bool):
                result['auto_send'] = data['auto_send']
            if isinstance(data.get('text_enabled'), bool):
                result['text_enabled'] = data['text_enabled']
            if 'shortcut' in data:
                result['shortcut'] = validate_binding(data['shortcut'])
            if 'voice_shortcut' in data:
                result['voice_shortcut'] = validate_binding(data['voice_shortcut'])
            if isinstance(data.get('voice_enabled'), bool):
                result['voice_enabled'] = data['voice_enabled']
            if isinstance(data.get('voice_auto_send'), bool):
                result['voice_auto_send'] = data['voice_auto_send']
            if data.get('voice_mode') in ('hold', 'toggle'):
                result['voice_mode'] = data['voice_mode']
    except (OSError, ValueError):
        pass
    return result


def save_settings(language, auto_send, path=SETTINGS_PATH, shortcut=None, source_language='Norwegian', text_enabled=True,
                  voice_shortcut=None, voice_enabled=False, voice_mode='hold', voice_auto_send=False):
    if language not in LANGUAGES or source_language not in LANGUAGES:
        raise ValueError('Choose a language from the list.')
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps({'target_language': language, 'source_language': source_language,
                                    'auto_send': bool(auto_send),
                                    'text_enabled': bool(text_enabled),
                                    'voice_shortcut': validate_binding(voice_shortcut or {'modifiers': [], 'key': None}),
                                    'voice_enabled': bool(voice_enabled), 'voice_mode': voice_mode,
                                    'voice_auto_send': bool(voice_auto_send),
                                    'shortcut': validate_binding(shortcut)}), encoding='utf-8')
    temporary.replace(path)
