# Sources and transcription kit

- Reference PDFs (clean pages of the same editions as some scans, comparison copies) live with
  the scans in the gitignored `songs/` folder: `reference-pages.pdf` (page 1 God Rest Ye Merry,
  page 2 Joy to the World, page 3 The First Nowell) and `A New Year Carol (TB comparison).pdf`.

## Scripts for new songs (development only, not used by the app)

- `scripts/vector_heads.py`: exact notehead pitches (with accidentals and stem/dot hints) from a
  vector PDF page, e.g. a clean online copy of the same edition. Use it whenever one exists.
- `scripts/check_lyrics.py`: compares every printed syllable of a vector PDF with the song data
  (nearest notehead column → measure and beat). Run it after writing a generator.
- `scripts/vector_score.py`: draft bars, ties and printed syllables from Finale/Petrucci vector
  PDFs (importable `read_page`); `scripts/raster_heads.py`: notehead pitches on raster scans.
- `scripts/omr.py`: draft MusicXML from a raster scan with Audiveris 5.4 (`prepare-build`, `tiff`,
  `run`, `dump`; see its docstring for the build notes). Drafts are starting points only.
- `scripts/song_kit.py`: shared helpers for generators — note onsets, one-syllable-per-beat cues,
  fitting shared lyrics to a part's held notes, cropping scan systems, validated saving.
- `scripts/make_<song>.py` (God Rest, Joy, Ding Dong, Away Cradle, Three Ships, Holy Night, Carol of the Bells, Angels’ Carol, …): worked examples. Each records every reading
  (parts, verses, verse-specific ties, staggered entries, form, compact layout) and regenerates
  `data/<id>.json`. Copy one as `make_<song>.py` for a new song.

Typical flow: find a clean copy → `vector_heads.py`, otherwise `omr.py` and `dump` → write
`make_<song>.py` → `check_lyrics.py` → `python tools/export.py` → `python tools/digital_score.py --pdf` → tests.

Run these with the gitignored dev environment: `python -m venv .venv && .venv/bin/pip install playwright pymupdf`.
Audiveris, Maven and tessdata live in the gitignored `.omr/` (see `omr.py`; rebuilt November 2026).
