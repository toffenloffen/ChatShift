"""Install the complete Windows runtime without recording or sending any audio."""
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent


def run(*args):
    subprocess.run([str(arg) for arg in args], cwd=ROOT, check=True)


def main():
    if sys.platform != 'win32':
        raise RuntimeError('This installer currently supports Windows only.')
    if sys.version_info[:2] != (3, 13):
        raise RuntimeError('Please run Install ChatShift.cmd to use Python 3.13.')
    import tkinter  # Check Tcl/Tk before installing dependencies.
    environment = ROOT / '.venv'
    python = environment / 'Scripts' / 'python.exe'
    if not python.exists():
        print('1/4 Creating the ChatShift Python environment...', flush=True)
        venv.EnvBuilder(with_pip=True).create(environment)
    print('2/4 Installing text and voice requirements...', flush=True)
    run(python, '-m', 'pip', 'install', '-r', ROOT / 'requirements-voice.txt')
    print('3/4 Preparing noise suppression and cloud voice. No audio upload.', flush=True)
    run(python, '-c',
        "import sys; from pathlib import Path; sys.path.insert(0, 'packaging'); "
        "from model_setup import download_verified; from deepfilter_stream import _meta; "
        "[download_verified(f'{_meta.RELEASE_BASE_URL}/{n}', "
        "Path('.models/deepfilter')/_meta.MODEL_VERSION/n, h, lambda *a: None) "
        "for n,h in _meta.ASSETS.items()]")
    run(python, '-c',
        "import sys; sys.path.insert(0, 'norsk engelsk'); "
        "import tkinter, sounddevice, numpy; import cloud_voice, audio_recorder; "
        "print('Cloud voice dependencies are ready. Sign in to Codex before use.')")
    print('4/4 Creating desktop shortcut...', flush=True)
    # Pass paths as environment data, never interpolate them into shell code.
    env = os.environ.copy()
    env['CHATSHIFT_INSTALL_ROOT'] = str(ROOT)
    subprocess.run(['powershell.exe', '-NoProfile', '-Command',
        "$root = $env:CHATSHIFT_INSTALL_ROOT; "
        "$shell = New-Object -ComObject WScript.Shell; "
        "$link = $shell.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) 'ChatShift.lnk')); "
        "$link.TargetPath = Join-Path $root 'norsk engelsk/Start ChatShift.vbs'; "
        "$link.WorkingDirectory = Join-Path $root 'norsk engelsk'; "
        "$link.IconLocation = Join-Path $root 'norsk engelsk\\assets\\chatshift.ico'; "
        "$link.Save()"], env=env, check=True)
    print('Ready. Install/open Codex and sign in with your ChatGPT account,\n'
          'then open ChatShift from your desktop. Keep this installation folder.\n'
          'Voice is included: enable Voice input and choose a shortcut in the app.', flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'\nSetup failed: {error}\nFix the error and run Install ChatShift.cmd again.', file=sys.stderr)
        sys.exit(1)
