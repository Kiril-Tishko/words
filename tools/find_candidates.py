#!/usr/bin/env python3
"""Find every English word whose Ukrainian equivalent is (almost) the same word.

Method (no word comes from memory):
  1. Build a big English lexicon (words_alpha, wordfreq, CMUdict, hunspell en_US/en_GB, CEFR lists).
  2. Build a big Ukrainian lexicon (VESUM/dict_uk lemmas, hunspell uk_UA, Wiktionary, wordfreq).
  3. Render every English word into Ukrainian letters in all plausible ways:
       - by spelling  (taxi -> таксі, hotel -> готель, hockey -> хокей)
       - by sound     (CMUdict: computer -> комп'ютер, show -> шоу, manager -> менеджер)
       - by letter names for abbreviations (DJ -> діджей, PR -> піар)
     Renderings are compared with Ukrainian words after a normalisation that ignores
     soft sign / apostrophe / double letters / и~і~й / г~ґ~х.
  4. Ukrainian compounds (хот-дог, фастфуд) are split and each part matched.
Output: one JSON line per (English, Ukrainian) candidate pair with all evidence.
Every candidate is later checked by hand (agents) for meaning and form.
"""
import csv, json, os, re, sys
from collections import defaultdict
from multiprocessing import Pool

import wordfreq

SRC = os.environ.get('SRC', '/home/user/sources')
DICT_UK = os.environ.get('DICT_UK', '/home/user/brown-uk/dict_uk/data/dict')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SRC, 'candidates.jsonl')
MAXC = 3  # max total "unusualness" cost of a rendering

# ---------------------------------------------------------------- normalisation
NMAP = {'а': 'а', 'б': 'б', 'в': 'в', 'г': 'г', 'ґ': 'г', 'д': 'д', 'е': 'е', 'є': 'іе', 'ж': 'ж', 'з': 'з',
        'и': 'і', 'і': 'і', 'ї': 'іі', 'й': 'і', 'к': 'к', 'л': 'л', 'м': 'м', 'н': 'н', 'о': 'о', 'п': 'п',
        'р': 'р', 'с': 'с', 'т': 'т', 'у': 'у', 'ф': 'ф', 'х': 'г', 'ц': 'ц', 'ч': 'ч', 'ш': 'ш', 'щ': 'шч',
        'ь': '', 'ю': 'іу', 'я': 'іа', "'": '', '’': '', 'ʼ': '', '-': '', ' ': '', 'ё': 'іо', 'ы': 'і',
        'э': 'е', 'ъ': '', '́': ''}


def norm_chunk(s):
    return ''.join(NMAP.get(ch, '\x00') for ch in s)


def append(p, c):
    """append normalised chunk c to normalised partial p, collapsing double letters"""
    for ch in c:
        if p and p[-1] == ch:
            continue
        p += ch
    return p


def norm(w):
    s = norm_chunk(w.lower())
    if '\x00' in s:
        return None
    return append('', s)


# ---------------------------------------------------------------- spelling rules
VOW = set('aeiouy')


def spelling_alts(w, i):
    n = len(w)
    rest = w[i:]
    nxt = w[i + 1] if i + 1 < n else ''
    start = i == 0
    res = []

    def add(key, opts, cond=True):
        if cond and rest.startswith(key):
            res.append((len(key), opts))

    add('tch', [('ч', 0), ('тч', 0)])
    add('sch', [('ш', 0), ('ск', 1), ('сх', 1)])
    add('tion', [('ціон', 1), ('шн', 1), ('шен', 1)])
    add('ssion', [('шн', 1), ('сіон', 1)])
    add('sion', [('зіон', 1), ('сіон', 1), ('шн', 1), ('жн', 1)])
    add('ture', [('чер', 1)])
    add('ough', [('оу', 1), ('аф', 1), ('о', 1), ('у', 1), ('оф', 1)])
    add('augh', [('аф', 1), ('о', 1)])
    add('eigh', [('ей', 0)])
    add('igh', [('ай', 0)])
    add('eau', [('о', 0)])
    add('ph', [('ф', 0)])
    add('th', [('т', 0), ('с', 1), ('з', 1), ('д', 2)])
    add('sh', [('ш', 0)])
    add('ch', [('ч', 0), ('х', 0), ('к', 1), ('ш', 1)])
    add('ck', [('к', 0)])
    add('qu', [('кв', 0), ('к', 0)])
    add('gh', [('г', 1), ('', 1), ('ф', 1)])
    add('kn', [('н', 0)], start)
    add('wr', [('р', 0)], start)
    add('ps', [('с', 1)], start)
    add('pn', [('н', 1)], start)
    add('gn', [('н', 1)], start)
    add('wh', [('в', 0), ('у', 1), ('г', 1)])
    add('rh', [('р', 0)])
    add('oo', [('у', 0), ('о', 1)])
    add('ee', [('і', 0)])
    add('ea', [('і', 0), ('е', 0), ('еа', 1), ('іа', 1)])
    add('ai', [('ей', 0), ('ай', 0), ('е', 1), ('аі', 1)])
    add('ay', [('ей', 0), ('ай', 0), ('аі', 1)])
    add('ey', [('ей', 0), ('і', 0), ('еі', 1)])
    add('ei', [('ей', 0), ('і', 1), ('ай', 1), ('еі', 1)])
    add('oa', [('оу', 0), ('о', 0), ('оа', 1)])
    add('ou', [('ау', 0), ('у', 0), ('оу', 0), ('о', 1), ('а', 1)])
    add('ow', [('оу', 0), ('ау', 0), ('ов', 0), ('о', 1)])
    add('oi', [('ой', 0), ('оі', 0), ('уа', 2)])
    add('oy', [('ой', 0)])
    add('au', [('о', 0), ('ау', 0), ('ав', 1)])
    add('aw', [('о', 0), ('ав', 1), ('оу', 1)])
    add('ie', [('і', 0), ('ай', 1), ('іе', 1)])
    add('eu', [('ев', 0), ('ю', 1), ('еу', 1), ('йо', 2)])
    add('ew', [('ю', 0), ('ев', 1)])
    add('ui', [('уі', 0), ('у', 0), ('ві', 1)])
    add('ue', [('у', 0), ('ю', 0), ('уе', 1)])
    add('ae', [('е', 0)])
    add('oe', [('о', 1), ('е', 1), ('ое', 1)])
    add('ng', [('нг', 0), ('н', 0)])

    c = w[i]
    if c == 'a':
        o = [('а', 0), ('е', 0), ('ей', 0), ('о', 1), ('', 2)]
    elif c == 'e':
        o = [('е', 0), ('і', 0), ('', 0 if i == n - 1 else 1)]
    elif c == 'i':
        o = [('і', 0), ('ай', 0), ('', 2)]
    elif c == 'o':
        o = [('о', 0), ('а', 1), ('оу', 0), ('у', 1)]
    elif c == 'u':
        o = [('у', 0), ('а', 0), ('ю', 0), ('е', 1), ('', 2)]
    elif c == 'y':
        o = [('й', 0)] if (start and nxt in VOW) else [('і', 0), ('ай', 0), ('й', 0)]
    elif c == 'c':
        o = [('ц', 0), ('с', 0), ('ч', 2)] if nxt in ('e', 'i', 'y') else [('к', 0)]
    elif c == 'g':
        o = [('г', 0), ('дж', 0), ('ж', 1)] if nxt in ('e', 'i', 'y') else [('г', 0)]
    elif c == 's':
        o = [('с', 0), ('з', 0), ('ш', 2), ('ж', 2)]
    elif c == 'z':
        o = [('з', 0), ('ц', 1)]
    elif c == 'h':
        o = [('г', 0), ('х', 0), ('', 1)]
    elif c == 'j':
        o = [('дж', 0), ('ж', 1), ('й', 1), ('х', 2)]
    elif c == 'w':
        o = [('в', 0), ('у', 0)]
    elif c == 'x':
        o = [('кс', 0), ('гз', 1), ('з', 1)]
    elif c == 'r':
        o = [('р', 0), ('', 2)]
    else:
        o = SINGLE.get(c)
    if o:
        res.append((1, o))
    return res


SINGLE = {'b': [('б', 0)], 'd': [('д', 0)], 'f': [('ф', 0)], 'k': [('к', 0)], 'l': [('л', 0)], 'm': [('м', 0)],
          'n': [('н', 0)], 'p': [('п', 0)], 't': [('т', 0)], 'v': [('в', 0)], 'q': [('к', 0)],
          'é': [('е', 0)], 'è': [('е', 0)], 'ê': [('е', 0)], 'ë': [('е', 0)], 'á': [('а', 0)], 'à': [('а', 0)],
          'â': [('а', 0)], 'ä': [('е', 0), ('а', 0)], 'ö': [('е', 0), ('о', 0)], 'ü': [('ю', 0), ('у', 0)],
          'ñ': [('нь', 0)], 'ç': [('с', 0)], 'í': [('і', 0)], 'ó': [('о', 0)], 'ú': [('у', 0)], 'ô': [('о', 0)],
          'î': [('і', 0)], 'ï': [('і', 0)], 'û': [('у', 0)], 'ø': [('е', 0), ('о', 0)], 'å': [('о', 0)],
          "'": [('', 0)], '-': [('', 0)], ' ': [('', 0)], '.': [('', 0)]}

# ---------------------------------------------------------------- pronunciation rules (CMUdict / ARPAbet)
PH = {'AA': [('а', 0), ('о', 0)], 'AE': [('е', 0), ('а', 0)], 'AO': [('о', 0), ('а', 1)], 'AW': [('ау', 0)],
      'AY': [('ай', 0)], 'EH': [('е', 0)], 'EY': [('ей', 0), ('е', 0)], 'IH': [('і', 0), ('е', 1)],
      'IY': [('і', 0)], 'OW': [('оу', 0), ('о', 0)], 'OY': [('ой', 0)], 'UH': [('у', 0)],
      'UW': [('у', 0), ('ю', 0)], 'B': [('б', 0)], 'CH': [('ч', 0)], 'D': [('д', 0)],
      'DH': [('д', 0), ('з', 1), ('т', 1)], 'F': [('ф', 0)], 'G': [('г', 0)], 'HH': [('г', 0)],
      'JH': [('дж', 0)], 'K': [('к', 0)], 'L': [('л', 0)], 'M': [('м', 0)], 'N': [('н', 0)],
      'NG': [('нг', 0), ('н', 0)], 'P': [('п', 0)], 'R': [('р', 0)], 'S': [('с', 0)], 'SH': [('ш', 0)],
      'T': [('т', 0)], 'TH': [('т', 0), ('с', 0)], 'V': [('в', 0)], 'W': [('в', 0), ('у', 0)], 'Y': [('й', 0)],
      'Z': [('з', 0)], 'ZH': [('ж', 0)]}
PH_UNSTRESSED = {'AH': [('е', 0), ('а', 0), ('о', 0), ('', 0), ('у', 1), ('і', 1)],
                 'ER': [('ер', 0), ('ар', 0), ('ор', 0), ('р', 0), ('ур', 1)],
                 'IH': [('і', 0), ('е', 0), ('а', 1), ('о', 1)]}
PH_STRESSED = {'AH': [('а', 0), ('о', 1), ('е', 1), ('у', 1)], 'ER': [('ер', 0), ('ор', 1), ('ар', 1), ('ур', 1)]}


def phone_alts(ph):
    base = ph.rstrip('012')
    stress = ph[-1] if ph[-1] in '012' else ''
    if stress == '0' and base in PH_UNSTRESSED:
        return PH_UNSTRESSED[base]
    if base in PH_STRESSED:
        return PH_STRESSED[base]
    return PH.get(base, [])


LETTER = {'a': ['ей'], 'b': ['бі'], 'c': ['сі'], 'd': ['ді'], 'e': ['і'], 'f': ['еф'], 'g': ['джі'],
          'h': ['ейч', 'еш'], 'i': ['ай'], 'j': ['джей'], 'k': ['кей'], 'l': ['ел'], 'm': ['ем'], 'n': ['ен'],
          'o': ['оу', 'о'], 'p': ['пі'], 'q': ['кью'], 'r': ['ар'], 's': ['ес'], 't': ['ті'], 'u': ['ю'],
          'v': ['ві'], 'w': ['дабл-ю', 'дабл'], 'x': ['екс'], 'y': ['вай'], 'z': ['зет', 'зі']}

# ---------------------------------------------------------------- globals filled before fork
PREFIX = set()
TARGET = {}


def search(seq, alts_fn, base_cost=0):
    """DFS over seq producing normalised renderings that exist in TARGET. returns {norm: (cost, h_used)}"""
    found = {}
    n = len(seq)
    stack = [(0, '', base_cost, False)]
    seen = set()
    while stack:
        i, p, cost, hflag = stack.pop()
        key = (i, p, hflag)
        if key in seen:
            continue
        seen.add(key)
        if i == n:
            if p in TARGET:
                old = found.get(p)
                if old is None or cost < old[0]:
                    found[p] = (cost, hflag)
            continue
        for L, opts in alts_fn(seq, i):
            for out, c in opts:
                nc = cost + c
                if nc > MAXC:
                    continue
                q = append(p, norm_chunk(out))
                if q and q not in PREFIX:
                    continue
                hf = hflag or (L == 1 and isinstance(seq, str) and seq[i] == 'h' and out != '')
                stack.append((i + L, q, nc, hf))
    return found


def letters_alts(w, i):
    return [(1, [(x, 0) for x in LETTER.get(w[i], [])])]


def pron_alts(phs, i):
    return [(1, phone_alts(phs[i]))]


def render_word(args):
    w, prons = args
    out = []
    lw = w.lower()
    if all(ch.isalpha() or ch in "'- ." for ch in lw):
        for nf, (c, hf) in search(lw, spelling_alts).items():
            out.append((nf, 'spelling', c, hf))
        if 2 <= len(lw) <= 5 and lw.isalpha():
            for nf, (c, hf) in search(lw, letters_alts, 1).items():
                out.append((nf, 'letters', c, False))
    for pr in prons:
        phs = pr.split()
        for nf, (c, hf) in search(phs, pron_alts).items():
            out.append((nf, 'sound', c, 'HH' in pr))
    return w, out


# ---------------------------------------------------------------- lexicons
def load_english():
    en = defaultdict(set)  # word -> sources
    for line in open(f'{SRC}/words_alpha.txt', encoding='utf-8'):
        w = line.strip()
        if w:
            en[w].add('alpha')
    for w in wordfreq.get_frequency_dict('en', 'large'):
        if re.fullmatch(r"[a-zà-ÿ][a-zà-ÿ'\-]*", w):
            en[w].add('freq')
    for line in open(f'{SRC}/en_50k.txt', encoding='utf-8'):
        w = line.split()[0]
        if w.isalpha():
            en[w].add('subs')
    prons = defaultdict(list)
    for line in open(f'{SRC}/cmudict.dict', encoding='utf-8'):
        line = line.split('#')[0].strip()
        if not line:
            continue
        w, pr = line.split(' ', 1)
        w = re.sub(r'\(\d+\)$', '', w)
        prons[w].append(pr)
        en[w].add('cmu')
    for tag, fn in (('us', 'en_US.dic'), ('gb', 'en_GB.dic')):
        for line in open(f'{SRC}/{fn}', encoding='utf-8', errors='ignore'):
            w = line.split('/')[0].strip()
            if not w or w[0].isdigit():
                continue
            if w[0].isupper():
                en[w.lower()].add(tag + '_cap')
            else:
                en[w].add(tag)
    cefr = {}
    for fn, src in (('cefrj-vocabulary-profile-1.5.csv', 'cefrj'), ('octanove-vocabulary-profile-c1c2-1.0.csv', 'octanove')):
        for row in csv.DictReader(open(f'{SRC}/{fn}', encoding='utf-8')):
            for hw in row['headword'].split('/'):
                hw = hw.strip().lower()
                if not hw:
                    continue
                en[hw].add(src)
                lv = row['CEFR'].strip()
                if hw not in cefr or lv < cefr[hw]:
                    cefr[hw] = lv
    return en, prons, cefr


UK_SKIP = {'geo-other.lst', 'geo-ukr-composite.lst', 'geo-ukr-hydro.lst', 'geo-ukr-koatuu.lst', 'names-anim.lst',
           'names-composite.lst', 'names-other.lst', 'invalid.lst', 'invalid-composite.lst', 'invalid-compound.lst',
           'subst.lst', 'pronouns.lst', 'dot-abbr.lst', 'vulgar_obsc.lst', 'twisters.lst'}


def load_ukrainian():
    uk = defaultdict(lambda: {'src': set(), 'tags': set(), 'gloss': [], 'etym_en': False, 'pos': set()})
    for fn in sorted(os.listdir(DICT_UK)):
        if not fn.endswith('.lst') or fn in UK_SKIP:
            continue
        for line in open(f'{DICT_UK}/{fn}', encoding='utf-8'):
            line = line.split('#')[0].strip()
            if not line:
                continue
            parts = line.split()
            w = parts[0]
            if not re.fullmatch(r"[а-яґєіїА-ЯҐЄІЇ'’\-]+", w):
                continue
            rest = ' '.join(parts[1:])
            e = uk[w.lower() if fn != 'base-abbr.lst' else w]
            e['src'].add('vesum:' + fn.replace('.lst', ''))
            for t in re.findall(r':([a-z_0-9]+)', rest):
                if t in ('arch', 'rare', 'slang', 'coll', 'bad', 'alt', 'abbr', 'prop', 'up92', 'xp1', 'xp2', 'nv'):
                    e['tags'].add(t)
            if rest.startswith('/n') or rest.startswith('noun'):
                e['pos'].add('noun')
            elif rest.startswith('/adj') or rest.startswith('adj'):
                e['pos'].add('adj')
            elif rest.startswith('/v') or rest.startswith('verb'):
                e['pos'].add('verb')
            elif rest:
                tok = re.split(r'[:/\s]+', rest.strip())
                tok = [t for t in tok if t]
                if tok:
                    e['pos'].add(tok[0])
    for line in open(f'{SRC}/uk_UA.dic', encoding='utf-8', errors='ignore'):
        w = line.split('/')[0].strip()
        if not w or w.startswith('+') or not re.fullmatch(r"[а-яґєіїА-ЯҐЄІЇ'’\-]+", w):
            continue
        if w[0].isupper():
            continue  # proper nouns
        uk[w]['src'].add('hunspell')
    with open(f'{SRC}/kaikki.org-dictionary-Ukrainian.jsonl', encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            w = d['word']
            if d.get('pos') == 'name' or not re.fullmatch(r"[а-яґєіїА-ЯҐЄІЇ'’\- ]+", w) or w[0].isupper():
                continue
            e = uk[w]
            e['src'].add('wikt')
            e['pos'].add(d.get('pos', ''))
            et = d.get('etymology_text') or ''
            if 'English' in et:
                e['etym_en'] = True
            for s in d.get('senses', [])[:6]:
                for g in s.get('glosses', [])[:1]:
                    if len(e['gloss']) < 6:
                        e['gloss'].append(g[:160])
                for t in s.get('tags', []):
                    if t in ('archaic', 'obsolete', 'dated', 'slang', 'colloquial', 'rare'):
                        e['tags'].add(t)
    fd = wordfreq.get_frequency_dict('uk', 'large')
    for w in fd:
        if re.fullmatch(r"[а-яґєії'’\-]+", w) and w not in uk:
            uk[w]['src'].add('freq')
    return uk


def main():
    global PREFIX, TARGET
    print('loading english...', flush=True)
    en, prons, cefr = load_english()
    print(len(en), 'english words', flush=True)
    print('loading ukrainian...', flush=True)
    uk = load_ukrainian()
    print(len(uk), 'ukrainian words', flush=True)
    target = defaultdict(list)
    for w in uk:
        nf = norm(w)
        if nf and len(nf) >= 2:
            target[nf].append(w)
        # parts of hyphenated compounds are also targets (хот-дог -> хот, дог)
    TARGET = dict(target)
    pref = set()
    for nf in TARGET:
        for k in range(1, len(nf) + 1):
            pref.add(nf[:k])
    PREFIX = pref
    print(len(TARGET), 'targets', len(PREFIX), 'prefixes', flush=True)

    items = [(w, prons.get(w, [])) for w in en]
    pairs = defaultdict(lambda: {'methods': set(), 'cost': 99, 'h': False})
    with Pool(4) as pool:
        for k, (w, out) in enumerate(pool.imap_unordered(render_word, items, chunksize=500)):
            if k % 50000 == 0:
                print(k, flush=True)
            for nf, method, c, hf in out:
                for u in TARGET[nf]:
                    p = pairs[(w, u)]
                    p['methods'].add(method)
                    if c < p['cost']:
                        p['cost'] = c
                    p['h'] = p['h'] or hf
    print(len(pairs), 'raw pairs', flush=True)

    def zen(w):
        return round(wordfreq.zipf_frequency(w, 'en', wordlist='large'), 2)

    def zuk(w):
        return round(wordfreq.zipf_frequency(w, 'uk', wordlist='large'), 2)

    with open(OUT, 'w', encoding='utf-8') as f:
        for (w, u), p in sorted(pairs.items()):
            e = uk[u]
            gl = ' | '.join(e['gloss'])
            gloss_match = bool(re.search(r'(?<![a-z])' + re.escape(w) + r'(?![a-z])', gl.lower())) if gl else False
            rec = {'en': w, 'uk': u, 'methods': sorted(p['methods']), 'cost': p['cost'], 'h_shift': p['h'],
                   'en_src': sorted(en[w]), 'cefr': cefr.get(w), 'zipf_en': zen(w), 'zipf_uk': zuk(u),
                   'uk_src': sorted(e['src']), 'uk_tags': sorted(e['tags']), 'uk_pos': sorted(x for x in e['pos'] if x),
                   'gloss_match': gloss_match, 'etym_en': e['etym_en'], 'uk_gloss': gl[:300]}
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    print('written', OUT, flush=True)


if __name__ == '__main__':
    main()
