# Live multilingual text check — 24 September 2026

12 synthetic written messages were sent through ChatShift’s actual CodexTranslator using the configured Luna backend. No microphone audio or game input was used.

Manual semantic review found the intended negations, numbers and gaming meanings preserved in these examples. One nuance: the Japanese sentence leaves the subject unstated; the result chooses “we”. This is a small spot check, not a language-wide accuracy score or independent native-speaker evaluation.

Observed request times: 2.31–4.85 seconds, including language/session changes. These are not end-to-end game timings.

| Direction | Input | Actual output | Seconds |
| --- | --- | --- | --- |
| Norwegian → English | Ikke angrip ennå. Jeg trenger femti steiner, ikke fem. | Don’t attack yet. I need fifty stones, not five. | 3.08 |
| Swedish → English | Dra inte fler fiender. Healern har slut på mana. | Don’t pull any more enemies. The healer is out of mana. | 2.61 |
| Danish → English | Vent på mig. Brug ikke din cooldown endnu. | Wait for me. Don’t use your cooldown yet. | 2.39 |
| German → English | Heile nicht mich, sondern zuerst den Tank. Ich brauche fünfzig Steine, nicht fünf. | Don’t heal me; heal the tank first. I need fifty stones, not five. | 3.38 |
| Spanish → English | No hagas pull todavía. El healer está OOM. Interrumpe el hechizo, no expulses al jugador. | Don’t pull yet. The healer is OOM. Interrupt the spell; don’t kick the player. | 2.65 |
| French → English | Ne commencez pas le raid sans moi. Je reviens dans dix minutes, pas deux. | Don't start the raid without me. I'll be back in ten minutes, not two. | 4.85 |
| Polish → English | Nie atakuj jeszcze. Potrzebuję pięćdziesięciu kamieni, nie pięciu. | Don't attack yet. I need fifty stones, not five. | 2.31 |
| Ukrainian → English | Не атакуй поки що. Мені потрібно п’ятдесят каменів, а не п’ять. | Don't attack yet. I need fifty stones, not five. | 4.09 |
| Japanese → English | まだ攻撃しないでください。石が5個ではなく50個必要です。 | Don't attack yet. We need 50 stones, not 5. | 2.59 |
| English → Norwegian | Do not heal me. Heal the tank first. I need fifty stones, not five. | Ikke heal meg. Heal tanken først. Jeg trenger femti steiner, ikke fem. | 2.57 |
| English → German | Interrupt the spell. Do not kick the healer from the group. | Unterbrich den Zauber. Wirf den Heiler nicht aus der Gruppe. | 2.61 |
| English → Spanish | The water tank by the house is leaking. Do not replace it yet. | El tanque de agua junto a la casa tiene una fuga. No lo reemplaces todavía. | 2.82 |

Reproduce with `.venv/Scripts/python.exe "norsk engelsk/tests/check_multilingual.py"`. This is an opt-in live check that uses your Codex allowance.
