# Lexicographer review: accuracy of pairs, meanings, frequency bands and examples

Reviewer: bilingual English–Ukrainian lexicographer. Data: `data/words.json` as rebuilt on 2026-11-02 12:05, the build that already uses the sense-share ranks. Note that `docs/review/cards-sample.txt` and the screenshots were made from the older build, before sense share. Some of their bands are out of date: in the sample, country = кантрі is in Top 2000, but it is now in Top 10K.

## What I checked, and how sure I am

| Check | How much I checked | Result |
|---|---|---|
| Every pair in Top 400 – Top 3000 (231 cards) | read one by one, with their examples | about 25 problem pairs (≈11%). Most are partial false friends. |
| Random pairs from Top 3000 – Top 20K | 170 pairs | ≈5–6% doubtful |
| Random pairs from Top 50K – Rare | 170 pairs, plus a script check of all 10,812 | ≈2–3% doubtful by meaning. Separately, 229 "English" words have no English evidence at all (see 5). |
| Examples | all 4 sentences of about 200 cards, chosen to cover risky narrow meanings | ≈10% of these cards have at least 1 sentence in the wrong meaning. For narrow-meaning cards (share ≤ 30%) it is ≈15%. Projected over all 2,756 cards: about 150–250 cards. |
| Usage notes | 70 random notes, plus a script check of all 740 | ≈97% correct. 1 note talks about the Ukrainian word. |
| British-only flags, US spelling | all 18 flags, plus a regex scan of all words | all correct |
| Sense-share (meaning frequency) | every Top 3000 card with share ≤ 40, plus slang pairs | about 15 clearly wrong values, several of them in the top bands |
| Duplicates and form | script over all words | about 60 duplicate cards that differ only in spelling. 41 cards have a Ukrainian side in Latin letters. 17 cards are prefixes, not words. |

The independent precision audit that is running now (`data/audit/judged-prec-*.json`: 4 judges, 200 pairs each) rejects 19–22 of every 200 pairs, so about 10%. That matches my count for the common bands.

**Overall estimate:** about 92–95% of all cards are correct pairs. In the bands beginners see first (Top 400 – Top 3000), only about 88–90% are. The mistakes are concentrated in the most used words, because those words have the most meanings.

---

## Problems, most important first

### 1. Examples use the wrong meaning: the example writer is never told which meaning the card is about

**Cause.** `tools/workflows/examples.js` gives the writer only `english = ukrainian | pos | topic`. The new `examples2.js` does the same. The first checker already wrote down the exact meaning in `words.json → note`, but that note never reaches the example writer. The result is that, for many cards, the checker's note itself says the examples are wrong:

| Card | Checker's note (already in words.json) | What the examples do |
|---|---|---|
| market = маркет | "an open-air market is ринок" | all 4 are open-air markets: "We buy fresh fruit at the market", "farmers market" |
| block = блок | "a city block is квартал" | 4/4 are wrong: "two blocks away", "around the block", "a tower of blocks" (toy blocks = кубики) |
| cream = крем | "dairy cream = вершки" | "cream in your coffee", "Strawberries with cream" |
| hall = хол | "a concert hall = зала" | "The concert hall was full", "the end of the hall" (that is a corridor) |
| killer = кілер | "кілер = hitman; a killer in general is вбивця" | 3/4 are about any murderer: "Police are looking for the killer" |
| sort = сорт | "сорт is a variety or a grade" | 4/4 use "what sort of …" (= kind) |
| basis = базис | "the everyday word is основа" | 4/4 use "on a weekly basis", "the basis of friendship" |
| argument = аргумент | "a quarrel = сварка" | "I had an argument with my brother", "got into an argument about money" |
| hospital = госпіталь | "usually a military hospital; an ordinary hospital is лікарня" | 4/4 are about an ordinary hospital |
| light = лайт | the light, low-calorie meaning | "This bag is very light", "Wear light clothes" (that is weight or colour) |
| true = тру | "slang 'real, genuine'" | "Is it true that…", "That is not true" |
| sense = сенс | — | "sense of humor", "sense of smell" (почуття, нюх) |
| coach = коуч | (life or business coach) | 4/4 are sports coaches (= тренер) |
| director = директор | — | "director of the movie", "film director" (= режисер). "Our school director" is also a calque: say principal (US) or head teacher (UK). |
| hostess = хостес | — | "She thanked the hostess for a lovely dinner" (that is a host at home) |
| display = дисплей | — | "Shoes are on display in the window" |
| camp = кемп | — | "summer camp" (= табір) |
| parallel = паралель (noun) | — | "The two lines are parallel", "run in parallel" (adjective and adverb) |
| gay = гей | — | "the first gay to win", "Many gays and lesbians". The card's own note says this use is rude. |

**Fix:**
1. In `prepare` for examples2, add the checker's note and the sense share to every line, for example:
   `market = маркет | noun | places | MEANING: a (super)market store | NOT: open-air market (ринок)`
   Add to the prompt: "Every sentence must be one where a Ukrainian would naturally say the Ukrainian word on the card. If not, rewrite it."
2. Add a verification pass with a second agent. For each card it reads the 4 sentences and the meaning line, and answers per sentence: "Would a Ukrainian translate this word here with the card's Ukrainian word? yes/no". Every "no" is regenerated. Run it first on the ≈1,000 cards with share ≤ 50 or with a checker note that names a different Ukrainian word (`grep` for Cyrillic other than `uk` in `note`).
3. Replacement examples for the worst cards:
   - **cream**: "Put this cream on your hands." / "I use face cream every day."
   - **block**: "The walls are made of concrete blocks." / "Buy a block of cheese." The political meaning already has its own bloc card.
   - **hall**: "Wait for me in the hall of the hotel." / "The hall has a big mirror."
   - **coach**: "She works as a life coach." / "My business coach helps me plan."
   - **killer**: "The killer was paid to do it." / "He was a hired killer."
   - **director**: "She is the director of a big company." / "The director signs the papers."
   - **gay**: "He is gay." / "They are a gay couple." / "gay people".

### 2. Partial false friends are shown as "identical"

The rubric says the shared meaning must be a **main** meaning in both languages. For the cards below, the shared meaning is a small part of the English word's use (share 1–15%), or the Ukrainian word means something else in everyday speech. A learner would misuse them.

**Remove from the site and move to `partial_false_friends.json`** (verdict `partial_false_friend`):
- sort = сорт (2%)
- basis = базис (1%)
- true = тру (1%, slang only)
- hospital = госпіталь (military)
- market = маркет (supermarket, not market)
- killer = кілер (hitman only)
- speech = спіч: Ukrainian спіч is a toast or speech at an event; English speech is also the ability to speak, as in "freedom of speech"
- The audit also rejects: conto = конто, coxite = коксит (this one is a false friend: коксит = coxitis), banya = баня, sondage = зондаж, academist = академіст.

**Remove as not real or not standard Ukrainian** (a beginner would learn a word nobody uses):
- **elephant = елефант** (Top 5000. The Ukrainian word is слон; the checker even wrote "Obsolete in Ukrainian".)
- **alphabet = альфабет** (алфавіт or абетка)
- **welfare = велфер**
- **WTF = втф**
- **PC = ПК** (a Ukrainian abbreviation read "пе-ка", not a loan)
- **SUV = SUV** (Ukrainians say позашляховик or кросовер)
- **hey = гей**: modern Ukrainian borrows it as хей, which is already in `uk_alt`. гей as a greeting is folk-poetic, and on this site it collides with gay = гей. Swap the main form to **хей**, or drop the card.

**Keep, but add an English-only note and correct the examples** (the card's meaning is real but not the main one):

| Card | Note to add |
|---|---|
| article = артикль | "Most often 'article' is a text in a newspaper or on a website." |
| argument = аргумент | "Also, very often, a quarrel: 'We had an argument.'" |
| character = характер | "Also a person in a book, film or game." |
| check = чек | "A paper from a shop is a 'receipt'." |
| course = курс | "Also a part of a meal, and 'of course'." |
| coach = коуч | "Also a sports trainer, and (British) a long-distance bus." |
| director = директор | "A film director is also 'director'. A school head is 'principal' (US)." |

Similar narrow cards that need meaning-correct examples: front, security, hit, express, initial, chip, traffic, cream, block, hall, camp.

**Rule to add to `RUBRIC.md`:** "If the shared meaning is under 15% of the English word's use (sense share), AND the main English meaning has a different usual Ukrainian word, the verdict is `partial_false_friend`." Run it automatically: share < 15 plus a checker note naming another Ukrainian word gives a list for re-verdict, about 300 cards.

### 3. Sense-share (frequency in the card's meaning): about 15 clear errors, some in the top bands

Sense share is now applied, which is a big improvement: country = кантрі moved from Top 2000 to Top 10K, court = корт from Top 1000 to Top 5000, take = тейк to Top 20K. But the sense-share prompt (`sense-share.js`) was also not given the meaning, and the graders lowered the share when the Ukrainian word is slang. Share is a property of the **English** word only, so that is wrong:

| Card | Share now | Should be | Effect |
|---|---|---|---|
| people = піпл | 25 | 100 | rank 210 → 66 |
| cash = кеш | 0.5 | ~95 | now **Top 50K**, should be Top 2000 |
| profit = профіт | 1 | ~95 | Top 50K → Top 2000 |
| trouble = трабл | 1 | ~85 | Top 50K → Top 2000 |
| friendly = френдлі | 0.5 | ~95 | Top 50K → Top 3000 |
| digital = діджитал | 2 | ~90 | Top 20K → Top 2000 |
| proof = пруф | 1 | ~60 | Top 50K → Top 3000 |
| flag = флаг | 0.5 | ~90 | Top 50K → Top 5000 |
| easy = ізі | 1 | ~100 if the card is plain "easy"; keep 1 only if the card is limited to a game mode | — |
| Miss = міс | 25 | ~5 | too high: the verb "miss" is folded into the word |
| director = директор | 100 | ~50 | too high: film director |
| speech = спіч | 95 | ~40 | too high, if the card is kept |

**Fix:**
- Re-run sense share for the 535 cards with `uk_nonstd = true`, and for every card whose checker note names another Ukrainian word. Pass the meaning line, and add to the prompt: "How Ukrainians say it, and whether the Ukrainian word is slang, does not matter. Judge only how often English uses this meaning."
- Estimated ranks are shown as "About top 3,074", which suggests a precision they don't have. For `approx` ranks, show only the band ("About top 5,000").
- Phrase frequencies (`pm`) are agents' guesses on a different scale from wordfreq. For example, hot dog is 6 per million, while smartphone is 11.5 from wordfreq. If possible, calibrate the 356 phrases against a real n-gram source (Google Books Ngram or COCA). This is low priority.

### 4. Inside a band, slang pairs come first: the very first cards are "friend = френд" and "people = піпл"

`build_site.py` defines `odd()` ("standard words first, then slang…") but never uses it in the sort. Top 400 therefore opens with two Ukrainian slang words, and Top 1000 has party = паті, activity = актівіті, baby = бебі, and sorry = сорі near the top.

**Fix:** sort key `(band, uk_nonstd, rank)`. Standard pairs come first in every band, and slang pairs still show unless the filter hides them.

### 5. About 229 "English" words with no English evidence

229 cards are not in English Wiktionary, not in Hunspell en_US/en_GB, and have zero wordfreq frequency. All of them are in Rare. Many are Russian or Ukrainian terms written in Latin letters, or the wrong English form:
- **Not English words:** beskozyrka, dniprianka, BRDM = БРДМ
- **Form mismatch:** raskolnik = розкольник
- **Wrong English form:**
  - podometer (pedometer)
  - rotang (rattan)
  - demonstrant (demonstrator)
  - electrobus (electric bus)
  - versificator (versifier)
  - brachydactylia (brachydactyly)
  - onym, galloman, putinist, ukrainophobe
- **Also rejected by the audit:** disbalance (English: imbalance), angloman, explicator, eristavi, batyr, vatrushka, ara (English: macaw), beton (concrete).

My estimate is that 30–50% of these 229 are not real English. 454 cards are missing from English Wiktionary altogether.

**Fix:** keep these 229 off the site until a real English dictionary attests them (Merriam-Webster, Collins or Oxford). Where English uses another form, record it as `similar` with the real English word.

### 6. Duplicate cards that differ only in spelling (about 60)

The de-duplication in `build_site.py` only folds -our/-or, -re/-er and -ise/-ize. Duplicates left on the site:
- **Space, hyphen or accent only:** fast food / fastfood, time-out / timeout, prime time / primetime, wild card / wildcard, team building / teambuilding, lunch box / lunchbox, flash mob / flashmob, tie-break / tiebreak, chateau / château, eclair / éclair, souffle / soufflé, macrame / macramé, bechamel / béchamel, maître d'hôtel / maitre d'hotel. That is 37 groups.
- **Other spelling variants:** amoeba / ameba, tsar / czar, fjord / fiord, rajah / raja, jinn / djinn, hajji / haji / hadji, aesthete / esthete, kissel / kisel, epinephrine / epinephrin, hydrazine / hydrazin, novitiate / noviciate.
- **Word plus prefix:** ex / ex-, demo / demo-, eco / eco-, mono / mono-, techno / techno-, kilo / kilo-, psycho / psycho-.

**Fix:** merge cards by a key that ignores accents, spaces and hyphens, plus Wiktionary's "alternative spelling of". Keep the most frequent form, using the US form when frequency is close, and put the others in an "also spelled" field.

### 7. Cards that are not two words written in two alphabets

- **41 Ukrainian sides in Latin letters** (CEO = CEO, MVP = MVP, PDF = PDF, VPN = VPN, KPI = KPI, …). The front then shows "MVP = MVP", which teaches nothing.
  **Fix:**
  - Where Ukrainians write a Cyrillic reading, show it. It is already in `uk_alt` for HR → ейчар, USB → юесбі and IP → айпі; it is also common for SEO → сео and DJ → діджей.
  - Move the rest to a separate "Abbreviations" set.
- **17 prefixes** (ex-, extra-, eco-, geo-, kilo-, nano-, … yocto-). ex- is in **Top 2000**. They are not words, and the extra- examples hyphenate wrongly in predicative use: "The bus was extra-crowded" should have no hyphen.
  **Fix:** move them to a "Word parts" set, or drop them.

### 8. English usage labels are almost missing

Only 240 of 10,812 cards have any English register label (`register.json → en`). Cards with no label include:
- bullshit (Top 3000) and WTF (Top 5000): **vulgar**
- LOL and OMG: internet slang
- sexy, loser, cop, bro, ex: informal or rude

On the other hand, photo is labelled informal, which it is not. The owner wants the labels to describe the English word, so this matters.

**Fix:** label every card in Top 400 – Top 10K by hand or with an agent (about 1,100 cards). Add `vulgar` and `offensive` to the allowed labels. Keep vulgar cards out of Top 400 – Top 3000 by default, or give them a visible label.

### 9. Examples for the most used words are not yet A0–A1

The current examples are short (6.6–7.3 words), but many in Top 400 and Top 1000 use idioms, phrasal verbs and past tenses that beginners don't know:
- "got off to a good start"
- "throw a party"
- "went to Chicago on business"
- "pays attention to small details"
- "lined up at the start line"
- "He lived abroad for a period of five years"
- "It is a fact that water boils at 100 degrees"
- "Fall is a busy season for farmers"

The tier-1 spec in `examples2.js` is right (3–7 words, present simple, practical). Two conditions:
- (a) Assign tiers from the **new** bands, after sense share and the fixes above. Many words moved by 1–3 bands.
- (b) Add the meaning line from problem 1, so that the "simple" sentences are also in the right meaning.

20 cards in Top 5000 – Top 20K still have no examples, all multi-word or hyphenated: hip-hop (Top 5000), sci-fi, high-end, avant-garde, stand-up, know-how, déjà vu, a priori, pop-up, add-on, and others.

### 10. Small things

- **detective**: the note talks about the Ukrainian word ("In Ukrainian 'детектив' can also mean…"). Rewrite it as: "A crime novel is a 'detective story' or 'mystery'."
- **no-name**: the note "for brands say 'unknown brand'" contradicts itself. Use: "Informal; 'generic' or 'unbranded' is more common."
- **face control** is not really English. The card's own note says "door policy" is the English term. Move it to `similar` or `false_friends`.
- **home office** in English is a room, or the UK ministry. Ukrainian хоум-офіс means working from home, so it is a partial false friend. Check it.
- **Cards that share one Ukrainian form** (cash / cache = кеш, gin / jinn = джин, block / bloc = блок, hey / gay = гей) are fine as separate cards. Each needs examples that are clearly in its own meaning.
- `docs/review/cards-sample.txt` repeats some cards (stop, friend, people, general appear 2–3 times). The sampler has a bug; the data does not.

## What is already good

- **British-only flags:** all 18 are correct (lift, jumper, barrister, paracetamol, aeroplane, …). American spelling is used consistently (center, theater, meter). No missing British flag found.
- **Form adaptations** follow the rubric well. Of the 120 pairs with the least spelling similarity, all are correct sound-based borrowings (wow = вау, guideline = гайдлайн, cupcake = капкейк).
- **Usage notes** are short, correct and about English: uncountable nouns, irregular plurals, US/UK differences.
- **Recall spot check:** of 202 obvious everyday words, every one that is truly identical is on the site. The rest are correctly sent to `similar`: banana = банан, music = музика, police = поліція, restaurant = ресторан. tomato = томат is in `similar` by the rubric's "no dropped ending" rule. That is defensible, but worth a second look, because томат is a full standard word.
