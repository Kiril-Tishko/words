#!/usr/bin/env python3
"""Make expert-QA input batches (data/qa-in/*.json) for site words that have no QA result yet.

Words in bands up to top-20k get "full" batches (60 cards: also grammar and word partners);
rarer words get "light" batches (160 cards). Current examples/notes are taken from the built
details-<band>.js files, so run tools/build_site.py first.
Usage: tools/make_qa_batches.py            -> prints the new batch names
"""
import glob, json, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data')
FULL_BANDS = {'top-1000', 'top-2000', 'top-3000', 'top-5000', 'top-10k', 'top-20k'}


def load_details():
    det = {}
    for f in glob.glob(f'{REPO}/details-*.js'):
        s = open(f, encoding='utf-8').read()
        m = re.search(r'\|\| \{\}, (\{.*\})\);?\s*$', s, re.S)
        if m:
            det.update(json.loads(m.group(1)))
    return det


def main():
    words = json.load(open(f'{D}/words.json', encoding='utf-8'))
    qa = {}
    for f in glob.glob(f'{D}/qa/*.json'):
        qa.update(json.load(open(f, encoding='utf-8')))
    queued = set()
    for f in glob.glob(f'{D}/qa-in/*.json'):
        if not os.path.exists(f'{D}/qa/{os.path.basename(f)}'):
            queued |= {c['en'] for c in json.load(open(f, encoding='utf-8'))}
    det = load_details()
    full, light = [], []
    for w in words:
        if w['en'] in qa or w['en'] in queued:
            continue
        d = det.get(f"{w['en']}|{w['uk']}", {})
        card = {'en': w['en'], 'uk': w['uk'], 'pos': w.get('pos') or '', 'band': w['band'],
                'share': w.get('share', 100.0), 'raw_rank': w.get('rank_raw'),
                'meaning_hint': w.get('note') or '', 'examples': d.get('ex') or [], 'note': d.get('note') or ''}
        (full if w['band'] in FULL_BANDS else light).append(card)
    made = []
    for kind, cards, size in (('full', full, 60), ('light', light, 160)):
        nums = [int(re.search(r'(\d+)', os.path.basename(f)).group(1)) for f in glob.glob(f'{D}/qa-in/{kind}-*.json')]
        n = max(nums) + 1 if nums else 0
        for i in range(0, len(cards), size):
            name = f'{kind}-{n:03d}'
            json.dump(cards[i:i + size], open(f'{D}/qa-in/{name}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
            made.append(name)
            n += 1
    print(len(full), 'full +', len(light), 'light cards')
    print(json.dumps(made))


if __name__ == '__main__':
    main()
