#!/usr/bin/env python3
"""Record the clouds: every word, ready phrase and dialogue line of each cloud.

Same voice as the word cards (Kokoro-82M, af_heart, American English). One file per cloud, so opening a cloud loads
one small file: audio/cloud-<id>.mp3, positions in data/clouds/audio.json ({cloud id: {text: [start_s, duration_s]}}).
Run after tools/build_clouds.py, then run build_clouds.py again to put the positions into clouds.js:
    /home/user/tts-venv/bin/python tools/make_cloud_audio.py [cloud ids…]
Clips are cached in AUDIO_CACHE, so a second run only records what changed.
"""
import json, os, re, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_audio as M   # noqa: E402

REPO, D = M.REPO, os.path.join(M.REPO, 'data')
GAP = 0.35


def say(text, kind):
    """the raw clip of one text (cached)"""
    p = M.cache_path(('S|' if kind == 's' else '') + text, M.VOICE_US)
    if os.path.exists(p):
        return np.load(p).astype(np.float32)
    t = text if kind == 's' else M.tts_text(text)
    parts = [a.numpy() if hasattr(a, 'numpy') else np.asarray(a) for _, _, a in M._pipes['a'](t, voice=M.VOICE_US, speed=1.0)]
    raw = np.concatenate(parts) if parts else np.zeros(1, np.float32)
    np.save(p, raw.astype(np.float16))
    return raw.astype(np.float32)


def main():
    only = set(a for a in sys.argv[1:] if not a.startswith('-'))
    data = json.load(open(f'{D}/clouds/clouds.json', encoding='utf-8'))
    ap = f'{D}/clouds/audio.json'
    man = json.load(open(ap, encoding='utf-8')) if os.path.exists(ap) else {}
    os.makedirs(M.CACHE, exist_ok=True)
    M._init()
    for ci in data['circles']:
        for c in ci['clouds']:
            if only and c['id'] not in only:
                continue
            items = []
            for w in c['w'] + c['m']:          # every word of the cloud, so the cloud needs only its own file
                items.append((w['en'], 'w'))
            for en, _ in c['s'] + c['d'] + [x[:2] for x in c.get('f', [])]:
                t = re.sub(r'^[AB]:\s*', '', en)
                if re.search(r'[A-Za-z]{2}', t) and not t.startswith('-'):
                    items.append((t, 's'))
            seen, pcm, t0, pos = set(), [np.zeros(int(GAP * M.SR), np.float32)], GAP, {}
            for text, kind in items:
                if text in seen:
                    continue
                seen.add(text)
                clip = M.trim_and_level(say(text, kind))
                pos[text] = [round(t0, 3), round(len(clip) / M.SR, 3)]
                pcm += [clip, np.zeros(int(GAP * M.SR), np.float32)]
                t0 += len(clip) / M.SR + GAP
            M.encode(np.concatenate(pcm), os.path.join(M.AUDIO, f"cloud-{c['id']}.mp3"))
            man[c['id']] = pos
            json.dump(man, open(ap, 'w', encoding='utf-8'), ensure_ascii=False)
            print(c['id'], len(pos), 'clips', round(t0), 's', flush=True)


if __name__ == '__main__':
    main()
