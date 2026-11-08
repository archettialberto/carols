"""Build data/dio-ci-benedira.json: Dio ci benedirà (the composers), SATB.
Source: the supplied six-page Finale vector PDF (Maestro font; a local choir,
a local choir), E♭ major → F major at bar 64, 4/4 with 2/4 bars 87 and 89, 96 bars on four
staves, one through-composed text. Notes, rhythms, ties and syllables are read by
vector_score.read_page and checked against the page; fixes are listed below."""
import re
import sys
from pathlib import Path

import fitz
sys.path.insert(0, str(Path(__file__).parent))
import vector_score as vs  # noqa: E402
from song_kit import crop_systems, save_song  # noqa: E402

PDF = 'songs/Dio ci benedirà.pdf'
VOICES = ['soprano', 'alto', 'tenor', 'bass']
PAGES = {0: 6, 1: 15, 2: 32, 3: 47, 4: 67, 5: 83}   # first sounding measure on each page
REST_BARS = [1, 2, 3, 4, 5, 28, 29, 52, 53, 54]        # printed multirests (instrumental bars)
SHORT = {87: 2, 89: 2}                                 # 2/4 bars inside the 4/4 meter
LAST = 96

bars = {v: {} for v in VOICES}
for page, first in PAGES.items():
    systems, _ = vs.read_page(PDF, page, ['T', 'T', 'T8', 'B'], 'B,E,A', (64, vs.parse_key('B')), 4.0, 'Maestro', first)
    for system in systems:
        for k, staff in enumerate(system['staves']):
            for bar in staff:
                if not bar['rest_bars'] and bar['measure'] <= LAST:
                    bars[VOICES[k]][bar['measure']] = bar['notes']

# Bar 90: the tempo text “Rall.” sits where the syllable “Dio” belongs (bass reads it correctly).
for v in ('soprano', 'alto', 'tenor'):
    for note in bars[v][90]:
        if note['syl'] == 'Rall.': note['syl'] = None
    [n for n in bars[v][90] if n['pitch'] != 'R'][-1]['syl'] = 'Dio'

# Ties across system and page breaks: a bar that opens on the previous pitch with no new syllable.
for v in VOICES:
    previous = None
    for m in range(1, LAST + 1):
        notes = bars[v].get(m, [])
        if notes and previous and notes[0]['pitch'] == previous['pitch'] != 'R' and not notes[0]['syl']:
            previous['tie'] = True
        previous = notes[-1] if notes else None

TEXT = ('Notte di felicità, notte di Natale. Ogni cuor esulta già, libero dal male. Il Signore di lassù '
        'sempre guiderà; ci ascolterà, ci aiuterà, che lodato sia. Inizia qui il miracolo, Dio ci benedirà! '
        'Per chi è solo e soffrirà, noi pregheremo, con amore e carità, forza infonderemo; padri, madri, '
        'figli che sono in armonia, si amano, si cercano, si ritrovano; e l’amore vincerà, Dio ci benedirà! '
        'Inizia qui il miracolo, Dio ci benedirà! Notte di felicità, notte di Natale; ogni cuor esulta già, '
        'libero dal male. Padri, madri, figli che, sono in armonia; si amano, si cercano, si ritrovano. '
        'E l’amore vincerà, Dio ci benedirà! Inizia qui il miracolo! Dio ci benedirà!')
norm = lambda s: re.sub(r"[^a-zàèéìòù']", '', s.lower().replace('’', "'"))


def syllabify(voice):
    """Per-measure cue strings: printed syllables joined into the words of TEXT with '-'.
    An elision dot (ci.as) becomes ‿ and closes the first word."""
    words, i, buffer, cues = [norm(w) for w in TEXT.split()], 0, '', []
    for m in range(1, LAST + 1):
        at, out = 0, []
        for note in bars[voice].get(m, []):
            if note['pitch'] != 'R' and note['syl']:
                ended = False
                for part in re.split(r'(?<=\w)\.(?=\w)', note['syl']):
                    buffer += norm(part)
                    assert words[i].startswith(buffer), (voice, m, note['syl'], words[i], buffer)
                    ended = buffer == words[i]
                    if ended: i, buffer = i + 1, ''
                text = re.sub(r'(?<=\w)\.(?=\w)', '‿', note['syl']).replace("'", '’') + ('' if ended else '-')
                out.append(f'{at:g}:{text}')
            at += note['duration']
        cues.append(' '.join(out))
    assert i == len(words), (voice, i, len(words))
    return cues


def bar_string(voice, m):
    if m in REST_BARS: return 'R:4'
    notes = bars[voice][m]
    if not notes: return f'R:{SHORT.get(m, 4)}'
    return ' '.join(f"{n['pitch']}:{n['duration']:g}{'~' if n['tie'] else ''}" for n in notes)


# All printed bars are kept. No accompaniment is printed, so (at the user's request) an organ part
# is added: it doubles the four choir parts, and in the instrumental multirest bars it plays
# printed choir music: intro 1–5 = bars 6–9 + an E♭ chord, 28–29 = bars 6–7, 52–54 = bars 49–51.
KEEP = list(range(1, LAST + 1))
parts = {v: [bar_string(v, m) for m in KEEP] for v in VOICES}
lyrics = {v: syllabify(v) for v in VOICES}
data_no = {m: m for m in KEEP}
FILL = {1: 6, 2: 7, 3: 8, 4: 9, 28: 6, 29: 7, 52: 49, 53: 50, 54: 51}
ENDING = {'soprano': 'G4:4', 'alto': 'Eb4:4', 'tenor': 'Bb3:4', 'bass': 'Eb3:4'}  # bar 5: E♭ chord
organ = {f'organ_{v}': [ENDING[v] if m == 5 else bar_string(v, FILL.get(m, m)) for m in KEEP] for v in VOICES}
# A tie into a filled bar would break: the organ restarts the note instead.
for lane in organ.values():
    for i in range(len(lane) - 1):
        if lane[i].endswith('~') and (i + 2 in FILL or i + 2 == 5 or i + 1 in FILL or i + 1 == 5):
            lane[i] = lane[i][:-1]
divisi = sorted({m for m in range(1, LAST + 1) if m not in REST_BARS
                 for n in bars['soprano'][m] if len(n['chord']) > 1})

# Systems as printed: (measures, page); crop bands from the staff positions.
LAYOUT = [(0, [9, 5]), (1, [5, 5, 7]), (2, [5, 5, 5]), (3, [8, 6, 6]), (4, [5, 5, 6]), (5, [6, 7, 1])]
systems, measure, index = [], 1, 0
doc = fitz.open(PDF)
for page, counts in LAYOUT:
    height = doc[page].rect.height
    tops = sorted({round(y, 1) for d in doc[page].get_drawings() for it in d['items'] if it[0] == 'l'
                   and abs(it[1].y - it[2].y) < .01 and abs(it[1].x - it[2].x) > 300 for y in [it[1].y]})
    staff_tops = [y for i, y in enumerate(tops) if i == 0 or y - tops[i - 1] > 12]
    bands = []
    for s in range(len(counts)):
        top, bottom = staff_tops[4 * s] - 28, staff_tops[4 * s + 3] + 50
        bands.append((counts[s], max(0, top / height), min(1, bottom / height)))
    first_kept = next(data_no[m] for m in range(measure, LAST + 1) if m in data_no)
    systems += crop_systems('dio-ci-benedira', PDF, bands, page=page, x=(.07, .97), first=first_kept, start_index=index)
    measure += sum(counts); index += len(counts)

song = {
    'id': 'dio-ci-benedira', 'title': 'Dio ci benedirà', 'emoji': '🙏',
    'composer': 'the composers', 'arranger': 'a local choir',
    'meter': [4, 4], 'key_fifths': -3, 'measure_keys': {str(data_no[64]): -1}, 'tempo': 96,
    'measure_beats': [SHORT.get(m, 4) for m in KEEP],
    'source_pdf': PDF,
    'sources': [{'description': 'Supplied six-page Finale vector PDF (Maestro font), SATB on four staves; all notes and words.'}],
    'review_notes': [
        'Notes, rhythms, ties and syllables read from the vector glyphs with sources/scripts/vector_score.py and compared with every page.',
        'Printed bars 1–5, 28–29 and 52–54 are multirests for an accompaniment that is not printed. At the user’s request an organ part was added (not printed in the source, arranged here): it doubles the choir throughout and plays choir material in those bars (intro = bars 6–9 + E♭ chord; 28–29 = bars 6–7; 52–54 = bars 49–51).',
        f'The sopranos divide in (printed) bars {", ".join(map(str, divisi))}; the data keeps the upper (melody) note of each printed dyad.',
        'Key change to F major at printed bar 64; printed bars 87 and 89 are printed in 2/4 (shown as short bars, the engraving keeps 4/4).',
        'The score prints no hyphens; word divisions follow the Italian text. Printed elisions (ci.as, qui.il, …) are shown with ‿.',
        'No tempo is printed: quarter = 96 is a suggested moderate tempo; the closing “Rall.” is not applied automatically.',
    ],
    'backing_track': {'instrument': 'organ', 'parts': organ},
    'parts': parts, 'playback': [{'measure': m} for m in range(1, len(KEEP) + 1)],
    'systems': systems,
    'verses': [{'number': 1, 'title': 'Testo', 'lyrics': lyrics}],
    'staff_bands': {'soprano': [0, .25], 'alto': [.25, .5], 'tenor': [.5, .75], 'bass': [.75, 1]},
    'shared_lyrics': True,
    'compact': {},
}

save_song(song)
