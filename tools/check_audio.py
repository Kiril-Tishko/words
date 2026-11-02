#!/usr/bin/env python3
"""Listen to the recorded words with a speech recognizer and flag clips that do not sound like the word.

Uses faster-whisper (base.en) on the cached clips (made by tools/make_audio.py). Checks the most used
words (rank <= LIMIT), where a recognizer is reliable; rare technical words are skipped.
Output: data/audio-check.json  [{"en": ..., "heard": ..., "score": ...}, ...] for clips that look wrong.
Run: /home/user/tts-venv/bin/python tools/check_audio.py [limit]
"""
import json, os, re, sys

import numpy as np
from rapidfuzz import fuzz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_audio  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 20000


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def main():
    from faster_whisper import WhisperModel
    model = WhisperModel('base.en', device='cpu', compute_type='int8')
    words = json.load(open(os.path.join(REPO, 'data', 'words.json'), encoding='utf-8'))
    flagged, n = [], 0
    for w in words:
        if not w.get('rank') or w['rank'] > LIMIT:
            continue
        voice = make_audio.VOICE_GB if w.get('british') else make_audio.VOICE_US
        p = make_audio.cache_path(w['en'], voice)
        if not os.path.exists(p):
            continue
        clip = make_audio.trim_and_level(np.load(p).astype(np.float32))
        audio16 = np.interp(np.arange(0, len(clip), 1.5), np.arange(len(clip)), clip).astype(np.float32)  # 24k -> 16k
        pad = np.zeros(8000, np.float32)
        segs, _ = model.transcribe(np.concatenate([pad, audio16, pad]), language='en', beam_size=5,
                                   initial_prompt='A single English word or short phrase.')
        heard = ' '.join(s.text for s in segs).strip()
        target = w['en']
        letters = target.isupper() and len(target) <= 6
        a, b = norm(heard), norm(target)
        score = fuzz.ratio(a, b)
        ok = score >= 80 or (len(b) >= 3 and b in a) or (letters and a.replace('.', '') == b) or (b == 'ok' and a == 'okay')
        n += 1
        if not ok:
            flagged.append({'en': target, 'heard': heard, 'score': round(score)})
    json.dump(flagged, open(os.path.join(REPO, 'data', 'audio-check.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(n, 'checked,', len(flagged), 'flagged')
    for f in flagged[:80]:
        print(f"{f['en']!r:28} heard {f['heard']!r} ({f['score']})")


if __name__ == '__main__':
    main()
