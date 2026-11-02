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
# frequency bands shown on the site: rank among the most used English words (data/levels/en-rank.tsv)
BANDS = [(1000, 'top-1000'), (2000, 'top-2000'), (3000, 'top-3000'),
         (5000, 'top-5000'), (10000, 'top-10k'), (20000, 'top-20k'), (50000, 'top-50k'), (100000, 'top-100k')]
BAND_KEYS = [k for _, k in BANDS] + ['rare']


def load_ranks():
    import bisect
    rank, neg = {}, []
    for line in open(f'{D}/levels/en-rank.tsv', encoding='utf-8'):
        if line.startswith('#'):
            continue
        w, f = line.rstrip('\n').split('\t')
        rank[w] = len(neg) + 1
        neg.append(-float(f))

    def rank_of(word):
        """(rank, estimated?) — words outside the list (phrases, rare words) are placed by their own frequency"""
        e = word.lower()
        if e in rank:
            return rank[e], False
        f = wordfreq.word_frequency(e, 'en', wordlist='large')
        if f <= 0:
            return None, True
        return bisect.bisect_left(neg, -f) + 1, True

    def rank_from_freq(f):
        return bisect.bisect_left(neg, -f) + 1 if f > 0 else None

    def freq_of(word):
        e = word.lower()
        return -neg[rank[e] - 1] if e in rank else wordfreq.word_frequency(e, 'en', wordlist='large')
    return rank_of, rank_from_freq, freq_of


def load_sense():
    """Linguists' estimates (tools/workflows/sense-share.js): {"word": {"s": % of uses in the card's meaning}}
    or {"phrase": {"pm": occurrences per million words}}."""
    out = {}
    for f in sorted(glob.glob(f'{D}/sense/*.json')):
        try:
            for k, v in json.load(open(f, encoding='utf-8')).items():
                if isinstance(v, dict) and ('s' in v or 'pm' in v):
                    out[k] = v
        except Exception as e:
            print('skip broken', f, e, file=sys.stderr)
    return out


COLLIDE = {'it', 'us', 'am', 'id', 'as', 'or', 'so', 'an', 'at', 'be', 'do', 'go', 'he', 'me', 'my', 'no', 'of', 'on',
           'to', 'up', 'we', 'is', 'in', 'if', 'by', 'hi', 'oh', 'ad', 'pa', 'ma', 'dr', 'mr'}
FLOOR_SLACK = {'A0': 1, 'A1': 1, 'A2': 401, 'B1': 1001, 'B2': 2001, 'C1': 3001, 'C2': 5001}
FLOOR_STRICT = {'A0': 1, 'A1': 1, 'A2': 1001, 'B1': 2001, 'B2': 3001, 'C1': 5001, 'C2': 10001}


def band_of(r):
    if r is None:
        return 'rare'
    for edge, key in BANDS:
        if r <= edge:
            return key
    return 'rare'
OTHER_LANGS = ['de', 'fr', 'es', 'it', 'pt', 'nl', 'sv', 'pl', 'cs']
USAGE = {'archaic', 'obsolete', 'dated', 'literary', 'informal', 'slang', 'abbreviation', 'technical', 'rare', 'international'}


def clean_uk(s):
    s = unicodedata.normalize('NFC', (s or '').strip()).replace('’', "'").replace('ʼ', "'")
    # drop stress marks, then recompose: й and ї must stay single letters (NFC), not и/і + a combining mark
    return unicodedata.normalize('NFC', ''.join(ch for ch in unicodedata.normalize('NFD', s) if ch != '́')).strip()


def clean_en(s):
    return re.sub(r'\s+', ' ', (s or '').strip())


def strip_accents(s):
    return ''.join(ch for ch in unicodedata.normalize('NFD', s) if unicodedata.category(ch) != 'Mn')


# Ukrainian form to show when a word has several identical Ukrainian forms and the most frequent one is ambiguous
# (гей is mostly "gay" in Ukrainian, so hey = хей).
UK_PREFER = {'hey': 'хей'}


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
    rank_of, rank_from_freq, freq_of = load_ranks()
    sense = load_sense()
    pfp = f'{D}/levels/phrase-freq.json'
    phrase_freq = json.load(open(pfp, encoding='utf-8'))['phrases'] if os.path.exists(pfp) else {}
    qa = {}   # final expert pass (tools/workflows/card-qa.js): verdict, share, labels, grammar, examples, note
    for f in sorted(glob.glob(f'{D}/qa/*.json')):
        try:
            for k, v in json.load(open(f, encoding='utf-8')).items():
                if isinstance(v, dict):
                    qa[k] = {**qa.get(k, {}), **v}   # later files (e.g. zz-*.json review fixes) refine earlier ones
        except Exception as e:
            print('skip broken', f, e, file=sys.stderr)
    for k, v in qa.items():          # the QA's share estimate (with the card's meaning in view) wins
        if 'pm' in v:
            sense[k] = {'pm': v['pm']}
        elif 's' in v:
            sense[k] = {'s': v['s']}
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
        ws.sort(key=lambda w: (UK_PREFER.get(en) != w['uk'].lower(), -w['checked'], -wordfreq.zipf_frequency(w['uk'], 'uk')))
        w = dict(ws[0])
        alts = [x['uk'] for x in ws[1:] if x['uk'].lower() != w['uk'].lower()]
        if alts:
            w['uk_alt'] = sorted(set(alts))
        w['labels'] = sorted(set().union(*[set(x['labels']) for x in ws]))
        merged.append(w)
    # clean-up (reviewers' findings): no prefixes, no English words without English evidence,
    # no Latin-script Ukrainian sides (use the Cyrillic reading when there is one), one card per spelling group
    evp = f'{D}/levels/en-evidence.json'
    ev = json.load(open(evp, encoding='utf-8')) if os.path.exists(evp) else {'missing': [], 'variants': {}}
    missing, variants = set(ev['missing']), ev['variants']
    latin = re.compile(r'[A-Za-z]')
    excluded, cleaned = [], []
    for w in merged:
        e = w['en']
        if e.startswith('-') or e.endswith('-'):
            excluded.append({'en': e, 'uk': w['uk'], 'why': 'prefix, not a word'})
            continue
        if e.lower() in missing:
            excluded.append({'en': e, 'uk': w['uk'], 'why': 'no English dictionary or corpus evidence'})
            continue
        if latin.search(w['uk']):
            cyr = [a for a in w.get('uk_alt', []) if not latin.search(a)]
            if not cyr:
                excluded.append({'en': e, 'uk': w['uk'], 'why': 'Ukrainian side written in Latin letters'})
                continue
            w['uk_alt'] = [a for a in w.get('uk_alt', []) if a != cyr[0]] + [w['uk']]
            w['uk'] = cyr[0]
        cleaned.append(w)

    def dkey(e):
        e = e.lower()
        e = variants.get(e, e)
        e = re.sub(r"[\s\-'.]", '', strip_accents(e))
        return re.sub(r'ise$', 'ize', re.sub(r're$', 'er', e.replace('our', 'or')))
    groups = defaultdict(list)
    for w in cleaned:
        groups[dkey(w['en'])].append(w)
    final = []
    for ws in groups.values():
        if len(ws) == 1:
            final += ws
            continue
        def score(w):   # American/international spelling first, then the most used form
            e = w['en'].lower()
            brit = bool(re.search(r'our|re$|ise$|ae|oe|ll[eio]', e)) and not w['british']
            return (w['checked'], wordfreq.zipf_frequency(e, 'en') - (0.6 if brit else 0) - (0.3 if e != strip_accents(e) else 0))
        ws.sort(key=score, reverse=True)
        keep = dict(ws[0])
        keep['also'] = sorted({x['en'] for x in ws[1:]})
        keep['labels'] = sorted(set().union(*[set(x['labels']) for x in ws]))
        alts = set(keep.get('uk_alt', [])) | {x['uk'] for x in ws[1:] if x['uk'].lower() != keep['uk'].lower()}
        if alts:
            keep['uk_alt'] = sorted(alts)
        final.append(keep)
    kept = []
    for w in final:
        v = (qa.get(w['en']) or {}).get('v', 'keep')
        if v != 'keep':
            excluded.append({'en': w['en'], 'uk': w['uk'], 'why': 'final expert pass: ' + v})
        else:
            kept.append(w)
    final = kept
    json.dump(excluded, open(f'{D}/excluded.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

    for w in final:
        e = w['en'].lower()
        z = wordfreq.zipf_frequency(e, 'en')
        w['zipf'] = round(z, 2)
        w['list_level'] = None if w['en'].isupper() else list_level(e, w['pos'], starters, cefr)
        lv = w.pop('lvl', None)
        w['level'] = lv if lv in LEVELS else (w['list_level'] or 'C2')
        w['rank'], w['rank_est'] = rank_of(w['en'])
        if w['en'].isupper() and len(w['en']) > 1:
            w['rank_est'] = True   # abbreviations collide with lowercase words (IT vs it)
        if w['rank'] is None or w['rank'] > 50000:
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
        # A word form's frequency counts all its meanings (take = тейк is not a top-100 word, "are" the unit
        # is not the verb). The second check set a level for the SHARED meaning, so the rank may not be more
        # common than that level allows. Phrases, abbreviations and big gaps get the stricter floor.
        raw = w['rank']
        w['rank_raw'] = raw
        sh = sense.get(w['en'])
        if sh and 'pm' in sh:
            # phrase: its own frequency. Two sources, like words: the linguists' estimate (per million words)
            # and the Google Books Ngram count put on the word-list scale (tools/phrase_freq.py); geometric mean.
            # A phrase Google Books does not have counts as rare there (a quarter of the estimate).
            f = max(0.0, float(sh['pm'])) / 1e6
            pf = phrase_freq.get(w['en'])
            if pf is not None:
                w['books_pm'] = round(pf['freq'] * 1e6, 3)
                f = (f * pf['freq']) ** 0.5 if pf['freq'] > 0 else f * 0.25
            w['rank'] = rank_from_freq(f)
            w['rank_est'] = True
        elif sh and 's' in sh:
            # frequency of the word in the meaning on the card = word frequency x share of that meaning
            share = max(0.0, min(100.0, float(sh['s'])))
            w['share'] = share
            w['rank'] = rank_from_freq(freq_of(w['en']) * share / 100)
            w['rank_est'] = w['rank_est'] or share < 90
            if w['en'].isupper() and w['en'].lower() in COLLIDE and w['rank'] and w['rank'] < 2001:
                w['rank'] = 2001   # IT/US/ID: the share of a function word ("it") is too uncertain to rank higher
        elif raw:
            lv = w['level']
            strict = w['rank_est'] or raw * 5 < FLOOR_SLACK.get(lv, 1)
            floor = (FLOOR_STRICT if strict else FLOOR_SLACK).get(lv, 1)
            if raw < floor:
                w['rank'] = floor
                w['rank_est'] = True
        w['band'] = band_of(w['rank'])
    # within a level: standard words first, then slang/archaic/rare-in-Ukrainian ones; then most common first
    def odd(w):
        return bool(set(w['labels']) & NONSTANDARD) or ('rare' in w['labels'] and w['level'] != 'C2')
    # sorted by how often the English word is used (most used first)
    final.sort(key=lambda w: (w['rank'] is None, w['rank'] or 0, w['rank_raw'] or 0, -w['zipf'], w['en'].lower()))
    json.dump(final, open(f'{D}/words.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for name, v in (('similar', 'similar'), ('false_friends', 'false_friend'), ('partial_false_friends', 'partial_false_friend')):
        rows = sorted(buckets[v].values(), key=lambda w: w['en'].lower())
        json.dump(rows, open(f'{D}/{name}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # website data: usage labels as tags, topic labels as categories.
    # Checker notes are drafts that often describe the Ukrainian word, so they are NOT shown on the site;
    # card notes will be written later and must talk only about the English word.
    # labels shown on cards describe the ENGLISH word only (from English Wiktionary, tools/compute_register.py);
    # "ns" marks pairs whose Ukrainian word is slang/colloquial/rare/archaic, used only by the site filter
    reg = json.load(open(f'{D}/levels/register.json', encoding='utf-8')) if os.path.exists(f'{D}/levels/register.json') else {}
    examples = {}
    # data/examples2 (level-graded by frequency band) overrides the first examples in data/examples
    for f in sorted(glob.glob(f'{D}/examples/*.json')) + sorted(glob.glob(f'{D}/examples2/*.json')):
        try:
            examples.update(json.load(open(f, encoding='utf-8')))
        except Exception as e:
            print('skip broken', f, e, file=sys.stderr)
    am_path = os.path.join(REPO, 'audio', 'manifest.json')
    audio = json.load(open(am_path, encoding='utf-8')) if os.path.exists(am_path) else {'chunks': [], 'words': {}}
    def ekey(e):   # match example keys regardless of accents, hyphens, spaces and case (déjà vu / deja vu)
        return re.sub(r"[\s\-'.]", '', strip_accents(e.lower()))
    ex_norm = {ekey(k): v for k, v in examples.items()}
    stp = f'{D}/levels/stress.json'
    stress = json.load(open(stp, encoding='utf-8')) if os.path.exists(stp) else {}
    # pictures for the back of the card: images/<slug>.(webp|jpg|jpeg|png|svg), slug = English word in lowercase,
    # accents removed, spaces -> "-" (images/taxi.webp, images/hot-dog.jpg, images/deja-vu.png)
    pics = {}
    ppath = f'{D}/levels/pictures.json'      # Noto Emoji pictures chosen per card (tools/make_pictures.py)
    emoji_pics = json.load(open(ppath, encoding='utf-8')) if os.path.exists(ppath) else {}
    if os.path.isdir(os.path.join(REPO, 'images')):
        for fn in sorted(os.listdir(os.path.join(REPO, 'images'))):
            stem, ext = os.path.splitext(fn)
            if ext.lower() in ('.webp', '.jpg', '.jpeg', '.png', '.svg', '.avif'):
                pics.setdefault(stem.lower(), 'images/' + fn)
    site = []
    details = defaultdict(dict)
    for w in final:
        r = reg.get(w['en'], {})
        q = qa.get(w['en'], {})
        tags = sorted(set(r.get('en', [])) | set(q.get('reg', [])))
        tags += [l for l in ('abbreviation', 'technical') if l in w['labels'] and l not in tags]
        if isinstance(q.get('tags'), list):
            tags = q['tags']          # a manual or review override replaces the computed English labels
        topics = [l for l in w['labels'] if l not in USAGE]
        ex = examples.get(w['en']) or ex_norm.get(ekey(w['en'])) or {}
        if q.get('ex'):
            ex = {'ex': q['ex'], 'note': q.get('note', ex.get('note', ''))}
        elif 'note' in q:
            ex = dict(ex, note=q['note'])
        if ex.get('ex'):
            w['examples'] = [e for e in ex['ex'] if isinstance(e, str)][:4]
        if ex.get('note'):
            w['en_note'] = ex['note']
        rec = {'en': w['en'], 'uk': w['uk'], 'band': w['band']}
        if w['rank']:
            rec['rank'] = w['rank']
            if w['rank_est']:
                rec['approx'] = True
        if w['pos']:
            rec['pos'] = w['pos']
        if topics:
            rec['topics'] = topics
        if w['british']:
            rec['british'] = True
        # details (shown on the back) go to details-<band>.js, loaded by the page when needed
        det = {}
        if w.get('examples'):
            det['ex'] = w['examples']
        if w.get('en_note'):
            det['note'] = w['en_note']
        if tags:
            det['tags'] = tags
        if q.get('gram'):
            det['gram'] = q['gram']
        if q.get('say'):
            det['say'] = q['say']
        details[w['band']][rec['en'] + '|' + rec['uk']] = det
        if 'ns' in q:
            ns = bool(q['ns'])          # the expert pass decides when it has looked at the pair
        else:
            ns = bool(r.get('uk_nonstd'))
        if ns:
            rec['ns'] = 1
        en_reg = set(r.get('en', [])) | set(q.get('reg', []))
        if en_reg & {'vulgar', 'offensive', 'derogatory'}:
            rec['rude'] = 1
        if w['en'] in stress:
            rec['st'] = stress[w['en']]
        if w['en'] in audio['words']:
            rec['au'] = audio['words'][w['en']]
        slug = re.sub(r'[^a-z0-9]+', '-', strip_accents(w['en'].lower())).strip('-')
        if slug in pics:
            rec['img'] = pics[slug]
        elif w['en'] in emoji_pics:
            det['svg'] = emoji_pics[w['en']]
        site.append(rec)
    with open(os.path.join(REPO, 'words.js'), 'w', encoding='utf-8') as f:
        f.write('// Generated by tools/build_site.py from data/words.json — do not edit by hand.\n')
        f.write('window.AUDIO = ' + json.dumps({'chunks': audio['chunks']}) + ';\n')
        f.write('window.WORDS = [\n' + ',\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in site) + '\n];\n')
    for old in glob.glob(os.path.join(REPO, 'details-*.js')):
        os.remove(old)
    for band, det in details.items():
        with open(os.path.join(REPO, f'details-{band}.js'), 'w', encoding='utf-8') as f:
            f.write('// Generated by tools/build_site.py — examples, notes, grammar for one frequency band.\n')
            f.write('Object.assign(window.DETAILS = window.DETAILS || {}, ' + json.dumps(det, ensure_ascii=False, separators=(',', ':')) + ');\n')

    # Stories tab: chapters of words in story order (tools/build_stories.py -> data/stories/stories.json)
    sp = f'{D}/stories/stories.json'
    if os.path.exists(sp):
        st = json.load(open(sp, encoding='utf-8'))
        on_site = {r['en'] for r in site}
        chs = []
        for c in st['chapters']:
            ws = [w for w in c['words'] if w in on_site]
            if ws:
                chs.append({'id': c['id'], 'part': c['part'], 'title': c['title'], 'level': c.get('level', ''),
                            'words': ws, 'story': c.get('story', '')})
        with open(os.path.join(REPO, 'stories.js'), 'w', encoding='utf-8') as f:
            f.write('// Generated by tools/build_site.py from data/stories/stories.json — chapters for the Stories tab.\n')
            f.write('window.STORIES = ' + json.dumps({'parts': st['parts'], 'chapters': chs}, ensure_ascii=False,
                                                     separators=(',', ':')) + ';\n')
        print('stories:', len(chs), 'chapters,', sum(len(c['words']) for c in chs), 'words')

    frag = open(os.path.join(REPO, 'site', 'app.html'), encoding='utf-8').read()
    i = frag.index('<div class="wrap">')
    html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + frag[:i].strip() + '\n</head>\n<body>\n' + frag[i:].strip() + '\n</body>\n</html>\n')
    open(os.path.join(REPO, 'index.html'), 'w', encoding='utf-8').write(html)

    counts = defaultdict(int)
    for w in final:
        counts[w['band']] += 1
    counts = {k: counts[k] for k in BAND_KEYS}
    print('identical', len(final), dict(sorted(counts.items())), '| similar', len(buckets['similar']),
          '| false friends', len(buckets['false_friend']), '| partial', len(buckets['partial_false_friend']))


if __name__ == '__main__':
    main()
