#!/usr/bin/env python3
"""Pictures for the back of the cards from the Noto Emoji set (Google, Apache License 2.0).

Agents chose, per card, an emoji that clearly shows the card's meaning (tools/workflows/emoji-map.js ->
data/images/emoji-*.json, {"taxi": "taxi", "doctor": "health-worker"}). This script takes the SVG of each
chosen emoji from the Iconify copy of Noto Emoji (npm @iconify-json/noto, icons.json) and writes
data/levels/pictures.json {"taxi": "<svg ...>...</svg>"}; tools/build_site.py puts the SVG on the card's back.
A photo saved as images/<word>.* takes priority over the emoji.
Usage: tools/make_pictures.py [path/to/icons.json]   (default /home/user/sources/noto-icons.json)
"""
import glob, json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, 'data')


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else '/home/user/sources/noto-icons.json'
    s = json.load(open(src, encoding='utf-8'))
    icons, aliases = s['icons'], s.get('aliases', {})
    W, H = s.get('width', 128), s.get('height', 128)
    words = {w['en'] for w in json.load(open(f'{D}/words.json', encoding='utf-8'))}
    chosen = {}
    for f in sorted(glob.glob(f'{D}/images/emoji-*.json')):
        chosen.update(json.load(open(f, encoding='utf-8')))
    out, missing = {}, []
    for en, name in chosen.items():
        if en not in words:
            continue
        seen = 0
        while name in aliases and name not in icons and seen < 5:
            name = aliases[name].get('parent', name)
            seen += 1
        ic = icons.get(name)
        if not ic:
            missing.append((en, name))
            continue
        w, h = ic.get('width', W), ic.get('height', H)
        out[en] = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">' + ic['body'] + '</svg>')
    json.dump(out, open(f'{D}/levels/pictures.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    size = sum(len(v) for v in out.values())
    print(len(out), 'pictures,', round(size / 1e6, 2), 'MB of SVG;', len(missing), 'unknown names', missing[:10])


if __name__ == '__main__':
    main()
