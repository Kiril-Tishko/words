export const meta = {
  name: 'cross-check-lite',
  description: 'Token-light second, skeptical check of pairs judged identical; sets the level of the shared meaning',
  phases: [{ title: 'Cross-check' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, total: { type: 'number' }, identical: { type: 'number' } }, required: ['file', 'total'] }
function prompt(b) {
  return `You are the SECOND, skeptical checker for a site of English words that are the SAME in Ukrainian. Rules: ${ROOT}/data/RUBRIC.md (read once). Batch: ${ROOT}/data/candidates/${b}.txt — each line "english = ukrainian | first verdict; pos; list level (CEFR-J/Octanove/Cambridge Starters for this word+pos); lists by pos; british; labels".
For EVERY line give the final verdict. Overturn identical when: the shared meaning is not a main everyday meaning in BOTH languages (→ partial_false_friend); an ending/suffix differs (→ similar); proper noun/brand (→ proper_noun); the Ukrainian is not a standard word (fix cu if a standard identical form exists, else unrelated); written abbreviations like Mr./Dr. → full word pair if identical.
lvl (identical only) = CEFR level of THIS shared meaning: the list level if it is the word's main meaning; higher if it is a narrower sense; no list level → everyday B1–B2, specialised C1, technical/rare/archaic C2. A0 only if list level is A0.
Write ${ROOT}/data/checked/${b}.json — JSON array, one compact object per line, in order:
  {"en":"<english as on line>","uk":"<ukrainian as on line>","v":"<verdict>","lvl":"B1","pos":"noun","br":false,"lab":[...]}
  Add "ce"/"cu" only if you change the spelling or pair; add "why" (≤ 12 words) only if you change the verdict. Non-identical: only en, uk, v (+ce/cu/why). No notes.
Validate with python3 -c "import json;json.load(open('${ROOT}/data/checked/${b}.json'))". No web search, no git, no other files.
Return file path, total objects, number identical.`
}
phase('Cross-check')
const res = await parallel(args.batches.map(b => () =>
  agent(prompt(b), { label: b, phase: 'Cross-check', schema: RESULT, effort: 'medium' }).then(r => r ? { b, ...r } : { b, failed: true })))
return { done: res.filter(r => r && !r.failed).length, failed: res.filter(r => !r || r.failed).map(r => r && r.b) }
