# Progress

## Done
- **Identical words**: about 13,000 cards (`data/words.json`), each checked at least twice and then by a final expert pass. Words in Top 1000–Top 10K were also read by a linguist (`docs/review/linguist-final.md`).
- **Bands by frequency of the card's meaning** (not of the word form), with the subtitle blend for everyday words and Google Books Ngram counts for phrases. Top 400 was merged into Top 1000.
- **Examples**: 4 sentences on every card, graded by band (A0–A1 in Top 1000), practical, in the card's meaning. **Grammar** ("a photo · photos") and **Say:** word partners on common cards. Notes are English-only.
- **Pronunciation**: every word is recorded with Kokoro-82M. The most used words were checked with a speech recognizer, and unclear ones were re-recorded with another voice. The stressed vowel is underlined on the card, matching the recording (misaki pronunciations, CMUdict fallback); noun/verb pairs use the noun reading.
- **Site**:
  - bigger words, and a picture place on the back (`images/<word>.webp`, see README)
  - grid and one-by-one views, swipe, shuffle, topics, Hide slang (also hides rude English words)
  - My words, basic training
  - examples are loaded per band, audio per bundle
- **Pictures**: about 470 cards have a Noto Emoji picture that shows the card's meaning (taxi, doctor, hotel, koala…). The place for your own photos is ready (`images/<word>.webp`).
- **Second sweep round** for modern loanwords: 14 domains, 2,187 suggestions. About 430 passed the dictionary check, and about 370 were confirmed identical by the second check and the expert pass (смолток, плот-твіст, хепі-ауер, сіті-брейк…).
- **Precision sweep**: every card in Top 20K and rarer (about 12,000) was judged by two independent judges. The 161 pairs both rejected were removed.
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
- `docs/review/linguist-final.md`: final review of all 244 cards in Top 1000–3000. 34 cards fixed: examples, shares, Say lines, notes. A second reviewer read the 813 cards of Top 5000–10K and fixed 32.
- Examples in Top 2000–5000 were rewritten where needed, so at least 2 of 4 sentences are things a learner would say (questions, requests, "I…" sentences).

## Next
- Photos for concrete nouns where an emoji is not enough (drop files into `images/`).
- "Hide slang" is on by default. The linguist suggests showing these pairs (please = пліз, hello = хелло) by default, because they are key A0 words.
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
