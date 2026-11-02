#!/usr/bin/env python3
"""Corpus frequency for multi-word and hyphenated cards (coffee shop, real-time, fake news).

Single words are ranked from word-frequency lists (tools/compute_ranks.py), but those lists have no phrases,
so phrase ranks used to come only from the expert pass's estimate ("pm", uses per million words).
This script looks every phrase up in the Google Books Ngram corpus (English 2019, years 2015-2019,
case-insensitive, singular + plural of the last word) and puts the number on the same scale as the word list:
  scale = median over reference words of  (word-list frequency of the lemma) / (Books frequency of word + plural)
Output: data/levels/phrase-freq.json  {"coffee shop": {"books": 2.3e-06, "freq": 5.1e-06}, ...}
        (freq = Books frequency x scale; build_site.py blends it with the expert estimate)
Raw API answers are cached in data/levels/ngram-cache.json, so re-runs only fetch new phrases.
"""
import json, os, re, sys, time, urllib.parse, urllib.request
from statistics import median

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data')
CACHE = f'{D}/levels/ngram-cache.json'
API = 'https://books.google.com/ngrams/json?year_start=2015&year_end=2019&corpus=en&smoothing=0&case_insensitive=true&content='
BAD = re.compile(r"[+*/():,\[\]&'’!?\"]")


def plural(p):
    last = p.split(' ')[-1]
    if not re.fullmatch(r'[a-z]+', last) or len(last) < 3:
        return None
    if re.search(r'(s|x|z|ch|sh)$', last):
        return p + 'es'
    if re.search(r'[^aeiou]y$', last):
        return p[:-1] + 'ies'
    return p + 's'


def fetch(terms, cache):
    todo = [t for t in terms if t not in cache]
    for i in range(0, len(todo), 10):
        chunk = todo[i:i + 10]
        url = API + urllib.parse.quote(','.join(chunk), safe='')
        for attempt in range(5):
            try:
                with urllib.request.urlopen(url, timeout=30) as r:
                    data = json.load(r)
                break
            except Exception as e:      # 429 / network: back off
                print('retry', attempt, e, file=sys.stderr)
                time.sleep(4 * (attempt + 1))
        else:
            continue
        got = {}
        for x in data:
            if x.get('type') in ('CASE_INSENSITIVE', 'NGRAM'):
                key = re.sub(r' \(All\)$', '', x['ngram']).replace(' - ', '-').lower()
                ts = x.get('timeseries') or [0]
                got[key] = max(got.get(key, 0.0), sum(ts) / len(ts))
        for t in chunk:
            cache[t] = got.get(t.lower(), 0.0)
        json.dump(cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        time.sleep(1.0)


def main():
    words = json.load(open(f'{D}/words.json', encoding='utf-8'))
    phrases = sorted({w['en'] for w in words if re.search(r'[ \-]', w['en'])})
    cache = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}
    # reference words for the scale: every 50th lemma of the top 20,000
    ranked = [l.split('\t') for l in open(f'{D}/levels/en-rank.tsv', encoding='utf-8') if not l.startswith('#')]
    refs = [(w, float(f)) for w, f in ranked[200:20000:50] if re.fullmatch(r'[a-z]{3,}', w)]
    terms = []
    for p in phrases:
        if BAD.search(p) or len(re.split(r'[ \-]', p)) + p.count('-') > 5:
            continue
        terms.append(p.lower())
        pl = plural(p.lower())
        if pl:
            terms.append(pl)
    for w, _ in refs:
        terms.append(w)
        pl = plural(w)
        if pl:
            terms.append(pl)
    print(len(phrases), 'phrases;', len(set(terms) - set(cache)), 'terms to fetch', flush=True)
    fetch(sorted(set(terms)), cache)
    ratios = []
    for w, f in refs:
        b = cache.get(w, 0.0) + cache.get(plural(w) or '', 0.0)
        if b > 0:
            ratios.append(f / b)
    scale = median(ratios)
    out = {}
    for p in phrases:
        k = p.lower()
        if k not in cache:
            continue
        b = cache.get(k, 0.0) + cache.get(plural(k) or '', 0.0)
        out[p] = {'books': b, 'freq': b * scale}
    json.dump({'scale': scale, 'phrases': out}, open(f'{D}/levels/phrase-freq.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)
    print('scale', round(scale, 3), 'from', len(ratios), 'reference words;', len(out), 'phrases with a count,',
          sum(1 for v in out.values() if v['books'] > 0), 'non-zero')


if __name__ == '__main__':
    main()
