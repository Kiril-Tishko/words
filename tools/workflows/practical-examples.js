export const meta = {
  name: 'practical-examples',
  description: 'Rewrite examples of common cards into short, practical sentences a learner would say',
  phases: [{ title: 'Rewrite' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, cards: { type: 'number' }, rewritten: { type: 'number' } }, required: ['file', 'cards'] }

function prompt(part) {
  const band = args.band || 'Top 2000 and Top 3000 (the 2,000–3,000 most used English words)'
  const len = args.len || '4–9 words each, A1–A2 words around the card word, simple tenses (mostly present; past only if natural)'
  return `You are an English teacher for Ukrainian learners, improving flashcard examples. Each card pairs an English word with the identical Ukrainian word; the Ukrainian word shows WHICH meaning the card teaches. Examples are English only.
Input: ${ROOT}/data/review/${part}.txt — cards of band(s) ${band}: "english = ukrainian [band · rank · share · pos]", then gram, say, 4 numbered examples, note.
Goal: the owner wants examples that are SIMPLE and PRACTICAL ("practical is more important"). For each card, keep the current examples if they already meet ALL of these rules; otherwise rewrite all 4:
- ${len}
- at least 2 of the 4 are things the learner would really SAY in daily life: a question, a request or a first-person sentence (in a shop, cafe, at work, school, on the phone, travelling, with friends)
- at most 1 sentence about a third person ("he/she/the president…"), and no stories about strangers
- every sentence uses the card's meaning (would a Ukrainian say the card's Ukrainian word here?) and shows a natural word partner (the "say" line helps)
- nothing US-specific (no US places, college sports, US politics), no names except Anna or Kyiv, no idioms, American spelling
Write ${ROOT}/data/qa/zz-ex-${part}.json — ONE JSON object keyed by the English word exactly as on the card, ONLY for cards you rewrite: {"senator": {"ex": ["...", "...", "...", "..."]}, ...}
Validate: python3 -c "import json;d=json.load(open('${ROOT}/data/qa/zz-ex-${part}.json'));assert all(len(v['ex'])==4 for v in d.values());print(len(d))"
No web search, no git, no other files.
Return: file path, number of cards read, number rewritten.`
}
phase('Rewrite')
const res = await parallel(args.parts.map(p => () =>
  agent(prompt(p), { label: p, phase: 'Rewrite', schema: RESULT, effort: 'high' }).then(r => r ? { p, ...r } : { p, failed: true })))
return res
