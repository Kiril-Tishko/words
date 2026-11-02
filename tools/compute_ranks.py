#!/usr/bin/env python3
"""How common is each English word? Build a ranked list of English words (lemmas).

Reference: the wordfreq 'large' English frequency list.
  - only alphabetic words (apostrophes and hyphens allowed), no digits;
  - words that Wiktionary knows only as names (people, places) are dropped;
  - pure inflected forms (every Wiktionary sense is "plural of X", "simple past of X", ...)
    are folded into their base word, and their frequencies are added to it
    (computers -> computer, went -> go);
  - lemmas are sorted by summed frequency: rank 1 = most used English word.
Output: data/levels/en-rank.tsv  ("word<TAB>frequency" lines, most frequent first, top 100,000).
"""
import json, os, re
from collections import defaultdict

import wordfreq

SRC = os.environ.get('SRC', '/home/user/sources')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, 'data', 'levels', 'en-rank.tsv')
KEEP = 100000

FORM = re.compile(r"(?:^|\b)(?:plural|participle|past tense|simple past|third-person singular[\w ]*|singular|comparative|"
                  r"superlative|gerund|inflection|(?:alternative|obsolete|archaic|nonstandard|dated|rare) (?:spelling|form)|"
                  r"misspelling|contraction)\s+(?:form\s+)?of\s+([a-z][a-z'\-]*)")


def main():
    pos = defaultdict(set)
    lemma_of = {}          # word -> base word, for words whose every sense is an inflection
    has_lemma_sense = set()
    for line in open(f'{SRC}/en_wikt_small.jsonl', encoding='utf-8'):
        d = json.loads(line)
        w = (d.get('w') or '').lower()
        if not w:
            continue
        pos[w].add(d.get('pos'))
        targets = []
        for g, tags, _tr in d.get('s', []):
            m = FORM.search((g or '').lower())
            if m and m.group(1) != w:
                targets.append(m.group(1))
            elif d.get('w') == w and not set(tags) & {'obsolete', 'archaic', 'rare', 'dated', 'historical'}:
                # only lowercase entries count (capitalized ones like "Went" are names/titles)
                has_lemma_sense.add(w)   # a living sense of its own: keep the word as a separate lemma
        if targets and w not in lemma_of:
            lemma_of[w] = targets[0]
    for w in has_lemma_sense:
        lemma_of.pop(w, None)

    freq = defaultdict(float)
    for w, f in wordfreq.get_frequency_dict('en', 'large').items():
        if not re.fullmatch(r"[a-z][a-z'\-]*", w):
            continue
        if len(w) == 1 and w not in ('a', 'i'):
            continue
        p = pos.get(w)
        if p and p <= {'name'}:
            continue
        base = lemma_of.get(w, w)
        if lemma_of.get(base):          # one more hop at most (e.g. a spelling variant of a form)
            base = lemma_of[base]
        freq[base] += f
    ranked = sorted(freq.items(), key=lambda x: -x[1])[:KEEP]
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('# English lemmas by frequency (wordfreq large list; inflected forms folded into base words; '
                'name-only words removed). Built by tools/compute_ranks.py\n')
        for w, fr in ranked:
            f.write(f'{w}\t{fr:.3e}\n')
    print(len(freq), 'lemmas; wrote top', len(ranked))
    print('top 40:', ' '.join(w for w, _ in ranked[:40]))


if __name__ == '__main__':
    main()
