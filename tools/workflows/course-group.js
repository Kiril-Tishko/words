export const meta = {
  name: 'course-group',
  description: 'Group the words of one level into short topical lessons for the leveled course',
  phases: [{ title: 'Group' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, lessons: { type: 'number' }, words: { type: 'number' } }, required: ['file', 'lessons'] }

function prompt(g) {
  return `You are an applied linguist designing a course for Ukrainian speakers learning English with words that are the SAME in Ukrainian (taxi = таксі). The course has levels (A0 Starter, A1, A2, B1, B2, C1). Each level has topic sections, and each section has short lessons. A lesson teaches 6–10 words of ONE level through a short story written at that level. The owner said: "making stories with A0 words for A2 level doesn't make any sense". So a lesson only holds words of its own level, and the scene must suit that level (A0–A1: very concrete everyday things; B2–C1 can be more abstract).
Input: ${ROOT}/data/course/in-${g}.txt — lines "[LEVEL] english = ukrainian | band | part of speech | topic: … | family: … (optional) | e.g. example". Words are roughly sorted by topic.
Group EVERY word into lessons:
- 6–10 words per lesson (an A0 lesson may have 5–8). All words of a lesson have the same [LEVEL] tag.
- Each lesson is one concrete scene that a short story can tell (title 2–5 words, e.g. "At the café", "Max's first job", "A day at the zoo"). Group words that really meet in one scene.
- Words with the same "family" (very similar words such as mister / Mrs. / Miss, hotel / motel / hostel, dollar / cent) MUST be in the same lesson.
- Give each lesson a "section": a short, simple topic name for the level's table of contents. Use a small set of plain section names, reused across lessons, for example: People and family, Food and drink, Home, Town and shopping, Travel, Work and money, School and study, Health and body, Sport, Free time and culture, Media and technology, Nature and animals, Society, Science, History and world. Use 4–8 sections for A0–A2 and 6–12 for larger levels.
- Order the lessons from the most everyday and useful to the least, within the file.
Write ${ROOT}/data/course/group-${g}.json — a JSON array in course order:
[{"level": "A1", "section": "Food and drink", "title": "Pizza night", "words": ["pizza", "cola", ...]}, ...]
Use the english exactly as in the input. Validate with python3 that every input word appears exactly once, every lesson has words of one level only, and sizes are within limits. Fix until it passes.
No web search, no git, no other files.
Return: file path, number of lessons, number of words.`
}
phase('Group')
const res = await parallel(args.groups.map(g => () =>
  agent(prompt(g), { label: `group-${g}`, phase: 'Group', schema: RESULT, effort: 'medium' }).then(r => r ? { g, ...r } : { g, failed: true })))
return res
