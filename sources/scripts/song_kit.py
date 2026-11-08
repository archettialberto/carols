"""Shared helpers for the per-song generator scripts (make_<song>.py).

A generator records every transcription reading (parts, lyrics, form) as plain Python and
calls these helpers to derive per-voice lyric timing, crop the scan's systems and write a
validated data/<id>.json. Development only (needs PyMuPDF for crop_systems); not used by the app.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from music import parse_bar, validate  # noqa: E402

JOIN = '‿'  # elision mark joining two words sung on one held note


def onsets(bar):
    """Beats inside a measure where a non-rest note starts (tie continuations included)."""
    at, out = 0, []
    for note in parse_bar(bar):
        if note['pitch'] != 'R':
            out.append(at)
        at += note['duration']
    return out


def even(text, start=0):
    """'rest ye mer- ry,' -> '0:rest 1:ye 2:mer- 3:ry,' (one syllable per beat)."""
    return ' '.join(f'{start + i:g}:{w}' for i, w in enumerate(text.split()))


def fit_lyrics(bars, rows):
    """Adapt shared lyric rows to one part: a syllable falling inside that part's held note
    joins the previous syllable instead of being lost or misplaced."""
    result, last = [], None
    for number, row in enumerate(rows, 1):
        starts = onsets(bars[number - 1])
        kept = []
        for cue in row.split():
            beat, word = cue.split(':', 1)
            if float(beat) in starts:
                kept.append([beat, word])
                last = kept[-1]
            elif last is not None:
                last[1] = (last[1][:-1] if last[1].endswith('-') else last[1] + JOIN) + word
        result.append(' '.join(f'{b}:{w}' for b, w in kept))
    return result


def crop_systems(slug, pdf, systems, page=0, x=(.07, .9), scale=2, first=1, start_index=0):
    """Save one PNG per printed system as web/scores/<slug>-<n>.png and return the song's
    `systems` list. `systems` holds (measure_count, top, bottom) as fractions of the page height.
    Bar lines are spread evenly: playback follows the digital notation, not the scan.
    For a score on several pages call it once per page with `first` (first measure on that
    page) and `start_index` (systems already cropped), then concatenate the lists."""
    import fitz
    doc = fitz.open(ROOT / pdf)
    sheet = doc[page]
    w, h = sheet.rect.width, sheet.rect.height
    out = []
    for index, (count, y0, y1) in enumerate(systems):
        pix = sheet.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=fitz.Rect(w * x[0], h * y0, w * x[1], h * y1))
        name = f'{slug}-{start_index + index + 1}.png'
        (ROOT / 'web' / 'scores').mkdir(parents=True, exist_ok=True)
        pix.save(ROOT / 'web' / 'scores' / name)
        out.append(dict(image='scores/' + name, page=page + 1, first_measure=first,
                        barlines=[round(i / count, 5) for i in range(count + 1)], width=pix.width, height=pix.height))
        first += count
    return out


def save_song(song):
    """Validate and write data/<id>.json; run tools/export.py and tools/digital_score.py --pdf next."""
    validate(song)
    # Internal rehearsal copies: no author, arranger or source credits are stored.
    song = {k: v for k, v in song.items() if k not in ('composer', 'arranger', 'sources')}
    path = ROOT / 'data' / f"{song['id']}.json"
    path.write_text(json.dumps(song, indent=2, ensure_ascii=False) + '\n')
    print('saved', path.relative_to(ROOT), len(song['parts']['soprano']), 'measures')
    return path
