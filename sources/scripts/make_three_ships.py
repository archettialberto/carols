"""Build data/i-saw-three-ships.json: I Saw Three Ships (traditional English carol).
Source: the supplied one-page vector PDF (Sibelius/Opus, online edition), G major, 6/8,
eighth pickup + 8 bars on two staves, four printed stanzas (the only ones sung). Pitches from
vector_heads.py --font Opus --dot 2122 --key F# --clefs T,B; rhythms read from the page."""
from song_kit import crop_systems, fit_lyrics, save_song

PDF = 'songs/I Saw Three Ships.pdf'
parts = {  # data measure 1 is the eighth pickup; printed bar n is data measure n+1
    'soprano': ['D4:0.5', 'G4:1 G4:0.5 A4:1 B4:0.5', 'D5:1 B4:0.5 A4:1 C5:0.5',
                'B4:1 G4:0.5 G4:1 B4:0.5', 'A4:1 F#4:0.5 D4:1 D4:0.5',
                'G4:1 G4:0.5 A4:1 B4:0.5', 'D5:1 B4:0.5 A4:1 C5:0.5',
                'B4:1 G4:0.5 G4:0.5 A4:0.5 B4:0.5', 'A4:1.5 G4:1'],
    'alto': ['D4:0.5', 'D4:1 D4:0.5 D4:1 D4:0.5', 'G4:1 D4:0.5 D4:1 F#4:0.5',
             'E4:1 E4:0.5 E4:1 E4:0.5', 'F#4:1 D4:0.5 A3:1 C4:0.5',
             'B3:1 E4:0.5 D4:1 D4:0.5', 'G4:1 D4:0.5 D4:1 D4:0.5',
             'D4:1 B3:0.5 D4:0.5 D4:0.5 D4:0.5', 'D4:1 C4:0.5 B3:1'],
    'tenor': ['D4:0.5', 'B3:1 G3:0.5 F#3:1 G3:0.5', 'B3:1 G3:0.5 F#3:1 A3:0.5',
              'G3:1 B3:0.5 C4:1 C4:0.5', 'D4:1 A3:0.5 F#3:1 A3:0.5',
              'G3:1 B3:0.5 A3:1 G3:0.5', 'B3:1 G3:0.5 F#3:1 A3:0.5',
              'G3:1 G3:0.5 G3:0.5 G3:0.5 G3:0.5', 'F#3:1.5 G3:1'],
    'bass': ['D3:0.5', 'G2:1 B2:0.5 D3:1 G3:0.5', 'G2:1 B2:0.5 D3:1 D3:0.5',
             'E3:1 E3:0.5 C3:1 A2:0.5', 'D3:1 D3:0.5 D3:1 D3:0.5',
             'E3:1 E3:0.5 F#3:1 G3:0.5', 'G2:1 B2:0.5 D3:1 D3:0.5',
             'G2:1 G2:0.5 B2:0.5 B2:0.5 B2:0.5', 'D3:1.5 G2:1'],
}

LINE = [0], [0, 1, 1.5, 2.5], [0, 1, 1.5, 2.5]  # pickup, first bar, second bar (+ next "On")
CODA = [[0, 1, 1.5, 2.5], [0, 1, 1.5, 2.5], [0, 1, 1.5, 2.5], [0, 1, 1.5, 2, 2.5], [0, 1.5]]


def stanza(first, line, close, second_first):
    """first: pickup word; line: 'w w w w | w w w On' (the sung line, twice);
    close: 'mas day;' punctuation word; second_first: pickup word before the repeat."""
    a, b = line.split(' | ')
    words = [[first], a.split(), b.split(),
             ['Christ-', 'mas', 'day,', 'on'], ['Christ-', 'mas', close, second_first],
             a.split(), b.split(), ['Christ-', 'mas', 'day', 'in', 'the'], ['morn-', 'ing.']]
    onsets = [LINE[0], LINE[1], LINE[2]] + CODA[:2] + [LINE[1], LINE[2], CODA[3], CODA[4]]
    rows = []
    for beats, text in zip(onsets, words):
        assert len(beats) == len(text), (beats, text)
        rows.append(' '.join(f'{b:g}:{w}' for b, w in zip(beats, text)))
    return rows


texts = [  # the four printed stanzas
    ('I', 'saw three ships come | sail- ing in On', 'day;', 'I'),
    ('And', 'what was in those | ships all three, On', 'day?', 'And'),
    ('Our', 'Sa- vior Christ and | His la- dy, On', 'day:', 'Our'),
    ('Pray', 'whi- ther sailed those | ships all three, On', 'day?', 'Pray'),
]

verses = []
for number, text in enumerate(texts, 1):
    rows = stanza(*text)
    verses.append({'number': number, 'title': f'Strofa {number}',
                   'lyrics': {voice: fit_lyrics(parts[voice], rows) for voice in parts}})

systems = crop_systems('i-saw-three-ships', PDF,
                       [(3, .07, .29), (2, .29, .50), (2, .50, .71), (2, .72, .94)], x=(.05, .97))

song = {
    'id': 'i-saw-three-ships', 'title': 'I Saw Three Ships', 'emoji': '⛵',
    'composer': 'Traditional English carol', 'arranger': 'an online edition',
    'meter': [6, 8], 'key_fifths': 1, 'tempo': 132,
    'measure_beats': [0.5] + [3] * 7 + [2.5],
    'source_pdf': PDF,
    'review_notes': [
        'Pitches read from the embedded Opus glyphs (vector_heads.py) and checked against all four systems; rhythms read from the page.',
        'The eighth pickup is data measure 1, so printed bar n is data measure n+1. Final bar: dotted quarter + quarter (completes the pickup).',
        'The score prints stanzas 1–4, and only those are sung (stanzas 5–8 from a public-domain hymnal were removed 2026-11-15 at the user’s request, with stanza 7’s split notes); stanza 2 keeps the printed “what was in those ships”.',
        'Suggested tempo quarter = 132 (dotted quarter = 88), a lilting 6/8.',
    ],
    'parts': parts, 'playback': [{'measure': i} for i in range(1, 10)],
    'systems': systems, 'verses': verses,
    'staff_bands': {'soprano': [0, .5], 'alto': [0, .5], 'tenor': [.5, 1], 'bass': [.5, 1]},
    'shared_lyrics': True,
    'compact': {'instructions': 'Quattro strofe numerate sulle stesse note; testo comune alle quattro voci.'},
}

save_song(song)
