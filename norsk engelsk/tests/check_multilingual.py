"""Opt-in live text check. Uses Codex allowance; never types into another app."""
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codex_translator import CodexTranslator

CASES = [
    ('Norwegian', 'English', 'Ikke angrip ennå. Jeg trenger femti steiner, ikke fem.'),
    ('Swedish', 'English', 'Dra inte fler fiender. Healern har slut på mana.'),
    ('Danish', 'English', 'Vent på mig. Brug ikke din cooldown endnu.'),
    ('German', 'English', 'Heile nicht mich, sondern zuerst den Tank. Ich brauche fünfzig Steine, nicht fünf.'),
    ('Spanish', 'English', 'No hagas pull todavía. El healer está OOM. Interrumpe el hechizo, no expulses al jugador.'),
    ('French', 'English', 'Ne commencez pas le raid sans moi. Je reviens dans dix minutes, pas deux.'),
    ('Polish', 'English', 'Nie atakuj jeszcze. Potrzebuję pięćdziesięciu kamieni, nie pięciu.'),
    ('Ukrainian', 'English', 'Не атакуй поки що. Мені потрібно п’ятдесят каменів, а не п’ять.'),
    ('Japanese', 'English', 'まだ攻撃しないでください。石が5個ではなく50個必要です。'),
    ('English', 'Norwegian', 'Do not heal me. Heal the tank first. I need fifty stones, not five.'),
    ('English', 'German', 'Interrupt the spell. Do not kick the healer from the group.'),
    ('English', 'Spanish', 'The water tank by the house is leaking. Do not replace it yet.'),
]

if __name__ == '__main__':
    translator = CodexTranslator()
    results = []
    output = Path(__file__).resolve().parents[1] / '.runtime' / 'multilingual-check.json'
    output.parent.mkdir(exist_ok=True)
    try:
        for source, target, text in CASES:
            started = time.perf_counter()
            result = {'source': source, 'target': target, 'input': text}
            try:
                result['output'] = translator.translate(text, source_language=source, target_language=target)
            except Exception as exc:
                result['error'] = str(exc)
            result['seconds'] = round(time.perf_counter() - started, 2)
            results.append(result)
            output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps(result, ensure_ascii=True), flush=True)
    finally:
        translator.close()
