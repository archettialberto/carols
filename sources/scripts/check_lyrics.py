"""Cross-check lyric cues against a vector PDF: each printed syllable is matched to the nearest
notehead column on the upper staff of its system, and that column to (measure, beat) in the song
data. Prints every disagreement. Development only (PyMuPDF).

  python sources/scripts/check_lyrics.py SONG_ID PDF --systems "p:first-last,..." [--font Opus]
         [--rows 3] [--offset 0]

--systems lists each printed system as page:first_measure-last_measure (data measure numbers).
Lyric lines are the text lines between the system's upper staff and the next staff.
"""
import argparse, json, sys
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from music import parse_bar  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument('song'); ap.add_argument('pdf')
ap.add_argument('--systems', required=True); ap.add_argument('--font', default='Opus')
ap.add_argument('--heads', default='153,2d9,77')
args = ap.parse_args()
song = json.loads((ROOT / 'data' / f'{args.song}.json').read_text())
heads_codes = {int(h, 16) for h in args.heads.split(',')}
doc = fitz.open(args.pdf)
lengths = song.get('measure_beats') or [song['meter'][0] * 4 / song['meter'][1]] * len(song['parts']['soprano'])

def onsets(m):
    out = set()
    for v in ('soprano', 'alto'):
        at = 0
        prev_tie = False
        for n in parse_bar(song['parts'][v][m - 1]):
            if n['pitch'] != 'R': out.add(at)
            at += n['duration']
    return sorted(out)

def cues(verse, m):
    lyr = verse['lyrics']['soprano'][m - 1]
    return {float(t.split(':', 1)[0]): t.split(':', 1)[1] for t in lyr.split()} if lyr else {}

problems = 0
compared = 0
systems = []
for spec in args.systems.split(','):
    page, rng = spec.split(':'); a, b = map(int, rng.split('-')); systems.append((int(page), a, b))
by_page = {}
for s in systems: by_page.setdefault(s[0], []).append(s)
for page_no, specs in by_page.items():
    page = doc[page_no]
    heads = []
    for span in page.get_texttrace():
        if span['font'].startswith(args.font) and span['size'] >= 12:
            for c in span['chars']:
                if c[0] in heads_codes: heads.append(c[2])
    words = [w for w in page.get_text('words') if not any(ch in w[4] for ch in 'œ˙') and w[4] not in ('-',) and w[3]-w[1] < 16]
    # staff tops = clusters of heads by y; use systems in order of y
    ys = sorted(y for _, y in heads)
    # split heads into systems by large y gaps between upper/lower staves: cluster into 2*len(specs) bands
    bands = [[ys[0]]]
    for y in ys[1:]:
        if y - bands[-1][-1] > 28: bands.append([y])
        else: bands[-1].append(y)
    if len(bands) != 2 * len(specs):
        print(f'page {page_no}: found {len(bands)} staff bands, expected {2*len(specs)}'); continue
    for i, (_, first, last) in enumerate(specs):
        top, bottom = bands[2 * i][0], bands[2 * i][-1]
        nxt = bands[2 * i + 1][0]
        xs = sorted(x for x, y in heads if top <= y <= bottom)
        cols = []
        for x in xs:
            if cols and x - cols[-1][-1] < 9: cols[-1].append(x)
            else: cols.append([x])
        cols = [sum(c) / len(c) for c in cols]
        grid = [(m, beat) for m in range(first, last + 1) for beat in onsets(m)]
        if len(cols) != len(grid):
            print(f'system {first}-{last}: {len(cols)} head columns vs {len(grid)} onsets'); problems += 1; continue
        lines = {}
        for w in words:
            if bottom + 4 < w[1] < nxt - 4: lines.setdefault(round(w[1]), []).append(w)
        rows = [lines[k] for k in sorted(lines)]
        for r, row in enumerate(rows[:len(song['verses'])]):
            verse = song['verses'][r]
            expected = {}
            for m in range(first, last + 1):
                for beat, text in cues(verse, m).items(): expected[(m, beat)] = text
            seen = set()
            for w in row:
                cx = (w[0] + w[2]) / 2 if len(w[4]) > 1 else w[0] + 3
                j = min(range(len(cols)), key=lambda k: abs(cols[k] - (w[0] + 4)))
                key = grid[j]
                text = expected.get(key)
                clean = lambda s: s.replace('-', '').replace('‿', ' ').replace('’', "'").strip()
                if text is None or clean(text).split()[0] != w[4].replace('’', "'").replace('ﬁ', 'fi').replace('ﬂ', 'fl').rstrip('-'):
                    print(f'verse {r+1} m{key[0]} b{key[1]:g}: printed "{w[4]}" at x={w[0]:.0f}, data "{text}"'); problems += 1
                seen.add(key); compared += 1
            for key, text in expected.items():
                if key not in seen: print(f'verse {r+1} m{key[0]} b{key[1]:g}: data "{text}" has no printed syllable'); problems += 1
print('problems:', problems, 'syllables compared:', compared)
