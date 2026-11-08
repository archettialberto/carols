"""Build data/angels-carol.json: Angels' Carol, SATB (divided) with piano or harp. Source: the
supplied eight-page raster scan, F major → G major at bar 71, 2/2 (4/4 from bar 104), 107 bars,
three stanzas set through-composed. Notes: Audiveris draft (omr.py, .omr/out/angels.mxl) checked
and corrected system by system against 200–350 dpi crops; missing or garbled bars read by eye.
Divisi: the upper note goes to the named voice (S1, A1, T1, B1). The piano part becomes a simplified
organ: the bass and the chord of each half bar (see make_organ below)."""
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


def starts(bar):
    beat, out, tied = 0.0, [], False
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
            beats = ONSETS[voice].get(m) or starts(parts[voice][m - 1])
            beats = beats[:len(syl)]
            assert len(beats) == len(syl), (voice, m, parts[voice][m - 1], syl)
            rows[m - 1] = ' '.join(f'{b:g}:{w}' for b, w in zip(beats, syl))
    for m, cue in AH.get(voice, {}).items():
        rows[m - 1] = cue
    lyrics[voice] = fit_lyrics(parts[voice], rows)


# ---- organ: one chord per half bar read from the piano part (root in the pedal, three chord
# tones close-voiced from G3). “X Y” = first half X, second half Y.
CHORDS = (
          'F F F Gm C7 F F Bb Gm C '  # 1–10
          'F Eb F7 Bb C7 C|F Gm|Gm7 Eb C|F Gm '  # 11–20
          'C7 F F|Dm Gm C7 Am Cm7|F Bb|Gm Am|Dm Gm7|C7 '  # 21–30
          'Am|Bb F Gm7|C7 F F F F Gm C|Bb F '  # 31–40
          'F Bb|F Gm C|C7 F Cm7|Gm F7 Dm C7 C|F '  # 41–50
          'Gm Eb C|F Gm C7 F F Gm Bb|C7 Am '  # 51–60
          'Am|F7 Bb|Gm Am|Dm Gm|C Am|Bb F Gm7|C7 F Am D7 '  # 61–70
          'D|G Am7 D7|G G G|Em7 Am7 D7 G G Bm7b5 '  # 71–80
          'G7 C|Am7 D7 Bm|Em Am7 F D|G Am7 D7|G G '  # 81–90
          'G Am7|Em D7 G F|G C|Am D|Em Am|D7 G|C G '  # 91–100
          'Am|D7 Em Eb G Am7|D7 G G'  # 101–107
          ).split()
assert len(CHORDS) == 107, len(CHORDS)
QUALITY = {'': (0, 4, 7), 'm': (0, 3, 7), '7': (4, 7, 10), 'm7': (3, 7, 10), 'm7b5': (3, 6, 10)}
ROOTS = {'C': 0, 'D': 2, 'Eb': 3, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'Bb': 10, 'B': 11, 'F#': 6}
NAMES_F = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
NAMES_G = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']


def name(n, bar):
    return (NAMES_G if bar >= 71 else NAMES_F)[n % 12] + str(n // 12 - 1)


def make_organ():
    """Pedal on the root, three held chord tones voice-led around middle C, and a quarter-note
    figure on top (5th, root, 3rd, 5th per half bar) that keeps the piano's constant motion."""
    lanes = {f'organ_{i}': [] for i in range(1, 6)}
    held = [55, 60, 64]
    for bar, symbol in enumerate(CHORDS, 1):
        halves = symbol.split('|') if '|' in symbol else [symbol, symbol]
        rows = [[] for _ in range(5)]
        for chord in halves:
            root = next(r for r in sorted(ROOTS, key=len, reverse=True) if chord.startswith(r))
            pc, quality = ROOTS[root], chord[len(root):]
            pcs = [(pc + i) % 12 for i in QUALITY[quality]]
            # nearest voicing (each tone within G3–G4) to the previous chord
            options = []
            for shift in range(3):
                tones = pcs[shift:] + pcs[:shift]
                voiced, low = [], 55
                for t in tones:
                    n = low + (t - low) % 12; voiced.append(n); low = n + 1
                if voiced[-1] <= 69: options.append(voiced)
            held = min(options, key=lambda v: sum(abs(x - y) for x, y in zip(v, held)))
            rows[0].append(f'{name(40 + (pc - 40) % 12, bar)}:2')
            for i in range(3):
                rows[i + 1].append(f'{name(held[i], bar)}:2')
            third, fifth = (pc + (3 if quality.startswith('m') else 4)) % 12, (pc + (6 if quality == 'm7b5' else 7)) % 12
            up = lambda x: 69 + (x - 69) % 12
            rows[4].append(' '.join(f'{name(up(x), bar)}:1' for x in (fifth, pc))
                           if len(rows[4]) == 0 else ' '.join(f'{name(up(x), bar)}:1' for x in (third, fifth)))
        for i, row in enumerate(rows):
            text = ' '.join(row)
            if i < 4 and row[0] == row[1]:
                text = row[0].replace(':2', ':4')
            lanes[f'organ_{i + 1}'].append(text)
    return lanes


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

song = {
    'id': 'angels-carol', 'title': 'Angels’ Carol', 'emoji': '😇',
    'source_pdf': PDF,
    'meter': [2, 2], 'key_fifths': -1, 'measure_keys': {'71': 1}, 'tempo': 138,
    'review_notes': [
        'Notes from an Audiveris draft checked and corrected system by system against enlarged crops of the scan; the alto moves B3 → B♭3 at 102–103 with the tenor; bars the draft missed (e.g. 54–61, 72, 78, 80–81, 94–95, 102–107) were read by eye. Inner divisi notes are the least certain.',
        'Divisi: each part sings the upper note of its own divisi (sopranos in thirds at 96–99, basses in octaves at 34, 56, 58, 106).',
        'Bars 3–10 sopranos and altos in unison; 11–18 tenors alone; 19–20 sopranos and tenors in octaves. Basses rest until bar 28.',
        'The piano/harp part becomes a simplified organ backing track: one chord per half bar read from the piano (CHORDS, rechecked against the score), root in the pedal, three held chord tones voice-led around middle C and a quarter-note figure on top echoing the piano’s constant arpeggios (e.g. the four F-major bars 34–37). It is not a transcription of the piano part.',
        'Bars 104–107 are printed in 4/4 (“Tranquil”, quarter = 92) with a rallentando; playback keeps the opening pulse. Suggested tempo half = 69 (quarter = 138).',
    ],
    'parts': parts, 'playback': [{'measure': m} for m in range(1, 108)],
    'backing_track': {'instrument': 'organ', 'parts': make_organ()},
    'sections': [{'at': [1, 0], 'name': 'intro'}, {'at': [3, 0], 'name': 'verse'}, {'at': [28, 0], 'name': 'chorus'},
                 {'at': [35, 0], 'name': 'interlude'}, {'at': [37, 0], 'name': 'verse'},
                 {'at': [62, 0], 'name': 'chorus'}, {'at': [71, 0], 'name': 'verse'}, {'at': [96, 0], 'name': 'chorus'},
                 {'at': [104, 0], 'name': 'coda'}],
    'systems': systems,
    'verses': [{'number': 1, 'title': 'Brano intero', 'lyrics': lyrics}],
    'staff_bands': {'soprano': [0, .25], 'alto': [0, .25], 'tenor': [.25, .5], 'bass': [.25, .5]},
    'compact': {'instructions': 'Brano in forma continua: tre strofe con Gloria; da battuta 71 in sol maggiore.'},
}

save_song(song)
