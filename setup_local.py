"""Reproducible local model download; dependencies live in .venv."""
import hashlib
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent / '.models'
URL = 'https://data.argosopentech.com/argospm/v1/translate-nb_en-1_9.argosmodel'
SHA256 = 'ee2e3b3541abecb51566b095d3409d97c61b920c9e37956d211fb8b9e9e7d027'


def main():
    ROOT.mkdir(exist_ok=True)
    archive = ROOT / 'nb_en.argosmodel'
    if not archive.exists():
        with urllib.request.urlopen(URL, timeout=60) as response, archive.open('wb') as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
    if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
        raise ValueError('Modellfilen er ufullstendig eller feil. Den ble ikke pakket ut.')
    with zipfile.ZipFile(archive) as package:
        for member in package.infolist():
            destination = (ROOT / member.filename).resolve()
            if not destination.is_relative_to(ROOT.resolve()):
                raise ValueError('Ugyldig filsti i modellen.')
        package.extractall(ROOT)
    print('Norsk-engelsk språkmodell er klar.')


if __name__ == '__main__':
    main()
