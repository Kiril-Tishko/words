# Same Words · Однакові слова

Flip cards of English words that are the same in Ukrainian (taxi = таксі, computer = комп'ютер, hotel = готель), sorted by level A0–C2. The site is for learning English.

Open `index.html` in a browser. It works offline, and it also works on GitHub Pages (Settings → Pages → deploy from this branch, root folder).

## Site
- Choose a frequency band (Top 400 … Rare) to get its cards. **Grid** shows 4 cards per row; **One by one** shows a single card (← → keys, Space flips it).
- Card front: the English word, "=", and the Ukrainian word. 🇬🇧 marks words used only in British English. 🔊 reads the word aloud in the browser's English voice.
- Click a card to flip it. The back has room for 4 examples and a usage note (to be added later) and shows the word's labels.
- **+** adds a word to **My words**. These are saved in this browser only.
- **Train** (basic): shows the Ukrainian word; you recall the English word, then mark "I knew it" or "Again".

## How the word list is built
No word list comes from memory. Each step is a script or a recorded check.

1. `tools/fetch_sources.sh` downloads open word lists:
   - English: words_alpha (~370k words, including archaic), CMUdict pronunciations, Hunspell en_US/en_GB, Wiktionary (via kaikki.org), wordfreq
   - Ukrainian: VESUM/dict_uk, Hunspell uk_UA, Wiktionary, wordfreq
   - English–Ukrainian dictionaries: MUSE, Wiktionary translations
2. `tools/find_candidates.py` renders every English word (~617k) into Ukrainian letters in all plausible ways:
   - by spelling (hotel → готель)
   - by sound (computer → комп'ютер)
   - by letter names (DJ → діджей)
   
   It then matches the renderings against ~650k Ukrainian words, giving 2.4M raw look-alike pairs.
3. `tools/prepare_batches.py` keeps the plausible pairs and splits them into batches:
   - **verify** batches: a dictionary lists the pair as a translation
   - **scan** batches: everything else
   - It also adds pairs where a dictionary translation looks like the English word but the matcher missed it.
4. Agents check every batch against `data/RUBRIC.md` and save their verdicts in `data/checked/*.json`. The verdicts are: identical, similar, false friend, partial false friend, proper noun, inflected form, unrelated.
5. A second, independent agent re-checks every "identical" pair and every borderline pair (`data/checked/cross-*.json`). It also sets the level of the shared meaning.
6. Topic sweeps (`data/checked/sweep-*.json`) look for words the matcher missed. Every suggestion must exist in both the English and the Ukrainian dictionaries (`tools/check_gaps.py`), and it is then verified like everything else.
7. `tools/build_site.py` merges everything into `data/words.json` and builds `words.js` and `index.html`.

## Status
10,812 identical words, all checked twice. See `PROGRESS.md`.

## Frequency bands (site categories)
- Each word is labelled by how often it is used in English: its rank among the most used English words. The categories are Top 400, Top 1000, Top 2000, Top 3000, Top 5000, Top 10K, Top 20K, Top 50K, Top 100K and Rare. Cards are sorted from most to least used.
- Ranks come from `data/levels/en-rank.tsv`, built by `tools/compute_ranks.py`:
  - source: the wordfreq English frequency list
  - inflected forms are folded into their base word (computers → computer, went → go)
  - words Wiktionary knows only as names are removed
- A word form's frequency counts all its meanings, so a rank may not be more common than the level of the *shared* meaning allows (take = тейк, a film take, is not a top-100 word). Such ranks, and the ranks of phrases and abbreviations, are estimates and are shown as "About top N".
- The CEFR levels are still kept in `data/words.json` (`level`):
  - A0: Cambridge Pre A1 Starters
  - A1–B2: CEFR-J
  - C1–C2: Octanove
  - for the shared meaning, set by the second check

## Labels
- Usage: `international`, `archaic`, `obsolete`, `dated`, `literary`, `informal`, `slang`, `abbreviation`, `technical`, `rare`.
- Topic: one or two of food, sport, music, tech, science, …
- `british`: the word is used only in British English. One spelling per card: American/international, or British for British-only words.

## Saved for later
- `data/similar.json`: same meaning, different form (problem = проблема)
- `data/false_friends.json`, `data/partial_false_friends.json`

## Rebuild
```bash
pip install wordfreq rapidfuzz
tools/fetch_sources.sh
python3 tools/find_candidates.py ../sources/candidates.jsonl
python3 tools/prepare_batches.py
python3 tools/build_site.py
```
