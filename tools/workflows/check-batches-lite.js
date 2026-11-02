export const meta = {
  name: 'check-batches-lite',
  description: 'Token-light first check of English–Ukrainian candidate batches (only non-trivial verdicts written)',
  phases: [{ title: 'Check' }],
}

const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, written: { type: 'number' } }, required: ['file', 'written'] }

function prompt(b) {
  const scan = b.startsWith('rscan-')
  const fmt = scan
    ? 'Each line is "ukrainian :: english look-alike, ...". Almost all lines are coincidences. Report only lines where the Ukrainian word and one listed English word are the same word with the same meaning (identical or similar), or a clear false friend. Ukrainian inflected forms: report the lemma pair with v "not_lemma" and "lv".'
    : 'Each "## english" block lists candidate Ukrainian words ("- ukrainian [evidence]"). Judge every candidate; most are similar words, inflected forms, names or coincidences.'
  return `Check English–Ukrainian word pairs for a site of words that are the SAME in both languages.
Rules: ${ROOT}/data/RUBRIC.md (read it once). Batch: ${ROOT}/data/candidates/${b}.txt. ${fmt}
Work quickly; no web search; do not run git; do not touch other files.
Write ${ROOT}/data/checked/${b}.json: a JSON array with ONE object per pair whose verdict is identical, similar, false_friend, partial_false_friend or not_lemma — SKIP unrelated and proper_noun pairs entirely. No notes.
  identical: {"en":"<as in batch>","uk":"<as in batch>","v":"identical","ce":"<American/intl spelling>","cu":"<Ukrainian headword>","pos":"noun","br":false,"lab":["usage labels if any","1-2 topic labels"]}
  not_lemma: same fields plus "lv" (verdict of the lemma pair); if lv is identical fill pos/br/lab too.
  similar / false_friend / partial_false_friend: {"en","uk","v","ce","cu"} only.
Then validate: python3 -c "import json;json.load(open('${ROOT}/data/checked/${b}.json'))" and fix if needed.
Return the file path and number of objects written.`
}

phase('Check')
const res = await parallel(args.batches.map(b => () =>
  agent(prompt(b), { label: b, phase: 'Check', schema: RESULT, effort: 'low' }).then(r => r ? { b, ...r } : { b, failed: true })))
return { done: res.filter(r => r && !r.failed).length, failed: res.filter(r => !r || r.failed).map(r => r && r.b) }
