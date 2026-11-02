export const meta = {
  name: 'full-vocabulary-scan',
  description: 'Linguists scan the whole English and Ukrainian vocabulary (chunks) for identical words the list is missing',
  phases: [{ title: 'Scan' }],
}
const ROOT = '/home/user/words'
const RESULT = { type: 'object', properties: { file: { type: 'string' }, count: { type: 'number' } }, required: ['file', 'count'] }
function prompt(name) {
  const en = name.startsWith('en-')
  return `You are an expert linguist fluent in English and Ukrainian. Rules for "identical" words: ${ROOT}/data/RUBRIC.md (read it).
Input: ${ROOT}/data/fullscan/${name}.txt — 1,200 ${en ? 'English' : 'Ukrainian'} words, one per line (some are junk tokens, names or inflected forms; skip those).
Task: find EVERY word in the list that has an IDENTICAL ${en ? 'Ukrainian' : 'English'} word — same main meaning and the same form (transliterated by spelling or by sound, with the rubric's adaptations, h→г/х allowed, no added or dropped endings). Include everyday words, modern loanwords and IT/slang words even if they are not in dictionaries yet (e.g. fallback = фолбек, skill = скіл), technical and archaic words, abbreviations read as words${en ? '' : ', and hyphenated compounds whose parts are English (слайд-шоу = slide show, проксі-сервер = proxy server)'}. Skip names of people/places/brands and words that only look alike.
Go line by line and be exhaustive — every find is checked again later.
No web search; do not open other project files; no git.
Write ${ROOT}/data/fullscan/found-${name}.json — a JSON array: [{"en": "<English word>", "uk": "<Ukrainian word>"}, ...] (${en ? '"en" exactly as in the list' : '"uk" exactly as in the list'}); [] if none.
Validate with python3 -c "import json;print(len(json.load(open('${ROOT}/data/fullscan/found-${name}.json'))))".
Return the file path and the number of pairs.`
}
phase('Scan')
const res = await parallel(args.chunks.map(c => () =>
  agent(prompt(c), { label: c, phase: 'Scan', schema: RESULT, effort: 'medium' }).then(r => r ? { c, ...r } : { c, failed: true })))
return { done: res.filter(r => r && !r.failed).length, failed: res.filter(r => !r || r.failed).map(r => r && r.c) }
