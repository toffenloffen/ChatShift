"""Fetch hash-verified noise assets before offline tests on a clean checkout."""
from pathlib import Path
from deepfilter_stream import _meta
from model_setup import download_verified

root = Path(__file__).resolve().parents[1]
folder = root / '.models' / 'deepfilter' / _meta.MODEL_VERSION
for filename, digest in _meta.ASSETS.items():
    download_verified(f'{_meta.RELEASE_BASE_URL}/{filename}', folder / filename,
                      digest, lambda *args: None)
print('Verified DeepFilter assets are ready for offline tests.')
