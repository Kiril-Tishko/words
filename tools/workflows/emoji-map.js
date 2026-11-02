export const meta = {
  name: 'emoji-map',
  description: 'Pick a Noto emoji picture for cards whose meaning a picture shows clearly (concrete things)',
  phases: [{ title: 'Pick' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, cards: { type: 'number' }, pictures: { type: 'number' } }, required: ['file', 'cards'] }

function prompt(p) {
  return `You are choosing pictures for the backs of flashcards for Ukrainian learners of English. Each card pairs an English word with the identical Ukrainian word (taxi = таксі). The Ukrainian word shows WHICH meaning the card is about.
Input: ${ROOT}/data/images/cand-${p}.txt — lines "english = ukrainian | part of speech | topics | e.g. example sentence".
Pictures available: the Noto emoji set. All names, one per line, are in ${ROOT}/data/images/noto-names.txt (e.g. taxi, pizza, hotel, guitar, tiger, laptop, soccer-ball, man-technologist, woman-pilot, ambulance, high-voltage). Search it with grep (grep -i -E "taxi|cab" ${ROOT}/data/images/noto-names.txt); do not read it whole.
For EVERY card, decide whether one emoji clearly shows the card's meaning, so that a learner who sees the picture thinks of this word:
- YES for concrete things: objects, food, drinks, animals, plants, vehicles, places and buildings, sports, musical instruments, clothes, body parts, jobs and people with a clear emoji (doctor → health-worker, pilot → pilot), weather, devices, well-known symbols (dollar → dollar-banknote, euro → euro-banknote).
- NO for abstract words (idea, fact, process, method, period), for adjectives, verbs and interjections unless the picture is unmistakable (OK → ok-hand is fine), and whenever the emoji would show ANOTHER meaning of the English word (bar = бар is a place for drinks: a cocktail glass is fine, a chocolate bar is not). Never use flags of countries.
- Prefer the most typical picture (taxi → taxi, not oncoming-taxi; hotel → hotel).
- When no picture is clearly right, skip the card. A wrong picture is worse than none.
Write ${ROOT}/data/images/emoji-${p}.json — ONE JSON object {"<english exactly as in the line>": "<emoji name exactly as in noto-names.txt>", ...}, only for cards that get a picture.
Validate: python3 -c "import json;d=json.load(open('${ROOT}/data/images/emoji-${p}.json'));n=set(open('${ROOT}/data/images/noto-names.txt').read().split());bad=[k for k,v in d.items() if v not in n];print(len(d),'bad names:',bad)" and fix any bad names.
No web search, no git, no other files.
Return: file path, number of cards read, number of pictures chosen.`
}
phase('Pick')
const res = await parallel(args.parts.map(p => () =>
  agent(prompt(p), { label: `emoji-${p}`, phase: 'Pick', schema: RESULT, effort: 'medium' })
    .then(r => r ? { p, ...r } : { p, failed: true })))
return res
