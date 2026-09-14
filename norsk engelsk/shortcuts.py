"""Validated, side-specific shortcut preferences."""
MODIFIER_NAMES = {0xA2: 'Left Ctrl', 0xA3: 'Right Ctrl', 0xA4: 'Left Alt',
                  0xA5: 'Right Alt', 0xA0: 'Left Shift', 0xA1: 'Right Shift'}
KEY_NAMES = {13: 'Enter', 32: 'Space', 9: 'Tab', 8: 'Backspace', 46: 'Delete',
             35: 'End', 36: 'Home', 33: 'Page Up', 34: 'Page Down',
             37: 'Left', 38: 'Up', 39: 'Right', 40: 'Down'}
KEY_NAMES.update({vk: chr(vk) for vk in list(range(48, 58)) + list(range(65, 91))})
KEY_NAMES.update({vk: f'F{vk - 111}' for vk in range(112, 124)})


def normalize_modifiers(modifiers):
    result = set(modifiers)
    if 0xA5 in result:
        result.discard(0xA2)  # Windows supplies a synthetic Left Ctrl for AltGr.
    return result


def validate_binding(binding):
    if binding is None:
        return None
    if not isinstance(binding, dict) or set(binding) != {'modifiers', 'key'}:
        raise ValueError('Choose a valid keyboard shortcut.')
    modifiers = binding['modifiers']
    key = binding['key']
    if (not isinstance(modifiers, list) or not modifiers or
            any(type(vk) is not int or vk not in MODIFIER_NAMES for vk in modifiers) or
            type(key) is not int or key not in KEY_NAMES):
        raise ValueError('Use Ctrl or Alt with a letter, number, function key or navigation key.')
    modifiers = normalize_modifiers(modifiers)
    if not modifiers & {0xA2, 0xA3, 0xA4, 0xA5}:
        raise ValueError('Include Ctrl or Alt so normal typing stays unaffected.')
    return {'modifiers': sorted(modifiers), 'key': key}


def binding_label(binding):
    if binding is None:
        return 'Right Ctrl + Enter'
    return ' + '.join([name for vk, name in MODIFIER_NAMES.items() if vk in binding['modifiers']] +
                      [KEY_NAMES[binding['key']]])
