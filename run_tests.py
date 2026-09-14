"""Run offline tests from any working directory. Close ChatShift first."""
from pathlib import Path
import sys
import unittest

app = Path(__file__).resolve().parent / 'norsk engelsk'
sys.path.insert(0, str(app))
suite = unittest.defaultTestLoader.discover(str(app / 'tests'))
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
