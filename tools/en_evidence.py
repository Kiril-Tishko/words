#!/usr/bin/env python3
"""English-side evidence for the site's words (run when sources are available; the build reads the result).

- missing: English words that no English dictionary or corpus attests (not in English Wiktionary, not in
  Hunspell en_US/en_GB, not in CMUdict, zero frequency in wordfreq). Such cards are often Russian/Ukrainian
  terms written in Latin letters (beskozyrka) or a wrong English form (podometer); they are kept off the site.
- variants: English Wiktionary "alternative spelling/form of X" links, used to merge duplicate cards
  (fiord -> fjord, czar -> tsar).
Output: data/levels/en-evidence.json
"""
import json, os, re
from collections import defaultdict

import wordfreq

SRC = os.environ.get('SRC', '/home/user/sources')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data')
ALT = re.compile(r'^(?:alternative|archaic|obsolete|dated|rare|nonstandard|less common) (?:spelling|form|variant)s? of ([^\s.,;(]+(?: [^\s.,;(]+)?)', re.I)


def main():
    words = [w['en'] for w in json.load(open(f'{D}/words.json', encoding='utf-8'))]
    for f in os.listdir(f'{D}/checked'):
        if f.endswith('.json'):
            try:
                for r in json.load(open(f'{D}/checked/{f}', encoding='utf-8')):
                    if isinstance(r, dict) and (r.get('ce') or r.get('en')):
                        words.append(r.get('ce') or r.get('en'))
            except Exception:
                pass
    want = {w.lower() for w in words}
    wikt, variants = set(), {}
    alt_only = defaultdict(lambda: [0, 0, None])   # word -> [alt senses, all senses, target]
    for line in open(f'{SRC}/en_wikt_small.jsonl', encoding='utf-8'):
        m = re.match(r'\{"w": "((?:[^"\\]|\\.)*)"', line)
        if not m:
            continue
        w = m.group(1).lower()
        wikt.add(w)
        if w not in want:
            continue
        d = json.loads(line)
        for g, _t, _tr in d.get('s', []):
            a = alt_only[w]
            a[1] += 1
            mm = ALT.match((g or '').strip())
            if mm:
                a[0] += 1
                a[2] = a[2] or mm.group(1).lower()
    for w, (na, n, t) in alt_only.items():
        if n and na == n and t and t != w:
            variants[w] = t
    hun = set()
    for fn in ('en_US.dic', 'en_GB.dic'):
        for line in open(f'{SRC}/{fn}', encoding='utf-8', errors='ignore'):
            hun.add(line.split('/')[0].strip().lower())
    cmu = set()
    for line in open(f'{SRC}/cmudict.dict', encoding='utf-8'):
        cmu.add(re.sub(r'\(\d+\)$', '', line.split(' ', 1)[0]).lower())
    missing = []
    for w in sorted(want):
        parts = [p for p in re.split(r"[ \-]+", w) if p]
        attested = (w in wikt or w in hun or w in cmu or wordfreq.zipf_frequency(w, 'en') > 0
                    or (len(parts) > 1 and all(p in wikt or p in hun or wordfreq.zipf_frequency(p, 'en') > 0 for p in parts)))
        if not attested:
            missing.append(w)
    json.dump({'missing': missing, 'variants': variants}, open(f'{D}/levels/en-evidence.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)
    print(len(want), 'words checked;', len(missing), 'without English evidence;', len(variants), 'spelling variants')
    print('e.g.', missing[:25], list(variants.items())[:15])


if __name__ == '__main__':
    main()
