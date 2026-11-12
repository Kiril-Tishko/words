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
  F A {cola|lemonade}, please. | {Колу|Лимонад}, будь ласка.   one frame, several known words ("change one word")
  D A: Hi! A latte, please. | Привіт! Лате, будь ласка.   a line of a short dialogue
  ! chef ≠ шеф | chef = кухар; шеф = boss           a look-alike to watch out for
  K I have | у мене є                               a little word of the start clouds (shown as a chip, with sound)
Other sources:
  data/clouds/kit.txt        the little words (I, is, a, the, have, like…). Every S, F and D sentence may use only these
                             words and the words of the clouds: the build reports any other word and any long sentence.
  data/clouds/words/*.txt    for every word: its picture (an emoji, drawn with Fluent Emoji 3D) and a usage note
                             ("rare: bartender" = English speakers use this word much less; what they usually say).
Output: clouds.js (window.CLOUDS) for the site, data/clouds/unchecked.json (pairs still to verify) and
data/clouds/pictures.json (the pictures of each cloud, in the order of its picture sheet; see tools/make_cloud_pictures.py).
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


def frame(text):
    """'A {x|y}, please. | {Х|У}, будь ласка.' -> [[English sentence, Ukrainian sentence, the changing English words], ...]"""
    depth, cut = 0, -1
    for i, ch in enumerate(text):
        depth += ch == '{'
        depth -= ch == '}'
        if ch == '|' and depth == 0:
            cut = i
            break
    if cut < 0:
        raise ValueError('a frame needs "English | Ukrainian"')
    out = []
    for side in (text[:cut].strip(), text[cut + 1:].strip()):
        m = re.match(r'^(.*?)\{([^{}]+)\}(.*)$', side)
        if not m:
            raise ValueError('a frame needs one {a|b|c} group on each side')
        out.append((m.group(1), [a.strip() for a in m.group(2).split('|')], m.group(3)))
    (ep, ea, es), (up, ua, us) = out
    if len(ea) != len(ua):
        raise ValueError('the frame has a different number of words on the two sides')
    return [[ep + a + es, up + b + us, a] for a, b in zip(ea, ua)]


def load_kit():
    """the little words: [{'t': group, 'items': [[English, Ukrainian], ...]}] and the set of allowed tokens"""
    groups, allowed = [], set()
    for raw in open(f'{D}/clouds/kit.txt', encoding='utf-8'):
        s = raw.strip()
        if not s or s.startswith('//'):
            continue
        if s.startswith('#'):
            groups.append({'t': s[1:].strip(), 'items': []})
            continue
        en, _, uk = s.partition('|')
        groups[-1]['items'].append([en.strip(), uk.strip()])
        allowed.update(re.findall(r"[a-z']+", en.lower()))
    return groups, allowed


def load_facts():
    """data/clouds/words/*.txt -> {'word' or 'cloud/word': {'pic', 'sym', 'rare', 'usual', 'note'}}"""
    facts, problems = {}, []
    for f in sorted(glob.glob(f'{D}/clouds/words/*.txt')):
        for ln, raw in enumerate(open(f, encoding='utf-8'), 1):
            s = raw.strip()
            if not s or s.startswith('//') or s.startswith('#'):
                continue
            p = [x.strip() for x in s.split('|')]
            if len(p) < 2 or not p[1]:
                problems.append(f'{os.path.basename(f)}:{ln}: a line needs "word | picture"')
                continue
            use = p[2] if len(p) > 2 else ''
            kind, _, usual = use.partition(':')
            if kind.strip() not in ('', 'rare', 'tip'):
                problems.append(f'{os.path.basename(f)}:{ln}: usage must start with "rare" or "tip"')
            if p[0] in facts:
                problems.append(f'{os.path.basename(f)}:{ln}: "{p[0]}" is there twice')
            facts[p[0]] = {'pic': p[1].lstrip('~'), 'sym': p[1].startswith('~'), 'rare': kind.strip() == 'rare',
                           'usual': usual.strip(), 'note': p[3] if len(p) > 3 else ''}
    return facts, problems


def forms(word):
    """the word and its simple forms: plural or he/she form"""
    w = word.lower()
    out = {w, w + 's', w + 'es'}
    if w.endswith('y'):
        out.add(w[:-1] + 'ies')
    return out


def tokens(text):
    return re.findall(r"[a-z']+", text.lower().replace('’', "'"))


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
    for f in sorted(glob.glob(f'{D}/clouds/[a-z]-*.txt')):
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
            elif line.startswith('F '):       # one frame, several words: "A {cappuccino|latte}, please. | {Капучино|Лате}, будь ласка."
                try:
                    cloud['f'] = frame(line[2:])
                except ValueError as e:
                    problems.append(f'{where}: {e}')
            elif line.startswith('R '):
                en, _, uk = line[2:].partition('|')
                cloud['r'] = [en.strip(), uk.strip()]
            elif line.startswith('K '):
                en, _, uk = line[2:].partition('|')
                cloud.setdefault('k', []).append([en.strip(), uk.strip()])
            elif line.startswith('! '):
                a, _, b = line[2:].partition('|')
                cloud['x'].append([a.strip(), b.strip()])
            else:
                problems.append(f'{where}: cannot read this line')
    n = sum(len(c['w']) + len(c['m']) for ci in circles for c in ci['clouds'])
    json.dump(unchecked, open(f'{D}/clouds/unchecked.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    kit, kit_words = load_kit()
    facts, fact_problems = load_facts()
    problems += fact_problems
    clouds = [c for ci in circles for c in ci['clouds']]
    out = {'circles': circles, 'kit': kit}
    json.dump(out, open(f'{D}/clouds/clouds.json', 'w', encoding='utf-8'), ensure_ascii=False)   # for tools/make_cloud_audio.py

    # very simple sentences: only the little words and the words of the clouds, six words at most
    known = set(kit_words)
    for c in clouds:
        for w in c['w'] + c['m']:
            for part in tokens(w['en']):
                known |= forms(part)
    for c in clouds:
        own = set()
        for w in c['w'] + c['m']:
            for part in tokens(w['en']):
                own |= forms(part)
        lines = [('S', s[0]) for s in c['s']] + [('D', d[0]) for d in c['d']] + [('F', f[0]) for f in c.get('f', [])]
        for kind, en in lines:
            text = re.sub(r'^[AB]:\s*', '', en)
            for sent in re.split(r'[.!?…]+', text):
                ts = tokens(sent)
                bad = [x for x in ts if x not in known]
                if bad:
                    problems.append(f'{c["id"]}: "{en}" uses {bad}: not a little word and not a word of the clouds')
                if len(ts) > 6:
                    problems.append(f'{c["id"]}: "{sent.strip()}" has {len(ts)} words (six at most)')
            if kind == 'S' and not (set(tokens(text)) & own):
                notes.append(f'{c["id"]}: "{en}" has no word of its own cloud')

    # a picture and a usage note for every word; each cloud has one picture sheet (index 0 is the cloud's own picture)
    def fact(c, en):
        return facts.get(c['id'] + '/' + en) or facts.get(en)

    def word_at(text, words):
        """the first of these words that the sentence uses: (position, word)"""
        low = ' ' + ' '.join(tokens(text)) + ' '
        best = None
        for en in words:
            ts = tokens(en)
            if not ts:
                continue
            for last in forms(ts[-1]):
                i = low.find(' ' + ' '.join(ts[:-1] + [last]) + ' ')
                if i >= 0 and (best is None or (i, -len(en)) < (best[0], -len(best[1]))):
                    best = (i, en)
        return best

    first_cloud = {}
    for c in clouds:
        for w in c['w'] + c['m']:
            first_cloud.setdefault(w['en'], c)
    pictures = {}
    for c in clouds:
        sheet = [c['e']]

        def index(emoji):
            if emoji not in sheet:
                sheet.append(emoji)
            return sheet.index(emoji)

        for w in c['w'] + c['m']:
            f = fact(c, w['en'])
            if not f:
                problems.append(f'{c["id"]}: "{w["en"]}" has no picture (data/clouds/words/*.txt)')
                continue
            w['p'] = index(f['pic'])
            if f['rare']:
                w['r'] = 1
            if f['usual']:
                w['u'] = f['usual']
            if f['note']:
                w['un'] = f['note']
        # "Look and say": words whose picture is the thing itself, and only that word's in this cloud
        literal = [w for w in c['w'] + c['m'] if fact(c, w['en']) and not fact(c, w['en'])['sym']]
        times = {}
        for w in literal:
            times[w['p']] = times.get(w['p'], 0) + 1
        look = [[w['en'], w['p']] for w in literal if times[w['p']] == 1][:8]
        if len(look) >= 4:
            c['l'] = look
        # the picture of a sentence: the first word of this cloud that it uses (else the first word of any cloud)
        own_words = [w['en'] for w in c['w'] + c['m']]

        def sentence_picture(text):
            hit = word_at(text, own_words)
            if hit:
                return index(fact(c, hit[1])['pic']) if fact(c, hit[1]) else -1
            hit = word_at(text, list(first_cloud))
            if hit and fact(first_cloud[hit[1]], hit[1]):
                return index(fact(first_cloud[hit[1]], hit[1])['pic'])
            return -1

        for s in c['s']:
            s.append(sentence_picture(s[0]))
        for f in c.get('f', []):
            f.append(sentence_picture(f[2]) if word_at(f[2], own_words) or word_at(f[2], list(first_cloud)) else sentence_picture(f[0]))
        pictures[c['id']] = sheet
    json.dump(pictures, open(f'{D}/clouds/pictures.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
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
    # the stressed vowel of each word, and the pairs whose stress moves (tools/compute_cloud_stress.py)
    sp, hp = f'{D}/clouds/stress.json', f'{D}/clouds/stress-shift.json'
    stress = json.load(open(sp, encoding='utf-8')) if os.path.exists(sp) else {}
    shift = json.load(open(hp, encoding='utf-8')) if os.path.exists(hp) else {}
    for ci in circles:
        for c in ci['clouds']:
            for w in c['w'] + c['m']:
                card = cards.get((w['en'], w['uk']))
                own = c['id'] + '/' + w['en']
                if own in stress or w['en'] in stress:
                    w['st'] = stress.get(own) or stress[w['en']]
                elif card and card.get('st'):
                    w['st'] = card['st']
                moved = shift.get(own + '|' + w['uk']) if own in stress else shift.get(w['en'] + '|' + w['uk'])
                if moved and w.get('st'):
                    w['us'] = moved             # the Ukrainian word with its stress mark: the English stress is elsewhere
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
        out['kau'] = au.get('_kit', {})
    with open(os.path.join(REPO, 'clouds.js'), 'w', encoding='utf-8') as f:
        f.write('// Generated by tools/build_clouds.py from data/clouds/*.txt — word clouds by everyday situation.\n')
        f.write('window.CLOUDS = ' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
    rare = len({w['en'] for c in clouds for w in c['w'] + c['m'] if w.get('r')})
    print(len(clouds), 'clouds,', n, 'words,', rare, 'marked rare,', sum(len(c['s']) for c in clouds), 'phrases,',
          len(unchecked), 'pairs to check,', len(problems), 'problems')
    for p in problems[:400] + notes[:100]:
        print('  ', p)
    return 1 if problems and '--strict' in sys.argv else 0


if __name__ == '__main__':
    sys.exit(main())
