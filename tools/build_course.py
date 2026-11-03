#!/usr/bin/env python3
"""The course: levels (A0 … C1) -> topic sections -> short lessons, each with a story at the lesson's level.

Pipeline (agents do the language work, this script does the bookkeeping):
  1. data/course/in-g*.txt            words of each level with topic and family hints (made with levels.json)
  2. tools/workflows/course-group.js  -> data/course/group-g*.json   lessons: level, section, title, words
  3. python3 tools/build_course.py lessons [K]  -> data/course/lessons.json + batch-*.json (K lessons per batch)
  4. tools/workflows/course-write.js  -> data/course/story-*.json    order + story per lesson
  5. python3 tools/build_course.py final        -> data/course/course.json (read by tools/build_site.py)
Exclamations (wow, oops, ciao…) are not leveled: they stay a collection of short dialogues taken from the
earlier Stories outline (data/stories/stories.json, part "Exclamations").
"""
import glob, json, os, re, sys
from collections import OrderedDict

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(REPO, 'data', 'course')
LEVELS = [('A0', 'Starter', 'Your very first words: things you can see and point at.'),
          ('A1', 'Beginner', 'Everyday words for people, places, food and plans.'),
          ('A2', 'Elementary', 'Words for work, travel, shopping and talking about your day.'),
          ('B1', 'Intermediate', 'Words for news, health, opinions and the wider world.'),
          ('B2', 'Upper-intermediate', 'Words for business, society, science and culture.'),
          ('C1', 'Advanced', 'Less common words you meet in articles, films and books.')]
MARK = re.compile(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
# near-duplicate section names from different grouping agents
SECTION_MERGE = {'School and science': 'School and study', 'Work and business': 'Work and money', 'Money and finance': 'Work and money'}


def word_meta():
    out = {}
    for f in glob.glob(f'{C}/in-g*.txt'):
        for line in open(f, encoding='utf-8'):
            m = re.match(r'\[(\w+)\] (.+?) = (.+?) \| (\S+) \| (\S+) \| (.*)$', line.rstrip('\n'))
            if not m:
                continue
            lv, en, uk, band, pos, rest = m.groups()
            ex = rest.split(' | e.g. ', 1)[1] if ' | e.g. ' in rest else ''
            out[en] = {'en': en, 'uk': uk, 'level': lv, 'band': band, 'pos': pos, 'ex': ex}
    return out


def cmd_lessons(k=8):
    meta = word_meta()
    lessons, seen = [], set()
    for f in sorted(glob.glob(f'{C}/group-g*.json')):
        for l in json.load(open(f, encoding='utf-8')):
            ws = [w for w in l.get('words', []) if w in meta and w not in seen]
            if not ws:
                continue
            seen |= set(ws)
            lv = l.get('level') or meta[ws[0]]['level']
            lessons.append({'level': lv, 'section': (l.get('section') or 'More words').strip(), 'title': l.get('title', ''), 'words': ws})
    missing = [w for w in meta if w not in seen]
    by_level = OrderedDict((lv, [l for l in lessons if l['level'] == lv]) for lv, _, _ in LEVELS)
    for w in missing:          # words no group file placed: a "More words" lesson at the end of their level
        lv = meta[w]['level']
        tail = [l for l in by_level[lv] if l['title'] == 'More words' and len(l['words']) < 10]
        if tail:
            tail[0]['words'].append(w)
        else:
            by_level[lv].append({'level': lv, 'section': 'More words', 'title': 'More words', 'words': [w]})
    out = []
    for lv, ls in by_level.items():
        # keep each section together, sections in order of first appearance
        order = OrderedDict()
        for l in ls:
            order.setdefault(l['section'], []).append(l)
        n = 0
        for sec, items in order.items():
            for l in items:
                n += 1
                l['id'] = f'{lv.lower()}-{n:02d}'
                out.append(l)
    json.dump(out, open(f'{C}/lessons.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    for f in glob.glob(f'{C}/batch-*.json'):
        os.remove(f)
    names = []
    for i in range(0, len(out), k):
        name = f'{i // k:02d}'
        batch = [dict(l, words=[meta[w] for w in l['words']]) for l in out[i:i + k]]
        json.dump(batch, open(f'{C}/batch-{name}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        names.append(name)
    from collections import Counter
    print(len(out), 'lessons', dict(Counter(l['level'] for l in out)), '|', len(missing), 'unplaced words added to "More words"')
    print('sizes', sorted(Counter(len(l['words']) for l in out).items()))
    print('batches:', json.dumps(names))


def cmd_final():
    lessons = json.load(open(f'{C}/lessons.json', encoding='utf-8'))
    stories = {}
    for f in sorted(glob.glob(f'{C}/story-*.json')):
        stories.update(json.load(open(f, encoding='utf-8')))
    out, problems = [], []
    for l in lessons:
        st = stories.get(l['id'], {})
        words = l['words']
        text = MARK.sub(lambda m: m.group(0) if (m.group(2) or m.group(1)).strip() in words else m.group(1), st.get('story', ''))
        seq, seen = [], set()
        for m in MARK.finditer(text):
            w = (m.group(2) or m.group(1)).strip()
            if w in words and w not in seen:
                seen.add(w)
                seq.append(w)
        rest = [w for w in words if w not in seen]
        if not st:
            problems.append((l['id'], 'no story'))
        elif rest:
            problems.append((l['id'], 'not in story', rest[:4]))
        sec = SECTION_MERGE.get(l['section'], l['section'])
        out.append({'id': l['id'], 'level': l['level'], 'section': sec, 'title': st.get('title') or l['title'],
                    'words': seq + rest, 'story': text})
    # lessons of one section stay together within a level (sections in order of first appearance)
    ordered = []
    for lv, _, _ in LEVELS:
        groups = OrderedDict()
        for l in out:
            if l['level'] == lv:
                groups.setdefault(l['section'], []).append(l)
        for g in groups.values():
            ordered += g
    out = ordered
    levels = [{'id': lv.lower(), 'code': lv, 'name': name, 'about': about} for lv, name, about in LEVELS
              if any(l['level'] == lv for l in out)]
    # exclamations: the dialogue chapters of the earlier Stories outline
    excl = []
    sp = os.path.join(REPO, 'data', 'stories', 'stories.json')
    if os.path.exists(sp):
        st = json.load(open(sp, encoding='utf-8'))
        pid = next((p['id'] for p in st['parts'] if p['title'].lower().startswith('exclamation')), None)
        for c in st['chapters']:
            if c['part'] == pid:
                excl.append({'id': 'ex-' + c['id'], 'level': '', 'section': 'Exclamations', 'title': c['title'],
                             'words': c['words'], 'story': c.get('story', '')})
    json.dump({'levels': levels, 'lessons': out, 'exclamations': excl}, open(f'{C}/course.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)
    print(len(out), 'lessons,', sum(len(l['words']) for l in out), 'words,', len(excl), 'exclamation dialogues;',
          len(problems), 'problems', problems[:8])


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'lessons':
        cmd_lessons(int(sys.argv[2]) if len(sys.argv) > 2 else 8)
    elif cmd == 'final':
        cmd_final()
    else:
        print(__doc__)
