#!/usr/bin/env python3
"""Record every English word with a neural voice and pack the clips into audio bundles.

Voice: Kokoro-82M (hexgrad/Kokoro-82M, Apache-2.0), voice "af_heart" (American English);
British-only words use "bf_emma" (British English). Run with the Python 3.12 venv that has `kokoro`:
    /home/user/tts-venv/bin/python tools/make_audio.py [--workers 2]
Output (in the repo):
    audio/chunk-NNN.mp3   250 words each, most used words first, 0.3 s of silence between words
    audio/manifest.json   {"voice": ..., "chunks": [...], "words": {"computer": [chunk, start_s, dur_s], ...}}
Resumable: words already in the manifest are kept; new words are appended in new bundles.
"""
import hashlib, json, os, re, subprocess, sys, unicodedata
from multiprocessing import Pool

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO = os.path.join(REPO, 'audio')
CACHE = os.environ.get('AUDIO_CACHE', '/home/user/audio-cache')
SR = 24000
CHUNK = 250
GAP = 0.3
SPEED = 0.9
VOICE_US, VOICE_GB = 'af_heart', 'bf_emma'

# respellings for words the pronunciation dictionary gets wrong
OVERRIDES = {'déjà vu': 'deja vu', 'château': 'chateau', 'jalapeño': 'jalapeno', 'tête-à-tête': 'tet a tet',
             'prêt-à-porter': 'pret a porter', 'IT': 'I.T.', 'ID': 'I.D.'}
# all-caps words that are said as words, not letter by letter
WORDLIKE = {'COVID', 'BIOS', 'LAN', 'MILF', 'OLED', 'NATO', 'PIN', 'LOL', 'FAQ', 'OK', 'SaaS', 'DevOps', 'IMHO', 'WTF', 'OMG'}
COMMON = set()


def tts_text(en):
    if en in OVERRIDES:
        return OVERRIDES[en]
    out = []
    for tok in en.split(' '):
        bare = re.sub(r'[^A-Za-z]', '', tok)
        if len(bare) >= 2 and bare.isupper() and tok not in WORDLIKE and bare.lower() in COMMON:
            tok = '.'.join(bare) + '.'          # IT -> I.T. so it is not read as the word "it"
        out.append(tok)
    return ' '.join(out)


def cache_path(en, voice):
    return os.path.join(CACHE, hashlib.sha1(f'{voice}|{en}'.encode()).hexdigest()[:20] + '.npy')


_pipes = {}


def _init():
    import torch
    torch.set_num_threads(int(os.environ.get('TTS_THREADS', '2')))
    from kokoro import KPipeline
    _pipes['a'] = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M')
    _pipes['b'] = KPipeline(lang_code='b', repo_id='hexgrad/Kokoro-82M')


def trim_and_level(x):
    x = np.asarray(x, dtype=np.float32)
    if not len(x):
        return x
    peak = float(np.max(np.abs(x))) or 1.0
    idx = np.where(np.abs(x) > 0.03 * peak)[0]
    if len(idx):
        a = max(0, idx[0] - int(0.04 * SR))
        b = min(len(x), idx[-1] + int(0.08 * SR))
        x = x[a:b]
    rms = float(np.sqrt(np.mean(x ** 2))) or 1e-6
    x = x * min(0.1 / rms, 0.95 / peak)       # even loudness, never clipping
    fade = min(len(x) // 4, int(0.01 * SR))
    if fade:
        ramp = np.linspace(0, 1, fade, dtype=np.float32)
        x[:fade] *= ramp
        x[-fade:] *= ramp[::-1]
    return x


def render(item):
    en, british = item
    voice = VOICE_GB if british else VOICE_US
    p = cache_path(en, voice)
    if os.path.exists(p):
        return en, p
    pipe = _pipes['b' if british else 'a']
    parts = [a.numpy() if hasattr(a, 'numpy') else np.asarray(a) for _, _, a in pipe(tts_text(en), voice=voice, speed=SPEED)]
    audio = trim_and_level(np.concatenate(parts) if parts else np.zeros(1, np.float32))
    np.save(p, audio)
    return en, p


def encode(pcm, path):
    proc = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', 'pipe:0',
                           '-c:a', 'libmp3lame', '-b:a', '48k', path], input=pcm.astype(np.float32).tobytes())
    if proc.returncode:
        raise RuntimeError('ffmpeg failed for ' + path)


def main():
    workers = int(sys.argv[sys.argv.index('--workers') + 1]) if '--workers' in sys.argv else 2
    os.makedirs(AUDIO, exist_ok=True)
    os.makedirs(CACHE, exist_ok=True)
    for line in open(os.path.join(REPO, 'data', 'levels', 'en-rank.tsv'), encoding='utf-8'):
        if not line.startswith('#'):
            COMMON.add(line.split('\t')[0])
            if len(COMMON) >= 30000:
                break
    words = json.load(open(os.path.join(REPO, 'data', 'words.json'), encoding='utf-8'))
    mpath = os.path.join(AUDIO, 'manifest.json')
    man = json.load(open(mpath, encoding='utf-8')) if os.path.exists(mpath) else \
        {'voice': f'Kokoro-82M {VOICE_US} (US), {VOICE_GB} for British-only words', 'chunks': [], 'words': {}}
    todo = [w for w in words if w['en'] not in man['words']]   # words.json is already in frequency order
    print(len(words), 'words,', len(todo), 'to record', flush=True)
    with Pool(workers, initializer=_init) as pool:
        for i in range(0, len(todo), CHUNK):
            group = todo[i:i + CHUNK]
            done = dict(pool.map(render, [(w['en'], bool(w.get('british'))) for w in group], chunksize=4))
            n = len(man['chunks'])
            name = f'chunk-{n:03d}.mp3'
            gap = np.zeros(int(GAP * SR), np.float32)
            pcm, t = [gap], GAP
            entries = {}
            for w in group:
                clip = np.load(done[w['en']])
                entries[w['en']] = [n, round(t, 3), round(len(clip) / SR, 3)]
                pcm += [clip, gap]
                t += len(clip) / SR + GAP
            encode(np.concatenate(pcm), os.path.join(AUDIO, name))
            man['chunks'].append(name)
            man['words'].update(entries)
            json.dump(man, open(mpath, 'w', encoding='utf-8'), ensure_ascii=False)
            print(f'{name}: {len(group)} words, {t:.0f} s, total {len(man["words"])}', flush=True)


if __name__ == '__main__':
    main()
