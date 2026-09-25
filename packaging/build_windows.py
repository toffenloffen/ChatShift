"""Build inside a clean Python 3.13 venv; no user settings or models are copied."""
from importlib.metadata import distributions
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'norsk engelsk'


def main():
    args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
            '--windowed', '--onedir', '--name', 'ChatShift',
            '--paths', str(APP), '--icon', str(APP / 'assets/chatshift.ico'),
            '--copy-metadata', 'faster-whisper', '--copy-metadata', 'huggingface-hub']
    for asset in (APP / 'assets').iterdir():
        if asset.suffix in ('.png', '.ico', '.svg'):
            args += ['--add-data', f'{asset};assets']
    for module in APP.glob('*.py'):
        args += ['--hidden-import', module.stem]
    for package in ('faster_whisper', 'deepfilter_stream', 'sounddevice', '_sounddevice_data',
                    'soxr', 'onnxruntime', 'ctranslate2', 'av', 'tokenizers', 'huggingface_hub'):
        args += ['--collect-all', package]
    args += [str(ROOT / 'packaging/launcher.py')]
    subprocess.run(args, cwd=ROOT, check=True)
    output = ROOT / 'dist/ChatShift'
    notices = output / 'licenses'
    notices.mkdir(exist_ok=True)
    for name in ('LICENSE', 'LICENSE-MIT-LEGACY.txt', 'THIRD_PARTY_NOTICES.md'):
        shutil.copy2(ROOT / name, notices / name)
    shutil.copytree(ROOT / 'third_party_licenses', notices / 'third_party', dirs_exist_ok=True)
    # Include every installed dependency's actual license and metadata, not a hand-picked list.
    inventory = []
    for dist in distributions():
        name = dist.metadata['Name']
        inventory.append(f'{name}=={dist.version}')
        for entry in dist.files or []:
            parts = entry.parts
            if any(part.endswith('.dist-info') for part in parts) and (
                    'license' in str(entry).lower() or 'copying' in str(entry).lower() or
                    'notice' in str(entry).lower() or entry.name == 'METADATA'):
                target = notices / name / Path(*parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(dist.locate_file(entry), target)
    (notices / 'runtime-inventory.txt').write_text('\n'.join(sorted(inventory)), encoding='utf-8')
    shutil.copy2(Path(sys.base_prefix) / 'LICENSE.txt', notices / 'Python-LICENSE.txt')
    # Source archives fetched separately using fetch_sources.py, including LGPL components.
    shutil.copytree(ROOT / 'build/redistribution-sources', notices / 'sources', dirs_exist_ok=True)
    shutil.copy2(ROOT / 'packaging/COMPONENTS.md', notices / 'COMPONENTS.md')
    compiler = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r'C:\Program Files (x86)\Inno Setup 6\ISCC.exe')
    subprocess.run([str(compiler), str(ROOT / 'packaging/ChatShift.iss')], check=True)


if __name__ == '__main__':
    main()
