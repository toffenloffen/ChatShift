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
    result = {'target_language': 'English', 'auto_send': True}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(data, dict):
            if data.get('target_language') in LANGUAGES:
                result['target_language'] = data['target_language']
            if isinstance(data.get('auto_send'), bool):
                result['auto_send'] = data['auto_send']
            if 'shortcut' in data:
                result['shortcut'] = validate_binding(data['shortcut'])
    except (OSError, ValueError):
        pass
    return result


def save_settings(language, auto_send, path=SETTINGS_PATH, shortcut=None):
    if language not in LANGUAGES:
        raise ValueError('Choose a language from the list.')
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps({'target_language': language,
                                    'auto_send': bool(auto_send),
                                    'shortcut': validate_binding(shortcut)}), encoding='utf-8')
    temporary.replace(path)
