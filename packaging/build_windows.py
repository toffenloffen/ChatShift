"""Build cloud voice from a minimal environment without local speech engines."""
from importlib.metadata import distributions
import os
from pathlib import Path
import shutil
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'norsk engelsk'
LEGACY = {'local_voice', 'filtered_recorder', 'audio_cleanup', 'local_translator', 'model_setup'}
ENGINES = ('faster_whisper', 'deepfilter_stream', 'soxr', 'onnxruntime', 'ctranslate2', 'tokenizers', 'huggingface_hub', 'av')


def main():
    args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--windowed', '--onedir', '--name', 'ChatShift', '--paths', str(APP), '--icon', str(APP / 'assets/chatshift.ico')]
    for name in sorted(LEGACY | set(ENGINES)):
        args += ['--exclude-module', name]
    for asset in (APP / 'assets').iterdir():
        if asset.suffix in ('.png', '.ico', '.svg'):
            args += ['--add-data', f'{asset};assets']
    for module in APP.glob('*.py'):
        if module.stem not in LEGACY:
            args += ['--hidden-import', module.stem]
    for package in ('sounddevice', '_sounddevice_data'):
        args += ['--collect-all', package]
    args += [str(ROOT / 'packaging/launcher.py')]
    environment = os.environ.copy()
    environment.pop('PYTHONPATH', None)
    subprocess.run(args, cwd=ROOT, env=environment, check=True)
    output = ROOT / 'dist/ChatShift'
    notices = output / 'licenses'; notices.mkdir(exist_ok=True)
    for name in ('LICENSE', 'LICENSE-MIT-LEGACY.txt', 'THIRD_PARTY_NOTICES.md'):
        shutil.copy2(ROOT / name, notices / name)
    inventory = []
    for dist in distributions():
        name = dist.metadata['Name']; inventory.append(f'{name}=={dist.version}')
        for entry in dist.files or []:
            if any(part.endswith('.dist-info') for part in entry.parts) and (any(word in str(entry).lower() for word in ('license', 'copying', 'notice')) or entry.name == 'METADATA'):
                target = notices / name / Path(*entry.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(dist.locate_file(entry), target)
    (notices / 'runtime-inventory.txt').write_text('\n'.join(sorted(inventory)), encoding='utf-8')
    shutil.copy2(Path(sys.base_prefix) / 'LICENSE.txt', notices / 'Python-LICENSE.txt')
    shutil.copy2(ROOT / 'packaging/COMPONENTS.md', notices / 'COMPONENTS.md')
    compiler = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r'C:\Program Files (x86)\Inno Setup 6\ISCC.exe')
    subprocess.run([str(compiler), str(ROOT / 'packaging/ChatShift.iss')], check=True)


if __name__ == '__main__':
    main()
