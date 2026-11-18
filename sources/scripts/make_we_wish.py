"""Build data/we-wish-you-a-merry-christmas.json: We Wish You a Merry Christmas (traditional English,
“Canto autoctono Inglese”), SATB a cappella, supplied as a NoteWorthy Composer vector PDF
(songs/We Wish You a Merry Christmas.pdf, 3 pages, 49 bars, B♭ major, 3/4, ♩ = 120).

Pitches from vector_heads.py (NWC2STDA font):
  --font NWC2 --filled f06b --half f06a --whole none --dot f07a --rest f06d
  --accidentals f064,f066,f065 --key B,E --clefs T,T,T8,B
(the dump applies only the key signature: printed accidentals carry through the bar here, so the
tenor's second E in bars 30/46 is E♮ and its F♯ in bars 6/22/38 holds for the whole bar).
Rhythms, slurs and syllables read from the page. Through-composed, one stanza: tenors and basses
alone (1–9), sopranos and altos alone (9–17), everyone (18–25), “Good tidings” (25–33),
“din don diri” (33–41), “Good tidings” and the close (41–49)."""
from song_kit import crop_systems, save_song

PDF = 'songs/We Wish You a Merry Christmas.pdf'
REST = 'R:3'

# ---- the tune and its harmony, eight bars from “wish” to “Year!” (S/A bars 10–17, T/B bars 2–9)
S_TUNE = ['Bb4:1 Bb4:0.5 C5:0.5 Bb4:0.5 A4:0.5', 'G4:1 G4:1 G4:1', 'C5:1 C5:0.5 D5:0.5 C5:0.5 Bb4:0.5',
          'A4:1 F4:1 F4:1', 'D5:1 D5:0.5 Eb5:0.5 D5:0.5 C5:0.5', 'Bb4:1 G4:1 F4:0.5 F4:0.5', 'G4:1 C5:1 A4:1',
          'Bb4:2 F4:1']
A_TUNE = ['F4:1 F4:0.5 A4:0.5 G4:0.5 F4:0.5', 'Eb4:1 Eb4:1 Eb4:1', 'G4:1 G4:0.5 Bb4:0.5 A4:0.5 G4:0.5',
          'F4:1 F4:1 F4:1', 'A4:1 A4:0.5 C5:0.5 Bb4:0.5 A4:0.5', 'G4:1 D4:1 D4:0.5 D4:0.5', 'C4:1 G4:1 F4:1',
          'F4:2 F4:1']
T_TUNE = ['F3:1 F3:0.5 F3:0.5 F3:0.5 F3:0.5', 'Bb3:1 Bb3:1 Bb3:1', 'Eb4:1 Eb4:0.5 Eb4:0.5 Eb4:0.5 D4:0.5',
          'C4:1 A3:1 G3:1', 'F#3:1 F#3:0.5 F#3:0.5 G3:0.5 A3:0.5', 'G3:1 Bb3:1 Bb3:0.5 A3:0.5', 'G3:1 Eb4:1 C4:1']
B_TUNE = ['D3:1 D3:0.5 Bb2:0.5 C3:0.5 D3:0.5', 'Eb3:1 Eb3:0.5 F3:0.5 Eb3:0.5 D3:0.5', 'C3:1 C3:0.5 C3:0.5 D3:0.5 Eb3:0.5',
          'F3:1 F3:0.5 G3:0.5 F3:0.5 Eb3:0.5', 'D3:1 D3:0.5 D3:0.5 E3:0.5 F#3:0.5', 'G3:1 G3:1 D3:0.5 D3:0.5',
          'Eb3:1 C3:1 F3:1']

# ---- “Good tidings we bring … happy new Year!” (bars 26–33 and 42–49)
S_GOOD = ['Bb4:1 Bb4:1 Bb4:1', 'A4:2 A4:1', 'Bb4:1 A4:1 G4:1', 'F4:2 C5:1', 'D5:1 C5:0.5 C5:0.5 Bb4:0.5 Bb4:0.5',
          'C5:1 A4:1 F4:0.5 F4:0.5', 'G4:1 C5:1 A4:1']
A_GOOD = ['F4:1 F4:1 F4:1', 'F4:2 F4:1', 'G4:1 F4:1 E4:1', 'C4:2 F4:1', 'Bb4:1 A4:0.5 A4:0.5 F4:0.5 F4:0.5',
          'G4:1 F4:1 F4:0.5 F4:0.5', 'Eb4:1 G4:1 F4:1']
T_GOOD = ['Bb3:1 D4:1 Bb3:1', 'C4:0.5 D4:0.5 C4:1 C4:1', 'Bb3:1 Bb3:1 C4:0.5 Bb3:0.5', 'A3:2 F3:1',
          'F3:1 E3:0.5 E3:0.5 F3:0.5 F3:0.5', 'Eb3:1 C4:1 Bb3:0.5 A3:0.5', 'Bb3:1 Eb4:1 C4:1']
B_GOOD = ['D3:1 Bb2:0.5 C3:0.5 D3:0.5 Eb3:0.5', 'F3:1.5 G3:0.5 F3:0.5 Eb3:0.5', 'D3:1 D3:1 E3:1', 'F3:1 F2:1 A2:1',
          'Bb2:1 C3:0.5 C3:0.5 D3:0.5 D3:0.5', 'C3:1 F3:1 D3:0.5 D3:0.5', 'Eb3:1 C3:1 F3:1']

# Bar 1 and the bar before each pickup.
parts = {
    'soprano': [REST] * 8 + ['R:2 F4:1'] + S_TUNE + S_TUNE + S_GOOD + ['Bb4:2 F4:1'] + S_TUNE + S_GOOD + ['Bb4:3'],
    'alto':    [REST] * 8 + ['R:2 F4:1'] + A_TUNE + A_TUNE + A_GOOD + ['F4:2 F4:1'] + A_TUNE + A_GOOD + ['F4:3'],
    'tenor':   ['R:2 F3:1'] + T_TUNE + ['D4:3'] + [REST] * 7 + ['R:2 F3:1'] + T_TUNE + ['D4:2 A3:1']
               + T_GOOD + ['D4:2 F3:1'] + T_TUNE + ['D4:2 A3:1'] + T_GOOD + ['D4:3'],
    'bass':    ['R:2 F3:1'] + B_TUNE + ['Bb2:3'] + [REST] * 7 + ['R:2 F3:1'] + B_TUNE + ['Bb2:2 F3:1']
               + B_GOOD + ['Bb2:2 F3:1'] + B_TUNE + ['Bb2:2 F3:1'] + B_GOOD + ['Bb2:3'],
}
assert all(len(p) == 49 for p in parts.values()), {v: len(p) for v, p in parts.items()}

# ---- words: one syllable per sounding note, bar by bar ('|'); '_' = the note continues the
# previous syllable (a slurred melisma), so it takes no word.
WISH = 'wish you a Mer- ry | Christ- mas, We | wish you a Mer- ry | Christ- mas, We | wish you a Mer- ry | Christ- mas, and a | hap- py new'
GOOD = 'ti- dings we | bring to | you and your | kin; We | wish you a Mer- ry | Christ- mas, and a | hap- py new'
DIN = ('don di- ri- di- ri- | din don din | don di- ri- di- ri- | din don din | don di- ri- di- ri- | '
       'din don di- ri- | din don din')
SILENT7 = ' | '.join([''] * 7)
upper = (' | '.join([''] * 8) + ' | We | ' + WISH + ' | Year! We | ' + WISH + ' | Year! Good | ' + GOOD
         + ' | Year! din | ' + DIN + ' | dan Good | ' + GOOD + ' | Year!')
lower = 'We | ' + WISH + ' | Year! | ' + SILENT7 + ' | We | ' + WISH + ' | Year! Good | ' + GOOD + ' | Year! din | '
words = {
    'soprano': upper,
    'alto': upper,
    'tenor': lower + DIN + ' | dan Good | ' + GOOD + ' | Year!',
    'bass': lower + 'don di- ri- di- ri- | din di- ri di- ri | don di- ri- di- ri- | din di- ri di- ri | '
            'don di- ri- di- ri- | din don di- ri | din don din | dan Good | ' + GOOD + ' | Year!',
}
# Printed slurs (melismas): the bass's “Christ-mas, We” (its din-don bars 35/37 have the same notes
# unslurred, one syllable each), “tidings we bring to” and the “kin; We” leap; the tenor's “bring”
# (C–D–C) and “your” (C–B♭).
CHRISTMAS, TIDINGS, BRING, KIN = 'Christ- mas, _ We _', 'ti- dings _ we _', 'bring _ to _', 'kin; We _'
SLURS = {'bass': {3: CHRISTMAS, 5: CHRISTMAS, 19: CHRISTMAS, 21: CHRISTMAS,
                  26: TIDINGS, 27: BRING, 29: KIN, 42: TIDINGS, 43: BRING, 45: KIN},
         'tenor': {27: 'bring _ _ to', 28: 'you and your _', 43: 'bring _ _ to', 44: 'you and your _'}}


def onsets(bar):
    at, out = 0.0, []
    for token in bar.split():
        pitch, duration = token.split(':')
        if pitch != 'R':
            out.append(at)
        at += float(duration)
    return out


def cues(voice):
    bars = [b.strip() for b in words[voice].split('|')]
    assert len(bars) == 49, (voice, len(bars))
    rows = []
    for number, (music, text) in enumerate(zip(parts[voice], bars), 1):
        text = SLURS.get(voice, {}).get(number, text)
        syllables, starts = text.split(), onsets(music)
        assert len(syllables) == len(starts), (voice, number, syllables, starts)
        rows.append(' '.join(f'{b:g}:{w}' for b, w in zip(starts, syllables) if w != '_'))
    return rows


lyrics = {voice: cues(voice) for voice in parts}

H = 842
systems = []
for page, (first, rows) in enumerate(((1, [(5, 115, 335), (6, 345, 565), (6, 570, 790)]),
                                       (18, [(5, 70, 290), (6, 315, 535), (6, 560, 785)]),
                                       (35, [(6, 70, 290), (6, 315, 535), (3, 560, 785)]))):
    systems += crop_systems('we-wish-you-a-merry-christmas', PDF, [(n, a / H, b / H) for n, a, b in rows],
                            page=page, x=(.05, .94), first=first, start_index=len(systems))

song = {
    'id': 'we-wish-you-a-merry-christmas', 'title': 'We Wish You a Merry Christmas', 'emoji': '🎁',
    'composer': 'Traditional English (“Canto autoctono Inglese”)', 'arranger': 'unnamed (NoteWorthy Composer file supplied by the user)',
    'meter': [3, 4], 'key_fifths': -2, 'tempo': 120, 'source_pdf': PDF,
    'sources': [{'description': 'Vector PDF supplied by the user (WhatsApp document DOC-20261103-WA0004.pdf, '
                                'NoteWorthy Composer 2 export via Nuance PDF Create, 2017), renamed '
                                '“We Wish You a Merry Christmas.pdf”; used directly as the transcription source.'}],
    'review_notes': [
        'Pitches read from the exact notehead positions of the supplied vector PDF (NoteWorthy Composer font); rhythms, slurs and syllables read from the page. Accidentals carry through the bar: tenor bars 30/46 sing E♮ twice, tenor bars 6/22/38 F♯ three times.',
        'Through-composed, one stanza (49 bars): tenors and basses alone in bars 1–9, sopranos and altos alone in bars 9–17 (the other pair rests), all four from bar 18; “Good tidings” 25–33, “din don diri” 33–41 (the basses sing “din di-ri di-ri” on their eighths), “Good tidings” again and the close 41–49. Bars 18–25 and 34–41 repeat the music of bars 10–17 (S/A) and 2–9 (T/B); bars 42–48 repeat 26–32.',
        'Slurs are melismas, not ties: bass “mas,” and “We” in bars 3, 5, 19, 21, “dings”/“we” in 26 and 42, “bring”/“to” in 27 and 43, “We” (F2–A2) in 29 and 45; tenor “bring” (C–D–C) in 27/43 and “your” in 28/44.',
        'The traditional stanzas (“Now bring us some figgy pudding …”) are not part of this arrangement, which sets only the refrain words; none were added.',
        'Staccato dots are not encoded; “rall.” at bar 47 is printed as an annotation (playback keeps ♩ = 120, the printed tempo, throughout). No handwritten marks on the source.',
    ],
    'parts': parts, 'playback': [{'measure': m} for m in range(1, 50)],
    'sections': [{'at': [25, 2], 'name': 'chorus'}, {'at': [33, 2], 'name': 'interlude'}, {'at': [41, 2], 'name': 'chorus'}],
    'systems': systems,
    'verses': [{'number': 1, 'title': 'Brano intero', 'lyrics': lyrics}],
    'staff_bands': {'soprano': [0, .25], 'alto': [.25, .5], 'tenor': [.5, .75], 'bass': [.75, 1]},
    'compact': {'annotations': [{'measure': 47, 'voice': 'soprano', 'beat': 0, 'text': 'rall.'}],
                'instructions': 'Brano in forma continua: tenori e bassi da soli (1–9), soprani e contralti da soli (9–17), poi tutti.'},
}

save_song(song)
