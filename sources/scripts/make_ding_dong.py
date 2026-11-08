"""Build data/ding-dong.json: Ding Dong! Merrily on High, arr. the arranger.
Source: the supplied vector PDF (Sibelius export, songs/Ding Dong.pdf, 2 pages, 24 measures).
Pitches from vector_heads.py (--font Opus --dot 2122 --key B,E --clefs T,T,T8,B); rhythms read
from the page; syllables matched to the nearest printed note. The PDF prints stanza 1 only;
stanzas 2–3 are the author public-domain text as given by a public-domain hymnal."""
from song_kit import crop_systems, save_song

verse = {  # measures 1–8: identical rhythm in every part (homophonic)
 'soprano': ['Bb4:1 Bb4:1 C5:0.5 Bb4:0.5 A4:0.5 G4:0.5', 'F4:3 F4:1', 'G4:1 Bb4:1 Bb4:1 A4:1', 'Bb4:2 Bb4:2'],
 'alto':    ['F4:1 F4:1 G4:0.5 G4:0.5 Eb4:0.5 Eb4:0.5', 'C4:3 F4:1', 'F4:1 Eb4:1 C4:1 F4:1', 'F4:2 F4:2'],
 'tenor':   ['D4:1 Bb3:1 G3:0.5 G3:0.5 C4:0.5 Bb3:0.5', 'A3:3 Bb3:1', 'Bb3:1 Bb3:1 C4:1 C4:1', 'D4:2 D4:2'],
 'bass':    ['Bb2:1 D3:1 Eb3:0.5 Eb3:0.5 C3:0.5 C3:0.5', 'F3:3 D3:1', 'Eb3:1 G3:1 F3:1 F3:1', 'Bb2:2 Bb2:2'],
}
gloria = {  # measures 9–16, printed again as 17–24
 'soprano': ['F5:1.5 Eb5:0.5 D5:0.5 Eb5:0.5 F5:0.5 D5:0.5', 'Eb5:1.5 D5:0.5 C5:0.5 D5:0.5 Eb5:0.5 C5:0.5',
             'D5:1.5 C5:0.5 Bb4:0.5 C5:0.5 D5:0.5 Bb4:0.5', 'C5:1.5 Bb4:0.5 A4:0.5 Bb4:0.5 C5:0.5 A4:0.5',
             'Bb4:1.5 A4:0.5 G4:0.5 A4:0.5 Bb4:0.5 G4:0.5', 'A4:1.5 G4:0.5 F4:1 F4:1'],
 'alto':    ['R:1 F4:2 Bb4:1', 'Bb4:0.5 A4:0.5 G4:0.5 F4:0.5 G4:0.5 F4:0.5 Eb4:1', 'R:1 F4:0.5 Eb4:0.5 D4:1 G4:1',
             'G4:0.5 F4:0.5 Eb4:0.5 D4:0.5 Eb4:0.5 D4:0.5 C4:1', 'R:1 D4:0.5 C4:0.5 Bb3:1 Eb4:1',
             'C4:0.5 D4:0.5 Eb4:0.5 D4:0.5 C4:1 F4:1'],
 'tenor':   ['R:1 C4:1 D4:1 Bb3:1', 'C4:1 Bb3:2 C4:1', 'R:1 A3:1 Bb3:1 G3:1', 'A3:1 G3:2 A3:1', 'R:1 F3:1 G3:2',
             'C4:1 Bb3:1 C4:1 D4:1'],
 'bass':    ['R:1 A3:1 Bb3:1 D3:1', 'C3:1 D3:1 Eb3:0.5 D3:0.5 C3:1', 'R:1 F3:1 G3:1 Bb2:1', 'A2:1 Bb2:1 C3:0.5 Bb2:0.5 A2:1',
             'R:1 D3:1 Eb3:1 G3:1', 'F3:1 G3:1 A3:1 Bb3:1'],
}
# Gloria measures 15–16 repeat the music of measures 3–4.
parts = {v: verse[v] * 2 + (gloria[v] + verse[v][2:]) * 2 for v in verse}

lines = [  # (measures 1–4, measures 5–8) per stanza; one syllable per printed note
 (['Ding dong mer- ri- ly on', 'high, In', 'heav’n the bells are', 'ring- ing:'],
  ['Ding dong! ve- ri- ly the', 'sky Is', 'riv’n with an- gel', 'sing- ing.']),
 (['E’en so here be- low, be-', 'low, Let', 'stee- ple bells be', 'swun- gen,'],
  ['And i- o, i- o, i-', 'o, By', 'priest and peo- ple', 'sun- gen.']),
 (['Pray ye du- ti- ful- ly', 'prime Your', 'ma- tin chime, ye', 'ring- ers;'],
  ['May ye beau- ti- ful- ly', 'rhyme Your', 'eve- time song, ye', 'sing- ers.']),
]
ONSETS = [[0, 1, 2, 2.5, 3, 3.5], [0, 3], [0, 1, 2, 3], [0, 2]]
first_glo = {'soprano': 0, 'alto': 1, 'tenor': 1, 'bass': 1}     # lower parts enter after a rest
ria = {'soprano': 1.5, 'alto': 1.5, 'tenor': 1, 'bass': 1}       # where "ri-" falls in measure 14/22

def cue(onsets, text):
    words = text.split(); assert len(words) == len(onsets), text
    return ' '.join(f'{b:g}:{w}' for b, w in zip(onsets, words))

verses = []
for number, (first_half, second_half) in enumerate(lines, 1):
    stanza = [cue(o, t) for o, t in zip(ONSETS * 2, first_half + second_half)]
    lyrics = {}
    for voice in verse:
        refrain = [f'{first_glo[voice]}:Glo-', '', '', '', '', f'{ria[voice]:g}:ri- 2:a, 3:Ho-',
                   '0:san- 1:na 2:in 3:ex-', '0:cel- 2:sis!']
        lyrics[voice] = stanza + refrain * 2
    verses.append(dict(number=number, title=f'Strofa {number}', lyrics=lyrics))

systems = crop_systems('ding-dong', 'songs/Ding Dong.pdf', [(4, .09, .37), (4, .38, .67), (4, .68, .97)], page=0, x=(.08, .98))
systems += crop_systems('ding-dong', 'songs/Ding Dong.pdf', [(5, .07, .35), (3, .36, .65), (4, .66, .95)], page=1,
                        x=(.08, .98), first=13, start_index=3)

song = dict(id='ding-dong', title='Ding Dong! Merrily on High', emoji='🔔',
  composer='Tune: Branle de l’Official (1589); words the author', arranger='the arranger',
  meter=[2, 2], key_fifths=-2, tempo=140, source_pdf='songs/Ding Dong.pdf',
  review_notes=['Pitches read from the exact notehead positions of the supplied vector PDF; rhythms read from the page and syllables matched to the nearest printed note in each part.',
    'Measures 1–8 are homophonic; in the Gloria the lower parts enter after a quarter rest and “ri-a” falls on beat 2½ (S/A) or beat 2 (T/B), as printed.',
    'Stanzas 2–3 are not in the supplied score: their words come from a public-domain hymnal and are fitted to the same notes as stanza 1 (seven syllables per line). the author 1924 wording reads “Pray you … May you … rime”; the a public-domain hymnal text has “ye … rhyme”. The refrain keeps the printed spelling “Hosanna”.',
    'Every stanza is sung through all 24 printed measures (verse, then the Gloria twice). Printed tempo quarter = 140.'],
  review_notes_it=['Altezze esatte dal PDF vettoriale fornito; ritmi letti dalla pagina e sillabe abbinate alla nota stampata più vicina.',
    'Strofe 2–3 assenti nella partitura: testo di the author da a public-domain hymnal, adattato alle stesse note della strofa 1.'],
  parts=parts, playback=[{'measure': i + 1} for i in range(24)], systems=systems, verses=verses,
  sections=[{'at': [9, 0], 'name': 'chorus'}],
  staff_bands={'soprano': [0, .25], 'alto': [.25, .5], 'tenor': [.5, .75], 'bass': [.75, 1]}, shared_lyrics=True,
  compact=dict(refrain_measures=[9, 24], voice_lyrics={'alto': [9, 24], 'tenor': [9, 24], 'bass': [9, 24]},
    instructions='Strofe 1–3 sulle righe numerate, poi il Gloria due volte.'))
save_song(song)
