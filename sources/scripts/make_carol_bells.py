"""Build data/carol-of-the-bells.json: Carol of the Bells, SATB a cappella (keyboard for rehearsal
only, not encoded). Source: the supplied six-page raster scan, G minor, 3/4, 42 bars:
bars 5–36 are repeated (1st ending 33–36, 2nd ending 37–42). Read by eye from 260–300 dpi crops,
with notehead steps measured against local staff lines where the scan was doubtful."""
from song_kit import crop_systems, fit_lyrics, save_song

PDF = 'songs/Carol of the Bells.pdf'
R = 'R:3'
O = 'Bb4:1 A4:0.5 Bb4:0.5 G4:1'          # the four-note bell ostinato
QEEQ = [0, 1, 1.5, 2]


def down(bar, octaves=1):
    out = []
    for token in bar.split():
        pitch, rest = token.split(':', 1)
        out.append(token if pitch == 'R' else f'{pitch[:-1]}{int(pitch[-1]) - octaves}:{rest}')
    return ' '.join(out)


def held(pitch, bars):
    """A dotted half sustained (tied) over several bars."""
    return [f'{pitch}:3~'] * (bars - 1) + [f'{pitch}:3']


def rep(bar, pitch):
    return f'{pitch}:1 {pitch}:0.5 {pitch}:0.5 {pitch}:1'


MERRY = ['D4:0.5 E4:0.5 F#4:0.5 G4:0.5 A4:0.5 Bb4:0.5', 'C5:0.5 D5:0.5 C5:1 Bb4:1']
S = ([O] * 16 + ['D5:1 C5:0.5 D5:0.5 Bb4:1'] * 4
     + ['G5:1 G5:0.5 G5:0.5 F5:0.5 Eb5:0.5', 'D5:1 D5:0.5 D5:0.5 C5:0.5 Bb4:0.5',
        'C5:1 C5:0.5 C5:0.5 D5:0.5 C5:0.5', rep(0, 'G4')] + MERRY * 2
     + [O] * 8 + held('G4', 4) + ['Bb4:1 A4:0.5 Bb4:0.5 G4:1~', 'G4:3'])
DING = ['E4:1 F#4:1 G4:1']
A = ([R] * 4 + ['G4:3', 'F4:3', 'Eb4:3', 'D4:3'] * 2 + [rep(0, 'G4')] * 4 + [O] * 4 + [rep(0, 'G4')] * 4
     + ['D4:3'] + DING + ['D4:3'] + DING + ['D4:3', 'C4:3', 'F4:3', 'Eb4:3'] + held('D4', 3) + [R]
     + held('D4', 4) + [R, R])
T = ([R] * 8 + ['Eb4:3', 'D4:3', 'C4:3', 'G3:3'] + [rep(0, 'C4'), rep(0, 'D4'), rep(0, 'Eb4'), rep(0, 'D4')]
     + ['D4:3', 'E4:3', 'F4:1 Eb4:1 D4:1', 'G4:0.5 F4:0.5 Eb4:1 D4:1',
        'D4:1 D4:0.5 D4:0.5 D4:0.5 C4:0.5', rep(0, 'D4'), 'Eb4:1 Eb4:0.5 Eb4:0.5 F4:0.5 Eb4:0.5', rep(0, 'D4')]
     + [down(O)] * 4 + ['G3:3'] * 4 + held('G3', 3) + [R] + [down(O)] * 4 + [R, R])
OB = 'Bb3:1 A3:0.5 Bb3:0.5 G3:1'
B = ([R] * 12 + [rep(0, 'Eb3'), rep(0, 'G3'), rep(0, 'C4'), rep(0, 'G3')] + [rep(0, 'G3')] * 4
     + [OB] * 4 + ['D3:3', 'D3:3', 'D3:3', 'D3:2 E3:1', 'F3:3', 'Eb3:3', 'D3:3', 'C3:3']
     + held('G2', 3) + [R] + held('G2', 4) + [R, 'G2:3'])
parts = {'soprano': S, 'alto': A, 'tenor': T, 'bass': B}
assert all(len(p) == 42 for p in parts.values()), {v: len(p) for v, p in parts.items()}

# Words: one entry per bar as (onsets, syllables); an empty string means no words.
HARK = ['Hark! how the bells,', 'sweet sil- ver bells,', 'All seem to say,', '“throw cares a- way.”']
TEXT_S = (HARK + ['Christ- mas is here', 'bring- ing good cheer,', 'To young and old,', 'meek and the bold.',
                  'Ding, dong, ding, dong,', 'that is their song,', 'With joy- ful ring,', 'all car- ol- ing.',
                  'One seems to hear', 'words of good cheer', 'From ev- ’ry- where,', 'fill- ing the air.',
                  'Oh, how they pound,', 'rais- ing the sound,', 'O’er hill and dale,', 'tell- ing their tale.',
                  'Gai- ly they ring,', 'while peo- ple sing,', 'songs of good cheer,', 'Christ- mas is here!',
                  'Mer- ry, Mer- ry, Mer- ry,', 'Mer- ry Christ- mas!', 'Mer- ry, Mer- ry, Mer- ry,', 'Mer- ry Christ- mas!',
                  'On, on they send,', 'on with- out end,', 'Their joy- ful tone', 'to eve- ry home.']
          + HARK + ['dong.', '', '', '', 'Ding, dong, ding, dong.', ''])
WORDS13 = TEXT_S[12:24]
TEXT_A = (['', '', '', ''] + ['Ding,', 'dong,', 'ding,', 'dong,'] * 2 + WORDS13
          + ['Ding,', 'ding, dong.', 'Ding,', 'ding, dong,', 'Ding,', 'dong,', 'ding,', '', 'dong.', '', '', '',
             'dong.', '', '', '', '', ''])
TEXT_T = (['', ''] * 4 + ['Ding,', 'dong,', 'ding,', 'dong.'] + TEXT_S[12:16]
          + ['Oh,', 'how', 'hap- py', 'are their tones.'] + TEXT_S[20:24] + TEXT_S[8:12]
          + ['Ding,', 'dong,', 'ding,', 'ding,', 'dong.', '', '', ''] + TEXT_S[28:32] + ['', ''])
TEXT_B = (['', ''] * 6 + TEXT_S[12:24] + ['Ding,', 'dong,', 'ding,', 'dong.', 'Ding,', 'dong,', 'ding,', '',
                                         'dong.', '', '', '', 'dong.', '', '', '', '', 'Bohm!'])
# Bars where a syllable spans two notes (slur): voice → {bar: onsets}.
MELISMA = {'soprano': {21: [0, 1, 1.5, 2], 22: [0, 1, 1.5, 2], 23: [0, 1, 1.5, 2], 41: [0, 1, 1.5, 2]},
           'alto': {26: [0, 2], 28: [0, 2]},
           'tenor': {19: [0, 2], 20: [0, 1, 2], 21: [0, 1, 1.5, 2], 23: [0, 1, 1.5, 2]},
           'bass': {28: [0]}}


def starts(bar):
    beat, out, tied = 0.0, [], False
    for token in bar.split():
        pitch, dur = token.split(':')
        if pitch != 'R' and not tied:
            out.append(beat)
        tied = dur.endswith('~'); beat += float(dur.rstrip('~'))
    return out


lyrics = {}
for voice, text in (('soprano', TEXT_S), ('alto', TEXT_A), ('tenor', TEXT_T), ('bass', TEXT_B)):
    assert len(text) == 42, (voice, len(text))
    rows = []
    for m, (bar, words) in enumerate(zip(parts[voice], text), 1):
        syl = words.split()
        beats = MELISMA[voice].get(m, starts(bar))[:len(syl)]
        assert len(beats) == len(syl), (voice, m, beats, syl)
        rows.append(' '.join(f'{b:g}:{w}' for b, w in zip(beats, syl)))
    lyrics[voice] = fit_lyrics(parts[voice], rows)

LAYOUT = [(0, [(3, .10, .42), (4, .45, .84)]), (1, [(4, .07, .46), (4, .48, .86)]),
          (2, [(4, .07, .46), (3, .48, .86)]), (3, [(3, .07, .46), (3, .48, .86)]),
          (4, [(4, .07, .46), (4, .48, .86)]), (5, [(3, .07, .46), (3, .48, .72)])]
systems, first = [], 1
for page, rows in LAYOUT:
    systems += crop_systems('carol-of-the-bells', PDF, rows, page=page, x=(.2, .97), first=first, start_index=len(systems))
    first += sum(r[0] for r in rows)
assert first == 43

song = {
    'id': 'carol-of-the-bells', 'title': 'Carol of the Bells', 'emoji': '🔔',
    'source_pdf': PDF,
    'meter': [3, 4], 'key_fifths': -2, 'tempo': 140,
    'review_notes': [
        'Read by eye from 260–300 dpi crops of a raster scan (OMR failed); doubtful heads were measured against local staff lines. The rehearsal keyboard part is not encoded.',
        'Form: bars 5–36 repeat (1st ending 33–36), then the 2nd ending 37–42. Playback: 1–36, 5–32, 37–42; the words are the same both times.',
        'Bar 41 sopranos divide (D5–C5–D5 over B♭4–A4–B♭4): only the lower line (the ostinato) is encoded. Bar 42 “Bohm!” is basses only; the “Slowly (dictated)” close and the fermatas are not applied.',
        'Default tempo quarter = 140 (user choice; “Allegro”).',
    ],
    'parts': parts,
    'playback': [{'measure': m} for m in list(range(1, 37)) + list(range(5, 33)) + list(range(37, 43))],
    'systems': systems,
    'verses': [{'number': 1, 'title': 'Strofa 1', 'lyrics': lyrics}],
    'staff_bands': {'soprano': [0, .25], 'alto': [.25, .5], 'tenor': [.5, .75], 'bass': [.75, 1]},
    'compact': {'instructions': 'Ritornello: dopo la battuta 36 si torna alla 5; la seconda volta si salta da 32 alla 37.'},
}

save_song(song)
