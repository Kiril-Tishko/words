export const meta = {
  name: 'cross-check-identical',
  description: 'Second, independent and skeptical check of word pairs judged identical; sets the level of the shared meaning',
  phases: [{ title: 'Cross-check', detail: 'one agent per cross batch; writes data/checked/cross-<n>.json' }],
}

const ROOT = '/home/user/words'
const RESULT = {
  type: 'object',
  properties: {
    file: { type: 'string' },
    total: { type: 'number' },
    identical: { type: 'number' },
    overturned: { type: 'array', items: { type: 'string' }, description: 'up to 10 pairs you changed from identical, as "en=uk -> verdict"' },
  },
  required: ['file', 'total', 'identical'],
}

function prompt(b) {
  return `You are the SECOND, independent checker for a learner's website of English words that are the SAME in Ukrainian. A first checker already judged each pair below; your job is to catch their mistakes. Be skeptical — a wrong word on the site is worse than a missing one.

1. Read the rules in ${ROOT}/data/RUBRIC.md, then the batch ${ROOT}/data/candidates/${b}.txt.
   Each line: "english = ukrainian | first: <first verdict>; pos; list level <level for this word+pos in CEFR-J/Octanove/Cambridge Starters lists> (lists: <levels per part of speech>); british; labels; note".
2. For EVERY line decide the final verdict (identical, similar, false_friend, partial_false_friend, proper_noun, unrelated). Overturn "identical" when:
   - the shared meaning is not a main, everyday meaning of the word in BOTH languages for a learner (e.g. the Ukrainian word only covers a rare/technical sense while the English word's main sense is different → partial_false_friend);
   - the form differs beyond the rubric's allowed adaptations (an added/dropped ending or suffix → similar);
   - it is a proper noun, a brand, or a nationality used as a name;
   - the Ukrainian word is not a real, standard Ukrainian word (misspelling, Russianism, nonce form) — if a standard identical form exists, give it in cu instead;
   - a written abbreviation like "Mr." / "Dr.": use the full word pair if that is identical (mister = містер), otherwise reject.
   Promote a borderline "similar"/"partial" line to identical only if it truly meets the rubric.
3. For final identical pairs also set:
   - ce (American/international spelling; British only if the word is British-only), cu (Ukrainian headword), pos, br (true only if British-only), lab (usage labels + 1–2 topic labels from the rubric), note (≤ 120 chars, English; ONLY about how the English word is used in English — never about the Ukrainian word's meanings; empty if not needed).
   - lvl = CEFR level (A0, A1, A2, B1, B2, C1, C2) of THIS shared meaning for a learner of English:
     • A0 only if "list level" is A0 and the shared meaning is that basic meaning.
     • If the shared meaning is the word's main meaning, use the list level.
     • If the shared meaning is a narrower or less common sense (flag = флаг only on ships/computing, front = military front, like = a social-media like), choose a higher level that fits that sense.
     • If there is no list level: common everyday words B1–B2, specialised C1, technical/rare/archaic C2.
4. Write a JSON array to ${ROOT}/data/checked/${b}.json — one object per line, in order:
   {"en": "<english exactly as on the line>", "uk": "<ukrainian exactly as on the line>", "v": "<final verdict>", "ce": "...", "cu": "...", "pos": "...", "br": false, "lab": [...], "lvl": "B1", "note": "", "why": "<only if you changed the first verdict: short reason>"}
   For non-identical verdicts fill only en, uk, v, ce, cu, why.
5. Validate: python3 -c "import json;d=json.load(open('${ROOT}/data/checked/${b}.json'));print(len(d))" and fix if it fails. Do not modify other files. Do not run git. Do not use web search.
Return: file path, total objects, number of final identical, up to 10 overturned pairs.`
}

phase('Cross-check')
const results = await parallel(args.batches.map(b => () =>
  agent(prompt(b), { label: b, phase: 'Cross-check', schema: RESULT }).then(r => r ? { batch: b, ...r } : { batch: b, failed: true })))
const ok = results.filter(r => r && !r.failed)
return { done: ok.length, failed: results.filter(r => !r || r.failed).map(r => r && r.batch), identical: ok.reduce((s, r) => s + (r.identical || 0), 0), overturned: ok.flatMap(r => r.overturned || []).slice(0, 40) }
