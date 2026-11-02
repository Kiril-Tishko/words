export const meta = {
  name: 'card-qa',
  description: 'Expert quality pass per card: verdict, meaning share, English labels, grammar, collocation, examples and note',
  phases: [{ title: 'Card QA' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, cards: { type: 'number' }, removed: { type: 'number' }, rewritten: { type: 'number' } }, required: ['file', 'cards'] }

const LEVEL = {
  'top-1000': 'A0–A1, strict: each sentence at most 7 words; present simple, to be, have, like, can, imperative, there is/are; NO past tense, NO phrasal verbs, NO idioms; every other word basic A1; at least 2 of the 4 are questions or requests a learner would really say (shop, street, school, work, phone); at least 1 shows the main word partner (take a photo, watch a video); no names except Anna or Kyiv; nothing US-specific.',
  'top-2000': 'A1–A2: 4–9 words, simple tenses, no idioms, practical everyday situations, at least 1 question or request.',
  'top-3000': 'A1–A2: 4–9 words, simple tenses, no idioms, practical everyday situations, at least 1 question or request.',
  'top-5000': 'A2–B1: 6–11 words, practical, common vocabulary.',
  'top-10k': 'A2–B1: 6–11 words, practical, common vocabulary.',
  'top-20k': 'B1: 6–12 words, natural and practical, other words simple.',
  'top-50k': 'B1: 6–12 words, natural and practical, other words simple.',
  'top-100k': 'B1–B2: clear practical sentences that show what the thing is or where it is used; other words simple.',
  'rare': 'B1–B2: clear practical sentences that show what the thing is or where it is used; other words simple.',
}

function prompt(b, full) {
  return `You are a senior lexicographer and teacher of English to Ukrainian speakers, doing the final quality pass on flashcards. Each card pairs an English word with the IDENTICAL Ukrainian word (rules: ${ROOT}/data/RUBRIC.md). Cards teach the ENGLISH word; the Ukrainian word only shows which meaning the card is about.
Batch: ${ROOT}/data/qa-in/${b}.json — a JSON array; each card has: en, uk, pos, band (frequency band of the English word in this meaning), share (current estimate of % of uses of the English word in this meaning), raw_rank (rank of the English word form overall), meaning_hint (a checker's note, may mention Ukrainian), examples (current 4 English sentences, may be missing), note (current English note).

For EVERY card decide and write:
1. "v": "keep", or "partial_false_friend" (the shared meaning is a minor sense of the English word (under ~15% of its use) AND its main meaning has a different usual Ukrainian word — e.g. sort = сорт, killer = кілер, hospital = госпіталь, market = маркет), "similar" (form differs: an added/dropped ending or suffix), "false_friend", "not_standard_ukrainian" (nobody uses this Ukrainian form, e.g. елефант, альфабет), "not_english" (not a real English word in this form), or "proper_noun".
2. "s": % (0–100) of all uses of the English word form (all meanings and parts of speech) that are in THIS meaning. The Ukrainian word being slang or informal must NOT lower it (cash = кеш means money → ~95; friend = френд → ~95; people = піпл → 100). Count abbreviations on their own (IT as information technology, not the pronoun "it"). For multi-word or hyphenated items give "pm" instead: occurrences per million words.
3. "reg": usage labels of the ENGLISH word in this meaning, only from: informal, slang, vulgar, offensive, dated, archaic, literary, formal, technical. [] if neutral.
4. "ns": true if the UKRAINIAN word is slang, colloquial, rare or non-standard in Ukrainian (піпл, френд, кеш as money); false if it is a normal dictionary word (доктор, ген, тату, імейл, софтвер).${full ? `
5. "gram": for nouns, the article + plural pattern: "a photo · photos", "an idea · ideas", "a baby · babies", "a person · people", "the internet", "rice · uncountable", "jeans · plural". For other parts of speech: "".
6. "say": for bands top-1000 … top-5000 only: the most useful word partners, especially where Ukrainian uses a different verb or preposition (photo → "take a photo · in the photo"; internet → "on the internet"; test → "take a test"; party → "at a party"). Otherwise "".` : ''}
${full ? 7 : 5}. Examples: check each sentence. Rewrite ALL 4 (as "ex") if any sentence uses another meaning of the English word than the card's meaning, contains an error, or breaks the level for its band; also write them if the card has none. Otherwise omit "ex". Level by band:
${Object.entries(LEVEL).map(([k, v]) => `   ${k}: ${v}`).join('\n')}
   Always practical, real situations, American spelling, the card's word in every sentence, no real people or brands.
${full ? 8 : 6}. "note": the final English note, ONLY about the English word, ≤ 110 characters, simple English. Required when s < 50 and raw_rank ≤ 10000: say what the word most often means, e.g. 'Most often "country" means a state: "Ukraine is a big country."'. For uncountable nouns: 'Uncountable: some rice, a lot of rice (not "a rice").' Fix wrong notes (a school head is the "principal" in the US, not the "director"). Never describe the Ukrainian word. "" if nothing is needed.

Write ${ROOT}/data/qa/${b}.json — ONE JSON object keyed by "en" exactly as in the batch, e.g.
  {"photo": {"v": "keep", "s": 95, "reg": [], "ns": false${full ? ', "gram": "a photo · photos", "say": "take a photo · in the photo"' : ''}, "note": ""}, "cream": {"v": "keep", "s": 30, "reg": [], "ns": false${full ? ', "gram": "cream · uncountable", "say": ""' : ''}, "ex": ["Put this cream on your hands.", "..."], "note": "..."}}
Every card must have an entry. Validate with python3 -c "import json;d=json.load(open('${ROOT}/data/qa/${b}.json'));print(len(d))" and fix if needed. No web search, no git, no other files.
Return the file path, number of cards, number not "keep", number with rewritten examples.`
}
phase('Card QA')
const res = await parallel(args.batches.map(b => () =>
  agent(prompt(b, b.startsWith('full-')), { label: b, phase: 'Card QA', schema: RESULT, effort: b.startsWith('full-') ? 'high' : 'medium' })
    .then(r => r ? { b, ...r } : { b, failed: true })))
return { done: res.filter(r => r && !r.failed).length, failed: res.filter(r => !r || r.failed).map(r => r && r.b),
  removed: res.reduce((s, r) => s + ((r && r.removed) || 0), 0), rewritten: res.reduce((s, r) => s + ((r && r.rewritten) || 0), 0) }
