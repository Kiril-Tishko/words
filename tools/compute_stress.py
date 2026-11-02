#!/usr/bin/env python3
"""Where is the stress in the English word? (for the underline on the card front)

The underline should match what the learner hears, so the main source is the pronunciation the recording uses:
the voice model's G2P (misaki) reading of the word, or the respelling in tools/make_audio.py OVERRIDES.
When misaki is not available or does not know the word, CMUdict is used (primary stress = 1); for noun cards with
several CMUdict pronunciations (project, update) the one stressed like the noun is taken.
The stressed syllable is mapped to a vowel-letter group of the spelling only when the number of vowel groups equals
the number of syllables (after dropping a silent final -e), so ambiguous spellings are left unmarked.
One-syllable words are not marked. Run with the TTS venv (it has misaki) for the full check.
Output: data/levels/stress.json  {"president": [2, 3], ...}  (character span of the stressed vowel letters)
"""
import json, os, re, sys

SRC = os.environ.get('SRC', '/home/user/sources')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data')
V = set('AIOWYiuɑɔəɛɜɪʊʌæᵊɚᵻɐ')                  # misaki vowel symbols (A = eɪ, I = aɪ, O = oʊ, W = aʊ, Y = ɔɪ)
NOUN_FIRST = {'reset', 'redirect', 'respawn'}   # nouns stressed on the first syllable that G2P reads as verbs


HIATUS = {'ia', 'io', 'iu', 'eo', 'ea', 'eu', 'ua', 'ue', 'uo', 'ie', 'oa', 'oe', 'ao', 'ui', 'ei', 'ai', 'oi'}


def vowel_groups(w):
    groups = []
    for m in re.finditer(r'[aeiouy]+', w):
        a, b = m.span()
        if w[a] == 'y' and a == 0 and b > 1:          # initial y before a vowel is a consonant (yoga)
            a += 1
        if w[a] == 'u' and a > 0 and w[a - 1] == 'q' and b - a > 1:
            a += 1                                    # qu: the u is a consonant (quiet, equal)
        if a < b:
            groups.append((a, b))
    return groups


def stress_of_phonemes(ph):
    """(index of the primary-stressed vowel, number of vowels) in a misaki phoneme string."""
    n, idx = 0, None
    for ch in ph:
        if ch == 'ˈ' and idx is None:
            idx = n
        elif ch in V:
            n += 1
    return idx, n


def fit(w, g, n):
    """Vowel groups of the spelling that line up with n syllables, or None.
    Allows a silent final e (office) and one two-vowel group said as two syllables (vi-de-o, i-de-a, mu-se-um)."""
    cands = [g]
    if w.endswith('e') and g and g[-1] == (len(w) - 1, len(w)):
        cands.append(g[:-1])                        # silent final e (office, minute)
    for c in cands:
        if len(c) == n:
            return c
    for c in cands:
        if len(c) == n - 1:
            splits = [i for i, (a, b) in enumerate(c) if b - a == 2 and w[a:b] in HIATUS]
            if len(splits) == 1:                    # exactly one place where the extra syllable can be
                i = splits[0]
                a, b = c[i]
                return c[:i] + [(a, a + 1), (a + 1, b)] + c[i + 1:]
    return None


def main():
    g2p, overrides = None, {}
    try:
        from misaki import en as misaki_en
        g2p = misaki_en.G2P(trf=False, british=False, fallback=None)
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from make_audio import OVERRIDES
        overrides = OVERRIDES
    except Exception as e:
        print('misaki not available (', e, '): CMUdict only')
    allprons, prons = {}, {}
    for line in open(f'{SRC}/cmudict.dict', encoding='utf-8'):
        line = line.split('#')[0].strip()
        if not line:
            continue
        w, pr = line.split(' ', 1)
        base = re.sub(r'\(\d+\)$', '', w)
        allprons.setdefault(base, []).append(pr.split())
        if base == w:
            prons[w] = pr.split()                       # first pronunciation by default
    entries = json.load(open(f'{D}/words.json', encoding='utf-8'))

    def k_of(p):
        v = [x for x in p if x[-1].isdigit()]
        return next((i for i, x in enumerate(v) if x.endswith('1')), None)

    out, src = {}, {'audio': 0, 'cmu': 0, 'none': 0}
    disagree = []
    for e in entries:
        en, pos = e['en'], e.get('pos')
        w = en.lower()
        if not re.fullmatch(r'[a-z]+', w) or en.isupper():
            continue
        g = vowel_groups(w)
        span = None
        # 1) the recording's own pronunciation
        if g2p:
            o = overrides.get(en)
            m = re.search(r'\(/(.+?)/\)', o) if o else None
            if m:
                ph = m.group(1)
            elif o:
                ph = None                               # respelled (déjà vu → deja vu): leave to CMUdict
            else:
                ph, _ = g2p(en[0].upper() + en[1:] + '.')
            if ph and '❓' not in ph:
                idx, n = stress_of_phonemes(ph)
                gg = fit(w, g, n)
                if idx is not None and n >= 2 and gg:
                    span = gg[idx]
        # 2) CMUdict
        span_cmu = None
        if w in prons:
            pr = prons[w]
            if pos == 'noun' and len({k_of(p) for p in allprons.get(w, [])}) > 1:
                want = 0 if w in NOUN_FIRST else None
                if want is None and g2p:
                    ph, _ = g2p('the ' + w + '.')
                    i, _n = stress_of_phonemes(ph)
                    want = None if i is None else i - 1
                match = [p for p in allprons[w] if k_of(p) == want]
                if match:
                    pr = match[0]
            vow = [p for p in pr if p[-1].isdigit()]
            if len(vow) >= 2 and any(p.endswith('1') for p in vow):
                gg = fit(w, g, len(vow))
                if gg:
                    span_cmu = gg[k_of(pr)]
        if span is not None:
            src['audio'] += 1
            if span_cmu is not None and span_cmu != span:
                disagree.append(en)
        elif span_cmu is not None:
            span = span_cmu
            src['cmu'] += 1
        else:
            src['none'] += 1
            continue
        out[en] = list(span)
    json.dump(out, open(f'{D}/levels/stress.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(out), 'words marked', src, '| CMUdict differs from the recording for', len(disagree), 'words, e.g.',
          ' '.join(disagree[:30]))
    for e in ['president', 'student', 'computer', 'internet', 'hotel', 'email', 'lemonade', 'superstar', 'update', 'reset',
              'project', 'chardonnay', 'video', 'taxi', 'museum']:
        if e in out:
            a, b = out[e]
            print(f'  {e[:a]}[{e[a:b]}]{e[b:]}')


if __name__ == '__main__':
    main()
