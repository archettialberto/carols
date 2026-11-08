"""Build data/a-new-year-carol.json: A New Year Carol (the composer, the 1936 original.
Source: the clean two-page edition supplied by the user (unison voices + piano), E♭ major, 3/4:
intro 1–4, verse 5–12, refrain 13–22 with D.S., coda (refrain for verse 3) 23–30.
All choir parts sing the printed tune (tenors and basses an octave lower); the piano part is a
slightly simplified organ backing track (chord tones per half + quarter, as printed)."""
from song_kit import crop_systems, fit_lyrics, save_song

PDF = 'songs/A New Year Carol.pdf'
R3 = 'R:3'
TUNE = (['R:3'] * 4 + [
    'G4:0.5 F4:0.5 Eb4:1 G4:1', 'F4:0.5 G4:0.5 Ab4:1 F4:0.5 F4:0.5', 'G4:0.5 F4:0.5 Eb4:1 Eb4:1', 'Ab4:2 R:1',
    'G4:0.5 F4:0.5 Eb4:1 G4:1', 'Bb4:1 Ab4:1 F4:1', 'G4:0.5 F4:0.5 Eb4:1 G4:1', 'F4:2 F4:1'])
REFRAIN = ['Bb4:0.5 Ab4:0.5 G4:1 Bb4:1', 'Ab4:0.5 Bb4:0.5 C5:1 Ab4:1', 'Bb4:0.5 Ab4:0.5 G4:1 G4:1', 'C5:2 C5:1',
           'D5:0.5 C5:0.5 Bb4:1 Bb4:1', 'Eb5:2 D5:0.5 C5:0.5', 'Bb4:0.5 Ab4:0.5 G4:1 F4:1', 'Eb4:2 R:1']
TUNE += REFRAIN + [R3, R3] + REFRAIN


def down(bar):
    """The same bar an octave lower (tenors and basses)."""
    out = []
    for token in bar.split():
        pitch, rest = token.split(':', 1)
        out.append(token if pitch == 'R' else f'{pitch[:-1]}{int(pitch[-1]) - 1}:{rest}')
    return ' '.join(out)


parts = {'soprano': TUNE, 'alto': TUNE, 'tenor': [down(b) for b in TUNE], 'bass': [down(b) for b in TUNE]}

# Piano → organ: each bar is (half-note chord, quarter chord), notes listed high → low.
I_ = (['G4', 'Bb3', 'G3', 'Bb2', 'Eb2'], ['G4', 'Bb3', 'Eb3'])          # verse, odd bars
IV = (['Ab4', 'C4', 'Ab3', 'Bb2', 'Eb2'], ['Ab4', 'C4', 'F3'])          # verse, even bars
RI = (['Bb4', 'D4', 'G3', 'Bb2', 'Eb2'], ['Bb4', 'D4', 'G3'])           # refrain
RIV = (['C5', 'Eb4', 'Ab3', 'Bb2', 'Eb2'], ['C5', 'Eb4', 'Ab3'])
CI = (['Bb5', 'D5', 'Bb4', 'G3', 'Bb2', 'Eb2'], ['G4', 'D4', 'G3'])     # coda (higher, fuller)
CIV = (['C6', 'Eb5', 'C5', 'Ab3', 'Bb2', 'Eb2'], ['Ab4', 'Eb4', 'Ab3'])
CHORDS = ([I_, IV] * 4 + [I_, 'b10', I_, IV]
          + [RI, RIV, RI, RIV, (['D5', 'F4', 'Bb3', 'D3', 'G2'], ['D5', 'F4', 'Bb3']),
             (['Eb5', 'Ab4', 'C4', 'C3', 'F2'], ['Ab4', 'C4', 'F3']), I_, IV, I_, IV]
          + [CI, CIV, CI, CIV, (['Bb5', 'F5', 'D5', 'F3', 'Bb2', 'G2'], ['D5', 'G4', 'F3']),
             (['C6', 'Ab5', 'Eb5', 'C3', 'Ab2', 'C2'], ['C5', 'Ab4', 'C3']), 'b29', 'b30'])
LANES = 6
SPECIAL = {  # bars written out lane by lane (top lane first)
    'b10': ['Bb4:1 Ab4:1 Ab4:1', 'C4:2 C4:1', 'Ab3:2 F3:1', 'Bb2:2 R:1', 'Eb2:2 R:1', R3],
    'b29': ['D6:2 Bb5:1', 'Bb5:1 Bb4:1 R:1', 'F5:2 R:1', 'Bb3:1 Bb3:1 Bb2:1', 'F2:2 R:1', 'Bb1:2 R:1'],
    'b30': ['Eb6:2 R:1', 'G5:2 R:1', 'Eb5:2 R:1', 'Bb2:2 R:1', 'G2:2 R:1', 'Eb2:2 R:1'],
}
lanes = {f'organ_{i + 1}': [] for i in range(LANES)}
for chord in CHORDS:
    if isinstance(chord, str):
        rows = SPECIAL[chord]
    else:
        half, quarter = chord
        rows = []
        for i in range(LANES):
            h = f'{half[i]}:2' if i < len(half) else 'R:2'
            q = f'{quarter[i]}:1' if i < len(quarter) else 'R:1'
            rows.append(f'{h} {q}')
    for i, row in enumerate(rows):
        lanes[f'organ_{i + 1}'].append(row)
assert all(len(v) == 30 for v in lanes.values())

E4 = [0, .5, 1, 2]
VERSE_ONSETS = {1: [E4, [0, 1, 2, 2.5], [0, 2], [0], E4, [0, 1, 2], [0, 1, 2], [0, 2]],
                2: [[0, 1, 2], [0, 1, 2], E4, [0], E4, [0, 1, 2], E4, [0, 2]]}
VERSE_ONSETS[3] = VERSE_ONSETS[2]
REFRAIN_ONSETS = [E4, E4, E4, [0, 2], E4, [0, 2, 2.5], E4, [0]]
REFRAIN_WORDS = 'le- vy dew, sing | le- vy dew, the | wa- ter and the | wine; The | se- ven bright gold | wires and the | bu- gles that do | shine.'
VERSES = {
    1: 'Here we bring new | wa- ter from the | well so | clear, | For to wor- ship | God with, this | hap- py New | Year. Sing',
    2: 'Sing reign of | Fair Maid, with | gold up- on her | toe, | O- pen you the | West Door, and | turn the Old Year | go. Sing',
    3: 'Sing reign of | Fair Maid, with | gold up- on her | chin, | O- pen you the | East Door, and | let the New Year | in. Sing',
}


def cues(onsets, text):
    out = []
    for beats, words in zip(onsets, text.split('|')):
        words = words.split(); assert len(beats) == len(words), (beats, words)
        out.append(' '.join(f'{b:g}:{w}' for b, w in zip(beats, words)))
    return out


refrain = cues(REFRAIN_ONSETS, REFRAIN_WORDS)
verses = []
for number in (1, 2, 3):
    rows = [''] * 4 + cues(VERSE_ONSETS[number], VERSES[number]) + refrain + ['', ''] + refrain
    order = list(range(1, 23)) if number == 1 else list(range(5, 23)) if number == 2 else list(range(5, 13)) + list(range(23, 31))
    verses.append({'number': number, 'title': f'Strofa {number}', 'playback': [{'measure': m} for m in order],
                   'lyrics': {v: fit_lyrics(parts[v], rows) for v in parts}})

systems = crop_systems('a-new-year-carol', PDF, [(4, .12, .37), (4, .37, .62), (4, .62, .92)], page=0, x=(.05, .97))
systems += crop_systems('a-new-year-carol', PDF, [(4, .0, .26), (6, .25, .49), (4, .48, .73), (4, .72, .99)],
                        page=1, x=(.05, .97), first=13, start_index=3)

song = {
    'id': 'a-new-year-carol', 'title': 'A New Year Carol', 'emoji': '🎆',
    'composer': 'the composer; words anon.', 'arranger': 'the 1936 original',
    'meter': [3, 4], 'key_fifths': -3, 'tempo': 92,
    'source_pdf': PDF,
    'sources': [{'description': 'Clean two-page edition (unison voices and piano) supplied by the user; it replaces the worn S.S.A. 1971 scan (kept locally as “A New Year Carol (SSA scan).pdf”, not transcribed).'}],
    'review_notes': [
        'Printed for unison voices: all four parts sing the tune, tenors and basses an octave lower. The S.S.A. 1971 arrangement of the old scan is not encoded.',
        'Form: intro 1–4, verse 5–12, refrain 13–22, D.S. to bar 5; verse 3 goes from bar 12 to the coda (refrain for verse 3, bars 23–30). Playback: verse 1 = 1–22, verse 2 = 5–22, verse 3 = 5–12 + 23–30.',
        'The piano part becomes the organ backing track in six lanes, simplified to the printed chord tones of each half + quarter pattern (arpeggiations, pedal and una corda omitted). Upper coda voicings were read at reduced certainty.',
        '“Sing” on bar 12 beat 3 is taken in every verse (it leads into both the refrain and the coda).',
        'Suggested tempo quarter = 92 (“Quietly”).',
    ],
    'parts': parts, 'playback': [{'measure': m} for m in range(1, 23)],
    'backing_track': {'instrument': 'organ', 'parts': lanes},
    'sections': [{'at': [1, 0], 'name': 'intro'}, {'at': [5, 0], 'name': 'verse'}, {'at': [13, 0], 'name': 'chorus'},
                 {'at': [21, 0], 'name': 'interlude'}, {'at': [23, 0], 'name': 'coda'}],
    'systems': systems, 'verses': verses,
    'staff_bands': {'soprano': [0, .5], 'alto': [0, .5], 'tenor': [.5, 1], 'bass': [.5, 1]},
    'shared_lyrics': True,
    'compact': {'instructions': 'Strofe 1–2: strofa e ritornello, poi D.S.; strofa 3: dopo “in.” al Coda (battute 23–30).'},
}

save_song(song)
