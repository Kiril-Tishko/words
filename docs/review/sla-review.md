# SLA review: what a student gains on the first visit

*Same Words · Однакові слова. Reviewer: professor of applied linguistics and second-language acquisition (vocabulary learning for Ukrainian speakers). 10 November 2026.*

**What I looked at.** The site as built at 02:45 UTC on 10 November (`site/app.html`, 1,009 lines), at phone size (390×844) and desktop size (1280×800): the first screen, level A0, lesson a0-01, all three practice modes, the end screen, a return visit with words due, Words and Exclamations. I used it with empty storage, as a new student would. The site changed while I worked: spaced review (`sw.srs`), the Say it / Listen / Type it modes, a "Next lesson" button and List view on phones arrived between 02:36 and 02:45. This review starts from that build.

There are no accounts, so "log in" means "open the site". Progress lives in this browser's localStorage.

## The main point

For a Ukrainian speaker, the meaning of these words is free. Cognates are learned faster and forgotten more slowly than other words (de Groot & Keijzer 2000), but only the meaning comes free. The English form still has to be learned:
- where the stress goes
- how the vowels sound
- how the word is spelled
- which words go with it ("take a photo")

So in the first minutes the site should do two things: let the student *feel* how much they already know, and then spend every minute after that on the form.

Two facts from the data should shape the design:
- **Stress is the biggest trap, and "first syllable" is the best rule.**
  - The earlier teacher review compared 444 frequent cards with Ukrainian stress. In 58% of them the stressed syllable is different: студЕнт → STUdent, момЕнт → MOment, інтернЕт → INternet, таксІ → TAXi. So the Ukrainian instinct is right less than half the time.
  - In the card data, 80% of the 710 stress-marked Top-10K words take the stress on the first syllable. "Stress the first syllable" is right 8 times in 10.
- **A correction to the brief.** comPUter / комп'Ютер and hoTEL / готЕль have the stress on the same syllable, and the site underlines them correctly. Their traps are the vowels and one consonant:
  - computer is [kəmˈpjuːtər]: the first o is weak, and -er is a weak [ər], not a full Ukrainian «ер».
  - hotel starts with [hoʊ], and English h is a breath, not the voiced Ukrainian г [ɦ].

  A stress drill built on "HOtel" would teach an error.

## (a) Diagnosis: what keeps a student from gaining value today

1. **The first screen asks for a choice, in English, and proves nothing.**
   - The headline "English words you already know" and a four-line lead are in English only. On a phone even "Однакові слова" is hidden (`.brand span` is hidden under 560 px).
   - Then come one button, "Start: My family photo · A0", and six level tiles that a beginner cannot place themselves on.
   - Nothing plays, so the headline is never shown to be true for this visitor.
2. **"Start" leads to children's words, not the most useful ones.**
   - A0 comes from a young learners' list. Lesson 1 is photo, people, cousin, friend, Miss, baby, face. Four of these are slang pairs: піпл, френд, бебі, фейс.
   - A0 goes on to zebra, kiwi, badminton and skateboarding, all Top 20K.
   - Hello, OK and sorry are in no lesson and in no Exclamations set. President, message and process wait until B1.
   - The course is upside down: A0 has 6 lessons and 38 words, B2 has 156 lessons and 1,278 words.
3. **A beginner cannot find hello.**
   - "Hide slang" is on by default and hides every pair whose Ukrainian side is colloquial.
   - On the live Words page, "hello" finds only "phellogen", "OK" opens on "okra", and "sorry" and "please" find nothing.
   - Yet these are the clearest proof that the student already knows English, and the most useful words a beginner can have.
4. **Practice mostly checks what the student already knows, and the student marks it.**
   - The default mode, Say it, shows "френд = ?", then "Show English", then "I knew it". Listen plays the word and again asks the student to mark themselves.
   - Only Type it checks an answer, and no mode asks for the stress.
   - These self-marks now feed the review boxes. A word also moves up a box every time it is answered right, even on the same day: six "Practice again" runs in one evening schedule a word for 60 days.
5. **The sound is on the card, but it is not taught.**
   - The stress mark is a thin 2 px underline, and 🔊 is a small grey icon in the corner.
   - "=" tells the student the word is the same, which invites the Ukrainian pronunciation.
   - Only the single word is recorded. The word partners ("take a photo"), the examples and the stories have no sound.
6. **The best teaching sits at the bottom of the card, in English.**
   - 115 of the 1,001 Top-10K cards already have a "not …" note, most of them aimed at a typical Ukrainian error: "Say 'take a photo', not 'make a photo'", "two million dollars, not two millions", "Food from a store is 'groceries', not 'products'". 456 cards have "Say:" word partners.
   - The note comes last on the back, and none of it comes up in practice.
   - In Grid and One by one, a card without a picture opens its back with an empty grey box. The photo card has no picture.
7. **The A0 story is not yet readable for a true beginner.**
   - "Max, look at my photo. Six people are in it…" has 37 words. Only the 7 highlighted ones have help, and there is no audio.
   - A beginner who knows only the highlighted words and the names knows about a third of the text. Reading with understanding needs about 95–98% known words (Laufer 1989; Hu & Nation 2000).
8. **Nothing warns against false friends.**
   - The message "same words" teaches students to trust every look-alike.
   - The repo's own list of 378 false friends never reaches the site (`data/false_friends.json`: list ≠ лист, data ≠ дата, magazine ≠ магазин, actual ≠ актуальний, accurate ≠ акуратний).
   - "Almost the same" still shows partial false friends with "≈": letter = літера (a letter is usually лист), number = номер, sort = сорт.

## What a student should get

| When | What the student should get | What happens today |
|---|---|---|
| First 10 seconds | Proof, in Ukrainian and by ear, that they know these words, plus one surprise: інтернЕт is INternet. | An English headline, a lesson-title button, six level tiles. |
| First 5 minutes | 12 of the most frequent words heard, stressed, spelled and used in a phrase, each with feedback. One rule to keep ("first syllable"). A reason to come back tomorrow. | The lesson 1 story (cousin, Miss, baby), then "I knew it". |
| First week | 5 minutes a day: due words first, then 8 new ones in frequency order. By day 7: about 60 of the 67 Top-1000 cards practised and said with English stress, a "words I can say" count, a few stories read with words they now know. | A Review button and "Next lesson" now exist. New words still come in children's-list order, and progress counts lessons and every word touched. |

## (b) Changes, ranked

Effort: S = under a day, M = one to three days, L = longer. Unless a change says otherwise, everything is plain JS in `site/app.html`, uses localStorage only, and uses data the cards already have.

### 1. A first screen in Ukrainian that proves the claim in 10 seconds (S)
- **The student sees and does:**
  - A Ukrainian headline and one line, with English under them (wording in section c).
  - Three word buttons: інтернЕт → INternet, студЕнт → STUdent, таксІ → TAXi. A tap plays the recording and lights up the stressed letters.
  - One large button: «Почати · 5 хвилин / Start · 5 minutes».
  - Levels and collections move below, under «Обрати рівень / Choose a level».
- **Why:** an early success raises the student's expectation of success, and that expectation keeps beginners going (Dörnyei 2001). Across two alphabets, cognates connect mainly through sound, so the link has to be heard, not just printed.
- **Build:**
  - In `viewLearn()`, when `Object.keys(srs).length === 0 && done.size === 0`, render a hero block instead of the current h1 and lead.
  - The word buttons carry `data-sayid="internet|інтернет"` and so on, so the existing click handler plays them through `playWord()`. This first tap also unlocks audio on iOS.
  - Preload audio bundles 0–2 (about 0.74 MB each), so the first tap plays at once.
  - Delete `.brand span { display: none; }` from the 560 px rule, so "Однакові слова" shows on phones.
  - The big button opens `#start` (change 2).

### 2. «Перші 5 хвилин»: a ready first session with no choices (M)
- **The student sees and does:** `#start` runs one fixed session of 12 frequent words, one item per screen, about 25 taps. The words are hello, OK, sorry, photo, computer, hotel, idea, student, moment, internet, president and million.
  1. *Listen and pick* (12 items). The word plays, and the student taps its Ukrainian twin from three. Nearly everyone gets these right, fast; that is the point.
  2. *Find the stress* (6 items):
     - student, moment, internet, president, million and computer are split into vowel groups (STU · dent). The student taps the stressed one, then hears it.
     - Feedback: «Українською — студЕнт. Англійською — STUdent.»
     - For computer: "Same stress here, but the first o is weak: kəm-PYOO-tər."
     - After the last item comes the "first syllable" rule.
  3. *Missing letters* (3 items). The student hears the word and types the gap: __oto (ph), _omputer (c), he__o (ll).
  4. *Word partners* (3 items): "Can you ___ a photo of us?" take / make; "two ___ dollars" million / millions; "I have ___ idea" an / a.
  - The end screen: «12 слів у вашому списку. Завтра — 2 хвилини повторення.»
  - One last card: «Обережно: magazine — це журнал, а не магазин.»
  - Two buttons: «Ще 5 хвилин» (the next 8 Top-1000 words) and «Прочитати історію» (the lesson that holds most of these words).
- **Why:**
  - Retrieval with immediate feedback builds memory far better than looking at the pair (Roediger & Karpicke 2006).
  - When the meaning is already known, the effort should go to the form (Barcroft 2002).
  - Hearing before reading keeps students from reading English letters with Ukrainian values (Bassetti 2008).
- **Build:**
  - A `viewStart()` route with a hard-coded list of the 12 ids, the Ukrainian stress for the 6 stress words, and the 3 partner items written from the cards' own `say` and `note` (photo, million, idea).
  - The steps reuse the `.train` layout.
  - Vowel groups come from `/[aeiouy]+/g` on `w.en`, the rule `tools/compute_stress.py` uses. The right group is the one that contains `w.st[0]`.
  - The distractors in step 1 are other words of the session.
  - Each word's first answer calls `grade(w, ok)`, so all 12 come back tomorrow.
  - Set `sw.started = 1`, so the first screen switches to the return view.

### 3. One daily session: due words first, then 8 new ones in frequency order (M)
- **The student sees and does:**
  - At the top of Learn there is one block, «Сьогодні: повторити 9 слів і вивчити 8 нових · ≈5 хв», with one button.
  - Due words come first. Then come the next 8 cards by rank (Top 1000, then Top 2000, then Top 3000), in the checked formats of change 4.
  - The end screen says when the words come back. It offers «Історія дня»: the course lesson that holds most of today's words, read after they are known.
- **Why:** spacing retrieval over days is the most reliable memory effect we know (Cepeda et al. 2006; Nakata 2015 for second-language words). Frequency order gives the most understanding per word learned (Nation 2013).
- **Build:**
  - The store is already there: `sw.srs`, `grade()`, `dueIds()` and `startReview()`.
  - Add `startDaily()`: take `dueIds()` capped at 20, then add `WORDS.filter(w => !srs[w.id] && !w.rude && TOP3.has(w.band)).sort((a, b) => a.rank - b.rank).slice(0, 8)`, with `const TOP3 = new Set(['top-1000', 'top-2000', 'top-3000'])`. Keep the colloquial pairs in this list.
  - Story of the day: count today's words in each `C().lessons[i].words` and pick the highest.
  - In `continueHTML()`, replace the two buttons with this block, and keep «Продовжити урок» as a link.
  - Fix `grade()` so that a word moves up only when it is due: `if (ok && srs[w.id] && srs[w.id][1] > today()) return;`. A miss can still move it down.

### 4. Practice that checks the form and asks for the stress (M)
- **The student sees and does:**
  - New words no longer ask "I knew it?". Each word gets three checked formats in turn:
    - hear and type: nothing on screen but 🔊, and the student types the word
    - tap the stress
    - type from the Ukrainian, as now
  - Feedback marks the first wrong letter and plays the word.
  - "Say it" stays, as a step before the check: «Скажіть уголос, потім перевірте».
  - An optional «🎙 Запишіть себе» plays the student's voice right after the model. Nothing is stored.
  - A lesson counts as learned when its words have been answered right on two different days. "Mark as learned" goes.
- **Why:**
  - Recalling the form builds the productive knowledge that recognition does not (Webb 2009; Laufer & Goldstein 2004).
  - Learners who mark themselves overrate what they know (Koriat & Bjork 2005).
  - Saying a word aloud helps it stick (MacLeod et al. 2010).
- **Build:**
  - In `viewPractice()`, pick the mode for each item instead of one `state.pmode` for the whole session: `stress` when `w.st`, `listen-type` when `canPlay(w)`, else `type`. Keep the switch for students who want one mode.
  - Hear-and-type reuses `checkTyped()` with the word hidden.
  - Stress uses the vowel groups from change 2.
  - Checked answers call `grade()` as now. A self-mark can lift a word no higher than box 2.
  - Letter feedback: compare the `fold()`ed strings and wrap the first difference in `<mark>`.
  - Recording: `MediaRecorder` with an object URL, never saved.

### 5. Put the sound first on every card (S)
- **The student sees and does:**
  - The stressed letters are bold and coloured, not a thin underline.
  - 🔊 is a clear button beside the word.
  - A lesson gets «▶ Послухати всі / Play all».
  - On 58 frequent cards whose Ukrainian twin is stressed elsewhere, a small line appears under the Ukrainian word: «укр. президЕнт · англ. PREsident».
  - On the back, a 🔊 next to "Say:" reads the phrase, such as "take a photo".
- **Why:** making a form stand out helps learners notice it (Sharwood Smith 1993). Explicit pronunciation teaching works, and works especially well for stress (Lee, Jang & Plonsky 2015).
- **Build:**
  - CSS: `.st { font-weight: 700; color: var(--accent); }`.
  - Play all: chain `playWord()` with `setTimeout((w.au[2] + 0.35) * 1000)`.
  - The 58-word list is in the appendix, ready to paste as `UK_STRESS`. Render it in `cardHTML()` and `rowHTML()`.
  - The phrase button calls the existing `speak()`, which uses the browser's voice. Hide it when `speechSynthesis.getVoices()` has no English voice.

### 6. Teach the word partners and the "not …" warnings (M)
- **The student sees and does:**
  - On cards with a "not …" note, the note moves to the top of the back and of the opened row, marked ⚠. "Say:" comes next.
  - In practice and in the daily session, these words get one gap item made from the card's own examples: "Can you ___ a photo of us?" take / make / do.
- **Why:** contrasting the English phrase with the Ukrainian habit (зробити фото → *make a photo) teaches collocations better than practice without the contrast (Laufer & Girsai 2008). Phrases learned whole come out fluently (Boers & Lindstromberg 2009).
- **Build:**
  - The data is on the cards: `DET[id].say` on 456 Top-10K cards, and a "not …" `note` on 115. Of those notes, 97 quote the wrong form, for example `not "make a photo"`.
  - Gap item: pick an example from `DET[id].ex` that contains the `say` phrase, and blank the partner word. Take the wrong option from the note with `/not "([^"]+)"/`.
  - In `backHTML()` and `detailHTML()`, put `.note` before the examples when it matches `/\bnot\b/`.

### 7. Ukrainian for the instructions, English for the words (S)
- **The student sees and does:** buttons, hints and feedback are in Ukrainian with English beside them, or behind a «УКР / ENG» switch: «Тренувати», «Показати англійською», «Знаю», «Ще раз», «Наступний урок →». Words, stories and examples stay in English.
- **Why:** a beginner's attention should go to the English word, not to the interface. The first language is the right tool for instructions at A0–A2 (Cook 2001).
- **Build:**
  - One `T` object with about 60 strings, and `sw.lang` with `'uk'` as the default. Replace the string literals in the view functions.
  - Ukrainian plurals need three forms (1 слово, 2 слова, 5 слів). Write a `pluralUk(n, ['слово', 'слова', 'слів'])` next to `plural()`.

### 8. Count progress in words the student can say, and in days (S)
- **The student sees and does:**
  - Under the daily block: «Ви вже вмієте сказати 47 слів · 4 дні цього тижня ●●●●○○○».
  - Level tiles add «42 / 152 частих слів».
- **Why:** visible, honest progress toward a near goal keeps effort up (Dörnyei 2001). Today's "7 words practiced" counts every word touched, misses included.
- **Build:**
  - Count `Object.values(srs).filter(([box]) => box >= 2).length`. Once the `grade()` fix in change 3 is in, box 2 means right on two separate days.
  - Days: push `today()` into `sw.days` at the end of each session, and draw the last 7.

### 9. Stories with sound, read after the words (S)
- **The student sees and does:**
  - «▶ Слухати історію» reads the story one sentence at a time and highlights each sentence.
  - Tapping a highlighted word opens a small bubble in place (photo = фото 🔊) instead of scrolling down to the card.
  - In A0–A1 the lesson opens with the words, and the story follows as «Тепер прочитайте».
- **Why:** reading while listening helps beginners connect spelling to sound and pick up words (Brown, Waring & Donkaewbua 2008). A story is readable only when nearly all its words are known (Hu & Nation 2000).
- **Build:**
  - Split `l.story` on sentence ends and strip the `[[…]]` marks.
  - Read each sentence with `speechSynthesis`. Its `onend` starts the next sentence and moves the highlight.
  - Build the bubble in `storyWord()` instead of calling `scrollIntoView()`.
  - In `viewLesson()`, put `#cards` before `.story` when `l.level` is A0 or A1.

### 10. Let beginners find hello, with fewer controls on a phone (S)
- **The student sees and does:**
  - "hello", "OK", "sorry" and "please" turn up in search.
  - "Hide slang" hides rude words and the slang pairs outside the top 2000.
  - On a phone, the three menus and the checkbox fold into one «Фільтри» button, so the list starts on the first screen.
- **Why:** frequency, not register, should decide what a beginner sees (Nation 2013). The pairs окей, сорі and пліз are the clearest proof that the student already knows English. The linguist made the same point (PROGRESS.md).
- **Build:**
  - In `wordsBase()`, change the Hide slang filter to `l = l.filter(w => !w.rude && (!w.ns || w.band === 'top-1000' || w.band === 'top-2000'))`.
  - If a search finds nothing visible but something hidden, show the hidden result with a note.
  - On narrow screens, put the filters in a `<details>`.

### 11. «Обережно»: the 25 false friends that matter (S)
- **The student sees and does:**
  - A collection under Learn, «Обережно: схожі, але інші / Careful: look-alike, different». It includes list ≠ лист, data ≠ дата, magazine ≠ магазин, actual ≠ актуальний, accurate ≠ акуратний, fabric ≠ фабрика, artist ≠ артист, piece ≠ п'єса, step ≠ степ, personal ≠ персонал, and others.
  - One closes the first session, and one appears in each daily session as a "which is right?" item.
- **Why:** a strategy that works 9 times in 10 gets overused. A short list of the exceptions keeps the "same word" strategy safe.
- **Build:** copy about 25 entries with their notes from `data/false_friends.json` into a `FALSE` array in app.html, because the site's files do not include them today. Show each as a card with the note on the front.

### 12. "Almost the same" taught as rules, after a check (M)
- **The student sees and does:**
  - Three rule cards under Learn, each opening a frequency-ordered session:
    - «-ція = -tion»: information, situation, station, position (83 Top-10K words)
    - «-ія = -y»: story, company, history, energy (53)
    - «-ний = -al / -ic»: real, special, national, local (88)
  - Each card starts with the rule and three examples, then gives 10 words.
- **Why:** one taught correspondence lets a student recognise and spell hundreds of words they have never seen (Nagy et al. 1993; Lubliner & Hiebert 2011). The set has 56 Top-1000 words, almost as many as the main set's 67.
- **Build:**
  - Call `loadSimilar()`, then filter `SIM` with `/ція$/` + `/tion$/`, `/ія$/` + `/y$/` and `/ний$/` + `/(al|ic)$/`, sorted by `rank`.
  - These entries have no recording, stress mark or examples, so they use `speak()` and the typed formats.
  - Before featuring them, have a linguist read the top 300 and note or move the partial false friends (letter, number, sort).

## (c) First screen copy

Here the stressed vowel is written as a capital letter. On screen, make it bold and coloured.

**First visit**

| Element | Ukrainian | English |
|---|---|---|
| Headline | **Ви вже знаєте тисячі англійських слів** | You already know thousands of English words |
| One line | Таксі, готель, інтернет — ті самі слова. Тепер навчіться вимовляти їх по-англійськи: 5 хвилин на день. | Taxi, hotel, internet: the same words. Now learn to say them the English way, 5 minutes a day. |
| Sound demo label | Послухайте, де наголос: | Listen for the stress: |
| Sound demo buttons | [ інтернЕт → INternet 🔊 ] [ студЕнт → STUdent 🔊 ] [ таксІ → TAXi 🔊 ] | (the same buttons) |
| After the first tap | Чуєте? В англійській наголос часто на першому складі. | Hear it? In English the stress is often on the first syllable. |
| Main button | **Почати · 5 хвилин** | Start · 5 minutes |
| Under the button, small | Без реєстрації. Прогрес зберігається в цьому браузері. | No sign-up. Your progress is saved in this browser. |
| Links | Обрати рівень · Усі 13 147 слів | Choose a level · All 13,147 words |

**Return visit**

| Element | Ukrainian | English |
|---|---|---|
| Headline | **З поверненням!** | Welcome back! |
| One line | Сьогодні: повторити 9 слів і вивчити 8 нових. Близько 5 хвилин. | Today: review 9 words and learn 8 new ones. About 5 minutes. |
| Main button | **Продовжити** | Continue |
| Progress line | Ви вже вмієте сказати 47 слів · 4 дні цього тижня | You can already say 47 words · 4 days this week |
| When nothing is due | На сьогодні все. Наступне повторення — завтра. | That's all for today. Next review: tomorrow. |
| Button when nothing is due | **Ще 5 хвилин** | 5 more minutes |

**Inside the first session**

| Screen | Ukrainian | English |
|---|---|---|
| Step 1 | Послухайте й оберіть слово | Listen and pick the word |
| Step 2 | Де наголос? Торкніться наголошеного складу | Where is the stress? Tap the stressed syllable |
| Step 2, feedback | Українською — студЕнт. Англійською — STUdent. | In Ukrainian: студЕнт. In English: STUdent. |
| Step 2, rule | Не впевнені? Ставте наголос на перший склад — так у 8 з 10 частих слів цього сайту. | Not sure? Stress the first syllable: that is right for 8 in 10 common words on this site. |
| Step 3 | Послухайте й допишіть літери | Listen and fill in the letters |
| Step 3, feedback | ph читається як ф: photo, phone. | ph sounds like ф: photo, phone. |
| Step 4 | Яке слово підходить? | Which word fits? |
| Step 4, feedback | Англійці фото не «роблять», а «беруть»: take a photo. | In English you don't "make" a photo, you "take" one. |
| End | Готово! 12 слів у вашому списку. Завтра — 2 хвилини повторення, і вони ваші. | Done! 12 words are on your list. Two minutes of review tomorrow, and they're yours. |
| Last card | Обережно: magazine — це журнал, а не магазин. Схожі слова інколи обманюють. | Careful: magazine means журнал, not магазин. Look-alikes sometimes lie. |
| Buttons | Ще 5 хвилин · Прочитати історію | 5 more minutes · Read a story |

## (d) What to remove or hide for a beginner

- **The six level tiles and the collections on a first visit.** Move them below the fold, under «Обрати рівень». "A0 Starter … C1 Advanced" is a choice a beginner cannot make.
- **"Mark as learned".** Remove it. It lets a student skip the practice; a lesson is learned when its words come back right on a later day.
- **The Say it / Listen / Type it switch.** Once the session picks the format for each word (change 4), hide it behind a small «Як тренуватися?» link.
- **The Grid / One by one / List switch inside lessons.** Hide it. List on phones and Grid on desktop are good defaults.
- **The empty grey picture box** on the back of cards without a picture. Remove it; the photo card opens with an empty frame.
- **"#727 most used word".** Replace it with a plain label («Щоденне слово · Топ 1000»), or hide it in A0–A2. A rank number means nothing to a learner.
- **The "anglicism" and "★ English too" badges in A0–A2 lessons.** Hide them there. For a beginner they are trivia, and "anglicism" next to people = піпл can read as "this is wrong". Keep them in Words and in the collections.
- **Exclamations as a path for beginners.** Keep it as a fun collection, but feh, fie, achtung, bazinga and inshallah do not belong in week one. Hello, OK, sorry, please, stop and wow belong in the daily path.
- **The rare bands**: Top 20K and below, 12,146 of the 13,147 cards. Offer them through search only. "13,147" is a good number for the headline, but it is not a list for a beginner to scroll.
- **English-only hints** such as "Tap a highlighted word to hear it and see its card". Say them in Ukrainian.

## Later: steps that need new data (outside app.html)

- A Ukrainian stress field for every card, so the stress contrast covers all cards and not only the 58 below.
- A0–A1 regrouped so they hold the Top-1000 and Top-2000 cards (hello, OK, sorry, student, president) instead of zebra and badminton.
- Recordings for the "Say:" phrases and for the "Almost the same" set.
- A Ukrainian line for each sentence of the A0–A1 stories.

## Appendix: Ukrainian stress for 58 frequent cards

I checked each pair by hand against the card data: in every pair, the English stress mark is on a different syllable from the Ukrainian stress. A capital letter marks the stressed vowel. The keys are the cards' `en` values.

```js
// Frequent cards whose Ukrainian twin is stressed on another syllable (Top 1000 → Top 10K).
const UK_STRESS = {
  student: 'студЕнт', moment: 'момЕнт', president: 'президЕнт', season: 'сезОн', million: 'мільйОн',
  process: 'процЕс', secret: 'секрЕт', agent: 'агЕнт', model: 'модЕль', partner: 'партнЕр',
  internet: 'інтернЕт', product: 'продУкт', project: 'проЄкт', contract: 'контрАкт', officer: 'офіцЕр',
  material: 'матеріАл', football: 'футбОл', album: 'альбОм', minister: 'мінІстр', episode: 'епізОд',
  client: 'кліЄнт', actor: 'актОр', document: 'докумЕнт', metal: 'метАл', talent: 'талАнт',
  visit: 'візИт', ocean: 'океАн', expert: 'експЕрт', progress: 'прогрЕс', contact: 'контАкт',
  website: 'вебсАйт', signal: 'сигнАл', detective: 'детектИв', lieutenant: 'лейтенАнт',
  interview: "інтерв'Ю", festival: 'фестивАль', concert: 'концЕрт', theater: 'теАтр',
  telephone: 'телефОн', basketball: 'баскетбОл', journalist: 'журналІст', pilot: 'пілОт',
  palace: 'палАц', budget: 'бюджЕт', region: 'регІон', champion: 'чемпіОн', candidate: 'кандидАт',
  tourist: 'турИст', menu: 'менЮ', comfort: 'комфОрт', taxi: 'таксІ', helicopter: 'гелікОптер',
  calendar: 'календАр', final: 'фінАл', lemon: 'лимОн', concept: 'концЕпт', sofa: 'софА', picnic: 'пікнІк',
};
```

## Sources

- Barcroft, J. (2002). Semantic and structural elaboration in L2 lexical acquisition. *Language Learning* 52(2).
- Bassetti, B. (2008). Orthographic input and second language phonology. In Piske & Young-Scholten (eds), *Input Matters in SLA*.
- Boers, F. & Lindstromberg, S. (2009). *Optimizing a Lexical Approach to Instructed Second Language Acquisition*.
- Brown, R., Waring, R. & Donkaewbua, S. (2008). Incidental vocabulary acquisition from reading, reading-while-listening, and listening to stories. *Reading in a Foreign Language* 20(2).
- Cepeda, N. J. et al. (2006). Distributed practice in verbal recall tasks. *Psychological Bulletin* 132(3).
- Cook, V. (2001). Using the first language in the classroom. *Canadian Modern Language Review* 57(3).
- de Groot, A. & Keijzer, R. (2000). What is hard to learn is easy to forget. *Language Learning* 50(1).
- Dörnyei, Z. (2001). *Motivational Strategies in the Language Classroom*.
- Hu, M. & Nation, P. (2000). Unknown vocabulary density and reading comprehension. *Reading in a Foreign Language* 13(1).
- Koriat, A. & Bjork, R. A. (2005). Illusions of competence in monitoring one's knowledge during study. *JEP: Learning, Memory, and Cognition* 31(2).
- Laufer, B. (1989). What percentage of text-lexis is essential for comprehension? In Lauren & Nordman (eds), *Special Language*.
- Laufer, B. & Girsai, N. (2008). Form-focused instruction in second language vocabulary learning: a case for contrastive analysis and translation. *Applied Linguistics* 29(4).
- Laufer, B. & Goldstein, Z. (2004). Testing vocabulary knowledge: size, strength, and computer adaptiveness. *Language Learning* 54(3).
- Lee, J., Jang, J. & Plonsky, L. (2015). The effectiveness of second language pronunciation instruction: a meta-analysis. *Applied Linguistics* 36(3).
- Lubliner, S. & Hiebert, E. H. (2011). An analysis of English–Spanish cognates as a source of general academic language. *Bilingual Research Journal* 34(1).
- MacLeod, C. M. et al. (2010). The production effect: delineation of a phenomenon. *JEP: Learning, Memory, and Cognition* 36(3).
- Nagy, W. E., García, G. E., Durgunoğlu, A. Y. & Hancin-Bhatt, B. (1993). Spanish–English bilingual students' use of cognates in English reading. *Journal of Reading Behavior* 25(3).
- Nakata, T. (2015). Effects of expanding and equal spacing on second language vocabulary learning. *Studies in Second Language Acquisition* 37(4).
- Nation, I. S. P. (2013). *Learning Vocabulary in Another Language* (2nd ed.).
- Roediger, H. L. & Karpicke, J. D. (2006). Test-enhanced learning. *Psychological Science* 17(3).
- Sharwood Smith, M. (1993). Input enhancement in instructed SLA. *Studies in Second Language Acquisition* 15(2).
- Webb, S. (2009). The effects of receptive and productive learning of word pairs on vocabulary knowledge. *RELC Journal* 40(3).
