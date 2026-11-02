export const meta = {
  name: 'check-word-batches',
  description: 'Check English–Ukrainian candidate word batches against the rubric and save verdicts',
  phases: [{ title: 'Check', detail: 'one agent per batch file; writes data/checked/<batch>.json' }],
}

const ROOT = '/home/user/words'
const RESULT = {
  type: 'object',
  properties: {
    file: { type: 'string' },
    total: { type: 'number' },
    identical: { type: 'number' },
    examples: { type: 'array', items: { type: 'string' }, description: 'up to 8 identical pairs as "en=uk"' },
  },
  required: ['file', 'total', 'identical'],
}

function verifyPrompt(b) {
  return `You are checking candidate English–Ukrainian word pairs for a learner's website of words that are the SAME in English and Ukrainian.

1. Read ${ROOT}/data/RUBRIC.md (the rules — follow them exactly) and the batch file ${ROOT}/data/candidates/${b}.txt.
   Batch format: each "## english" block gives the English word with [CEFR level; word frequency (zipf, 1=very rare, 7=very common)], Wiktionary usage tags, a few English glosses ("en:"), then candidate lines "- ukrainian [how it matched; ev = dictionaries that list the pair as translations (muse, wikt_tr, gloss_match, dict); zipf-uk; uk-tags] uk-gloss: ...".
   The candidates were produced automatically (transliteration + dictionaries), so many are wrong: names, inflected forms, coincidences. Dictionary evidence is a hint, not proof.
2. Decide a verdict for EVERY candidate line, using your own knowledge of both languages and the rubric. Do not use web search.
3. Write a JSON array to ${ROOT}/data/checked/${b}.json — one object per candidate line, in batch order:
   {"en": "<english exactly as in the batch>", "uk": "<ukrainian exactly as in the batch>", "v": "<verdict>", "ce": "<canonical English>", "cu": "<canonical Ukrainian>", "pos": "<pos>", "br": false, "lab": ["..."], "note": ""}
   - verdict one of: identical, similar, false_friend, partial_false_friend, proper_noun, not_lemma, unrelated.
   - identical: fill ce, cu, pos, br, lab (usage labels that apply + 1–2 topic labels). note only if a learner really needs it (e.g. a meaning difference, a common other spelling).
   - not_lemma: fill ce/cu with the lemma pair and add "lv" = the verdict the LEMMA pair would get (identical/similar/...). If it would be identical, also fill pos, br, lab.
   - similar, false_friend, partial_false_friend: fill ce, cu and a very short note (what differs).
   - unrelated, proper_noun: only en, uk, v.
4. Validate the file: python3 -c "import json;d=json.load(open('${ROOT}/data/checked/${b}.json'));print(len(d))" — fix and rewrite if it fails, and make sure every candidate line has an object.
Do not modify any other file. Do not run git.
Return: file path, total objects, number of identical (including not_lemma whose lv is identical), and up to 8 identical examples "en=uk".`
}

function scanPrompt(b) {
  return `You are helping build a learner's website of words that are the SAME in English and Ukrainian (borrowings / international words with the same meaning).

1. Read ${ROOT}/data/RUBRIC.md (the rules — follow them exactly) and the batch file ${ROOT}/data/candidates/${b}.txt.
   Each line is "ukrainian :: english look-alike 1, english look-alike 2, ...". The look-alikes were produced by blind automatic transliteration, so almost all lines are pure coincidences (native Ukrainian words that happen to look like some English word). Your job is to find the few real ones.
2. Go through EVERY line. Report a pair when the Ukrainian word and one of its listed English words are the same word with the same meaning (verdict identical or similar), or are a clear false friend / partial false friend where both words are reasonably common. Skip coincidences, names of people/places/brands, and lines where you are unsure the English word even means that. Ukrainian words may be inflected forms: then report the lemma pair with v = "not_lemma" and "lv" = verdict of the lemma pair.
   Do not use web search.
3. Write a JSON array of ONLY the reported pairs to ${ROOT}/data/checked/${b}.json (write [] if none):
   {"en": "<english as listed>", "uk": "<ukrainian as listed>", "v": "<verdict>", "ce": "<canonical English>", "cu": "<canonical Ukrainian>", "pos": "<pos>", "br": false, "lab": ["..."], "note": ""}
   For identical (or not_lemma with lv identical) fill pos, br, lab (usage labels + 1–2 topic labels from the rubric); note only if really needed.
4. Validate: python3 -c "import json;d=json.load(open('${ROOT}/data/checked/${b}.json'));print(len(d))" — fix if it fails.
Do not modify any other file. Do not run git.
Return: file path, total objects written, number identical, up to 8 identical examples "en=uk".`
}

phase('Check')
const batches = args.batches
const results = await parallel(batches.map(b => () =>
  agent(b.startsWith('scan-') ? scanPrompt(b) : verifyPrompt(b), { label: b, phase: 'Check', schema: RESULT })
    .then(r => r ? { batch: b, ...r } : { batch: b, failed: true })
))
const ok = results.filter(r => r && !r.failed)
const failed = results.filter(r => !r || r.failed).map(r => r ? r.batch : '?')
log(`${ok.length} batches done, ${failed.length} failed`)
return { slice: args.tag, done: ok.length, failed, identical: ok.reduce((s, r) => s + (r.identical || 0), 0), examples: ok.slice(0, 5).map(r => r.examples) }
