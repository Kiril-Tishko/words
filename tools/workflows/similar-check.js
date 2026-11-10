export const meta = { name: 'similar-check', description: 'Strictly check almost-the-same pairs', phases: [{ title: 'Check' }] }
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, kept: { type: 'number' } }, required: ['file', 'kept'] }
function prompt(i) {
  return `You are a strict bilingual English–Ukrainian linguist. Input: ${ROOT}/data/similar2/check-${i}.txt — lines "english = ukrainian", claimed to be words that SOUND ALMOST THE SAME and MEAN THE SAME (problem = проблема, music = музика, police = поліція).
Keep a pair ONLY if all are true: a Ukrainian learner would hear/see the similarity at once (team = команда, rest = решта, won = вона are NOT similar); the MAIN everyday meaning of the English word is the same (matter = матерія, report = рапорт are not); the Ukrainian word is normal standard Ukrainian (not slang like файний).
Write ${ROOT}/data/similar2/ok-${i}.json — a JSON array of the KEPT pairs [{"en": "...", "uk": "..."}]. Validate it with python3. No web search, no git, no other files. Return: file path and number kept.`
}
phase('Check')
const res = await parallel(args.parts.map(i => () => agent(prompt(i), { label: `check-${i}`, phase: 'Check', schema: RESULT, effort: 'medium' }).then(r => r ? { i, ...r } : { i, failed: true })))
return res
