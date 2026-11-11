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
- The main view focuses the current system, with sung syllables below. Render
  clean digital SVG notation by default using `web/notation.js` and the vendored
  abcjs renderer. Solo views engrave one independent vocal staff. Do not restore
  a duplicate scan view or advanced-options section in the app.
- On phones, keep notation readable with horizontal panning and zoom, persistent
  playback controls. There is no fullscreen/focus mode. Test narrow widths including 320px,
  touch targets, and verse/voice-specific lyric timing.
- MusicXML and MIDI exports now expand all printed verses by default. MusicXML
  includes the active stanza's syllables under the corresponding notes.

- Keep the interface restrained, using evergreen, berry and warm gold accents.
  The Brani list and practice song selector share alphabetical title order. The list has an
  single list of all songs (with or without organ); cards show only icon and title.
  The top bar has one "Home" button (no tabs); every view is a history entry so the phone's back
  gesture works. Leaving the score pauses its audio; selecting the current song preserves its position.
- On phones the song/verse/voice summary carries a visible "Opzioni ▾" pill so it is clear
  that tapping it opens the song options; the selection sheet opens from the top.
- Offer light, dark and device-adaptive appearance from one cycling icon button, remember the preference,
  and follow live device changes in adaptive mode. Adapt the digital score paper and notation colors to the resolved theme.
  The PDF download is always the light edition, in every theme.

- Listening modes, in this order: all voices, S/A/T/B "in evidenza", solo S/A/T/B (no custom
  mix). The lyrics shown always follow the voice being heard (soprano for all voices); there is
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

- The only download is one icon button (in line with the score controls) for the light
  generated PDF `exports/<id>-digital.pdf`. Original scans are never offered, served or
  published: `songs/` and the scan crops `web/scores/` are gitignored, local-only sources.
  MusicXML/MIDI/HTML remain development artifacts under `exports/`, not UI controls.
- The verse selector reads "Str. N · “first 3–4 words”" (`verse_incipit`, skipping an
  opening chorus); the interface omits redundant captions such as a lyric heading or tap hints.
- Lyrics run as one sliding line under the score: the sung syllable sits near the left quarter so
  the next bars' words are always visible to read ahead; the left edge fades only once text scrolled.
- The Home card “Genera PDF” opens its own view that joins the chosen editions (checkboxes, “Seleziona tutti”, drag ⠿ to reorder)
  into one PDF in the browser (vendored pdf-lib, loaded on demand); “Rendi pagine pari” pads each
  song to an even page count so double-sided copies start every song on a right-hand page.
- The playback dock puts Play/restart on the left and the starting-note keys on the right.
- Provide starting-note keys S/A/T/B that behave like piano keys: a tap rings a short
  cue (1.6 s), holding sustains, several keys together form a chord (multi-touch).
  Use the first non-rest event of that voice, at sounding pitch. They must be audible
  even if the voice is muted in the practice mix, pause playback without seeking,
  and cancel when normal playback, the library tab or another song starts.
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
  Songs with a backing track (“base”) get a “Volume base” slider (0–150%, remembered on the device) and the listening modes “Solo base (organo)” and “Solo base (pianoforte)”.
  Every song is now a cappella (no `backing_track` in any data file, 2026-11-11), and bars where nobody
  sings are left out of the data; the backing-track support stays for a future accompanied score.
- Songs with recorded parts (`choir` in `api/songs.json`) show “Suono: Coro / Pianoforte”, Coro by
  default: the interactive score plays the part recordings (decoded once per song, started on the same
  beat clock, through the per-voice buses, so emphasis/solo work; a single verse plays its slice and
  fades out; the end keeps the reverb tail). Only at the recording's tempo (stored per recording) and
  in the printed key; a transposition (or a data tempo changed after recording) falls back to piano, and the summary says
  “· Pianoforte”. Unrecorded voices stay on piano. Starting-note keys are always piano.
- There is no bpm field: every song plays at its data tempo, and “Lento” (a toggle in the dock,
  remembered on the device) is the only speed control, 0.75×: the piano exactly, the choir through a WSOLA time-stretch computed
  in the browser once per song (pitch kept, parts aligned within ±10 ms; recordings decoded at 32 kHz
  to keep phone memory low). The playlists have no speed control. On a computer Space plays/pauses the score (the playlist elsewhere), even with a clicked button focused; fields, selects, checkboxes and the S/A/T/B keys keep it. Lento uses the standard button shape (as every button:
  44px, 8px corners); pressed it takes the primary colours.
- Phones (≤700px) must not need vertical scrolling while practising: one top bar (name, back button,
  appearance icon), a one-line song/verse/voice summary opening a sheet, the score, the current
  lyrics and the playback dock (keys, restart, play, Lento, seek). Song, verse, voice and
  transposition live in the selection sheet. Desktop shows the
  selectors inline. Test 320×568, 390×664 and 1280px.
- Keep the app installable from Safari/Chrome: `manifest.webmanifest`, `icons/` (SVG source and
  PNGs incl. 180px apple-touch and maskable; regenerate PNGs from `icon.svg` when it changes),
  iOS meta tags, and `sw.js` (network-first; only active on localhost/HTTPS). The server sends
  `Cache-Control: no-cache` so updates are never stale.
- Victorian but readable: IM Fell English (vendored, OFL) only for titles; Georgia for lyrics;
  system UI for controls; cream paper, evergreen, berry and gold in both themes.
- Keep only needed files: no duplicate copies of scans or downloaded exports in `songs/`.
  `sources/` holds clean reference editions and the reusable transcription kit (`vector_heads.py`,
  `omr.py`, `song_kit.py`, one `make_<song>.py` per song; see `sources/README.md`). Delete one-off
  leftovers, but keep and extend reusable code for future songs.
- Keep the app deployable as a static site (GitHub Pages): the browser only fetches relative
  URLs (`api/songs.json`, `api/performance/<song>/<verse>.json`, `exports/…`, `songs/…`).
  `app.py` computes those files live; `tools/build_static.py` writes them to `site/` (ignored by
  git; deployed by `.github/workflows/pages.yml`). Never add server-only behaviour to the player.
- Transposition (±6 semitones) applies to playback, starting-note keys and engraving, resets to
  the printed key on every song change, and does not change data or exports. Handwritten
  transposition remarks on scans are ignored.
- iPhone audio: Web Audio is muted by the silent switch unless the page also plays media.
  Keep `unlockAudio()` (playback `navigator.audioSession` plus a looping silent `<audio>`),
  started from a click/touchend; pointerdown alone does not unlock audio on iOS.
- The app opens on Home: three cards with no captions, "Spartiti interattivi" (Brani list → practice),
  "Playlist" (voice albums → playlist) and "Genera PDF" (booklet, no hint text). The first song is
  preloaded for practice. A song with `"hidden": true` (e.g. a transcription being redone) is left out of the
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
  `LATE` splits a note so a staggered syllable sounds together and `VOWEL` writes the vowel on every
  note of a long melisma, across rests: Ding Dong's Gloria is “Glo-o-…-ri-a”, “ri” only on the last sixteenth (beat 1¾) of bar 14 in all voices; `A_CAPPELLA` songs, now Dio ci benedirà (Italian, rendered
  on request), drop the bars where no voice sings and hold a note at most one bar, the final one two); the user renders each part in MuseScore Studio + Cantai and exports WAVs that
  start at measure 1 beat 1. `scratch/` holds only these import files.
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
- Cantai sings Italian too (experimental, since late 2026; MuseScore Studio ≥ 4.6.5, MuseHub ≥ 3.0): the
  language is chosen in the Cantai window under the singer's name and applies to the whole score.
  Until Dio ci benedirà has a Cantai render, its playlists use piano parts.
- Songs with no sung render get piano parts:
  `tools/recordings.py piano <song-id>` renders each part of the score with the app's piano and converts
  it like a recording, marked `"piano": true`; they fill the playlists (their “in evidenza” mixes keep the
  others at .25, as the score's piano), while the interactive score keeps its live piano (no “Coro”).
- In a playlist every song cover takes that playlist's colour and its season emoji, faint behind (the list,
  the mini player and the lock-screen artwork): Ding Dong in Bassi is snowy blue, in Tenori orange.
- The Playlist page has two headings: “Playlist completa” (one card, “Christmas Carols” 🎄, no title
  beside the cover) and “Playlist per voce” (the eight voice albums); every album is the same card, the cover alone (no song count).
  Christmas Carols plays the whole choir, `choir.m4a` per song (the four
  parts at equal level, −16 LUFS), nothing before each song: no title, note or count-in.
- Eight voice albums: Soprani/Contralti/Tenori/Bassi, then the same “in evidenza” (`lead-<voice>`: the
  four parts mixed by the build with that voice at 1 and the others at .4, in `play-lead-<voice>.m4a`).
  Seasons 🌸 ☀️ 🍂 ❄️ (never a song's emoji; song emojis are unique); covers are one SVG drawing on a
  fixed 200×200 grid (they scale like an image, nothing overlaps) in the season's colour
  with a gold double frame, the initial and name in IM Fell, the emoji only large and faint behind, and a gold
  “in evidenza” band. A voice's own album plays per song its track, then tenor-bass (T/B) and all when
  they exist. No tick boxes, back link or hint: every song plays, reordered by dragging ⠿ (remembered
  per device). Rows show only what the album name does not say (extra recordings, length); the mini
  player shows the album name alone for the album's own tracks. Song lists (Brani, playlists, PDF)
  share the title face, the emoji in a soft circle or cover, and views never scroll the top bar away. Song covers show the emoji; the lock-screen artwork draws the emoji into its own small
  canvas with a solid fill and scales it (iOS Safari draws no emoji with a gradient fill). One
  `<audio>` element plays the queue, so it continues with the screen locked, with Media Session
  metadata/artwork and play/pause/previous/next on the lock screen.
- The synthesized score pauses cleanly when the page is hidden (background timers garble it), and
  the Screen Wake Lock keeps the phone awake while the app is visible. The server answers byte
  ranges for recordings (iOS Safari needs them); the service worker never caches them.
- Check with `tests/playlist_smoke.py` (and `tests/browser_smoke.py`) against a running server.
