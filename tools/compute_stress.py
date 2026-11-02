#!/usr/bin/env python3
"""Where is the stress in the English word? (for the underline on the card front)

Uses CMUdict (primary stress = 1). The stressed syllable is mapped to a vowel-letter group of the spelling;
the mapping is used only when the number of vowel groups equals the number of syllables (after dropping a
silent final -e), so ambiguous spellings are simply left unmarked. One-syllable words are not marked.
Output: data/levels/stress.json  {"president": [2, 3], ...}  (character span of the stressed vowel letters)
"""
import json, os, re

SRC = os.environ.get('SRC', '/home/user/sources')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data')


def vowel_groups(w):
    groups = []
    for m in re.finditer(r'[aeiouy]+', w):
        a, b = m.span()
        if w[a] == 'y' and a == 0 and b > 1:          # initial y before a vowel is a consonant (yoga)
            a += 1
        if a < b:
            groups.append((a, b))
    return groups


def main():
    prons = {}
    for line in open(f'{SRC}/cmudict.dict', encoding='utf-8'):
        line = line.split('#')[0].strip()
        if not line:
            continue
        w, pr = line.split(' ', 1)
        if re.search(r'\(\d+\)$', w):
            continue                                    # first pronunciation only
        prons[w] = pr.split()
    words = [w['en'] for w in json.load(open(f'{D}/words.json', encoding='utf-8'))]
    out, skipped = {}, 0
    for en in words:
        w = en.lower()
        if not re.fullmatch(r'[a-z]+', w) or en.isupper() or w not in prons:
            continue
        vow = [p for p in prons[w] if p[-1].isdigit()]
        if len(vow) < 2 or not any(p.endswith('1') for p in vow):
            continue
        k = next(i for i, p in enumerate(vow) if p.endswith('1'))
        g = vowel_groups(w)
        if len(g) == len(vow) + 1 and w.endswith('e') and g[-1] == (len(w) - 1, len(w)):
            g = g[:-1]                                  # silent final e (office, minute)
        if len(g) != len(vow):
            skipped += 1
            continue
        out[en] = list(g[k])
    json.dump(out, open(f'{D}/levels/stress.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(out), 'words marked;', skipped, 'skipped (ambiguous spelling)')
    for e in ['president', 'student', 'computer', 'internet', 'hotel', 'season', 'moment', 'theater', 'office', 'idea', 'video', 'taxi', 'project', 'banana', 'museum']:
        if e in out:
            a, b = out[e]
            print(f'  {e[:a]}[{e[a:b]}]{e[b:]}')


if __name__ == '__main__':
    main()
