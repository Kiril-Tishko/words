export const meta = {
  name: 'precision-sweep',
  description: 'Two independent strict judges re-check every pair in a band batch; pairs both reject are removed later',
  phases: [{ title: 'Judge' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, judged: { type: 'number' }, rejected: { type: 'number' } }, required: ['file', 'judged'] }

function prompt(b, who) {
  return `You are an expert linguist, fluent in English and Ukrainian, checking a word list for Ukrainian learners of English. Each line pairs an English word with a Ukrainian word that is claimed to be the SAME word: same main meaning, and the same word form written in Ukrainian letters. Rules: ${ROOT}/data/RUBRIC.md (read it).
Input: ${ROOT}/data/prec-sweep/${b}.txt. Each line is "english = ukrainian | part of speech | e.g. <one example sentence>". There are 200 lines.
Judge EVERY line strictly and independently. A pair is WRONG if any of these is true:
- similar: the form differs beyond the rubric's letter adaptations, e.g. an added or dropped ending or suffix, or a different root shape. chancellor ≠ канцлер, carapace ≠ карапакс, department ≠ департамент.
- partial_false_friend: the shared meaning is a minor sense of the English word (under ~15% of its use) and the main meaning has another usual Ukrainian word.
- false_friend: the main meanings differ.
- not_standard_ukrainian: Ukrainians do not use this word.
- not_english: not a real English word in this form.
- proper_noun: a name, place or brand.
Also treat as wrong an abbreviation that is a native Ukrainian abbreviation, not a borrowing (PC ≠ ПК).
Being rare, technical, slang or archaic is NOT a reason to reject.
Write ${ROOT}/data/prec-sweep/judged-${b}-${who}.json — a JSON array with ONLY the wrong pairs:
  [{"en": "<english exactly as in the line>", "uk": "<ukrainian exactly as in the line>", "v": "<one verdict from the list above>", "why": "<≤ 10 words>"}]
Write [] if every pair is right.
Validate: python3 -c "import json;print(len(json.load(open('${ROOT}/data/prec-sweep/judged-${b}-${who}.json'))))".
No web search, no git, no other files.
Return: file path, number of lines judged (200), number rejected.`
}
phase('Judge')
const jobs = []
for (const b of args.batches) for (const who of ['A', 'B']) jobs.push({ b, who })
const res = await parallel(jobs.map(j => () =>
  agent(prompt(j.b, j.who), { label: `${j.b}-${j.who}`, phase: 'Judge', schema: RESULT, effort: 'medium' })
    .then(r => r ? { t: `${j.b}-${j.who}`, ...r } : { t: `${j.b}-${j.who}`, failed: true })))
return { done: res.filter(r => !r.failed).length, failed: res.filter(r => r.failed).map(r => r.t),
  rejected: res.reduce((s, r) => s + (r.rejected || 0), 0) }
