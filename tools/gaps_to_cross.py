#!/usr/bin/env python3
"""Send dictionary-grounded topic-sweep suggestions (data/candidates/gapverify-*.txt, made by
tools/check_gaps.py) straight to the second, skeptical check (data/candidates/cross-XXX.txt).

The sweep agent's suggestion counts as the first opinion. The records are saved as
data/checked/gap-<name>.json with "gap": true, and tools/build_site.py shows them only after
a cross-check result exists for the pair.
Usage: python3 tools/gaps_to_cross.py <name>   (e.g. sweep-r1b)
"""
import glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_site import list_level  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data')
SIZE = 250


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else 'sweep'
    starters = json.load(open(f'{D}/levels/pre-a1-starters.json', encoding='utf-8'))
    cefr = json.load(open(f'{D}/levels/cefr.json', encoding='utf-8'))
    recs, rows = [], []
    for f in sorted(glob.glob(f'{D}/candidates/gapverify-*.txt')):
        cur = None
        for line in open(f, encoding='utf-8'):
            if line.startswith('## '):
                cur = line[3:].split('   [')[0].strip()
            elif line.startswith('   - ') and cur:
                uk = line[5:].split('   [')[0].strip()
                m = re.search(r'\[sweep (\S*);', line)
                topic = m.group(1) if m else ''
                recs.append({'en': cur, 'uk': uk, 'v': 'identical', 'ce': cur, 'cu': uk,
                             'lab': [topic] if topic else [], 'gap': True})
                ll = ('-' if cur.isupper() else list_level(cur.lower(), '', starters, cefr)) or '-'
                lists = ', '.join(f'{p} {l}' for p, l in sorted(cefr.get(cur.lower(), {}).items())) or '-'
                rows.append(f"{cur} = {uk}   | first: identical (suggested by topic sweep, needs real check); "
                            f"pos -; list level {ll} (lists: {lists}); british False; labels {topic or '-'}")
        os.remove(f)
    if not recs:
        print('nothing to send')
        return
    out = f'{D}/checked/gap-{name}.json'
    old = json.load(open(out, encoding='utf-8')) if os.path.exists(out) else []
    json.dump(old + recs, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    n = len(glob.glob(f'{D}/candidates/cross-*.txt'))
    made = []
    for i in range(0, len(rows), SIZE):
        p = f'{D}/candidates/cross-{n:03d}.txt'
        open(p, 'w', encoding='utf-8').write('\n'.join(rows[i:i + SIZE]) + '\n')
        made.append(os.path.basename(p)[:-4])
        n += 1
    print(len(recs), 'pairs ->', made)


if __name__ == '__main__':
    main()
