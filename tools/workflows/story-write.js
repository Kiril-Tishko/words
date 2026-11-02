export const meta = {
  name: 'story-write',
  description: 'Write a short, simple English story per chapter that uses the chapter words in order (Stories tab)',
  phases: [{ title: 'Write' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, chapters: { type: 'number' }, dropped: { type: 'number' } }, required: ['file', 'chapters'] }

function prompt(b) {
  return `You are an English teacher and a good storyteller, writing the "Stories" tab of a flashcard site for Ukrainian speakers learning English. Every card pairs an English word with the IDENTICAL Ukrainian word (taxi = таксі). The Ukrainian word shows which meaning the card teaches (bar = бар: a place for drinks, not a chocolate bar).
A linguist grouped the words into chapters; each chapter is one scene. Your batch: ${ROOT}/data/stories/batch-${b}.json — a list of chapters: {"id", "part", "title", "scene", "level", "words": [{"en", "uk", "band", "pos", "ex": example sentence}]}.
For EVERY chapter in your batch:
1. Put the chapter's words in the order a story would naturally use them ("order").
2. Write the story ("story"): a short English story of the scene, 4–12 sentences, that uses EVERY chapter word exactly once, in that order, in the card's meaning.
   - Mark each chapter word in the text as [[word]], with the english exactly as on the card. If you use another form, write [[form|word]], for example [[hotels|hotel]] or [[photos|photo]].
   - Do not mark any other words.
   - Level by "level": A1 = present simple, short sentences of at most 9 words, everyday vocabulary. A2 = simple tenses, up to 12 words. B1 = natural sentences, up to 16 words, other words still simple.
   - Use the recurring cast: Anna (a student in Kyiv) and her friend Max, plus their family, friends and colleagues as needed. Make it a real little story with something happening and a small ending, and keep it practical and everyday where possible.
   - English only, American spelling. No real people or brands, no politics about real countries. Keep it kind and suitable for teenagers.
   - For the Exclamations part, write a short dialogue: a few lines, each starting with a name and a colon.
   - If a chapter has "old_story", it is the chapter's previous story: keep its plot, cast and tone, and work the new words in naturally. Very similar words (mister / Mrs. / Miss; hotel / motel / hostel; dollar / cent / penny) are in one chapter on purpose, so the learner sees them side by side: make the story show how they differ or go together.
3. "title": keep the linguist's title, or improve it (2–5 words).
4. If a word really cannot fit this scene in its card meaning, leave it out of the story and list it in "drop". Use "drop" rarely. Never invent words that are not in the chapter, and never mark them.
5. If a chapter has more than 16 words, you may split it into two chapters: keep the id for the first and use the id + "b" for the second, each with its own title, order and story.
Write ${ROOT}/data/stories/story-${b}.json — ONE JSON object: {"c001": {"title": "...", "order": ["en", ...], "story": "...", "drop": []}, ...}.
Validate with python3: for each chapter, every word in "order" must appear exactly once as [[word]] or [[form|word]] in "story"; "order" + "drop" must equal the chapter's words. Fix until it passes.
No web search, no git, no other files.
Return: file path, number of chapters written, number of dropped words.`
}
phase('Write')
const res = await parallel(args.batches.map(b => () =>
  agent(prompt(b), { label: `story-${b}`, phase: 'Write', schema: RESULT, effort: 'high' }).then(r => r ? { b, ...r } : { b, failed: true })))
return res
