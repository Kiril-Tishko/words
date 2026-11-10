export const meta = {
  name: 'similar-find',
  description: 'Find English words whose Ukrainian equivalent sounds ALMOST the same with the same meaning (problem = проблема)',
  phases: [{ title: 'Find' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, pairs: { type: 'number' } }, required: ['file', 'pairs'] }
function prompt(i) {
  return `You are a bilingual English–Ukrainian linguist. Input: ${ROOT}/data/similar2/in-${i}.txt — common English words, one per line (most used first).
For EVERY word, decide whether Ukrainian has a word that SOUNDS ALMOST THE SAME and has the SAME MAIN MEANING, so a Ukrainian learner can recognize it easily. Typical differences: an added or dropped ending (problem = проблема, system = система, history = історія, music = музика, banana = банан, minute = хвилина is NOT similar), one or two changed sounds (chocolate = шоколад, police = поліція, energy = енергія, company = компанія, program = програма, information = інформація).
Rules: the main everyday meaning must be the same (not a false friend like magazine/магазин); a normal, standard Ukrainian word; skip names; skip pairs whose Ukrainian is IDENTICAL in form (those are already on the site).
Write ${ROOT}/data/similar2/out-${i}.json — a JSON array [{"en": "problem", "uk": "проблема"}, ...] with only the words that have such a twin. Work quickly but go through every line.
Validate: python3 -c "import json;print(len(json.load(open('${ROOT}/data/similar2/out-${i}.json'))))". No web search, no git, no other files.
Return: file path and number of pairs.`
}
phase('Find')
const res = await parallel(args.parts.map(i => () =>
  agent(prompt(i), { label: `similar-${i}`, phase: 'Find', schema: RESULT, effort: 'low' }).then(r => r ? { i, ...r } : { i, failed: true })))
return res
