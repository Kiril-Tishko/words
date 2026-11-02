# Same Words · Однакові слова

Flip cards of English words that are the same in Ukrainian (taxi = таксі, computer = комп'ютер, hotel = готель), for learning English. Cards are sorted by how often the English word is used in the meaning on the card.

Open `index.html` in a browser. It works offline, and on any static host such as GitHub Pages (Settings → Pages → deploy from this branch, root folder).

## Site
- **Bands**: Top 1000, Top 2000, Top 3000, Top 5000, Top 10K, Top 20K, Top 50K, Top 100K and Rare. A word's band is its rank among the most used English words, counted **in the meaning on the card** (see Frequency). Cards go from most to least used.
- **Grid** shows 4 cards per row (3 on tablets, 1 on phones) and loads more as you scroll. **One by one** shows one big card: ← → keys or swipe, Space flips. **Shuffle** mixes the order; press it again for frequency order.
- **Front**: the English word with its stressed vowel underlined, "=", and the Ukrainian word. 🇬🇧 marks words used only in British English. 🔊 plays a recorded pronunciation.
- **Back**: a picture place, the word with its grammar ("a photo · photos", "rice · uncountable"), its rank, a **Say:** line with the usual word partners (take a photo · in the photo), 4 example sentences, English labels (informal, technical…) and a usage note when needed. Notes and labels are about the English word only.
- **Hide slang** (on by default) hides pairs whose Ukrainian word is slang, colloquial or rare (people = піпл), and rude English words. **Topics** filters a band by topic.
- **+** adds a card to **My words** (saved in this browser). **Train** (basic): see the Ukrainian word, recall the English one, mark "I knew it" or "Again"; missed cards come back in a second round. Without saved words it uses 10 sample cards of the current band.

### Pictures
The back of every card has a picture place.
- About 470 cards (taxi, hotel, doctor, guitar, koala…) show a picture from **Noto Emoji** (Google, Apache License 2.0).
  - Agents picked a picture only where it clearly shows the card's meaning (`tools/workflows/emoji-map.js`). Abstract words get none.
  - `tools/make_pictures.py` turns the choices into `data/levels/pictures.json`, and the build puts the SVG on the card.
- To add your own picture, save it as `images/<word>.webp` (or `.jpg`, `.png`, `.svg`, `.avif`) and rebuild. It replaces the emoji.
  - The file name is the English word in lowercase, accents removed, spaces as hyphens: `images/taxi.webp`, `images/hot-dog.jpg`, `images/deja-vu.png`.

### Stress mark
The underlined vowel is the stressed syllable as the recording says it (`tools/compute_stress.py`). It uses the voice model's pronunciation dictionary (misaki), with CMUdict as a fallback. Noun/verb pairs use the noun reading (UPdate, IMpact).

## Examples
Every card has 4 English example sentences in the card's meaning. Their level follows the band:
- Top 1000: A0–A1. At most 7 words, present tense, no idioms, at least 2 practical questions or requests, the key word partner (take a photo).
- Top 2000–3000: A1–A2.
- Top 5000–10K: A2–B1.
- Rarer words: B1, or B1–B2.

Each card also had a final expert pass (`tools/workflows/card-qa.js`). It checked the pair, the meaning share, English labels, grammar, word partners, examples and the note, and rewrote the examples where they used another meaning or broke the level.

## Audio
- Every word is recorded with the open neural voice Kokoro-82M (`tools/make_audio.py`): the American voice af_heart, and the British voice bf_emma for British-only words.
- Each word is said as a short sentence ("Face.") at normal speed, which makes word edges clearer. Abbreviations that collide with words are spelled out (IT → "I.T."), and accented and unit words get respellings (kHz → "kilohertz").
- Clips are packed into bundles of 100 words (`audio/chunk-NNN.mp3`, positions in `audio/manifest.json`). The page loads a bundle the first time a word from it is played and keeps the last 3 in memory.
- `tools/fix_audio.py` checks the clips of the most used words with a speech recognizer (Whisper small.en). Unclear clips are re-recorded with another voice when that is clearer (`data/audio-voices.json`).

## Frequency (how the bands are made)
- `tools/compute_ranks.py` builds `data/levels/en-rank.tsv`. It blends written English (wordfreq "large") and spoken English (OpenSubtitles 2018 counts) as a geometric mean. Inflected forms are folded into their base word (computers → computer, went → go), and name-only words are dropped.
- A word form's frequency counts all its meanings, so each card has a **share**: the % of the English word's uses that are in the card's meaning. The card's rank = word frequency × share. For example, country = кантрі (music) would be about 2% of "country", so it is not a top-2000 word. Shares come from the expert pass, with a calibration list (`tools/workflows/sense-share.js`, `data/sense/`). Ranks that depend on an estimate are shown as "About top N".
- Phrases and hyphenated words (coffee shop, real-time) are not in word lists. Their frequency is the geometric mean of the experts' estimate and the Google Books Ngram count (2015–2019, put on the word-list scale by `tools/phrase_freq.py`).

## How the word list is built
No word comes from memory. Each step is a script or a recorded check.

1. **Sources** (`tools/fetch_sources.sh`):
   - English: words_alpha (~370k words, including archaic), CMUdict, Hunspell en_US/en_GB, Wiktionary (kaikki.org), wordfreq, OpenSubtitles counts
   - Ukrainian: VESUM/dict_uk, Hunspell uk_UA, Wiktionary, wordfreq
   - English–Ukrainian: MUSE dictionary, Wiktionary translations
2. **Matching** (`tools/find_candidates.py`): every English word (~617k) is rendered into Ukrainian letters in all plausible ways and matched against ~650k Ukrainian words.
   - by spelling: hotel → готель
   - by sound: computer → комп'ютер
   - by letter names: DJ → діджей

   This gives 2.4M raw look-alike pairs.
3. **Batches** (`tools/prepare_batches.py`): 29k dictionary-backed pairs and 149k look-alike pairs.
4. **First check**: agents judge every pair against `data/RUBRIC.md`. Verdicts are identical, similar, false friend, partial false friend, proper noun, inflected form or unrelated.
5. **Second check**: an independent, skeptical agent re-checks every identical and borderline pair (`data/checked/cross-*.json`).
6. **Topic sweeps and full scan**: 24 topic sweeps, plus a scan of the whole common vocabulary (90,435 English and 60,629 Ukrainian words, read in full). These find words the matcher missed. Every suggestion must exist in both languages' dictionaries (`tools/check_gaps.py`) and passes the second check.
7. **Clean-up** (`tools/build_site.py`):
   - drops cards whose English word no dictionary or corpus knows (`tools/en_evidence.py`)
   - drops Latin-script Ukrainian sides and prefixes
   - merges spelling duplicates, keeping the American or international form
8. **Final expert pass** on every card (`tools/workflows/card-qa.js`), then a linguist review of all cards in Top 1000–Top 10K (`docs/review/linguist-final.md`).
9. **Second sweep round**: 14 domains of modern loanwords (воркаут, смолток, плот-твіст, хепі-ауер). Each suggestion went through the same dictionary check, second check and expert pass (`tools/workflows/sweep2.js`).
10. **Precision sweep**: two independent judges re-checked every card in Top 20K and rarer, about 12,000 cards. The pairs both judges rejected were removed (`tools/workflows/precision-sweep.js`, `tools/apply_prec_sweep.py`).

In total, about 62,000 recorded verdicts on 35,000 distinct pairs, plus about 24,000 pair judgments in the precision sweep, the full scans and the audits.

## Quality: how complete and how correct
Measured on random samples by independent agents who never saw the list (`data/audit/`):
- **Completeness (recall)**: two auditors went through 1,000 random English and 1,000 random Ukrainian words and listed every word with an identical twin. Disputed claims were adjudicated, and then went through the same expert pass as the list.
  - The list had 87% of the real pairs found from the English side (90% for common words), and 93% from the Ukrainian side (92% for common words).
  - The first audit, before the full scan, measured 73–75%.
  - The pairs the audit found missing were added.
- **Correctness (precision)**: two judges checked 400 random cards: 200 from Top 1000–Top 10K and 200 from the rest.
  - Common words: 94% accepted by both judges, 98% by at least one.
  - Rarer words: 89.5% by both, 96% by at least one.
  - Overall about 93%.
  - The pairs both judges rejected were removed.
- **After the precision sweep**, a fresh audit of 400 random cards from the final list:
  - rarer bands: 96% accepted by both judges, 99% by at least one
  - common bands: 88.5% by both, 95.5% by at least one
  - In common words, most rejections are cards whose meaning is a large but not the main sense of the English word, such as cream = крем (face cream) or director = директор. These stay on the site with a "Most often…" note. The clear errors were removed.

## Data
- `data/words.json`: all site words with rank, share, band, labels and sources. The site uses the generated `words.js` (cards), `details-<band>.js` (examples, notes, grammar; loaded per band) and `audio/`.
- Saved for later sets: `data/similar.json` (problem = проблема), `data/false_friends.json`, `data/partial_false_friends.json` (country = кантрі, set = сет).
- `data/excluded.json`: every word removed by a later check, with the reason.

## Rebuild
```bash
pip install wordfreq rapidfuzz
tools/fetch_sources.sh
python3 tools/find_candidates.py ../sources/candidates.jsonl
python3 tools/prepare_batches.py
python3 tools/compute_ranks.py
python3 tools/phrase_freq.py
python3 tools/compute_register.py
python3 tools/compute_stress.py
python3 tools/build_site.py
python3 tools/make_audio.py --workers 2     # needs the Kokoro venv; --rebundle to repack all bundles
```
