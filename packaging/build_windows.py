"""Build inside a clean Python 3.13 venv; no user settings or models are copied."""
from importlib.metadata import distributions
from importlib.util import find_spec
import difflib
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'norsk engelsk'


def main():
    # Isolated vendor copy: microphone input already supplies float32 PCM arrays.
    # Defer only upstream's optional file decoder imports, without replacing av.
    vendor = ROOT / 'build/vendor'
    upstream = Path(find_spec('faster_whisper').origin).parent
    patched = vendor / 'faster_whisper'
    shutil.copytree(upstream, patched, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__'))
    original = (upstream / 'audio.py').read_text(encoding='utf-8')
    if hashlib.sha256(original.encode()).hexdigest() != '60a1d8638f718cbf6d245aed3e5a5aa61c1f822a0b0fe9b48a7c928d47c23909':
        raise RuntimeError('Unexpected faster-whisper audio.py; review the lazy decoder patch before building.')
    modified = original.replace('import av\n', '', 1)
    modified = modified.replace('    resampler = av.audio.resampler.AudioResampler(', '    import av  # ChatShift: optional file decoding only.\n\n    resampler = av.audio.resampler.AudioResampler(', 1)
    modified = modified.replace('def _ignore_invalid_frames(frames):\n', 'def _ignore_invalid_frames(frames):\n    import av\n', 1)
    modified = modified.replace('def _group_frames(frames, num_samples=None):\n', 'def _group_frames(frames, num_samples=None):\n    import av\n', 1)
    (patched / 'audio.py').write_text(modified, encoding='utf-8')
    args = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--clean',
            '--windowed', '--onedir', '--name', 'ChatShift',
            '--paths', str(APP), '--icon', str(APP / 'assets/chatshift.ico'),
            '--paths', str(vendor), '--exclude-module', 'av',
            '--copy-metadata', 'faster-whisper', '--copy-metadata', 'huggingface-hub']
    for asset in (APP / 'assets').iterdir():
        if asset.suffix in ('.png', '.ico', '.svg'):
            args += ['--add-data', f'{asset};assets']
    for module in APP.glob('*.py'):
        args += ['--hidden-import', module.stem]
    for package in ('faster_whisper', 'deepfilter_stream', 'sounddevice', '_sounddevice_data',
                    'soxr', 'onnxruntime', 'ctranslate2', 'tokenizers', 'huggingface_hub'):
        args += ['--collect-all', package]
    args += [str(ROOT / 'packaging/launcher.py')]
    environment = os.environ.copy()
    environment['PYTHONPATH'] = str(vendor)
    subprocess.run(args, cwd=ROOT, env=environment, check=True)
    output = ROOT / 'dist/ChatShift'
    notices = output / 'licenses'
    notices.mkdir(exist_ok=True)
    (notices / 'faster-whisper-audio.patch').write_text(''.join(difflib.unified_diff(
        original.splitlines(keepends=True), modified.splitlines(keepends=True),
        fromfile='upstream/faster_whisper/audio.py', tofile='chatshift/faster_whisper/audio.py')), encoding='utf-8')
    for name in ('LICENSE', 'LICENSE-MIT-LEGACY.txt', 'THIRD_PARTY_NOTICES.md'):
        shutil.copy2(ROOT / name, notices / name)
    shutil.copytree(ROOT / 'third_party_licenses', notices / 'third_party', dirs_exist_ok=True)
    # Include every installed dependency's actual license and metadata, not a hand-picked list.
    inventory = []
    for dist in distributions():
        name = dist.metadata['Name']
        if name.lower() == 'av':
            continue  # Build resolver dependency, deliberately absent from the product.
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
    sources = notices / 'sources'
    sources.mkdir(exist_ok=True)
    retained = set()
    for archive in (ROOT / 'build/redistribution-sources').iterdir():
        if archive.name.startswith(('soxr-', 'faster_whisper-')) and archive.is_file():
            shutil.copy2(archive, sources / archive.name)
            retained.add(archive.name.split('-')[0])
    if retained != {'soxr', 'faster_whisper'}:
        raise RuntimeError('Missing redistribution sources; run packaging/fetch_sources.py first.')
    forbidden = [p for p in output.rglob('*') if p.name.lower().startswith(('avcodec', 'avdevice', 'avfilter', 'avformat', 'avutil', 'swresample', 'swscale', 'postproc', 'av.libs'))]
    if forbidden or (output / '_internal/av').exists():
        raise RuntimeError('Unexpected PyAV/FFmpeg in consumer payload: ' + str(forbidden))
    shutil.copy2(ROOT / 'packaging/COMPONENTS.md', notices / 'COMPONENTS.md')
    compiler = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r'C:\Program Files (x86)\Inno Setup 6\ISCC.exe')
    subprocess.run([str(compiler), str(ROOT / 'packaging/ChatShift.iss')], check=True)


if __name__ == '__main__':
    main()
