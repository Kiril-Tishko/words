export const meta = {
  name: 'sweep2',
  description: 'Second-round topic sweeps for modern English loanwords in Ukrainian that the list may still miss',
  phases: [{ title: 'Sweep' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, total: { type: 'number' } }, required: ['file', 'total'] }

function prompt(t) {
  return `You are a bilingual English–Ukrainian lexicographer helping build a COMPLETE list of English words that are the SAME word in Ukrainian: same meaning, and the same form written in Ukrainian letters by spelling or by sound. Rules: ${ROOT}/data/RUBRIC.md (read it once). h→г/х is allowed. An added or dropped ending is NOT identical: problem = проблема is out.
Our current list (about 13,000 pairs, one "english = ukrainian" per line) is ${ROOT}/data/sweeps/known-all.txt. Do NOT read it whole; check candidates with grep, e.g. grep -i -E "^(workout|shortcut) = " ${ROOT}/data/sweeps/known-all.txt.

Topic: **${t.title}** — ${t.detail}
Modern Ukrainian has many recent English loanwords: воркаут, шорткат, читинг, дедлайн, фідбек, кринж, бранч, худі, спойлер, стартап, коворкінг. Many are not in older dictionaries. Our audit found that most missing pairs are such loanwords and compounds.
1. Brainstorm systematically, sub-area by sub-area, every English word or phrase in this topic that Ukrainians use as a loanword in the same meaning. Include slang, professional jargon, compounds (бізнес-ланч, фуд-корт) and abbreviations read as words. Aim for 150–300 candidates.
2. Check every candidate against the list with grep, in batches, and keep ONLY pairs that are missing.
3. Keep a pair only if:
   - the English word is a real English word in that meaning
   - the Ukrainian word is really used (you have seen it in Ukrainian media, social networks or speech), in its usual modern spelling
   - the forms match by the rubric
   Skip names of people, places and brands.
4. Write ${ROOT}/data/checked/sweep-${t.key}-r2.json — a JSON array: [{"en": "english (American spelling)", "uk": "українське", "topic": "${t.key}"}, ...]
   Validate: python3 -c "import json;d=json.load(open('${ROOT}/data/checked/sweep-${t.key}-r2.json'));print(len(d))"
No web search, no git, no other files. Every pair will be checked against dictionaries and by a second skeptical reviewer, so list real words only.
Return: file path and number of pairs.`
}
phase('Sweep')
const res = await parallel(args.topics.map(t => () =>
  agent(prompt(t), { label: `sweep2:${t.key}`, phase: 'Sweep', schema: RESULT, effort: 'medium' })
    .then(r => r ? { topic: t.key, ...r } : { topic: t.key, failed: true })))
return res
