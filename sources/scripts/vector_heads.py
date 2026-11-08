"""Dump noteheads and rests from a vector PDF page (Finale/Sibelius/etc. exports).

For each staff, prints x-sorted groups with the exact pitch (key signature and printed
accidentals applied per head), head type (q = filled, h = half, w = whole), augmentation dot
and stem direction, plus quarter-rest positions. Rhythm and voice assignment still need to be
read from the page; pitches are exact. Development only; requires PyMuPDF.

  python sources/scripts/vector_heads.py PDF PAGE [--font Opus] [--filled 153] [--half 2d9]
         [--dot 2e] [--key B,E | --key F#,C#] [--clefs T,B]

--clefs repeats over the staves of each system: T = treble, T8 = treble sounding an octave
lower (tenor), B = bass. E.g. SATB on two staves: T,B; on four staves: T,T,T8,B.
Glyphs per font: Finale Maestro/Petrucci: filled 153, half 2d9, dot 2e;
Sibelius Opus: filled 153, half 2d9, dot 2122 (OpusSpecialStd). Rests: 152 = quarter.
capella (capella3): --font capella --filled e5 --half none --dot 2e --accidentals 53,, ; flags e6 (up) and ea (down).
"""
import argparse
import fitz

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('pdf'); parser.add_argument('page', type=int, help='0-based page index')
parser.add_argument('--font', default='Petrucci', help='music font name prefix')
parser.add_argument('--filled', default='153'); parser.add_argument('--half', default='2d9')
parser.add_argument('--whole', default='77'); parser.add_argument('--dot', default='2e')
parser.add_argument('--rest', default='152', help='quarter-rest glyph')
parser.add_argument('--key', default='', help='accidentals in the key, e.g. B,E or F#,C#')
parser.add_argument('--clefs', default='T,B')
parser.add_argument('--accidentals', default='23,62,6e',
                    help='hex glyphs for sharp,flat,natural (Opus/Petrucci: 23,62,6e; capella: e6,?,?)')
args = parser.parse_args()
code = lambda value: -1 if value == 'none' else int(value, 16)
filled, half, whole, dot, rest = map(code, (args.filled, args.half, args.whole, args.dot, args.rest))
key = {item[0]: ('#' if '#' in item else 'b') for item in args.key.split(',') if item}
clefs = args.clefs.split(',')
acc_codes = {int(h, 16): sign for h, sign in zip(args.accidentals.split(','), '#bn') if h not in ('', '?')}
TOP_LINE = {'T': 38, 'T8': 31, 'B': 26}  # diatonic index of each clef's top line: F5, F4 sounding, A3

page = fitz.open(args.pdf)[args.page]
segs = [it for d in page.get_drawings() for it in d['items'] if it[0] == 'l']
# Some engravers (capella) draw staff lines and stems as hairline rectangles: use their centre line.
for d in page.get_drawings():
    for it in d['items']:
        if it[0] == 're':
            r = it[1]
            if r.height < 1 and r.width > 2: segs.append(('l', fitz.Point(r.x0, (r.y0 + r.y1) / 2), fitz.Point(r.x1, (r.y0 + r.y1) / 2)))
            elif r.width < 1 and r.height > 2: segs.append(('l', fitz.Point((r.x0 + r.x1) / 2, r.y0), fitz.Point((r.x0 + r.x1) / 2, r.y1)))
raw = sorted(set(round(a.y, 2) for _, a, b in segs if abs(a.y - b.y) < .01 and abs(a.x - b.x) > 300))
lines = []  # thick staff lines may be drawn as several thin strokes: use their centre
for y in raw:
    if lines and y - lines[-1][-1] < 1: lines[-1].append(y)
    else: lines.append([y])
lines = [round(sum(g) / len(g), 2) for g in lines]
tops = [y for i, y in enumerate(lines) if y > 1 and (i == 0 or y - lines[i - 1] > 8)]
gap = lines[lines.index(tops[0]) + 1] - tops[0]
stems = [(a.x, min(a.y, b.y), max(a.y, b.y)) for _, a, b in segs if abs(a.x - b.x) < .01 and abs(a.y - b.y) > 2.5 * gap]
heads, dots, accs, rests = [], [], [], []
for span in page.get_texttrace():
    if not span['font'].startswith(args.font) or span['size'] < 12:
        continue  # small cue/range notes are ignored
    for c in span['chars']:
        x, y = c[2]
        if c[0] in (filled, half, whole): heads.append((x, y, {filled: 'q', half: 'h', whole: 'w'}[c[0]]))
        elif c[0] == dot: dots.append((x, y))
        elif c[0] == rest: rests.append((x, y))
        elif c[0] in acc_codes: accs.append((x, y, acc_codes[c[0]]))
for index, top in enumerate(tops):
    clef = clefs[index % len(clefs)]
    print(f'--- staff {index} ({clef}) top={top}')
    staff_rests = sorted(round(x, 1) for x, y in rests if top - gap < y < top + 5 * gap)
    if staff_rests: print('quarter rests at', staff_rests)
    mine = sorted(h for h in heads if top - 4 * gap < h[1] < top + 8 * gap)
    groups = []
    for h in mine:
        if groups and h[0] - groups[-1][-1][0] < 4: groups[-1].append(h)
        else: groups.append([h])
    for group in groups:
        out = []
        for x, y, kind in sorted(group, key=lambda h: h[1]):
            diatonic = TOP_LINE[clef] - round((y - top) / (gap / 2))
            letter = 'CDEFGAB'[diatonic % 7]
            # Key signature by default; a printed accidental just left of the head overrides it.
            printed = next((a for ax, ay, a in accs if 0 < x - ax < 14 and abs(ay - y) < 2), '')
            accidental = {'#': '#', 'b': 'b', 'n': ''}.get(printed, key.get(letter, ''))
            up = any(abs(sx - (x + 5.5)) < 2 and abs(y1 - y) < 3 for sx, y0, y1 in stems)
            down = any(abs(sx - x) < 2 and abs(y0 - y) < 3 for sx, y0, y1 in stems)
            dotted = any(0 < dx - x < 14 and abs(dy - y) < 3 for dx, dy in dots)
            mark = f'[{printed}]' if printed else ''
            out.append(f"{mark}{letter}{accidental}{diatonic // 7}{kind}{'.' if dotted else ''}{'^' if up else ''}{'v' if down else ''}")
        print(round(group[0][0], 1), ' '.join(out))
