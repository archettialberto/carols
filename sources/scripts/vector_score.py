"""Draft a score (our `pitch:duration` bars plus printed syllables) from a vector PDF whose music
font exposes noteheads, flags, dots, rests and accidentals as text glyphs (Finale Maestro /
Petrucci). Development only; requires PyMuPDF. Beams, tuplets and grace notes are not
interpreted, so every draft must still be checked against the page.

  python sources/scripts/vector_score.py PDF PAGE --clefs T,T,T8,B --key B,E,A [--first 6]
         [--key-from 64:B] [--meter 4]

Prints every staff of every system, one line per bar: `m<n> <notes>  [total]` (`!!` marks a total
different from --meter; time-signature changes are not read). Chords print as `{C5/Ab4}` (top
first; the draft keeps the top note). A curve joining two equal pitches is a tie only when the
second note carries no new syllable. A digit above an otherwise empty bar is a multirest.
Syllables are the lyric words printed between a staff and the next one (`@syl`).

Import `read_page(...)` to get the same data as Python structures.
"""
import argparse
import fitz

HEADS = {0x153: 1.0, 0x2d9: 2.0, 0x77: 4.0}
DOT, FLAG8, FLAG16 = 0x2e, {0x6a, 0x4a}, {0x6b, 0x4b}
RESTS = {0x152: 1.0, 0x2030: 0.5, 0xd3: 2.0, 0x2211: 'bar', 0x2264: 0.25}
ACCS = {0x23: '#', 0x62: 'b', 0x6e: 'n'}
TOP_LINE = {'T': 38, 'T8': 31, 'B': 26}  # diatonic index of each clef's top line: F5, F4 sounding, A3


def parse_key(text):
    return {i[0]: ('#' if '#' in i else 'b') for i in text.split(',') if i}


def read_page(pdf, page_no, clefs, key='', key_from=None, meter=4.0, font='Maestro', first=1):
    """Return (systems, next_measure). systems = [ {measures:[...], staves:[ [bar,...] ]} ],
    bar = {'measure', 'notes':[{'pitch','duration','tie','chord','syl'}], 'rest_bars'}."""
    page = fitz.open(pdf)[page_no]
    key = parse_key(key)
    hor, ver, curves = [], [], []
    for d in page.get_drawings():
        for it in d['items']:
            if it[0] == 'l':
                a, b = it[1], it[2]
                if abs(a.y - b.y) < .01 and abs(a.x - b.x) > 300: hor.append(round(a.y, 2))
                elif abs(a.x - b.x) < .01: ver.append((a.x, min(a.y, b.y), max(a.y, b.y)))
            elif it[0] == 're':
                r = it[1]
                if r.height < 1 and r.width > 300: hor.append(round((r.y0 + r.y1) / 2, 2))
                elif r.width < 1.5 and r.height > 2: ver.append(((r.x0 + r.x1) / 2, r.y0, r.y1))
            elif it[0] == 'c':
                curves.append((it[1], it[4]))
    lines = []
    for y in sorted(set(hor)):
        if lines and y - lines[-1][-1] < 1: lines[-1].append(y)
        else: lines.append([y])
    lines = [sum(g) / len(g) for g in lines]
    tops = [y for i, y in enumerate(lines) if i == 0 or y - lines[i - 1] > 12]
    gap = lines[1] - lines[0]
    glyphs, words = [], []
    for span in page.get_texttrace():
        if span['font'].startswith(font):
            if span['size'] >= 12:
                glyphs += [(c[0], c[2][0], c[2][1]) for c in span['chars']]
        else:
            word = None
            for c in span['chars']:
                ch = chr(c[0]); x0, y0, x1, y1 = c[3]
                if ch.isspace():
                    word = None; continue
                if word and x0 - word['x1'] < 1.5 and abs(y1 - word['y']) < 2:
                    word['text'] += ch; word['x1'] = x1
                else:
                    word = {'text': ch, 'x0': x0, 'x1': x1, 'y': y1}; words.append(word)

    def staff_of(y):
        for i, top in enumerate(tops):
            below = tops[i + 1] if i + 1 < len(tops) else top + 14 * gap
            if top - 6 * gap < y < (top + 4 * gap + below) / 2: return i
        return None

    systems, measure = [], first
    n = len(clefs)
    for s in range(0, len(tops), n):
        sys_tops = tops[s:s + n]
        s_top, s_bottom = sys_tops[0], sys_tops[-1] + 4 * gap
        xs = []
        for x in sorted(round(x, 1) for x, y0, y1 in ver if y1 - y0 >= 4 * gap - .6 and s_top - 1 <= y0 <= s_bottom
                        and any(y0 <= t + .6 and y1 >= t + 4 * gap - .6 for t in sys_tops)):
            if not xs or x - xs[-1] > 3: xs.append(x)
        staves, layout = [], None
        for k, top in enumerate(sys_tops):
            clef, staff = clefs[k], s + k
            mine = [g for g in glyphs if staff_of(g[2]) == staff]
            heads = [(x, y, HEADS[c]) for c, x, y in mine if c in HEADS]
            dots = [(x, y) for c, x, y in mine if c == DOT]
            flags8 = [x for c, x, y in mine if c in FLAG8]
            flags16 = [x for c, x, y in mine if c in FLAG16]
            rests = [(x, y, RESTS[c]) for c, x, y in mine if c in RESTS]
            accs = [(x, y, ACCS[c]) for c, x, y in mine if c in ACCS]
            digits = [(x, int(chr(c))) for c, x, y in mine if chr(c).isdigit() and y < top]
            lyric_top, lyric_bottom = top + 4 * gap, (sys_tops[k + 1] if k + 1 < n else top + 12 * gap)
            syllables = [w for w in words if lyric_top + 2 < w['y'] < lyric_bottom + 1]
            events = sorted([('n', x, y, d) for x, y, d in heads] + [('r', x, y, d) for x, y, d in rests],
                            key=lambda e: e[1])
            first_event = min((e[1] for e in events), default=xs[0] if xs else 0)
            cuts = [x for x in xs if x > first_event - 70]
            if cuts and cuts[0] > first_event: cuts.insert(0, first_event - 20)
            bars, m = [], measure
            for b in range(len(cuts) - 1):
                lo, hi = cuts[b], cuts[b + 1]
                bar_key = key_from[1] if key_from and m >= key_from[0] else key
                inbar = [e for e in events if lo < e[1] < hi]
                multi = [d for x, d in digits if lo < x < hi]
                if not inbar and multi:
                    bars.append({'measure': m, 'notes': [], 'rest_bars': multi[0]}); m += multi[0]; continue
                groups = []
                for e in inbar:
                    if groups and e[0] == 'n' and groups[-1][0][0] == 'n' and abs(e[1] - groups[-1][0][1]) < 4:
                        groups[-1].append(e)
                    else: groups.append([e])
                state, notes = {}, []
                for g in groups:
                    kind, x, y0, base = g[0]
                    dotted = any(0 < dx - x < 16 and abs(dy - y0) < 6 for dx, dy in dots)
                    if kind == 'r':
                        d = meter if base == 'bar' else base * (1.5 if dotted else 1)
                        notes.append({'pitch': 'R', 'duration': d, 'tie': False, 'chord': [], 'syl': None, 'x': x})
                        continue
                    pitches = []
                    for _, hx, hy, _ in sorted(g, key=lambda e: e[2]):
                        dia = TOP_LINE[clef] - round((hy - top) / (gap / 2))
                        letter, octave = 'CDEFGAB'[dia % 7], dia // 7
                        printed = next((a for ax, ay, a in accs if 0 < hx - ax < 14 and abs(ay - hy) < 2), None)
                        if printed: state[(letter, octave)] = '' if printed == 'n' else printed
                        pitches.append((f"{letter}{state.get((letter, octave), bar_key.get(letter, ''))}{octave}", hx, hy))
                    if base == 1.0:
                        if any(-3 < fx - x < 14 for fx in flags16): base = 0.25
                        elif any(-3 < fx - x < 14 for fx in flags8): base = 0.5
                    syl = [w['text'] for w in syllables if x - 8 < (w['x0'] + w['x1']) / 2 < x + 16]
                    tie_to = None
                    for p0, p3 in curves:
                        if abs(p0.x - (x + 5)) < 9 and abs(p0.y - pitches[0][2]) < 9 and p3.x - p0.x > 6:
                            tie_to = p3.x
                    notes.append({'pitch': pitches[0][0], 'duration': base * (1.5 if dotted else 1), 'tie': tie_to,
                                  'chord': [p[0] for p in pitches], 'syl': syl[0] if syl else None, 'x': x})
                bars.append({'measure': m, 'notes': notes, 'rest_bars': 0}); m += 1
            staves.append(bars)
            layout = m
        # Resolve ties: the curve must land on the next note of the same pitch carrying no syllable.
        flat = [[n for bar in staff for n in bar['notes']] for staff in staves]
        for notes in flat:
            for i, note in enumerate(notes):
                if note['tie'] is None or note['tie'] is False:
                    note['tie'] = False; continue
                nxt = notes[i + 1] if i + 1 < len(notes) else None
                note['tie'] = bool(nxt and nxt['pitch'] == note['pitch'] and not nxt['syl'])
        systems.append({'first': measure, 'staves': staves})
        measure = layout or measure
    return systems, measure


def bar_text(bar):
    return ' '.join(f"{n['pitch']}:{n['duration']:g}{'~' if n['tie'] else ''}" for n in bar['notes'])


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('pdf'); ap.add_argument('page', type=int)
    ap.add_argument('--clefs', default='T,T,T8,B'); ap.add_argument('--key', default='')
    ap.add_argument('--key-from', default='', help='measure:accidentals, e.g. 64:B')
    ap.add_argument('--meter', type=float, default=4.0)
    ap.add_argument('--font', default='Maestro'); ap.add_argument('--first', type=int, default=1)
    a = ap.parse_args()
    kf = (int(a.key_from.split(':')[0]), parse_key(a.key_from.split(':')[1])) if a.key_from else None
    systems, _ = read_page(a.pdf, a.page, a.clefs.split(','), a.key, kf, a.meter, a.font, a.first)
    for i, system in enumerate(systems, 1):
        for k, staff in enumerate(system['staves'], 1):
            print(f'--- system {i} staff {k}')
            for bar in staff:
                if bar['rest_bars']:
                    print(f"  m{bar['measure']} multirest {bar['rest_bars']}"); continue
                total = sum(n['duration'] for n in bar['notes'])
                chords = ' '.join('{' + '/'.join(n['chord']) + '}' for n in bar['notes'] if len(n['chord']) > 1)
                syl = ' '.join(n['syl'] or '_' for n in bar['notes'] if n['pitch'] != 'R')
                print(f"  m{bar['measure']} {bar_text(bar)}   [{total:g}]{'' if abs(total - a.meter) < 1e-6 else ' !!'}"
                      f"   @ {syl} {chords}")
