"""Build data/a-new-year-carol.json: A New Year Carol, the choir version supplied by the user
(songs/A New Year Carol (SATB).pdf, three pages of scan excerpts, E♭ major, 3/4), sung a cappella.

Each stanza is 16 bars (verse 8 + refrain 8) and the three are written out one after another:
stanza 1 sopranos alone; stanza 2 sopranos and altos; stanza 3 everyone, sopranos with a descant
in the refrain, altos taking the tune, tenors and basses in unison on the third staff (printed in
treble clef, sung an octave lower). The bars of rest after stanzas 1 and 2 (for the piano) are left
out, so every bar has singing. No organ or backing track."""
from song_kit import crop_systems, fit_lyrics, save_song

PDF = 'songs/A New Year Carol (SATB).pdf'
R16 = ['R:3'] * 16

# ---- the tune (stanza 1 sopranos), reused by the sopranos in stanzas 2–3 and the altos' refrain 3
VERSE1 = ['G4:0.5 F4:0.5 Eb4:1 G4:1', 'F4:0.5 G4:0.5 Ab4:1 F4:0.5 F4:0.5', 'G4:0.5 F4:0.5 Eb4:1 Eb4:1', 'Ab4:2 R:1',
          'G4:0.5 F4:0.5 Eb4:1 G4:1', 'Bb4:1 Ab4:1 F4:1', 'G4:0.5 F4:0.5 Eb4:1 G4:1', 'F4:2 F4:1']
# stanzas 2–3: "Fair Maid, with" ends on one quarter instead of two eighths
VERSE23 = VERSE1[:1] + ['F4:0.5 G4:0.5 Ab4:1 F4:1'] + VERSE1[2:]
REFRAIN = ['Bb4:0.5 Ab4:0.5 G4:1 Bb4:1', 'Ab4:0.5 Bb4:0.5 C5:1 Ab4:1', 'Bb4:0.5 Ab4:0.5 G4:1 G4:1', 'C5:2 C5:1',
           'D5:0.5 C5:0.5 Bb4:1 Bb4:1', 'Eb5:2 D5:0.5 C5:0.5', 'Bb4:0.5 Ab4:0.5 G4:1 F4:1', 'Eb4:2 R:1']
# ---- the second line (altos in stanza 2, tenors and basses in stanza 3)
LOW_REFRAIN = ['G4:0.5 Ab4:0.5 Bb4:1 G4:1', 'C5:0.5 Bb4:0.5 Ab4:1 C5:1', 'G4:0.5 Ab4:0.5 Bb4:1 G4:1']
ALTO2 = (['Eb4:0.5 F4:0.5 G4:1 Eb4:1', 'Ab4:0.5 G4:0.5 F4:1 Ab4:1', 'Eb4:0.5 F4:0.5 G4:1 Eb4:1', 'C4:2 R:1',
          'Eb4:0.5 F4:0.5 G4:1 Eb4:1', 'C4:1 F4:1 Ab4:1', 'Eb4:0.5 F4:0.5 G4:1 Eb4:1', 'F4:2 F4:1']
         + LOW_REFRAIN + ['Eb4:2 Ab4:1',
            'Bb4:0.5 Ab4:0.5 G4:1 F4:1', 'Eb4:1 C5:1 Bb4:0.5 Ab4:0.5', 'G4:0.5 G4:0.5 C4:1 D4:1', 'Eb4:2 R:1'])
# ---- stanza 3
ALTO3 = (['Bb4:1 G4:1 Eb4:1', 'Ab4:0.5 G4:0.5 F4:1 Ab4:1', 'Bb4:1 G4:1 Eb4:1', 'F4:2 R:1',
          'Bb4:1 G4:1 Eb4:0.5 Eb4:0.5', 'F4:1 F4:1 Eb4:1', 'Bb4:0.5 Ab4:0.5 G4:1 Eb4:1', 'F4:2 F4:1']
         + REFRAIN[:2] + ['Bb4:0.5 Ab4:0.5 G4:1 Bb4:1'] + REFRAIN[3:])
DESCANT = ['Bb4:3', 'C5:3', 'D5:3', 'Eb5:2 F5:1', 'F5:3', 'G5:1 F5:1 Eb5:1~', 'Eb5:1 D5:0.5 C5:0.5 Bb4:0.5 Ab4:0.5', 'G4:2 R:1']
LOW3 = (['Eb4:0.5 F4:0.5 G4:1 Eb4:1', 'C4:1 F4:1 Ab4:1', 'Eb4:0.5 F4:0.5 G4:1 Eb4:1', 'C4:2 R:1',
         'Eb4:0.5 F4:0.5 G4:1 Eb4:1', 'C4:1 F4:1 Ab4:1', 'Eb4:0.5 F4:0.5 G4:1 Eb4:1', 'F4:2 F4:1']
        + LOW_REFRAIN + ['Eb4:2 C5:1',
           'Bb4:0.5 Ab4:0.5 G4:0.5 F4:0.5 Eb4:0.5 D4:0.5', 'C4:2 D4:0.5 Eb4:0.5', 'F4:0.5 F4:0.5 Bb4:1 Bb3:1', 'Eb4:2 R:1'])


def down(bar):
    """The same bar an octave lower (tenors and basses sing the treble-clef line)."""
    out = []
    for token in bar.split():
        pitch, rest = token.split(':', 1)
        out.append(token if pitch == 'R' else f'{pitch[:-1]}{int(pitch[-1]) - 1}:{rest}')
    return ' '.join(out)


soprano = VERSE1 + REFRAIN + VERSE23 + REFRAIN + VERSE23 + DESCANT
alto = R16 + ALTO2 + ALTO3
low = R16 + R16 + [down(b) for b in LOW3]
parts = {'soprano': soprano, 'alto': alto, 'tenor': low, 'bass': list(low)}
assert all(len(p) == 48 for p in parts.values()), {v: len(p) for v, p in parts.items()}

# ---- words: 'syllables | per | bar' with the beats of each syllable
REFRAIN_WORDS = ('0:le- .5:vy 1:dew, 2:sing | 0:le- .5:vy 1:dew, 2:the | 0:wa- .5:ter 1:and 2:the | 0:wine; 2:The | '
                 '0:sev- .5:en 1:bright 2:gold | 0:wires 2:and 2.5:the | 0:bu- .5:gles 1:that 2:do | 0:shine.')
TUNE_ONSETS_1 = '0:{} .5:{} 1:{} 2:{} | 0:{} 1:{} 2:{} 2.5:{} | 0:{} 2:{} | 0:{} | 0:{} .5:{} 1:{} 2:{} | 0:{} 1:{} 2:{} | 0:{} 1:{} 2:{} | 0:{} 2:{}'
TUNE_ONSETS_23 = '0:{} 1:{} 2:{} | 0:{} 1:{} 2:{} | 0:{} .5:{} 1:{} 2:{} | 0:{} | 0:{} .5:{} 1:{} 2:{} | 0:{} 1:{} 2:{} | 0:{} .5:{} 1:{} 2:{} | 0:{} 2:{}'
STANZA = {
    1: 'Here we bring new wa- ter from the well so clear, For to wor- ship God with, this hap- py New Year. Sing',
    2: 'Sing reign of Fair Maid, with gold up- on her toe. O- pen you the West Door, and turn the Old Year go. Sing',
    3: 'Sing reign of Fair Maid, with gold up- on her chin, O- pen you the East Door, and let the New Year in. Sing',
}


def rows(text):
    return [' '.join(cue for cue in bar.split()) for bar in text.split('|')]


def fill(pattern, words):
    return rows(pattern.format(*words.split()))


EMPTY = [''] * 16
tune1 = fill(TUNE_ONSETS_1, STANZA[1]) + rows(REFRAIN_WORDS)
tune2 = fill(TUNE_ONSETS_23, STANZA[2]) + rows(REFRAIN_WORDS)
tune3 = fill(TUNE_ONSETS_23, STANZA[3])
descant = rows('0:le- | | 0:vy | 0:dew, 2:the | 0:bu- | 2:gles | 1:that 2:do | 0:shine.')
alto3_verse = rows('0:Sing 1:reign 2:of | 0:Fair 1:Maid, 2:with | 0:gold 1:on 2:her | 0:chin, | '
                   '0:O- 1:pen 2:you 2.5:the | 0:East 1:Door, 2:and | 0:let .5:the 1:New 2:Year | 0:in. 2:Sing')
alto2_words = fill(TUNE_ONSETS_23, STANZA[2]) + rows(
    '0:le- .5:vy 1:dew, 2:sing | 0:le- .5:vy 1:dew, 2:the | 0:wa- .5:ter 1:and 2:the | 0:wine; 2:The | '
    '0:sev- .5:en 1:bright 2:gold | 0:wires 2:and 2.5:the | 0:bu- .5:gles 1:that 2:do | 0:shine.')
low3_words = fill(TUNE_ONSETS_23, STANZA[3]) + rows(
    '0:le- .5:vy 1:dew, 2:sing | 0:le- .5:vy 1:dew, 2:the | 0:wa- .5:ter 1:and 2:the | 0:wine; 2:The | '
    '0:sev- .5:en 1:bright 2:gold | 0:wires 2:and 2.5:the | 0:bu- .5:gles 1:that 2:do | 0:shine.')
words = {
    'soprano': tune1 + tune2 + tune3 + descant,
    'alto': EMPTY + alto2_words + alto3_verse + rows(REFRAIN_WORDS),
    'tenor': EMPTY + EMPTY + low3_words,
    'bass': EMPTY + EMPTY + low3_words,
}
assert all(len(w) == 48 for w in words.values()), {v: len(w) for v, w in words.items()}
lyrics = {v: fit_lyrics(parts[v], words[v]) for v in parts}

# Printed systems: four bars each (stanza 1 on page 1; stanza 2 on pages 1–2; stanza 3 on pages 2–3).
H = 792
systems = crop_systems('a-new-year-carol', PDF, [(4, 95 / H, 148 / H), (4, 158 / H, 207 / H), (4, 216 / H, 267 / H),
                                               (4, 276 / H, 332 / H), (4, 392 / H, 507 / H), (4, 516 / H, 630 / H)],
                       page=0, x=(.09, .91))
systems += crop_systems('a-new-year-carol', PDF, [(4, 70 / H, 170 / H), (4, 180 / H, 285 / H), (4, 345 / H, 524 / H),
                                                (4, 534 / H, 691 / H)], page=1, x=(.09, .91), first=21, start_index=6)
systems += crop_systems('a-new-year-carol', PDF, [(4, 70 / H, 222 / H), (4, 232 / H, 393 / H)],
                        page=2, x=(.09, .91), first=37, start_index=10)
# crop_systems numbers bars by printed position; the data numbers the sung bars in order.
for index, system in enumerate(systems):
    system['first_measure'] = 1 + 4 * index

song = {
    'id': 'a-new-year-carol', 'title': 'A New Year Carol', 'emoji': '🎆',
    'composer': 'the composer; words anon.', 'arranger': 'choir version supplied by the user',
    'meter': [3, 4], 'key_fifths': -3, 'tempo': 92,
    'source_pdf': PDF,
    'sources': [{'description': 'Three pages of scan excerpts supplied by the user: stanza 1 sopranos; stanza 2 sopranos and altos; stanza 3 sopranos, altos, tenors and basses (“prima riga soprani, seconda contralti, terza tenori+bassi”). It replaces the unison + piano edition used before.'}],
    'review_notes': [
        'Sung a cappella: no piano or organ; the bars of rest after stanzas 1 and 2 are left out, so the three 16-bar stanzas follow each other (bars 1–16, 17–32, 33–48).',
        'Stanza 1: sopranos alone. Stanza 2: sopranos (tune) and altos (second line, often crossing above). Stanza 3: sopranos tune then a descant in the refrain (B♭4–G5 in long notes, “le- … vy dew, the bu- … gles that do shine”), altos the tune in the refrain, tenors and basses in unison an octave below the printed treble-clef line.',
        'Read by eye from small, uneven scan crops (about 10 px between staff lines): every head was checked against the staff lines next to it. Least certain: alto bar 18 and 34 “with” (A♭4, not G4), alto bar 36 “chin” (F4), stanza 3 low line bar 44 “The” (C5 printed) and bar 47 “do” (B♭3 printed, below a ledger line), alto bar 43 “the” (B♭4).',
        'Stanzas 2–3 sopranos sing “with” on one quarter (stanza 1 “from the” has two eighths). Stanza 3 altos sing “gold on her chin” (no “up-”) and “O- pen” on two quarters.',
        'Pencil marks on the scan (breaths, brackets) are not transcribed; the final fermata is not encoded. Tempo quarter = 92 (“Quietly”).',
    ],
    'parts': parts, 'playback': [{'measure': m} for m in range(1, 49)],
    'sections': [{'at': [m, 0], 'name': name} for m, name in
                 ((1, 'verse'), (9, 'chorus'), (17, 'verse'), (25, 'chorus'), (33, 'verse'), (41, 'chorus'))],
    'systems': systems,
    'verses': [{'number': 1, 'title': 'Brano intero', 'lyrics': lyrics}],
    'staff_bands': {'soprano': [0, .34], 'alto': [.33, .67], 'tenor': [.66, 1], 'bass': [.66, 1]},
    'compact': {'instructions': 'Strofa 1 soprani; strofa 2 soprani e contralti; strofa 3 tutti (tenori e bassi all’unisono, un’ottava sotto il rigo in chiave di violino).'},
}

save_song(song)
