#!/usr/bin/env python3
"""Turn flag-only second checks (data/checked/flags/cross-rNNN.json) into full cross-check
records (data/checked/cross-rNNN.json): flagged pairs get the flagged verdict, every other pair
in the batch is confirmed identical (level comes from the lists, else C2 + rare)."""
import glob, json, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data')
for f in sorted(glob.glob(f'{D}/checked/flags/cross-r*.json')):
    b = os.path.basename(f)[:-5]
    flags = {(r['en'].lower(), r['uk'].lower()): r for r in json.load(open(f, encoding='utf-8'))}
    out = []
    for line in open(f'{D}/candidates/{b}.txt', encoding='utf-8'):
        m = re.match(r'(.+?) = (.+?)   \|', line)
        if not m:
            continue
        en, uk = m.group(1), m.group(2)
        out.append(flags.get((en.lower(), uk.lower()), {'en': en, 'uk': uk, 'v': 'identical'}))
    json.dump(out, open(f'{D}/checked/{b}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(b, len(out), 'pairs,', len(flags), 'flagged')
