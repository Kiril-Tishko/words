#!/usr/bin/env python3
"""Where is the stress in the English word? (for the underline on the card front)

Uses CMUdict (primary stress = 1). The stressed syllable is mapped to a vowel-letter group of the spelling;
the mapping is used only when the number of vowel groups equals the number of syllables (after dropping a
silent final -e), so ambiguous spellings are simply left unmarked. One-syllable words are not marked.
Words with several CMUdict pronunciations that differ in stress (project, update, impact) are noun/verb pairs:
for a noun card the pronunciation is chosen by how the voice model's G2P (misaki, run with the TTS venv) reads
"the <word>", so the mark follows the noun (UPdate, not upDATE). Without misaki the first CMUdict entry is used.
Output: data/levels/stress.json  {"president": [2, 3], ...}  (character span of the stressed vowel letters)
"""
import json, os, re

SRC = os.environ.get('SRC', '/home/user/sources')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data')


def vowel_groups(w):
    groups = []
    for m in re.finditer(r'[aeiouy]+', w):
        a, b = m.span()
        if w[a] == 'y' and a == 0 and b > 1:          # initial y before a vowel is a consonant (yoga)
            a += 1
        if a < b:
            groups.append((a, b))
    return groups


V = set('AIOWYiuɑɔəɛɜɪʊʌæᵊɚ')
NOUN_FIRST = {'reset', 'redirect', 'respawn'}   # nouns stressed on the first syllable that the G2P reads as verbs


def noun_stress_index(g2p, word):
    """Index of the stressed vowel when the word is read as a noun ("the <word>"), from misaki phonemes."""
    ph, _ = g2p('the ' + word + '.')
    n, idx = 0, None
    for ch in ph:
        if ch == 'ˈ' and idx is None:
            idx = n
        elif ch in V:
            n += 1
    return None if idx is None else idx - 1        # minus the vowel of "the"


def main():
    try:
        from misaki import en as misaki_en
        g2p = misaki_en.G2P(trf=False, british=False, fallback=None)
    except Exception:
        g2p = None
        print('misaki not available: using the first CMUdict pronunciation for noun/verb pairs')
    allprons = {}
    prons = {}
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
    words = [w['en'] for w in entries]
    pos = {w['en']: w.get('pos') for w in entries}
    out, skipped, chosen = {}, 0, []
    for en in words:
        w = en.lower()
        if not re.fullmatch(r'[a-z]+', w) or en.isupper() or w not in prons:
            continue
        pr = prons[w]
        if g2p and pos.get(en) == 'noun' and len(allprons.get(w, [])) > 1:
            def k_of(p):
                v = [x for x in p if x[-1].isdigit()]
                return next((i for i, x in enumerate(v) if x.endswith('1')), None)
            if len({k_of(p) for p in allprons[w]}) > 1:
                want = 0 if w in NOUN_FIRST else noun_stress_index(g2p, w)
                match = [p for p in allprons[w] if k_of(p) == want]
                if match and match[0] != pr:
                    pr = match[0]
                    chosen.append(w)
        vow = [p for p in pr if p[-1].isdigit()]
        if len(vow) < 2 or not any(p.endswith('1') for p in vow):
            continue
        k = 0 if w in NOUN_FIRST and pos.get(en) == 'noun' else next(i for i, p in enumerate(vow) if p.endswith('1'))
        g = vowel_groups(w)
        if len(g) == len(vow) + 1 and w.endswith('e') and g[-1] == (len(w) - 1, len(w)):
            g = g[:-1]                                  # silent final e (office, minute)
        if len(g) != len(vow):
            skipped += 1
            continue
        out[en] = list(g[k])
    json.dump(out, open(f'{D}/levels/stress.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(len(out), 'words marked;', skipped, 'skipped (ambiguous spelling);', len(chosen), 'nouns use a later CMUdict entry:',
          ' '.join(chosen))
    for e in ['president', 'student', 'computer', 'internet', 'hotel', 'season', 'moment', 'theater', 'office', 'idea', 'video', 'taxi', 'project', 'banana', 'museum']:
        if e in out:
            a, b = out[e]
            print(f'  {e[:a]}[{e[a:b]}]{e[b:]}')


if __name__ == '__main__':
    main()
