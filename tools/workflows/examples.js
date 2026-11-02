export const meta = {
  name: 'card-examples',
  description: 'Write 4 English example sentences (and an English-only usage note when needed) for each card',
  phases: [{ title: 'Examples' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, words: { type: 'number' } }, required: ['file', 'words'] }
function prompt(b) {
  return `Write example sentences for flashcards that teach English to Ukrainian speakers. Each card pairs an English word with the identical Ukrainian word.
Batch: ${ROOT}/data/candidates/examples/${b}.txt — one line per card: "english = ukrainian | part of speech | topic".
The Ukrainian word only tells you WHICH meaning the card is about (e.g. "take = тейк" is a take in filming, "court = корт" is a tennis court). Use the English word in exactly that meaning and part of speech.
For every line write:
- "ex": 4 different, natural, everyday English sentences (6–12 words each) that show typical uses and word partners of the word in that meaning. American spelling. Simple vocabulary. The word itself must appear in each sentence (plural or other form is fine). No names of real people.
- "note": usually "" (empty). Write a note (English, ≤ 100 characters) ONLY when a learner of English would likely misuse the word — e.g. it is uncountable, has an irregular plural, is informal in English, or has a more common everyday synonym. The note talks only about the English word, never about the Ukrainian one.
Write ${ROOT}/data/examples/${b}.json as one JSON object keyed by the English word exactly as in the batch:
  {"people": {"ex": ["...", "...", "...", "..."], "note": ""}, ...}
Validate with python3 -c "import json;d=json.load(open('${ROOT}/data/examples/${b}.json'));print(len(d))" and fix if needed. Work quickly; no web search, no git, no other files.
Return the file path and the number of words written.`
}
phase('Examples')
const res = await parallel(args.batches.map(b => () =>
  agent(prompt(b), { label: b, phase: 'Examples', schema: RESULT, effort: 'low' }).then(r => r ? { b, ...r } : { b, failed: true })))
return { done: res.filter(r => r && !r.failed).length, failed: res.filter(r => !r || r.failed).map(r => r && r.b) }
