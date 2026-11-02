export const meta = {
  name: 'expert-review',
  description: 'ESL teacher, lexicographer and UX designer review the flashcard site and its data',
  phases: [{ title: 'Review' }],
}
const ROOT = '/home/user/words'
const RESULT = {
  type: 'object',
  properties: {
    file: { type: 'string' },
    top_issues: { type: 'array', items: { type: 'string' }, description: 'the most important problems, each with the concrete fix, most important first' },
  },
  required: ['file', 'top_issues'],
}
const CONTEXT = `Project: a website that teaches English to Ukrainian speakers with flip cards of English words that are IDENTICAL in Ukrainian (taxi = таксі, computer = комп'ютер). Owner's wishes: very simple minimal design; one card at a time or a 4-per-row grid; card front = English word, "=", Ukrainian word below; back = 4 examples + a note only if needed; notes and labels must talk only about the ENGLISH word (Ukrainian word is known); categories are frequency bands of the English word IN THE MEANING ON THE CARD (Top 400, Top 1000 … Rare); examples for the most frequent words must be very simple (A0–A1) and practical; a recorded pronunciation; "My words" + basic training; a filter hides pairs whose Ukrainian word is slang.
Read: ${ROOT}/README.md, ${ROOT}/data/RUBRIC.md, ${ROOT}/docs/review/cards-sample.txt (120 cards across all bands with examples/notes/labels), and look at the screenshots in ${ROOT}/docs/review/*.png (use the Read tool on each PNG). The full data is ${ROOT}/data/words.json (10,812 words; use grep/python to sample more) and examples in ${ROOT}/data/examples/*.json.`

const ROLES = [
  { key: 'teacher', who: 'an experienced teacher of English to Ukrainian-speaking learners (ESL methodology, CEFR, vocabulary teaching)',
    focus: 'What is going wrong from a TEACHING perspective? Which cards mislead or confuse learners, which words should be ordered/grouped differently, are the examples level-appropriate and practical, are notes useful, is the frequency order sensible for learning, what is missing for learning (e.g. articles, plural forms, stress, phrase patterns), how to make memorising easier, training mode ideas. Be concrete with real examples from the data.' },
  { key: 'lexicographer', who: 'a bilingual English–Ukrainian lexicographer',
    focus: 'Accuracy: wrong or doubtful pairs (meaning or form), pairs that are not really identical, Ukrainian words that are not standard, wrong part of speech, wrong American/British spelling choices, wrong British-only flags, examples that use the wrong meaning or contain errors, frequency/band placements that are clearly wrong for the meaning shown. Sample widely (grep data/words.json and data/examples) and give counts/estimates of how common each problem is, with examples.' },
  { key: 'ux', who: 'a senior product designer and front-end reviewer',
    focus: `Design and bugs. Review the screenshots and the page code ${ROOT}/site/app.html (the generated page is ${ROOT}/index.html with data ${ROOT}/words.js). Find visual problems, inconsistencies, inconveniences, accessibility issues, mobile problems, bugs in the JavaScript (event handling, state, paging, audio playback, training mode, localStorage, hash routing), and performance issues with ~4,000 cards. Keep the owner's minimal style. Give concrete, small fixes (CSS/JS level).` },
]
phase('Review')
const res = await parallel(ROLES.map(r => () => agent(
  `You are ${r.who}. ${CONTEXT}\n\nYour focus: ${r.focus}\n\nWrite your review to ${ROOT}/docs/review/${r.key}.md: a short summary, then a prioritised list of problems — each with concrete examples and the exact fix you recommend. Do not modify any other file. No git.\nReturn the file path and your top issues (most important first, each with its fix).`,
  { label: `review:${r.key}`, phase: 'Review', schema: RESULT, effort: 'high' }).then(x => x ? { role: r.key, ...x } : { role: r.key, failed: true })))
return res
