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
- The user needs Play, the moving position on the score, all voices together or individual S/A/T/B voices, tempo, and simple navigation. Avoid unnecessary features.

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
  Practice has only a "‹ Brani" back button (no tabs). Going back pauses audio; selecting the
  current song preserves its position.
- On phones the song/verse/voice summary carries a visible "Opzioni ▾" pill so it is clear
  that tapping it opens the song options; the selection sheet opens from the top.
- Offer light, dark and device-adaptive appearance from one cycling icon button, remember the preference,
  and follow live device changes in adaptive mode. Adapt the digital score paper and notation colors to the resolved theme.
  The PDF download is always the light edition, in every theme.

- Listening modes, in this order: all voices, S/A/T/B "in evidenza", solo S/A/T/B (no custom
  mix). The lyrics shown always follow the voice being heard (soprano for all voices); there is
  no separate lyric-voice selector. Emphasis
  keeps the chosen voice at gain 1 and the other voices at .25 (still audible as a mix), with energy-based
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
- At the bottom of the Brani list, “Genera PDF” joins the chosen editions (checkboxes, “Seleziona tutti”, drag ⠿ to reorder; summary with a ▾ arrow)
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

- `web/sounds.js` synthesizes sounds with Web Audio only (no samples, no network). Choir parts
  always play as piano; an optional `backing_track` (organ lanes with the same measure count,
  for arrangements printed with accompaniment) always plays as organ on its own gain bus.
  There is no instrument selector; songs with a backing track (“base”) get a “Volume base” slider (0–150%, remembered on the device) and the listening modes “Solo base (organo)” and “Solo base (pianoforte)”.
- Phones (≤700px) must not need vertical scrolling while practising: one top bar (name, back button,
  appearance icon), a one-line song/verse/voice summary opening a sheet, the score, the current
  lyrics and the playback dock (keys, restart, play, tempo, seek). Song, verse, voice and
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
- The app opens on the Brani (song list) tab; the first song is preloaded for Prova.
- Engraving beams eighths and shorter notes within a beat group (half note in 2/2, dotted quarter in
  6/8-type meters, otherwise a quarter), as printed scores do.
- When a supplied score prints only some stanzas, find the missing ones online, record the source
  and any wording variants in `review_notes`, and fit them to the printed notes.

