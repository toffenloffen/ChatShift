"""Opt-in live 260-case text check. Uses Codex allowance, no game input or audio."""
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codex_translator import CodexTranslator
from settings import LANGUAGES

CASES = [
    ('negation', 'Do not attack yet. Wait until I am ready.'),
    ('roles', 'Do not heal me. Heal the tank first.'),
    ('numbers', 'I need fifty stones, not five, and twelve pieces of wood.'),
    ('timing', 'My cooldown is not ready. Wait ten seconds, not two minutes.'),
    ('gaming', 'The healer is OOM. Do not pull more mobs. Use AoE on the adds.'),
    ('kick', 'Interrupt the spell. Do not kick the healer from the group.'),
    ('ordinary', 'The water tank by the house is leaking. My boss will look at it.'),
    ('names', 'Meet Aria in Tanaris at 18:30. Do not sell the Stonescale Eels yet.'),
    ('condition', 'If the door is locked, wait outside. Otherwise, come in. Do not break it.'),
    ('typos', 'i dont need healin yet, pls wait for me. can we do the dungeon after the raid?'),
]

if __name__ == '__main__':
    folder = Path(__file__).resolve().parents[1] / '.runtime'
    folder.mkdir(exist_ok=True)
    output = folder / 'all-languages-check.json'
    rows = []
    translator = CodexTranslator()
    try:
        for language in LANGUAGES:
            for name, source in CASES:
                started = time.perf_counter()
                row = dict(language=language, case=name, source=source)
                try:
                    row['output'] = translator.translate(source, source_language='English', target_language=language)
                except Exception as exc:
                    row['error'] = str(exc)
                row['seconds'] = round(time.perf_counter()-started, 2)
                rows.append(row)
                output.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(dict(language=language, completed=len(rows), errors=sum('error' in r for r in rows)), ensure_ascii=True), flush=True)
    finally:
        translator.close()
