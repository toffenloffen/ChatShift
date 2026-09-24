"""Present one audio backend's input devices instead of duplicate Windows APIs."""
import re


def friendly_name(name):
    return re.sub(r'^(?:Microphone|Mikrofon|Handset)\s*\((.*)\)?$',
                  lambda match: match.group(1).rstrip(')'), name, flags=re.I).strip()


def microphone_choices(devices, apis, default_input):
    # DirectSound exposes complete names and resamples to the recorder's 16 kHz.
    # WASAPI is intentionally not preferred: many devices only accept their mix rate.
    ranks = {'Windows DirectSound': 0, 'MME': 1, 'Windows WASAPI': 2, 'Windows WDM-KS': 3}
    inputs = [(index, device) for index, device in enumerate(devices)
              if device['max_input_channels'] > 0]
    if not inputs:
        return {'System default microphone': None}
    host = min({device['hostapi'] for _, device in inputs},
               key=lambda value: (ranks.get(apis[value]['name'], 4), value))
    default_name = friendly_name(devices[default_input]['name']) if 0 <= default_input < len(devices) else ''
    selected = []
    for index, device in inputs:
        if device['hostapi'] != host:
            continue
        raw = device['name']
        if raw.casefold().startswith(('primary sound capture', 'primærdriver', 'microsoft sound mapper', 'microsoft lydtilordning')):
            continue
        name = friendly_name(raw)
        selected.append((name, index))
    matches = [(name, index) for name, index in selected if default_name and
               (name.casefold() == default_name.casefold() or
                (len(default_name) >= 8 and name.casefold().startswith(default_name.casefold())))]
    default_label = matches[0][0] if len(matches) == 1 else default_name
    choices = {f'System default · {default_label}' if default_label else 'System default microphone': None}
    for name, index in selected:
        # The default mic already has its own clearly named row.
        if len(matches) == 1 and index == matches[0][1]:
            continue
        label = name
        count = 2
        while label in choices:
            label = f'{name} ({count})'
            count += 1
        choices[label] = index
    return choices


def list_microphones():
    import sounddevice as sd
    return microphone_choices(sd.query_devices(), sd.query_hostapis(), sd.default.device[0])
