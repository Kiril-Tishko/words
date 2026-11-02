export const meta = {
  name: 'rare-flag-check',
  description: 'Cheap second check for rare words: flag only the pairs that are NOT identical',
  phases: [{ title: 'Flag' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, flagged: { type: 'number' } }, required: ['file', 'flagged'] }
function prompt(b) {
  return `Second check of rare/technical English–Ukrainian pairs that a first checker judged IDENTICAL (same word, same meaning). Rules: ${ROOT}/data/RUBRIC.md (read once). Batch: ${ROOT}/data/candidates/${b}.txt — one pair per line "english = ukrainian | ...".
Most pairs are correct. Flag ONLY the wrong ones: different meaning (false_friend / partial_false_friend), different form such as an added or dropped ending or suffix (similar), names/brands (proper_noun), or not real words (unrelated). If only the spelling of one side is wrong, give the corrected pair with v "identical" and ce/cu.
Write ${ROOT}/data/checked/flags/${b}.json — JSON array of flagged pairs only ([] if none): {"en":"<as on line>","uk":"<as on line>","v":"<verdict>","why":"≤ 8 words"} (+ "ce"/"cu" for spelling fixes).
Validate with python3 -c "import json;json.load(open('${ROOT}/data/checked/flags/${b}.json'))". Work quickly; no web search, no git, no other files.
Return the file path and the number flagged.`
}
phase('Flag')
const res = await parallel(args.batches.map(b => () =>
  agent(prompt(b), { label: b, phase: 'Flag', schema: RESULT, effort: 'low' }).then(r => r ? { b, ...r } : { b, failed: true })))
return { done: res.filter(r => r && !r.failed).length, failed: res.filter(r => !r || r.failed).map(r => r && r.b), flagged: res.reduce((s, r) => s + ((r && r.flagged) || 0), 0) }
