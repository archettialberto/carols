"""Build data/angels-carol.json: Angels' Carol, SATB (divided) with piano or harp. Source: the
supplied eight-page raster scan, F major → G major at bar 71, 2/2 (4/4 from bar 104), 107 bars,
three stanzas set through-composed. Notes: Audiveris draft (omr.py, .omr/out/angels.mxl) checked
and corrected system by system against 200–350 dpi crops; missing or garbled bars read by eye.
Divisi: the upper note goes to the named voice (S1, A1, T1, B1). Sung a cappella: the piano part is
not encoded, and the bars where only the piano plays (1–2, 35–36, 69–70) are left out (DROP below);
everything above is written in printed bar numbers and renumbered at the end."""
from song_kit import crop_systems, fit_lyrics, save_song

PDF = "songs/Angels' Carol.pdf"
R = 'R:4'
MEL1 = ['R:1 C4:0.5 C4:0.5 F4:1 A4:1', 'G4:4~', 'G4:1 A4:0.5 G4:0.5 F4:1 G4:1', 'A4:2 A4:2',
        'R:1 C4:0.5 C4:0.5 F4:1 C5:1', 'Bb4:2 Bb4:2~', 'Bb4:1 A4:0.5 Bb4:0.5 G4:1 D5:1', 'C5:4']



S = ([R, R] + MEL1 + [R] * 8                                                  # 1–18
     + ['R:1 C4:0.5 C4:0.5 F4:1 A4:1', 'G4:4~', 'G4:1 A4:0.5 G4:0.5 F4:1 G4:1', 'A4:2 A4:2',   # 19–22
        'R:1 C4:0.5 C4:0.5 F4:1 C5:1', 'Bb4:2 Bb4:2~', 'Bb4:1 A4:0.5 Bb4:0.5 G4:1 D5:1', 'C5:4~', 'C5:3 R:1',
        'D5:0.5 E5:0.5 F5:2 E5:0.5 D5:0.5', 'E5:1 C5:1 A4:1 F4:1',                           # 28–29
        'Bb4:0.5 C5:0.5 D5:2 C5:0.5 Bb4:0.5', 'C5:1 A4:1 F4:1 D4:1',                         # 30–31
        'R:1 C4:0.5 C4:0.5 F4:1 A4:1', 'G4:1 D4:1 E4:1 G4:1', 'F4:4', R, R,                    # 32–36
        'A4:4', 'Bb4:3 D5:1', 'C5:2 Bb4:1 C5:1', 'A4:3 C5:1', 'F5:3 E5:1', 'D5:3 C5:1',         # 37–42
        'Bb4:3 R:1', 'C5:3 Bb4:1', 'A4:2 R:2', 'R:1 G4:1 Bb4:1 D5:1', 'C5:2 F4:2',             # 43–47
        'D5:3 F5:1', 'E5:3 D5:1', 'C5:3 A4:1', 'Bb4:3 A4:1', 'G4:3 F4:1',                       # 48–52
        'E4:1 C4:0.5 C4:0.5 F4:1 A4:1', 'G4:4~', 'G4:1 A4:0.5 G4:0.5 F4:1 G4:1', 'A4:2 A4:2',   # 53–56
        'R:1 C4:0.5 C4:0.5 F4:1 C5:1', 'Bb4:2 Bb4:2~', 'Bb4:1 A4:0.5 Bb4:0.5 G4:1 D5:1', 'C5:4~', 'C5:2 R:2',
        R, R, 'Bb4:0.5 C5:0.5 D5:2 C5:0.5 Bb4:0.5', 'C5:1 A4:1 F4:1 D4:1',                    # 62–65
        'E4:3 C5:1', 'Bb4:2 Bb4:1 Bb4:1', 'A4:4', R, R,                                         # 66–70
        R, 'R:1 C5:0.5 C5:0.5 E5:1 G5:1', 'F#5:0.5 E5:0.5 D5:0.5 C5:0.5 B4:1 A4:1', 'B4:2 B4:2',  # 71–74
        'R:1 D4:0.5 D4:0.5 G4:1 D5:1', 'C5:2 C5:2~', 'C5:1 B4:0.5 C5:0.5 A4:1 E5:1', 'D5:4',     # 75–78
        'R:1 G4:0.5 G4:0.5 D5:1 G5:1', 'F5:4~', 'F5:1 G5:0.5 F5:0.5 E5:1 D5:1', 'E5:2 E5:2~',    # 79–82
        'E5:1 F#5:0.5 E5:0.5 D5:1 C5:1', 'D5:3 G4:1', 'C5:1 B4:1 A4:1 G4:1', 'A4:4',            # 83–86
        R, 'R:1 C5:0.5 C5:0.5 E5:1 G5:1', 'F#5:0.5 E5:0.5 D5:0.5 C5:0.5 B4:1 A4:1', 'B4:2 B4:2',  # 87–90
        'R:1 D4:0.5 D4:0.5 G4:1 D5:1', 'C5:2 C5:2~', 'C5:1 B4:0.5 C5:0.5 A4:1 E5:1', 'D5:4~',    # 91–94
        'D5:3 R:1', 'E5:0.5 F#5:0.5 G5:2 F#5:0.5 E5:0.5', 'F#5:1 D5:1 B4:1 G4:1',                # 95–97
        'C5:0.5 D5:0.5 E5:2 D5:0.5 C5:0.5', 'D5:1 B4:1 G4:1 E4:1',                              # 98–99
        'R:1 D4:0.5 D4:0.5 G4:1 B4:1', 'A4:1 E4:1 F#4:1 A4:1', 'G4:4~', 'G4:4',                 # 100–103
        'R:1 D4:0.5 D4:0.5 G4:1 D5:1', 'C5:1 E5:1 D5:1 F#5:1', 'G5:4~', 'G5:2 R:2'])            # 104–107
A = ([R, R] + MEL1 + [R] * 8 + [R] * 9                                         # 1–27
     + ['Bb4:0.5 C5:0.5 D5:2 C5:0.5 Bb4:0.5', 'C5:1 A4:1 F4:1 F4:1',
        'D4:0.5 E4:0.5 F4:2 E4:0.5 E4:0.5', 'E4:1 C4:1 D4:1 D4:1',
        'R:1 C4:0.5 C4:0.5 F4:1 E4:1', 'D4:1 D4:1 C4:1 C4:1', 'C4:4', R, R,
        'C4:4', 'D4:3 F4:1', 'E4:2 D4:1 E4:1', 'C4:3 F4:1', 'A4:3 C5:1', 'F4:3 A4:1',          # 37–42
        'G4:3 R:1', 'E4:3 G4:1', 'F4:2 R:2', 'R:1 Eb4:1 G4:1 Bb4:1', 'A4:2 F4:2',               # 43–47
        'F4:3 A4:1', 'G4:4~', 'G4:1 A4:0.5 G4:0.5 F4:1 E4:1', 'D4:4', 'Eb4:2 Bb3:2',           # 48–52
        'C4:1 C4:0.5 C4:0.5 F4:1 A4:1', 'G4:2 F4:2', 'E4:1 F4:0.5 E4:0.5 D4:1 E4:1', 'F4:2 F4:2',  # 53–56
        'R:1 C4:0.5 C4:0.5 F4:1 E4:1', 'D4:2 D4:2~', 'D4:1 C4:0.5 D4:0.5 E4:1 Bb4:1', 'A4:4~', 'A4:2 R:2',
        R, R, 'D4:0.5 E4:0.5 F4:2 E4:0.5 D4:0.5', 'E4:1 C4:1 D4:1 Bb3:1',
        'C4:3 C4:1', 'D4:2 C4:1 C4:1', 'C4:4', R, R,                                           # 66–70
        'R:1 D4:0.5 D4:0.5 G4:1 B4:1', 'A4:4~', 'A4:1 B4:0.5 A4:0.5 G4:1 A4:1', 'G4:2 G4:2',   # 71–74
        'R:1 D4:0.5 D4:0.5 D4:1 G4:1', 'G4:2 G4:2~', 'G4:1 G4:0.5 G4:0.5 A4:1 A4:1', 'G4:4',   # 75–78
        'R:1 G4:0.5 G4:0.5 G4:1 G4:1', 'A4:4', 'B4:4', 'G4:2 C5:1 B4:1',                      # 79–82
        'A4:2 F#4:2~', 'F#4:1 B4:0.5 A4:0.5 G4:1 F#4:1', 'E4:1 D4:1 C4:1 B3:1', 'C4:4',          # 83–86
        'R:1 D4:0.5 D4:0.5 G4:1 B4:1', 'A4:4~', 'A4:1 B4:0.5 A4:0.5 G4:1 A4:1', 'G4:2 G4:2',   # 87–90
        R, 'R:1 E4:0.5 E4:0.5 G4:1 B4:1', 'A4:2 A4:2~', 'A4:1 G4:0.5 A4:0.5 F#4:1 B4:1',        # 91–94
        'A4:2 G4:1 R:1', 'G4:1.5 G4:0.5 C5:1 G4:0.5 G4:0.5', 'B4:1 F#4:1 G4:0.5 F#4:0.5 E4:1',  # 95–97
        'E4:0.5 F#4:0.5 G4:2 F#4:0.5 E4:0.5', 'F#4:1 F#4:1 E4:0.5 D4:0.5 C4:1',                 # 98–99
        'R:1 D4:0.5 D4:0.5 G4:1 F#4:1', 'E4:1 E4:1 D4:1 C4:1', 'B3:4', 'Bb3:4',                 # 100–103
        'R:1 D4:0.5 D4:0.5 G4:1 B4:1', 'A4:1 E4:1 F#4:1 A4:1', 'G4:4~', 'G4:2 R:2'])            # 104–107
T = ([R] * 10 + ['R:1 F3:0.5 F3:0.5 C4:1 F4:1', 'Eb4:4~', 'Eb4:1 F4:0.5 Eb4:0.5 D4:1 C4:1', 'D4:2 D4:2~',
                 'D4:1 E4:0.5 D4:0.5 C4:1 Bb3:1', 'C4:3 F3:1', 'Bb3:1 A3:1 G3:1 F3:1', 'G3:4']   # 1–18
     + ['R:1 C3:0.5 C3:0.5 F3:1 A3:1', 'G3:4~', 'G3:1 A3:0.5 G3:0.5 F3:1 G3:1', 'A3:2 A3:2',
        'R:1 C4:0.5 C4:0.5 A3:1 F3:1', 'G3:2 G3:2~', 'G3:1 F3:0.5 G3:0.5 E3:1 G3:1', 'C4:4~', 'C4:3 R:1',
        'F4:0.5 E4:0.5 D4:0.5 C4:0.5 Bb3:0.5 C4:0.5 D4:1', 'C4:0.5 D4:0.5 E4:1 F4:0.5 E4:0.5 D4:0.5 C4:0.5',
        'Bb3:1.5 C4:0.5 D4:1 E4:0.5 D4:0.5', 'C4:1 E4:1 D4:0.5 C4:0.5 Bb3:1',                  # 30–31
        'R:1 C4:0.5 C4:0.5 A3:1 F3:1', 'Bb3:1 G3:1 C4:1 Bb3:1', 'A3:4', R, R,                   # 32–36
        'R:1 C3:0.5 C3:0.5 F3:1 A3:1', 'G3:4~', 'G3:1 A3:0.5 G3:0.5 F3:1 G3:1', 'A3:2 A3:2',
        'R:1 C3:0.5 C3:0.5 F3:1 C4:1', 'Bb3:2 Bb3:2~', 'Bb3:1 A3:0.5 Bb3:0.5 G3:1 D4:1', 'C4:4~',  # 41–44
        'C4:1 F3:0.5 F3:0.5 C4:1 F4:1', 'Eb4:4~', 'Eb4:1 F4:0.5 Eb4:0.5 D4:1 C4:1', 'D4:2 D4:2',  # 45–48
        'R:1 E4:0.5 D4:0.5 C4:1 Bb3:1', 'C4:3 F3:1', 'Bb3:1 A3:1 G3:1 F3:1', 'A3:4', 'G3:1 R:3',  # 49–53
        'Bb3:4~', 'Bb3:4', 'A3:4~', 'A3:4', 'Bb3:4~', 'Bb3:4', 'A3:2 C4:2', 'C4:2 R:2',        # 54–61
        'D4:0.5 E4:0.5 F4:2 E4:0.5 D4:0.5', 'E4:1 C4:1 A3:1 F3:1', R, R,                        # 62–65
        'R:1 C3:0.5 C3:0.5 F3:1 A3:1', 'G3:1 D3:1 E3:1 G3:1', 'G3:4', R, R,                     # 66–70
        'R:1 D3:0.5 D3:0.5 G3:1 B3:1', 'A3:4~', 'A3:1 B3:0.5 A3:0.5 G3:1 A3:1', 'B3:2 B3:2',   # 71–74
        'R:1 D4:0.5 D4:0.5 B3:1 G3:1', 'C4:2 C4:2~', 'C4:1 C4:0.5 C4:0.5 C4:1 C4:1', 'D4:4',     # 75–78
        R, 'R:1 A3:0.5 A3:0.5 C4:1 E4:1', 'B3:4~', 'B3:1 C4:0.5 B3:0.5 A3:1 G3:1',              # 79–82
        'A3:2 A3:2', 'A3:2 B3:2', 'C4:3 C4:1', 'A3:4',                                          # 83–86
        'R:1 D3:0.5 D3:0.5 G3:1 B3:1', 'A3:4~', 'A3:1 B3:0.5 A3:0.5 G3:1 A3:1', 'B3:2 B3:2',   # 87–90
        'R:1 D3:0.5 D3:0.5 G3:1 D4:1', 'C4:2 C4:2~', 'C4:1 B3:0.5 C4:0.5 A3:1 E4:1', 'D4:4',     # 91–94
        'F4:3 R:1', 'E4:1.5 D4:0.5 C4:0.5 D4:0.5 E4:1', 'D4:0.5 E4:0.5 F#4:0.5 D4:0.5 E4:1 B3:1',  # 95–97
        'C4:1.5 D4:0.5 E4:0.5 C4:0.5 D4:0.5 E4:0.5', 'D4:1 D4:1 C4:1 G3:1',                     # 98–99
        'R:1 D4:0.5 D4:0.5 B3:1 G3:1', 'C4:1 A3:1 D4:1 D4:1', 'B3:4', 'Bb3:4',                  # 100–103
        'B3:4', 'C4:4', 'B3:4~', 'B3:2 R:2'])                                                   # 104–107
B = ([R] * 27
     + ['Bb3:1.5 A3:0.5 G3:2', 'A3:1 A3:1 D3:1 D3:1', 'G3:1.5 A3:0.5 Bb3:1 C4:0.5 C4:0.5', 'A3:1 A3:1 Bb3:1 Bb2:1',
        'C3:3 C3:1', 'C3:1 C3:1 C3:1 C3:1', 'C3:4', R, R,                                       # 32–36
        'R:1 C3:0.5 C3:0.5 F3:1 A3:1', 'G3:4~', 'G3:1 A3:0.5 G3:0.5 F3:1 G3:1', 'A3:2 A3:2',
        'R:1 C3:0.5 C3:0.5 F3:1 C4:1', 'Bb3:2 Bb3:2~', 'Bb3:1 A3:0.5 Bb3:0.5 G3:1 D4:1', 'C4:4~',
        'C4:1 F3:0.5 F3:0.5 A3:1 F3:1', 'G3:4', 'A3:1 A3:0.5 G3:0.5 F3:1 Eb3:1', 'F3:2 F3:2',   # 45–48
        'R:1 G3:0.5 F3:0.5 E3:1 G3:1', 'A3:3 F3:1', 'Bb3:1 A3:1 G3:1 F3:1', 'G3:4~', 'G3:1 R:3',  # 49–53
        'G3:4', 'C3:4', 'C3:4', 'F3:4', 'D3:4', 'F3:2 G3:2', 'A3:2 E3:2', 'A2:2 R:2',           # 54–61
        'Bb3:0.5 C4:0.5 D4:2 C4:0.5 Bb3:0.5', 'C4:1 A3:1 F3:1 D3:1', R, R,                      # 62–65
        'R:1 C3:0.5 C3:0.5 F3:1 A3:1', 'G3:1 D3:1 E3:1 G3:1', 'F3:4', R, R,                     # 66–70
        'R:1 D3:0.5 D3:0.5 G3:1 B3:1', 'G3:4', 'A3:1 B3:0.5 A3:0.5 G3:1 A3:1', 'B3:2 B3:2',     # 71–74
        'R:1 D3:0.5 D3:0.5 E3:1 E3:1', 'A3:2 A3:2~', 'A3:1 G3:0.5 A3:0.5 F#3:1 A3:1', 'B3:4',   # 75–78
        'R:1 G3:0.5 G3:0.5 B3:1 G3:1', 'B2:4', 'G3:3 G3:0.5 G3:0.5', 'C3:4', 'C3:4',            # 79–83
        'B2:2 E3:2', 'A2:3 A3:1', 'F3:4',                                                       # 84–86
        'R:1 D3:0.5 D3:0.5 G3:1 B3:1', 'G3:4', 'A3:1 B3:0.5 A3:0.5 G3:1 A3:1', 'B3:2 B3:2',     # 87–90
        R, 'R:1 B3:0.5 B3:0.5 A3:1 G3:1', 'F#3:2 F#3:2', 'B3:3 D4:1',                           # 91–94
        'C4:2 B3:1 R:1', 'C4:1.5 B3:0.5 A3:0.5 B3:0.5 C4:1', 'B3:0.5 C4:0.5 D4:0.5 B3:0.5 E4:1 E3:1',  # 95–97
        'A3:1.5 B3:0.5 C4:0.5 A3:0.5 B3:0.5 C4:0.5', 'B3:1 B2:1 C3:1 C3:1',                     # 98–99
        'D3:3 D3:1', 'D3:1 D3:1 D3:1 D3:1', 'G3:4~', 'G3:4',                                    # 100–103
        'D3:4~', 'D3:4', 'D3:4~', 'D3:2 R:2'])                                                  # 104–107
parts = {'soprano': S, 'alto': A, 'tenor': T, 'bass': B}
assert all(len(p) == 107 for p in parts.values()), {v: len(p) for v, p in parts.items()}

# ---- words: per voice, {first bar: 'syllables | per | bar'}; onsets come from the notes unless given.
V1A = 'Have you heard the | sound | of the an- gel | voi- ces | Ring- ing out so | sweet- ly, | ring- ing out so | clear?'
V1T = 'Have you seen the | star | shi- ning out so | bright- ly | As a sign from | God that | Christ the Lord is | here?'
NEWS = 'Have you heard the | news | that they bring from | hea- ven | To the hum- ble | shep- herds | who have wait- ed | long?'
GLORIA_SA = 'Glo- ri- a in ex- | cel- sis De- o, | Glo- ri- a in ex- | cel- sis De- o!'
HEAR = 'Hear the an- gels | sing their joy- ful | song.'
V2 = 'He is come in | peace | in the win- ter’s | still- ness, | Like a gen- tle | snow- fall | in the gen- tle | night;'
JOY = 'He is come in | joy | like the sun at | morn- ing | Fill- ing all the | world with | ra- diance and with | light.'
LOVE = 'He is come in | love | as the child of | Ma- ry; | In a sim- ple | sta- ble | we have seen his | birth:'
LIGHT = 'He will bring new | light | to a world in | dark- ness, | Like a bright star | shi- ning | in the skies a- | bove;'
REJOICE = 'Let the earth re- | joice | at the Sa- viour’s | com- ing;'
CHRIST = 'Hear the an- gels | sing- ing ‘Christ is | born’,'
WORDS = {
    'soprano': {3: V1A, 19: NEWS, 28: GLORIA_SA, 32: HEAR, 53: LOVE,
                64: 'Glo- ri- a in ex- | cel- sis De- o! | Hear them | sing ‘Peace on | earth’.',
                72: 'He will bring new | light to a world in | dark- ness, | Like a bright star | shi- ning | in the skies a- | bove;',
                79: 'He will bring new | hope | to the wait- ing | na- tions | When he comes to | reign in | pu- ri- ty and | love.',
                88: 'Let the earth re- | joice at the Sa- viour’s | com- ing; | Let the hea- vens | an- swer | with the joy- ful | morn:',
                96: GLORIA_SA + ' | ' + CHRIST + ' | | ' + CHRIST.replace('born’,', 'born’.')},
    'alto': {3: V1A, 28: GLORIA_SA, 32: HEAR, 53: LOVE,
             64: 'Glo- ri- a in ex- | cel- sis De- o! | Hear them | sing ‘Peace on | earth’.',
             71: LIGHT, 79: 'He will bring new | hope | | to the | na- tions | When he comes in | pu- ri- ty and | love.',
             87: REJOICE + ' | | Let the hea- vens | an- swer | with the joy- ful | morn:',
             96: GLORIA_SA + ' | ' + CHRIST + ' | | ' + CHRIST.replace('born’,', 'born’.')},
    'tenor': {11: V1T, 19: NEWS, 28: 'Glo- ri- a | in ex- cel- sis, | Glo- ri- a in ex- | cel- sis De- o!', 32: HEAR,
              37: V2, 45: JOY, 54: 'Hum | | | | | | | Hum', 62: 'Glo- ri- a in ex- | cel- sis De- o,',
              66: 'Hear the an- gels | sing- ing ‘Peace on | earth’.', 71: LIGHT,
              80: 'He will bring new | hope | to the wait- ing | na- tions | When he | comes in | love.',
              87: REJOICE + ' | Let the hea- vens | an- swer | with the joy- ful | morn:',
              96: 'Glo- ri- a | in ex- cel- sis, | Glo- ri- a | in ex- cel- sis! | ' + CHRIST + ' | | Hum'},
    'bass': {28: 'Glo- ri- a | in ex- cel- sis, | Glo- ri- a in ex- | cel- sis De- o!', 32: 'Hear them | sing their joy- ful | song.',
             37: V2, 45: JOY, 54: 'Hum | | | | | | | Hum', 62: 'Glo- ri- a in ex- | cel- sis De- o,',
             66: 'Hear the an- gels | sing- ing ‘Peace on | earth’.', 71: LIGHT,
             79: 'He will bring new | hope | to the | na- | tions | When he | comes in | love.',
             87: REJOICE + ' | | Let the hea- vens | an- swer | with the | morn:',
             96: 'Glo- ri- a | in ex- cel- sis, | Glo- ri- a | in ex- cel- sis! | Hear them | sing- ing ‘Christ is | born’, | | Hum'},
}
# Explicit onsets where one syllable spans several notes: voice → {bar: [beats]}.
ONSETS = {
    'soprano': {53: [1, 1.5, 2, 3], 72: [1, 1.5, 2, 3], 73: [0, 1, 1.5, 2, 3], 81: [1, 1.5, 2, 3], 83: [1, 1.5, 2, 3], 84: [0, 3],
                88: [1, 1.5, 2, 3], 89: [0, 1, 1.5, 2, 3], 93: [1, 1.5, 2, 3]},
    'alto': {55: [1, 1.5, 2, 3], 53: [1, 1.5, 2, 3], 59: [1, 1.5, 2, 3], 82: [2, 3], 84: [1, 1.5, 2, 3],
             94: [1, 1.5, 2, 3], 97: [0, 1, 2, 3], 99: [0, 1, 2, 3]},
    'tenor': {28: [0, 2, 2.5], 29: [0, 1, 2, 3], 30: [0, 1.5, 2, 3, 3.5], 31: [0, 1, 2, 3], 45: [1, 1.5, 2, 3],
              47: [1, 1.5, 2, 3], 96: [0, 1.5, 2], 97: [0, 1, 2, 3], 98: [0, 1.5, 2], 99: [0, 1, 2, 3]},
    'bass': {28: [0, 1.5, 2], 29: [0, 1, 2, 3], 30: [0, 1.5, 2, 3, 3.5], 45: [1, 1.5, 2, 3], 47: [1, 1.5, 2, 3],
             73: [1, 1.5, 2, 3], 81: [3, 3.5], 89: [1, 1.5, 2, 3], 96: [0, 1.5, 2], 97: [0, 1, 2, 3], 98: [0, 1.5, 2], 99: [0, 1, 2, 3]},
}

# Vocalise “Ah” at the start of each slurred phrase (sopranos and altos, bars 37–50).
AH = {v: {37: '0:Ah', 40: '3:Ah', 44: '0:Ah', 46: '1:Ah', 47: '2:Ah', 50: '3:Ah' if v == 'soprano' else '1:Ah'}
      for v in ('soprano', 'alto')}


def starts(bar, tied=False):
    """Beats where the bar's notes are sung; `tied` = the previous bar ends with a tie into this one."""
    beat, out = 0.0, []
    for token in bar.split():
        pitch, dur = token.split(':')
        if pitch != 'R' and not tied:
            out.append(beat)
        tied = dur.endswith('~'); beat += float(dur.rstrip('~'))
    return out


lyrics = {}
for voice, blocks in WORDS.items():
    rows = [''] * 107
    for first, text in blocks.items():
        for offset, chunk in enumerate(text.split('|')):
            syl = chunk.split()
            if not syl:
                continue
            m = first + offset
            beats = ONSETS[voice].get(m) or starts(parts[voice][m - 1], m > 1 and parts[voice][m - 2].endswith('~'))
            beats = beats[:len(syl)]
            assert len(beats) == len(syl), (voice, m, parts[voice][m - 1], syl)
            rows[m - 1] = ' '.join(f'{b:g}:{w}' for b, w in zip(beats, syl))
    for m, cue in AH.get(voice, {}).items():
        rows[m - 1] = cue
    lyrics[voice] = fit_lyrics(parts[voice], rows)


LAYOUT = [(0, [(4, .14, .33), (4, .33, .51), (4, .51, .69), (4, .69, .87)]),
          (1, [(4, .05, .36), (4, .36, .68), (4, .68, .99)]),
          (2, [(4, .05, .36), (5, .36, .62), (5, .62, .93)]),
          (3, [(4, .05, .33), (4, .33, .62), (5, .62, .93)]),
          (4, [(5, .05, .33), (4, .33, .62), (5, .62, .93)]),
          (5, [(4, .06, .34), (4, .34, .63), (4, .63, .95)]),
          (6, [(4, .06, .34), (4, .34, .63), (4, .63, .95)]),
          (7, [(4, .06, .34), (5, .34, .63), (5, .63, .95)])]
systems = []
first = 1
for page, rows in LAYOUT:
    systems += crop_systems('angels-carol', PDF, rows, page=page, x=(.05, .98), first=first, start_index=len(systems))
    first += sum(r[0] for r in rows)
assert first == 108, first

# ---- a cappella: leave out the piano-only bars and renumber (printed bar → data bar).
DROP = {1, 2, 35, 36, 69, 70}
assert all(all(t.startswith('R:') for t in parts[v][m - 1].split()) for v in parts for m in DROP)
KEEP = [m for m in range(1, 108) if m not in DROP]
new = {m: i for i, m in enumerate(KEEP, 1)}
parts = {v: [p[m - 1] for m in KEEP] for v, p in parts.items()}
lyrics = {v: [rows[m - 1] for m in KEEP] for v, rows in lyrics.items()}
for system in systems:
    printed = range(system['first_measure'], system['first_measure'] + len(system['barlines']) - 1)
    count = sum(m in new for m in printed)
    system['first_measure'] = next(new[m] for m in printed if m in new)
    system['barlines'] = [round(i / count, 5) for i in range(count + 1)]

song = {
    'id': 'angels-carol', 'title': 'Angels’ Carol', 'emoji': '😇',
    'source_pdf': PDF,
    'meter': [2, 2], 'key_fifths': -1, 'measure_keys': {str(new[71]): 1}, 'tempo': 138,
    'review_notes': [
        'Notes from an Audiveris draft checked and corrected system by system against enlarged crops of the scan; the alto moves B3 → B♭3 at 102–103 with the tenor; bars the draft missed (e.g. 54–61, 72, 78, 80–81, 94–95, 102–107) were read by eye. Inner divisi notes are the least certain.',
        'Divisi: each part sings the upper note of its own divisi (sopranos in thirds at 96–99, basses in octaves at 34, 56, 58, 106).',
        'Bars 3–10 sopranos and altos in unison; 11–18 tenors alone; 19–20 sopranos and tenors in octaves. Basses rest until bar 28.',
        'Sung a cappella: the piano/harp part is not encoded and its solo bars (printed 1–2, 35–36, 69–70) are left out, so data bars are printed bars − 2 from bar 3, − 4 from 37 and − 6 from 71. Bar numbers in these notes are the printed ones.',
        'Bars 104–107 are printed in 4/4 (“Tranquil”, quarter = 92) with a rallentando; playback keeps the opening pulse. Suggested tempo half = 69 (quarter = 138).',
    ],
    'parts': parts, 'playback': [{'measure': m} for m in range(1, len(KEEP) + 1)],
    'sections': [{'at': [new[m], 0], 'name': name} for m, name in
                 ((3, 'verse'), (28, 'chorus'), (37, 'verse'), (62, 'chorus'), (71, 'verse'), (96, 'chorus'), (104, 'coda'))],
    'systems': systems,
    'verses': [{'number': 1, 'title': 'Brano intero', 'lyrics': lyrics}],
    'staff_bands': {'soprano': [0, .25], 'alto': [0, .25], 'tenor': [.25, .5], 'bass': [.25, .5]},
    'compact': {'instructions': f'Brano in forma continua: tre strofe con Gloria; da battuta {new[71]} in sol maggiore.'},
}

save_song(song)
