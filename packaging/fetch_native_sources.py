"""Archive upstream's exact FFmpeg recipe and SHA-256-checked source inputs.

Read literal Package fields with AST; never execute downloaded build scripts.
"""
import ast
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import urllib.request
import ssl
import certifi

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/redistribution-sources/native'
OUT.mkdir(parents=True, exist_ok=True)
RECIPE = 'https://raw.githubusercontent.com/PyAV-Org/pyav-ffmpeg/a71bf9279f7a4659154b68ba6783e89be460bcd5/'


def fetch(url, path, sha=None):
    if not path.exists() or (sha and hashlib.sha256(path.read_bytes()).hexdigest() != sha):
        req = urllib.request.Request(url.replace('http://', 'https://'), headers={'User-Agent': 'ChatShift-source-audit'})
        with urllib.request.urlopen(req, timeout=60, context=ssl.create_default_context(cafile=certifi.where())) as response:
            path.write_bytes(response.read())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if sha and digest != sha:
        raise ValueError('Source hash mismatch: ' + path.name)
    return digest


def main():
    files = ['README.rst', 'setup.py', 'pyproject.toml', '.github/workflows/build-ffmpeg.yml',
             'scripts/build-ffmpeg.py', 'scripts/pkg.py', 'scripts/cibuildpkg.py',
             'scripts/cache.py', 'scripts/grab.py', 'scripts/sbom.py',
             'scripts/install-static-clang.sh', 'patches/ffmpeg.patch',
             'patches/amf-headers.patch', 'patches/gmp.patch', 'patches/lame.patch', 'patches/vpx.patch']
    for filename in files:
        target = OUT / 'recipe' / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        fetch(RECIPE + filename, target)
    source = (OUT / 'recipe/scripts/pkg.py').read_text(encoding='utf-8')
    packages = []
    for call in ast.walk(ast.parse(source)):
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == 'Package':
            fields = {k.arg: ast.literal_eval(k.value) for k in call.keywords
                      if k.arg in ('name', 'source_url', 'sha256', 'source_filename')}
            packages.append(fields)
    def one(package):
        target = OUT / (package['name'] + '-' + package.get('source_filename', package['source_url'].split('/')[-1]))
        try:
            fetch(package['source_url'], target, package['sha256'])
            package['status'] = 'verified'
            package['file'] = target.name
        except Exception as error:
            package['status'] = 'unavailable'
            package['error'] = str(error)
        print(package['name'], package['status'], flush=True)
        return package
    with ThreadPoolExecutor(max_workers=5) as pool:
        result = list(pool.map(one, packages))
    (OUT / 'source-manifest.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    import av._core
    (OUT / 'packaged-ffmpeg-build.json').write_text(json.dumps(av._core.library_meta, indent=2), encoding='utf-8')
    missing = [item['name'] for item in result if item['status'] != 'verified']
    if missing:
        raise SystemExit('Upstream source downloads need review: ' + ', '.join(missing))


if __name__ == '__main__':
    main()
