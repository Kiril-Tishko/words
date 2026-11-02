# Progress

## Done: identical words (first set)
- **10,812 identical words**, every one checked twice. Saved in `data/words.json` and shown on the site via `words.js`.
- By level: A0 43 · A1 88 · A2 137 · B1 380 · B2 1,073 · C1 1,568 · C2 7,523. Most C2 words are rare or technical, labelled `rare`/`technical`.
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

## Next
- English-only usage notes for the card backs (the checkers' draft notes describe the Ukrainian side and are not shown).
- 4 examples per card.
- Training mode (basic version is in place).
- "Similar words" and "false friends" sets.
- Possibly paging for the very large C2 level.
