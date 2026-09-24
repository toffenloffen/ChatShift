"""Validated, side-specific shortcut preferences."""
MODIFIER_NAMES = {0xA2: 'Left Ctrl', 0xA3: 'Right Ctrl', 0xA4: 'Left Alt',
                  0xA5: 'Right Alt', 0xA0: 'Left Shift', 0xA1: 'Right Shift'}
NUMPAD_ENTER = 0x10D  # Internal key ID: VK_RETURN with the extended-key flag.
KEY_NAMES = {13: 'Enter', 32: 'Space', 9: 'Tab', 8: 'Backspace', 46: 'Delete',
             35: 'End', 36: 'Home', 33: 'Page Up', 34: 'Page Down',
             37: 'Left', 38: 'Up', 39: 'Right', 40: 'Down'}
KEY_NAMES.update({vk: chr(vk) for vk in list(range(48, 58)) + list(range(65, 91))})
KEY_NAMES.update({vk: f'F{vk - 111}' for vk in range(112, 124)})
KEY_NAMES.update({4: 'Mouse wheel click', 5: 'Mouse side 1', 6: 'Mouse side 2'})
KEY_NAMES.update({96+i: f'Num {i}' for i in range(10)})
KEY_NAMES.update({106: 'Num *', 107: 'Num +', 109: 'Num -', 110: 'Num .', 111: 'Num /', 45: 'Insert'})
KEY_NAMES[NUMPAD_ENTER] = 'Num Enter'
KEY_NAMES.update(MODIFIER_NAMES)


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
    if modifiers == [] and key is None:
        return {'modifiers': [], 'key': None}
    if (not isinstance(modifiers, list) or
            any(type(vk) is not int or vk not in MODIFIER_NAMES for vk in modifiers) or
            type(key) is not int or key not in KEY_NAMES):
        raise ValueError('Choose a supported key or mouse button.')
    modifiers = normalize_modifiers(set(modifiers) | ({key} if key in MODIFIER_NAMES else set()))
    modifiers.discard(key)
    if len(modifiers) > 2:
        raise ValueError('Choose up to three buttons.')
    return {'modifiers': sorted(modifiers), 'key': key}


def binding_label(binding):
    if binding is None:
        return 'Right Ctrl + Enter'
    if binding['key'] is None:
        return 'No shortcut'
    return ' + '.join([name for vk, name in MODIFIER_NAMES.items() if vk in binding['modifiers']] +
                      [KEY_NAMES[binding['key']]])
