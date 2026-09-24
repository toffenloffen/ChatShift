"""Gaming vocabulary hints; never unconditional word replacement."""
# Spellings only: speech recognition must not receive translation instructions or
# example sentences that it could mistake for spoken content.
SPEECH_GAMING_HINTS = (
    'heal, healer, healing, tank, DPS, aggro, threat, pull, adds, mob, boss, wipe, '
    'CC, AoE, DoT, HoT, OOM, cooldown, CD, LoS, rez, res, buff, debuff, proc, '
    'kite, peel, taunt, interrupt, kick, PUG, LFG, LFM, BiS, loot, raid, dungeon, '
    'AFK, BRB, GG, WP'
)
GAMING_CONTEXT = '''Gaming vocabulary across source languages (including English loanwords):
heal/healer = restore health/the healing role; tank = the role taking enemy attacks;
DPS = damage per second or a damage-dealing role, depending on the sentence.
aggro/threat = enemy attention; pull = engage or lure enemies; adds = extra enemies;
mob = a game creature/enemy; boss = a major encounter enemy; wipe = group defeat.
CC = crowd control; AoE = area effect; DoT = damage over time; HoT = healing over time;
OOM = out of mana; CD/cooldown = ability recovery time or an ability on cooldown;
LoS = line of sight; rez/res = resurrect; buff/debuff = beneficial/harmful effect.
proc = a triggered effect; kite = keep enemies chasing while maintaining distance;
peel = get enemies off an ally; taunt = an ability that draws enemy attention;
interrupt/kick = stop a cast when discussing an enemy spell, but kick from a group
means remove a player. Do not confuse these meanings.
Distinguish the healer (a person/role) from a heal (an action). In Norwegian use
healeren, and in Danish healeren, for "the healer", not healen. In Dutch prefer
natural genezen/healen, never invented conjugations such as heileer. In Arabic
gaming context, retain tank or use a clear role label, not a literal military vehicle.
PUG = a pickup group; LFG = looking for group; LFM = looking for more members;
BiS = best in slot; loot = dropped rewards; raid/dungeon = group game content;
AFK = away from keyboard; BRB = be right back; GG = good game; WP = well played.
Use these meanings only where the sentence supports a gaming interpretation.
Preserve conventional acronyms, player names and game-specific names rather than
inventing expansions or translating them literally.
For named items, characters and places, retain the source spelling rather than
guessing a localized name or partially translating it. Keep multiword item names
together, including Stonescale Eels. Ordinary descriptive nouns still translate.
Use natural target-language gaming terminology, not forced English for every word. Ambiguous abbreviations
without enough context should stay as written. Ordinary sentences retain ordinary
meanings (a water tank, a pet pug, pulling a door, or a boss at work).
Preserve negation, numbers, timing and who does what to whom. Never turn "do not
pull yet" into permission to pull, or "fifty, not five" into five. Do not add tactics
or details not stated by the speaker.'''
