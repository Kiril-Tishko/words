# Design and bug review: Same Words

Reviewer: product design / front-end. Scope: `site/app.html` (built into `index.html`), `words.js`, the screenshots in `docs/review/*.png`.
How it was checked: I read the code and the 7 screenshots. I loaded the built page in headless Chrome at 1280 px and about 500 px wide, scripted it over the DevTools protocol, and ran the highlight function over all 11,024 example sentences. Numbers marked **measured** come from those runs. Other claims come from reading the code.

## Summary

The look is already close to what the owner wants: quiet chips, white cards, a serif word. The problems are mostly underneath:

1. **The words are small for the card.** The English word is 34 px on a 270 px desktop card and 24 px on phones. Long words wrap in the middle (432 Rare cards).
2. **The image slot does not fit yet.** The back already has an empty picture box, but with it, examples overflow and need scrolling inside the card. That happens on 160 of 1,122 Top 20K cards on desktop and on 97% of them in the 2-column phone/tablet layout (**measured**).
3. **Audio fails in common cases.**
   - Opening `index.html` from disk falls back to the robotic browser voice, because `fetch()` is blocked on `file://` (**measured**).
   - Each decoded bundle takes about 71 MB of memory, which can crash iPhones.
   - Quick taps can play the wrong word.
   - The iPhone silent switch mutes everything.
4. **Real state bugs:**
   - Training scores are wrong after "Train again" (**measured**: 2/3 instead of 3/3).
   - The "My words" count does not match the list (**measured**: chip 2, list 1).
   - "Hide slang" makes My words say "No words yet".
   - The Back button leaves the site.
   - Space does not flip the card in One by one view.
   - "About Rare in English" appears on 1,489 cards.
5. **Accessibility:** the card is `role="button"` with buttons inside it and an `aria-label`. A screen reader can never reach the examples. The face you cannot see stays in the tab order.
6. **Mobile:** the level chips take 5 rows (about 230 px) before the first card. In One by one view the ← → buttons are below the fold, and there is no swipe.
7. **Scale:** scrolling through Rare builds 4,176 cards and **105,000 DOM nodes** (**measured**, 5.4 s of total build time). `words.js` is 2.1 MB (907 KB gzipped) and blocks the first paint.

All the fixes below are small CSS/JS changes in `site/app.html`, except where I say "build". None of them change the minimal style.

---

## Problems, most important first

### 1. The word is too small, and long words break in the middle (owner request)
- Grid: `.en` is `clamp(24px, 2.9vw, 34px)`, so it is 34 px on a 270 px card (**measured**). The card is mostly empty space (see `desktop-top1000-front.png`).
- Phone: the size depends on the *viewport*, so it drops to 24 px on a 358 px wide card (`phone-top400.png`: "people" looks tiny).
- `overflow-wrap: anywhere` breaks long words in the middle. 432 of 4,176 Rare cards wrap, for example "ferromagnetic", "neo-Darwinist", "phenolphthalein", "холекальциферол". 25 Top 20K cards wrap too, for example "memorandum" and "project manager" (**measured**).

**Fix.** Size the word from the *card* width and the length of its longest token:
```js
// in cardHTML()
const longest = s => Math.max(4, ...s.split(/[\s-]+/).map(p => p.length));
'<div class="en" style="--n:' + longest(w.en) + '">' + esc(w.en) + '</div><div class="eq">=</div>' +
'<div class="uk" lang="uk" style="--n:' + longest(w.uk) + '">' + esc(w.uk) + '</div>'
```
```css
.card { container-type: inline-size; }
.en { font-size: clamp(22px, min(16cqi, 150cqi / var(--n)), var(--max-en, 64px)); overflow-wrap: break-word; hyphens: manual; }
.uk { font-size: clamp(19px, min(13.5cqi, 135cqi / var(--n)), var(--max-uk, 54px)); overflow-wrap: break-word; hyphens: manual; }
.eq { font-size: clamp(16px, 6cqi, 26px); }
.single { --max-en: 84px; --max-uk: 70px; }   /* replaces the .single .en / .single .uk rules */
```
Expected results: short words go to about 43 px on a desktop grid card (from 34) and about 57 px on a phone (from 24). "acetazolamide" goes to about 31 px and fits on one line. Phrases wrap only at spaces. Keep the old `clamp(...)` line above each rule as a fallback for browsers without `cqi` (Safari before 16).

### 2. Image on the back: the slot exists, but it pushes the examples out of the card (owner request)
- The back already renders `.pic`, a dashed box with an icon, on **every** card. No word has an `img` yet (0 of 10,812).
- At 32% of the card height it leaves too little room. Examples overflow and scroll inside the card on 160/1,122 Top 20K cards on desktop. At 481–640 px (2 columns, 214 px cards) they overflow on 1,088/1,122 (**measured**). The only cue is a thin scrollbar, so learners will not see examples 3–4.
- The back repeats the word on its own line, puts the rank on a second line, and sets the pos tag ("noun") in the serif font. That wastes about 20 px and looks inconsistent (see `desktop-top1000-back.png`).

**Fix.**
- **Build:** add `img` (path, for example `img/<id>.webp`, 480×270, about 20 KB) and `img_credit` to the data. Images from Wikimedia/Openverse need the credit.
- Render the image with fixed proportions, lazy loading, and a fallback when it fails to load:
  ```js
  '<div class="pic has"><img src="' + esc(w.img) + '" alt="" loading="lazy" decoding="async" width="480" height="270" title="' + esc(w.img_credit || '') + '" onerror="this.parentNode.classList.remove(\'has\');this.remove()"></div>'
  ```
- Merge the head and rank lines into one line, and give the back a speaker button (see #13):
  ```js
  '<div class="head">' + esc(w.en) + ' <span class="meta">' + (w.pos ? esc(w.pos) + ' · ' : '') + rankText(w) + '</span></div>'
  ```
  ```css
  .back .head .meta { font: 400 12px var(--ui); color: var(--muted); margin-left: 4px; }
  .back .pic { flex: 0 0 auto; height: 28%; }
  .grid .back ol { font-size: 12.5px; line-height: 1.3; }
  /* show that there is more below instead of a hidden scrollbar */
  .back { mask-image: linear-gradient(#000 calc(100% - 18px), transparent); }
  .back.fits { mask-image: none; }   /* set when scrollHeight <= clientHeight, checked on flip */
  ```
- Phone/tablet: drop the 2-column band. 214 px cards cannot hold a picture and 4 examples.
  ```css
  @media (max-width: 640px) { .grid { grid-template-columns: minmax(0, 440px); justify-content: center; } }
  ```
  Delete the `max-width: 480px` aspect override, so phones keep 4/5 with the bigger word from #1.
- Until images exist, make the empty slot quieter: `.pic:not(.has) { border-style: solid; background: transparent; }`. It still shows where the picture will go.

### 3. Audio: offline fallback, memory, a race, and the iPhone silent switch
- **`file://`:** `fetch('audio/chunk-000.mp3')` fails with "Failed to fetch" when the page is opened from disk (**measured** in Chrome). Every word then falls back to `speechSynthesis`, which is robotic and on some Linux/Android setups silent. The README says the site "works offline".
  **Fix:** use an `<audio>` element when `fetch` fails or `location.protocol === 'file:'`. Media elements can load `file://` and seek with range reads.
  ```js
  const els = {};
  function playViaElement(w) {
    const a = els[w.au[0]] || (els[w.au[0]] = new Audio('audio/' + AUDIO.chunks[w.au[0]]));
    a.pause(); a.currentTime = Math.max(0, w.au[1] - 0.03);
    a.play().catch(() => speak(w.en));
    clearTimeout(a._t); a._t = setTimeout(() => a.pause(), (w.au[2] + 0.1) * 1000);
  }
  // in playWord: if (location.protocol === 'file:') return playViaElement(w);  and .catch(() => { done(); playViaElement(w); })
  ```
- **Memory:** each bundle is 370 s of 24 kHz mono. `decodeAudioData` turns it into float PCM at the context's sample rate (48 kHz on most phones), which is about **71 MB per bundle**, and the decoded bundles are never released. Browsing Rare touches many bundles, which can push iOS Safari past its memory limit.
  **Fix:**
  - Create the context at the source rate, which halves the memory:
    ```js
    try { actx = new C({ sampleRate: 24000 }); } catch (e) { actx = new C(); }
    ```
  - Keep at most 3 decoded bundles (LRU): keep `const lru = []`, and in `loadBundle(i)` do `lru.splice(lru.indexOf(i) >>> 0, 1); lru.push(i); while (lru.length > 3) delete bundles[lru.shift()];`.
  - **Build:** pack 50 words per bundle instead of 250. The first tap then downloads about 380 KB instead of 1.9 MB.
- **Race:** if you tap word A, whose bundle is still loading, and then word B, whose bundle is cached, B plays and then A *interrupts* it when A's bundle arrives.
  **Fix:**
  ```js
  let seq = 0;
  // in playWord():
  const my = ++seq;
  // then in .then(buf => ...):
  if (my !== seq) return;
  ```
- **iPhone silent switch:** Web Audio is muted when the ring/silent switch is on. Most learners will hear nothing and think the button is broken.
  **Fix:** in `audioCtx()`, add `try { if (navigator.audioSession) navigator.audioSession.type = 'playback'; } catch (e) {}` (Safari 16.4+).
- The padding is `-0.02 / +0.06` s while the gaps between words are 0.30 s (**measured**, minimum 0.30). Safari does not trim the MP3 encoder delay, so use `-0.05 / +0.12` for a safer margin.

### 4. Training mode bugs and gaps
- **Wrong score after "Train again" (measured).**
  - Steps: 3 words; miss all three; in round 2 know one and miss two; in round 3 know both; press "Train again" and know all three. The result shows **2 / 3**.
  - Cause: `_missed` is written onto the shared `WORDS` objects, and `t-restart` only clears the last round's queue. Leaving Train in the middle also leaves the flags set.
  - **Fix:** keep the state inside `tr`:
    ```js
    tr = { ..., missed: new Set() };
    // know:  if (!tr.missed.has(w.id)) tr.known++;
    // again: tr.missed.add(w.id); tr.again.push(w);
    ```
    Then delete `_missed` everywhere.
- **Ignores "Hide slang", and the sample shows slang.** `startTrain()` uses all of My words, and the sample is `WORDS.slice(0, 8)`. The first sample card is "френд = friend" (`phone-train.png`), a slang word, shown on the Ukrainian side.
  **Fix:** use `baseList('mine')`, and for the sample `baseList('top-400').concat(baseList('top-1000')).slice(0, 10)`. Both respect `hideNs`.
- **The progress counter restarts each round** ("1 / 8", then "1 / 3"), which looks like a reset.
  **Fix:** show `'Round ' + round + ' · ' + (tr.i + 1) + ' / ' + tr.queue.length`, or a single line such as "5 of 8 learned".
- **No keyboard.**
  **Fix:** in `keydown`, replace `if (state.level === 'train') return;` with a train branch: Space/Enter clicks `#t-show`; `1` or ← clicks `#t-again`; `2` or → clicks `#t-know`.
- **Unbiased shuffle.** `sort(() => Math.random() - .5)` is biased. Use Fisher–Yates here and in Shuffle (#9).

### 5. Accessibility: the back of the card cannot be reached
- The card is `<div role="button" aria-label="show equals шоу. Flip card">`. A button's children are presentational, and the label replaces them. A screen reader never reads the examples, notes or labels, and the `+` and 🔊 buttons are invalid nested interactive elements.
- The face you cannot see stays in the tab order. When a card is flipped, Tab still lands on the hidden `+` and 🔊.
- The page is `lang="en"`, so Ukrainian words are read with English rules. `hyphens: auto` also applies English hyphenation to Cyrillic.

**Fix.**
- Card: `<div class="card" role="group" aria-roledescription="flip card" tabindex="0" data-id=…>` with no `aria-label`. Enter/Space already flip it.
- Add `inert` to `.face.back` in the HTML, and flip through a single function:
  ```js
  function flip(card) {
    const f = card.classList.toggle('flipped');
    card.querySelector('.front').inert = f;
    card.querySelector('.back').inert = !f;
  }
  ```
  Use it in the click handler and the keydown handler. `inert` also stops clicks reaching the hidden face in browsers where `backface-visibility` does not block hit-testing (older Safari). Chrome was fine in my test.
- Add `lang="uk"` to `.uk`, to the training card's `.uk`, and to `.brand span`.
- Touch targets: `.icon` is 30 px. Add `@media (pointer: coarse) { .icon { width: 44px; height: 44px; } .say { bottom: 2px; left: 2px; } .add { top: 2px; right: 2px; } }`.

### 6. My words: wrong counts and misleading messages
- **Stale ids (measured).** The chip says "My words 2" while the list shows "1 words". The count is `mine.size`, which includes ids no longer in the data. Ids are `en|uk`, so any data fix to a Ukrainian spelling silently drops a saved word.
  **Fix:**
  - Count `baseList('mine').length` in `renderLevels`.
  - **Build:** give every pair a stable `id` that does not change when a spelling is fixed, plus an alias map for renamed pairs. On load: `mine = new Set([...mine].map(id => (window.ALIAS || {})[id] || id))`.
- **Hide slang + My words (measured).** With the filter on, the chip says 2 but the page says "No words yet. Press + on a card to add it here." The same wrong message ("Words for this level are being checked…") appears when a topic or the filter empties a band.
  **Fix:** choose the message by cause:
  ```js
  const all = state.level === 'mine' ? mine.size : (byLevel[state.level] || []).length;
  msg = !all ? (state.level === 'mine' ? 'No words yet. Press + on a card to add it here.' : 'No words in this group yet.')
             : 'All cards here are hidden by "Hide slang" or the topic filter.';
  ```
- **"1 words".** Use `n + (n === 1 ? ' word' : ' words')`.
- **Removing a word in My words** re-renders the whole page, which resets flips and paging and can make the scroll jump.
  **Fix:** in My words, remove only that card: `t.closest('.card').remove(); state.order = null; renderLevels();` and update `#count`. Use the full render only when the list becomes empty.

### 7. Phone layout: chips push the cards off the first screen
- `phone-top400.png`: the level chips take 5 rows (Top 400 … Train), about 230 px, and then come 2 more rows of tools. The first card starts around y = 380 on an 844 px screen.
- In One by one view on a phone, the header plus a 4/5 card plus the nav is about 860 px. The ← → buttons are below the fold, and there is no swipe.

**Fix.**
- Put the levels in one horizontally scrolling row on phones:
  ```css
  @media (max-width: 640px) {
    #levels { flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; width: calc(100% + 32px); margin-inline: -16px; padding-inline: 16px; scroll-padding-inline: 16px; }
    #levels::-webkit-scrollbar { display: none; }
  }
  ```
  After `renderLevels()`, keep the active chip in view: `const a = $('#levels [aria-pressed="true"]'); if (a) a.scrollIntoView({ inline: 'center', block: 'nearest' });`
- Show the count only once, in `#count`. Drop the `<small>` counts from the level chips. That also fits the desktop chips on **one** row: today "Rare / My words / Train" wrap to a second row at 1280 px (`desktop-top1000-front.png`).
- Add swipe in One by one view:
  ```js
  let sx = null, swiped = false;
  document.addEventListener('pointerdown', e => { sx = e.target.closest('.single .card') ? [e.clientX, e.clientY] : null; });
  document.addEventListener('pointerup', e => {
    if (!sx) return;
    const dx = e.clientX - sx[0], dy = e.clientY - sx[1];
    sx = null;
    if (Math.abs(dx) > 50 && Math.abs(dx) > 1.5 * Math.abs(dy)) { swiped = true; move(dx < 0 ? 1 : -1); }
  });
  // at the top of the click handler: if (swiped) { swiped = false; return; }
  ```
  ```css
  .single .card { touch-action: pan-y; }
  ```
- In `move()`, use `c.focus({ preventScroll: true })` so the page does not jump on phones.

### 8. Performance with about 4,000 cards
- Scrolling through Rare appends 34 pages and ends with **4,176 cards and 104,908 DOM elements**: about 160 ms per page and 5.4 s in total (**measured** on a desktop CPU). Each card builds its whole back, runs the `mark()` regex 4 times, and creates a 3D context. Most backs are never seen.
- `words.js` is 2.1 MB (907 KB gzipped) and loads as a blocking `<script>`. Examples and notes are about 1.6 MB of it. Nothing paints until it has been parsed.

**Fix.**
- **Lazy backs.** Render `<div class="face back" inert></div>` empty. On the first flip, fill it: `if (!back.firstChild) back.innerHTML = backHTML(w);`. This removes about 60% of the DOM and almost all the regex work.
- Optionally add `.grid .card { content-visibility: auto; contain-intrinsic-size: auto 340px; }`. Paint containment clips the `.face` shadow, so move `box-shadow` from `.face` to `.card` if you do this.
- **Build:** move examples and notes into `ex-<band>.js`, loaded when that band is first opened. `words.js` then drops to about 500 KB. Load scripts with `defer` so the header paints first.

### 9. Routing, Shuffle and Space
- **The Back button leaves the site.** `go()` uses `history.replaceState`, so moving between levels never adds a history entry (**measured**: `history.length` stays at 2 after 3 level changes). The position in One by one view is lost on reload.
  **Fix:** in `go()`, do `if (location.hash !== '#' + level) { location.hash = level; return; }` and let the existing `hashchange` handler render. For One by one view, add the index (`#top-1000/37`) and parse it in `fromHash()`.
- **Space does not flip in One by one view (measured).** The README says Space flips, but it only works when the card has focus. After clicking a level or the view chip, Space does nothing.
  **Fix:**
  ```js
  const a = document.activeElement;
  const card = a && a.classList.contains('card') ? a
    : (state.view === 'single' && (!a || a === document.body) ? document.querySelector('.single .card') : null);
  if ((e.key === ' ' || e.key === 'Enter') && card) { e.preventDefault(); flip(card); }
  ```
- **Shuffle has no state and no undo.** It uses a biased sort, and the only way back to frequency order is to change level.
  **Fix:** make Shuffle a toggle with `aria-pressed`. On: `state.order = fisherYates(n)`. Off: `state.order = null`.
  ```js
  function fisherYates(n) {
    const a = Array.from({ length: n }, (_, i) => i);
    for (let i = n - 1; i > 0; i--) { const j = Math.random() * (i + 1) | 0; [a[i], a[j]] = [a[j], a[i]]; }
    return a;
  }
  ```

### 10. "About Rare in English" (1,489 cards)
`rankText()` returns `'About ' + LEVEL_NAMES[w.band]…` for estimated ranks, and for Rare that gives "About Rare in English" (`desktop-rare-dark.png`).
**Fix:** start the function with `if (!w.rank || w.band === 'rare') return 'Rare in English';`.

### 11. "Hide slang" should probably be on by default
Of the 11 Top 400 cards, 4 have a slang Ukrainian side, and the site opens on **friend = френд, people = піпл, party = паті** (`phone-top400.png`). That is the first impression for every new visitor.
**Fix:** `hideNs: store.get('sw.hideNs', true)`. This is the owner's call. The teacher review (#9) also questions what the filter hides.

### 12. Bold word in examples misses 34 sentences on 24 cards (measured)
`mark()` does not handle -y → -ies ("activities", "ladies", "hobbies", "pennies", "huskies"), irregular plurals ("feet", "elves", "cacti", "morae") or prefix entries (`eco-`, `nano-`, `theo-`).
**Fix:**
```js
const stem = /[^aeiou]y$/i.test(last) ? last.slice(0, -1) + '(?:y|ie)'
           : last.length > 3 && /e$/i.test(last) ? last.slice(0, -1) + 'e?' : last;
// prefix entries: if (/-$/.test(word)) use '(' + esc(word.slice(0,-1)) + '\\p{L}*)' as the pattern
```
**Build:** for irregular forms, store the matched span with the example (for example `"He is six [feet] tall."`) so the page does not have to guess.

### 13. Smaller things
- **No 🔊 on the back.** After flipping, you cannot hear the word. Put `.say` inline in `.back .head`, not absolutely positioned.
- **The pos tag is in the serif font** ("noun" in `desktop-top1000-back.png`) while the other tags are sans. Fix: `.head .tag { font-family: var(--ui); font-weight: 400; }`. Not needed if you take the `.meta` line from #2.
- **"Examples coming soon."** appears on the back of 1,858 Rare cards (and about 150 others), which reads as broken. Show only the rank, labels and note. If none of those exist, do not flip: skip `.flipped` when the back would be empty.
- **Sticky hover on touch.** `.icon:hover` stays highlighted after a tap. Wrap it in `@media (hover: hover) { … }`.
- **Selecting text on the back flips the card.** Copying an example is impossible. Add `if (String(getSelection())) return;` before the flip in the click handler.
- **The flag SVG repeats `id="fc"` / `id="ft"`** on each British card (18 cards), so the ids are duplicated. Put the `<clipPath>` defs once in a hidden `<svg>` at the top of `<body>`, and keep only `<g clip-path="url(#fc)">…` in each card.
- **The "Show more" button jumps** when the IntersectionObserver appends the next page under the cursor. That is harmless, but `rootMargin: '1200px 0px'` loads earlier and hides it.
- **Fonts offline:** Literata/Golos come from Google Fonts, so offline the page shows Georgia/system fonts and the word looks different. Ship the two WOFF2 files with the site if offline use matters.
- **Data spotted while testing,** for the linguist: Rare contains name-like entries ("amelia", "spencer", "maxwell") and adjective words tagged `noun` ("acute", "definitive").
