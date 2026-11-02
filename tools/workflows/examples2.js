export const meta = {
  name: 'card-examples-graded',
  description: 'Write 4 practical English example sentences per card, as simple as the word\'s frequency band requires, plus an English-only note when needed',
  phases: [{ title: 'Examples' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, words: { type: 'number' } }, required: ['file', 'words'] }
const LEVEL = {
  1: `These are among the 1,000 most used English words, for absolute beginners (A0–A1). Each sentence 3–7 words, present simple or "can", only the most basic everyday words, about real practical situations (home, family, food, shop, school, work, phone, street, travel). Like: "I have a new computer." "Call a taxi, please." "The hotel is near here."`,
  2: `These are among the 3,000 most used English words, for beginners (A1–A2). Each sentence 4–9 words, simple tenses, everyday vocabulary, practical real-life situations. Like: "We watched a good film last night." "Can I pay by card at the bank?"`,
  3: `These are common English words (A2–B1). Each sentence 6–11 words, common vocabulary, practical everyday or work situations.`,
  4: `These are less common English words (B1). Each sentence 6–12 words, natural and practical; keep the other words simple so the sentence is easy to understand.`,
  5: `These are rare, specialised or technical English words. Each sentence 6–14 words; make clear what the thing is or where it is used (a practical, real situation); keep the other words simple (B1).`,
}
function prompt(b) {
  const tier = +b.match(/-t(\d)-/)[1]
  return `Write example sentences for flashcards that teach English to Ukrainian speakers. Each card pairs an English word with the identical Ukrainian word.
Batch: ${ROOT}/data/candidates/examples2/${b}.txt — one card per line: "english = ukrainian | part of speech | topic".
The Ukrainian word only tells you WHICH meaning the card is about (e.g. "country = кантрі" is country music, "court = корт" is a sports court, "take = тейк" is a take in filming). Use the English word ONLY in that meaning and part of speech.
Level: ${LEVEL[tier]}
For every line write:
- "ex": 4 different sentences. Practical is most important: things people really say or write in daily life, useful situations, common word partners. American spelling. The card's word must appear in every sentence (a plural or other form is fine). No names of real people or brands.
- "note": usually "" (empty). Only if a learner would likely misuse the English word, write a short note (≤ 90 characters, simple English) about the ENGLISH word only — e.g. uncountable, irregular plural, informal, British word, a more common everyday synonym. Never describe the Ukrainian word.
Write ${ROOT}/data/examples2/${b}.json as one JSON object keyed by the English word exactly as in the batch:
  {"computer": {"ex": ["...", "...", "...", "..."], "note": ""}, ...}
Every line must have an entry. Validate with python3 -c "import json;d=json.load(open('${ROOT}/data/examples2/${b}.json'));print(len(d))" and fix if needed. No web search, no git, no other files.
Return the file path and the number of words written.`
}
phase('Examples')
const res = await parallel(args.batches.map(b => () =>
  agent(prompt(b), { label: b, phase: 'Examples', schema: RESULT, effort: +b.match(/-t(\d)-/)[1] <= 3 ? 'medium' : 'low' })
    .then(r => r ? { b, ...r } : { b, failed: true })))
return { done: res.filter(r => r && !r.failed).length, failed: res.filter(r => !r || r.failed).map(r => r && r.b) }
