"""Fetch verified PyPI source archives for native LGPL wrappers and their vendored code."""
import hashlib
import json
from pathlib import Path
import urllib.request

output = Path(__file__).resolve().parents[1] / 'build/redistribution-sources'
output.mkdir(parents=True, exist_ok=True)
for package, version in [('soxr', '1.1.0'), ('av', '18.1.0')]:
    with urllib.request.urlopen(f'https://pypi.org/pypi/{package}/{version}/json') as response:
        metadata = json.load(response)
    source = next(item for item in metadata['urls'] if item['packagetype'] == 'sdist')
    target = output / source['filename']
    urllib.request.urlretrieve(source['url'], target)
    assert hashlib.sha256(target.read_bytes()).hexdigest() == source['digests']['sha256']
    (output / (source['filename'] + '.json')).write_text(json.dumps(source, indent=2), encoding='utf-8')
