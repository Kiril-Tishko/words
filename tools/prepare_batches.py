#!/usr/bin/env python3
"""Turn raw candidate pairs into review batches for agents.

Evidence used to rank / filter pairs (all automatic, from open dictionaries):
  muse      - pair is in the MUSE English–Ukrainian dictionary
  wikt_tr   - English Wiktionary lists the Ukrainian word as a translation
  gloss     - Ukrainian Wiktionary entry glosses it with the English word
Pairs with dictionary evidence go to "verify" batches (full check + labels).
Pairs without it go to "scan" batches (agents pick out the real ones, which are then verified).
Extra pairs are added when a dictionary translation looks like the English word but the
rule-based matcher missed it (e.g. jaguar = ягуар).
"""
import json, os, re, sys, unicodedata
from collections import defaultdict

from rapidfuzz import fuzz

SRC = os.environ.get('SRC', '/home/user/sources')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(REPO, 'data', 'candidates')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def strip_stress(s):
    if not s:
        return ""
    return unicodedata.normalize('NFC', ''.join(ch for ch in unicodedata.normalize('NFD', s) if ch != '́'))


UK2LAT = dict(zip('абвгґдеєжзиіїйклмнопрстуфхцчшщьюя',
                  ['a', 'b', 'v', 'h', 'g', 'd', 'e', 'ye', 'zh', 'z', 'y', 'i', 'yi', 'y', 'k', 'l', 'm', 'n', 'o',
                   'p', 'r', 's', 't', 'u', 'f', 'kh', 'ts', 'ch', 'sh', 'shch', '', 'yu', 'ya']))


def lat_key(s):
    """coarse Latin phonetic key used to compare an English word with a transliterated Ukrainian one"""
    s = s.lower()
    s = ''.join(UK2LAT.get(ch, ch) for ch in s)
    s = re.sub(r"['’ʼ\- ]", '', s)
    for a, b in (('ph', 'f'), ('ck', 'k'), ('qu', 'kv'), ('x', 'ks'), ('c', 'k'), ('w', 'v'), ('y', 'i'),
                 ('kh', 'h'), ('j', 'dzh'), ('g', 'h'), ('ee', 'i'), ('oo', 'u'), ('th', 't')):
        s = s.replace(a, b)
    s = re.sub(r'(.)\1+', r'\1', s)
    return s


def gloss_head_match(en, gl):
    """True if the English word is one of the headline equivalents in a Ukrainian gloss
    (e.g. gloss 'taxi, cab' or 'a taxi (vehicle)'), not just any word inside a long definition."""
    if not gl:
        return False
    for g in gl.lower().split(' | '):
        g = re.sub(r'\([^)]*\)', '', g)
        for item in re.split(r'[,;:]', g):
            item = re.sub(r'^(a|an|the|to)\s+', '', item.strip())
            if item == en:
                return True
    return False


def write_verify(path, batch):
    out = []
    for item in batch:
        en = item['en']
        c0 = item['candidates'][0]
        head = f"## {en}   [cefr {c0['cefr'] or '-'}; zipf {c0['zen']}]"
        if c0['en_tags']:
            head += ' en-tags: ' + ','.join(c0['en_tags'])
        out.append(head)
        for g in dict.fromkeys(c0.get('en_gloss', [])):
            out.append('   en: ' + g)
        for r in item['candidates']:
            line = f"   - {r['uk']}   [{r['how']}"
            if r['cost'] is not None:
                line += f" c{r['cost']}"
            line += f"; ev {','.join(r['ev']) or '-'}; zipf-uk {r['zuk']}"
            if r['uk_tags']:
                line += '; uk-tags ' + ','.join(r['uk_tags'])
            line += ']'
            if r.get('uk_gloss'):
                line += '  uk-gloss: ' + r['uk_gloss'][:160]
            out.append(line)
    open(path, 'w', encoding='utf-8').write('\n'.join(out) + '\n')


def main():
    muse = set()
    for line in open(f'{SRC}/en-uk.txt', encoding='utf-8'):
        p = line.split()
        if len(p) == 2:
            muse.add((p[0], p[1]))

    # English Wiktionary: translations to Ukrainian + usage tags + short glosses
    wtr = defaultdict(set)
    wtags = defaultdict(set)
    wgloss = defaultdict(list)
    for line in open(f'{SRC}/en_wikt_small.jsonl', encoding='utf-8'):
        d = json.loads(line)
        w = (d.get('w') or '').lower()
        if not w:
            continue
        for t in d.get('tr', []):
            wtr[w].add(strip_stress(t).lower())
        for g, tags, trs in d.get('s', []):
            for t in trs:
                wtr[w].add(strip_stress(t).lower())
            for t in tags:
                wtags[w].add(t)
            if len(wgloss[w]) < 3 and g:
                wgloss[w].append(f"({d.get('pos')}) {g[:90]}" + (f" [{','.join(tags)}]" if tags else ''))

    seen = set()
    verify = defaultdict(list)   # en -> pairs
    scan = defaultdict(list)     # uk -> pairs
    stats = defaultdict(int)
    for line in open(f'{SRC}/candidates.jsonl', encoding='utf-8'):
        d = json.loads(line)
        en, uk = d['en'], d['uk']
        if re.search(r"[.'’]", en) or uk.startswith('-') or uk.endswith('-'):
            continue
        d['gloss_match'] = gloss_head_match(en, d.get('uk_gloss', ''))
        d['muse'] = (en, uk) in muse
        d['wikt_tr'] = uk.lower() in wtr.get(en, ())
        conf = d['muse'] or d['wikt_tr'] or d['gloss_match']
        src = set(d['en_src'])
        lemma = any(s.startswith('vesum') or s in ('hunspell', 'wikt') for s in d['uk_src'])
        if not conf:
            if not (src & {'alpha', 'cmu', 'us', 'gb', 'cefrj', 'octanove'}):
                continue
            if not lemma and d['zipf_uk'] < 3:
                continue
            pos = set(d['uk_pos'])
            if pos & {'verb', 'adj'} and 'noun' not in pos:
                continue
            if re.search(r'(ти|тися|ться|ся)$', uk):
                continue
            if d['cost'] >= 2:
                continue
            if len(en) <= 2 and 'letters' not in d['methods']:
                continue
            if uk.isupper() and len(uk) > 1:
                continue
        seen.add((en, uk))
        rec = {'en': en, 'uk': uk, 'how': '+'.join(d['methods']), 'cost': d['cost'],
               'ev': [k for k in ('muse', 'wikt_tr', 'gloss_match') if d[k]],
               'cefr': d['cefr'], 'zen': d['zipf_en'], 'zuk': d['zipf_uk'],
               'uk_tags': d['uk_tags'], 'en_tags': sorted(wtags.get(en, ()))[:8]}
        if conf:
            rec['en_gloss'] = wgloss.get(en, [])[:3]
            rec['uk_gloss'] = d['uk_gloss'][:200]
            verify[en].append(rec)
            stats['verify'] += 1
        else:
            scan[uk].append(rec)
            stats['scan'] += 1

    # rule gaps: dictionary translations that look like the English word but were not matched
    import wordfreq
    added = 0
    pairs = set()
    for en, trs in wtr.items():
        for t in trs:
            pairs.add((en, t))
    pairs |= muse
    for en, uk in pairs:
        if (en, uk) in seen or ' ' in uk and ' ' not in en:
            continue
        if not re.fullmatch(r"[a-z][a-z \-]*", en) or not re.fullmatch(r"[а-яґєії'’ \-]+", uk):
            continue
        a, b = lat_key(en), lat_key(uk)
        if len(a) < 3 or len(b) < 3:
            continue
        r = fuzz.ratio(a, b)
        if r >= 80 and abs(len(a) - len(b)) <= 2:
            rec = {'en': en, 'uk': uk, 'how': 'dict-similar', 'cost': None, 'ev': ['dict'], 'cefr': None,
                   'zen': round(wordfreq.zipf_frequency(en, 'en'), 2), 'zuk': round(wordfreq.zipf_frequency(uk, 'uk'), 2),
                   'uk_tags': [], 'en_tags': sorted(wtags.get(en, ()))[:8], 'en_gloss': wgloss.get(en, [])[:3], 'uk_gloss': ''}
            verify[en].append(rec)
            seen.add((en, uk))
            added += 1
    stats['dict_similar_added'] = added
    print(dict(stats), 'verify en words', len(verify), 'scan uk words', len(scan))

    os.makedirs(OUTDIR, exist_ok=True)
    for f in os.listdir(OUTDIR):
        if f.startswith(('verify-', 'scan-')):
            os.remove(os.path.join(OUTDIR, f))
    # verify: most common English words first, ~120 pairs per batch
    ens = sorted(verify, key=lambda w: (-max(r['zen'] for r in verify[w]), w))
    batch, bn, size = [], 0, 0
    for w in ens:
        batch.append({'en': w, 'candidates': verify[w]})
        size += len(verify[w])
        if size >= 120:
            write_verify(f'{OUTDIR}/verify-{bn:03d}.txt', batch)
            bn += 1; batch = []; size = 0
    if batch:
        write_verify(f'{OUTDIR}/verify-{bn:03d}.txt', batch)
        bn += 1
    # scan: one line per Ukrainian word with its English look-alikes, ~600 lines per batch
    uks = sorted(scan, key=lambda u: (-max(r['zuk'] for r in scan[u]), u))
    sn = 0
    for i in range(0, len(uks), 600):
        lines = []
        for u in uks[i:i + 600]:
            ens_ = sorted({r['en'] for r in scan[u]}, key=lambda e: -max(r['zen'] for r in scan[u] if r['en'] == e))
            lines.append(u + ' :: ' + ', '.join(ens_[:25]))
        open(f'{OUTDIR}/scan-{sn:03d}.txt', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
        sn += 1
    print('verify batches', bn, 'scan batches', sn)


if __name__ == '__main__':
    main()
