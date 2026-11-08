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

- **Brani**: the song list. Tap a song to rehearse it; **Brani** goes back.
- **Opzioni**: song, verse, voice (all, one voice *in evidenza*, or solo) and
  transposition (±6 semitones).
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
deploys it to GitHub Pages via `.github/workflows/pages.yml`.
