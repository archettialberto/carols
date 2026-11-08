"""Build data/what-child-is-this.json: What Child Is This (Greensleeves), arr. the arranger.
Source: the supplied an online edition PDF (capella vector engraving, page 3), E minor, 6/8, eighth
pickup + 16 bars on two staves, three stanzas (the hymn author). Pitches from
vector_heads.py --font capella --filled e5 --half none --dot 2e --accidentals 53,, --key F#
--clefs T,B; rhythms from the page (capella flags: e6 up, ea down)."""
from song_kit import crop_systems, fit_lyrics, save_song

PDF = 'songs/What Child Is This.pdf'
A1 = {'soprano': 'G4:1 A4:0.5 B4:0.75 C5:0.25 B4:0.5', 'alto': 'E4:1 D4:0.5 D4:1 G4:0.5',
      'tenor': 'B3:1 A3:0.5 G3:1 B3:0.5', 'bass': 'E3:1 F#3:0.5 G3:1 G3:0.5'}
A2 = {'soprano': 'A4:1 F#4:0.5 D4:0.75 E4:0.25 F#4:0.5', 'alto': 'F#4:1 D4:0.5 D4:1 C4:0.5',
      'tenor': 'D4:1 A3:0.5 F#3:1 A3:0.5', 'bass': 'D3:1 D3:0.5 D3:1 D#3:0.5'}
CADENCE = {'soprano': 'G4:0.75 F#4:0.25 E4:0.5 D#4:0.75 C#4:0.25 D#4:0.5', 'alto': 'B3:1 C4:0.5 B3:1 B3:0.5',
           'tenor': 'G3:1 A3:0.5 F#3:1 F#3:0.5', 'bass': 'E3:1 A2:0.5 B2:1 B2:0.5'}
B1 = {'soprano': 'D5:1.5 D5:0.75 C5:0.25 B4:0.5', 'alto': 'F#4:1.5 B4:0.75 A4:0.25 G4:0.5',
      'tenor': 'B3:1.5 D4:1 D4:0.5', 'bass': 'B3:1.5 G3:1 G3:0.5'}
rows = {
    'pickup': {'soprano': 'E4:0.5', 'alto': 'B3:0.5', 'tenor': 'G3:0.5', 'bass': 'E3:0.5'},
    'a3': {'soprano': 'G4:1 E4:0.5 E4:0.75 D#4:0.25 E4:0.5', 'alto': 'B3:1 B3:0.5 A3:1 E4:0.5',
           'tenor': 'G3:1 G3:0.5 E3:1 E3:0.5', 'bass': 'E3:1 E3:0.5 C3:1 C3:0.5'},
    'a4': {'soprano': 'F#4:1.5 B3:1 E4:0.5', 'alto': 'D#4:1.5 B3:1 B3:0.5',
           'tenor': 'B3:1.5 B3:1 G3:0.5', 'bass': 'B2:1.5 B3:1 E3:0.5'},
    'end8': {'soprano': 'E4:1.5 E4:1.5', 'alto': 'B3:1.5 B3:1.5', 'tenor': 'G3:1.5 G3:1.5', 'bass': 'E3:1.5 E3:1.5'},
    'b3': {'soprano': 'G4:1 E4:0.5 E4:0.75 D#4:0.25 E4:0.5', 'alto': 'B3:1 B3:0.5 A3:1 E4:0.5',
           'tenor': 'G3:1 G3:0.5 A3:1 E3:0.5', 'bass': 'E3:1 E3:0.5 C3:1 C3:0.5'},
    'b4': {'soprano': 'F#4:1 D#4:0.5 B3:1.5', 'alto': 'D#4:1 B3:0.5 B3:1.5',
           'tenor': 'B3:1 F#3:0.5 B3:1.5', 'bass': 'B2:1 B2:0.5 B2:1.5'},
    'end16': {'soprano': 'E4:1.5 E4:1', 'alto': 'B3:1.5 B3:1', 'tenor': 'G3:1.5 G3:1', 'bass': 'E3:1.5 E3:1'},
}
ORDER = ['pickup', A1, A2, 'a3', 'a4', A1, A2, CADENCE, 'end8', B1, A2, 'b3', 'b4', B1, A2, CADENCE, 'end16']
parts = {v: [(rows[b] if isinstance(b, str) else b)[v] for b in ORDER] for v in ('soprano', 'alto', 'tenor', 'bass')}

QE = [0, 1, 1.5, 2.5]   # quarter, eighth, dotted-eighth+16th (melisma), eighth
ONSETS = [[0], QE, QE, QE, [0, 1.5, 2.5], QE, QE, QE, [0, 1.5],
          [0, 1.5, 2.5], QE, QE, [0, 1, 1.5], [0, 1.5, 2.5], QE, QE, [0, 1.5]]
words = [
    'What | child is this, who, | laid to rest, on | Ma- ry’s lap is | sleep- ing? Whom |'
    ' an- gels greet with | an- thems sweet, while | shep- herds watch are | keep- ing? |'
    ' This, this is | Christ the King; whom | shep- herds guard and | an- gels sing: |'
    ' Haste, haste to | bring him laud, the | babe, the Son of | Ma- ry!',
    'Why | lies he in such | mean es- tate, where | ox and ass are | feed- ing? Good |'
    ' Christ- ian fear: for | sin- ners here the | si- lent Word is | plead- ing: |'
    ' Nails, spear shall | pierce him through, the | cross be borne, for | me, for you: |'
    ' Hail, hail, the | Word made flesh, the | babe, the Son of | Ma- ry!',
    'So | bring him in- cense, | gold and myrrh. Come | pea- sant, King to | own him; the |'
    ' King of kings, sal- | va- tion brings; let | lo- ving hearts en- | throne him. |'
    ' Raise, raise the | song on high, The | Vir- gin sings her | lul- la- by: |'
    ' Joy, joy for | Christ is born, the | babe, the Son of | Ma- ry!',
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

systems = crop_systems('what-child-is-this', PDF, [(5, .12, .31), (4, .32, .50), (4, .51, .70), (4, .71, .89)],
                       page=2, x=(.04, .97))

song = {
    'id': 'what-child-is-this', 'title': 'What Child Is This', 'emoji': '👶',
    'composer': 'Traditional', 'arranger': 'the arranger',
    'meter': [6, 8], 'key_fifths': 1, 'tempo': 78,
    'measure_beats': [0.5] + [3] * 15 + [2.5],
    'source_pdf': PDF,
    'review_notes': [
        'Pitches read from the capella glyphs (vector_heads.py with capella codes) and checked against all four systems; rhythms from the page.',
        'The eighth pickup is data measure 1 (printed bar n = data n+1); the last bar is dotted quarter + quarter.',
        'Printed bar 12 (data 13) drops the middle syllable in all three stanzas (“an - sing”, “me, you”, “lul - by”); the original text “angels sing”, “for me, for you”, “lullaby” is restored on the three printed notes.',
        'Edition typos corrected in stanza 2: “bourne” → “borne”, “bane” → “babe”.',
        'Suggested tempo quarter = 78 (dotted quarter = 52).',
    ],
    'parts': parts, 'playback': [{'measure': i} for i in range(1, 18)],
    'systems': systems, 'verses': verses,
    'staff_bands': {'soprano': [0, .5], 'alto': [0, .5], 'tenor': [.5, 1], 'bass': [.5, 1]},
    'shared_lyrics': True,
    'compact': {'instructions': 'Tre strofe numerate sulle stesse note; testo comune alle quattro voci.'},
}

save_song(song)
