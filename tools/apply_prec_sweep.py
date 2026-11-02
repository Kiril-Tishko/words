#!/usr/bin/env python3
"""Remove pairs that BOTH independent judges of the precision sweep rejected (tools/workflows/precision-sweep.js).

Input: data/prec-sweep/judged-<batch>-A.json and -B.json (only rejected pairs, with a verdict and reason).
A pair is removed only when both judges reject it; KEEP lists pairs the project keeps anyway, with the reason.
Output: data/qa/zz-prec-sweep.json ({"scalp": {"v": "partial_false_friend", "why": "..."}}), read by build_site.py,
and a summary of agreement per batch.
"""
import glob, json, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data')
KEEP = {
    'Bluetooth': 'used as an everyday generic word in both languages, like Wi-Fi',
}


def main():
    out, both, one, batches = {}, 0, 0, 0
    for fa in sorted(glob.glob(f'{D}/prec-sweep/judged-ps-*-A.json')):
        fb = fa[:-7] + '-B.json'
        if not os.path.exists(fb):
            continue
        try:
            A = {(r['en'], r['uk']): r for r in json.load(open(fa, encoding='utf-8'))}
            B = {(r['en'], r['uk']): r for r in json.load(open(fb, encoding='utf-8'))}
        except Exception as e:
            print('skip', fa, e)
            continue
        batches += 1
        for k in set(A) | set(B):
            if k in A and k in B:
                both += 1
                if k[0] in KEEP:
                    continue
                va, vb = A[k].get('v'), B[k].get('v')
                out[k[0]] = {'v': va if va == vb else (va or vb or 'similar'),
                             'why': 'precision sweep, both judges: ' + (A[k].get('why') or '')[:80]}
            else:
                one += 1
    json.dump(out, open(f'{D}/qa/zz-prec-sweep.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(batches, 'batches judged twice;', both, 'pairs rejected by both judges (', len(out), 'removed );', one,
          'rejected by one judge only (kept)')


if __name__ == '__main__':
    main()
