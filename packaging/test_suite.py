"""Run existing suite using a separate real OS mutex; leave installed ChatShift running."""
from pathlib import Path
import runpy
import sys
import uuid

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'norsk engelsk'))
import windows_input

original = windows_input.kernel32.CreateMutexW
name = 'Local\\ChatShift.InstallerTest.' + str(uuid.uuid4())
windows_input.kernel32.CreateMutexW = lambda security, owner, unused: original(security, owner, name)
try:
    runpy.run_path(str(root / 'run_tests.py'), run_name='__main__')
finally:
    windows_input.kernel32.CreateMutexW = original
