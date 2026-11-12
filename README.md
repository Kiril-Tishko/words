# Same Words · Однакові слова

English words a Ukrainian already knows (taxi = таксі, metal = метал, organize ≈ організувати), grouped into **clouds**: one real-life situation, its words with pictures, and very simple sentences that use them. For Ukrainian students of English, from beginners up.

Open `index.html` in a browser. It works offline, and on any static host such as GitHub Pages (Settings → Pages → deploy from this branch, root folder).

## Site
The page has the shape of a lesson page: one thing per screen, the big line in the middle, Back and Next at the bottom. Labels are in simple English; Ukrainian appears in small fixed places (the twin of each word, the prompt to say, the translation behind «Переклад», the warning).

- **Today** opens on the next cloud with one button, **Start** or **Continue**. No level to choose.
- **A cloud** is one situation (At the café, At the doctor's, At the office). Its screens:
  1. **Repeat**: three sentences from earlier clouds. A rule cloud starts with its rule on one card.
  2. **Words**: the cloud. 16 words the student already knows, each with a picture and its Ukrainian twin; tap to hear it. More words are folded under one button.
     - The stressed vowel is underlined. The line is pink when the stress is not where it is in the Ukrainian word (меню́, but **ME**nu).
     - A **rare** tag marks a word that English speakers use much less than Ukrainians use its twin. A tap shows what people usually say (barman → bartender, telephone → phone).
  3. **Look and say**: pictures only. The student says the word, then taps the picture to check and hear it.
  4. **Say it**: five very simple sentences. The Ukrainian line comes first; the student says it in English, taps **Answer** and hears it.
  5. **Change one word**: one sentence, and the student swaps in other words they already know (A latte, please → cappuccino → espresso).
  6. **Dialogue**: four short lines marked "You hear" and "You say", with sound and a hidden translation.
  7. **Careful**: the look-alike that causes mistakes in this situation (magazine ≠ магазин, costume ≠ костюм).
  8. **All together**: the sentences as a list with sound.
  9. **This week**: three sentences the student writes for their own week.
- **Clouds** lists all 81 clouds, so a teacher can send a student straight to one (`index.html#c/doctor`).
- **Little words** (`index.html#kit`) lists the 68 little words that all the sentences are made of, with sound.
- **Search** finds any of the 13,000+ identical words and the "almost the same" words, in English or Ukrainian.

### Very simple sentences
Every sentence is made of **little words + words of the clouds**, six words at most: *A latte, please. This is my passport. I need a doctor. Where is the bank?* The little words are in `data/clouds/kit.txt` (I, is, a, the, this, have, need, want, like, where, and, no, please…). There are no past forms, no "can" and no "do" questions. The build checks every sentence and stops on any other word. Two start clouds teach the little words first. Why and how: `docs/review/simple-natural-pictures.md`.

### Clouds instead of levels
Every word here is already known, so there are no difficulty levels. The clouds go from what is needed every day to what is needed less often (`docs/review/practical-redesign.md`):

| Circle | Clouds | Examples |
|---|---|---|
| Every day | 39 | two start clouds, café, supermarket, home, clothes, city, transport, countries, travel, money, doctor, people, sport, music, internet |
| Rules | 9 | ‑ція → ‑tion, ‑ія → ‑y, ‑ний → ‑al / ‑ic / ‑ive, ‑ізм → ‑ism, ‑но → ‑ly |
| Work and study | 19 | office, projects, business, banking, IT, production, delivery, and three clouds of verbs |
| The wider world | 11 | politics, law, science, space, art |
| On the side | 3 | reactions (OK, wow, oops), slang (friend, people, cool) and old relatives (sister ≈ сестра, nose ≈ ніс) |

How they are made:
- The clouds are written by hand in `data/clouds/[a-e]-*.txt`: words, sentences, a dialogue and a warning for each. `tools/build_clouds.py` looks every word up in the checked lists, checks every sentence against the little words, and builds `clouds.js`. A word that is not in the lists cannot enter a cloud unchecked.
- 350 pairs were new, mostly verbs, adjectives, adverbs and place names. 317 were kept and 33 rejected; each decision is in `data/clouds/checked.json`.
- `data/clouds/words/*.txt` has one line for every word: its picture and, where needed, a usage note ("rare: bartender"). Both were decided by hand. 97 words are marked rare and 46 more have a tip.
- Pictures are Fluent Emoji 3D (Microsoft, MIT license). `tools/make_cloud_pictures.py` makes one picture sheet per cloud (`pictures/cloud-<id>.webp`).
- `tools/compute_cloud_stress.py` finds the stressed vowel of every word and the 668 words whose stress moves. The Ukrainian stress comes from the Ukrainian Wiktionary (CC BY-SA), kept in `data/clouds/uk-stress.json`.
- `tools/make_cloud_audio.py` records every word, sentence and dialogue line, one file per cloud (`audio/cloud-<id>.mp3`), and the little words (`audio/kit.mp3`).

The earlier site (CEFR levels, lessons with stories, flip cards) is kept as `site/app-v2-levels.html`; its data is still in `data/course/` and `data/stories/`. The sections below describe the word cards, which Search still shows.

Cards:
- **Front**: the English word with its stressed vowel marked, "=", and the Ukrainian word. 🇬🇧 marks British-only words, and 🔊 plays the recording.
- **Back**: a picture, grammar ("a photo · photos"), rank, word partners ("Say:"), 4 examples and an English-only note.

### Marks
Two small badges on the card (front, bottom right), chosen by agents for every card (`tools/workflows/word-marks.js` → `data/marks/`):
- **anglicism**: Ukrainians use the word as an English word, often as slang or only about English-speaking life (mister = містер, stuff = стаф, please = пліз). About 1,450 cards.
- **★ English too**: a word a Ukrainian would not expect in English, because it feels Ukrainian, Slavic or local (tsar = цар, hooligan = хуліган, bolt = болт, bazaar = базар, steppe = степ). About 430 cards.

The **Topics** menu can show only one kind ("★ English too", "Anglicisms") in any band.

### The earlier course (kept, not shown)
Every course word has a CEFR level (Cambridge Starters, CEFR-J and Octanove lists, or the checker's level for the card's meaning). The course holds all A0–B2 words and the C1 words of Top 20K: 2,590 words in 318 lessons.
- `tools/build_course.py` runs the pipeline. `tools/workflows/course-group.js` groups each level's words into scenes, keeping very similar words together (mister / Mrs. / Miss). `tools/workflows/course-write.js` writes each story at the lesson's level. The result is `data/course/course.json`, which becomes `course.js`.
- The earlier topic-based Stories outline (`data/stories/`, `docs/review/grouping.md`) is kept: the Exclamations dialogues come from it, and so do the families of similar words.
- **The grouping:** a linguist designed parts that run like a course: first words, café, shopping, travel, work, home, health, sport, media, the wider world. Each part is split into chapters. Each chapter is one scene with Anna, a student in Kyiv, and her friend Max (`docs/review/grouping.md`).
- **The story:** each chapter has a short, simple English story that uses its words in order. Click a word to hear it and see its card. The cards follow in the same order, and **Train these words** drills the chapter.
- **Exclamations:** wow, oops, hmm, bravo, ciao, meow and the like have their own part at the end, with short dialogues.
- **Very similar words are together** (`data/stories/families-*.json`, `tools/build_stories.py families`). Examples: mister, Mrs., Miss, sir, madam, lady and gentleman; hotel, motel, hostel and resort; cop, policeman, constable and sheriff; currencies; units; dances; dog breeds.
- **How it is built:** `tools/build_stories.py` runs the pipeline. A linguist outline (`data/stories/outline.json`) comes first. Then `tools/workflows/story-assign.js` places every word and `tools/workflows/story-write.js` writes the stories. The result is `data/stories/stories.json`, which becomes `stories.js`.

### Pictures
The back of every card has a picture place.
- About 470 cards (taxi, hotel, doctor, guitar, koala…) show a picture from **Noto Emoji** (Google, Apache License 2.0).
  - Agents picked a picture only where it clearly shows the card's meaning (`tools/workflows/emoji-map.js`). Abstract words get none.
  - `tools/make_pictures.py` turns the choices into `data/levels/pictures.json`, and the build puts the SVG on the card.
- To add your own picture, save it as `images/<word>.webp` (or `.jpg`, `.png`, `.svg`, `.avif`) and rebuild. It replaces the emoji.
  - The file name is the English word in lowercase, accents removed, spaces as hyphens: `images/taxi.webp`, `images/hot-dog.jpg`, `images/deja-vu.png`.

### Stress mark
The underlined vowel is the stressed syllable as the recording says it (`tools/compute_stress.py`). It uses the voice model's pronunciation dictionary (misaki), with CMUdict as a fallback. Noun/verb pairs use the noun reading (UPdate, IMpact).

### Almost the same
2,820 more words whose Ukrainian twin sounds almost the same and means the same: problem ≈ проблема, music ≈ музика, chocolate ≈ шоколад (`tools/build_similar.py` → `similar.js`). They come from two sources:
- the pairs the first check judged "similar"
- a new pass over the 5,000 most used English words (`tools/workflows/similar-find.js`)

A strict checker (`tools/workflows/similar-check.js`) then re-read every pair in Top 20K. It kept only pairs that a learner hears as similar at once, with the same main everyday meaning and a standard Ukrainian word. That removed won = вона, rest = решта, report = рапорт and matter = матерія. Names are left out.

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
python3 tools/build_clouds.py                # clouds.js from data/clouds/; checks every sentence against the little words
/home/user/tts-venv/bin/python tools/compute_cloud_stress.py   # stress marks of the cloud words, then build_clouds.py again
python3 tools/make_cloud_pictures.py         # one picture sheet per cloud (needs Pillow and the Fluent Emoji 3D pictures)
/home/user/tts-venv/bin/python tools/make_cloud_audio.py   # one sound file per cloud, then build_clouds.py again
python3 tools/build_site.py                  # index.html, words.js, details
python3 tools/make_audio.py --workers 2     # needs the Kokoro venv; --rebundle to repack all bundles
```
