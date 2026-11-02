export const meta = {
  name: 'word-marks',
  description: 'Mark cards whose English word Ukrainians use as an English word (anglicism) or which a Ukrainian would not expect in English (surprise)',
  phases: [{ title: 'Mark' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, words: { type: 'number' }, anglicism: { type: 'number' }, surprise: { type: 'number' } }, required: ['file', 'words'] }

function prompt(b) {
  return `You are a bilingual Ukrainian–English linguist. On a flashcard site every card pairs an English word with the IDENTICAL Ukrainian word (taxi = таксі). The owner wants two kinds of cards marked.
Input: ${ROOT}/data/marks/in-${b}.txt — lines "english = ukrainian | band | part of speech | e.g. example".
For EVERY line decide one of:
- "anglicism": a Ukrainian speaker immediately feels the Ukrainian word is an English word. Ukrainians use it as English, often only about English-speaking life or as slang or jargon, and it is not really a Ukrainian word.
  Examples: Mr. = містер, Mrs. = місіс, stuff = стаф, sorry = сорі, please = пліз, bro = бро, cool = кул, weekend = вікенд, deadline = дедлайн, hype = хайп, like = лайк, crush = краш, outfit = аутфіт.
- "surprise": a Ukrainian would NOT expect this word to exist in English. It feels Ukrainian, Slavic or local, or it is a borrowing Ukrainians think of as their own, but English has it too.
  Examples: steppe = степ, dacha = дача, borscht = борщ, cossack = козак, hetman = гетьман, oblast = область, hryvnia = гривня, kefir = кефір, pogrom = погром, babushka = бабушка, samovar = самовар, kurgan = курган, bandura = бандура, sable = соболь, mammoth = мамонт, chai = чай, bazaar = базар.
- "none": an ordinary international word that everyone expects in both languages (hotel, computer, president, idea, chemistry terms…).
Most words are "none". Use "anglicism" for clear cases only. Use "surprise" when a typical Ukrainian learner would really say "I didn't know that is English!"
Write ${ROOT}/data/marks/out-${b}.json — ONE JSON object with ONLY the marked words: {"<english exactly as in the line>": "anglicism" | "surprise", ...}.
Validate: python3 -c "import json;d=json.load(open('${ROOT}/data/marks/out-${b}.json'));w={l.split(' = ')[0] for l in open('${ROOT}/data/marks/in-${b}.txt') if l.strip()};print(len(d),[k for k in d if k not in w][:5],set(d.values()))"
No web search, no git, no other files.
Return: file path, number of words read, numbers marked anglicism and surprise.`
}
phase('Mark')
const res = await parallel(args.batches.map(b => () =>
  agent(prompt(b), { label: `marks-${b}`, phase: 'Mark', schema: RESULT, effort: 'medium' }).then(r => r ? { b, ...r } : { b, failed: true })))
return { done: res.filter(r => !r.failed).length, failed: res.filter(r => r.failed).map(r => r.b),
  anglicism: res.reduce((s, r) => s + (r.anglicism || 0), 0), surprise: res.reduce((s, r) => s + (r.surprise || 0), 0) }
