# Simple sentences, natural words, pictures

*12–13 November 2026. The teacher's verdict on the first cloud site, what the analysis showed, and what changed.*

## The verdict

- "Say it" is not practical. The words and the structures are far above people who came to learn these very simple words. Use very, very simple sentences.
- How natural will people sound when they use these words? Where the English word is used much less, put a "rare" note right at the word.
- Find the best picture for every word. The pictures must look nice.
- Analyze what else to add, and start adding it.

## What the analysis showed

| | Before | Now |
|---|---|---|
| Words in a "Say it" sentence | 5.6 on average, up to 10 | 4.0 on average, 6 at most |
| Words in a dialogue sentence | 4.2 on average, up to 10 | 2.9 on average, 6 at most |
| Other words the sentences needed (not words of the clouds) | 304: can, can't, do, does, did, forgot, gave, getting, enough, expensive… | 45, and all of them are on one list |
| Words marked as rare in English | none | 97 of 1,913 |
| Words with a picture | none (only one emoji per cloud) | all 1,913 |
| Words with the stress marked | 812 | 1,496 |

The first version taught known words inside sentences the learner could not build: *Can I have the sauce on the side? I reserved a table for seven o'clock. When will I get the test results?* The word was free, but the sentence cost more than the word saved.

## 1. Very simple sentences

Every sentence now follows one rule, and the build checks it (`tools/build_clouds.py` stops on any other word and on any sentence longer than six words):

**a sentence = the little words + words of the clouds.**

The little words are in `data/clouds/kit.txt`: 68 of them (I, you, he, she, it, we, they; am, is, are; a, the, this, my, your; have, need, want, like; where, what, who; yes, no, not, and, or; please, thank you, sorry, hello; here, there, in, on, at, to, from, with, for; good, bad, big, small, new, old, very; now, today; one to ten). There are no past forms, no "can", no "do" questions and no short forms.

That gives ten sentence shapes, and they work with every word of the site:

| Shape | Example |
|---|---|
| X, please. | A latte, please. |
| This is X. | This is my passport. |
| I am X. / He is X. | I am a tourist. |
| I have X. | I have a visa. |
| I need X. | I need a doctor. |
| I want X. | I want a pizza. |
| I like X. | I like jazz. |
| Where is X? | Where is the bank? |
| X is here / in… / good. | The bank is in the center. |
| No X. / It is not X. | No ketchup, please. |

The verb clouds add the plain verb: *I plan. We organize a conference. Click here.*

All 412 phrases, 132 dialogue lines and 80 "Change one word" frames were rewritten, read once more as an editor would, and recorded again.

## 2. How natural the words sound

A twin is easy to learn, but it is not always the word an English speaker uses. Three things were checked for each of the 1,913 words.

**How.** For every pair, how often the English word is used and how often the Ukrainian word is used (wordfreq). Ukrainian has many endings, so its numbers run lower; the comparison takes that into account. That gave 250 candidates: pairs where the English word is used much less than the Ukrainian one, and English words that are rare in general. Each candidate was then decided by hand, and the main lists were read in full for words that are common but have a more usual partner (telephone → phone).

**Result.**

| | Words | Examples |
|---|---|---|
| The word people use | 1,770 | taxi, menu, bank, doctor, problem |
| Rare, and people usually say something else | 89 | barman → bartender, telephone → phone, cinema → movie theater, pensioner → retiree, motor → engine, rucksack → backpack, excursion → tour, prognosis → forecast, cosmonaut → astronaut |
| Rare, with no other word | 8 | trolleybus, kvass, kefir, borscht, halva, funicular, steppe, brr |
| Fine, with a tip | 46 | toilet (in the US: bathroom, restroom), center (downtown), client (customer in a shop), guarantee (warranty), temperature (fever) |

**On the page.** A rare word has a small "rare" tag on its chip. A tap says the word and shows, in Ukrainian, what people usually say. Search shows the same tag; for the words outside the clouds the tag means the English word is outside the 50,000 most used.

**In the lists.** Rare words left the main 16 where a common word could take the place (barman, boiler, corridor, parquet, pullover, motor, medic, pensioner, trainer, premier, bandit and others moved to "more words"). A few stay in the main list on purpose, because they lead to the everyday word: telephone → phone, television → TV, cola → a Coke, cinema → movie theater. One wrong friend was removed (adequate ≠ адекватний) and became a "Careful" card.

Some notes depend on the situation: *tariff* is the right word in the news (import tariffs), but a phone tariff is a *plan*; *organism* is right in science, but "my organism" is *my body*.

The decisions are in `data/clouds/words/*.txt`, one line per word, and can be edited by hand.

## 3. Where the stress falls

The most common reason a known word is not understood is the stress: меню́ but **ME**nu, шокола́д but **CHO**colate, сала́т but **SA**lad.

- The stressed vowel is now underlined on 1,496 words (all words of more than one syllable where the spelling allows it), taken from the pronunciation the recording uses (`tools/compute_cloud_stress.py`).
- In 668 words the stress is on another syllable than in the Ukrainian word. There the underline is pink, and a tap shows both words: *menu = меню́ · наголос інший*. The Ukrainian stress comes from the Ukrainian Wiktionary.

## 4. Pictures

- The pictures are Fluent Emoji 3D (Microsoft, MIT license): one style for the whole site, clear at the size of a word chip.
- The picture of each word was chosen by hand (`data/clouds/words/*.txt`), 917 different pictures in all.
- For about 300 words the picture is the thing itself (pizza, taxi, tiger, guitar, the flag of a country). For the others it is the closest thing or a symbol (idea 💡, risk ⚠️, strategy ♟️), because the word is abstract. Where several words are one thing (four kinds of coffee, three burgers) they share a picture.
- Each cloud has one picture sheet (`pictures/cloud-<id>.webp`, 50–230 KB), loaded when the cloud opens. Pictures are on the word chips, on the "Say it" cards and in the list of clouds.

Photos would show the difference between a latte and an espresso, but at the size of a chip a photo is unclear, and there was no checked source of 1,900 photos here.

## 5. What was added

- **Two start clouds.** "Start: this is, I am" and "Start: I have, I like" teach the little words with 16 words everybody knows, so the first sentence comes in the first minute: *A taxi, please.*
- **Little words.** One page with all the little words, their Ukrainian meaning and sound.
- **Look and say.** A new step after the words: pictures only. The student says the word, then taps the picture to check and hear it. It appears in the 49 clouds that have at least four pictures of the thing itself.
- **Countries and cities.** A new cloud (43 names) for the sentence every student needs: *I am from Ukraine.*
- **Stress marks** for all words, and the pink mark where the stress moves (section 3).

## Still open

- A second reader for the rare notes and the new sentences. The notes follow American English; a British reader would mark some differently (cinema, tram, reception).
- The list of little words is strict on purpose. The next words to consider are *can*, *do / don't* and *go*: they open many natural sentences (*Can I pay by card? I don't know.*), and the teacher can decide when to add them.
- For abstract words the picture is a symbol. A teacher who has a better picture for a word can change one line in `data/clouds/words/*.txt` and rebuild.
- From the earlier list: an independent check of the new pairs, the familiar words that are in no cloud yet, extra clouds for a student's own job.
