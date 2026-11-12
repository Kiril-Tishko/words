#!/usr/bin/env python3
"""The stressed vowel of every word of the clouds (for the underline on the word).

Same method as tools/compute_stress.py: the pronunciation the recording uses (the voice model's G2P), mapped to the
vowel letters of the spelling when that can be done safely. Words that are verbs in the "Actions" clouds and names
with a fixed pronunciation take it from tools/make_cloud_audio.py. One-syllable words are not marked.
Run with the TTS venv (it has misaki), after tools/build_clouds.py; then run build_clouds.py again:
    /home/user/tts-venv/bin/python tools/compute_cloud_stress.py
Output: data/clouds/stress.json  {"salad": [1, 2], "do-work/export": [3, 4], ...}

It also finds the words whose stress moves: меню́ but MEnu, шокола́д but CHOcolate. The Ukrainian stress comes from
the Ukrainian Wiktionary (the kaikki.org dump, CC BY-SA; only the words of the clouds are kept, in
data/clouds/uk-stress.json). The stress "moves" when the stressed syllable, counted from the start of the word, is
not the same in the two words (two vowels in a row in the Ukrainian word may be one English syllable: кру-а-сан,
croi-ssant). Output: data/clouds/stress-shift.json  {"menu|меню": "меню́", "do-work/export|експортувати": …}
"""
import unicodedata
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compute_stress import V, fit, stress_of_phonemes, vowel_groups   # noqa: E402
from make_audio import OVERRIDES                                        # noqa: E402
from make_cloud_audio import PLACES, VERBS                              # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data')


UK_VOWELS = set('аеєиіїоуюяАЕЄИІЇОУЮЯ')
ACUTE = '\u0301'


def uk_stress_source(words):
    """{Ukrainian word: the word with its stress mark} for the given words; from the dump if it is here, else the saved file"""
    path, dump = f'{D}/clouds/uk-stress.json', os.path.join(os.environ.get('SRC', '/home/user/sources'), 'kaikki.org-dictionary-Ukrainian.jsonl')
    saved = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
    if os.path.exists(dump):
        want = set(words)
        for line in open(dump, encoding='utf-8'):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            w = e.get('word', '')
            if w not in want or w in saved:
                continue
            cands = [f.get('form', '') for f in e.get('forms', []) if 'canonical' in f.get('tags', [])]
            cands += [h.get('expansion', '').split(' ')[0] for h in e.get('head_templates', [])]
            for c in cands:
                c = unicodedata.normalize('NFD', c)
                if ACUTE in c and unicodedata.normalize('NFC', c.replace(ACUTE, '')).lower() == w.lower():
                    saved[w] = unicodedata.normalize('NFC', c)
                    break
        saved = {k: saved[k] for k in sorted(saved) if k in want}
        json.dump(saved, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    return saved


def uk_syllable(stressed):
    """Where the stress is in a Ukrainian word with one stress mark: the index of the stressed syllable, and the same
    index when vowels in a row count as one syllable. None for one-syllable words and words with two stress marks."""
    s = unicodedata.normalize('NFC', stressed)      # NFC keeps й and ї as single letters; the stress mark stays apart
    if s.count(ACUTE) != 1:
        return None
    n, idx, runs, run_idx, prev_vowel = 0, None, 0, None, False
    for i, ch in enumerate(s):
        if ch == ACUTE:
            continue
        if ch in UK_VOWELS:
            if not prev_vowel:
                runs += 1
            if i + 1 < len(s) and s[i + 1] == ACUTE:
                idx, run_idx = n, runs - 1
            n += 1
            prev_vowel = True
        else:
            prev_vowel = False
    return {idx, run_idx} if idx is not None and n >= 2 else None


def main():
    from misaki import en as misaki_en
    g2p = misaki_en.G2P(trf=False, british=False, fallback=None)
    data = json.load(open(f'{D}/clouds/clouds.json', encoding='utf-8'))
    out, none, where = {}, [], {}

    def span_of(en, ph=None, key=None):
        w = en.lower()
        if not re.fullmatch(r'[a-z]+', w) or en.isupper():
            return None
        if ph is None:
            o = OVERRIDES.get(en)
            m = re.search(r'\(/(.+?)/\)', o) if o else None
            ph = m.group(1) if m else None if o else g2p(en[0].upper() + en[1:] + '.')[0]
        if not ph or '❓' in ph:
            return None
        idx, n = stress_of_phonemes(ph)
        core = ph.rstrip('.!? ')
        gg = fit(w, vowel_groups(w), n, ends_in_vowel=bool(core) and core[-1] in V)
        if idx is None or n < 2 or not gg:
            return None
        where[key or en] = idx          # which syllable is stressed, counted from the start
        return list(gg[idx])

    for ci in data['circles']:
        for c in ci['clouds']:
            for w in c['w'] + c['m']:
                en = w['en']
                if c['id'].startswith('do-') and en.lower() in VERBS:
                    s = span_of(en, VERBS[en.lower()], c['id'] + '/' + en)
                    if s:
                        out[c['id'] + '/' + en] = s
                    continue
                if en in out:
                    continue
                s = span_of(en, PLACES.get(en))
                if s:
                    out[en] = s
                elif re.fullmatch(r'[A-Za-z]+', en):
                    none.append(en)
    json.dump(out, open(f'{D}/clouds/stress.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(out), 'words marked;', len(set(none)), 'left unmarked (one syllable or an unclear spelling)')
    # the stress moves: the stressed syllable, counted from the start, is not the same as in the Ukrainian word
    pairs = set()
    for ci in data['circles']:
        for c in ci['clouds']:
            for w in c['w'] + c['m']:
                key = c['id'] + '/' + w['en']
                pairs.add((key if key in where else w['en'], w['uk']))
    uk = uk_stress_source({u for _, u in pairs})
    shift, same, unknown = {}, 0, 0
    for en, u in sorted(pairs):
        s = uk_syllable(uk[u]) if u in uk else None
        if en not in where or not s:
            unknown += 1
        elif where[en] not in s:
            shift[en + '|' + u] = uk[u]
        else:
            same += 1
    json.dump(shift, open(f'{D}/clouds/stress-shift.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('stress moves in', len(shift), 'pairs; stays in', same, '; not known for', unknown)
    print('  ', ', '.join(f'{k.split("|")[0]} / {v}' for k, v in list(shift.items())[:40]))
    for e in ['salad', 'banana', 'hotel', 'menu', 'cafe', 'balcony', 'police', 'tomato', 'Ukraine', 'Kyiv', 'Canada', 'organize', 'do-work/export', 'do-talk/protest']:
        if e in out:
            x = e.split('/')[-1]
            a, b = out[e]
            print(f'  {e}: {x[:a]}[{x[a:b]}]{x[b:]}')


if __name__ == '__main__':
    main()
