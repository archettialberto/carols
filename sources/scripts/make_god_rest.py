"""Build data/god-rest-ye-merry.json. Pitches/accidentals from vector_heads.py on the clean
reference page (songs/reference-pages.pdf, page 1; local only), rhythms and dashed
(verse-specific) ties read from that page; matched against songs/God Rest Ye Merry.pdf."""
from song_kit import crop_systems, even, save_song

parts = {
 'soprano': ['D4:1', 'D4:1 A4:1 A4:1 G4:1', 'F4:1 E4:1 D4:1 C4:1', 'D4:1 E4:1 F4:1 G4:1', 'A4:2 R:1 D4:1',
             'D4:1 A4:1 A4:1 G4:1', 'F4:1 E4:1 D4:1 C4:1', 'D4:1 E4:1 F4:1 G4:1', 'A4:2 R:1 A4:1',
             'Bb4:1 G4:1 A4:1 Bb4:1', 'C5:1 D5:1 A4:1 G4:1', 'F4:1 D4:1 E4:1 F4:1', 'G4:2 F4:1 G4:1',
             'A4:2 Bb4:1 A4:1', 'A4:1 G4:1 F4:1 E4:1', 'D4:2 F4:0.5 E4:0.5 D4:1', 'G4:2 F4:1 G4:1',
             'A4:1 Bb4:1 C5:1 D5:1', 'A4:1 G4:1 F4:1 E4:1', 'D4:4'],
 'alto':    ['D4:1', 'D4:1 F4:1 E4:1 C#4:1', 'D4:1 C4:1 Bb3:1 A3:1', 'D4:1 C#4:1 D4:1 D4:1', 'C#4:2 R:1 D4:1',
             'D4:1 F4:1 E4:1 C#4:1', 'D4:1 C4:1 Bb3:1 A3:1', 'D4:1 C#4:1 D4:1 D4:1', 'C#4:2 R:1 D4:1',
             'D4:1 C4:1 C4:1 F4:1', 'Eb4:1 D4:1 C4:1 C#4:1', 'D4:1 B3:1 C4:1 F4:1', 'E4:2 F4:1 C4:1',
             'C4:2 D4:1 C4:1', 'F4:1 E4:1 D4:1 C#4:1', 'D4:2 A3:0.5 A3:0.5 B3:1', 'C4:2 D4:1 E4:1',
             'F4:2 F4:1 F4:1', 'F4:1 E4:1 D4:1 C#4:1', 'D4:4'],
 'tenor':   ['D3:1', 'F3:1 D3:1 E3:1 A3:1', 'A3:1 A3:1 F3:1 F3:1', 'F3:1 A3:1 A3:1 D3:1', 'E3:2 R:1 D3:1',
             'F3:1 D3:1 E3:1 A3:1', 'A3:1~ A3:1 F3:1 F3:1', 'F3:1 A3:1 A3:1 D3:1', 'E3:2 R:1 F#3:1',
             'G3:1 G3:1 F3:1 F3:1', 'F3:1 F3:1 F3:1 E3:1', 'F3:1 F3:1 G3:1 C4:1', 'C4:1 Bb3:1 A3:1 G3:1',
             'F3:2 F3:1 F3:1', 'C4:1 Bb3:1 A3:1 A3:1', 'F3:2 F3:0.5 F3:0.5 F3:1', 'E3:1 G3:1 C4:1 Bb3:1',
             'A3:1 F3:1 C4:1 Bb3:1', 'C4:1 Bb3:1 A3:1 A3:1', 'F3:4'],
 'bass':    ['D3:1', 'D3:1 D3:1 C#3:1 A2:1', 'D3:1 A2:1 Bb2:1 F2:1', 'Bb2:1 A2:1 D3:1 Bb2:1', 'A2:2 R:1 D3:1',
             'D3:1 D3:1 C#3:1 A2:1', 'D3:1 A2:1 Bb2:1 F2:1', 'Bb2:1 A2:1 D3:1 Bb2:1', 'A2:2 R:1 D3:1',
             'G3:1 E3:1 F3:1 D3:1', 'A2:1 Bb2:1 F2:1 A2:1', 'D3:1 D3:1 C3:1 A2:1', 'C3:2 D3:1 E3:1',
             'F3:2 Bb2:1 F3:1', 'F2:1 G2:1 A2:1 A2:1', 'D3:2 D3:0.5 D3:0.5 D3:1', 'C3:1 Bb2:1 A2:1 G2:1',
             'F2:1 D3:1 A2:1 Bb2:1', 'F2:1 G2:1 A2:1 A2:1', 'D3:4'],
}
refrain = ['ti- 2:dings 3:of', 'com- 2:fort 3:and', 'joy, 2:com- 2.5:fort 3:and', 'joy, 2:O',
           'ti- 2:dings 3:of', 'com- 2:fort 3:and', 'joy!']
verses_text = [
 ['God', 'rest ye mer- ry,', 'gen- tle- men, let', 'noth- ing you dis-', '0:may, 3:re-', 'mem- ber Christ our',
  '0:Sav- 2:iour 3:was', 'born on Christ- mas', '0:day 3:to', 'save us all from', 'Sa- tan’s power when',
  'we were gone a-', '0:stray. 2:O'],
 ['From', 'God, our heav’n- ly', '0:fa- 2:ther, 3:a', 'bles- sed an- gel', '0:came, 3:and', 'un- to cer- tain',
  '0:shep- 2:herds 3:brought', 'ti- dings of the', '0:same: 3:how', 'that in Beth- le-', 'hem was born the',
  'Son of God by', '0:name. 2:O'],
 ['“Fear', 'not, then” said the', '0:an- 2:gel, 3:“Let', 'noth- ing you af-', '0:fright. 3:This', 'day is born a',
  '0:Sav- 2:iour 3:of', 'a pure vir- gin', '0:bright 3:to', 'free all those who', 'trust in Him from',
  'Sa- tan’s pow’r and', '0:might. 2:O'],
 ['Now', 'to the Lord sing', '0:prais- 2:es, 3:all', 'you with- in this', '0:place, 3:and', 'with true love and',
  'broth- er- hood each', 'oth- er now em-', '0:brace. 3:This', 'ho- ly tide of', '0:Christ- 2:mas 3:doth',
  'bring re- deem- ing', '0:grace. 2:O'],
]
verses = []
for number, rows in enumerate(verses_text, 1):
    lines = [row if ':' in row else even(row) for row in rows] + ['0:' + r for r in refrain]
    verse = dict(number=number, title=f'Strofa {number}', lyrics={'all': lines})
    # Dashed ties in the print apply only to stanzas with fewer syllables there.
    overrides = {}
    if number > 1: overrides['3'] = 'A3:1~ A3:1 F3:1 F3:1'
    if number == 4: overrides['7'] = 'A3:1 A3:1 F3:1 F3:1'
    if number == 4: overrides['11'] = 'F3:1~ F3:1 F3:1 E3:1'
    if overrides: verse['parts'] = {'tenor': overrides}
    verses.append(verse)

systems = crop_systems('god-rest-ye-merry', 'songs/God Rest Ye Merry.pdf',
                       [(5, .165, .305), (5, .345, .485), (5, .51, .645), (5, .685, .81)], x=(.07, .88))

song = dict(id='god-rest-ye-merry', title='God Rest Ye Merry, Gentlemen', emoji='🎩', composer='Traditional English',
  arranger='the arranger', meter=[4, 4], key_fifths=-1, tempo=140,
  source_pdf='songs/God Rest Ye Merry.pdf',
  review_notes=['Pitches and accidentals read from the vector notehead positions of the clean copy of the same edition; rhythms, ties and slurs read from that page and compared with the scan.',
    'Dashed curves: tenor ties in measure 3 (stanzas 2–4), 7 (stanzas 1–3) and 11 (stanza 4) are encoded as verse-specific ties; the other dashed curves join different pitches and are phrase slurs (melismas for those stanzas).',
    'The refrain from “O tidings” (measure 13, beat 3) is common to all stanzas.',
    'Handwritten notes on the scan (“Scritta in Re, da fare in Mi”, unison/part allocation, stanza assignments) are not transcribed. Playback is at printed pitch.'],
  review_notes_it=['Altezze e alterazioni dalla copia vettoriale pulita della stessa edizione; ritmi e legature letti su quella pagina e confrontati con la scansione.',
    'Legature tratteggiate del tenore solo per alcune strofe (b. 3 strofe 2–4, b. 7 strofe 1–3, b. 11 strofa 4); le altre curve tratteggiate sono legature di frase.',
    'Le note a mano sulla scansione (“Scritta in Re, da fare in Mi”, ecc.) non sono trascritte: la riproduzione è all’altezza stampata.'],
  parts=parts, playback=[{'measure': i+1} for i in range(20)], systems=systems, verses=verses,
  sections=[{'at': [13, 2], 'name': 'chorus'}],
  staff_bands={'soprano': [0, .5], 'alto': [0, .5], 'tenor': [.5, 1], 'bass': [.5, 1]},
  measure_beats=[1] + [4]*19, shared_lyrics=True,
  compact=dict(refrain_measures=[14, 20], merge_refrain_systems=False, refrain_pickup_measures=[13],
    annotations=[{'measure': 13, 'voice': 'soprano', 'beat': 2, 'text': 'Ritornello'}],
    instructions='Strofe 1–4 sulle righe numerate; il ritornello “O tidings” è comune.'))
save_song(song)
