# Linguist review: the first three bands

Reviewer: applied linguist, teacher of English to Ukrainian speakers.
What I read: all 244 cards in `data/review/cards-a.txt` (70 in Top 1000, 84 in Top 2000, 90 in Top 3000).
For each card I checked the pair, the band, the 4 sentences, the note, the grammar and "Say" lines, the stress mark and the slang flag.
My fixes are in `data/qa/zz-review-a.json` (34 cards). The build merges this file last, so it wins.

## What is good now

- The pairs are clean. I found no false friend and no "similar" pair among the 244 cards.
- Top 1000 is close to the A0–A1 target. The sentences are short and in the present tense.
  More than half are questions or requests a learner would really say: "Can you take a photo of us?", "Where is the bank?"
- Almost every card now has a grammar line ("a photo · photos", "rice · uncountable") and a "Say:" line.
- Many notes target real Ukrainian errors: "take a photo" (not "make"), "groceries" (not "products"),
  "principal" (not "school director"), "a loan" (not "a credit"), "people is" → "people are".
- Cards that show a rare meaning of a common word now say what the word usually means (show, course, party, rock, foot, account).
- The problems from the earlier reviews are fixed: the school-director error, the gay examples, the detective note, US place names.

## What is still going wrong (most important first)

### 1. The default filter hides the most useful beginner words
24 of the 67 Top 1000 cards (35%) are hidden by default.
They include please, hello, sorry, OK, friend, people, good and nice.
A beginner with the default settings never sees "please" or "hello".
The flag is about the Ukrainian word (пліз, хелло are slang), but the English word is as basic as English gets.
Fix: in the learning bands, show these cards with a small "slang" tag on the Ukrainian side. Keep hiding only the rude cards.

### 2. Some cards were in the wrong band
- Phrase frequencies were guesses, and some were far too high.
  "vice president" was set higher than the word "vice" on its own, which is impossible.
  "real-time" was set above "software" and "update". "follow-up" was set as common as "pizza".
  These are B1–C1 words, and they sat next to "lunch" and "weekend".
- The rank counts every form of a word (start, started, starts). The share was estimated for the noun form only.
  For "start", the form "started" alone is two-thirds as common as "start". So the noun is about 10% of uses, not 20%.
- Some Ukrainian words are narrower than the English word:
  - файл is only a computer file. English "file" is also a paper file ("the police have a file on him") and a verb.
  - файт is a bout (boxing, MMA). English "fight" is mostly the verb, a quarrel or a struggle.
  - "cent" is often British "per cent", not the coin.
- I moved 7 cards (table below). Please ask whoever runs the data to repeat the "all forms" check
  for other noun cards whose verb is common. The effect is smaller for offer, show, post and test.

| card | was | now |
|---|---|---|
| start | Top 1000 (#632) | Top 2000 (~1240) |
| fight | Top 1000 (#961) | Top 2000 (~1630) |
| file | Top 1000 (#968) | Top 2000 (~1910) |
| cent | Top 2000 (#1857) | Top 3000 (~2480) |
| vice president | Top 2000 (~1855) | Top 5000 (~3370) |
| real-time | Top 2000 (~1855) | Top 10K (~6950) |
| follow-up | Top 3000 (~2320) | Top 10K (~6300) |

### 3. A few cards look identical but mean less in Ukrainian
- **hey = гей.** The data also has хей, which is what Ukrainians say today.
  The build picks гей because гей ("gay") is a very common Ukrainian word. So the site shows "hey = гей" and "gay = гей".
  Fix: show "hey = хей". This is a one-line change in the build. My file cannot change the Ukrainian side.
- **message = меседж.** In Ukrainian, меседж is mostly "the main idea of a speech". The card is about text messages.
- **class = клас.** Ukrainians say "in fifth class". I added a note: a school year is a "grade" (US) or "year" (UK).
- **college = коледж** (a US college is a university) and **character = характер** (most often a person in a film). Their notes already cover this.
- **start = старт** and **stop = стоп** are at the edge of the 15% rule. I kept them. The Ukrainian word has the same core idea,
  only as another part of speech, so a learner will not misuse them. If you want the rule applied strictly, both go.

### 4. In Top 2000–3000 the sentences are still about other people
- Every card now has at least one question or request. But only about 1 sentence in 3 is a question or request (Top 1000: more than half).
- About 1 sentence in 5 is a past-tense story about someone else: "The senator visited our school.",
  "The telephone rang in the middle of the night.", "Mama cooked dinner for everyone." This is allowed at A2,
  but a learner never says these sentences.
- US-only topics are common in Top 3000: senator, congress, county sheriff, baseball, highway, mall, resume.
  Ukrainian schools teach British English.
- Fix: when examples are regenerated, ask for 2 of 4 sentences in the first person, about a real situation, in these bands too.

### 5. Stress marks
- Two underlines are wrong. The tool takes the first pronunciation in its dictionary:
  "email" is marked em**ai**l (should be **e**mail), and "impact" is marked imp**a**ct (the noun is **i**mpact).
- 16 words with two or more syllables have no underline. Seven of them are words where Ukrainian puts the stress elsewhere,
  so they matter most: period, material, theater, management, champion, baseball, idiot.

### 6. Smaller things
- Some "Say:" lines show phrases that are the same in Ukrainian (watch a film, play football). The line teaches most
  when it shows the phrase Ukrainians get wrong. Examples I added: "make sense", "make a profit", "Cash or card?", "this season" (not "in this season").
- "photo" is tagged "informal". It is a neutral word. This tag is outside the fields I can change.

## What I changed (34 cards)

- **Examples rewritten: 18 cards.** In Top 1000: easy, face, trouble (past tense, 8–10 words), chance ("This is a good chance" is copied word for word from Ukrainian),
  video ("I watch a video on my phone" → "videos"), partner, model. In Top 2000–3000: fight, gay, task, impact, port, camp,
  character, friendly, focus, service, football (no question, too long or too short).
- **Band corrections: 7 cards** (the table in section 2): 4 by meaning share, 3 by phrase frequency.
- **Notes: 7** (class, fight, file, cent, focus, internet, mama).
  For example, the internet note said always use "the", but two sentences say "Do you have internet?". The new note explains both.
- **"Say:" lines: 11. Grammar lines: 3** (cash, proof, profit: learners say "a proof", "get a profit").
- **Slang flag: 2 cards now shown by default.** lunch = ланч is the normal menu word (бізнес-ланч). ID = айді is treated the same as IT = айті.
- **Removed: 0.**

Result: Top 1000 has no past tense and no sentence over 7 words. Every Top 2000–3000 card has a question or request.
No note is over 110 characters, and no note talks about the Ukrainian word.

## Five next steps for the product as a learning tool

1. **A real first lesson.** Start beginners with a "Start here" set of about 60 everyday words a tourist needs on day one
   (taxi, hotel, menu, pizza, bank, photo, video, doctor, OK, please, sorry, hello). Group them in small topic sets of 8–12
   (In town, Food, Phone and internet, People). Frequency bands are good for a dictionary, not for lesson one.
2. **Show slang pairs with a tag instead of hiding them** (see 1 above). "please = пліз (slang)" teaches more than an empty slot.
3. **Practice what identical words still hide.** The meaning is already known, so practise these instead:
   - tap the stressed syllable (PREsident, THEater);
   - listen and type (spelling: business, photo, theater);
   - fill the gap with the "Say:" phrase ("Can you ___ a photo of us?");
   - pick a / an and the plural;
   - "which meaning?" for cards with a narrow meaning (class, file, college).
   Repeat the practice over days (spaced repetition).
4. **Audio for the example sentences**, at least for the questions. Learners need to hear the stress inside a sentence
   ("Is the hotel easy to find?"), not only the single word.
5. **Use the product's best idea as motivation:** "You already know 240 of the 3,000 most used English words." Add a 2-minute check at the start,
   and a counter that grows. For a Ukrainian beginner, seeing how much English they already know is the strongest reason to continue.
