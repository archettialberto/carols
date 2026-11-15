# Song processing

Turn the PDFs in `songs/` into actual editable music and a very simple local choir practice app. There will be more songs later; process each arrangement individually.

- Preserve the original scans. Ignore handwritten notes, highlighting, and rehearsal annotations; transcribe the printed score.
- Inspect every page, identify title, arranger, key, meter, clefs, voice allocation, pickups, ties, accidentals, and repeat instructions. Tenor treble clefs may sound an octave below their notation.
- Prefer an exact existing digital edition if its notes and arrangement match the scan. Look online when useful, record the source, and never silently substitute another harmonization.
- When a clearer online copy of the *same* edition/arrangement exists (e.g. a vector PDF of the same
  page), use it as the primary transcription source: vector PDFs give exact notehead positions and
  lyric text. Record its URL/page in the song's `sources`, keep it in `sources/`, and keep the user's
  scan as the original-PDF download. Different harmonizations are comparison only.
- For short scores, manual transcription is fine. For longer scores, Audiveris can provide a MusicXML draft (`sources/scripts/omr.py`), but recognition must be checked against the scan, voice by voice. A scan is not music data.
- Keep one readable JSON file per song in `data/`, with separate soprano, alto, tenor, and bass measures. Pitches are sounding scientific pitch (C4 = middle C); durations are quarter-note beats. `R` is a rest and `~` ties to the next note of the same pitch. Do not encode slurs as ties.
- Describe form in the data, not in code: `playback` is one stanza's measure order (repeats
  unfolded), optional `final_playback` is played once after the last stanza (D.C. al Fine), and an
  entry's `silence_last` lists voices whose last note (an optional pickup) becomes a rest there.
  `sections` (`{"at":[measure,beat],"name":"chorus"}`; names verse/chorus/intro/interlude/coda) label
  the position. `shared_lyrics` prints common words once. The `compact` block drives printed PDFs:
  `refrain_measures`, `merge_refrain_systems`, `refrain_pickup_measures`, `annotations`
  (`measure`, `voice`, `note` index or `beat`, `text`), `lyric_replace`, `instructions`, `notes`,
  and `voice_lyrics` (`{"bass":[13,17]}`: also print that part's own words in those measures).
- Record source-system images and measure boundaries so playback can follow the original score. Record ambiguous readings explicitly in each song's `review_notes`; do not claim unchecked transcriptions are authoritative.
- Preserve all printed measures. Define playback order explicitly for repeats and D.C. al Fine; suppress any optional pickup on the final return. Explain decisions about multiple verses and suggested tempos.
- Run `python tools/export.py` after changing data. Check measure lengths, matching parts, legal pitches, ties, repeat order, and the generated MusicXML and MIDI. Visually compare notes and rhythms with each page, especially shared staves and annotations.
- Keep source attribution and processing decisions in `PROCESSING.md`. Export MusicXML for editing in a notation editor and MIDI for reuse.
- Keep the app readable and small: Python standard library server, plain HTML/CSS/JavaScript, browser audio. No database, frontend build, deployment framework, or runtime network dependency is needed.
- The user needs Play, the moving position on the score, all voices together or individual S/A/T/B voices, a slower (Lento) option, and simple navigation. Avoid unnecessary features.

Run locally: `python app.py`, then open http://localhost:8000. Validate with `python -m unittest discover -s tests`.

## Practice interface and lyrics

- Keep the name **Christmas Carol Choir** in English, preceded by the 🎄 emoji (also the app
  icon, on green). The interface is Italian only (no language switch). Sung text stays in
  its original language.
- Transcribe every printed stanza. Add numbered `verses` with per-measure
  `beat:syllable` cues in `lyrics`. Use `all` only when all voices share the same
  timing/text; otherwise record each voice separately. A trailing `-` joins
  syllables. Use explicit verse `parts` overrides when another stanza requires
  different note articulation. Check cue onsets against sounding notes.
- Keep pickups, melismas, rests, staggered voice entrances, chorus returns, and
  final Fine behavior aligned between lyrics and music. All-verses playback
  must update both the stanza number and text, not just loop the first stanza.
- The practice view engraves the whole performance (repeats unfolded, every stanza) as one endless
  line, always the four staves, scrolled under a fixed cursor at about a third of the width, which
  follows the most recent onset (a note held from before never pulls the view back): no line breaks
  in the interactive score (they are for the printed PDF), and no repeated clef strip (it broke on
  key changes). At the default zoom the line is fitted to the height left by the head, options and
  words (60–130%), refitted whenever they change size or the chosen stanza chip widens; desktop adds −/+ zoom. The words are
  not engraved in the staves: they are read from the sliding line. Solo and "in evidenza" fade the
  other voices whole (notes, stems, beams, rests: every element abcjs tags `abcjs-vN`), never change
  the staves. Render with `web/notation.js` and the vendored abcjs. Do not restore a duplicate scan
  view or advanced-options section in the app.
- On phones the staves and the words get all the height: no app bar or tabs in the score, a one-line
  head (back, stanza · section above the title, options), the line, the words, the dock. There is no
  fullscreen/focus mode. Test 320×568, 390×664 and 1280px, touch targets, and verse/voice-specific lyric timing.
- MusicXML and MIDI exports now expand all printed verses by default. MusicXML
  includes the active stanza's syllables under the corresponding notes.

- Look: "Rubrica", a Victorian hymnal printed in two inks (chosen 2026-11-15): ivory paper, black
  ink, vermilion rubrics (numbers, the current note and syllable, the main action), double gilt rules
  on covers; the dark theme is the same in reverse. IM Fell English (vendored, OFL) for titles,
  EB Garamond (vendored, OFL, `web/fonts/`) for sung words and small italics, system UI for controls.
- Three tabs, Playlist · Spartiti · PDF (a bottom bar on phones, hidden in the score), no home page:
  the app opens on Playlist. Every view is a URL hash (`#/playlist[/<album>]`, `#/brani`,
  `#/spartito/<id>`, `#/pdf`), so the phone's back gesture and links work. Leaving the score pauses
  its audio; opening the current song again keeps its position. The Spartiti list is alphabetical.
- Show the minimum and never repeat information on one screen: no page title that repeats the tab,
  no captions under covers, no decorative eyebrows or taglines, no "Strofa" section beside a stanza
  number, no lyric heading or tap hints.
- Offer light, dark and device-adaptive appearance from one cycling icon button (half disc, sun, moon,
  in the tabs' colour), remember the preference, and follow live device changes in adaptive mode.
  The PDF download is always the light edition, in every theme.

- Listening modes: all voices, S/A/T/B "in evidenza", solo S/A/T/B (no custom mix), from one row
  of keys Tutti · S · C · T · B: a tap puts a part in evidenza, a second isolates it, a third returns to all. The lyrics shown always follow the voice being heard (soprano for all voices); there is
  no separate lyric-voice selector. Emphasis
  keeps the chosen voice at gain 1 and the other voices at .25 on piano, .4 with the recorded choir
  (sung voices stand out more; the playlists' "in evidenza" mixes use .4 too), with energy-based
  master normalization. Route all sounding notes through per-voice gain buses;
  mix changes must not restart the transport or lose sustained notes.
- Generate digital notation from exactly the performance's notes and active verse
  lyrics. Keep rests, ties, accidental state per measure, and the tenor's sounding
  octave correct. SVG note clicks and highlight timing use the same beat clock.
- `python tools/digital_score.py` regenerates standalone, offline printable HTML;
  `--pdf` additionally generates PDF using Playwright/Chromium in a development
  environment. Commit generated HTML/PDF alongside the existing MusicXML/MIDI.
  Regenerate after data or renderer changes; verify no SVG ink is clipped.
- Keep abcjs pinned and vendored with its license. No runtime network, npm build,
  or Python package installation is required by users of the app. Upgrading the
  renderer requires rerunning the notation smoke checks.

- The only download is the light generated PDF `exports/<id>-digital.pdf`, a button in the score
  options. Original scans are never offered, served or
  published: `songs/` and the scan crops `web/scores/` are gitignored, local-only sources.
  MusicXML/MIDI/HTML remain development artifacts under `exports/`, not UI controls.
- Stanzas are chips: the number, and its first words “…” (computed from the lyrics, skipping an
  opening chorus) on the chosen one and in the phone sheet; a tap jumps to the stanza, its pickup included.
- Lyrics run as one sliding line under the score: the sung syllable sits near the left quarter so
  the next bars' words are always visible to read ahead; the left edge fades only once text scrolled.
- The PDF tab joins the chosen editions (the shared song rows with a tick box, “Seleziona tutti”,
  drag ⠿ to reorder) into one PDF in the browser (vendored pdf-lib, loaded on demand); “Pagine pari”
  pads each song to an even page count so double-sided copies start every song on a right-hand page.
- The playback dock holds only Play and the time bar. Play from the beginning of the song opens like
  a playlist track: the first note of each voice heard (the chord for all voices) on the app's piano
  held 1.7 s, then 0.35 s after its release a metronome count-in as built by
  `tools/recordings.py` (one bar, two when a bar has fewer than three beats; a dotted quarter in
  6/8-type metres, a half in 2/2), the music entering on the next beat. The clock waits at the
  starting beat meanwhile and the Play button shows ♪, then the beats. The cue goes straight to the
  output, audible whatever the mix. Resuming after a pause, a tap on a note, word or stanza, or a change of
  voice, key, sound or speed goes on at once, with no cue. There are no starting-note keys and no restart button.
- Generate only the light digital PDF with `tools/digital_score.py --pdf`; check SVG bounds.

- Printed digital PDFs/HTML use a compact score: every source measure appears
  once, with numbered stanza lyric rows under the same notes and one common
  refrain. Playback and MIDI/MusicXML still unfold the full verse sequence.
- Keep stanza numbers in the first lyric syllable (e.g. `1.~The` in ABC), rather
  than a separate token that would consume a note. Verify every printed syllable,
  including the last word of a system, against its intended note onset.
- `tools/compact_score.py` merges equal-pitch rhythmic variants onto one note grid
  with tied subdivisions preserving the base verse. Document stanza-specific
  rearticulation in a footnote. Pitch variants require explicit separate notation.
- For shared Nowell words, print one set of five lyric rows below soprano. For staggered Jingle entries, preserve the
  three lyric rows under each voice. Retain Fine/D.C. and pickup instructions.

- For empty ABC lyric cells, use a nonbreaking blank (`~`) rather than `*`:
  abcjs may consume a skip on a leading rest. Regression-check numbered stanza
  rows with delayed entrances against the parsed note lyrics.

- Digital PDFs open with one header on page 1: only the title in IM Fell English (embedded).
  These are internal rehearsal copies: no composer/arranger credits or tempo anywhere published
  (PDF/HTML, MusicXML, app list, `api/songs.json`; `music.public()` strips them). Songs with a
  `backing_track` also print the organ on a braced two-staff system (chords merged from lanes).
  The PDF engraving is slightly reduced so most songs fit three systems on page 1.
  Print pure black on white (no colour).
  Number every system after the first with its real source measure (abcjs `%%setbarnb`). Otherwise keep them free of boilerplate:
  no product blurb, review disclaimer, stanza section headings or system-level
  measure-range labels. Preserve attribution and review notes in the song data
  and processing documentation, and retain musical annotations/necessary footnotes.
- Print a small footer on every digital PDF page: song title, page/total, and the
  actual source-measure range on that page. Explicitly paginate complete systems
  before printing, so footer measure ranges match physical PDF pages in both themes.

## Sounds, phone layout and installable app

- `web/sounds.js` synthesizes sounds with Web Audio only (no samples, no network). Without
  recordings the choir parts play as piano; an optional `backing_track` (organ lanes with the same measure count,
  for arrangements printed with accompaniment) always plays as organ on its own gain bus.
  Songs with a backing track (“base”) get a “Volume base” slider (0–150%, remembered on the device) and the listening modes “Solo base (organo)” and “Solo base (pianoforte)” (a “Base” key: organ, piano, off).
  Every song is now a cappella (no `backing_track` in any data file, 2026-11-11), and bars where nobody
  sings are left out of the data; the backing-track support stays for a future accompanied score.
- Songs with recorded parts (`choir` in `api/songs.json`) show “Suono: Coro / Pianoforte”, Coro by
  default: the interactive score plays the part recordings (decoded once per song, started on the same
  beat clock, through the per-voice buses, so emphasis/solo work; the end keeps the reverb tail). Only at the recording's tempo (stored per recording) and
  in the printed key; a transposition (or a data tempo changed after recording) falls back to piano, and the options say
  “· Pianoforte”. Unrecorded voices stay on piano. The count-in is always piano.
- There is no bpm field: every song plays at its data tempo, and “Lento” (in the options, off
  whenever the app opens) is the only speed control, 0.75×: the piano exactly, the choir through a WSOLA time-stretch computed
  in the browser once per song (pitch kept, parts aligned within ±10 ms; recordings decoded at 32 kHz
  to keep phone memory low). The playlists have no speed control. On a computer Space plays/pauses the score (the playlist elsewhere), even with a clicked button focused; fields and tick boxes keep it.
- Phones (≤760px) must not need vertical scrolling while practising: voices, stanzas, Lento,
  Coro/Pianoforte, transposition and the PDF live in a bottom sheet behind one options button.
  Desktop shows them inline above the line.
- Keep the app installable from Safari/Chrome: `manifest.webmanifest`, `icons/` (SVG source and
  PNGs incl. 180px apple-touch and maskable; regenerate PNGs from `icon.svg` when it changes),
  iOS meta tags, and `sw.js` (network-first; only active on localhost/HTTPS). The server sends
  `Cache-Control: no-cache` so updates are never stale.
- Controls: 44px targets, round icon buttons and pills with thin rules (icons from `web/icons.svg`);
  the main action is vermilion (the round ringed Play, Riproduci, Genera PDF). Similar things look
  alike: one song row everywhere, Spartiti, playlists and PDF (number, tile, title, length, and a
  trailing slot: the playing equaliser or the tick box; in the PDF view only, the ⠿ grip outside the row), drawn by
  `web/ui.js`. The playing playlist's mini player stays on every view but the score; opening a score
  ends it. Tapping the mini player opens its playlist; ✕ stops it.
- Emojis in HTML must be colour by default (no U+FE0F; 🕯️ ☀️ ❄️ 🖨️ drew off-centre or as text). The two
  album seasons that need it (☀️ altos, ❄️ basses) are drawn only in SVG covers and the lock-screen
  canvas, written as escapes in `web/ui.js`; a unit test checks.
- Keep only needed files: no duplicate copies of scans or downloaded exports in `songs/`.
  `sources/` holds clean reference editions and the reusable transcription kit (`vector_heads.py`,
  `omr.py`, `song_kit.py`, one `make_<song>.py` per song; see `sources/README.md`). Delete one-off
  leftovers, but keep and extend reusable code for future songs.
- Keep the app deployable as a static site (GitHub Pages): the browser only fetches relative
  URLs (`api/songs.json`, `api/recordings.json`, `exports/…`, `recordings/…`).
  `app.py` computes those files live; `tools/build_static.py` writes them to `site/` (ignored by
  git; deployed by `.github/workflows/pages.yml`). Never add server-only behaviour to the player.
- Transposition (±6 semitones) applies to playback, the count-in and engraving, resets to
  the printed key on every song change, and does not change data or exports. Handwritten
  transposition remarks on scans are ignored.
- iPhone audio: Web Audio is muted by the silent switch unless the page also plays media.
  Keep `unlockAudio()` (playback `navigator.audioSession` plus a looping silent `<audio>`),
  started from a click/touchend; pointerdown alone does not unlock audio on iOS.
- The first song is preloaded for practice. A song with `"hidden": true` (e.g. a transcription being redone) is left out of the
  list, score selector, booklet and static site.
  The interactive score has no recordings controls, and the playlists have no score.
- Engraving beams eighths and shorter notes within a beat group (half note in 2/2, dotted quarter in
  6/8-type meters, otherwise a quarter), as printed scores do.
- When a supplied score prints only some stanzas, find the missing ones online, record the source
  and any wording variants in `review_notes`, and fit them to the printed notes.


## Rehearsal recordings and playlists

- Recordings are synthesized from our own scores only (old voice notes and YouTube tracks were
  removed 2026-11-11): `python tools/cantai_scores.py` writes `scratch/<song-id>.musicxml` (SATB,
  every verse unfolded, all syllables on lyric line 1 because Cantai sings only line 1, extenders on
  held syllables, and a tie broken wherever a syllable sits on its tied-over note, else Cantai skips it; per song,
  `JOIN` sings a staggered syllable together with the next one, on its note, and `VOWEL` writes the vowel on every
  note of a long melisma, across rests: Ding Dong's Gloria is “Glo-o-…-o-aw-ria”, “aw” on beat 1½ and “ria” on beat 2 of bar 14 in all voices (straight from the “o” run, Cantai started “ria” early) (a “ri” on its own sixteenth, the earlier `LATE` split, still came early in Cantai's bass and also shifted “mer-ri-ly”); `A_CAPPELLA` songs, now Dio ci benedirà (Italian, rendered
  on request), drop the bars where no voice sings and hold a note at most one bar, the final one two); the user renders each part in MuseScore Studio + Cantai and exports WAVs that
  start at measure 1 beat 1. `SUNG_AS` songs also get `scratch/<song-id>-latin.musicxml` (Angels' Carol,
  Ding Dong) or `-italian.musicxml` (Dio ci benedirà) for an English-only voice: Latin (Italianate
  church pronunciation) or Italian respelled per syllable for English letter-to-sound rules,
  e.g. “ex-cel-sis” → “Eck-shell-cease”, “be-ne-di-rà” → “beh-neh-dee-rah”. `scratch/` holds only these import files.
- `python tools/recordings.py convert <wav> <song-id> <voice> --source "…"` writes
  `recordings/<song-id>/<voice>.m4a` (AAC mono 48 kHz 64 kbit/s, −16 LUFS) and lists it in
  `recordings/index.json`; originals stay local in the gitignored `songs/recordings/cantai/<song-id>/`.
  Voices soprano, alto, tenor, bass (tenor-bass and all are still supported). A recording in another
  key gets `"transpose": <semitones>`.
- `.venv/bin/python tools/recordings.py build` joins separate parts into one track per voice,
  `recordings/<song-id>/play-<voice>.m4a`: the spoken title (`title.m4a`, Piper TTS, offline voices in
  gitignored `.tts/`), the voice's first note on the app's piano and a metronome count-in (one bar,
  two when a bar has under three beats; beat group as in the engraving), both computed from the song
  data, then the recording one beat after the last click. Decoded and encoded once, sample-accurate.
  A solo track (`play-<voice>`) skips the bars at the start and end where that voice does not sing
  (it starts at the downbeat of the voice's first sung bar, so the count-in still leads into it, and
  ends 2 s after its last sung bar): A New Year Carol for the basses starts at stanza 3. The “in
  evidenza” and Christmas Carols tracks stay whole.
  Rerun after adding recordings or changing a song's tempo, metre or first notes; only `play-*.m4a`
  are served. Generated tracks (`play-*.m4a`, `play-lead-*.m4a`, `choir.m4a`) are gitignored to keep
  the repository small: the Pages workflow installs ffmpeg + numpy and runs the build before the tests
  and `build_static.py`. Commit the parts, `title.m4a` (no TTS in CI) and `recordings/index.json`.
  The build skips a song whose inputs (parts, title, data, `tools/recordings.py`) match the fingerprint
  in `recordings/<song>/.build` and whose tracks exist; the workflow keeps the tracks in `actions/cache`,
  so a publish rebuilds only changed songs.
- Cantai sings only English and Latin (Cantai FAQ, checked 2026-11-15; an earlier note here claimed
  Italian, which the user could not find). Dio ci benedirà is rendered with the English voice from
  `scratch/dio-ci-benedira-italian.musicxml` (Italian respelled, every syllable its own word: joined
  words were re-split by Cantai's English rules, putting syllables early); the plain file is
  respelled for Cantai's Latin voice (`AS_LATIN`), if it can be selected. Its held phrase-end chords
  are shortened in the data itself (`make_dio.py`, 76 bars), which the recordings follow.
- Songs with no sung render get piano parts:
  `tools/recordings.py piano <song-id>` renders each part of the score with the app's piano and converts
  it like a recording, marked `"piano": true`; they fill the playlists (their “in evidenza” mixes keep the
  others at .25, as the score's piano), while the interactive score keeps its live piano (no “Coro”).
- In a playlist every song tile takes that playlist's ink (the list, the mini player and the lock-screen
  artwork, which adds the season faint behind); Spartiti and PDF use the choir's black.
- The Playlist page shows the covers alone: Christmas Carols 🎄, a double rule, then the eight voice
  albums (headings only for screen readers; no titles or song counts).
  Christmas Carols plays the whole choir, `choir.m4a` per song (the four
  parts at equal level, −16 LUFS), nothing before each song: no title, note or count-in.
- Eight voice albums: Soprani/Contralti/Tenori/Bassi, then the same “in evidenza” (`lead-<voice>`: the
  four parts mixed by the build with that voice at 1 and the others at .4, in `play-lead-<voice>.m4a`).
  Seasons 🌸 ☀️ 🍂 ❄️ (spring, summer as a plain sun, never the sun with a face, autumn, snow; never a
  song's emoji; song emojis are unique); covers are typographic title pages, one SVG on a fixed 200×200
  grid (they scale like an image, nothing overlaps): the voice's deep ink (choir black, madder, ochre,
  pine, indigo), a double gilt rule with corner lozenges, the initial and name in IM Fell, the season
  large and faint behind, and “in evidenza” in the same gilt italic (no band). A voice's own album plays per song its track, then tenor-bass (T/B) and all when
  they exist. No tick boxes, back link, hint or reordering: Play plays every song, in alphabetical order
  as in Spartiti. Rows show only what the album name does not say (extra recordings, length); the mini
  player shows the album name alone for the album's own tracks. Song lists share the one row, and views never scroll the top bar away. The lock-screen artwork draws the emoji into its own small
  canvas with a solid fill and scales it (iOS Safari draws no emoji with a gradient fill). One
  `<audio>` element plays the queue, so it continues with the screen locked, with Media Session
  metadata/artwork and play/pause/previous/next on the lock screen.
- The synthesized score pauses cleanly when the page is hidden (background timers garble it), and
  the Screen Wake Lock keeps the phone awake while the app is visible. The server answers byte
  ranges for recordings (iOS Safari needs them); the service worker never caches them.
- Check with `tests/playlist_smoke.py`, `tests/browser_smoke.py`, `tests/count_in_smoke.py` and
  `tests/notation_smoke.py` against a running server.
