# Practical redesign: word clouds

*12 November 2026. Why the site changed from levels and stories to clouds, and how the clouds are made.*

## What was wrong

The teacher's verdict on the earlier site: not practical. The groups, the levels and the texts were wrong, and the useful words were buried under thousands of rare ones.

Looking at the data and at the teacher's own lesson pages confirmed each point:

- **Levels.** The site used CEFR levels of the English word. By that measure 12,479 of the 13,147 cards are B2 or higher, so metal, vitamin and radiator sat in "advanced" lessons. But for a Ukrainian these words are easy: they say метал, вітамін and радіатор every day. A textbook level measures how hard a word is for a learner who starts from nothing. Here the learner starts with the word already known.
- **Groups.** Lessons were cut inside each level, so the kitchen words were spread over A1, B1, B2 and C1. A learner remembers a word together with its situation, so the words of one situation have to be together.
- **Texts.** The stories were ordinary English texts with a few highlighted words. They did not lean on what the learner knows, and nothing in them could be said in a shop or at work the same day.
- **Trash.** Half of the cards are rare (сфінкс, амін, біді). They are correct, but they hid the useful ones.
- **Little words.** OK, hey, wow and oops led the frequency list, but they do not build sentences. Slang pairs (піпл, френд, гуд) are English words Ukrainians already know as English.
- **Presentation.** Levels, lessons, three views, filters, practice modes: too many choices before anything useful appears.

## The task from five sides

**The learner** (adults at A2–B1 who need English for the week ahead: an order, an appointment, a meeting). The gain is not "I know the word menu". It is "I can say *Can I see the menu, please?* today". So the unit is a situation with its words and the sentences that use them.

**The teacher.** The teacher's own lesson pages have one shape: one thing per screen, a big line in the middle, Back and Next at the bottom, no menu before the content, old items first, "Say it in English" then tap Answer, Ukrainian only in small fixed places, sound on every English line, and three sentences of the student's own at the end. The site now has that shape, so a cloud works like one more lesson page.

**Linguistics.**
- A word is easy when the Ukrainian word is familiar, its form is close, and its main meaning matches. Familiarity is measured on the Ukrainian side (how common the Ukrainian word is), not by English textbook lists.
- Words that only look the same are the real danger: magazine, costume, accurate, data, list, variant. Each cloud names the one trap that belongs to its situation.
- Sentences need verbs and adjectives. The identical list is almost all nouns (12,901 of 13,147), because Ukrainian verbs and adjectives carry their own endings. So the clouds add the "almost the same" words: організувати ≈ organize, активний ≈ active, інформація ≈ information.
- Endings are regular. Nine rule clouds (‑ція → ‑tion, ‑ія → ‑y, ‑ний → ‑al / ‑ic / ‑ive, ‑ізм, ‑іст, ‑ор, ‑ент, ‑ика, ‑ура, ‑но → ‑ly) let one rule open hundreds of words.

**Memory.** A word is stored with its scene. Thinking of a kitchen brings blender, toaster and filter with it. So words are grouped by scene (a cloud), each cloud is small (16 main words, the rest folded), and each new cloud starts with three sentences from earlier clouds.

**The Latin lesson.** The Latin course the teacher liked starts with words the learner already has (poēta, discipula, agricola) and builds two-word sentences from them, changing one thing at a time. The clouds do the same for English: the content words are free, so the learner can say a whole sentence at once.

## What a cloud is

One situation, in this order:

1. **Repeat**: three sentences from clouds finished earlier (Ukrainian first, say it, then check).
2. **Words**: the cloud itself. 16 words on one screen, each with its Ukrainian twin; tap to hear. More words are folded under one button.
3. **Say it**: five ready phrases for the situation. The Ukrainian line comes first, the student says it in English, then taps Answer and hears it.
4. **Change one word**: one sentence frame and several known words (A cappuccino, please → latte → espresso). This is the Latin lesson's move: the same sentence, one thing changed, so one frame gives many sentences the student can say.
5. **Dialogue**: four lines, "You hear" and "You say", with sound and a hidden translation.
6. **Careful**: the look-alike that causes mistakes in this situation.
7. **All together**: the phrases as a list with sound.
8. **This week**: three sentences the student writes for their own week.

## No levels: an order

Every word in a cloud is already known, so there are no difficulty levels. The clouds are in the order of need:

| Circle | Clouds | What is in it |
|---|---|---|
| Every day | 36 | café, restaurant, food, home, clothes, city, transport, car, travel, hotel, money, shopping, doctor, people, jobs, feelings, sport, music, films, internet, phone, computer, animals, nature, time, numbers |
| Rules | 9 | endings that turn a Ukrainian word into an English one |
| Work and study | 19 | office, words for any conversation, projects, documents, business, clients, banking, IT, production, materials, delivery, studying, and three clouds of verbs |
| The wider world | 11 | politics, society, army, law, science, space, medicine, art, books, traditions, geography |
| On the side | 3 | reactions (OK, wow, oops), slang (friend, people, cool) and old relatives (sister ≈ сестра) |

The site opens on the next cloud with one button. The list of all clouds is one tap away, so a teacher can send a student straight to the cloud for this week's topic.

## How the clouds were made

1. **Pool.** The 13,147 identical cards and the 2,820 checked "almost the same" pairs. For each, how common the Ukrainian word is (wordfreq) and how common the English word is.
2. **Clouds by hand.** Each cloud was written top down (the situation first, then its words), then every word was looked up in the checked lists by `tools/build_clouds.py`. A word that is not in the lists cannot enter a cloud unchecked.
3. **New pairs.** 305 pairs were not in the lists, mostly verbs, adjectives and adverbs. Each was checked against three conditions: the Ukrainian word is one every adult uses; the English word is the normal word for that meaning; the link is heard at once. 272 were kept and 33 rejected (ventilator, packet, variant, hymn, argue, concrete…). The 36 pairs of the "Old relatives" cloud follow a looser rule: they are inherited relatives (sister and сестра are one ancient word), not loans, and they stay in that cloud only. The decisions and reasons are in `data/clouds/checked.json`. This check was made by the author of the clouds; an independent second check is still to do.
4. **Phrases and dialogues** were written for the situation at A2 level and use the cloud's words. American English. All of them were then read again as an editor would, and about 30 were corrected. Most fixes were calques: a missile attack (not a rocket attack), the environment (not ecology), a blood test (not an analysis), a receptionist (not an administrator).
5. **Sound.** Every phrase, dialogue line and word is recorded with the same voice as the cards (`tools/make_cloud_audio.py`), one file per cloud.

## Where things are

- `data/clouds/*.txt`: the clouds, in a plain format (words, phrases, dialogue, warning). The order of the files and lines is the order on the site.
- `data/clouds/checked.json`: the new pairs with the decision for each.
- `tools/build_clouds.py` → `clouds.js`; `tools/make_cloud_audio.py` → `audio/cloud-<id>.mp3`.
- `site/app.html`: the page. The earlier page with levels and stories is kept as `site/app-v2-levels.html`.

## Still open

- An independent check of the new pairs and of all phrases by a second linguist.
- The remaining familiar words that are in no cloud yet (the full list stays in Search).
- Extra clouds for a student's own job.
