# Processing record

Processed 8 November 2026; practice interface and lyric alignment updated subsequently. The two supplied files are image-only PDFs, with no
extractable notation or text layer. Original PDFs have not been changed.

## Approach

The canonical data is a readable JSON transcription of each printed measure,
with separate sounding S/A/T/B pitches, explicit accidentals, durations, rests,
and ties. MusicXML makes this portable to a notation editor; MIDI makes it
portable to audio software. All three playback paths share the same repeat and
tie interpretation. Scan crops and measure boundaries let the webapp follow the
exact supplied edition without introducing a notation-rendering dependency.

For these short scores, direct transcription was chosen. For longer future
scores, [Audiveris](https://github.com/Audiveris/audiveris) is a suitable source of
an initial MusicXML draft, followed by manual checking. Its
[handbook](https://audiveris.github.io/audiveris/_pages/handbook/) describes the
scan-to-MusicXML workflow. Automatic recognition is not part of this app.

The printed an online carol site credit on Nowell was checked online, but
that site could not be retrieved. Searches for the exact Jingle Bells arranger
did not supply a confirmed matching editable score. No different online
harmonization was substituted; the supplied scans remain the source.

## The First Nowell

- Source: `songs/The First Nowell.pdf`, one page, four systems.
- Printed credit: traditional English; harmony the arranger, altered;
  an online carol site.
- D major, 3/4. 25 source measures, counting the two initial beats of rest as
  part of measure 1. Four voices are separated from two shared staves.
- Tenor and bass use the printed bass-clef pitches directly. The exported
  separate tenor staff uses an octave treble clef without changing sounding pitch.
- All five printed verses and their refrains are available, individually or in
  sequence. Verse 2 rearticulates the tenor D4 in measure 15 for “tin-ued”.
  Practice tempo: quarter = 84 (was 96; online editions and recordings range about 80–96, and
  a slower, stately pace suits the carol). Soprano measures 15–16 were corrected to
  A4 B4 C#5 | D5 A4 G4 from the clean digital source (the same phrase as measures 7–8).
- Pencil alternatives, added notes, numbers, and rehearsal instructions were
  ignored. Printed phrase slurs with different pitches are not sustained ties.
- Visual review corrected the lower voice crossings in the closing refrain,
  especially measures 20–23.
- **Review status:** manual draft. The alto at measures 7–8 and the shared-staff
  voice crossings deserve an independent musical proofreading pass; pencil
  strokes obscure some printed stems. These are explicit review points, not a
  claim of a fully verified edition.

## Jingle Bells

- Source: `songs/Jingle Bells.pdf`, three pages, six systems.
- Printed credit: J. S. the composer; arranged by the arranger.
- G major, 2/4; 32 source measures; four separate SATB staves.
- The tenor's treble notation is interpreted at the conventional octave below,
  so the opening written D5 sounds D4. Alto and soprano sound as written.
- Single-verse playback is measures 1–32, then 1–16 (D.C. al Fine): 48 played measures.
  On that final return the parenthesized alto/tenor/bass pickup in measure 16
  becomes a rest, so the piece finishes rather than starting the verse again.
- All three printed verses are encoded, with separate soprano and lower-voice
  lyric timing, bass responses, and the laughter fill in measure 24. All-verses
  playback runs 1–32 for each verse, then one final 1–16 chorus: 112 measures.
  Only the final chorus suppresses the verse-entry pickup. Practice tempo: quarter = 112.
- Dotted phrase marks in the verse are not ties: repeated syllables/verse pickups
  rearticulate. The printed C-sharp in measure 7 is explicitly encoded, including
  its bass repetition. Highlighting on the bass staff was ignored.
- Visual review corrected soprano pitches in measures 21–24 and 28–32.
- **Review status:** manually transcribed and visually checked on all pages;
  still a draft without independent musical proofreading.

## Validation and limits

The automated checks verify all measure lengths, four-part alignment, pitches,
ties, measure-image coverage, and the final-return pickup behavior. Exports use
expanded playback order, so an editor does not need to interpret D.C. instructions.
MusicXML contains pitches, rhythms, and note-aligned lyric syllables for all
printed verses; MIDI contains the matching all-verses note sequence. Slurs and
printed dynamic markings remain visible in the source images.

An independent music21 parser was used during development to import both
MusicXML files and compare every sounding pitch, onset, duration, and merged tie
against playback data; both MIDI files also imported as four parts and matched
every sounding event, with key and time-signature metadata preserved. This verifies
format/export consistency, **not** the accuracy of a reading from the scan.

The player uses the Web Audio clock for note scheduling. Scan highlighting is
at measure/beat level, with linear interpolation inside each measure; it is not
an exact notehead cursor. The app has no runtime network dependencies.

Chromium smoke checks passed for both songs: audio scheduling, pause/resume,
voice solo, tempo changes, return navigation, clicking measures, end-of-score
silence, downloads, and a 390px mobile viewport. There were no browser script
errors. These checks exercise the player; they are not an auditory proofreading
of the harmonization. The original five standard-library unit tests passed; additional lyric and verse
checks and mobile browser checks are described below.


## Mobile practice and lyrics

The name remains **Christmas Carol Choir**. Italian is the default interface
language, English is optional, and the chosen language persists locally. The
sung text is transcribed from the supplied PDFs and remains English, including
the printed spellings and alternate verses. No online lyric edition was used.

Each verse stores explicit per-measure syllable onsets. Shared Nowell lyrics use
one map; Jingle uses separate maps because soprano enters a measure later than
alto/tenor/bass and the bass has extra responses. “Is-ra-” in Nowell's closing
phrase changes syllable on beat 2, with the intervening note a melisma. The verse
2 tenor articulation in measure 15 is recorded as an explicit rhythmic override.
The parenthesized introductory A is included for Jingle verses 1–2 and omitted
from verse 3; final-chorus pickups are silent. Bass laughter remains a fill rather
than an extra invented pickup syllable.

Lyrics and notes use one beat timeline: tempo changes, seek, pause, verse
selection and chorus returns cannot independently advance the text. Rests stop
syllable highlighting. The selected text voice can differ from the ensemble being
heard. Choosing a solo voice selects its text and crops to its printed staff.
The scan itself retains all printed stanza rows and annotations; the separate
lyric panel shows only the currently sung stanza.

The current system replaces page-length scrolling. Narrow screens keep a
readable horizontal score, follow its beat marker, and expose zoom, line
navigation, and fixed bottom transport controls. Playback initially focuses this
view on phones; the focus button restores the song and voice selectors. The full
scan overview is available in the options. Staff cropping uses the original
raster image and does not isolate individual notes on shared staves.

Updated validation: nine unit tests pass, including rejection of lyrics on rests,
all printed verse/chorus orders, the verse-specific tenor rhythm, and MusicXML
syllable coverage. The browser smoke suite passes at 320, 390, 768 and 1280px,
with Italian defaults, remembered English, independent lyric voice selection,
solo staff cropping, focus mode, verse switching, beat highlights, audio and
final silence. All-verses MusicXML and MIDI were independently reimported with
music21; every sounding note, onset, duration and tie matches the player data.
These checks do not replace musical proofreading of the original draft notes.


## Digital edition and vocal balance

The main score is now clean SVG notation engraved from the existing structured
pitches, durations, rests, ties and verse-specific syllables. SATB are separate
staves; tenor uses a treble clef sounding one octave below written pitch. Every
note is connected to its exact playback onset, including note-click seeking and
highlighting. The optional scan view and original PDFs remain available for
comparison. This engraving does not constitute independent musical proofreading;
all draft transcription review points above remain applicable.

The renderer is abcjs 6.7.2, bundled locally under its MIT license. ABC accidental
state is reset per measure and follows the key signature, with explicit natural,
sharp and flat changes only where needed. Actual SVG ink bounds are included to
avoid clipping final lyric syllables. The original structured data remains the
source of truth; no replacement online arrangement was used.

`exports/*-digital.html` are standalone offline printable editions containing
all verses and the local renderer. `exports/*-digital.pdf` are vector PDFs
rendered from those editions. A print-specific layout avoids absolute-positioned
SVG fragmentation; the original scans are not embedded in the digital editions.

All-vocal and solo presets now coexist with emphasis presets for each SATB voice.
The emphasized voice has gain 1, backing voices gain .22 (about 13 dB lower), and
the master level is normalized for the selected mix. Gain changes are smoothed;
all notes continue on the same clock so changing a mix neither restarts the song
nor truncates a newly unmuted sustained note.

The notation regression check reconstructs sounding notes from the engraved ABC
and compares all 2,731 sounding events across both songs' complete printed verses
with the performance data. It checks tenor octave, accidental state, rhythm,
merged ties, SVG anchors, click-to-play, solo/emphasis/ensemble gains, continuous
transport, mobile widths and the original-scan fallback.

Final checks: nine unit tests and both browser suites pass. The full browser suite
covers 320/390/768/1280px, themes, languages and stanza timing with digital notation
as the default. The notation suite validates all 2,731 sounding events and checks
that all SVG ink is within its viewBox. Both generated digital PDFs have eight
pages, retain searchable lyric text and were visually checked after correcting
print layout and final-syllable bounds. No scanned image is used in these PDFs.


## Simplified controls, attack notes and dark editions

The advanced-options section and duplicate scan overview were removed. The
interface now exposes only two direct downloads: generated PDF and original PDF.
The original supplied PDFs are unchanged. Source-image references and MusicXML,
MIDI and standalone HTML remain processing artifacts rather than extra controls.

The first-note control reads the selected voice's first non-rest performance
event, at sounding pitch. It does not follow the current measure or the muted
voice mix: an isolated 1.6-second tone sounds directly, pauses normal playback
without seeking, and is cancelled by stopping, switching songs/voices or starting
normal playback. Italian display names use Do/Re/Mi/Fa/Sol/La/Si.

The on-screen SVG now uses theme-aware paper, ink and note highlight colors.
The printable HTML adapts to device appearance. The PDF generator writes both
light and dark editions for each song; the site's generated-PDF link switches
with its resolved theme, including live device changes. Page margins are dark in
the dark PDF, and text remains searchable. The original PDF download is never
modified or recolored.

Validation covers all eight vocal attack pitches across the two songs, initial
rests, muted-voice previews, cancellation, natural release and unchanged transport
position. The responsive browser suite passes at 320/390/768/1280px with no
advanced sections, two PDF links, language switching, light/dark/device themes,
existing stanza synchronization and audio controls. Nine unit tests also pass.


## Compact stanza PDFs

Digital PDF/HTML now engrave each original measure once: 25 for The First Nowell
and 32 for Jingle Bells. Numbered lyric rows share the same note positions, while
the common refrain is printed once. Playback and existing MusicXML/MIDI retain
their unfolded verse sequences.

Nowell's five lyric rows appear once below soprano, with a note that the text is
common to SATB. Its refrain is combined into one system after the verse systems.
The verse 2 tenor articulation in measure 15 is shown on a shared grid: the base
D4 half note is engraved as tied quarters, with a star/footnote explaining that
verse 2 rearticulates them. The other verses retain the original sustained sound.

Jingle keeps the original 32-measure structure, a single chorus, and three
numbered lyric rows per voice in the verse section. The staggered soprano/lower
voice entries and bass responses remain individually aligned. Fine and D.C. al
Fine are printed, with directions to use the next stanza on each pass and omit
the optional pickup when finishing.

ABC stanza numbers are attached to the first sung syllable with a nonbreaking
space. Treating a number as a separate lyric token would shift all later words;
the notation regression test now checks every printed syllable against its note,
including the final word of each system. Printed notes are also checked against
the base verse's sounding pitches, durations and ties.


Final compact-edition checks: 13 unit tests pass. The notation suite verifies all
669 sounding events on the compact note grids, each SVG note/rest anchor, every
printed stanza syllable and the live player's click/mix controls. A nonbreaking
blank lyric cell avoids abcjs consuming a leading skip at a rest, preserving the
later soprano entrance in Jingle verse 3. All four PDF variants were regenerated;
Nowell has two pages and Jingle three. The base performance data was unchanged.


## Clean PDF pages and footers

Printed credits, product text, review disclaimer, stanza headings and repeated
system captions were removed from the digital PDF/HTML body. Attribution and
transcription-review notes remain in the structured song data and this record.
Musical annotations and the tenor articulation/final-pickup footnotes are retained.

The printable HTML now explicitly paginates intact musical systems at the physical
A4 content width and height before printing. Each page has a small footer with
song title, page/total and the actual source-measure range on that page. The footer
uses the same theme colors as the score. Nowell's two pages cover 1–12 and 13–25;
Jingle's three pages cover 1–16, 17–27 and 28–32. Both light/dark PDFs were checked
for physical page counts, footer placement and removal of boilerplate. The
notation regression test checks footer ranges as well as notes and sung syllables.


## Away in a Manger · the composer

- Source: `songs/Away in a Manger.pdf`, page 1 (page 2 is a different tune, Cradle Song,
  to be catalogued as a separate song). The PDF is vector, not a scan: noteheads and lyric
  text were read from the drawn symbols and their staff positions, so pitches are exact.
- Printed credits are omitted (internal copy);
  tune of the 1887 setting. F major, 3/4, quarter-note pickup and a two-beat final measure
  (17 source measures). Two shared staves; all three printed stanzas are encoded with
  common SATB timing (`shared_lyrics`), so the words are printed once under soprano.
- Practice tempo: quarter = 90. Rhythms were assigned from the printed pattern and checked
  against page 1; exports and light/dark digital PDFs were generated in this session.
- **Review status:** exact pitches from vector data; rhythm/lyric alignment visually checked,
  not independently proofread.


## Data-driven form, sounds, phone layout and installable app

Form is now described in each song file instead of the code: `playback` (one stanza),
`final_playback` with `silence_last` (Jingle's D.C. al Fine and silent final pickup),
`sections` (the Nowell refrain starts at measure 17 beat 2; Jingle's chorus is 1–16) and a
`compact` block for the printed edition. Jingle and Nowell were migrated; their playback,
lyrics, PDFs and all 846 engraved sounding events are unchanged according to the regression
suites. Sounding events now carry their syllable for the experimental sung-vowel mode.

The dark digital PDF existed and was correct; the light download was most likely a cached
older `player.js`. The server now sends `Cache-Control: no-cache`, and the link names the
theme (*chiaro*/*scuro*) and the downloaded file.

The starting-note selector became four piano-like keys (tap = 1.6 s cue, hold = sustain,
multi-touch = chord), independent of the mix. `web/sounds.js` synthesizes six instruments
with Web Audio. Syllable singing: vowels are feasible with formant filters; intelligible
consonants and words are not, without a real singing synthesizer (e.g. offline rendering with
an external singing-voice synthesis tool to audio files). The mode is therefore labelled
experimental.

The phone layout replaces permanent selectors with a settings sheet and a one-line selection
summary; the score shrinks (to at most 80%) to fit the screen height. At 390×664 the score,
lyrics and controls fit without scrolling; at 320×568 the lyrics fit once Play enters focus view.
The app is installable (manifest, icons drawn for this project as SVG, iOS meta tags,
network-first service worker on localhost/HTTPS). Titles use IM Fell English (SIL OFL,
`web/fonts/OFL.txt`).

Housekeeping: duplicate copies of the Jingle/Nowell scans and an old downloaded export were
removed from `songs/`; clean reference pages and Audiveris drafts were moved from temporary
storage into `sources/`. Validation: 15 unit tests; browser, notation and starting-note suites pass.


## Away in a Manger · Cradle Song, God Rest Ye Merry, Joy to the World

All three were transcribed from vector sources, so every pitch comes from an exact notehead
position (`sources/scripts/vector_heads.py`), while rhythms, ties, rests and lyric placement were
read from the page and checked against the user's scan. Generator scripts in `sources/scripts/`
(`make_cradle_song.py`, `make_god_rest.py`, `make_joy.py`) record every reading.

- **Cradle Song** (`songs/Away in a Manger.pdf`, page 2; the composer, 1895). F major, 3/4,
  pickup + 16 measures, three stanzas, quarter = 84. The measure 2 alto is overfull as printed
  (dotted half C4 plus D4/C4 eighths on the soprano stem): all printed heads sound. Single
  heads with one stem are unisons (pickup T/B C3, measure 7 T/B eighths).
- **God Rest Ye Merry, Gentlemen** (harm. the arranger as printed). Primary source: the
  clean vector copy of the identical an online carol site page (`songs/reference-pages.pdf`,
  page 1). D minor, 4/4, pickup + 19 measures, four stanzas, common refrain “O tidings” from
  measure 13 beat 3, quarter = 140. Dashed tenor ties apply only to some stanzas (m. 3: 2–4;
  m. 7: 1–3; m. 11: 4) and are verse-specific `parts`; other dashed curves are slurs.
- **Joy to the World** (Antioch, arr. the arranger). Clean copy page 2. D major, 2/2 (played in
  quarter beats, quarter = 180, i.e. half = 90; slowed from 185 — hymn-playing guides give 76–96 per beat for Antioch), 20 measures, three stanzas. Tenor and bass rest at the end of
  measure 12 and enter staggered with their own words (measures 13–17), so lyrics are per voice;
  the printed PDF shows the bass words only there (`compact.voice_lyrics`).

Handwritten remarks on the God Rest and Joy scans (transposition such as “Scritta in Re, da fare
in Mi”, dynamics, part allocation) are not transcribed; playback is at printed pitch. Exports and
light/dark digital PDFs were generated and visually compared with the clean pages. 15 unit tests
and the browser/notation suites pass; the starting-note suite can fail intermittently in headless
Chromium under WSL because the Web Audio clock stalls there (rerun passes).


## Transposition and static hosting

A transposition control (±6 semitones) shifts audio, the starting-note keys and the engraving
(abcjs `visualTranspose`); it resets to the printed key on every song change. The player now
fetches only relative static paths, which `app.py` serves live and `tools/build_static.py` writes
for GitHub Pages. The static build was checked from a sub-folder URL with a plain file server:
six songs, verse switching and both PDF downloads load without errors.


## Simplified practice controls and private scans

Downloads are now a single light digital PDF (dark PDFs are no longer generated); original
scans are neither offered nor served, and `songs/` plus the scan crops `web/scores/` are
gitignored and excluded from the static build. The sound pool is piano, organ, choir and synth.
Listening modes are all voices, solo and “in evidenza” (backing voices lowered from .22 to .12
gain); the custom mix and the lyric-voice selector were removed because the words now follow
the voice being heard. Verse options show “Str. N” and the stanza's first words. The lyric
heading and tap hint were removed; Play/restart moved left and the starting-note keys right.


## Printed edition header

Digital PDFs now open with the title in IM Fell English (embedded in the standalone HTML),
the composer/arranger line and the default tempo, and print in pure black on white. The
notation regression suite checks the single first-page header, footers and every engraved note.


## Away in a Manger removed

At the user's request both Away in a Manger arrangements (the composer and Cradle Song) were removed
from the app: their song data, exports, scan crops, recognition draft and generator scripts were
deleted. The sections above remain as a record of how they had been transcribed. Only the private
original scan `songs/Away in a Manger.pdf` is kept.

Leftover working files were then removed from `sources/`: all Audiveris drafts and two
exploratory scripts. It now holds only the clean reference pages and the generator scripts
for the current songs.

Reusable code was kept for future songs and gathered in `sources/scripts/`: `vector_heads.py`,
a single `omr.py` (Audiveris build preparation, 300-dpi TIFF conversion, batch recognition and
per-part draft dump; its generated pom matches the build used here and a full run on the First
Nowell scan succeeded), and `song_kit.py` with the helpers shared by the generators. The two
generators were refactored onto it and still reproduce their data files byte for byte.


## Ding Dong! Merrily on High

- Rendering (2026-11-11): as printed, “ri-” of Gloria falls on beat 1½ (S/A, an eighth) or beat 1
  (T/B, a quarter), and the lower voices re-enter after rests inside the melisma with no syllable,
  so Cantai sang a long, staggered “riii”. The Cantai file only (not the app or PDF) splits the T/B
  quarter and sings “o” on every melisma note: Glo-o-…-ri-a, with “ri” on beat 1½ in all voices.
  The next render still had sopranos and altos early on “ria”; the file now gives “ri” only the last
  sixteenth before “a” (beat 1¾) in every voice, the vowel “o” holding until then.

- Source: the supplied two-page vector PDF (Sibelius export, arr. the arranger), stored privately
  as `songs/Ding Dong.pdf`. Bb major, 2/2 with quarter = 140 as printed, four separate staves
  (tenor in octave treble clef), 24 measures: verse (1–8), Gloria (9–16) printed twice (17–24).
- Pitches come from exact notehead positions (`vector_heads.py --font Opus --dot 2122 --key B,E
  --clefs T,T,T8,B`), rhythms were read from the page and every syllable was matched to its
  nearest printed note. Measures 1–8 are homophonic; in the Gloria the lower parts enter after a
  quarter rest and “ri-a” falls on beat 2½ (S/A) or 2 (T/B).
- The score prints stanza 1 only. Stanzas 2–3 are the author's public-domain text
  from a public-domain hymnal (representative text, Complete Anglican Hymns Old and New #148), fitted to the
  same notes; the author 1924 wording “Pray you … May you … rime” is noted as a variant.
  Each stanza is sung through all 24 measures. Generator: `sources/scripts/make_ding_dong.py`.

Also in this round: the app opens on the song list, and the renderer now beams eighth notes
within each beat group. The notation suite re-verified every engraved note and syllable.

## Interface simplification, organ backing and Away in a Manger (Cradle Song)

- Interface (TODO.md round): Italian only; choir voices always piano and the optional organ
  `backing_track` always organ (no sound selector); one cycling appearance icon; a single
  “‹ Brani” back button instead of tabs; listening order *tutte → in evidenza → solo*; 🎄 icon;
  an *A cappella / Con organo* library switch filtering on `backing_track`. Then: no check mark on
  the current song card, no fullscreen/focus mode, a visible “Opzioni ▾” pill on the phone
  summary, and the other voices in “in evidenza” raised from .12 to .25 (≈ −12 dB).
- Review of the previous agent's work: a JavaScript syntax error (assigning to
  `getAttribute(...)` in the theme button) stopped `player.js`, so the song list never loaded;
  the library switch silently snapped back while no organ songs existed. Both fixed.
- **Away in a Manger (Cradle Song)**: `songs/Away in a Manger - Cradle Song.pdf`, a one-page
  Sibelius vector PDF (online edition), the composer, F major, 3/4,
  pickup + 16 bars on two staves, three printed stanzas. The earlier draft had wrong notes: bars
  13–14 (data 14–15) were copies of bars 9–10 in all voices, the bass of bar 10 and the tenor of
  bar 7 (B♮ carries through the bar) were wrong, and stanza 2 was shifted one syllable from
  “a-wakes” onward. All pitches were re-read with `vector_heads.py --font Opus --dot 2122 --key B
  --clefs T,B` and every syllable checked against its printed x position. Generator:
  `sources/scripts/make_away_cradle.py`.

## I Saw Three Ships

- Source: `songs/I Saw Three Ships.pdf`, a one-page Sibelius vector PDF (online edition),
  traditional English carol, G major, 6/8, eighth pickup + 8 bars on two staves, stanzas 1–4
  printed. Pitches from `vector_heads.py --font Opus --dot 2122 --key F# --clefs T,B`; rhythms
  read from the page. Data measure 1 is the pickup (printed bar n = data n+1).
- Stanzas 5–8 come from a public-domain hymnal (The Hymnal for Boys and Girls #33, public domain); stanza 2
  keeps the printed “what was in those ships” (a public-domain hymnal: “who”). the 1833 collection “Then let us all rejoice
  amain” is not in that source and is not added. Stanza 7 (“in Heav’n shall sing”) splits the
  first quarter of printed bars 2 and 6 into two eighths in every voice (verse `parts` override;
  one footnote in the PDF). Tempo ♩ = 132 (dotted quarter 88).
- Renderer: 6/8 now beams by dotted quarter; equal rearticulation footnotes are merged per stanza.
  Generator: `sources/scripts/make_three_ships.py`.

## O Holy Night

- Source: `songs/O Holy Night.pdf` (renamed from `O-Holy-Night-Db-Major-1.pdf`), a two-page
  Sibelius vector PDF (online edition), the composer, D♭ major, 6/8, 50 bars on two staves,
  three printed stanzas, each sung through all 50 bars. Pitches from `vector_heads.py --font Opus
  --dot 2122 --key B,E,A,D,G --clefs T,B`; rhythms from the page and the Opus flag/rest glyphs.
- Decisions: printed accidentals persist through the bar (tenor bar 14 B♮, alto bar 16 E♮); the
  bass B𝄫3 in bar 34 is stored as sounding A3; in bars 45–46 the soprano divisi keeps the upper
  (melody) line; the printed quadruplet (4 in the time of 6 eighths) and tenor duplet are dotted
  eighths, which sound the same. Stanza 3 bar 12 holds “slave” over two notes as printed.
  Tempo ♩ = 72 (dotted quarter 48). Generator: `sources/scripts/make_holy_night.py`.
- New reusable check: `sources/scripts/check_lyrics.py` matches every printed syllable of a vector
  PDF to its notehead column and to the (measure, beat) of the data. Away in a Manger, I Saw Three
  Ships and O Holy Night all pass with no differences.

## What Child Is This

- Source: `songs/What Child Is This.pdf` (renamed from `What-Child-Is-This---Greensleeves.pdf`),
  an online edition: cover, terms page, music on page 3 (capella vector engraving). Greensleeves
  arr. the arranger, words the hymn author; E minor, 6/8, eighth pickup + 16 bars, three stanzas.
  The music and words are public domain; the engraving is an online edition's and is not reused (the
  notes were transcribed into our own data and renderer).
- `vector_heads.py` now reads capella engravings: hairline-rectangle staff lines/stems and a
  configurable accidental code (`--font capella --filled e5 --half none --dot 2e --accidentals 53,,`).
- Printed bar 12 omits the middle syllable in all three stanzas; the original “angels sing”, “for me, for
  you” and “lullaby” are restored on the three printed notes. Stanza 2 typos “bourne”/“bane” are
  corrected. `check_lyrics.py` reports exactly these differences. Tempo ♩ = 78.
  Generator: `sources/scripts/make_what_child.py`.

## Dio ci benedirà

- Source: `songs/Dio ci benedirà.pdf` (renamed from `Dio_ci_benedir.pdf`), a six-page Finale vector
  PDF (Maestro font) by G. the composers and A. the composers as sung by the a local choir
  (a local choir): SATB on four staves, 96 bars, E♭ major → F major at bar 64, 4/4 with 2/4 bars
  87 and 89, one through-composed Italian text.
- New reusable reader `sources/scripts/vector_score.py`: for fonts that expose noteheads, flags,
  dots, rests and accidentals as glyphs it drafts every bar (with per-bar accidental state, key
  changes, multirests, chords) and attaches the printed syllable under each note; a curve between
  equal pitches is a tie only when the second note has no new syllable. `make_dio.py` uses it
  directly, then adds: ties across system/page breaks, the bar-90 syllable (the reader picked up the
  “Rall.” text), hyphens derived from the full text (the score prints none) and ‿ for printed
  elisions (ci.as → ci‿as).
- Decisions: printed multirests (bars 1–5, 28–29, 52–54; instrumental, no accompaniment printed)
  stay as silent bars so numbers match the score; the soprano divisi keeps the upper note of each
  dyad; no tempo is printed (♩ = 96 suggested). A single text is not numbered in the PDF.
- Fixes needed by this song: `measure_keys` now applies from its measure on (music.py `key_at`), the
  engraving opens each system in its current key and repeats the clef on inline key changes
  (abcjs otherwise resets lower staves to treble), and MusicXML writes the key change.

## Good King Wenceslas

- Source: `songs/Good King Wenceslas.pdf` (renamed from `Good_King_Wenceslas.pdf`), an online edition
  edition, one page, a 16th-century tune arr. the arranger, words the author; A major, 4/4, 17 bars,
  five stanzas. Every glyph, text included, is an outlined path, so pitches were computed from the
  notehead path centres (5.4×4.7 pt; filled = quarter, hollow = half) against the hairline staff
  lines and checked on the page; the words were typed from the page.
- Bar 11 alto A3 (voice exchange with the tenor) and the printed final chord (bass on A3) are kept.
  The edition's dramatised solo suggestion (king = tenor, page = treble) is kept as a footnote;
  playback stays SATB. Tempo ♩ = 100. Generator: `sources/scripts/make_wenceslas.py`.

## Hark! the Herald Angels Sing

- Source: `songs/Hark the Herald Angels Sing.pdf` (renamed from `Hark_the_herald_angels_sing.pdf`),
  a three-page scan of the a choral anthology edition (the composer; descant and organ part by David
  the arranger), G major, 4/4. Page 1: SATB verses 1–2 (20 bars, refrain from bar 17, bars 19–20
  printed “Unison”); pages 2–3: verse 3 with descant and full organ part.
- At the user's request all three verses use the page-1 SATB setting (verse-3 words from page 2;
  the descant/organ setting is not encoded) and the song stays a cappella. Small parenthesised
  organ notes in bars 17–18 are omitted. Unison bars: tenors and basses an octave below the tune.
- Bar 20 (Unison): the final “King” was corrected from B to G (G A G), as printed on page 1, in
  all four voices (tenors and basses an octave lower).
- Tooling: Audiveris 5.4 was rebuilt in the gitignored `.omr/` (Maven 3.9.9, tessdata 4.1.0;
  `omr.py prepare-build` now excludes bsaf's obsolete `javax.jnlp` system dependency). New
  `sources/scripts/raster_heads.py` finds filled/hollow noteheads on scans (staff lines removed,
  blob centres → pitch) to cross-check OMR drafts. Generator: `sources/scripts/make_hark.py`.
- Engine: a verse may now carry its own `playback` (validated so every measure is played), and the
  compact score groups stanza rows by the verses that actually sing each measure.

## Follow-up requests (TODO round 2)

- Tempos: O Holy Night ♩ = 110, Good King Wenceslas ♩ = 120 (user choices).
- Dio ci benedirà: the printed multirests (bars 1–5, 28–29, 52–54) are removed because no
  accompaniment exists; data measure numbers therefore differ from the printed ones (key change
  now at data bar 54). Card credit shortened to “a local choir”.
- Phone interface: “‹ Brani” and the theme button share a 44 px height (minimum touch target);
  single-text songs hide the stanza selector, the “Tutte le strofe” summary and “Strofa 1 di 1”;
  the generic “· Strofa” label appears only for songs with named sections; “1 strofa” singular;
  tighter song cards; the score may shrink to 60% so score, lyrics and dock fit at 320×568; the
  current-syllable highlight no longer spills over neighbouring letters.

## A New Year Carol

- Source (2026-11-11): the choir version supplied by the user, `songs/A New Year Carol (SATB).pdf`
  (three pages of scan excerpts): stanza 1 sopranos; stanza 2 sopranos and altos; stanza 3 sopranos,
  altos and tenors + basses on one treble-clef staff, sung an octave lower. It replaces the earlier
  transcription of the unison + piano edition (all voices on the tune, piano as organ), which was wrong
  for this choir. E♭ major, 3/4, ♩ = 92.
- A cappella: no organ; the rest bars after stanzas 1 and 2 are left out, so the data is the three
  16-bar stanzas in a row (1–16, 17–32, 33–48), one “Brano intero” verse. In stanza 3 the sopranos
  sing a descant in the refrain and the altos take the tune.
- Read by eye from small crops (staff spaces ~10 px), each head against the lines next to it; the
  doubtful heads are listed in the song's `review_notes`. Generator: `sources/scripts/make_new_year.py`.

## Round 3: organ in editions, single list, internal copies

- One song list (no organ switch); cards show icon and title only.
- Printed editions add the organ (two braced staves; lanes merged into chords per hand by
  `compact_score.organ_staves`, lanes averaging ≥ C4 in the right hand). `notation.js` prints chords.
- Published files are internal rehearsal copies: no credits or tempo in the header, no credits at the
  end, none in MusicXML; `music.public()` removes composer, arranger, sources and review notes from
  `api/songs.json` and the HTML editions. Attribution stays in `data/` and this record. The PDF
  engraving is a little smaller (render width 1060, staff gap 42) so most songs fit 3 systems on page 1.
- Dio ci benedirà: all 96 printed bars restored; an organ part was added at the user's request
  (not printed in the source): it doubles the choir and fills the instrumental bars with choir
  material (1–4 = bars 6–9, 5 = E♭ chord, 28–29 = bars 6–7, 52–54 = bars 49–51).
- 2026-11-11: Dio ci benedirà is a cappella again: the organ part was removed, and with it the bars
  where nobody sings (printed 1–5, 28–29, 52–54 and the rest bar 63), leaving 85 bars (F major from
  data bar 53). Its playlist tracks are the app's piano playing each part (`tools/recordings.py piano`),
  since Cantai does not sing Italian.

## Carol of the Bells

- Source: the supplied six-page raster scan, renamed `songs/Carol of the Bells.pdf`. SATB a cappella
  (the rehearsal keyboard is not encoded), G minor, 3/4, 42 bars: bars 5–36 repeat (1st ending
  33–36), 2nd ending 37–42. Playback 1–36, 5–32, 37–42 with the same words both times.
- Audiveris failed on this scan; notes were read by eye from 260–300 dpi crops, with doubtful heads
  measured against local staff lines. Bar 41 soprano divisi: the lower (ostinato) line is encoded.
  Tempo ♩ = 160 (“Allegro”). Generator: `sources/scripts/make_carol_bells.py`.
- `tests/test_compact_score.py` now compares compact and unfolded music only up to the first
  repeat jump.

## Angels' Carol

- Source: the supplied eight-page scan, renamed `songs/Angels' Carol.pdf`. F major → G major at bar
  71, 2/2 (4/4 Tranquil at 104), 107 printed bars, three stanzas through-composed with Gloria refrains.
- An Audiveris draft (`.omr/out/angels.mxl`) was checked system by system against enlarged crops;
  bars it missed or garbled were read by eye. Divisi: each part takes its upper note.
- Sung a cappella (2026-11-11): the piano/harp part is not encoded (an earlier simplified organ
  backing track was removed), and the bars where only the piano plays (printed 1–2, 35–36, 69–70)
  are left out, so the data has 101 bars: data bar = printed − 2 from 3, − 4 from 37, − 6 from 71
  (G major from data bar 65). The generator keeps printed numbers and renumbers at the end (`DROP`).
  Tempo 𝅗𝅥 = 69. Generator: `sources/scripts/make_angels_carol.py`. Listening check still advised.
- Lyric fix (2026-11-11): in 26 bars that open with a note tied from the bar before (e.g. “sound __ |
  of the an-gel”), the words sat one note early (“of” on the held G, “gel” on the F). The generator's
  onset finder now knows about ties into the bar, and `music.validate` rejects a voice's own syllable
  on a tied-over note (shared “all” words may fall there: another voice sings them).

## Rehearsal recordings

- 2026-11-11: all earlier recordings (supplied voice notes, YouTube practice tracks) were removed
  from the app; recordings are now synthesized from the transcribed scores with MuseScore Studio +
  Cantai, so they match our arrangements, keys and tempos exactly.
- Joy to the World S/A/T/B: Cantai renders of `scratch/joy-to-the-world.musicxml` at ♩ = 180
  (44.1 kHz float WAV, 83 s incl. reverb tail). Each part's first sound is within 11 ms of the score's
  beat 1 and its last within 0.4 s of the score's end, so no trimming was needed.
- Playlist tracks (`tools/recordings.py build`): title spoken by Piper (en_GB-alba-medium;
  it_IT-paola-medium for Italian titles), the voice's first sounding note on the app's piano
  spectrum, a count-in of four minim clicks at 90/min for Joy's 2/2, then the part. Measured in the
  built file: clicks 0.667 s apart and the part entering one beat after the last click (±1 ms).
- Carol of the Bells S/A/T/B: Cantai renders at ♩ = 140 (93 s with tail); first sounds at 0.0 /
  5.1 / 10.3 / 15.4 s, matching the score's staggered entries (the bass's consonant ~50 ms early).
- Hark! the Herald (rendered after the bar-20 fix; the final “King” sings G4/G3) and Jingle Bells
  S/A/T/B: Cantai renders aligned with the score within 13 ms. Away in a Manger, I Saw Three Ships
  and What Child Is This: within 33 ms (6/8 count-ins: four dotted-quarter clicks). The First Nowell
  (♩ = 84): each file a single voice, 95–100 % of notes at the expected pitch on the score's beat.
- Check every part file before converting (sum of the others inside it? notes on the score's beats?).
  God Rest Ye Merry and O Holy Night: the exported `soprano.wav` was the four parts summed (least
  squares: alto, tenor, bass each at gain 1.00), so the soprano is that file minus the other three
  renders (nothing of them left, gains < .01; the original kept as `soprano-exported-mix.wav`). In God
  Rest that soprano also sang one beat + 80 ms early throughout (constant in every 15 s window): it is
  delayed 0.509 s, and its lost pickup “God” (D4, the same note and word as the alto) is the alto's,
  level-matched and crossfaded in 20 ms. Both then match 94–96 % of notes on the beat. The data and
  MusicXML were correct; `scratch/god-rest-ye-merry.musicxml` stays for a clean re-render.
- Angels' Carol (a cappella, after the lyric fix) and The First Nowell (re-rendered after the tie
  rule): single voices, 94–100 % of notes on the beat.
- O Holy Night (♩ = 110, already a cappella) and Good King Wenceslas (♩ = 120): the other parts single
  voices, 95–100 % of notes on the beat.
- `choir.m4a` (Christmas Carols album): the four parts summed at equal level, normalised to −16 LUFS,
  with no intro.
- `tools/recordings.py build` also writes `play-lead-<voice>.m4a` (“in evidenza”): the intro, then
  the four parts with that voice at gain 1 and the others at .4, scaled to that part's loudness.
- The interactive score also plays the plain part recordings (`<voice>.m4a`) as “Coro” at the
  recording's tempo (stored at convert time) and printed key, piano otherwise. Chromium decodes them
  with the first sound at 0–9 ms, the same as ffmpeg, so no decoder offset needs compensating.
- Ding Dong's emoji changed from 🔔 (also Carol of the Bells) to 🎶; song emojis are now unique.
- Synthesized part recordings: `python tools/cantai_scores.py` writes one SATB MusicXML per English
  song to the gitignored `scratch/` for MuseScore Studio + Cantai (Synthesizer V renders as well but
  its trial cannot export; OpenUtau/DiffSinger was tried and judged not good enough). Every verse is
  unfolded, all syllables sit on lyric line 1 (Cantai ignores lines 2+) and held syllables get
  extenders. Rendered WAVs go through `tools/recordings.py convert … --source "synthesized: Cantai"`,
  then `tools/recordings.py build`.
