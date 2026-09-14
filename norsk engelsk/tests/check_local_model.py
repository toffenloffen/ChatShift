"""Print representative translations and measured CPU times; no network."""
from pathlib import Path
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from local_translator import LocalTranslator

start = time.perf_counter()
translator = LocalTranslator()
print(f'Model loaded in {time.perf_counter() - start:.2f}s')
for source in ['Jeg så rød gå inn i ventilen.', 'Hvor ble liket funnet?',
               'Det var ikke meg, jeg var i elektrisk.',
               'kan dere vente litt, jeg må selge noen ting', 'jeg så blå drepe gul']:
    start = time.perf_counter()
    translated = translator.translate(source)
    print(f'{source} => {translated} ({time.perf_counter() - start:.3f}s)')
