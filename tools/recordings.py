"""Rehearsal recordings: convert files and build the playlist tracks (development only).

    python tools/recordings.py convert <input> <song-id> <voice> [--source TEXT]
    .venv/bin/python tools/recordings.py build [--retitle]

convert: writes recordings/<song-id>/<voice>.m4a in the one repo format (AAC-LC, mono, 48 kHz,
64 kbit/s, loudness -16 LUFS, true peak -1.5 dBTP, metadata stripped; plays in every browser,
including iOS Safari) and records it, with its length and the song's current tempo, in
recordings/index.json. The interactive score plays it instead of piano at that tempo. The recording
must start exactly at the beginning of the score (measure 1, beat 1), as a MuseScore/Cantai export
does. Voices: soprano, alto, tenor, bass, tenor-bass (men together), all (whole choir).
A recording in another key than the printed score gets `"transpose": <semitones>` in the index
(check with a pitch-class histogram); its starting note then sounds in the recording's key.

build: for every song with S/A/T/B recordings, writes recordings/<song-id>/play-<voice>.m4a, the
one track a voice's playlist plays. It joins separate parts, sample-accurately, and encodes once:
  1. the spoken title: recordings/<song-id>/title.m4a (Piper TTS, offline voices in the gitignored
     .tts/; made once, --retitle remakes it);
  2. the voice's first sounding note on the app's piano spectrum, and
  3. a metronome count-in at the score's tempo and beat (one bar; two bars when a bar has fewer
     than three beats), both computed from data/<song-id>.json, so the score stays the ground truth;
  4. the recording itself (<voice>.m4a), starting one beat after the last click.
When all four parts exist it also writes play-lead-<voice>.m4a ("<voice> in evidenza"): the same
intro, then the four parts mixed with that voice at gain 1 and the others at LEAD_OTHERS (the
score's choir uses the same balance), and choir.m4a: the four parts at equal level, nothing before
them, for the "Christmas Carols" album (listening to the whole choir, not rehearsing a part).
Rerun after adding recordings or changing a song's tempo, metre or first notes.
Needs ffmpeg, numpy and piper-tts:
    .venv/bin/pip install piper-tts
    .venv/bin/python -m piper.download_voices --data-dir .tts en_GB-alba-medium it_IT-paola-medium
"""
import argparse
import json
import math
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
INDEX = ROOT/'recordings'/'index.json'
VOICES = ('soprano', 'alto', 'tenor', 'bass', 'tenor-bass', 'all')
PARTS = ('soprano', 'alto', 'tenor', 'bass')
# Titles are spoken in their own language.
TITLE_VOICE = {'dio-ci-benedira': 'it_IT-paola-medium'}
DEFAULT_TITLE_VOICE = 'en_GB-alba-medium'
RATE = 48000
LEAD_OTHERS = .4  # "in evidenza" with recorded voices: the others at -8 dB
PIANO_OTHERS = .25  # with piano parts, as the score's piano emphasis
AAC = ['-vn', '-map_metadata', '-1', '-ac', '1', '-ar', str(RATE), '-c:a', 'aac', '-b:a', '64k', '-movflags', '+faststart']
ENCODE = ['-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', *AAC]


def load_index():
    return json.loads(INDEX.read_text()) if INDEX.exists() else {'songs': {}}


def save_index(index):
    index['songs'] = {k: index['songs'][k] for k in sorted(index['songs'])}
    INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n')


def encode(source, target, args=ENCODE):
    target.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(source), *args, str(target)], check=True)


def seconds(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)],
                         check=True, capture_output=True, text=True).stdout
    return round(float(out), 1)


def convert(source, song_id, voice, note=None):
    if voice not in VOICES:
        raise SystemExit(f'voice must be one of {", ".join(VOICES)}')
    if not (ROOT/'data'/f'{song_id}.json').exists():
        raise SystemExit(f'unknown song id {song_id!r} (no data/{song_id}.json)')
    target = ROOT/'recordings'/song_id/f'{voice}.m4a'
    encode(source, target)
    index = load_index()
    # Generated entries (the whole-choir track) are dropped: `build` recreates them from the parts.
    entries = [e for e in index['songs'].get(song_id, []) if e['voice'] != voice and not e.get('built')]
    song = json.loads((ROOT/'data'/f'{song_id}.json').read_text())
    # The tempo the recording was made at: the score plays it only at this tempo.
    entry = {'voice': voice, 'file': target.relative_to(ROOT).as_posix(), 'seconds': seconds(target), 'tempo': song['tempo']}
    if note:
        entry['source'] = note
    index['songs'][song_id] = sorted(entries + [entry], key=lambda e: VOICES.index(e['voice']))
    save_index(index)
    return target


def decode(path):
    """Mono float samples at RATE. AAC decoding drops the encoder delay, so time 0 is the music's."""
    import numpy as np
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-ac', '1', '-ar', str(RATE), '-f', 'f32le', '-'],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).astype(float)


def piano_tone(midi, length=2.2, held=1.7):
    """The app's synthesized piano (web/sounds.js): same partials, attack, decay and release."""
    import numpy as np
    t = np.arange(int(RATE*length))/RATE
    f = 440*2**((midi-69)/12)
    partials = [1, .55, .32, .22, .12, .08, .05, .035, .02, .012]
    wave_ = sum(a*np.sin(2*np.pi*f*(n+1)*t) for n, a in enumerate(partials) if f*(n+1) < RATE/2)
    env = np.where(t < .005, t/.005*1.5, .35 + 1.15*np.exp(-(t-.005)/.35))
    env = np.where(t > held, env[int(held*RATE)]*np.exp(-(t-held)/.06), env)
    return wave_*env


def click(accent):
    """A short woodblock-like metronome tick; the first beat of each bar is higher."""
    import numpy as np
    t = np.arange(int(RATE*.06))/RATE
    f = 1760 if accent else 1320
    return (np.sin(2*np.pi*f*t) + .3*np.sin(2*np.pi*2.01*f*t))*np.exp(-t/.012)*np.minimum(1, t/.0008)


def count_in(song):
    """Beat length in seconds and the number of clicks, from the score's metre and tempo
    (quarter-note tempo; beat group as in the engraving: half in 2/2, dotted quarter in 6/8)."""
    beats, unit = song['meter']
    if unit == 8 and beats % 3 == 0 and beats > 3:
        beat, per_bar = 1.5, beats//3
    else:
        beat, per_bar = 4/unit, beats
    bars = 2 if per_bar < 3 else 1
    return beat*60/song['tempo'], per_bar, per_bar*bars


def spoken_title(song, target, retitle=False):
    if target.exists() and not retitle:
        return target
    model = ROOT/'.tts'/f'{TITLE_VOICE.get(song["id"], DEFAULT_TITLE_VOICE)}.onnx'
    with tempfile.TemporaryDirectory() as tmp:
        speech = pathlib.Path(tmp)/'title.wav'
        subprocess.run([sys.executable, '-m', 'piper', '-m', str(model), '-f', str(speech)],
                       input=song['title'].replace('!', ','), text=True, check=True, capture_output=True)
        encode(speech, target)
    return target


def lead_mix(parts, voice, others=LEAD_OTHERS):
    """The four parts with `voice` in front, at the loudness of that part alone."""
    import numpy as np
    length = max(len(p) for p in parts.values())
    mix = np.zeros(length)
    for name, part in parts.items():
        mix[:len(part)] += part*(1 if name == voice else others)
    own = parts[voice]
    rms = lambda x: np.sqrt(np.mean(x[np.abs(x) > .02*np.abs(x).max()]**2))
    mix *= 1.15*rms(own)/rms(mix)
    return mix/max(1, np.abs(mix).max()/.97)


def sung_span(song, voice):
    """Seconds from the start of the first bar where `voice` sings to the end of its last such bar
    (all verses): a solo track skips the bars before and after, where the voice has nothing to sing."""
    from music import performance
    perf = performance(song, 'all')
    events = perf['events'][voice]
    if not events:
        return 0, None
    first, last = events[0]['start'], max(e['start'] + e['duration'] for e in events)
    start = max(b['start'] for b in perf['bars'] if b['start'] <= first)
    end = min((b['start'] + b['duration'] for b in perf['bars'] if b['start'] + b['duration'] >= last - 1e-9),
              default=perf['duration'])
    spb = 60/song['tempo']
    return start*spb, end*spb


def track(song, voice, entry, title, recording=None, trim=False):
    """Title, starting note, count-in and recording as one array (the recording starts at its score
    time 0, or with `trim` at the voice's first sung bar, ending 2 s after its last one)."""
    import numpy as np
    from music import performance
    if recording is None:
        recording = decode(ROOT/entry['file'])
    if trim:
        start, end = sung_span(song, voice)
        tail = None if end is None else round((end + 2)*RATE)
        recording = recording[round(start*RATE):tail]
    loud = recording[np.abs(recording) > .02*np.abs(recording).max()]
    level = np.sqrt(np.mean(loud**2)) if len(loud) else .1
    speech = decode(title)
    speech *= .9*level/max(np.sqrt(np.mean(speech[np.abs(speech) > .02]**2)), 1e-6)
    first = next(e for e in performance(song, 'all')['events'][voice])
    tone = piano_tone(first['midi'] + entry.get('transpose', 0))
    tone *= 1.6*level/np.abs(tone).max()
    beat, per_bar, clicks = count_in(song)
    lead = np.zeros(round(clicks*beat*RATE))
    for k in range(clicks):
        tick = click(k % per_bar == 0)*1.6*level
        at = round(k*beat*RATE)
        lead[at:at+len(tick)] += tick[:len(lead)-at]
    gap = lambda s: np.zeros(round(s*RATE))
    return np.concatenate([gap(.15), speech, gap(.45), tone, gap(.35), lead, recording]).clip(-1, 1)


def piano(song_id):
    """Parts played by the app's piano, for songs no singing synthesizer can sing (Italian): each
    voice of the all-verses performance at the score's tempo, converted like a recording and marked
    "piano" (the interactive score keeps its own live piano for these)."""
    import numpy as np
    import wave
    from music import load_songs, performance
    song = next(s for s in load_songs() if s['id'] == song_id)
    spb = 60/song['tempo']
    perf = performance(song, 'all')
    length = round((perf['duration']*spb + 2.5)*RATE)
    for voice in PARTS:
        out = np.zeros(length)
        for event in perf['events'][voice]:
            held = event['duration']*spb
            tone = piano_tone(event['midi'], held + .4, held)
            at = round(event['start']*spb*RATE)
            out[at:at+len(tone)] += tone[:length-at]
        out /= max(1e-9, np.abs(out).max()/.9)
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp)/f'{voice}.wav'
            with wave.open(str(path), 'wb') as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
                w.writeframes((out*32767).astype('<i2').tobytes())
            print(convert(path, song_id, voice, "piano: the app's synthesized piano, from the score").relative_to(ROOT))
        index = load_index()
        for entry in index['songs'][song_id]:
            if entry['voice'] == voice:
                entry['piano'] = True
        save_index(index)


def build(retitle=False):
    import numpy as np
    from music import load_songs
    songs = {s['id']: s for s in load_songs()}
    index = load_index()
    with tempfile.TemporaryDirectory() as tmp:
        for song_id, entries in index['songs'].items():
            song = songs[song_id]
            for entry in entries:
                if (ROOT/entry['file']).exists():
                    entry['seconds'] = seconds(ROOT/entry['file'])
            title = spoken_title(song, ROOT/'recordings'/song_id/'title.m4a', retitle)
            parts = {e['voice']: decode(ROOT/e['file']) for e in entries if e['voice'] in PARTS}
            entries[:] = [e for e in entries if e['voice'] != 'choir']
            if len(parts) == len(PARTS) and not any('transpose' in e for e in entries):
                length = max(len(p) for p in parts.values())
                mix = sum(np.pad(p, (0, length - len(p))) for p in parts.values())
                raw = pathlib.Path(tmp)/'choir.f32'
                raw.write_bytes((mix/max(1, np.abs(mix).max())).astype(np.float32).tobytes())
                target = ROOT/'recordings'/song_id/'choir.m4a'
                # Same loudness as every part (-16 LUFS); no title, note or count-in.
                subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'f32le', '-ar', str(RATE),
                                '-ac', '1', '-i', str(raw), *ENCODE, str(target)], check=True)
                entries.append({'voice': 'choir', 'file': target.relative_to(ROOT).as_posix(), 'seconds': seconds(target), 'built': True})
                print(target.relative_to(ROOT), f'{entries[-1]["seconds"]}s')
            for entry in entries:
                if entry['voice'] not in PARTS:
                    continue
                kinds = [('play', parts[entry['voice']])]
                if len(parts) == len(PARTS) and 'transpose' not in entry:
                    others = PIANO_OTHERS if entry.get('piano') else LEAD_OTHERS
                    kinds.append(('lead', lead_mix(parts, entry['voice'], others)))
                for kind, recording in kinds:
                    # Solo tracks skip the bars at the start and end where the voice is silent.
                    samples = track(song, entry['voice'], entry, title, recording, trim=kind == 'play')
                    raw = pathlib.Path(tmp)/'track.f32'
                    raw.write_bytes(samples.astype(np.float32).tobytes())
                    target = ROOT/'recordings'/song_id/(f'play-{entry["voice"]}.m4a' if kind == 'play' else f'play-lead-{entry["voice"]}.m4a')
                    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'f32le', '-ar', str(RATE),
                                    '-ac', '1', '-i', str(raw), *AAC, str(target)], check=True)
                    entry[kind] = target.relative_to(ROOT).as_posix()
                    entry[f'{kind}_seconds'] = seconds(target)
                    beat, _, clicks = count_in(song)
                    print(target.relative_to(ROOT), f'{entry[f"{kind}_seconds"]}s;', clicks, f'clicks at {60/beat:.0f}/min')
    save_index(index)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)
    c = commands.add_parser('convert')
    c.add_argument('input'); c.add_argument('song_id'); c.add_argument('voice'); c.add_argument('--source')
    p = commands.add_parser('piano', help='parts played by the app piano (songs Cantai cannot sing)')
    p.add_argument('song_id')
    b = commands.add_parser('build')
    b.add_argument('--retitle', action='store_true', help='remake the spoken titles')
    args = parser.parse_args()
    if args.command == 'convert':
        print(convert(args.input, args.song_id, args.voice, args.source).relative_to(ROOT))
    elif args.command == 'piano':
        piano(args.song_id)
    else:
        build(args.retitle)
