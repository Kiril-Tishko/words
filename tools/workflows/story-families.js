export const meta = {
  name: 'story-families',
  description: 'Find families of very similar words (like Miss and Mr.) across story chapters, one kind of family per agent',
  phases: [{ title: 'Find' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, families: { type: 'number' } }, required: ['file', 'families'] }
const KINDS = {
  people: 'forms of address and titles (mister, Mrs., Miss, sir, madam, lady, gentleman, monsieur, madame, mademoiselle, Herr, Frau, senpai, amigo…), family members (mama, papa, baby, sibling, cousin, grandma…), and male/female or role pairs (actor/actress, steward/stewardess, host/hostess, baron/baroness, king/queen titles…)',
  synonyms: 'near-synonyms and short/long forms of the same thing (hotel/motel/hostel, cop/policeman/constable, champion/champ, admin/administrator, update/upgrade, marijuana/cannabis/ganja, lava/magma, laptop/notebook, film/movie-type pairs, bus/minibus…) — words a learner should see side by side to learn the difference',
  sets: 'small closed sets of the same kind: currencies (dollar, euro, cent, penny, dime, ruble…), units of measure (meter, kilometer, gram, kilo, liter…), music genres, dances, martial arts, ball games, card and board games, dog breeds, cocktails or coffee drinks, chess pieces, planets, Greek letters, months or days if present',
}
function prompt(kind) {
  return `You are an applied linguist working on the "Stories" tab of a flashcard site for Ukrainian speakers learning English (each card: an English word = the identical Ukrainian word). Words are grouped into 200 story chapters. The owner says: "words that are very similar put together (like Miss and Mr)" — very similar words must be learned in ONE chapter, but now they are spread over different chapters.
Input: ${ROOT}/data/stories/chapters-now.txt — one line per chapter: "chapter id | part title (part id) | chapter title | English words of the chapter, comma separated".
Your kind of family: ${KINDS[kind]}.
Go through ALL 200 chapters and list every family of this kind that has members in two or more chapters (a family already complete in one chapter needs nothing). Skip the Exclamations part. Do not group words that only look alike (cash/cache). A word belongs to one family only; a family has 2–12 words, using exact strings from the input.
For each family choose the target: the existing chapter whose scene fits the family best and that already holds most of its members, as long as it stays at most 18 words after adding the others; otherwise "new" with a part id, a 2–5 word title and a one-sentence scene using the cast (Anna, a student in Kyiv; her friend Max; Anna's mama, dad, brother Taras and grandparents; Max's sister Sofia; friends Lisa and Ira).
Write ${ROOT}/data/stories/families-${kind}.json — a JSON array like
[{"name": "Mister, Mrs. and Miss", "words": ["mister", "Mrs.", "Miss", "sir", "madam", "lady", "gentleman"], "target": "c002"},
 {"name": "Martial arts", "words": ["karate", "kung fu", "judo"], "target": "new", "part": "p10", "title": "Martial arts club", "scene": "Taras tries karate, judo and kung fu."}]
Validate with python3 that every word exists in the input and that targets are existing chapter ids or "new". No web search, no git, no other files. Be quick: about 5 minutes.
Return: file path and number of families.`
}
phase('Find')
const res = await parallel(args.kinds.map(k => () =>
  agent(prompt(k), { label: `families-${k}`, phase: 'Find', schema: RESULT, effort: 'medium' }).then(r => r ? { k, ...r } : { k, failed: true })))
return res
