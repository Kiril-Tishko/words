#!/usr/bin/env python3
"""Make sure the recorded words are understandable.

1. A speech recognizer (faster-whisper small.en) listens to every recorded word with rank <= LIMIT.
2. Words it does not recognize are re-recorded with other voices (af_bella, then af_nicole); the first
   voice whose clip is recognized wins and is saved in data/audio-voices.json.
   (Homophones like role/roll or site/sight are accepted via a small list.)
3. Bundles that contain changed words are rebuilt (audio/chunk-NNN.mp3 + audio/manifest.json).
Remaining unclear words are listed in data/audio-check.json.
Run: /home/user/tts-venv/bin/python tools/fix_audio.py [limit]
"""
import json, os, re, sys

import numpy as np
from rapidfuzz import fuzz
from scipy.signal import resample_poly

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_audio as M  # noqa: E402

REPO = M.REPO
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
ALTERNATES = ['af_bella', 'af_nicole']
HOMOPHONES = {'role': ['roll'], 'site': ['sight', 'cite'], 'cent': ['sent', 'scent'], 'sense': ['cents', 'scents'],
              'sex': ['sax'], 'post': ['posed'], 'flu': ['flew'], 'pi': ['pie'], 'karat': ['carrot', 'carat'],
              'chili': ['chilly'], 'mustard': ['mustered'], 'ion': ['iron'], 'bass': ['base'], 'medal': ['meddle']}


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


class Ear:
    def __init__(self):
        from faster_whisper import WhisperModel
        self.m = WhisperModel('small.en', device='cpu', compute_type='int8')

    def hear(self, clip):
        a16 = resample_poly(clip, 2, 3).astype(np.float32)
        pad = np.zeros(8000, np.float32)
        segs, _ = self.m.transcribe(np.concatenate([pad, a16, pad]), language='en', beam_size=5)
        return ' '.join(s.text for s in segs).strip()

    def ok(self, en, heard):
        a, b = norm(heard), norm(en)
        if not b:
            return True
        if fuzz.ratio(a, b) >= 80 or (len(b) >= 3 and b in a) or (b == 'ok' and a == 'okay'):
            return True
        if en.isupper() and a.replace('.', '') == b:
            return True
        return any(norm(h) == a or (len(norm(h)) >= 3 and norm(h) in a) for h in HOMOPHONES.get(en.lower(), []))


def rebuild_chunks(man, chunk_ids):
    """Re-encode the given bundles from the clip cache (re-recording clips that are missing)."""
    import subprocess  # noqa: F401
    by_chunk = {}
    for en, (c, start, _d) in man['words'].items():
        if c in chunk_ids:
            by_chunk.setdefault(c, []).append((start, en))
    words = {w['en']: w for w in json.load(open(os.path.join(REPO, 'data', 'words.json'), encoding='utf-8'))}
    for c in sorted(by_chunk):
        gap = np.zeros(int(M.GAP * M.SR), np.float32)
        pcm, t = [gap], M.GAP
        for _, en in sorted(by_chunk[c]):
            br = bool(words.get(en, {}).get('british'))
            voice = M.voice_for(en, br)
            p = M.cache_path(en, voice)
            if not os.path.exists(p):
                M.render((en, br, voice))
            clip = M.trim_and_level(np.load(p).astype(np.float32))
            man['words'][en] = [c, round(t, 3), round(len(clip) / M.SR, 3)]
            pcm += [clip, gap]
            t += len(clip) / M.SR + M.GAP
        M.encode(np.concatenate(pcm), os.path.join(M.AUDIO, man['chunks'][c]))
        print('rebuilt', man['chunks'][c], flush=True)


def main():
    for line in open(os.path.join(REPO, 'data', 'levels', 'en-rank.tsv'), encoding='utf-8'):
        if not line.startswith('#'):
            M.COMMON.add(line.split('\t')[0])
            if len(M.COMMON) >= 30000:
                break
    vf = os.path.join(REPO, 'data', 'audio-voices.json')
    if os.path.exists(vf):
        M.VOICE_FIX.update(json.load(open(vf, encoding='utf-8')))
    M._init()
    ear = Ear()
    man = json.load(open(os.path.join(M.AUDIO, 'manifest.json'), encoding='utf-8'))
    words = json.load(open(os.path.join(REPO, 'data', 'words.json'), encoding='utf-8'))
    changed, unclear, n = set(), [], 0
    for w in words:
        en = w['en']
        if not w.get('rank') or w['rank'] > LIMIT or en not in man['words']:
            continue
        br = bool(w.get('british'))
        voice = M.voice_for(en, br)
        p = M.cache_path(en, voice)
        if not os.path.exists(p):
            M.render((en, br, voice))
        heard = ear.hear(M.trim_and_level(np.load(p).astype(np.float32)))
        n += 1
        if ear.ok(en, heard):
            continue
        fixed = None
        for alt in ([] if br else ALTERNATES):
            if alt == voice:
                continue
            _, pa = M.render((en, br, alt))
            h2 = ear.hear(M.trim_and_level(np.load(pa).astype(np.float32)))
            if ear.ok(en, h2):
                fixed = alt
                break
        if fixed:
            M.VOICE_FIX[en] = fixed
            changed.add(man['words'][en][0])
            print(f'{en!r}: heard {heard!r} -> using {fixed}', flush=True)
        else:
            unclear.append({'en': en, 'heard': heard})
    json.dump(M.VOICE_FIX, open(vf, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump(unclear, open(os.path.join(REPO, 'data', 'audio-check.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(n, 'checked;', len(M.VOICE_FIX), 'words use another voice;', len(unclear), 'still unclear', flush=True)
    if changed:
        rebuild_chunks(man, changed)
        json.dump(man, open(os.path.join(M.AUDIO, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False)


if __name__ == '__main__':
    main()
