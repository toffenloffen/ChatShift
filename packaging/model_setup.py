"""Download setup assets with real byte progress; never use a saved Hub token."""
import fnmatch
import hashlib
import io
from pathlib import Path
import urllib.request


def download_verified(url, destination, expected_hash, progress):
    destination = Path(destination)
    if destination.exists() and hashlib.sha256(destination.read_bytes()).hexdigest() == expected_hash:
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + '.part')
    try:
        digest = hashlib.sha256()
        with urllib.request.urlopen(url, timeout=30) as response, partial.open('wb') as output:
            total = int(response.headers.get('Content-Length') or 0)
            done = 0
            progress(done, total)
            while chunk := response.read(256 * 1024):
                output.write(chunk)
                digest.update(chunk)
                done += len(chunk)
                progress(done, total)
        if total and done != total:
            raise ValueError('Download was interrupted. Please try again.')
        if digest.hexdigest() != expected_hash:
            raise ValueError('Downloaded file failed its integrity check. Please try again.')
        partial.replace(destination)
    finally:
        partial.unlink(missing_ok=True)


def prepare_downloads(models, report):
    from deepfilter_stream import _meta
    from huggingface_hub import HfApi, hf_hub_download
    from tqdm.auto import tqdm

    folder = models / 'deepfilter' / _meta.MODEL_VERSION
    for filename, digest in _meta.ASSETS.items():
        label = 'Noise suppression · ' + filename
        report(label, 0, 0)
        download_verified(f'{_meta.RELEASE_BASE_URL}/{filename}', folder / filename,
                          digest, lambda done, total: report(label, done, total))

    report('Checking voice download…', 0, 0)
    info = HfApi(token=False).model_info('Systran/faster-whisper-small')
    patterns = ('config.json', 'preprocessor_config.json', 'model.bin',
                'tokenizer.json', 'vocabulary.*')
    filenames = sorted(s.rfilename for s in info.siblings
                       if any(fnmatch.fnmatch(s.rfilename, p) for p in patterns))
    if not {'config.json', 'model.bin', 'tokenizer.json'}.issubset(filenames):
        raise ValueError('The voice download is incomplete. Please try again later.')
    for filename in filenames:
        label = 'Voice recognition · ' + filename
        report(label, 0, 0)

        class SetupProgress(tqdm):
            def __init__(self, *args, **kwargs):
                # Keep byte counters active even in a windowed application.
                kwargs['disable'] = False
                kwargs['file'] = io.StringIO()
                super().__init__(*args, **kwargs)

            def display(self, *args, **kwargs):
                if self.unit == 'B':
                    report(label, self.n, self.total or 0)

        hf_hub_download('Systran/faster-whisper-small', filename,
                        revision=info.sha, cache_dir=str(models / 'voice'),
                        token=False, tqdm_class=SetupProgress)
    return folder


def progress_text(done, total):
    if total > 0:
        percent = min(100, done * 100 / total)
        return f'{done / 1_000_000:.1f} / {total / 1_000_000:.1f} MB · {percent:.0f}%', percent
    if done:
        return f'{done / 1_000_000:.1f} MB downloaded · total size unavailable', 0
    return 'Checking files / connecting…', 0
