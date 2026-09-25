"""Keep installed user data separate from replaceable program files."""
import os
from pathlib import Path
import sys

FROZEN = getattr(sys, 'frozen', False)
SOURCE = Path(__file__).resolve().parent
DATA = (Path(os.environ.get('CHATSHIFT_DATA_DIR') or
             str(Path(os.environ['LOCALAPPDATA']) / 'ChatShift'))
        if FROZEN else SOURCE)
MODELS = DATA / 'models' if FROZEN else SOURCE.parent / '.models'
if FROZEN:
    DATA.mkdir(parents=True, exist_ok=True)
