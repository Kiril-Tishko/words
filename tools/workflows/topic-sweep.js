export const meta = {
  name: 'topic-sweep',
  description: 'Topic-by-topic sweep for identical English–Ukrainian words the automatic matcher may have missed',
  phases: [{ title: 'Sweep', detail: 'one agent per topic; writes data/checked/sweep-<topic>-<round>.json' }],
}

const ROOT = '/home/user/words'
const RESULT = {
  type: 'object',
  properties: { file: { type: 'string' }, total: { type: 'number' } },
  required: ['file', 'total'],
}

function prompt(t) {
  const known = t.known ? `\n   Pairs ALREADY in our list for this topic are in ${ROOT}/${t.known} — read it and do NOT repeat them; find what is missing.` : ''
  return `You are helping build a COMPLETE list of English words that are the SAME word in Ukrainian (same meaning and same form — see the rules).

1. Read the rules in ${ROOT}/data/RUBRIC.md ("identical" verdict: letter-for-letter or sound-for-sound, h→г/х allowed, no added/dropped endings).${known}
2. Topic: **${t.title}** — ${t.detail}
   Go through the topic systematically, sub-area by sub-area, and list every identical English–Ukrainian pair you can find: everyday words, technical terms, archaic or old-fashioned English words, slang, and abbreviations read as words (DJ = діджей). Aim for completeness (often 100–300 pairs). Skip names of people, countries, cities, brands. Skip pairs where Ukrainian adds an ending (problem = проблема is NOT identical).
   Do not use web search.
3. Write a JSON array to ${ROOT}/data/checked/sweep-${t.key}-${t.round}.json:
   [{"en": "english headword (American/international spelling)", "uk": "ukrainian headword", "topic": "${t.key}"}, ...]
4. Validate: python3 -c "import json;d=json.load(open('${ROOT}/data/checked/sweep-${t.key}-${t.round}.json'));print(len(d))" and fix if it fails. Do not modify other files. Do not run git.
Every pair you list will be checked against English and Ukrainian dictionaries and by another reviewer, so list real words only.
Return: file path and number of pairs.`
}

phase('Sweep')
const results = await parallel(args.topics.map(t => () =>
  agent(prompt(t), { label: `sweep:${t.key}`, phase: 'Sweep', schema: RESULT }).then(r => r ? { topic: t.key, ...r } : { topic: t.key, failed: true })))
return results
