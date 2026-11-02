#!/usr/bin/env python3
"""Separate usage labels by language.

- English labels (shown on cards): from English Wiktionary, for the card's part of speech. A label is
  given only when EVERY sense of the word in that part of speech carries it (so "people" gets nothing,
  "thou" gets archaic).
- uk_nonstd (used only by the site filter "Hide slang"): the Ukrainian word is slang, colloquial, rare,
  archaic or a non-standard spelling — per VESUM / Ukrainian Wiktionary, or per the checkers' labels when
  the English word does not carry that label itself.
Output: data/levels/register.json  {"<english>": {"en": [...], "uk_nonstd": true|false}}
"""
import json, os, re

import wordfreq
from collections import Counter, defaultdict

SRC = os.environ.get('SRC', '/home/user/sources')
DICT_UK = os.environ.get('DICT_UK', '/home/user/brown-uk/dict_uk/data/dict')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data')

EN_TAGS = {'archaic': 'archaic', 'obsolete': 'obsolete', 'dated': 'dated', 'slang': 'slang', 'informal': 'informal',
           'colloquial': 'informal', 'literary': 'literary', 'poetic': 'literary', 'vulgar': 'vulgar',
           'derogatory': 'derogatory', 'rare': 'rare'}
POS = {'noun': {'noun', 'name'}, 'adj': {'adj'}, 'adv': {'adv'}, 'interj': {'intj'}, 'verb': {'verb'},
       'num': {'num'}, 'abbr': {'noun', 'abbrev', 'name', 'adj'}, 'phrase': {'phrase', 'noun', 'intj'}}
NONSTD = {'slang', 'informal', 'archaic', 'obsolete', 'dated'}


def main():
    words = json.load(open(f'{D}/words.json', encoding='utf-8'))
    want = {w['en'] for w in words} | {w['en'].lower() for w in words}
    senses = defaultdict(list)   # en -> [(pos, set(tags))]
    for line in open(f'{SRC}/en_wikt_small.jsonl', encoding='utf-8'):
        m = re.match(r'\{"w": "((?:[^"\\]|\\.)*)"', line)
        if not m or m.group(1) not in want:
            continue
        d = json.loads(line)
        for g, tags, _ in d.get('s', []):
            senses[d['w']].append((d.get('pos'), {EN_TAGS[t] for t in tags if t in EN_TAGS}))

    uk_reg = defaultdict(set)
    for fn, tag in (('slang.lst', 'slang'), ('arch.lst', 'archaic'), ('alt.lst', 'nonstandard')):
        for line in open(f'{DICT_UK}/{fn}', encoding='utf-8'):
            line = line.split('#')[0].strip()
            if line:
                uk_reg[line.split()[0].lower()].add(tag)
    for fn in ('base.lst', 'base-compound.lst'):
        for line in open(f'{DICT_UK}/{fn}', encoding='utf-8'):
            line = line.split('#')[0].strip()
            if not line:
                continue
            for t in re.findall(r':(rare|coll|bad|slang|arch)\b', line):
                uk_reg[line.split()[0].lower()].add({'coll': 'informal', 'arch': 'archaic', 'bad': 'nonstandard'}.get(t, t))
    for line in open(f'{SRC}/kaikki.org-dictionary-Ukrainian.jsonl', encoding='utf-8'):
        m = re.search(r'"word": "([^"]+)"', line)
        if not m:
            continue
        d = json.loads(line)
        tags = {t for s in d.get('senses', []) for t in s.get('tags', [])}
        main = d.get('senses', [{}])[0].get('tags', []) if d.get('senses') else []
        for t in ('archaic', 'obsolete', 'dated', 'slang', 'colloquial', 'rare'):
            if t in main:
                uk_reg[d['word'].lower()].add({'colloquial': 'informal'}.get(t, t))

    out, stats = {}, Counter()
    for w in words:
        en = w['en']
        cand = senses.get(en) or senses.get(en.lower()) or []
        pos_ok = POS.get(w.get('pos') or '', set())
        rel = [t for p, t in cand if p in pos_ok] or [t for p, t in cand]
        en_labels = []
        if rel and all(rel_t for rel_t in rel):
            c = Counter(t for tset in rel for t in tset)
            en_labels = sorted(t for t, n in c.items() if n == len(rel))   # labels shared by every sense
        # Ukrainian-side evidence only: dictionary tags, checkers' slang/informal labels (their archaic/dated
        # labels often describe the English word), or a Ukrainian form far rarer than the English word.
        agent = set(w.get('labels', [])) & {'slang', 'informal'}
        ukr = uk_reg.get(w['uk'].lower(), set())
        z_uk = wordfreq.zipf_frequency(w['uk'].lower(), 'uk')
        z_en = wordfreq.zipf_frequency(en.lower(), 'en')
        uk_nonstd = (bool(ukr & {'slang', 'informal', 'archaic', 'obsolete', 'nonstandard', 'rare'})
                     or bool(agent - set(en_labels)) or (z_uk < 2.0 and z_en >= 3.5))
        out[en] = {'en': en_labels, 'uk_nonstd': uk_nonstd}
        stats['en_labeled'] += bool(en_labels)
        stats['uk_nonstd'] += uk_nonstd
    json.dump(out, open(f'{D}/levels/register.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(dict(stats), 'of', len(words))
    top = [w for w in words if out[w['en']]['uk_nonstd']][:60]
    print('flagged (most used first):', ', '.join(f"{w['en']}={w['uk']}" for w in top))
    print('english labels:', ', '.join(f"{w['en']}:{'/'.join(out[w['en']]['en'])}" for w in words if out[w['en']]['en'])[:700])


if __name__ == '__main__':
    main()
