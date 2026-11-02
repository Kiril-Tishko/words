#!/usr/bin/env python3
"""Collect every pair judged identical (or borderline) in the first check and write
batches for an independent second check (data/candidates/cross-XXX.txt).

Borderline = first verdict 'similar' / 'partial_false_friend' / 'false_friend' where the
automatic matcher found a near-exact form (these are the likeliest wrong rejections).
Pairs already cross-checked are skipped, so this can be re-run as new batches finish.
"""
import glob, json, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data')
SIZE = 150


def main():
    done = set()
    for f in glob.glob(f'{D}/checked/cross-*.json'):
        try:
            for r in json.load(open(f, encoding='utf-8')):
                done.add((r.get('en', '').lower(), r.get('uk', '').lower()))
        except Exception:
            pass
    queued = set()
    for f in glob.glob(f'{D}/candidates/cross-*.txt'):
        for line in open(f, encoding='utf-8'):
            m = re.match(r'(.+?) = (.+?)   \|', line)
            if m:
                queued.add((m.group(1).lower(), m.group(2).lower()))
    rows = []
    for f in sorted(glob.glob(f'{D}/checked/*.json')):
        name = os.path.basename(f)
        if name.startswith('cross-'):
            continue
        try:
            data = json.load(open(f, encoding='utf-8'))
        except Exception:
            continue
        for r in data:
            if not isinstance(r, dict):
                continue
            v = r.get('lv') if r.get('v') == 'not_lemma' else r.get('v')
            if v not in ('identical', 'similar', 'partial_false_friend', 'false_friend'):
                continue
            ce, cu = (r.get('ce') or r.get('en') or '').strip(), (r.get('cu') or r.get('uk') or '').strip()
            if not ce or not cu:
                continue
            if v != 'identical':
                # borderline only: same length-ish and no extra Ukrainian ending
                if not re.search(r'[бвгґджзклмнпрстфхцчшщь]$', cu) or abs(len(ce) - len(cu)) > 2:
                    continue
            key = (ce.lower(), cu.lower())
            if key in done or key in queued:
                continue
            queued.add(key)
            lab = ','.join(r.get('lab') or [])
            rows.append(f"{ce} = {cu}   | first: {v}; pos {r.get('pos') or '-'}; british {bool(r.get('br'))}; labels {lab or '-'}"
                        + (f"; note: {r['note']}" if r.get('note') else ''))
    existing = sorted(glob.glob(f'{D}/candidates/cross-*.txt'))
    n = len(existing)
    made = []
    for i in range(0, len(rows), SIZE):
        p = f'{D}/candidates/cross-{n:03d}.txt'
        open(p, 'w', encoding='utf-8').write('\n'.join(rows[i:i + SIZE]) + '\n')
        made.append(os.path.basename(p)[:-4])
        n += 1
    print(len(rows), 'pairs ->', made)


if __name__ == '__main__':
    main()
