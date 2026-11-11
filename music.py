"""Read the small score format and unfold it into sounding notes."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VOICES = ('soprano', 'alto', 'tenor', 'bass')
SECTIONS = ('verse', 'chorus', 'intro', 'interlude', 'coda')
TOKEN = re.compile(r'(R|[A-G](?:#|b)?[0-8]):(0\.25|0\.5|0\.75|1|1\.5|2|3|4)(~?)')


def parse_bar(text):
    notes=[]
    for token in text.split():
        match=TOKEN.fullmatch(token)
        if not match:
            raise ValueError(f'Invalid note: {token}')
        pitch, duration, tie=match.groups()
        if pitch == 'R' and tie:
            raise ValueError('A rest cannot be tied')
        notes.append(dict(pitch=pitch, duration=float(duration), tie=bool(tie)))
    return notes


def midi_pitch(pitch):
    if pitch == 'R':
        return None
    semitones={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
    accidental=1 if '#' in pitch else -1 if 'b' in pitch else 0
    return 12*(int(pitch[-1])+1)+semitones[pitch[0]]+accidental


def parse_lyrics(text):
    """Beat offsets and sung syllables; a trailing hyphen joins the next syllable."""
    return [dict(beat=float(token.split(':',1)[0]), text=token.split(':',1)[1])
            for token in text.split()]


def validate(song):
    assert set(song['parts']) == set(VOICES), 'Expected four SATB parts'
    count=len(song['parts']['soprano'])
    beats=song['meter'][0]*4/song['meter'][1]
    lengths=song.get('measure_beats',[beats]*count)
    assert len(lengths)==count and all(0<b<=beats for b in lengths), 'Invalid measure lengths'
    playbacks=[song['playback']]+[v['playback'] for v in song.get('verses',[]) if 'playback' in v]
    assert set(p['measure'] for order in playbacks for p in order) == set(range(1,count+1)), 'Every measure must be played'
    for entry in [e for order in playbacks for e in order]+song.get('final_playback',[]):
        assert 1<=entry['measure']<=count
        assert set(entry.get('silence_last',[])) <= set(VOICES)
    assert all(s['name'] in SECTIONS for s in song.get('sections',[]))
    assert sum(len(s['barlines'])-1 for s in song['systems'])==count
    for voice,bars in song['parts'].items():
        assert len(bars)==count, f'{voice}: different measure count'
        pending=None
        for number,bar in enumerate(bars,1):
            notes=parse_bar(bar)
            assert sum(n['duration'] for n in notes)==lengths[number-1], f'{voice} measure {number}: wrong duration'
            for note in notes:
                if pending:
                    assert note['pitch']==pending, f'{voice} measure {number}: broken tie'
                pending=note['pitch'] if note['tie'] else None
        assert pending is None, f'{voice}: unfinished tie'

    # An accompanied arrangement may add any number of monophonic organ lanes.
    # Multiple lanes can sound together, so this also represents printed chords
    # without forcing accompaniment into the four choir parts.
    backing=song.get('backing_track')
    if backing is not None:
        assert backing.get('instrument')=='organ', 'Backing track must use organ'
        assert isinstance(backing.get('parts'),dict) and backing['parts'], 'Backing track needs parts'
        for lane,bars in backing['parts'].items():
            assert lane and len(bars)==count, f'backing {lane}: different measure count'
            pending=None
            for number,bar in enumerate(bars,1):
                notes=parse_bar(bar)
                assert sum(n['duration'] for n in notes)==lengths[number-1], f'backing {lane} measure {number}: wrong duration'
                for note in notes:
                    if pending:
                        assert note['pitch']==pending, f'backing {lane} measure {number}: broken tie'
                    pending=note['pitch'] if note['tie'] else None
            assert pending is None, f'backing {lane}: unfinished tie'

    assert set(song['staff_bands'])==set(VOICES)
    assert all(0<=top<bottom<=1 for top,bottom in song['staff_bands'].values())
    for verse in song.get('verses', []):
        assert verse['number'] >= 1
        for voice, overrides in verse.get('parts',{}).items():
            assert voice in VOICES
            for measure,text in overrides.items():
                assert 1<=int(measure)<=count
                assert sum(n['duration'] for n in parse_bar(text))==lengths[int(measure)-1], 'Wrong verse rhythm'
        for voice, lines in verse['lyrics'].items():
            assert voice in (*VOICES, 'all')
            assert len(lines) == count, 'Missing lyric measures'
            for number,line in enumerate(lines):
                cues = parse_lyrics(line)
                positions = [cue['beat'] for cue in cues]
                assert positions == sorted(set(positions)), 'Unordered lyric cues'
                assert all(0 <= b < lengths[number] for b in positions), 'Lyric outside measure'
        for voice in VOICES:
            rows=verse['lyrics'].get(voice,verse['lyrics'].get('all'))
            assert rows is not None, 'Missing lyrics for a voice'
            # A voice's own words never fall on a tied-over note (shared "all" words may: another
            # voice sings them while this one holds).
            own=voice in verse['lyrics']; tied=False
            for number,line in enumerate(rows,1):
                text=verse.get('parts',{}).get(voice,{}).get(str(number),song['parts'][voice][number-1])
                at=0; onsets=[]
                for note in parse_bar(text):
                    if note['pitch']!='R' and not (own and tied): onsets.append(at)
                    tied=note['tie']; at+=note['duration']
                assert all(c['beat'] in onsets for c in parse_lyrics(line)), f'{voice} measure {number}: lyric without note onset'


def load_songs():
    songs=[]
    for path in sorted((ROOT/'data').glob('*.json')):
        song=json.loads(path.read_text())
        validate(song)
        songs.append(song)
    return songs


def playback_order(song, verse=1):
    """One selected verse, or all printed verses with the correct chorus returns."""
    numbers=[v['number'] for v in song['verses']]
    if verse != 'all' and verse not in numbers:
        raise ValueError('Unknown verse')
    chosen=numbers if verse == 'all' else [verse]
    # Each stanza follows `playback`; an optional `final_playback` (e.g. D.C. al Fine)
    # is played once after the last chosen stanza.
    # A verse may define its own `playback` when it is set to different printed music
    # (e.g. a last verse with descant printed after the hymn).
    verse_data={v['number']:v for v in song['verses']}
    order=[{**entry,'verse':v} for v in chosen for entry in verse_data[v].get('playback',song['playback'])]
    order+=[{**entry,'verse':chosen[-1],'final_return':True} for entry in song.get('final_playback',[])]
    return order


def section_at(song, measure, beat=0):
    """Name of the printed section (verse, chorus, ...) at a measure position."""
    name='verse'
    for section in song.get('sections',[]):
        if (measure,beat) >= tuple(section['at']): name=section['name']
    return name


def key_at(song, number):
    """Key signature in force at a source measure: `measure_keys` changes apply from that measure on."""
    changes=sorted((int(m),k) for m,k in song.get('measure_keys',{}).items())
    return next((k for m,k in reversed(changes) if m<=number),song['key_fifths'])


def performance(song, verse=1):
    """Unfold notes and syllables together, using quarter-note beats for both."""
    beats=song['meter'][0]*4/song['meter'][1]
    bars=[]
    events={voice:[] for voice in VOICES}
    lyrics={voice:[] for voice in VOICES}
    rests={voice:[] for voice in VOICES}
    pending={voice:False for voice in VOICES}
    backing=song.get('backing_track')
    backing_events=[]
    backing_pending={lane:False for lane in backing['parts']} if backing else {}
    lyric_join={voice:False for voice in VOICES}
    verse_data={v['number']:v for v in song['verses']}
    order=playback_order(song,verse)
    offset=0
    for index,entry in enumerate(order):
        number=entry['measure']
        bar_beats=song.get('measure_beats',[beats]*len(song['parts']['soprano']))[number-1]
        parts={}
        system=next(i for i,s in enumerate(song['systems'])
                    if s['first_measure'] <= number < s['first_measure']+len(s['barlines'])-1)
        stanza=verse_data[entry['verse']]
        for voice in VOICES:
            text=stanza.get('parts',{}).get(voice,{}).get(str(number),song['parts'][voice][number-1])
            notes=parse_bar(text)
            if voice in entry.get('silence_last',[]):
                # An optional pickup into another stanza is silent when the piece ends.
                notes[-1]={**notes[-1], 'pitch':'R', 'tie':False}
            parts[voice]=notes
            rows=stanza['lyrics'].get(voice,stanza['lyrics'].get('all'))
            syllables={c['beat']:c['text'] for c in parse_lyrics(rows[number-1])}
            at=offset
            for note in notes:
                text=syllables.get(at-offset)
                if text and note['pitch']!='R':
                    joins=text.endswith('-')
                    syllabic=('middle' if joins else 'end') if lyric_join[voice] else ('begin' if joins else 'single')
                    note['lyric']=dict(text=text.rstrip('-'),syllabic=syllabic)
                    lyric_join[voice]=joins
                if note['pitch']!='R':
                    if pending[voice]:
                        assert events[voice][-1]['pitch']==note['pitch']
                        events[voice][-1]['duration']+=note['duration']
                    else:
                        event=dict(start=at,duration=note['duration'],
                            pitch=note['pitch'],midi=midi_pitch(note['pitch']))
                        # The syllable lets the browser shape a sung vowel; melismas carry none.
                        if 'lyric' in note: event['syllable']=note['lyric']['text']
                        events[voice].append(event)
                else:
                    rests[voice].append((at,at+note['duration']))
                pending[voice]=note['tie']
                at+=note['duration']
            for cue in parse_lyrics(rows[number-1]):
                start=offset+cue['beat']
                if any(a <= start < b for a,b in rests[voice]):
                    continue
                section=section_at(song,number,cue['beat'])
                lyrics[voice].append(dict(start=start,text=cue['text'],measure=number,
                    verse=entry['verse'],section=section,system=system))
        if backing:
            for lane,lane_bars in backing['parts'].items():
                at=offset
                for note in parse_bar(lane_bars[number-1]):
                    if note['pitch']!='R':
                        if backing_pending[lane]:
                            previous=next(event for event in reversed(backing_events) if event['lane']==lane)
                            assert previous['pitch']==note['pitch']
                            previous['duration']+=note['duration']
                        else:
                            backing_events.append(dict(start=at,duration=note['duration'],pitch=note['pitch'],
                                midi=midi_pitch(note['pitch']),lane=lane,instrument='organ'))
                    backing_pending[lane]=note['tie']
                    at+=note['duration']
        bars.append(dict(measure=number,start=offset,parts=parts,verse=entry['verse'],system=system,
                         duration=bar_beats,key_fifths=key_at(song,number),
                         final_return=entry.get('final_return',False)))
        offset+=bar_beats
    duration=offset
    for voice,cues in lyrics.items():
        for i,cue in enumerate(cues):
            end=cues[i+1]['start'] if i+1<len(cues) else duration
            # End highlighting during rests, retaining it over sustained/melismatic notes.
            silence=next((a for a,b in rests[voice] if a>=cue['start']),duration)
            cue['end']=min(end,silence)
    return dict(bars=bars,events=events,backing_events=backing_events,lyrics=lyrics,
                duration=duration,beats_per_bar=beats)


def verse_incipit(song, number, words=4):
    """First few sung words of a stanza's own text (skipping a common opening chorus)."""
    verse=next(v for v in song['verses'] if v['number']==number)
    rows=verse['lyrics'].get('soprano',verse['lyrics'].get('all'))
    start=next((m for m in range(1,len(rows)+1) if section_at(song,m)=='verse'),1)
    text=''
    for row in rows[start-1:]:
        for cue in parse_lyrics(row):
            syllable=cue['text']
            text+=syllable[:-1] if syllable.endswith('-') else syllable+' '
    found=[w.strip('“”"()') for w in text.replace('‿',' ').split()]
    if len(found)>1 and found[0]=='A' and found[1][:1].isupper():
        found=found[1:]  # an introductory pickup "A" before the stanza proper
    chosen=[]
    for word in found[:words]:
        chosen.append(word)
        if len(chosen)>=3 and word[-1:] in ',;:.!?': break
    return ' '.join(chosen).rstrip(',;:.!?')


# Processing records stay in data/ and PROCESSING.md; published files (app API, editions)
# omit credits and sources: these are internal rehearsal copies.
PRIVATE_FIELDS = ('composer', 'arranger', 'sources', 'review_notes', 'review_notes_it', 'source_pdf')


def public(song):
    return {k: v for k, v in song.items() if k not in PRIVATE_FIELDS}


def songs_payload():
    """Song list for the player, each with its all-verses performance (served as api/songs.json)
    and, when parts are recorded, the choir recordings the interactive score plays instead of piano."""
    index = json.loads(RECORDINGS.read_text()) if RECORDINGS.exists() else {'songs': {}}
    payload = []
    for song in load_songs():
        if song.get('hidden'):  # e.g. a transcription being redone: no list, score or booklet entry
            continue
        item = {**public(song),'verses':[{**v,'incipit':verse_incipit(song,v['number'])} for v in song['verses']],
                'performance':performance(song,'all')}
        choir = choir_recordings(song, index['songs'].get(song['id'], []))
        if choir: item['choir'] = choir
        payload.append(item)
    return payload


# Rehearsal recordings (recordings/index.json, written by tools/recordings.py).
RECORDINGS = ROOT/'recordings'/'index.json'
PLAYLIST_VOICES = ('soprano', 'alto', 'tenor', 'bass')
# Albums: "Christmas Carols" (the whole choir, nothing before each song), each voice alone (then the
# shared recordings), and each voice "in evidenza" in the full mix.
ALBUMS = ('choir', *PLAYLIST_VOICES, *(f'lead-{voice}' for voice in PLAYLIST_VOICES))


def choir_recordings(song, entries):
    """The plain part recordings (all verses, from measure 1 beat 1) and the tempo they were made
    at; the score plays them only at that tempo and in the printed key."""
    # Piano parts (songs no synthesizer can sing) are for the playlists only: the score plays its own piano.
    files = {e['voice']: e['file'] for e in entries
             if e['voice'] in PLAYLIST_VOICES and 'transpose' not in e and not e.get('piano')}
    if not files:
        return None
    tempo = next((e['tempo'] for e in entries if e['voice'] in files and 'tempo' in e), song['tempo'])
    return {'tempo': tempo, 'files': files}


def playlist_entries(entries, voice):
    """The recordings a voice's playlist plays for one song: its own part first, then the men
    together (tenor/bass), then the whole choir."""
    shared = ['tenor-bass'] if voice in ('tenor', 'bass') else []
    return [e for wanted in [voice, *shared, 'all'] for e in entries if e['voice'] == wanted]


def recordings_payload():
    """The voice albums (served as api/recordings.json): songs in title order, each with the
    recordings to play. A voice's own track is the built one (spoken title, starting note and
    count-in joined to the part by tools/recordings.py build), followed by shared ones; a
    "lead-<voice>" album plays the full mix with that voice in front."""
    index = json.loads(RECORDINGS.read_text()) if RECORDINGS.exists() else {'songs': {}}
    songs = sorted(load_songs(), key=lambda s: s['title'].casefold())
    playlists = {}
    for album in ALBUMS:
        items = []
        for song in songs:
            entries = index['songs'].get(song['id'], [])
            if album == 'choir':
                tracks = [{'file': e['file'], 'voice': 'choir', 'intro': False, 'seconds': e.get('seconds', 0)}
                          for e in entries if e['voice'] == 'choir']
            elif album.startswith('lead-'):
                voice = album.removeprefix('lead-')
                tracks = [{'file': e['lead'], 'voice': album, 'intro': True, 'seconds': e.get('lead_seconds', 0)}
                          for e in entries if e['voice'] == voice and 'lead' in e]
            else:
                tracks = [{'file': t.get('play', t['file']), 'voice': t['voice'], 'intro': 'play' in t,
                           'seconds': t.get('play_seconds', t.get('seconds', 0))} for t in playlist_entries(entries, album)]
            if tracks:
                items.append({'id': song['id'], 'title': song['title'], 'emoji': song.get('emoji', '🎵'), 'tracks': tracks})
        playlists[album] = items
    return playlists


def recording_files():
    """Every audio file the app may serve: the playlist tracks and the parts the score plays."""
    index = json.loads(RECORDINGS.read_text()) if RECORDINGS.exists() else {'songs': {}}
    choir = {f for song in load_songs() for f in (choir_recordings(song, index['songs'].get(song['id'], [])) or {}).get('files', {}).values()}
    return choir | {t['file'] for items in recordings_payload().values() for item in items for t in item['tracks']}
