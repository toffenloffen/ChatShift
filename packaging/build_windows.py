"""Build local and experimental online voice without bundling Whisper model files."""
from importlib.metadata import distributions
import os
from pathlib import Path
import shutil
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'norsk engelsk'
sys.path.insert(0, str(APP))
LEGACY = {'local_translator', 'model_setup'}
ENGINES = ()


def main():
    args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean', '--windowed', '--onedir', '--name', 'ChatShift', '--paths', str(APP), '--icon', str(APP / 'assets/chatshift.ico')]
    # Bundle verified noise-suppression assets; never include a Whisper model.
    from deepfilter_stream import _meta
    from model_setup import download_verified
    noise = ROOT / 'build/noise-models'
    for filename, digest in _meta.ASSETS.items():
        download_verified(f'{_meta.RELEASE_BASE_URL}/{filename}', noise / filename,
                          digest, lambda *args: None)
    args += ['--add-data', f'{noise};noise-models']
    for name in sorted(LEGACY | set(ENGINES)):
        args += ['--exclude-module', name]
    for asset in (APP / 'assets').iterdir():
        if asset.suffix in ('.png', '.ico', '.svg'):
            args += ['--add-data', f'{asset};assets']
    for module in APP.glob('*.py'):
        if module.stem not in LEGACY:
            args += ['--hidden-import', module.stem]
    for package in ('sounddevice', '_sounddevice_data', 'deepfilter_stream', 'soxr', 'onnxruntime', 'aiortc', 'av', 'faster_whisper', 'ctranslate2', 'tokenizers', 'huggingface_hub'):
        args += ['--collect-all', package]
    args += [str(ROOT / 'packaging/launcher.py')]
    environment = os.environ.copy()
    environment.pop('PYTHONPATH', None)
    subprocess.run(args, cwd=ROOT, env=environment, check=True)
    output = ROOT / 'dist/ChatShift'
    notices = output / 'licenses'; notices.mkdir(exist_ok=True)
    for name in ('LICENSE', 'LICENSE-MIT-LEGACY.txt', 'THIRD_PARTY_NOTICES.md'):
        shutil.copy2(ROOT / name, notices / name)
    shutil.copytree(ROOT / 'third_party_licenses/deepfilter', notices / 'deepfilter', dirs_exist_ok=True)
    shutil.copytree(ROOT / 'third_party_licenses/realtime', notices / 'realtime', dirs_exist_ok=True)
    sources = notices / 'sources'; sources.mkdir(exist_ok=True)
    for archive in (ROOT / 'build/redistribution-sources').glob('soxr-*'):
        shutil.copy2(archive, sources / archive.name)
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
