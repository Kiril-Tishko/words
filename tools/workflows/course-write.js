export const meta = {
  name: 'course-write',
  description: 'Write a short story for each course lesson at exactly the lesson level, using its words in order',
  phases: [{ title: 'Write' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, lessons: { type: 'number' }, dropped: { type: 'number' } }, required: ['file', 'lessons'] }

const RULES = `   A0 (Starter): 4–7 sentences of 3–7 words. Only "be", "have", "like", "can", "want" in the present simple, and imperatives. Only the very first English words around the lesson words (I, you, my, this, is, big, small, good, red, one, two, here, look…). Very concrete: things you can see. Example: "This is Anna. Anna has a camera. Look! A big tiger!"
   A1: 5–8 sentences of at most 9 words. Present simple and present continuous, can, there is / there are. Everyday words only.
   A2: 6–9 sentences of at most 12 words. Past simple and "going to" are fine. Everyday words.
   B1: 6–10 sentences of at most 16 words. All common tenses. Other words at B1 or easier.
   B2: 6–10 natural sentences. Other words at B2 or easier.
   C1: 6–10 natural sentences. Clear and not literary.`

function prompt(b) {
  return `You are an English teacher writing the stories of a course for Ukrainian speakers. Every course word is the SAME in Ukrainian (taxi = таксі), and the Ukrainian word shows which meaning the lesson teaches (bar = бар is a place for drinks).
The owner's rule: the story must be at the level of its words. "Making stories with A0 words for A2 level doesn't make any sense." So an A0 lesson gets an A0 story, a B2 lesson a B2 story.
Your batch: ${ROOT}/data/course/batch-${b}.json — a list of lessons: {"id", "level", "section", "title", "words": [{"en", "uk", "pos", "ex": example sentence}]}.
For EVERY lesson:
1. "order": the lesson words in the order the story uses them.
2. "story": a short, practical, everyday English story of the lesson's scene that uses EVERY lesson word exactly once, in its card meaning. Mark each lesson word as [[word]] (the english exactly as on the card), or [[form|word]] for another form ([[photos|photo]]). Mark nothing else.
   Level rules (follow the lesson's "level" strictly; all the other words in the story must be at that level or easier):
${RULES}
   Use the recurring cast: Anna (a student in Kyiv), her friend Max, Anna's mama, dad, little brother Taras and their grandparents, Max's sister Sofia, friends Lisa and Ira. Something small should happen, with a little ending. English only, American spelling, kind and suitable for teenagers. No real people or brands.
3. "title": the lesson title, kept or improved (2–5 words, at the lesson's level).
4. A word that cannot fit in its card meaning may go to "drop" (rarely).
Write ${ROOT}/data/course/story-${b}.json — ONE JSON object: {"<lesson id>": {"title": "...", "order": [...], "story": "...", "drop": []}, ...}
Validate with python3: every word in "order" appears exactly once as [[word]] or [[form|word]]; "order" + "drop" equal the lesson words; count the words per sentence and fix sentences that break the level's limit. Fix until it passes.
No web search, no git, no other files.
Return: file path, number of lessons, number of dropped words.`
}
phase('Write')
const res = await parallel(args.batches.map(b => () =>
  agent(prompt(b), { label: `course-${b}`, phase: 'Write', schema: RESULT, effort: 'high' }).then(r => r ? { b, ...r } : { b, failed: true })))
return res
