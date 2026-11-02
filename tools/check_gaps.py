#!/usr/bin/env python3
"""Ground-truth check for words suggested by topic sweeps (data/checked/sweep-*.json).

A suggested pair is accepted for verification only if
  - the English word exists in an English dictionary/word list, and
  - the Ukrainian word exists in a Ukrainian dictionary (VESUM, hunspell, Wiktionary) or is
    attested in Ukrainian text (wordfreq zipf >= 1.0), and
  - the pair was not already checked.
Accepted pairs are written as verify batches data/candidates/gapverify-XXX.txt.
Rejected suggestions are logged to data/checked/sweep-rejected.json with the reason.
"""
import glob, json, os, re, sys
from collections import defaultdict

import wordfreq

SRC = os.environ.get('SRC', '/home/user/sources')
DICT_UK = os.environ.get('DICT_UK', '/home/user/brown-uk/dict_uk/data/dict')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def uk_lexicon():
    lex = set()
    for fn in os.listdir(DICT_UK):
        if fn.endswith('.lst'):
            for line in open(f'{DICT_UK}/{fn}', encoding='utf-8'):
                line = line.split('#')[0].strip()
                if line:
                    lex.add(line.split()[0].lower().replace('’', "'"))
    for line in open(f'{SRC}/uk_UA.dic', encoding='utf-8', errors='ignore'):
        lex.add(line.split('/')[0].strip().lower().replace('’', "'"))
    for line in open(f'{SRC}/kaikki.org-dictionary-Ukrainian.jsonl', encoding='utf-8'):
        m = re.search(r'"word": "([^"]+)"', line)
        if m:
            lex.add(m.group(1).lower().replace('’', "'"))
    return lex


def en_lexicon():
    lex = set(l.strip() for l in open(f'{SRC}/words_alpha.txt', encoding='utf-8'))
    for line in open(f'{SRC}/en_wikt_small.jsonl', encoding='utf-8'):
        m = re.match(r'\{"w": "([^"]+)"', line)
        if m:
            lex.add(m.group(1).lower())
    for fn in ('en_US.dic', 'en_GB.dic'):
        for line in open(f'{SRC}/{fn}', encoding='utf-8', errors='ignore'):
            lex.add(line.split('/')[0].strip().lower())
    return lex


def main():
    from find_candidates import NMAP  # noqa: F401  (keeps tools importable together)
    ukl, enl = uk_lexicon(), en_lexicon()
    done = set()
    for f in glob.glob(f'{D}/checked/*.json'):
        if os.path.basename(f).startswith('sweep-'):
            continue
        try:
            for r in json.load(open(f, encoding='utf-8')):
                if isinstance(r, dict):
                    for a, b in ((r.get('en'), r.get('uk')), (r.get('ce'), r.get('cu'))):
                        if a and b:
                            done.add((a.lower(), b.lower().replace('’', "'")))
        except Exception:
            pass
    for f in glob.glob(f'{D}/candidates/gapverify-*.txt'):
        for line in open(f, encoding='utf-8'):
            if line.startswith('## '):
                cur = line[3:].split('   [')[0].strip().lower()
            elif line.strip().startswith('- '):
                done.add((cur, line.strip()[2:].split('   [')[0].strip().lower()))
    accepted, rejected = defaultdict(list), []
    for f in sorted(glob.glob(f'{D}/checked/sweep-*.json')):
        if f.endswith('sweep-rejected.json'):
            continue
        for r in json.load(open(f, encoding='utf-8')):
            en, uk = (r.get('en') or '').strip(), (r.get('uk') or '').strip().replace('’', "'")
            if not en or not uk:
                continue
            key = (en.lower(), uk.lower())
            if key in done:
                continue
            done.add(key)
            en_ok = en.lower() in enl or all(p in enl for p in re.split(r"[ \-']+", en.lower()) if p) or en.isupper()
            zuk = wordfreq.zipf_frequency(uk.lower(), 'uk')
            uk_ok = uk.lower() in ukl or zuk >= 1.0
            if en_ok and uk_ok:
                accepted[en].append((uk, zuk, os.path.basename(f), r.get('topic', '')))
            else:
                rejected.append({'en': en, 'uk': uk, 'why': ('no English entry ' if not en_ok else '') + ('no Ukrainian entry' if not uk_ok else ''), 'src': os.path.basename(f)})
    old = []
    p = f'{D}/checked/sweep-rejected.json'
    if os.path.exists(p):
        old = json.load(open(p, encoding='utf-8'))
    json.dump(old + rejected, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    n = len(glob.glob(f'{D}/candidates/gapverify-*.txt'))
    items = sorted(accepted.items())
    made = []
    for i in range(0, len(items), 120):
        lines = []
        for en, cands in items[i:i + 120]:
            lines.append(f"## {en}   [cefr -; zipf {round(wordfreq.zipf_frequency(en.lower(), 'en'), 2)}] suggested by topic sweep")
            for uk, z, src, topic in cands:
                lines.append(f"   - {uk}   [sweep {topic}; ev dict-checked; zipf-uk {round(z, 2)}]")
        path = f'{D}/candidates/gapverify-{n:03d}.txt'
        open(path, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
        made.append(os.path.basename(path)[:-4])
        n += 1
    print('accepted', sum(len(v) for v in accepted.values()), 'rejected', len(rejected), made)


if __name__ == '__main__':
    main()
