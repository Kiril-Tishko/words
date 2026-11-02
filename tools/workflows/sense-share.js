export const meta = {
  name: 'sense-share',
  description: 'Linguist estimate: how much of an English word\'s everyday use is in the meaning shown on the card',
  phases: [{ title: 'Sense share' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, words: { type: 'number' } }, required: ['file', 'words'] }
function prompt(b) {
  return `You are a corpus linguist. A site teaches English words that are identical in Ukrainian, sorted by how often the English word is used IN THE MEANING SHOWN ON THE CARD.
Batch: ${ROOT}/data/candidates/sense/${b}.txt — one card per line: "english = ukrainian | part of speech | topic" (+ "| PHRASE" for multi-word or hyphenated items).
The Ukrainian word tells you which single meaning the card is about.

For each ordinary line, estimate "s": the percentage (0–100) of ALL everyday uses of the English word form — counting all its meanings and parts of speech — that are in THIS meaning and part of speech. Think of general English (speech, web, news, books). Calibration:
  computer = комп'ютер → 100 · class = клас (school class) → 50 · show = шоу (noun: TV show, performance) → 35 · tank = танк (military tank) → 25 · court = корт (sports court) → 10 · country = кантрі (country music) → 2 · like = лайк (a like on social media) → 0.5 · take = тейк (one take in filming) → 0.2 · IT = айті (information technology; share of all "it"/"IT") → 0.2 · are = ар (unit of area) → 0.001
For "| PHRASE" lines, estimate "pm": how many times the phrase occurs per million words of general English (e.g. hot dog → 6, rock and roll → 4, time-out → 3, know-how → 2, all-in → 1, show business → 2, face control → 0.05).
Be realistic, not generous: rare technical or narrow meanings get small numbers.

Write ${ROOT}/data/sense/${b}.json — one JSON object keyed by the English word exactly as in the batch:
  {"computer": {"s": 100}, "country": {"s": 2}, "hot dog": {"pm": 6}, ...}
Every line must have an entry. Validate with python3 -c "import json;d=json.load(open('${ROOT}/data/sense/${b}.json'));print(len(d))". No web search, no git, no other files.
Return the file path and number of entries.`
}
phase('Sense share')
const res = await parallel(args.batches.map(b => () =>
  agent(prompt(b), { label: b, phase: 'Sense share', schema: RESULT, effort: 'medium' }).then(r => r ? { b, ...r } : { b, failed: true })))
return { done: res.filter(r => r && !r.failed).length, failed: res.filter(r => !r || r.failed).map(r => r && r.b) }
