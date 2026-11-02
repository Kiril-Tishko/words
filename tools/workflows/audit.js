export const meta = {
  name: 'coverage-audit',
  description: 'Independent linguists: find all identical words in random samples (recall) and judge a random sample of the list (precision)',
  phases: [{ title: 'Audit' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, count: { type: 'number' } }, required: ['file', 'count'] }

function findPrompt(t) {
  const en = t.kind === 'en'
  return `You are an expert linguist fluent in English and Ukrainian. Rules for "identical" words: ${ROOT}/data/RUBRIC.md (read it).
Input: ${ROOT}/data/audit/${t.file}.txt — 1,000 random ${en ? 'English' : 'Ukrainian'} words, one per line (some are junk tokens, names or inflected forms; skip those).
Task: find EVERY word in the list that has an IDENTICAL ${en ? 'Ukrainian' : 'English'} word — same main meaning and the same word form (transliterated by spelling or by sound, with the rubric's adaptations, h→г/х allowed, no added or dropped endings). Include everyday, technical, archaic, slang words and abbreviations. Be exhaustive: go line by line; missing one is worse than listing a doubtful one (doubtful ones are checked later).
Do not use web search, do not open any other project files.
Write ${ROOT}/data/audit/found-${t.file}-${t.who}.json — a JSON array: [{"en": "<English word>", "uk": "<Ukrainian word>"}, ...] (${en ? '"en" exactly as in the list' : '"uk" exactly as in the list'}). Write [] if none.
Validate with python3 -c "import json;print(len(json.load(open('${ROOT}/data/audit/found-${t.file}-${t.who}.json'))))".
Return the file path and the number of pairs.`
}
function precPrompt(t) {
  return `You are an expert linguist fluent in English and Ukrainian, reviewing a word list for learners. Rules for "identical" words: ${ROOT}/data/RUBRIC.md (read it).
Input: ${ROOT}/data/audit/${t.file}.txt — 200 pairs "english = ukrainian" that are claimed to be identical words.
Judge every pair independently and strictly: is it really identical (same main meaning in both languages, same form within the rubric's adaptations, a real standard word on both sides)?
Write ${ROOT}/data/audit/judged-${t.file}-${t.who}.json — a JSON array with one object per line in order:
  {"en": "...", "uk": "...", "ok": true}  or  {"en": "...", "uk": "...", "ok": false, "why": "similar | false_friend | partial_false_friend | proper_noun | not_a_word | other: <≤8 words>"}
Validate with python3 -c "import json;print(len(json.load(open('${ROOT}/data/audit/judged-${t.file}-${t.who}.json'))))". No web search, no git, no other files.
Return the file path and the number of pairs judged.`
}
phase('Audit')
const res = await parallel(args.tasks.map(t => () =>
  agent(t.kind === 'prec' ? precPrompt(t) : findPrompt(t), { label: `${t.file}-${t.who}`, phase: 'Audit', schema: RESULT, effort: 'high' })
    .then(r => r ? { t: `${t.file}-${t.who}`, ...r } : { t: `${t.file}-${t.who}`, failed: true })))
return res
