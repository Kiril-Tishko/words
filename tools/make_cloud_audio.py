#!/usr/bin/env python3
"""Record the clouds: every word, little word, ready phrase and dialogue line of each cloud, and the page of little words.

Same voice as the word cards (Kokoro-82M, af_heart, American English). One file per cloud, so opening a cloud loads
one small file: audio/cloud-<id>.mp3, positions in data/clouds/audio.json ({cloud id: {text: [start_s, duration_s]}}).
The little words of data/clouds/kit.txt go to audio/kit.mp3 (positions under "_kit").
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
# names the voice reads wrongly, and words that are verbs in the "Actions" clouds (the voice would say the noun)
PLACES = {'Kyiv': 'kˈiɪv', 'Lviv': 'ləvˈiv'}
VERBS = {'export': 'ɛkspˈɔɹt', 'import': 'ɪmpˈɔɹt', 'present': 'pɹizˈɛnt', 'protest': 'pɹətˈɛst', 'transport': 'tɹænspˈɔɹt',
         'combine': 'kəmbˈIn', 'delegate': 'dˈɛləɡˌAt', 'initiate': 'ɪnˈɪʃiˌAt', 'isolate': 'ˈIsəlˌAt'}
VERB_IN_SENTENCE = re.compile(r'\b(We|I|You|They) (' + '|'.join(VERBS) + r')\b')


def say(text, kind, verbs=False):
    """the raw clip of one text (cached). kind: 'w' a word, 's' a sentence, 'k' a little word"""
    if kind == 'w' and (text in PLACES or (verbs and text.lower() in VERBS)):
        key = 'V|' + text
        t = '[' + text[0].upper() + text[1:] + '](/' + (PLACES.get(text) or VERBS[text.lower()]) + '/).'
    elif kind == 'w':
        key, t = text, M.tts_text(text)
    elif kind == 'k':
        key, t = 'K|' + text, text[0].upper() + text[1:] + '.'
    else:
        key, t = 'S|' + text, text
        for name, ph in PLACES.items():
            t = re.sub(r'\b' + name + r'\b', '[' + name + '](/' + ph + '/)', t)
        t = VERB_IN_SENTENCE.sub(lambda m: m.group(1) + ' [' + m.group(2) + '](/' + VERBS[m.group(2)] + '/)', t)
    p = M.cache_path(key, M.VOICE_US)
    if os.path.exists(p):
        return np.load(p).astype(np.float32)
    parts = [a.numpy() if hasattr(a, 'numpy') else np.asarray(a) for _, _, a in M._pipes['a'](t, voice=M.VOICE_US, speed=1.0)]
    raw = np.concatenate(parts) if parts else np.zeros(1, np.float32)
    np.save(p, raw.astype(np.float16))
    return raw.astype(np.float32)


def pack(items, path, verbs=False):
    """one file with all the clips; returns {text: [start, duration]}"""
    seen, pcm, t0, pos = set(), [np.zeros(int(GAP * M.SR), np.float32)], GAP, {}
    for text, kind in items:
        if text in seen:
            continue
        seen.add(text)
        clip = M.trim_and_level(say(text, kind, verbs))
        pos[text] = [round(t0, 3), round(len(clip) / M.SR, 3)]
        pcm += [clip, np.zeros(int(GAP * M.SR), np.float32)]
        t0 += len(clip) / M.SR + GAP
    M.encode(np.concatenate(pcm), path)
    return pos, t0


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
            for en, _ in c.get('k', []):       # the little words of a start cloud
                items.append((en, 'k'))
            for en, _ in c['s'] + c['d'] + [x[:2] for x in c.get('f', [])]:
                t = re.sub(r'^[AB]:\s*', '', en)
                if re.search(r'[A-Za-z]{2}', t) and not t.startswith('-'):
                    items.append((t, 's'))
            pos, t0 = pack(items, os.path.join(M.AUDIO, f"cloud-{c['id']}.mp3"), verbs=c['id'].startswith('do-'))
            man[c['id']] = pos
            json.dump(man, open(ap, 'w', encoding='utf-8'), ensure_ascii=False)
            print(c['id'], len(pos), 'clips', round(t0), 's', flush=True)
    if not only or '_kit' in only:
        items = [(en, 'k') for g in data.get('kit', []) for en, _ in g['items']]
        man['_kit'], t0 = pack(items, os.path.join(M.AUDIO, 'kit.mp3'))
        json.dump(man, open(ap, 'w', encoding='utf-8'), ensure_ascii=False)
        print('kit', len(man['_kit']), 'clips', round(t0), 's', flush=True)
    ids = {c['id'] for ci in data['circles'] for c in ci['clouds']} | {'_kit'}
    for old in [k for k in man if k not in ids]:          # clouds that no longer exist
        del man[old]
        json.dump(man, open(ap, 'w', encoding='utf-8'), ensure_ascii=False)


if __name__ == '__main__':
    main()
