"""Build data/good-king-wenceslas.json: Good King Wenceslas (a 16th-century tune), arr. the arranger,
words the author Source: the supplied one-page an online edition PDF in which every glyph
(notes and text) is an outlined path. Pitches were computed from the notehead path centres
(5.4×4.7 pt shapes; filled = quarter, hollow = half) against the staff lines, and checked on the
page; A major, 4/4, 17 bars, five stanzas."""
from song_kit import crop_systems, fit_lyrics, save_song

PDF = 'songs/Good King Wenceslas.pdf'
PHRASE = {  # bars 1–4, printed again as 5–8
    'soprano': ['A4:1 A4:1 A4:1 B4:1', 'A4:1 A4:1 E4:2', 'F#4:1 E4:1 F#4:1 G#4:1', 'A4:2 A4:2'],
    'alto': ['E4:1 E4:1 F#4:1 E4:1', 'E4:1 F#4:1 B3:2', 'D4:1 E4:1 D4:1 D4:1', 'C#4:2 C#4:2'],
    'tenor': ['C#4:1 C#4:1 C#4:1 B3:1', 'C#4:1 D4:1 G#3:2', 'A3:1 A3:1 A3:1 B3:1', 'E3:2 E3:2'],
    'bass': ['A3:1 A3:1 F#3:1 G#3:1', 'A3:1 D3:1 E3:2', 'D3:1 C#3:1 D3:1 B2:1', 'A2:2 A2:2'],
}
SECOND = {  # bars 9–17
    'soprano': ['E5:1 D5:1 C#5:1 B4:1', 'C#5:1 B4:1 A4:2', 'F#4:1 E4:1 F#4:1 G#4:1', 'A4:2 A4:2',
                'E4:1 E4:1 F#4:1 G#4:1', 'A4:1 A4:1 B4:2', 'E5:1 D5:1 C#5:1 B4:1', 'A4:2 D5:2', 'A4:4'],
    'alto': ['A4:1 A4:1 A4:1 G#4:1', 'A4:1 G#4:1 F#4:2', 'A3:1 E4:1 D4:1 D4:1', 'C#4:2 C#4:2',
             'E4:1 E4:1 D4:1 D4:1', 'C#4:1 C#4:1 E4:2', 'E4:1 A4:1 A4:1 G#4:1', 'A4:2 F#4:2', 'E4:4'],
    'tenor': ['E4:1 F#4:1 E4:1 E4:1', 'E4:1 E4:1 C#4:2', 'D4:1 A3:1 A3:1 B3:1', 'E3:2 E3:2',
              'A3:1 A3:1 A3:1 B3:1', 'A3:1 A3:1 G#3:2', 'A3:1 F#4:1 E4:1 F#4:1', 'C#4:2 D4:2', 'C#4:4'],
    'bass': ['C#3:1 D3:1 E3:1 E3:1', 'A3:1 E3:1 F#3:2', 'D3:1 C#3:1 D3:1 B2:1', 'A2:2 A2:2',
             'C#3:1 C#3:1 D3:1 B2:1', 'F#3:1 F#3:1 E3:2', 'C#3:1 D3:1 E3:1 E3:1', 'F#3:2 D3:2', 'A3:4'],
}
parts = {v: PHRASE[v] * 2 + SECOND[v] for v in PHRASE}

ONSETS = ([[0, 1, 2, 3], [0, 1, 2], [0, 1, 2, 3], [0, 2]] * 4) + [[0]]
ONSETS[15] = [0]  # bar 16: one syllable over the two-note melisma
words = [
    'Good King Wen- ces- | las looked out, | on the fest of | Ste- phen, | when the snow lay | round a- bout, |'
    ' deep and crisp and | e- ven: | Bright- ly shone the | moon that night, | though the frost was | cru- el, |'
    ' when a poor man | came in sight, | ga- th’ring win- ter | fu- | el.',
    '“Hi- ther page and | stand by me, | if thou know’st it | tell- ing, | yon- der pea- sant, | who is he? |'
    ' where and what his | dwell- ing?” | “Sire, he lives a | good league hence, | un- der- neath the | moun- tain; |'
    ' right a- gainst the | for- est fence, | by Saint Ag- nes | foun- | tain.”',
    '“Bring me flesh and | bring me wine, | bring me pine logs | hi- ther: | thou and I will | see him dine, |'
    ' when we bear them | thi- ther.” | Page and mon- arch | forth they went, | forth they went to- | geth- er; |'
    ' through the rude wind’s | wild la- ment | and the bit- ter | wea- | ther.',
    '“Sire, the night is | dark- er now, | and the wind blows | strong- er; | fails my heart, I | know not how, |'
    ' I can go no | lon- ger.” | “Mark my foot- steps, | good my page; | tread thou in them | bold- ly: |'
    ' thou shalt find the | win- ter’s rage | freeze thy blood less | cold- | ly.”',
    'In his mas- ter’s | steps he trod, | where the snow lay | dint- ed; | heat was in the | ve- ry sod |'
    ' which the saint had | print- ed. | There- fore, Christ- ian | men, be sure, | wealth or rank poss- | ess- ing, |'
    ' ye who now will | bless the poor, | shall your- selves find | bless- | ing.',
]
verses = []
for number, text in enumerate(words, 1):
    bars = [b.split() for b in text.split('|')]
    assert len(bars) == 17
    cues = []
    for m, (beats, syl) in enumerate(zip(ONSETS, bars), 1):
        assert len(beats) == len(syl), (number, m, syl)
        cues.append(' '.join(f'{b:g}:{w}' for b, w in zip(beats, syl)))
    verses.append({'number': number, 'title': f'Strofa {number}',
                   'lyrics': {v: fit_lyrics(parts[v], cues) for v in parts}})

systems = crop_systems('good-king-wenceslas', PDF, [(4, .08, .29), (4, .29, .50), (4, .50, .71), (5, .71, .93)],
                       x=(.05, .97))

song = {
    'id': 'good-king-wenceslas', 'title': 'Good King Wenceslas', 'emoji': '👑',
    'composer': 'a 16th-century tune; words the author', 'arranger': 'the arranger',
    'meter': [4, 4], 'key_fifths': 3, 'tempo': 120,
    'source_pdf': PDF,
    'review_notes': [
        'Pitches computed from the notehead path centres against the staff lines and checked on the page; durations from head shape (filled quarter, hollow half, whole in the last bar).',
        'Bar 11 alto is A3 (head centred below the C4 ledger; voice exchange with the tenor’s D4). The final chord is printed A4/E4 over C♯4/A3 (bass on A3).',
        'The edition suggests a dramatised performance: stanza 2 tenor solo (king) then treble solo (page); stanza 3 tenor solo then all; stanza 4 treble solo then tenor solo; stanzas 1 and 5 all. Playback keeps the full SATB texture.',
        'Default tempo quarter = 120 (user choice).',
    ],
    'parts': parts, 'playback': [{'measure': m} for m in range(1, 18)],
    'systems': systems, 'verses': verses,
    'staff_bands': {'soprano': [0, .5], 'alto': [0, .5], 'tenor': [.5, 1], 'bass': [.5, 1]},
    'shared_lyrics': True,
    'compact': {'instructions': 'Cinque strofe numerate sulle stesse note; testo comune alle quattro voci.',
                'notes': ['Suggerimento dell’edizione: str. 2 tenore solo (re), poi soprano solo (paggio); '
                          'str. 3 tenore solo, poi tutti; str. 4 soprano solo, poi tenore solo; str. 1 e 5 tutti.']},
}

save_song(song)
