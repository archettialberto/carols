# Christmas Carol Choir

Internal repository of a choir: a small rehearsal app for the carols we sing.
Each song is transcribed into editable data, played back voice by voice and
printed as a clean PDF. These are internal rehearsal copies, not editions for
distribution.

## Run

```sh
python app.py            # http://localhost:8000 (Python 3.10+, no packages needed)
python app.py --host 0.0.0.0   # reachable from a phone on the same Wi-Fi
```

On the phone open `http://<computer-IP>:8000`; in Safari use *Share → Add to Home
Screen* to install it. The published copy on GitHub Pages works the same way and
also offline after the first visit.

## Using the app

- **Home** offers three choices; the top **Home** button (or the back gesture) returns there.
- **Spartiti interattivi**: the song list. Tap a song to rehearse it.
- **Playlist**: **Christmas Carols** 🎄 plays the whole choir, song after song; then one album per voice (Soprani 🌸, Contralti ☀️, Tenori 🍂, Bassi ❄️) and one per
  voice *in evidenza* (the whole choir with that voice in front). Drag songs to reorder, then
  play: each song starts with its spoken title, first note and a count-in, then the music.
  Playback continues with the screen locked.
- **Genera PDF**: choose and order songs and get one printable PDF.
- The screen stays awake while the app is open; locking the phone pauses the interactive score.
- **Opzioni**: song, verse, voice (all, one voice *in evidenza*, or solo) and
  transposition (±6 semitones). Songs with recorded parts add **Suono**: *Coro* (the
  recordings, the default) or *Pianoforte*; a transposition uses the piano.
- **Lento** plays at 0.75× (the choir included, same pitch); there is no bpm field.
- **Space** plays and pauses the score on a computer.
- The score follows the audio with the words below; tap a note to start there.
- **S C T B** keys play each voice's starting note (hold to sustain, several for a chord).
- ⤓ downloads the printable PDF. Songs with accompaniment also play and print an organ part.

## Working on songs

- `data/<song>.json` is the source of truth (one file per song: notes per voice,
  lyrics per verse, optional organ `backing_track`). Format and rules: [AGENTS.md](AGENTS.md).
- Original scans live in `songs/` and never leave this computer (gitignored).
- `sources/scripts/make_<song>.py` rebuild each song; transcription tools are described
  in [sources/README.md](sources/README.md). Decisions and doubtful readings are in
  [PROCESSING.md](PROCESSING.md).

After changing a song:

```sh
python tools/export.py                 # MusicXML + MIDI in exports/
python tools/digital_score.py --pdf    # printable HTML + PDF (needs Playwright)
python -m unittest discover -s tests   # validation
```

Browser checks (development only, run against a running server):
`tests/browser_smoke.py`, `tests/notation_smoke.py`, `tests/starting_note_smoke.py`.
A gitignored `.venv` holds the development tools: `pip install -r requirements.txt`, then `playwright install chromium`.

## Publishing

Every push to `main` builds the static site (`tools/build_static.py` → `site/`) and
deploys it to GitHub Pages via `.github/workflows/pages.yml`. The playlist tracks are not in git:
the workflow first runs `tools/recordings.py build` (ffmpeg + numpy) on the committed voice parts
and spoken titles, so the repository holds only the recordings it cannot recreate.
