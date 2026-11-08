"""Build data/joy-to-the-world.json from the clean reference page 2 (same edition as the scan).
Pitches from vector_heads.py; rhythms and lyric positions from the page (word x positions)."""
from song_kit import crop_systems, fit_lyrics, save_song

parts = {
 'soprano': ['D5:2 C#5:1.5 B4:0.5', 'A4:3 G4:1', 'F#4:2 E4:2', 'D4:2 R:1 A4:1', 'B4:3 B4:1', 'C#5:3 C#5:1', 'D5:4~',
             'D5:2 R:1 D5:1', 'D5:1 C#5:1 B4:1 A4:1', 'A4:1.5 G4:0.5 F#4:1 D5:1', 'D5:1 C#5:1 B4:1 A4:1', 'A4:1.5 G4:0.5 F#4:1 F#4:1',
             'F#4:1 F#4:1 F#4:1 F#4:0.5 G4:0.5', 'A4:2 R:1 G4:0.5 F#4:0.5', 'E4:1 E4:1 E4:1 E4:0.5 F#4:0.5',
             'G4:2 R:1 F#4:0.5 E4:0.5', 'D4:1 D5:2 B4:1', 'A4:1.5 G4:0.5 F#4:1 G4:1', 'F#4:2 E4:2', 'D4:2 R:2'],
 'alto':    ['F#4:2 A4:1.5 G4:0.5', 'F#4:3 E4:1', 'D4:2 C#4:2', 'D4:2 R:1 D4:1', 'G4:3 G4:1', 'E4:3 E4:1', 'F#4:4~',
             'F#4:2 R:1 F#4:1', 'F#4:1 A4:1 G4:1 F#4:1', 'F#4:1.5 E4:0.5 D4:1 F#4:1', 'F#4:1 A4:1 G4:1 F#4:1', 'F#4:1.5 E4:0.5 D4:1 D4:1',
             'D4:1 D4:1 D4:1 D4:0.5 E4:0.5', 'F#4:2 R:1 E4:0.5 D4:0.5', 'C#4:1 C#4:1 C#4:1 C#4:0.5 D4:0.5',
             'E4:2 R:1 D4:0.5 C#4:0.5', 'D4:1 F#4:2 G4:1', 'F#4:1.5 E4:0.5 D4:1 E4:1', 'D4:2 C#4:2', 'D4:2 R:2'],
 'tenor':   ['A3:2 D4:1.5 D4:0.5', 'D4:3 B3:1', 'A3:3 G3:1', 'F#3:2 R:1 D4:1', 'D4:3 D4:1', 'A3:3 A3:1', 'A3:4~',
             'A3:2 R:1 A3:1', 'A3:2 D4:2', 'D4:3 A3:1', 'A3:2 D4:2', 'D4:3 R:1',
             'R:3 A3:1', 'A3:1 A3:1 A3:1 A3:1', 'A3:4~', 'A3:2 R:1 A3:0.5 G3:0.5', 'F#3:1 A3:2 D4:1', 'D4:3 B3:1', 'A3:2 A3:1 G3:1', 'F#3:2 R:2'],
 'bass':    ['D3:2 D3:1.5 D3:0.5', 'D3:3 G2:1', 'A2:2 A2:2', 'D3:2 R:1 F#3:1', 'G3:3 G3:1', 'A3:3 A3:1', 'D3:4~',
             'D3:2 R:1 D3:1', 'D3:2 D3:2', 'D3:3 D3:1', 'D3:2 D3:2', 'D3:3 R:1',
             'R:3 D3:1', 'D3:1 D3:1 D3:1 D3:1', 'A3:3 A2:1', 'A2:1 A2:1 A2:1 A2:1', 'D3:3 D3:1', 'D3:3 G2:1', 'A2:2 A2:2', 'D3:2 R:2'],
}
upper = [
 ['0:Joy 2:to 3.5:the', '0:world! 3:The', '0:Lord 2:is', '0:come. 3:Let', '0:earth 3:re-', '0:ceive 3:her', '0:King.', '3:Let',
  '0:ev- 2:’ry', '0:heart 3:pre-', '0:pare 2:Him', '0:room, 3:and', '0:heav’n 1:and 2:na- 3:ture', '0:sing, 3:and',
  '0:heav’n 1:and 2:na- 3:ture', '0:sing, 3:and', '0:hea- 1:ven 3:and', '0:hea- 2:ven 3:and', '0:na- 2:ture', '0:sing.'],
 ['0:Joy 2:to 3.5:the', '0:earth! 3:The', '0:Sav- 2:iour', '0:reigns. 3:Let', '0:men 3:their', '0:songs 3:em-', '0:ploy', '3:while',
  '0:fields 2:and', '0:floods, 3:rocks,', '0:hills 2:and', '0:plains 3:re-', '0:peat 1:the 2:sound- 3:ing', '0:joy, 3:re-',
  '0:peat 1:the 2:sound- 3:ing', '0:joy, 3:re-', '0:peat, 3:re-', '0:peat 3:the', '0:sound- 2:ing', '0:joy.'],
 ['0:He 2:rules 3.5:the', '0:world 3:with', '0:truth 2:and', '0:grace 3:and', '0:makes 3:the', '0:na- 3:tions', '0:prove', '3:the',
  '0:glo- 2:ries', '0:of 3:His', '0:right- 2:eous-', '0:ness 3:and', '0:won- 1:ders 2:of 3:His', '0:love, 3:and',
  '0:won- 1:ders 2:of 3:His', '0:love, 3:and', '0:won- 3:ders,', '0:won- 3:ders', '0:of 2:His', '0:love.'],
]
# Staggered lower entries (printed under the bass staff, measures 13–17).
lower = [dict(enter='and', words='heav’n and na- ture', end='sing', again='and'),
         dict(enter='re-', words='peat the sound- ing', end='joy', again='re-'),
         dict(enter='and', words='won- ders of His', end='love', again='and')]

verses = []
for number, rows in enumerate(upper, 1):
    low = lower[number-1]; words = ' '.join(f'{i}:{w}' for i, w in enumerate(low['words'].split()))
    tenor = rows[:11] + ['0:' + rows[11].split()[0].split(':')[1], f"3:{low['enter']}", words, f"0:{low['end']}", rows[15].split()[-1]] + rows[16:]
    bass = rows[:11] + ['0:' + rows[11].split()[0].split(':')[1], f"3:{low['enter']}", words, f"0:{low['end']} 3:{low['again']}", words] \
        + [f"0:{low['end']} {rows[16].split()[-1]}"] + rows[17:]
    tenor[2] = rows[2].replace('2:', '3:')  # the tenor's "is"/"iour"/"and" falls on its quarter on beat 4
    verses.append(dict(number=number, title=f'Strofa {number}',
                       lyrics={'soprano': rows, 'alto': rows, 'tenor': fit_lyrics(parts['tenor'], tenor), 'bass': fit_lyrics(parts['bass'], bass)}))

systems = crop_systems('joy-to-the-world', 'songs/Joy to the World.pdf',
                       [(7, .15, .32), (5, .345, .5), (3, .52, .69), (5, .70, .87)], x=(.08, .9))

song = dict(id='joy-to-the-world', title='Joy to the World', emoji='🌍', composer='Tune Antioch, George Frederick the composer; words the author, alt.',
  arranger='the arranger (adapt. & arr.)', meter=[2, 2], key_fifths=2, tempo=185, source_pdf='songs/Joy to the World.pdf',
  review_notes=['Pitches read from the vector notehead positions of the clean copy of the same edition; rhythms, rests and lyric positions from that page and compared with the scan.',
    'Tenor and bass rest at the end of measure 12 and enter staggered (“and heav’n and nature sing”), with their own printed words in measures 13–17. The tenor holds A3 through measure 15 and rejoins the upper words on the eighths of measure 16; the bass rejoins at measure 17 beat 4.',
    'Where a lower part has fewer notes than the shared words (tenor measure 3, measure 18) the syllables are joined or moved to the part’s own onset. Stanza 3 measure 17 beat 4 (“ders,”) is the printed upper text; the print gives the bass no separate word there.',
    'Handwritten notes on the scan (key/transposition remarks, dynamics, part allocation) are not transcribed. Played in 2/2 with quarter-note beats; default tempo quarter = 185 (half ≈ 92).'],
  review_notes_it=['Altezze dalla copia vettoriale pulita della stessa edizione; ritmi, pause e posizione delle sillabe da quella pagina, confrontati con la scansione.',
    'Tenori e bassi tacciono a fine b. 12 ed entrano sfalsati con parole proprie (bb. 13–17).',
    'Le annotazioni a mano sulla scansione (tonalità, dinamiche, divisione delle parti) non sono trascritte.'],
  parts=parts, playback=[{'measure': i+1} for i in range(20)], systems=systems, verses=verses,
  staff_bands={'soprano': [0, .5], 'alto': [0, .5], 'tenor': [.5, 1], 'bass': [.5, 1]}, shared_lyrics=True,
  compact=dict(voice_lyrics={'bass': [13, 17]},
    instructions='Strofe 1–3 sulle righe numerate; tenori e bassi entrano sfalsati con le parole sotto il basso.'))
save_song(song)
