# Progress

## Done
- **Identical words**: about 13,000 cards (`data/words.json`), each checked at least twice and then by a final expert pass. Words in Top 1000–Top 10K were also read by a linguist (`docs/review/linguist-final.md`).
- **Bands by frequency of the card's meaning** (not of the word form), with the subtitle blend for everyday words and Google Books Ngram counts for phrases. Top 400 was merged into Top 1000.
- **Examples**: 4 sentences on every card, graded by band (A0–A1 in Top 1000), practical, in the card's meaning. **Grammar** ("a photo · photos") and **Say:** word partners on common cards. Notes are English-only.
- **Pronunciation**: every word is recorded with Kokoro-82M. The most used words were checked with a speech recognizer, and unclear ones were re-recorded with another voice. The stressed vowel is underlined on the card (CMUdict).
- **Site**:
  - bigger words, and a picture place on the back (`images/<word>.webp`, see README)
  - grid and one-by-one views, swipe, shuffle, topics, Hide slang (also hides rude English words)
  - My words, basic training
  - examples are loaded per band, audio per bundle
- **Quality audits** (`data/audit/`):
  - recall 87% (English side) and 93% (Ukrainian side)
  - precision about 93%: 96% for common words
  - Details in README → Quality.

## Reviews
- `docs/review/teacher.md`, `docs/review/lexicographer.md`, `docs/review/ux.md`: first round. Their findings were acted on:
  - stress marks, grammar and Say lines
  - the A0–A1 rules for Top 1000
  - shares for slang pairs, and "Most often X means…" notes
  - the rude flag
  - the subtitle-based frequency, and the fix for "About Rare"
  - a11y and phone layout, plus audio and state bugs
- `docs/review/linguist-final.md`: final review of the current cards.

## Next
- Pictures for concrete nouns (the place on the card is ready).
- Training modes from the teacher review:
  - listen and type
  - tap the stressed syllable
  - fill the gap
  - a/an and plural
  - which meaning?
  - spaced repetition
- Sets saved for later: similar words (`data/similar.json`), false friends and partial false friends (country = кантрі).
- More archaic English words, each with a label.
- About 7–13% of identical pairs are still missing (see recall). Most are compounds and new loanwords that dictionaries do not list yet.
