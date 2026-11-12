"""Build Away in a Manger (Cradle Song) from the supplied vector score."""
from song_kit import crop_systems, fit_lyrics, save_song

parts = {
    'soprano': [
        'C4:1', 'F4:1 F4:1 G4:0.5 A4:0.5', 'F4:1 F4:1 A4:0.5 Bb4:0.5',
        'C5:1 C5:1 D5:1', 'Bb4:2 G4:0.5 A4:0.5', 'Bb4:1 Bb4:1 C5:1',
        'A4:1 A4:1 F4:0.5 A4:0.5', 'G4:1 D4:1 F4:1', 'E4:2 C4:1',
        'F4:1 F4:1 G4:0.5 A4:0.5', 'F4:1 F4:1 A4:0.5 Bb4:0.5',
        'C5:1 C5:1 D5:1', 'Bb4:2 G4:0.5 A4:0.5',
        'Bb4:1 Bb4:1 C5:1', 'A4:1 A4:1 F4:0.5 A4:0.5',
        'G4:1 D4:1 E4:1', 'F4:2',
    ],
    'alto': [
        'C4:1', 'C4:1 C4:1 C4:1', 'C4:1 C4:1 F4:1', 'F4:1 F4:1 F4:1',
        'D4:2 G4:1', 'G4:1.5 F4:0.5 E4:1', 'F4:1 F4:1 F4:1',
        'D4:1 D4:1 B3:1', 'C4:2 C4:1', 'C4:1 C4:1 C4:1',
        'C4:1 C4:1 F4:1', 'E4:1 E4:1 F#4:1', 'D4:2 G4:1',
        'G4:1.5 F4:0.5 E4:1', 'F4:1 F4:1 F4:1',
        'D4:1 D4:1 C4:0.5 Bb3:0.5', 'A3:2',
    ],
    'tenor': [
        'C4:1', 'A3:1 A3:1 Bb3:0.5 C4:0.5', 'A3:1 A3:1 C4:1',
        'C4:1 C4:1 A3:1', 'Bb3:2 Bb3:0.5 C4:0.5', 'D4:1 D4:1 C4:1',
        'C4:1 C4:1 A3:0.5 C4:0.5', 'B3:1 B3:1 G3:1',
        'G3:2 C4:0.5 Bb3:0.5', 'A3:1 A3:1 Bb3:0.5 C4:0.5',
        'A3:1 A3:1 C4:1', 'C4:1 C4:1 A3:1', 'Bb3:2 Bb3:0.5 C4:0.5',
        'D4:1 D4:1 C4:1', 'C4:1 C4:1 C4:1',
        'Bb3:1.5 A3:0.5 G3:1', 'F3:2',
    ],
    'bass': [
        'C3:1', 'F3:1 F3:1 F3:1', 'F3:1 F3:1 F3:0.5 G3:0.5',
        'A3:1 A3:1 D3:1', 'G3:2 G3:1', 'G3:1 G3:1 C3:1',
        'F3:1 F3:1 F3:1', 'G3:1 G3:1 G2:1', 'C3:2 C3:1',
        'F3:1 F3:1 F3:1', 'F3:1 F3:1 F3:0.5 G3:0.5', 'A3:1 A3:1 D3:1',
        'G3:2 G3:1', 'G3:1 G3:1 C3:1', 'F3:1 F3:1 A2:1',
        'Bb2:1 Bb2:1 C3:1', 'F2:2',
    ],
}

rows = [
    ['0:A', '0:way 1:in 2:a', '0:man- 1:ger, 2:no', '0:crib 1:for 2:a',
     '0:bed, 2:The', '0:lit- 1:tle 2:Lord', '0:Je- 1:sus 2:laid',
     '0:down 1:His 2:sweet', '0:head. 2:The', '0:stars 1:in 2:the',
     '0:sky 2:looked', '0:down 1:where 2:He', '0:lay, 2:The',
     '0:lit- 1:tle 2:Lord', '0:Je- 1:sus, 2:a-', '0:sleep 1:on 2:the', '0:hay.'],
    ['0:The', '0:cat- 1:tle 2:are', '0:low- 1:ing, 2:the', '0:Ba- 1:by 2:a-',
     '0:wakes, 2:But', '0:lit- 1:tle 2:Lord', '0:Je- 1:sus, 2:no',
     '0:cry- 1:ing 2:He', '0:makes; 2:I', '0:love 1:Thee, 2:Lord',
     '0:Je- 1:sus, 2:look', '0:down 1:from 2:the', '0:sky 2:And',
     '0:stay 1:by 2:my', '0:cra- 1:dle 2:til', '0:morn- 1:ing 2:is', '0:nigh.'],
    ['0:Be', '0:near 1:me, 2:Lord', '0:Je- 1:sus, 2:I', '0:ask 1:Thee 2:to',
     '0:stay 2:Close', '0:by 1:me 2:for-', '0:ev- 1:er, 2:and',
     '0:love 1:me, 2:I', '0:pray; 2:Bless', '0:all 1:the 2:dear',
     '0:chil- 1:dren 2:in', '0:Thy 1:ten- 2:der', '0:care, 2:And',
     '0:fit 1:us 2:for', '0:heav- 1:en 2:to', '0:live 1:with 2:Thee', '0:there.'],
]

verses = []
for number, row in enumerate(rows, 1):
    verses.append({'number': number, 'title': f'Strofa {number}',
                    'lyrics': {voice: fit_lyrics(parts[voice], row) for voice in parts}})

systems = crop_systems('away-in-a-manger-cradle-song',
                       'songs/Away in a Manger - Cradle Song.pdf',
                       [(5, .10, .30), (4, .31, .51), (4, .51, .72), (4, .72, .94)],
                       x=(.045, .955))

song = {
    'id': 'away-in-a-manger-cradle-song', 'title': 'Away in a Manger', 'emoji': '🐂',
    'composer': 'the composer', 'arranger': 'an online edition',
    'meter': [3, 4], 'key_fifths': -1, 'tempo': 84,
    'measure_beats': [1] + [3] * 15 + [2],
    'source_pdf': 'songs/Away in a Manger - Cradle Song.pdf',
    'sources': [{'description': 'Supplied one-page vector PDF (online edition, Sibelius/Opus); the exact printed arrangement is the transcription source.'}],
    'review_notes': [
        'Pitches were read from the embedded Opus note glyph positions (sources/scripts/vector_heads.py) and checked visually against all four printed systems.',
        'Measure 8 tenor: the printed natural on B3 carries through the bar, so both tenor B3s are B natural (G major to G7).',
        'The opening pickup is stored as measure 1; printed bar 13 therefore corresponds to data measure 14. Tenor pitches are sounding pitch.',
        'All three printed stanzas are encoded. Where an inner voice sustains across two printed syllables, its lyric cue joins those syllables instead of inventing a rearticulation.',
        'Phrase slurs over beamed notes are not encoded as ties. Practice tempo quarter = 84 is a suggested moderate lullaby tempo.',
    ],
    'review_notes_it': [
        'Altezze lette dai glifi vettoriali Opus e confrontate visivamente con tutti e quattro i sistemi.',
        'L’anacrusi iniziale è la misura dati 1; le legature di frase non sono legature di valore.',
    ],
    'parts': parts, 'playback': [{'measure': i} for i in range(1, 18)],
    'systems': systems, 'verses': verses,
    'staff_bands': {'soprano': [0, .5], 'alto': [0, .5], 'tenor': [.5, 1], 'bass': [.5, 1]},
    'shared_lyrics': True,
    'compact': {'instructions': 'Tre strofe numerate sulle stesse note; testo comune alle quattro voci.'},
}

save_song(song)
