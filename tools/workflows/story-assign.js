export const meta = {
  name: 'story-assign',
  description: 'Place every remaining word into the best chapter of the linguist outline for the Stories tab',
  phases: [{ title: 'Assign' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, words: { type: 'number' }, newChapters: { type: 'number' } }, required: ['file', 'words'] }

function prompt(n) {
  return `You are helping a linguist build the "Stories" tab of a flashcard site for Ukrainian speakers learning English. Every card pairs an English word with the identical Ukrainian word (the Ukrainian word shows which meaning the card teaches: bar = бар is a place for drinks).
The linguist's outline is ${ROOT}/data/stories/outline.json: parts (in course order) and chapters. Each chapter is one concrete scene ("scene") with a title and anchor words. A short story will later use all the words of a chapter. Read the whole outline first.
Your input: ${ROOT}/data/stories/todo-${n}.txt — words that are not anchors yet. Each line is "english = ukrainian | band | part of speech | topics | e.g. example".
For EVERY word, choose the ONE chapter whose scene would most naturally use this word in its card meaning.
- Prefer scenes where the word really occurs (passport → airport or hotel check-in), not just the same broad topic.
- Common words (Top 1000–5000) should go to early, everyday chapters when they fit there. Rare or specialized words go to the matching specialized scene.
- Do not put a word into a chapter that already has a near-synonym of it, if another good scene exists.
- Exclamations, interjections and sounds belong to the Exclamations part.
- If no chapter fits at all, use "new:<part id>:<short scene title>" (e.g. "new:p07:At the car wash"). Use the SAME new title for words that belong together, and use new chapters rarely.
Write ${ROOT}/data/stories/assign-${n}.json — ONE JSON object {"<english exactly as in the line>": "<chapter id or new:...>", ...} with every word of your input.
Validate: python3 -c "import json;d=json.load(open('${ROOT}/data/stories/assign-${n}.json'));o=json.load(open('${ROOT}/data/stories/outline.json'));ids={c['id'] for c in o['chapters']};w=[l.split(' = ')[0] for l in open('${ROOT}/data/stories/todo-${n}.txt') if l.strip()];print(len(w),len(d),[x for x in w if x not in d][:5],[v for v in d.values() if v not in ids and not v.startswith('new:')][:5])" and fix any missing words or unknown ids.
No web search, no git, no other files.
Return: file path, number of words, number of new-chapter suggestions.`
}
phase('Assign')
const res = await parallel(args.parts.map(n => () =>
  agent(prompt(n), { label: `assign-${n}`, phase: 'Assign', schema: RESULT, effort: 'medium' }).then(r => r ? { n, ...r } : { n, failed: true })))
return res
