"""Cloud launcher: no model downloads or microphone access at setup."""
import json
from pathlib import Path
import runpy
import sys
import traceback
import tkinter as tk
from tkinter import ttk, messagebox
from app_paths import DATA


def self_test():
    import PIL.Image, sounddevice, numpy
    import realtime_adapter, realtime_engine, realtime_backend, audio_recorder
    import importlib.util
    from settings import LANGUAGES
    assert set(LANGUAGES) == set(audio_recorder.LANGUAGE_CODES)
    for module in ('faster_whisper', 'ctranslate2', 'speech_models', 'cloud_voice', 'gpt_transcribe_voice'):
        assert importlib.util.find_spec(module) is not None, module + ' missing from bundle'
    assert (Path(__file__).parent / 'assets/chatshift.ico').is_file()
    from audio_cleanup import clean_audio
    import numpy as np
    cleaned = clean_audio(np.zeros(16000, dtype=np.float32), enabled=True)
    assert np.isfinite(cleaned).all() and len(cleaned) >= 16000
    root = tk.Tk(); root.withdraw(); root.update(); root.destroy()
    from speech_models import MODELS
    (DATA / 'self-test.json').write_text(json.dumps({'ok': True, 'languages': 26,
        'speech_models': {key: label for key, (label, _) in MODELS.items()}}), encoding='utf-8')


def welcome():
    root = tk.Tk()
    root.title('Welcome to ChatShift')
    root.geometry('640x360')
    frame = ttk.Frame(root, padding=28); frame.pack(fill='both', expand=True)
    ttk.Label(frame, text='Your words. More worlds.', font=('Segoe UI', 21)).pack(anchor='w')
    ttk.Label(frame, text='Text and voice · 26 languages', font=('Segoe UI', 12)).pack(anchor='w', pady=16)
    ttk.Label(frame, wraplength=575, text='Noise suppression is included. Choose one speech engine under Voice → AI models.\n\nOnline models send audio to OpenAI. Optional local Whisper models download on first use and recognize speech on your PC.\n\nTranslation uses your ChatGPT sign-in through Codex. Internet and account access are required. Cloud voice is experimental.').pack(anchor='w')
    result = [False]
    def launch():
        (DATA / 'cloud-setup-complete.json').write_text(json.dumps({'version': 1}), encoding='utf-8')
        result[0] = True
        root.destroy()
    ttk.Button(frame, text='Open ChatShift', command=launch).pack(anchor='w', pady=22)
    root.mainloop()
    return result[0]


def main():
    if '--self-test' in sys.argv:
        self_test(); return
    if '--setup' in sys.argv or not (DATA / 'cloud-setup-complete.json').exists():
        if not welcome():
            return
    runpy.run_module('app', run_name='__main__')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        (DATA / 'startup-error.log').write_text(traceback.format_exc(), encoding='utf-8')
        if '--self-test' not in sys.argv:
            messagebox.showerror('ChatShift could not start', 'Please run Setup again to repair ChatShift. Details: ' + str(DATA / 'startup-error.log'))
        sys.exit(1)
