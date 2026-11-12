#!/usr/bin/env python3
"""Picture sheets for the clouds: one image per cloud with the pictures of its words.

Pictures: Fluent Emoji 3D (Microsoft, MIT license), from the npm package @lobehub/fluent-emoji-3d:
    mkdir -p /home/user/sources/emoji/f3d && cd /home/user/sources/emoji/f3d
    npm pack @lobehub/fluent-emoji-3d && tar xzf lobehub-fluent-emoji-3d-*.tgz
Which picture a word has is decided by hand in data/clouds/words/*.txt; tools/build_clouds.py turns that into
data/clouds/pictures.json ({cloud id: [emoji, ...]}, the order of the sheet; index 0 is the cloud's own picture).
Run after tools/build_clouds.py:
    python3 tools/make_cloud_pictures.py [cloud ids…]
Output: pictures/cloud-<id>.webp (tiles of 128 px, 8 in a row) and pictures/clouds.webp (the picture of every cloud,
tiles of 96 px, 8 in a row, in the order of the site).
"""
import json, os, sys

from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get('FLUENT_3D', '/home/user/sources/emoji/f3d/package/assets')
OUT = os.path.join(REPO, 'pictures')
TILE, COLS, ICON = 128, 8, 96
_have = None


def source(emoji):
    """the file of an emoji in the package: code points joined by '-', with or without the variation selector"""
    global _have
    if _have is None:
        _have = set(f[:-5] for f in os.listdir(SRC) if f.endswith('.webp'))
    cps = [f'{ord(ch):04x}' for ch in emoji]
    for name in ('-'.join(cps), '-'.join(c for c in cps if c != 'fe0f'), '-'.join(cps) + '-fe0f'):
        if name in _have:
            return os.path.join(SRC, name + '.webp')
    return None


def sheet(emojis, tile, path):
    rows = (len(emojis) + COLS - 1) // COLS
    im = Image.new('RGBA', (COLS * tile, rows * tile), (0, 0, 0, 0))
    missing = []
    for i, e in enumerate(emojis):
        src = source(e)
        if not src:
            missing.append(e)
            continue
        pic = Image.open(src).convert('RGBA').resize((tile, tile), Image.LANCZOS)
        im.paste(pic, ((i % COLS) * tile, (i // COLS) * tile))
    im.save(path, 'WEBP', quality=80, method=6)
    return missing


def main():
    only = set(a for a in sys.argv[1:] if not a.startswith('-'))
    pics = json.load(open(os.path.join(REPO, 'data', 'clouds', 'pictures.json'), encoding='utf-8'))
    os.makedirs(OUT, exist_ok=True)
    total, missing = 0, []
    for cid, emojis in pics.items():
        if only and cid not in only:
            continue
        p = os.path.join(OUT, f'cloud-{cid}.webp')
        missing += [(cid, e) for e in sheet(emojis, TILE, p)]
        total += os.path.getsize(p)
    if not only:
        p = os.path.join(OUT, 'clouds.webp')
        missing += [('clouds', e) for e in sheet([v[0] for v in pics.values()], ICON, p)]
        total += os.path.getsize(p)
        for f in os.listdir(OUT):           # sheets of clouds that no longer exist
            if f.startswith('cloud-') and f[6:-5] not in pics:
                os.remove(os.path.join(OUT, f))
    print(len(pics) if not only else len(only), 'sheets,', round(total / 1e6, 2), 'MB;', len(missing), 'pictures missing', missing[:20])
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
