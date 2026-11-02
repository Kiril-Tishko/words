# Teacher review: Same Words / Однакові слова

Reviewer role: an English teacher for Ukrainian-speaking learners (ESL methods, CEFR, vocabulary teaching).

What I checked:
- All 65 cards in Top 400 and Top 1000, sentence by sentence.
- The 187 cards whose meaning is a minor sense of a common English word.
- Simple measurements over all 2,756 example sets.
- English stress (CMUdict) against Ukrainian stress (Wiktionary) for 444 cards in Top 10K.
- The slang flags of the 455 cards in Top 5000.
- The 7 screenshots and the card, train and filter code in `index.html`.

Note: `data/words.json` was rebuilt with meaning shares (`share`) at 12:05 today, while this review was in progress. `cards-sample.txt` and the screenshots show the older bands, for example country in Top 2000. The numbers below come from the current `words.json` (Top 400 11 · Top 1000 54 · Top 2000 78 · Top 3000 88 · Top 5000 224 · Top 10K 584 · Top 20K 1,100).

## Summary

The word list is clean. I found almost no false friends, and most examples are natural English. The problems are about teaching, not about the data:

1. **The card does not teach what a Ukrainian speaker actually gets wrong with an "identical" word.** The meaning is already known. What learners get wrong is:
   - the stress (58% of checked words differ: президе́нт → PREsident);
   - the spelling (ph, th, y, double letters, silent e);
   - the article and plural (a/an, babies);
   - the verb that goes with the word (take a photo, not "make").

   Almost none of this is on the cards today.
2. **Cards that use a minor meaning of a very common word (country = кантрі, set = сет, like = лайк) do not warn the learner.** The learner then misreads the word everywhere else. Only 17 of 187 such cards say what the word usually means.
3. **The meaning shares are wrong for slang pairs.** When the Ukrainian slang word has the main English meaning (cash = кеш, trouble = трабл, friendly = френдлі), the word is buried in Top 50K. The examples on those cards use the main meaning, so the card contradicts its own band.
4. **The examples for the first bands are not A0–A1 and not practical enough.** About 1 in 3 is in the past tense, there are idioms ("got off to a good start"), and only 4% are questions a learner would ask.
5. **Training is not training yet.** Asking "френд → ?" for an identical word tests nothing. Training should drill stress, spelling, and use in a sentence, with spaced repetition.

## Problems, most important first

### 1. Minor-meaning cards give no warning about the main meaning

187 cards have `share` < 30% and an English word in the top 5,000 forms. On these cards the Ukrainian side shows the minor meaning, so the card itself is clear. But the learner leaves believing that the English word means the Ukrainian one. The next time they read "I like it", "a set of keys", "my country" or "the top of the page", they misunderstand it. Only 17 of the 187 notes mention the main meaning.

Examples. "raw rank" is the rank of the English word form in all its meanings; share is how much of that the card's meaning covers.

| card | raw rank | share | current note |
|---|---|---|---|
| like = лайк | #43 | 0.5% | — |
| take = тейк | #81 | 0.2% | — |
| live = лайв | #196 | 5% | — (and /laɪv/, not /lɪv/) |
| country = кантрі | #212 | 2% | "Usually said as 'country music.'" |
| set = сет | #244 | 1% | — |
| top = топ | #260 | 3% | — |
| player = плеєр | #276 | 5% | — |
| level = левел | #277 | 3% | — |
| general = генерал | #328 | 3% | — |
| court = корт | #348 | 10% | — |
| light = лайт | #479 | 1% | — |
| major = майор | #502 | 3% | — |
| front = фронт | #535 | 3% | — |
| march = марш | #561 | 3% | — |
| perfect = перфект | #654 | 0.3% | — |
| safe = сейф | #788 | 3% | — |
| forward = форвард | #787 | 1% | — |
| sort = сорт | #927 | 2% | "'Kind' is more common" |
| focus = фокус | #954 | 1% | — |
| bridge = бридж | #1472 | 2% | — |

**Fix.**
- For every card with `share` < 50 and raw rank ≤ 10,000 (408 cards), write the note with one fixed template, in English only and about the English word: `Most often "country" means a state: "Ukraine is a big country."` Use a short A1 example of the main meaning.
- If the card is also a homograph, add the sound: `"live" here sounds like "five" (a live show); the verb "live" (I live here) sounds like "give".`
- The new image on the back (see 11) must show the card's meaning, never the main meaning.

### 2. Meaning shares penalise slang pairs, so useful words are buried and the cards contradict their bands

The share should answer one question: what part of the English uses would a learner who knows the Ukrainian word understand correctly? For many slang pairs, the share seems to have been lowered because the *Ukrainian* word is slang. The examples on these cards use the main English meaning, so the card is in the wrong band for its own sentences.

| card | share now | band now | example on the card | realistic share |
|---|---|---|---|---|
| cash = кеш | 0.5% | Top 50K | "Do you have any cash?" | ~95% (~Top 2000) |
| trouble = трабл | 1% | Top 50K | "I had trouble finding your house." | ~90% |
| friendly = френдлі | 0.5% | Top 50K | "The staff here are very friendly." | ~90% |
| proof = пруф | 1% | Top 50K | "Do you have proof of your address?" | ~80% |
| profit = профіт | 1% | Top 50K | "The shop made a small profit." | ~90% |
| benefit = бенефіт | 3% | Top 20K | "Free lunch is one benefit of this job." | ~70% |
| true = тру | 1% | Top 20K | "Is it true that you are moving?" | ~80% |
| easy = ізі | 1% | Top 20K | "I played the game on easy mode." | ~70% |
| face = фейс | 8% | Top 5000 | "She washed her face with cold water." | ~85% |
| hate = хейт | 3% | Top 20K | "There is so much hate online." | ~40% (noun) |
| sense = сенс | 2% | Top 20K | "Your idea makes sense to me." | ~40% |
| present = презент | 3% | Top 10K | "She gave me a nice birthday present." | ~15–20% (gift) |
| people = піпл | 25% | Top 400 | "Many people come to this park…" | ~100% (compare friend = 95%) |

Abbreviations have a related problem. IT = айті has share 0.2%, apparently counted as part of the pronoun "it". It should be counted on its own, case-sensitive.

**Fix.**
- Re-estimate the share for every card labelled `slang` or `informal`, and for every card with share < 30% whose examples use the main meaning. Do it with the rule above: the register of the Ukrainian word never lowers the share.
- Add a consistency check: the examples, the share and the image must all be about the same meaning.
- Where the card is meant to be about a narrow sense, rewrite the examples to that sense. For light = лайт that means "light beer, light yogurt" only; "This bag is very light" is a different sense.

### 3. Stress and pronunciation, the main learning point for identical words, are missing

I compared the English primary stress (CMUdict) with the Ukrainian stress (Wiktionary) for 444 cards in Top 10K. **259 (58%) have the stress on a different syllable.** A Ukrainian learner reading the English word will stress it the Ukrainian way, and the error becomes a habit.

Examples by band:
- Top 400: season (сезо́н / SEAson), president (президе́нт / PREsident), student (студе́нт / STUdent).
- Top 1000: moment, product, process, project, officer, period, material, model, football, internet, album, minister.
- Top 2000: episode, contract, resource, region, agent, secret, partner, document, interview, candidate, concept, champion, budget, actor, expert, progress, metal, client, contact, festival, parliament, ocean, talent, visit.
- Top 3000–5000: theater, concert, journalist, alcohol, basketball, pilot, medal, character, palace, final, motor, telephone, tourist, calendar, menu, comfort, helicopter, smartphone.

Only about 10 of 740 notes mention pronunciation (DJ, bass, cache, asthma, lieutenant…).

Sounds that Ukrainian speakers carry over:
- h said as г: hotel, hockey, hobby, hamburger.
- th said as т: method, author, theater, athlete.
- w said as в: website, weekend, wow.
- /æ/ in bank, fan, plan, taxi.
- reduced vowels (schwa) in president and computer.

Homographs where the reading must match the card: live (adj /laɪv/), record, present, object, project, contract, progress, protest, export, import, transfer, conflict, contrast, update, upgrade, discount, escort, estimate (noun), delegate (noun).

Audio flagged by the recogniser in the first bands: **photo (Top 1000, heard as "Foul")**, Mrs., hall, sauce, CD, cricket, trader. An A0 word with unclear audio is the worst place for an audio problem.

**Fix.**
- On the front, mark the stressed syllable of the English word from CMUdict. Bold or underline the stressed vowel, or use "PRES·i·dent" style; pick one look.
- Show a small "stress ≠" mark when the English stress differs from the Ukrainian (the data is already in the two sources above).
- Add a 🐢 slow replay button.
- Re-record photo and the other flagged words in the first bands.
- For the homographs listed above, record the word inside a sense phrase ("a live show", "a world record") and cut out the word, so the noun/adjective reading is used. Then check them by ear.
- Add a stress drill to Train (see 8).

### 4. Examples for Top 400 and Top 1000 are not A0–A1 and not practical enough

Measured over all example sentences:

| band | sentences | past tense | questions | start with I / we / you | start with he / she / the |
|---|---|---|---|---|---|
| Top 400 | 44 | 29% | 13% | 27% | 36% |
| Top 1000 | 216 | 37% | 4% | 22% | 45% |
| Top 2000 | 312 | 35% | 5% | 18% | 48% |

Specific problems in the first two bands:
- **Idioms and phrasal verbs:**
  - start: "got off to a good start", "lined up at the start line"
  - party: "throw a party"
  - business: "runs a small business"
  - process: "in the process of moving"
  - control: "under control", "be in control"
- **B1–B2 words:** lottery, blurry, streaming, delivery, checkup, label, press, government.
- **US place names and culture:** Chicago, Boston, the White House, "College is expensive in the US", "Fall is a busy season for farmers".
- **Third-person stories instead of the learner's own sentences:** "The general gave an order."

**Rules for the example generator** (`tools/workflows/examples.js`), Top 400 to Top 1000:
- At most 7 words per sentence.
- Present simple, "to be", have, like, can, imperative, "there is / are". No past tense, no phrasal verbs, no idioms.
- Every other word must be on the A1 list (Cambridge Starters + CEFR-J A1).
- At least 2 of the 4 sentences are things the learner would say: a question or a request in a real situation (shop, street, school, work, phone).
- At least 1 sentence shows the main collocation (take a photo, make a plan, watch a video).
- No proper names except very simple ones (Anna, Kyiv).

For Top 2000–3000, the same rules apply at A2: past tense is allowed, idioms are not. Above Top 5000, the current style is fine.

Suggested rewrites for every Top 400 card:

| card | now (worst sentence) | replace the 4 examples with |
|---|---|---|
| friend | "He made a lot of new friends at school." | This is my friend Anna. / She is my best friend. / Can my friend come too? / I have a lot of friends. |
| people | "Most people in my town are very friendly." | There are many people here. / A table for four people, please. / How many people? / I like these people. |
| business | "He went to Chicago on business." | I have a small business. / Here is my business card. / How is business? / He is here on business. |
| video | "We made a short video for class." | Look at this video! / Can you send me the video? / I watch videos on my phone. / I like this video. |
| season | "Fall is a busy season for farmers." | What is your favorite season? / Summer is my favorite season. / Winter is a cold season. / The new season of the show is out. |
| idea | "It was her idea to go to the beach." | Good idea! / I have an idea. / I have no idea. / Do you have any ideas? |
| president | "The president lives in the White House." | The president is on TV. / Who is the president? / She is the president of the club. / The president is in Kyiv today. |
| student | "She is a student at the local college." | I am a student. / Are you a student? / Is there a student discount? / She is a student at Kyiv University. |
| show | "We saw a great show in New York." | I like this show. / What is your favorite TV show? / The show starts at eight. / Let's watch a show tonight. |
| million | "He won a million dollars in the lottery." | One million people live here. / It costs two million dollars. / A million is a big number. / The city has three million people. |
| fact | "Check the facts before you share the story." | That is a fact. / Is that a fact? / Here is a fun fact. / In fact, I am tired. |

Top 1000 cards that need rewriting first:
- start: all 4 sentences are B1.
- control, process, period: abstract sentences at B1.
- director: also see 5.
- training: "went to a training" contradicts its own note that "training" is uncountable.
- officer, author, leader, minister: past-tense stories.
- photo: "blurry".
- million: "lottery".

### 5. Examples and notes that teach errors or can offend

- **director**: "Our school director gave a speech." This is the Ukrainian "директор школи" carried into English. In English the head of a school is the *principal* (US) or *head teacher* (UK). Replace the sentence and add the note `The head of a school is the "principal" (US) or "head teacher" (UK), not the "director".`
- **gay**: the note says the noun can sound rude, but 3 examples use exactly that form: "He is the first gay to win this award.", "Many gays and lesbians live here.", "The club welcomes gays of all ages." Replace them with adjective uses: "He is gay.", "a gay couple", "gay rights".
- **detective**: the note talks about the Ukrainian word ("In Ukrainian 'детектив' can also mean…"). This breaks the owner's rule. Rewrite it as `A crime novel or film is a "detective story" or "crime novel".`
- **Bare one-word notes** ("Uncountable.", 30+ cards such as cholesterol, recycling, enthusiasm) are too short for A1–A2 learners. Use the template `Uncountable: some rice, a lot of rice (not "a rice", "rices").`
- **Vulgar English words** sit in the learning bands with no filter: bullshit (Top 3000), WTF (Top 5000), plus sexy and joint. Their notes are correct, but see 9.

### 6. Missing grammar that Ukrainian speakers always get wrong

Ukrainian has no articles. It forms plurals with endings, uses different verbs with these nouns (робити фото, писати тест), and uses different prepositions (на фото, в інтернеті, на вечірці). None of this transfers. Today the back of the card shows only "noun".

**Fix.** Replace the "noun" tag on the back with the word's grammar pattern:
- "**a** photo · photos"
- "**an** idea · ideas"
- "**a** baby · bab**ies**"
- "**a** party · part**ies**"
- "**the** internet"
- "rice · *uncountable*"
- "**a** person · **people**"
- "**a** foot · **feet**"

Use "an" for: idea, office, album, author, officer, effect, episode, actor, expert, agent, interview, ocean, hour-type words.

For the Top 3000 nouns where the Ukrainian verb or preposition differs, add one "Say:" line (English only):

| card | Say: | the Ukrainian learner's typical error |
|---|---|---|
| photo | take a photo · in the photo | *make a photo, *on the photo |
| test | take / pass a test | *write a test |
| plan | make a plan | *do a plan |
| goal | score a goal | *hit / beat a goal |
| video | watch a video | *look a video |
| internet | on the internet | *in the internet |
| party | at a party · have a party | *on the party |
| bank / office | at the bank · at the office | *in the bank (possible, but less natural) |
| student | a student at Kyiv University · a second-year student | *student of university · *second course |
| class | in fifth grade (US) / in Year 5 (UK) | *in fifth class |
| course | a second-year student | *on the second course |
| sport | play sports (US) / do sport (UK) | *go in for sport (old textbook English) |
| visit | visit my grandma · pay a visit to | *visit to my grandma |
| role | play a role | — (good: same as грати роль, say so) |
| chance | have a chance · give me a chance | — |

### 7. Pure corpus frequency puts newspaper words first and everyday words late

The wordfreq list includes a lot of news and Wikipedia text. As a result:
- **Early:** president, minister, congress, senate, parliament, democrat, senator, candidate, management, factor and sector are all in Top 2000. 19 of the cards in Top 2000 are B2 or above.
- **Late:** the words a beginner needs on day one come much later: hotel #1029, bar #2570, pizza #3031, menu #3831, sandwich #3922, passport #4926, cafe #4974, taxi #4848, hobby #5482, Wi-Fi #7189, supermarket #6890, zebra #12509. Of the 43 A0 (Starters) cards, only 8 are in the first two bands.

The bands are also very uneven: Top 400 has 11 cards (9 with Hide slang on), Top 1000 has 54, Top 5000 has 224. A learner who starts at "Top 400" is done in two minutes.

**Fix.** These keep the owner's frequency categories:
1. Build the rank from **spoken / subtitle frequency** (SUBTLEX-US, or wordfreq without its news and Wikipedia parts). It still measures how often the word is used, but in everyday English, so taxi, hotel, pizza and menu move up and senate and sector move down.
2. Merge Top 400 into Top 1000 (one first band of about 65 cards), or label the first band "Start · most common".
3. Within a band, group the cards into small topic sets of 8–12: In town (taxi, hotel, bank, park, center, cafe, menu), Tech (computer, internet, video, photo, file, chat), Sport, People and jobs, Food. Topic sets are easier to remember than a mixed list. Do not put near-synonyms side by side, because they interfere with each other.
4. Treat Top 50K, Top 100K and Rare (8,673 cards, 80% of the site, 81% of Top 50K without examples) as a **dictionary**, not a course. No training from them, and no "Examples coming soon" in the grid.

### 8. Training mode does not train anything useful yet

Problems now:
- Ukrainian → English recall for an identical word is trivial (френд → friend).
- The learner grades themselves ("I knew it"), so scores are near 100% without any learning.
- The sample deck is `WORDS.slice(0, 8)`. It ignores Hide slang (the screenshot shows френд) and ignores the selected band.
- There is no spacing over days.

**Fix.** Use short modes that target what an identical word still teaches:
1. **Listen and type**: play the audio, the learner types the English word. This trains the spelling patterns. The first 5 bands contain 56 words with double letters (business, million, office, class, comment, professor, address…), 51 with a silent final e (office, college, site, role, code), 94 with c for [k] (club, doctor, computer), ph (photo, smartphone), th (method, author, theater) and y for [i] (style, type, symptom).
2. **Tap the stress**: show "pres·i·dent" and the learner taps the stressed syllable. Use the 259 stress-differs words first.
3. **Fill the gap**: an example sentence with the word blanked out, for example "Can you take a ___ of us?". This trains the collocation from 6.
4. **a / an and plural**: "___ idea" (a / an); "one baby, two ___".
5. **Which meaning?**: for the cards from problem 1, for example "I like your country" → state or music?
6. **Spaced repetition**: Leitner boxes (1, 3, 7, 21 days) stored in localStorage. "Again" moves the card back to box 1. Show "12 cards due today" on the Train chip.
7. **Sample deck**: the first 10 cards of the current band after the filters.

### 9. The slang filter hides standard words but shows English vulgar words

Of 455 cards in Top 5000, 79 are hidden by Hide slang. Several of them are standard Ukrainian: doctor = доктор, gene = ген, tattoo = тату, email = імейл, software = софтвер, hardware = хардвер, OK = окей, comment = комент, CD = сіді, ID = айді, mama = мама.

At the same time, English vulgar or offensive words are shown to everyone in the learning bands: bullshit (Top 3000), WTF (Top 5000), and idiot, loser and sexy without a filter.

**Fix.**
- Re-check `uk_nonstd` against VESUM tags and СУМ-11. A word with a normal dictionary entry is not slang.
- Add a separate English flag `rude` (vulgar or offensive). Hide those cards by default, show them with a visible "rude" tag, or move them to the end of their band.

### 10. American-only spelling while Ukrainian schools teach British

The cards use American spelling, which is fine as a base. But Ukrainian school textbooks are mostly British, so a learner who sees "center" and "theater" here and "centre" and "theatre" at school will think one of them is wrong.

**Fix.** Add one line to the back: `UK: centre`. It is needed for center, theater, meter, kilometer, humor, tumor and catalog.

Some examples are American in ways a British-taught learner will not recognise: "fall" for autumn, "check" for the bill, "on the weekend", "college", "movies", "soccer". Where the card word is not itself American, prefer neutral wording.

### 11. The image on the back: what to show

From a teaching point of view, the image matters most where the meaning is narrow or easy to misread:
- **Polysemous and minor-meaning cards (problem 1):** the image must show the card's meaning. Examples: country (guitar and cowboy hat, not a map), court (tennis court), top (a woman's top), level (game screen), set (tennis score), shot (a small glass), light (a "light" yogurt label), player (a CD player), general and major (uniform).
- **Concrete nouns in Top 5000** (taxi, hotel, pizza, tiger, passport, computer): images speed up recall, especially for children.
- **Abstract words** (idea, fact, period, method, process, factor): skip the image, or use a simple neutral icon. A forced stock photo teaches nothing.
- **Size and placement:** keep the image small and on the back, above the examples, so the front stays clean (English = Ukrainian).

### 12. Smaller things a learner will notice

- **"About Rare in English"** (Rare band, screenshot `desktop-rare-dark.png`). `rankText()` builds "About " + band name, so the Rare band gets an odd sentence. Show "Rare in English" for that band.
- **Word highlight in examples.** It misses plurals that change the spelling: babies, parties, activities, celebrities, hobbies. It also misses irregular forms: feet, people for person. Add a -y → -ies rule and a small table of irregular forms.
- **Missing examples:** hip-hop (Top 5000), high-end, sci-fi, avant-garde (Top 10K), and pop-up, stand-up, add-on, know-how, déjà vu, foie gras… (Top 20K). Hyphenated and accented words were skipped by the example generator.
- **"Hide slang" is ambiguous.** Learners will read it as English slang. A clearer label is "Hide slang pairs" with a tooltip: "Ukrainian side is slang (піпл)".
- **Bands are labelled by English rank but contain few cards.** Add one line under the chips: "Top 1000 = among the 1,000 most used English words".
- **Translations of examples.** For A0 learners, 4 sentences with no translation can be too much. An optional "tap to translate" under each sentence (hidden by default) keeps the design minimal and helps beginners. If the owner prefers English-only, then the strict A0 rules in 4 are the substitute.

## Top issues in one list

1. **Minor-meaning cards**: add a "Most often X means …" note with an A1 example for the 408 cards with share < 50 and raw rank ≤ 10K, and an image that shows the card's meaning.
2. **Wrong meaning shares for slang pairs**: re-estimate the share for slang and informal pairs (cash, trouble, friendly, proof, profit, true, easy, face, people, sense, present), with the rule that the Ukrainian register never lowers the share. Count IT apart from "it". Make the share, the examples and the image agree.
3. **Stress**: mark the stressed syllable on the front and show a "stress ≠" mark (58% differ, for example PREsident and MOment). Re-record photo and the other flagged words, and record the homographs (live, record, project…) in their card meaning.
4. **Examples for Top 400 and Top 1000**: regenerate them with strict A0–A1 rules (≤ 7 words, present tense, A1 vocabulary, 2 of 4 practical questions or requests, the key collocation, no idioms or US place names). Rewrites for all of Top 400 are in section 4.
5. **Bad examples and notes**: fix "school director" (→ principal / head teacher), the 3 gay examples, the detective note and the bare "Uncountable." notes.
6. **Grammar on the back**: replace the "noun" tag with "a / an word · plural" or "uncountable", and add a "Say:" collocation line where Ukrainian differs (take a photo, on the internet, a student at…, fifth grade).
7. **Frequency source**: rank by spoken / subtitle frequency, merge the tiny first band, group cards into topic sets, and treat Top 50K and beyond as a dictionary.
8. **Training**: replace "френд → ?" with listen-and-type, tap-the-stress, gap-fill, a/an and plural, and which-meaning drills, with Leitner spacing. Make the sample deck respect the band and the filters.
9. **Slang flag**: re-check it (doctor, gene, tattoo, email and software are standard Ukrainian), and add an English "rude" flag for bullshit, WTF and similar words.
10. **British spelling**: show "UK: centre" for center, theater, meter, kilometer, humor, tumor and catalog.
