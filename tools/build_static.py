"""Build a static copy of the app for GitHub Pages (or any static host).
Run: python tools/build_static.py [--out site]
Writes the web app, the JSON the Python server would compute, the digital PDFs and the recordings.
Original scans and scan crops are never published. Standard library only; run tools/export.py and tools/digital_score.py --pdf first.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from music import ROOT, load_songs, performance, recording_files, recordings_payload, songs_payload


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default=str(ROOT/'site'))
    out = Path(parser.parse_args().out).resolve()
    if out == ROOT or ROOT not in out.parents:
        raise SystemExit('Output must be a sub-folder of the project')
    shutil.rmtree(out, ignore_errors=True)
    # Scan crops (web/scores) and original PDFs stay private: the app only uses digital notation.
    shutil.copytree(ROOT/'web', out, ignore=shutil.ignore_patterns('scores'))
    write_json(out/'api'/'songs.json', songs_payload())
    write_json(out/'api'/'recordings.json', recordings_payload())
    for relative in sorted(recording_files()):
        (out/relative).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/relative, out/relative)
    for song in [s for s in load_songs() if not s.get('hidden')]:
        for verse in ['all'] + [v['number'] for v in song['verses']]:
            write_json(out/'api'/'performance'/song['id']/f'{verse}.json', performance(song, verse))
        for relative in [f"exports/{song['id']}-digital.pdf"]:
            source = ROOT/relative
            if not source.is_file():
                raise SystemExit(f'Missing {relative}: run tools/digital_score.py --pdf first')
            (out/relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, out/relative)
    (out/'.nojekyll').write_text('')  # serve every file as-is
    size = sum(f.stat().st_size for f in out.rglob('*') if f.is_file())
    print(f'{out.relative_to(ROOT)}/: {len(load_songs())} songs, {size/1e6:.1f} MB')


if __name__ == '__main__':
    main()
