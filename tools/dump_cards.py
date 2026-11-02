#!/usr/bin/env python3
"""Write the built cards (front + back) as plain text, for human or agent review.

Usage: tools/dump_cards.py OUT.txt band [band ...]      (bands: top-1000 top-2000 ... rare)
One block per card, in site order:
  english = ukrainian   [band · rank · share · pos · flags]
    gram / say / stress
    1-4 examples
    note / tags
"""
import json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_js(path, var):
    s = open(path, encoding='utf-8').read()
    if var == 'WORDS':
        m = re.search(r'window\.WORDS = (\[.*\]);', s, re.S)
    else:
        m = re.search(r'\|\| \{\}, (\{.*\})\);?\s*$', s, re.S)
    return json.loads(m.group(1))


def main():
    out, bands = sys.argv[1], sys.argv[2:]
    words = load_js(f'{REPO}/words.js', 'WORDS')
    meta = {w['en']: w for w in json.load(open(f'{REPO}/data/words.json', encoding='utf-8'))}
    det = {}
    for b in bands:
        p = f'{REPO}/details-{b}.js'
        if os.path.exists(p):
            det.update(load_js(p, 'DETAILS'))
    lines = []
    for w in words:
        if w['band'] not in bands:
            continue
        d = det.get(f"{w['en']}|{w['uk']}", {})
        m = meta.get(w['en'], {})
        flags = [f for f in ('ns', 'rude', 'british') if w.get(f)]
        st = w.get('st')
        stress = (w['en'][:st[0]] + '[' + w['en'][st[0]:st[1]] + ']' + w['en'][st[1]:]) if st else '-'
        rank = ('~' if w.get('approx') else '#') + str(w.get('rank', '-'))
        lines.append(f"{w['en']} = {w['uk']}   [{w['band']} · rank {rank} · share {m.get('share', '-')} · "
                     f"{w.get('pos', '-')}{' · ' + ','.join(flags) if flags else ''}]")
        lines.append(f"    gram: {d.get('gram', '-')} | say: {d.get('say', '-')} | stress: {stress}")
        for i, e in enumerate(d.get('ex') or [], 1):
            lines.append(f"    {i}. {e}")
        if d.get('note'):
            lines.append(f"    note: {d['note']}")
        if d.get('tags'):
            lines.append(f"    tags: {', '.join(d['tags'])}")
        lines.append('')
    open(out, 'w', encoding='utf-8').write('\n'.join(lines))
    print(sum(1 for l in lines if ' = ' in l and l[:1] != ' '), 'cards ->', out)


if __name__ == '__main__':
    main()
