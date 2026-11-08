"""Build data/o-holy-night.json: O Holy Night (the composer), SATB in Db major, 6/8.
Source: the supplied two-page vector PDF (Sibelius/Opus, online edition), 50 bars on two
staves, three printed stanzas. Pitches from vector_heads.py --font Opus --dot 2122
--key B,E,A,D,G --clefs T,B; rhythms from the page and the Opus flag/rest glyph positions."""
from song_kit import crop_systems, fit_lyrics, save_song

PDF = 'songs/O Holy Night.pdf'
# One string per bar; '|' separates bars. Accidentals persist through a bar as printed.
S = ('F4:1.5 F4:1 F4:0.5 | Ab4:2 R:0.5 Ab4:0.5 | Bb4:1 Bb4:0.5 Gb4:1 Bb4:0.5 | Db5:3 |'
     'Ab4:1 Ab4:0.5 F4:1 Eb4:0.5 | Db4:1.5 F4:1 Gb4:0.5 | Ab4:1.5 Gb4:1 Eb4:0.5 | Db4:3~ | Db4:3 |'
     'F4:1.5 F4:1 F4:0.5 | Ab4:2 R:0.5 Ab4:0.5 | Bb4:1 Bb4:0.5 Gb4:1 Bb4:0.5 | Db5:3 |'
     'Ab4:1 Ab4:0.5 G4:1 F4:0.5 | C5:1.5 Ab4:1 Bb4:0.5 | C5:1.5 Db5:1 C5:0.5 | F4:3~ |'
     'F4:2 R:0.5 Ab4:0.5 | Ab4:1.5 Bb4:1.5 | Eb4:1.5 Ab4:1.5 | Bb4:1 Ab4:0.5 Db5:1 F4:0.5 |'
     'Bb4:1.5 Ab4:1 Ab4:0.5 | Ab4:1.5 Bb4:1.5 | Eb4:1.5 Ab4:1.5 | Bb4:1 Ab4:0.5 Db5:1 F4:0.5 | Ab4:3 |'
     'Db5:3~ | Db5:1.5 C5:1 Bb4:0.5 | C5:3~ | C5:2 R:0.5 C5:0.5 | Eb5:3~ | Eb5:1 Bb4:0.5 Bb4:1 Bb4:0.5 |'
     'Db5:3 | Db5:2 R:0.5 Db5:0.5 | F5:3 | Eb5:2~ Eb5:0.5 Ab4:0.5 | Db5:3~ | Db5:1.5 C5:1 Bb4:0.5 |'
     'Ab4:3~ | Ab4:1 Ab4:0.5 Bb4:1 Ab4:0.5 | Ab4:3~ | Ab4:1.5 Db5:1.5 | Eb5:3~ | Eb5:1.5 Ab4:1.5 |'
     'Ab5:3~ | Ab5:0.75 Gb5:0.75 F5:0.75 Eb5:0.75 | Db5:3 | C5:1.5 Db5:1 Eb5:0.5 | Db5:3~ | Db5:3')
A = ('Db4:1.5 Db4:1 Db4:0.5 | F4:2 R:0.5 F4:0.5 | Gb4:1 Gb4:0.5 Gb4:1 Gb4:0.5 | F4:3 |'
     'F4:1 F4:0.5 Db4:1 Db4:0.5 | Db4:1.5 Db4:1 Db4:0.5 | C4:1.5 C4:1 C4:0.5 | Db4:3~ | Db4:3 |'
     'Db4:1.5 Db4:1 Db4:0.5 | F4:2 R:0.5 F4:0.5 | Gb4:1 Gb4:0.5 Gb4:1 Gb4:0.5 | F4:3 |'
     'F4:1 F4:0.5 F4:1 F4:0.5 | Ab4:1.5 F4:1 F4:0.5 | E4:1.5 E4:1 E4:0.5 | F4:3~ |'
     'F4:2 R:0.5 F4:0.5 | Gb4:1.5 Gb4:1.5 | Eb4:1.5 Gb4:1.5 | F4:1 F4:0.5 F4:1 F4:0.5 |'
     'F4:1.5 F4:1 F4:0.5 | Gb4:1.5 Gb4:1.5 | Eb4:1.5 Gb4:1.5 | F4:1 F4:0.5 F4:1 F4:0.5 | F4:3 |'
     'F4:3~ | F4:1.5 F4:1 F4:0.5 | Ab4:3~ | Ab4:2 R:0.5 F4:0.5 | Gb4:3~ | Gb4:1 Gb4:0.5 Gb4:1 Gb4:0.5 |'
     'F4:3 | F4:2 R:0.5 Gb4:0.5 | Ab4:3~ | Ab4:2~ Ab4:0.5 Gb4:0.5 | Ab4:3 | Bb4:1.5 Ab4:1 Gb4:0.5 |'
     'F4:3 | Gb4:1 Gb4:0.5 Gb4:1 Gb4:0.5 | F4:3~ | F4:1.5 Ab4:1.5 | Ab4:3~ | Ab4:1.5 Ab4:1.5 |'
     'Ab4:3 | Bb4:1.5 Bb4:1.5 | Ab4:3 | Gb4:1.5 F4:1 Gb4:0.5 | F4:3~ | F4:3')
T = ('Ab3:1.5 Ab3:1 Ab3:0.5 | Db4:2 R:0.5 Db4:0.5 | Db4:1 Db4:0.5 Bb3:1 Db4:0.5 | Db4:3 |'
     'Db4:1 Db4:0.5 Ab3:1 Gb3:0.5 | F3:1.5 Ab3:1 Ab3:0.5 | Eb3:1.5 Eb3:1 Gb3:0.5 | F3:3~ | F3:3 |'
     'Ab3:1.5 Ab3:1 Ab3:0.5 | Db4:2 R:0.5 Db4:0.5 | Db4:1 Db4:0.5 Bb3:1 Db4:0.5 | Db4:3 |'
     'Db4:1 Db4:0.5 B3:1 B3:0.5 | C4:1.5 C4:1 C4:0.5 | Bb3:1.5 Bb3:1 Bb3:0.5 | Ab3:3~ |'
     'Ab3:2 R:0.5 C4:0.5 | C4:1.5 C4:1.5 | Ab3:1.5 C4:1.5 | Db4:1 Db4:0.5 Ab3:1 Ab3:0.5 |'
     'Db4:1.5 Db4:1 Db4:0.5 | C4:1.5 C4:1.5 | Ab3:1.5 C4:1.5 | Db4:1 Db4:0.5 Ab3:1 Ab3:0.5 | Db4:3 |'
     'Db4:3~ | Db4:1.5 Eb4:1 Db4:0.5 | C4:3~ | C4:2 R:0.5 Ab3:0.5 | Bb3:3~ | Bb3:1 Eb4:0.5 Eb4:1 Eb4:0.5 |'
     'Db4:3 | Db4:2 R:0.5 Db4:0.5 | Db4:3 | C4:2 R:0.5 C4:0.5 | Db4:3~ | Db4:1.5 Db4:1.5 |'
     'Db4:3 | C4:1 C4:0.5 C4:1 C4:0.5 | Db4:3~ | Db4:1.5 Db4:1.5 | C4:3~ | C4:1.5 C4:1.5 |'
     'Db4:3~ | Db4:1.5 Db4:0.75 Eb4:0.75 | F4:3 | Eb4:1.5 Db4:1 C4:0.5 | Ab3:3~ | Ab3:3')
B = ('Db3:1.5 Db3:1 Db3:0.5 | Db3:2 R:0.5 Db3:0.5 | Gb3:1 Gb3:0.5 Gb3:1 Gb3:0.5 | Db3:3 |'
     'Db3:1 Db3:0.5 Db3:1 Db3:0.5 | Ab2:1.5 Ab2:1 Ab2:0.5 | Ab2:1.5 Ab2:1 Ab2:0.5 | Db3:3~ | Db3:3 |'
     'Db3:1.5 Db3:1 Db3:0.5 | Db3:2 R:0.5 Db3:0.5 | Gb3:1 Gb3:0.5 Gb3:1 Gb3:0.5 | Db3:3 |'
     'Db3:1 Db3:0.5 Db3:1 Db3:0.5 | C3:1.5 C3:1 C3:0.5 | C3:1.5 C3:1 C3:0.5 | F3:3~ |'
     'F3:2 R:0.5 F3:0.5 | Eb3:1.5 Ab2:1.5 | C3:1.5 Ab3:1.5 | Db3:1 Db3:0.5 Db3:1 Db3:0.5 |'
     'Db3:1.5 Db3:1 Db3:0.5 | Eb3:1.5 Ab2:1.5 | C3:1.5 Ab3:1.5 | Db3:1 Db3:0.5 Db3:1 Db3:0.5 | Db3:3 |'
     'Bb3:3~ | Bb3:1.5 Bb3:1 Bb3:0.5 | F3:3~ | F3:2 R:0.5 F3:0.5 | Eb3:3~ | Eb3:1 Eb3:0.5 Eb3:1 Eb3:0.5 |'
     'Bb3:3 | Bb3:2 R:0.5 A3:0.5 | Ab3:3 | Gb3:2 R:0.5 Gb3:0.5 | F3:3 | Gb3:1.5 Gb3:1.5 |'
     'Ab3:3 | Ab2:1 Ab2:0.5 Ab2:1 Ab2:0.5 | Db3:3~ | Db3:1.5 F3:1.5 | Ab3:3 | Gb3:1.5 Gb3:1.5 |'
     'F3:3 | Gb3:1.5 Gb3:1.5 | Ab3:3 | Ab3:1.5 Ab3:1 Ab3:0.5 | Db3:3~ | Db3:3')
parts = {voice: [bar.strip() for bar in text.split('|')]
         for voice, text in zip(('soprano', 'alto', 'tenor', 'bass'), (S, A, T, B))}

# Onset patterns used by the words (beats within the 6/8 bar, quarter = 1).
P = {'qe': [0, 1, 1.5, 2.5], 'dq': [0, 1.5, 2.5], 'h': [0], 'he': [0, 2.5], 'dd': [0, 1.5],
     'e': [2.5], 'm': [1.5], 'mm': [1.5, 2.5], '-': [], 'w': [1, 1.5, 2.5]}
SHAPE = ['dq', 'he', 'qe', 'h', 'qe', 'dq', 'dq', 'h', '-', 'dq', 'he', 'qe', 'h', 'qe', 'dq', 'dq', 'h',
         'e', 'dd', 'dd', 'qe', 'dq', 'dd', 'dd', 'qe', 'h', 'h', 'mm', 'h', 'e', 'h', 'w', 'h', 'he',
         'h', 'e', 'h', 'm', 'h', 'w', 'h', 'm', 'h', 'm', 'h', 'm', 'h', 'dq', 'h', '-']
assert len(SHAPE) == 50

words = [
 # stanza 1
 'O Ho- ly | Night! The | stars are bright- ly | shi- | ning, It is the | night of our | dear Sav- iour’s | birth. | |'
 ' Long lay the | world in | sin and er- ror | pin- | ning. Till He ap- | peared and the | soul felt its | worth. |'
 ' A | thrill of | hope the | wea- ry world re- | joi- ces, For | yon- der | breaks a | new and glor- ious | morn. |'
 ' Fall | on your | knees! | Oh, | hear | the an- gel | voi- | ces! O | night | di- |'
 ' vine, | O | night | when Christ was | born; | O | night, | O | Ho- | ly | Night, | O night di- | vine! |',
 # stanza 2
 'Led by the | light of | faith se- rene- ly | beam- | ing, With glow- ing | hearts by His | cra- dle we | stand. | |'
 ' O- ver the | world a | star is sweet- ly | gleam- | ing, Now come the | wise- men from | O- ri- ent | land. |'
 ' The | King of | kings lay | thus in low- ly | man- ger; In | all our | tri- als | born to be our | friend. |'
 ' He | knows our | need, | our | weak- | ness is no | strang- | er! Be- | hold | your |'
 ' King! | Be- | fore | him low- ly | bend! | Be- | hold | your | King! | Be- | fore | Him low- ly | bend! |',
 # stanza 3
 'Tru- ly He | taught us | love for one a- | noth- | er, His law is | love and His | gos- pel is | peace. | |'
 ' Chains He shall | break, the | slave@0 is@1.5 our@2.5 | broth- | er, And in His | name all op- | pres- sion shall | cease. |'
 ' Sweet | hymns of | joy in | grate- ful chor- us | raise we, With | all our | hearts we | praise His ho- ly | name. |'
 ' Christ | is the | Lord! | Oh, | praise | His name for- | ev- | er! His | pow’r | and |'
 ' glo- | ry | ev- | er- more pro- | claim! | His | pow’r | and | glo- | ry | ev- | er- more pro- | claim! |',
]

verses = []
for number, text in enumerate(words, 1):
    bars = [b.split() for b in text.split('|')]
    assert len(bars) == 50, (number, len(bars))
    rows = []
    for index, (shape, syllables) in enumerate(zip(SHAPE, bars), 1):
        beats = P[shape]
        if any('@' in w for w in syllables):  # stanza-specific timing, e.g. 'slave@0'
            beats = [float(w.split('@')[1]) for w in syllables]
            syllables = [w.split('@')[0] for w in syllables]
        assert len(beats) == len(syllables), (number, index, beats, syllables)
        rows.append(' '.join(f'{b:g}:{w}' for b, w in zip(beats, syllables)))
    verses.append({'number': number, 'title': f'Strofa {number}',
                   'lyrics': {voice: fit_lyrics(parts[voice], rows) for voice in parts}})

systems = crop_systems('o-holy-night', PDF, [(5, .09, .29), (7, .30, .50), (5, .52, .71), (5, .74, .93)],
                       page=0, x=(.06, .97))
systems += crop_systems('o-holy-night', PDF, [(6, .05, .23), (8, .27, .47), (7, .50, .70), (7, .72, .93)],
                        page=1, x=(.06, .97), first=23, start_index=4)

song = {
    'id': 'o-holy-night', 'title': 'O Holy Night', 'emoji': '✨',
    'composer': 'the composer; words the authors, tr. the authors', 'arranger': 'an online edition',
    'meter': [6, 8], 'key_fifths': -5, 'tempo': 110,
    'source_pdf': PDF,
    'sources': [{'description': 'Supplied two-page vector PDF (online edition, Sibelius/Opus), D♭ major; all notes and the three printed stanzas.'}],
    'review_notes': [
        'Pitches read from the embedded Opus glyphs (vector_heads.py); rhythms from the page and the flag/rest glyph positions; every syllable matched to the x position of its printed note.',
        'Accidentals persist through the bar as printed: tenor bar 14 B♮3 B♮3 (leading tone to C), alto bar 16 E♮4 throughout (C7♭9).',
        'Bar 34 bass: the printed B𝄫3 (minor iv, G♭ minor) is stored as its sounding pitch A3, since the data format has no double flats.',
        'Bar 45–46: the sopranos divide (A♭5/F5). The data keeps the upper (melody) line; the lower divisi F5–E♭5 is omitted. The printed quadruplet (4 eighths in the time of 6) is encoded as four dotted eighths and the tenor duplet as two dotted eighths, which sound identically.',
        'The three printed stanzas are each sung through all 50 bars. Default tempo quarter = 110 (user choice).',
    ],
    'parts': parts, 'playback': [{'measure': i} for i in range(1, 51)],
    'systems': systems, 'verses': verses,
    'staff_bands': {'soprano': [0, .5], 'alto': [0, .5], 'tenor': [.5, 1], 'bass': [.5, 1]},
    'shared_lyrics': True,
    'compact': {'instructions': 'Tre strofe numerate sulle stesse note; testo comune alle quattro voci.'},
}

save_song(song)
