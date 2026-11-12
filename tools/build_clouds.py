#!/usr/bin/env python3
"""Word clouds: everyday situations (café, kitchen, doctor, office…) with the words a Ukrainian already knows.

Source: data/clouds/*.txt, written by hand (see docs/review/practical-redesign.md). Format:
  === A | Щодня | Every day                      a circle (order of the files and of the lines is the order on the site)
  --- cafe | ☕ | У кафе | At the café            a cloud: id | emoji | Ukrainian name | English name
  W menu; cappuccino; croissant~круасан; cream=крем [Ice cream, please.]
        words. "en" is looked up in the checked lists; "en=uk" picks one card of several; "en~uk" is a pair that is
        not in the lists yet (it must be in data/clouds/checked.json, or the build reports it); [..] is the example to show
  M ...   more words of the cloud (shown folded)
  R -ція = -tion … | -ція = -tion …                    a rule or a short explanation, shown before the words
  S A cappuccino, please. | Капучино, будь ласка.     a ready phrase and its translation
  D A: Hi! A latte, please. | Привіт! Лате, будь ласка.   a line of a short dialogue
  ! chef ≠ шеф | chef = кухар; шеф = boss           a look-alike to watch out for
Output: clouds.js (window.CLOUDS) for the site, and data/clouds/unchecked.json (pairs still to verify).
"""
import glob, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data')


def load_lists():
    ident = {}
    for w in json.load(open(f'{D}/words.json', encoding='utf-8')):
        ident.setdefault(w['en'].lower(), []).append(w['uk'])
    s = open(f'{REPO}/similar.js', encoding='utf-8').read()
    sim = {w['en'].lower(): w['uk'] for w in json.loads(s[s.index('['):s.rindex(']') + 1])}
    p = f'{D}/clouds/checked.json'
    checked = {}
    if os.path.exists(p):
        for x in json.load(open(p, encoding='utf-8')):
            checked[x['en'].lower() + '|' + x['asked']] = x          # asked = the Ukrainian word as written in the cloud file
    return ident, sim, checked


def parse_word(tok):
    tok = tok.strip()
    ex = ''
    m = re.search(r'\[(.+)\]\s*$', tok)
    if m:
        ex, tok = m.group(1).strip(), tok[:m.start()].strip()
    for sep in ('=', '~'):
        if sep in tok:
            en, uk = tok.split(sep, 1)
            return en.strip(), uk.strip(), sep, ex
    return tok, '', '', ex


def main():
    ident, sim, checked = load_lists()
    circles, problems, unchecked, seen, notes = [], [], [], {}, []
    cur = cloud = None
    for f in sorted(glob.glob(f'{D}/clouds/*.txt')):
        for ln, raw in enumerate(open(f, encoding='utf-8'), 1):
            line = raw.rstrip('\n')
            if not line.strip() or line.lstrip().startswith('//'):
                continue
            where = f'{os.path.basename(f)}:{ln}'
            if line.startswith('==='):
                cid, uk, en = [x.strip() for x in line[3:].split('|')]
                cur = {'id': cid, 'uk': uk, 'en': en, 'clouds': []}
                circles.append(cur)
            elif line.startswith('---'):
                cid, emoji, uk, en = [x.strip() for x in line[3:].split('|')]
                cloud = {'id': cid, 'e': emoji, 'uk': uk, 'en': en, 'w': [], 'm': [], 's': [], 'd': [], 'x': []}
                cur['clouds'].append(cloud)
            elif line[:2] in ('W ', 'M '):
                for tok in line[2:].split(';'):
                    if not tok.strip():
                        continue
                    en, uk, sep, ex = parse_word(tok)
                    k = en.lower()
                    item = None
                    ck = checked.get(k + '|' + uk) if uk else None
                    if uk and k in ident and uk in ident[k]:
                        item = {'en': en, 'uk': uk, 'k': '='}
                    elif uk and sim.get(k) == uk:
                        item = {'en': en, 'uk': uk, 'k': '~'}
                    elif uk and ck and ck.get('ok'):
                        item = {'en': en, 'uk': ck.get('uk') or uk, 'k': ck.get('k', '~')}
                    elif uk and ck:                      # checked and rejected: say so
                        problems.append(f'{where}: "{en} ~ {uk}" was rejected by the check: {ck.get("why", "")}')
                        continue
                    elif uk:                             # a pair from outside the lists: must be checked
                        unchecked.append({'en': en, 'uk': uk, 'cloud': cloud['id']})
                        item = {'en': en, 'uk': uk, 'k': '~', 'new': 1}
                    elif k in ident:
                        item = {'en': en, 'uk': ident[k][0], 'k': '='}
                        if len(set(ident[k])) > 1:
                            problems.append(f'{where}: "{en}" has several cards {sorted(set(ident[k]))}: write en=uk')
                    elif k in sim:
                        item = {'en': en, 'uk': sim[k], 'k': '~'}
                    else:
                        problems.append(f'{where}: "{en}" is not in the checked lists (write en~uk to have it checked)')
                        continue
                    if ex:
                        item['ex'] = ex
                    if k in seen and line[0] == 'W':
                        item['also'] = seen[k]            # the word lives in an earlier cloud too
                    seen.setdefault(k, cloud['id'])
                    cloud['w' if line[0] == 'W' else 'm'].append(item)
            elif line[:2] in ('S ', 'D '):
                en, _, uk = line[2:].partition('|')
                cloud['s' if line[0] == 'S' else 'd'].append([en.strip(), uk.strip()])
            elif line.startswith('R '):
                en, _, uk = line[2:].partition('|')
                cloud['r'] = [en.strip(), uk.strip()]
            elif line.startswith('! '):
                a, _, b = line[2:].partition('|')
                cloud['x'].append([a.strip(), b.strip()])
            else:
                problems.append(f'{where}: cannot read this line')
    n = sum(len(c['w']) + len(c['m']) for ci in circles for c in ci['clouds'])
    json.dump(unchecked, open(f'{D}/clouds/unchecked.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    out = {'circles': circles}
    json.dump(out, open(f'{D}/clouds/clouds.json', 'w', encoding='utf-8'), ensure_ascii=False)   # for tools/make_cloud_audio.py
    # from the word cards: the stressed vowel and one example sentence; from the check: a short note
    cards, examples = {}, {}
    wp = os.path.join(REPO, 'words.js')
    if os.path.exists(wp):
        t = open(wp, encoding='utf-8').read()
        a = t.index('window.WORDS = ') + len('window.WORDS = ')
        for w in json.loads(t[a:t.rindex(']') + 1]):
            cards[(w['en'], w['uk'])] = w
        for f in glob.glob(os.path.join(REPO, 'details-*.js')):
            t = open(f, encoding='utf-8').read()
            for k, v in json.loads(t[t.index(', {') + 2:t.rindex('}') + 1]).items():
                if v.get('ex'):
                    examples[k] = v['ex'][0]
    word_notes = {x['en'].lower() + '|' + x['uk']: x['note'] for x in checked.values() if x.get('note')}
    for ci in circles:
        for c in ci['clouds']:
            for w in c['w'] + c['m']:
                card = cards.get((w['en'], w['uk']))
                if card and card.get('st'):
                    w['st'] = card['st']
                if not w.get('ex') and examples.get(w['en'] + '|' + w['uk']):
                    w['ex'] = examples[w['en'] + '|' + w['uk']]
                nt = word_notes.get(w['en'].lower() + '|' + w['uk'])
                if nt:
                    w['n'] = nt
                w.pop('new', None)
    ap = f'{D}/clouds/audio.json'       # recorded phrases and words: {cloud id: {text: [start, duration]}}
    if os.path.exists(ap):
        au = json.load(open(ap, encoding='utf-8'))
        for ci in circles:
            for c in ci['clouds']:
                c['au'] = au.get(c['id'], {})
    with open(os.path.join(REPO, 'clouds.js'), 'w', encoding='utf-8') as f:
        f.write('// Generated by tools/build_clouds.py from data/clouds/*.txt — word clouds by everyday situation.\n')
        f.write('window.CLOUDS = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
    print(sum(len(ci['clouds']) for ci in circles), 'clouds,', n, 'words,', len(unchecked), 'pairs to check,', len(problems), 'problems')
    for p in problems[:400] + notes[:100]:
        print('  ', p)
    return 1 if problems and '--strict' in sys.argv else 0


if __name__ == '__main__':
    sys.exit(main())
