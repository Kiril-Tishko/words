# Progress

## Done: identical words (first set)
- **10,812 identical words**, every one checked twice. Saved in `data/words.json` and shown on the site via `words.js`.
- By frequency band: Top 400 15 · Top 1000 75 · Top 2000 115 · Top 3000 186 · Top 5000 355 · Top 10K 785 · Top 20K 1,225 · Top 50K 2,305 · Top 100K 1,817 · Rare 3,934.
- The site uses frequency bands instead of A0–C2 (see README). CEFR levels are still kept in `data/words.json`.
- Saved for later sets: `data/similar.json` (2,946), `data/false_friends.json` (350), `data/partial_false_friends.json` (842).

## How it was checked
1. **Automatic matching.** Every English word was matched against every Ukrainian word by spelling, sound and letter names (`tools/find_candidates.py`), then batched (`tools/prepare_batches.py`).
2. **First check.**
   - Batches with dictionary evidence or look-alike scans were checked against `data/RUBRIC.md` (`tools/workflows/check-batches.js`).
   - After the usage limit, the remaining batches used a cheaper flow: obvious non-matches were sorted by script into `data/checked/auto-not-identical.json`, and the rest went through `tools/workflows/check-batches-lite.js`.
3. **Topic sweeps.** 24 topics (`tools/workflows/topic-sweep.js`). Every suggestion had to exist in the English and Ukrainian dictionaries (`tools/check_gaps.py`). Accepted ones went to the second check (`tools/gaps_to_cross.py`).
4. **Second check.**
   - Common words: full skeptical re-check that also sets the level of the shared meaning (`tools/workflows/cross-check(-lite).js`).
   - Rare words: flag-only re-check (`tools/workflows/rare-flag.js` + `tools/expand_flags.py`).

## Also done
- Frequency bands instead of A0–C2. Labels on cards describe only the English word. "Hide slang" filter.
- Examples + English notes: 2,756 most used words (Top 400 … Top 20K).
- Recorded pronunciations for all words (Kokoro neural voice), checked with a speech recognizer.

## Next
- Examples for the remaining 8,000 less common words (Top 50K, Top 100K, Rare).
- Training mode (basic version is in place).
- "Similar words" and "false friends" sets (`data/similar.json`, `data/false_friends.json`).
