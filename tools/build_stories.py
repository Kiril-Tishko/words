#!/usr/bin/env python3
"""Stories tab: words grouped by a linguist into scenes ("chapters"), each with a short story that uses them in order.

Pipeline (agents do the language work, this script does the bookkeeping):
  1. tools/workflows outline (linguist agent)      -> data/stories/outline.json  (parts, chapters, anchor words)
  2. python3 tools/build_stories.py todo [N]       -> data/stories/todo-*.txt    (words that are not anchors yet)
  3. tools/workflows/story-assign.js               -> data/stories/assign-*.json (word -> chapter)
  4. python3 tools/build_stories.py chapters [K]   -> data/stories/chapters.json + batch-*.json (K chapters per batch)
  5. tools/workflows/story-write.js                -> data/stories/story-*.json  (order + story per chapter)
  6. python3 tools/build_stories.py final          -> data/stories/stories.json  (read by tools/build_site.py)
Words in a story are marked [[word]] or [[form|word]], where word is the card's English.
"""
import glob, json, os, re, sys
from collections import defaultdict, OrderedDict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(REPO, 'data', 'stories')
SCOPE_BANDS = ['top-1000', 'top-2000', 'top-3000', 'top-5000', 'top-10k', 'top-20k']


def words_in():
    out = OrderedDict()
    for fn in ('words-in.txt', 'exclamations-in.txt'):
        for line in open(f'{S}/{fn}', encoding='utf-8'):
            if ' = ' not in line:
                continue
            en, rest = line.rstrip('\n').split(' = ', 1)
            parts = [p.strip() for p in rest.split(' | ')]
            out[en] = {'en': en, 'uk': parts[0], 'band': parts[1], 'pos': parts[2], 'topics': parts[3],
                       'ex': parts[4][5:] if len(parts) > 4 and parts[4].startswith('e.g. ') else ''}
    return out


def cmd_todo(n=6):
    o = json.load(open(f'{S}/outline.json', encoding='utf-8'))
    anchors = set()
    for c in o['chapters']:
        for k in ('anchors', 'extras', 'extra', 'more', 'words'):
            anchors |= {(w['en'] if isinstance(w, dict) else w) for w in (c.get(k) or [])}
    W = words_in()
    rest = [w for w in W if w not in anchors]
    for f in glob.glob(f'{S}/todo-*.txt'):
        os.remove(f)
    size = (len(rest) + n - 1) // n
    for i in range(n):
        chunk = rest[i * size:(i + 1) * size]
        open(f'{S}/todo-{i}.txt', 'w', encoding='utf-8').write(
            '\n'.join(f"{w} = {W[w]['uk']} | {W[w]['band']} | {W[w]['pos']} | {W[w]['topics']} | e.g. {W[w]['ex']}" for w in chunk) + '\n')
    print(len(W), 'words;', len(anchors), 'anchors;', len(rest), 'to assign in', n, 'files')


def cmd_chapters(k=12):
    o = json.load(open(f'{S}/outline.json', encoding='utf-8'))
    W = words_in()
    def outline_words(c):   # anchors plus any further words the linguist already placed
        ws = []
        for k in ('anchors', 'extras', 'extra', 'more', 'words'):
            for w in c.get(k) or []:
                w = w['en'] if isinstance(w, dict) else w
                if w in W and w not in ws:
                    ws.append(w)
        return ws
    chapters = OrderedDict((c['id'], dict(c, words=outline_words(c))) for c in o['chapters'])
    parts = {p['id'] for p in o['parts']}
    assign = {}
    for f in sorted(glob.glob(f'{S}/assign-*.json')):
        assign.update(json.load(open(f, encoding='utf-8')))
    placed = {w for c in chapters.values() for w in c['words']}
    new = defaultdict(list)
    for w, cid in assign.items():
        if w not in W or w in placed:
            continue
        if cid in chapters:
            chapters[cid]['words'].append(w)
        elif isinstance(cid, str) and cid.startswith('new:'):
            _, pid, title = (cid.split(':', 2) + ['', ''])[:3]
            new[(pid if pid in parts else 'misc', title.strip() or 'More words')].append(w)
        else:
            new[('misc', 'More words')].append(w)
        placed.add(w)
    missing = [w for w in W if w not in placed]
    for w in missing:
        new[('misc', 'More words')].append(w)
    # new chapters suggested by the assigners go at the end of their part
    n = len(chapters)
    for (pid, title), ws in sorted(new.items(), key=lambda x: -len(x[1])):
        n += 1
        cid = f'c{n:03d}'
        chapters[cid] = {'id': cid, 'part': pid, 'title': title, 'scene': title, 'anchors': [], 'level': 'A2', 'words': ws}
    order = {p['id']: i for i, p in enumerate(o['parts'])}
    seq = sorted(chapters.values(), key=lambda c: (order.get(c['part'], 999), int(re.sub(r'\D', '', c['id']) or 0)))
    full = []
    for c in seq:
        c['words'] = [dict(W[w]) for w in c['words']]
        full.append(c)
    json.dump({'parts': o['parts'], 'chapters': full}, open(f'{S}/chapters.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    for f in glob.glob(f'{S}/batch-*.json'):
        os.remove(f)
    names = []
    for i in range(0, len(full), k):
        name = f'{i // k:02d}'
        json.dump(full[i:i + k], open(f'{S}/batch-{name}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        names.append(name)
    sizes = [len(c['words']) for c in full]
    print(len(full), 'chapters;', sum(sizes), 'words; sizes min', min(sizes), 'max', max(sizes),
          '; new chapters', len(new), '; unassigned', len(missing))
    print('batches:', json.dumps(names))


MARK = re.compile(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')


def cmd_final():
    ch = json.load(open(f'{S}/chapters.json', encoding='utf-8'))
    stories = {}
    for f in sorted(glob.glob(f'{S}/story-*.json')):
        stories.update(json.load(open(f, encoding='utf-8')))
    out, dropped, problems = [], defaultdict(list), []
    for c in ch['chapters']:
        words = [w['en'] for w in c['words']]
        for cid in (c['id'], c['id'] + 'b'):
            st = stories.get(cid)
            if not st:
                continue
            text = MARK.sub(lambda m: m.group(0) if (m.group(2) or m.group(1)).strip() in words else m.group(1), st.get('story', ''))
            st = dict(st, story=text)
            marked = []
            for m in MARK.finditer(st.get('story', '')):
                marked.append((m.group(2) or m.group(1)).strip())
            order = [w for w in st.get('order', []) if w in words]
            # keep the order the story actually uses
            seq = [w for w in marked if w in words]
            seen = set()
            seq = [w for w in seq if not (w in seen or seen.add(w))]
            extra = [w for w in order if w not in seq]
            if extra:
                problems.append((cid, 'not in story', extra[:5]))
            out.append({'id': cid, 'part': c['part'], 'title': st.get('title') or c['title'], 'level': c.get('level', ''),
                        'words': seq + extra, 'story': st.get('story', '')})
        if c['id'] not in stories:
            problems.append((c['id'], 'no story', []))
            out.append({'id': c['id'], 'part': c['part'], 'title': c['title'], 'level': c.get('level', ''), 'words': words, 'story': ''})
        used = {w for o in out if o['id'] in (c['id'], c['id'] + 'b') for w in o['words']}
        for w in words:
            if w not in used:
                dropped[c['part']].append(w)
    # words a writer could not fit: one "More words" chapter at the end of their part
    for pid, ws in dropped.items():
        out.append({'id': f'm-{pid}', 'part': pid, 'title': 'More words', 'level': '', 'words': ws, 'story': ''})
    order = {p['id']: i for i, p in enumerate(ch['parts'])}
    out.sort(key=lambda c: (order.get(c['part'], 999), c['id'].startswith('m-')))
    parts = [p for p in ch['parts'] if any(c['part'] == p['id'] for c in out)]
    if any(c['part'] == 'misc' for c in out):
        parts.append({'id': 'misc', 'title': 'More words', 'about': ''})
    json.dump({'parts': parts, 'chapters': out}, open(f'{S}/stories.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(out), 'chapters,', sum(len(c['words']) for c in out), 'words,', sum(len(v) for v in dropped.values()),
          'dropped into "More words";', len(problems), 'problems', problems[:10])


def cmd_families(k=6):
    """Put very similar words together (owner: "like Miss and Mr."): apply data/stories/families.json.
    Moved words leave their old chapter, join the family's target chapter (or a new chapter at the end of
    its part); the changed chapters get batch-fNN.json files for the story writers."""
    ch = json.load(open(f'{S}/chapters.json', encoding='utf-8'))
    fams = json.load(open(f'{S}/families.json', encoding='utf-8'))
    old = {}
    if os.path.exists(f'{S}/stories.json'):
        old = {c['id']: c.get('story', '') for c in json.load(open(f'{S}/stories.json', encoding='utf-8'))['chapters']}
    chapters = OrderedDict((c['id'], c) for c in ch['chapters'])
    where = {w['en']: cid for cid, c in chapters.items() for w in c['words']}
    meta = {w['en']: w for c in chapters.values() for w in c['words']}
    changed, nnew, moved = set(), 0, 0
    for f in fams:
        words = [w for w in f.get('words', []) if w in where]
        if len(words) < 2:
            continue
        tgt = f.get('target')
        if tgt == 'new' or tgt not in chapters:
            nnew += 1
            tgt = f'f{nnew:02d}'
            chapters[tgt] = {'id': tgt, 'part': f.get('part') or chapters[where[words[0]]]['part'],
                             'title': f.get('title') or f.get('name', 'Words that go together'),
                             'scene': f.get('scene') or f.get('name', ''), 'anchors': [], 'level': 'A2', 'words': []}
        for w in words:
            src = where[w]
            if src == tgt:
                continue
            chapters[src]['words'] = [x for x in chapters[src]['words'] if x['en'] != w]
            chapters[tgt]['words'].append(meta[w])
            where[w] = tgt
            moved += 1
            changed.add(tgt)
    # drop chapters that lost all their words; keep the course order (new chapters at the end of their part)
    order = {p['id']: i for i, p in enumerate(ch['parts'])}
    seq = [c for c in chapters.values() if c['words']]
    pos = {c['id']: i for i, c in enumerate(seq)}
    seq.sort(key=lambda c: (order.get(c['part'], 999), c['id'].startswith('f'), pos[c['id']]))
    ch['chapters'] = seq
    json.dump(ch, open(f'{S}/chapters.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    todo = [dict(c, old_story=old.get(c['id'], '')) for c in seq if c['id'] in changed]
    for f in glob.glob(f'{S}/batch-f*.json'):
        os.remove(f)
    names = []
    for i in range(0, len(todo), k):
        name = f'f{i // k:02d}'
        json.dump(todo[i:i + k], open(f'{S}/batch-{name}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        names.append(name)
    print(len(fams), 'families;', moved, 'words moved;', nnew, 'new chapters;', len(todo), 'chapters to rewrite')
    print('batches:', json.dumps(names))


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'todo':
        cmd_todo(int(sys.argv[2]) if len(sys.argv) > 2 else 6)
    elif cmd == 'chapters':
        cmd_chapters(int(sys.argv[2]) if len(sys.argv) > 2 else 12)
    elif cmd == 'families':
        cmd_families(int(sys.argv[2]) if len(sys.argv) > 2 else 6)
    elif cmd == 'final':
        cmd_final()
    else:
        print(__doc__)
