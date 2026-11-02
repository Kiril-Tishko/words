#!/usr/bin/env python3
"""Merge checked batches into the master word list and build the website data.

Inputs : data/checked/*.json              (first check, one file per batch)
         data/checked/cross-*.json        (second, independent check; overrides the first)
         data/checked/gap-*.json          (words found by topic sweeps, already checked)
         data/levels/pre-a1-starters.json (A0), data/levels/cefr.json (A1–C2), both keyed by part of speech
Outputs: data/words.json        all identical words with labels and levels (master list)
         data/similar.json      same meaning, different form (for a later set)
         data/false_friends.json
         words.js               data for the website
         index.html             the website (from site/app.html)
"""
import glob, json, os, re, sys, unicodedata
from collections import defaultdict

import wordfreq

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data')
LEVELS = ['A0', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2']
OTHER_LANGS = ['de', 'fr', 'es', 'it', 'pt', 'nl', 'sv', 'pl', 'cs']
USAGE = {'archaic', 'obsolete', 'dated', 'literary', 'informal', 'slang', 'abbreviation', 'technical', 'rare', 'international'}


def clean_uk(s):
    s = unicodedata.normalize('NFC', (s or '').strip()).replace('’', "'").replace('ʼ', "'")
    return ''.join(ch for ch in unicodedata.normalize('NFD', s) if ch != '́').strip()


def clean_en(s):
    return re.sub(r'\s+', ' ', (s or '').strip())


def strip_accents(s):
    return ''.join(ch for ch in unicodedata.normalize('NFD', s) if unicodedata.category(ch) != 'Mn')


def load_checked():
    first, cross, gap = [], {}, []
    for f in sorted(glob.glob(f'{D}/checked/*.json')):
        name = os.path.basename(f)
        try:
            data = json.load(open(f, encoding='utf-8'))
        except Exception as e:
            print('skip broken', name, e, file=sys.stderr)
            continue
        if not isinstance(data, list):
            continue
        if name.startswith('cross-'):
            for r in data:
                if isinstance(r, dict) and r.get('en') and r.get('uk'):
                    # keyed by the pair as it was given to the second checker (= first check's ce/cu)
                    cross[(clean_en(r['en']).lower(), clean_uk(r['uk']).lower())] = r
        else:
            for r in data:
                if isinstance(r, dict):
                    r['_src'] = name
                    (gap if name.startswith('gap-') else first).append(r)
    return first, cross, gap


TOPICS = {'food', 'drinks', 'sport', 'music', 'art', 'media', 'tech', 'science', 'medicine', 'chemistry', 'physics',
          'biology', 'math', 'transport', 'clothing', 'home', 'business', 'finance', 'politics', 'law', 'military',
          'religion', 'education', 'people', 'nature', 'places', 'travel', 'games', 'language', 'units', 'time',
          'emotions', 'history', 'philosophy', 'other'}
# agents sometimes invented their own topic names; fold them into the fixed list
TOPIC_MAP = {'med': 'medicine', 'pharmacology': 'medicine', 'anatomy': 'medicine', 'psychology': 'medicine', 'psy': 'medicine',
             'chem': 'chemistry', 'biochemistry': 'chemistry', 'materials': 'chemistry', 'minerals': 'chemistry',
             'mineralogy': 'chemistry', 'botany': 'nature', 'bot': 'nature', 'plants': 'nature', 'zoology': 'nature',
             'zoo': 'nature', 'animals': 'nature', 'agriculture': 'nature', 'bio': 'biology', 'genetics': 'biology',
             'paleontology': 'biology', 'geology': 'science', 'geo': 'science', 'geography': 'science', 'astronomy': 'science',
             'linguistics': 'language', 'literature': 'language', 'lit': 'language', 'grammar': 'language',
             'phil': 'philosophy', 'logic': 'philosophy', 'technology': 'tech', 'computing': 'tech', 'internet': 'tech',
             'it': 'tech', 'electronics': 'tech', 'mathematics': 'math', 'statistics': 'math', 'num': 'math',
             'measurement': 'units', 'society': 'people', 'sociology': 'people', 'anthropology': 'people',
             'culture': 'art', 'folklore': 'art', 'mythology': 'religion', 'economics': 'finance', 'fin': 'finance',
             'biz': 'business', 'work': 'business', 'textiles': 'clothing', 'cloth': 'clothing', 'fashion': 'clothing',
             'arts': 'art', 'theater': 'art', 'dance': 'art', 'printing': 'art', 'film': 'media', 'sports': 'sport',
             'martial arts': 'sport', 'rel': 'religion', 'pol': 'politics', 'hist': 'history', 'historical': 'history',
             'archaeology': 'history', 'architecture': 'places', 'aviation': 'transport', 'nautical': 'transport',
             'crime': 'law', 'colloquial': 'informal', 'arch': 'archaic'}
NONSTANDARD = {'slang', 'informal', 'archaic', 'obsolete', 'dated'}


def norm_labels(labels):
    out = set()
    for l in labels:
        l = TOPIC_MAP.get(l, l)
        if l in USAGE or l in TOPICS:
            out.add(l)
    if not out & TOPICS:
        out.add('other')
    elif len(out & TOPICS) > 1:
        out.discard('other')
    return sorted(out)


POS_NAMES = {'adjective': 'adj', 'adverb': 'adv', 'interjection': 'interj', 'abbreviation': 'abbr', 'numeral': 'num',
             'preposition': 'prep', 'conjunction': 'conj', 'pronoun': 'pron'}
POS_ALIASES = {'abbr': None, 'phrase': None, 'interj': 'interj', 'num': 'num'}


def list_level(word, pos, starters, cefr):
    """Level from the learner lists for this word in this part of speech (None if not listed)."""
    p = POS_ALIASES.get(pos, pos)
    if word in starters and (not starters[word] or p is None or p in starters[word]):
        return 'A0'
    lv = cefr.get(word)
    if lv:
        if p in lv:
            return lv[p]
        if p is None:
            return min(lv.values())
    return None


def verdict(r):
    v = r.get('v')
    if v == 'not_lemma':
        return r.get('lv') or 'not_lemma'
    return v


def main():
    starters = json.load(open(f'{D}/levels/pre-a1-starters.json', encoding='utf-8'))
    cefr = json.load(open(f'{D}/levels/cefr.json', encoding='utf-8'))
    first, cross, gap = load_checked()

    buckets = defaultdict(dict)  # verdict -> key -> record
    for r in first + gap:
        v = verdict(r)
        ce, cu = clean_en(r.get('ce') or r.get('en')), clean_uk(r.get('cu') or r.get('uk'))
        if not ce or not cu or v in (None, 'unrelated', 'proper_noun', 'not_lemma'):
            continue
        key = (ce.lower(), cu.lower())
        c = cross.get(key)
        if r.get('gap') and c is None:
            continue  # topic-sweep suggestions appear only after the second check
        if c is not None:
            v = c.get('v', v)
            r = {**r, **{k: c[k] for k in ('ce', 'cu', 'pos', 'br', 'lab', 'note', 'lvl') if k in c}}
            ce, cu = clean_en(r.get('ce') or r.get('en')), clean_uk(r.get('cu') or r.get('uk'))
            key = (ce.lower(), cu.lower())
        rec = {'en': ce, 'uk': cu, 'pos': POS_NAMES.get(r.get('pos') or '', r.get('pos') or ''), 'british': bool(r.get('br')), 'lvl': r.get('lvl') if c is not None else None,
               'labels': sorted({l for l in (r.get('lab') or []) if isinstance(l, str)}),
               'note': (r.get('note') or '').strip(), 'checked': 2 if c is not None else 1, 'src': r.get('_src')}
        old = buckets[v].get(key)
        if old is None or rec['checked'] > old['checked']:
            buckets[v][key] = rec

    ident = list(buckets['identical'].values())
    # one card per English word: if several Ukrainian forms, keep the most frequent, list others
    by_en = defaultdict(list)
    for w in ident:
        by_en[w['en'].lower()].append(w)
    merged = []
    for en, ws in by_en.items():
        ws.sort(key=lambda w: (-w['checked'], -wordfreq.zipf_frequency(w['uk'], 'uk')))
        w = dict(ws[0])
        alts = [x['uk'] for x in ws[1:] if x['uk'].lower() != w['uk'].lower()]
        if alts:
            w['uk_alt'] = sorted(set(alts))
        w['labels'] = sorted(set().union(*[set(x['labels']) for x in ws]))
        merged.append(w)
    # spelling variants of the same Ukrainian word (centre/center): keep the American/international one
    by_uk = defaultdict(list)
    for w in merged:
        by_uk[w['uk'].lower()].append(w)
    final = []
    for uk, ws in by_uk.items():
        if len(ws) == 1:
            final += ws
            continue
        keep = []
        for w in sorted(ws, key=lambda w: -wordfreq.zipf_frequency(w['en'].lower(), 'en')):
            k = re.sub(r'(our)', 'or', re.sub(r're$', 'er', re.sub(r'ise$', 'ize', w['en'].lower())))
            if any(re.sub(r'(our)', 'or', re.sub(r're$', 'er', re.sub(r'ise$', 'ize', x['en'].lower()))) == k for x in keep):
                continue
            keep.append(w)
        final += keep

    for w in final:
        e = w['en'].lower()
        z = wordfreq.zipf_frequency(e, 'en')
        w['zipf'] = round(z, 2)
        w['list_level'] = None if w['en'].isupper() else list_level(e, w['pos'], starters, cefr)
        lv = w.pop('lvl', None)
        w['level'] = lv if lv in LEVELS else (w['list_level'] or 'C2')
        if not w['list_level'] and z < 3.0:
            w['labels'] = sorted(set(w['labels']) | {'rare'})
        # international: same spelling exists in most major European languages
        base = strip_accents(e)
        hits = sum(1 for lang in OTHER_LANGS
                   if wordfreq.zipf_frequency(e, lang) >= 2.0 or (base != e and wordfreq.zipf_frequency(base, lang) >= 2.0))
        labs = set(w['labels'])
        if len(e) >= 3 and ' ' not in e and (hits >= 5 or ('international' in labs and hits >= 3)):
            labs.add('international')
        else:
            labs.discard('international')
        w['labels'] = sorted(labs)
        w['langs'] = hits

    for w in final:
        w['labels'] = norm_labels(w['labels'])
    # within a level: standard words first, then slang/archaic/rare-in-Ukrainian ones; then most common first
    def odd(w):
        return bool(set(w['labels']) & NONSTANDARD) or ('rare' in w['labels'] and w['level'] != 'C2')
    final.sort(key=lambda w: (LEVELS.index(w['level']) if w['level'] in LEVELS else 9, odd(w), -w['zipf'], w['en'].lower()))
    json.dump(final, open(f'{D}/words.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for name, v in (('similar', 'similar'), ('false_friends', 'false_friend'), ('partial_false_friends', 'partial_false_friend')):
        rows = sorted(buckets[v].values(), key=lambda w: w['en'].lower())
        json.dump(rows, open(f'{D}/{name}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # website data: usage labels as tags, topic labels as categories.
    # Checker notes are drafts that often describe the Ukrainian word, so they are NOT shown on the site;
    # card notes will be written later and must talk only about the English word.
    site = []
    for w in final:
        tags = [l for l in w['labels'] if l in USAGE]
        topics = [l for l in w['labels'] if l not in USAGE]
        rec = {'en': w['en'], 'uk': w['uk'], 'level': w['level']}
        if w['pos']:
            rec['pos'] = w['pos']
        if tags:
            rec['tags'] = tags
        if topics:
            rec['topics'] = topics
        if w['british']:
            rec['british'] = True
        if w.get('en_note'):
            rec['note'] = w['en_note']
        site.append(rec)
    with open(os.path.join(REPO, 'words.js'), 'w', encoding='utf-8') as f:
        f.write('// Generated by tools/build_site.py from data/words.json — do not edit by hand.\n')
        f.write('window.WORDS = [\n' + ',\n'.join(json.dumps(r, ensure_ascii=False) for r in site) + '\n];\n')

    frag = open(os.path.join(REPO, 'site', 'app.html'), encoding='utf-8').read()
    i = frag.index('<div class="wrap">')
    html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + frag[:i].strip() + '\n</head>\n<body>\n' + frag[i:].strip() + '\n</body>\n</html>\n')
    open(os.path.join(REPO, 'index.html'), 'w', encoding='utf-8').write(html)

    counts = defaultdict(int)
    for w in final:
        counts[w['level']] += 1
    print('identical', len(final), dict(sorted(counts.items())), '| similar', len(buckets['similar']),
          '| false friends', len(buckets['false_friend']), '| partial', len(buckets['partial_false_friend']))


if __name__ == '__main__':
    main()
