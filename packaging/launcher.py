"""Consumer entry point; no shell, credentials, microphone or game interaction at setup."""
import json
import os
from pathlib import Path
import queue
import runpy
import sys
import threading
import traceback
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from app_paths import DATA, MODELS

# Public model downloads use ChatShift's cache and never inherit a saved Hub token.
os.environ['HF_HOME'] = str(MODELS / 'huggingface')
os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN'] = '1'


def prepare_models(report):
    # Use a dedicated cache, never the developer's or another application's cache.
    from deepfilter_stream import assets
    report('1 of 2 · Downloading and verifying noise suppression…')
    os.environ.pop('DEEPFILTER_STREAM_MODEL_DIR', None)
    paths = assets.ensure_assets(str(MODELS / 'deepfilter'))
    os.environ['DEEPFILTER_STREAM_MODEL_DIR'] = str(paths['onnx'].parent)
    report('2 of 2 · Downloading and checking voice recognition (about 500 MB)…')
    from local_voice import LocalTranscriber
    LocalTranscriber()
    from audio_cleanup import clean_audio
    import numpy as np
    clean_audio(np.zeros(1600, dtype=np.float32), enabled=True)
    (DATA / 'setup-complete.json').write_text(json.dumps({'version': 1}), encoding='utf-8')


def configure_filter():
    from deepfilter_stream import _meta
    os.environ['DEEPFILTER_STREAM_MODEL_DIR'] = str(MODELS / 'deepfilter' / _meta.MODEL_VERSION)


def self_test(models=False):
    """Packaging test: imports/resources only, no login, recording or global hooks."""
    import PIL.Image, sounddevice, soxr, onnxruntime, ctranslate2, tokenizers
    import importlib.util
    assert importlib.util.find_spec('av') is None, 'PyAV must not be in the consumer payload'
    import faster_whisper, deepfilter_stream
    from settings import LANGUAGES
    from local_voice import LANGUAGE_CODES
    assert len(LANGUAGES) == 26 and set(LANGUAGES) == set(LANGUAGE_CODES)
    assert (Path(__file__).parent / 'assets' / 'chatshift.ico').is_file()
    root = tk.Tk(); root.withdraw(); root.update(); root.destroy()
    if models:
        prepare_models(lambda text: None)
        if '--speech-fixture' in sys.argv:
            import wave
            import numpy as np
            from local_voice import LocalTranscriber
            fixture = sys.argv[sys.argv.index('--speech-fixture') + 1]
            with wave.open(fixture, 'rb') as source:
                assert source.getsampwidth() == 2 and source.getnchannels() == 1
                audio = np.frombuffer(source.readframes(source.getnframes()), dtype='<i2').astype(np.float32) / 32768
                audio = soxr.resample(audio, source.getframerate(), 16000)
            transcript = LocalTranscriber().transcribe(audio, 'English')
            assert 'friend' in transcript.lower() and 'quest' in transcript.lower(), transcript
            (DATA / 'transcription-test.json').write_text(json.dumps({'input': 'synthetic PCM speech array', 'text': transcript}), encoding='utf-8')
    (DATA / 'self-test.json').write_text(json.dumps({'ok': True, 'languages': 26, 'models': models}), encoding='utf-8')


def welcome():
    root = tk.Tk()
    root.title('Welcome to ChatShift')
    root.geometry('640x520')
    root.minsize(640, 520)
    root.iconbitmap(str(Path(__file__).parent / 'assets' / 'chatshift.ico'))
    frame = ttk.Frame(root, padding=28); frame.pack(fill='both', expand=True)
    ttk.Label(frame, text='Your words. More worlds.', font=('Segoe UI', 21)).pack(anchor='w')
    ttk.Label(frame, text='Text and voice · 26 languages', font=('Segoe UI', 12)).pack(anchor='w', pady=(6, 20))
    ttk.Label(frame, wraplength=575, text='ChatShift is installed. Prepare voice downloads the local speech and noise suppression models. This can take several minutes. No microphone recording is made. Keep this window open while it works.').pack(anchor='w')
    ttk.Label(frame, wraplength=575, text='Translation also needs Codex and your own ChatGPT account with Codex access. Open the official setup page, install/open Codex, and sign in there. ChatShift cannot sign in for you.').pack(anchor='w', pady=16)
    from help_view import SETUP_URL
    ttk.Button(frame, text='Open official Codex setup', command=lambda: webbrowser.open(SETUP_URL)).pack(anchor='w')
    status = tk.StringVar(value='Ready to prepare voice. Internet connection required.')
    ttk.Label(frame, textvariable=status, wraplength=575).pack(anchor='w', pady=(20, 8))
    progress = ttk.Progressbar(frame, mode='indeterminate'); progress.pack(fill='x')
    events = queue.Queue(); result = [False]; busy = [False]
    row = ttk.Frame(frame); row.pack(fill='x', pady=18)
    def launch():
        result[0] = True; root.destroy()
    def work():
        try:
            prepare_models(lambda text: events.put(('status', text)))
            events.put(('done', 'Voice is ready. Finish Codex sign-in, then open ChatShift.'))
        except Exception:
            (DATA / 'setup-error.log').write_text(traceback.format_exc(), encoding='utf-8')
            events.put(('error', 'Download or model check failed. Check internet access and free disk space, then Retry. Details: ' + str(DATA / 'setup-error.log')))
    def start():
        busy[0] = True; button.config(state='disabled'); skip.config(state='disabled')
        progress.start(); threading.Thread(target=work, daemon=True).start()
    button = ttk.Button(row, text='Prepare voice', command=start); button.pack(side='left')
    skip = ttk.Button(row, text='Continue with text for now', command=launch); skip.pack(side='right')
    def poll():
        try:
            while True:
                kind, text = events.get_nowait(); status.set(text)
                if kind != 'status':
                    busy[0] = False; progress.stop(); skip.config(state='normal')
                    button.config(state='normal', text='Open ChatShift' if kind == 'done' else 'Retry', command=launch if kind == 'done' else start)
        except queue.Empty:
            pass
        root.after(100, poll)
    def close():
        if not busy[0] or messagebox.askyesno('Stop setup?', 'Stop the download and close ChatShift? You can retry next time.'):
            root.destroy()
    root.protocol('WM_DELETE_WINDOW', close)
    poll(); root.mainloop()
    return result[0]


def main():
    if '--self-test' in sys.argv or '--test-models' in sys.argv:
        self_test('--test-models' in sys.argv); return
    configure_filter()
    if '--setup' in sys.argv or not (DATA / 'setup-complete.json').exists():
        if not welcome():
            return
    runpy.run_module('app', run_name='__main__')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        (DATA / 'startup-error.log').write_text(traceback.format_exc(), encoding='utf-8')
        if '--self-test' not in sys.argv and '--test-models' not in sys.argv:
            messagebox.showerror('ChatShift could not start', 'Please run Setup again to repair ChatShift. Details: ' + str(DATA / 'startup-error.log'))
        sys.exit(1)
