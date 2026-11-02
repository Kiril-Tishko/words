# Rubric: English–Ukrainian identical words

Every checking agent follows these rules. They match what the project owner asked for.

## Verdicts (one per candidate pair)

| verdict | meaning | examples |
|---|---|---|
| `identical` | Same meaning **and** same word form (see "Form" below). Goes on the site now. | taxi=таксі, park=парк, radio=радіо, computer=комп'ютер, show=шоу, manager=менеджер, hotel=готель, hockey=хокей, golf=гольф, jazz=джаз, pizza=піца, center=центр, tiger=тигр, DJ=діджей, OK=окей |
| `similar` | Same meaning, but the form differs more than the rules allow (ending/suffix added or dropped, other letters changed). Saved for a later "similar words" set. | problem=проблема, music=музика, history=історія, banana=банан, chips=чипси, system=система, group=група |
| `false_friend` | Look alike, but the main meanings are different. Saved for a later "false friends" set. | magazine≠магазин, list≠лист, family≠фамілія, accurate≠акуратний |
| `partial_false_friend` | Look alike and share some meaning, but an important main meaning differs, so a learner would misuse it. Saved for later. NOT on the site now. | artist (painter) vs артист (performer), meeting vs мітинг (rally), photograph vs фотограф (photographer) |
| `proper_noun` | Names of people, countries, cities, rivers, brands, companies, nationalities used as names. Excluded. | Canada=Канада, Aaron=Аарон, Adidas |
| `not_lemma` | One side is an inflected/derived form, not the dictionary headword (e.g. Ukrainian genitive/plural, English plural/past). Give the lemma pair in `canon_en`/`canon_uk` if that lemma pair would be identical. | проблему, системи, parks |
| `unrelated` | Coincidental look-alike, different words. | cat≠кат, dim≠дім, the≠да |

## Form: what counts as "identical"

The Ukrainian word is the English word written in Ukrainian letters — by spelling **or** by sound — with only these regular adaptations:
- letters: c→к/ц/с, k→к, q(u)→к(в), x→кс, w→в/у, j→дж, th→т, ph→ф, ch→ч/х/к, sh→ш, y→і/и/й, g→г/ґ/дж, **h→г or х** (allowed: hotel=готель, hobby=хобі, hockey=хокей)
- soft sign or apostrophe added (film=фільм, computer=комп'ютер), double letters written single (tennis=теніс), silent final -e dropped (smartphone=смартфон)
- vowel quality that follows English pronunciation (manager=менеджер, rating=рейтинг, cowboy=ковбой)
- -er / -re pronounced ending written -р (center=центр, meter=метр, tiger=тигр, theater=театр)
- compounds may be joined or hyphenated (hot dog=хот-дог, fast food=фастфуд, rock and roll=рок-н-рол)
- abbreviations read as words count (DJ=діджей, PR=піар, IT=айті, VIP=віп, MC=емсі)

NOT identical (→ `similar`): any added or removed ending or suffix (-а, -я, -ія, -ика, -ка, -ок, -ний, -ти…), or a different root shape. Ukrainian adjectives/verbs with their own endings are never identical.

## Meaning

- The shared meaning must be a **main, everyday meaning in both languages** (for that word). Extra meanings in one language are fine; mention them in `note` if a learner should know.
- If the Ukrainian word is only slang/rare while English is common, it can still be `identical` — add labels.
- Archaic/obsolete English words ARE included when they match — label them `archaic` or `obsolete`.

## Canonical forms for `identical`
- `canon_en`: dictionary headword in **American / international spelling** (center, color, theater, meter, humor). Use British spelling ONLY if the word itself exists only in British English. Abbreviations in their usual capitals (DJ, PR, OK, IT, VIP).
- `canon_uk`: Ukrainian dictionary headword (nominative singular, current spelling, apostrophe ' as in комп'ютер).
- `british`: true only if this word (or this meaning) is used just in British English (e.g. lift = elevator).
- `note`: written for a Ukrainian learning English, so it talks ONLY about the English word — how it is used in English (e.g. "Usually 'cell phone' in American English", "Plural: data"). Never describe the Ukrainian word's other meanings. Leave empty if nothing is needed.

## Labels (array, use only these)
Usage: `archaic`, `obsolete`, `dated`, `literary`, `informal`, `slang`, `abbreviation`, `technical`, `rare`, `international` (the same word exists in most major European languages, e.g. taxi, radio, hotel).
Topic (one or two): `food`, `drinks`, `sport`, `music`, `art`, `media` (film/TV/press/internet culture), `tech` (computers, internet, devices), `science`, `medicine`, `chemistry`, `physics`, `biology`, `math`, `transport`, `clothing`, `home`, `business`, `finance`, `politics`, `law`, `military`, `religion`, `education`, `people` (jobs, roles, family), `nature` (animals, plants, weather, geography terms), `places` (buildings, places in town), `travel`, `games`, `language`, `units`, `time`, `emotions`, `other`.

`pos`: noun, verb, adj, adv, interj, phrase, abbr, num, prep, conj, pron.
