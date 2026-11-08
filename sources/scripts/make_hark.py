"""Build data/hark-the-herald.json: Hark! the Herald Angels Sing (the composer), a choral anthology
edition (descant and organ part by the arranger). Source: the supplied three-page scan; page 1
holds the SATB hymn (verses 1–2, 20 bars, G major, 4/4). At the user's request all three verses
use this SATB setting; verse 3's words come from page 2 (the descant/organ setting is not used).
Readings: Audiveris draft (omr.py) + raster_heads.py notehead positions, checked bar by bar."""
from song_kit import crop_systems, fit_lyrics, save_song

PDF = 'songs/Hark the Herald Angels Sing.pdf'
S = ['D4:1 G4:1 G4:1.5 F#4:0.5', 'G4:1 B4:1 B4:1 A4:1', 'D5:1 D5:1 D5:1.5 C5:0.5', 'B4:1 A4:1 B4:2',
     'D4:1 G4:1 G4:1.5 F#4:0.5', 'G4:1 B4:1 B4:1 A4:1', 'D5:1 A4:1 A4:1.5 F#4:0.5', 'F#4:1 E4:1 D4:2',
     'D5:1 D5:1 D5:1 G4:1', 'C5:1 B4:1 B4:1 A4:1', 'D5:1 D5:1 D5:1 G4:1', 'C5:1 B4:1 B4:1 A4:1',
     'E5:1 E5:1 E5:1 D5:1', 'C5:1 B4:1 C5:2', 'A4:1 B4:0.5 C5:0.5 D5:1.5 G4:0.5', 'G4:1 A4:1 B4:2',
     'E5:1.5 E5:0.5 E5:1 D5:1', 'C5:1 B4:1 C5:2', 'A4:1 B4:0.5 C5:0.5 D5:1.5 G4:0.5', 'G4:1 A4:1 B4:2']
A = ['D4:1 D4:1 D4:1.5 D4:0.5', 'D4:1 G4:1 G4:1 F#4:1', 'G4:1 F#4:1 E4:1 A4:1', 'G4:1 F#4:1 G4:2',
     'D4:1 D4:1 D4:1.5 C4:0.5', 'B3:1 G4:1 G4:2', 'F#4:1 E4:1 F#4:1.5 D4:0.5', 'D4:1 C#4:1 D4:2',
     'D4:1 D4:1 D4:1 G4:1', 'A4:1 G4:1 G4:1 F#4:1', 'D4:1 D4:1 D4:1 G4:1', 'A4:1 G4:1 G4:1 F#4:1',
     'C5:1 C5:1 C5:1 B4:1', 'A4:1 G#4:1 A4:2', 'F#4:1 F#4:1 G4:1.5 D4:0.5', 'D4:1 F#4:1 G4:2',
     'C5:1.5 C5:0.5 C5:1 B4:1', 'A4:1 G#4:1 A4:2', 'A4:1 B4:0.5 C5:0.5 D5:1.5 G4:0.5', 'G4:1 A4:1 B4:2']
T = ['B3:1 B3:1 B3:1.5 A3:0.5', 'G3:1 D4:1 D4:2', 'D4:1 D4:1 E4:1 E4:1', 'D4:1 D4:1 D4:2',
     'B3:1 B3:1 B3:1.5 A3:0.5', 'G3:1 D4:1 E4:2', 'D4:1 E4:1 A3:1.5 A3:0.5', 'B3:1 G3:1 F#3:2',
     'D4:1 D4:1 D4:1 D4:1', 'D4:1 D4:1 D4:2', 'D4:1 D4:1 D4:1 D4:1', 'D4:1 D4:1 D4:2',
     'E4:1 E4:1 E4:1 F4:1', 'E4:1 D4:1 C4:2', 'D4:1 D4:1 D4:1.5 B3:0.5', 'B3:1 D4:1 D4:2',
     'E4:1.5 E4:0.5 E4:1 D4:1', 'C4:1 B3:1 C4:2', 'A3:1 B3:0.5 C4:0.5 D4:1.5 G3:0.5', 'G3:1 A3:1 B3:2']
B = ['G3:1 G3:1 G3:1.5 D3:0.5', 'B2:1 G2:1 D3:2', 'B2:1 B2:1 C3:1 C3:1', 'D3:1 D3:1 G2:2',
     'G3:1 G3:1 G3:1.5 D3:0.5', 'E3:1 D3:1 C#3:1.5 A2:0.5', 'B2:1 C#3:1 D3:1 F#2:1', 'G2:1 A2:1 D3:2',
     'D4:1 D4:1 D4:1 B3:1', 'F#3:1 G3:1 D3:2', 'D4:1 D4:1 D4:1 B3:1', 'F#3:1 G3:1 D3:2',
     'C3:1 C3:1 C3:1 D3:1', 'E3:1 E3:1 A3:2', 'D4:1 C4:1 B3:1.5 G3:0.5', 'D3:1 D3:1 G3:2',
     'C4:1.5 C4:0.5 C4:1 B3:1', 'A3:1 G#3:1 A3:2', 'A3:1 B3:0.5 C4:0.5 D4:1.5 G3:0.5', 'G3:1 A3:1 B3:2']
parts = {'soprano': S, 'alto': A, 'tenor': T, 'bass': B}

D, Q3, Q4 = [0, 1, 2, 3.5], [0, 1, 2], [0, 1, 2, 3]
ONSETS = [D, Q3, D, Q3, D, Q3, D, Q3, Q4, Q3, Q4, Q3, Q4, Q3, D, Q3, [0, 1.5, 2, 3], Q3, D, Q3]
REFRAIN = ' Hark! the he- rald | an- gels sing, | Glo- ry to the | new- born King.'
words = [
    'Hark! the he- rald | an- gels sing | Glo- ry to the | new- born King; | Peace on earth and | mer- cy mild, |'
    ' God and sin- ners | re- con- ciled: | Joy- ful all ye | na- tions rise, | Join the tri- umph | of the skies, |'
    ' With th’an- gel- ic | host pro- claim, | Christ is born in | Beth- le- hem. |' + REFRAIN,
    'Christ, by high- est | heav’n a- dored, | Christ, the e- ver- | last- ing Lord, | Late in time be- | hold him come, |'
    ' Off- spring of a | vir- gin’s womb: | Veiled in flesh the | God- head see, | Hail th’in- car- nate | De- i- ty! |'
    ' Pleased as man with | man to dwell, | Je- sus, our Em- | ma- nu- el. |' + REFRAIN,
    'Hail the heav’n- born | Prince of Peace! | Hail the Sun of | Right- eous- ness! | Light and life to | all he brings, |'
    ' Ris’n with heal- ing | in his wings; | Mild he lays his | glo- ry by, | Born that man no | more may die, |'
    ' Born to raise the | sons of earth, | Born to give them | se- cond birth. |' + REFRAIN,
]
verses = []
for number, text in enumerate(words, 1):
    bars = [b.split() for b in text.split('|')]
    assert len(bars) == 20
    cues = []
    for m, (beats, syl) in enumerate(zip(ONSETS, bars), 1):
        assert len(beats) == len(syl), (number, m, syl)
        cues.append(' '.join(f'{b:g}:{w}' for b, w in zip(beats, syl)))
    verses.append({'number': number, 'title': f'Strofa {number}',
                   'lyrics': {v: fit_lyrics(parts[v], cues) for v in parts}})

systems = crop_systems('hark-the-herald', PDF, [(4, .14, .31), (4, .31, .48), (4, .48, .64), (4, .64, .80), (4, .80, .98)],
                       x=(.05, .99))

song = {
    'id': 'hark-the-herald', 'title': 'Hark! the Herald Angels Sing', 'emoji': '🎺',
    'composer': 'the composer; words the author', 'arranger': 'the arranger (a choral anthology)',
    'meter': [4, 4], 'key_fifths': 1, 'tempo': 100,
    'source_pdf': PDF,
    'sources': [{'description': 'Supplied three-page scan of the a choral anthology edition (descant and organ part by the arranger): page 1 SATB verses 1–2; page 2 verse 3 words.'}],
    'review_notes': [
        'Notes from an Audiveris draft and raster notehead positions (sources/scripts/raster_heads.py), checked bar by bar against the scan; small parenthesised organ notes in bars 17–18 are not sung and are omitted.',
        'At the user’s request all three verses use the page-1 SATB setting; the printed verse-3 descant with organ (pages 2–3) is not encoded. Verse 3 words from page 2 (“Ris’n” sung as one syllable).',
        'Bars 19–20 are printed “Unison”: every voice sings the tune, tenors and basses an octave lower.',
        'Bar 7 tenor D4–E4 and bar 13 tenor F♮4 (printed natural) were read from enlarged crops; bar 15 bass is printed high (D4 C4 B3 G3).',
        'Suggested tempo quarter = 100.',
    ],
    'parts': parts, 'playback': [{'measure': m} for m in range(1, 21)],
    'sections': [{'at': [17, 0], 'name': 'chorus'}],
    'systems': systems, 'verses': verses,
    'staff_bands': {'soprano': [0, .5], 'alto': [0, .5], 'tenor': [.5, 1], 'bass': [.5, 1]},
    'shared_lyrics': True,
    'compact': {'refrain_measures': [17, 20],
                'instructions': 'Strofe 1–3 sulle righe numerate; il ritornello “Hark! the herald” è comune.'},
}

save_song(song)
