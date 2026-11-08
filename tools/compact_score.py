"""A printed measure occurs once; alternate stanza syllables share its note grid."""
from copy import deepcopy
from music import VOICES, midi_pitch, parse_bar, performance


ORGAN = ('organ_rh', 'organ_lh')


def organ_staves(song):
    """Per source measure, the organ lanes merged into two chord staves (right/left hand)."""
    lanes = song.get('backing_track', {}).get('parts', {})
    if not lanes: return None
    def mean(bars):
        pitches = [midi_pitch(n['pitch']) for bar in bars for n in parse_bar(bar) if n['pitch'] != 'R']
        return sum(pitches) / len(pitches) if pitches else 60
    hands = {'organ_rh': [l for l, b in lanes.items() if mean(b) >= 60], 'organ_lh': [l for l, b in lanes.items() if mean(b) < 60]}
    out = []
    for index in range(len(song['parts']['soprano'])):
        bar = {}
        for hand, names in hands.items():
            events = []
            for name in names:
                at = 0
                for n in parse_bar(lanes[name][index]):
                    if n['pitch'] != 'R': events.append((at, at + n['duration'], n['pitch'], n['tie']))
                    at += n['duration']
            length = sum(n['duration'] for n in parse_bar(lanes[names[0]][index])) if names else 0
            grid = sorted({0, length} | {a for a, b, p, t in events} | {b for a, b, p, t in events})
            notes = []
            for start, end in zip(grid, grid[1:]):
                sounding = sorted({p for a, b, p, t in events if a <= start < b}, key=midi_pitch, reverse=True)
                held = any(a <= start < b and (end < b or t) for a, b, p, t in events)
                if sounding:
                    notes.append(dict(pitch=sounding[0], pitches=sounding, duration=end - start, tie=held, lyrics=[]))
                else:
                    notes.append(dict(pitch='R', duration=end - start, tie=False, lyrics=[]))
            bar[hand] = notes
        out.append(bar)
    return out


def compact_score(song):
    # The first time each verse plays each source measure (verses may use different measures).
    played={}
    for verse in song['verses']:
        first={}
        for bar in performance(song,verse['number'])['bars']:
            first.setdefault(bar['measure'],bar)
        played[verse['number']]=first
    count=len(song['parts']['soprano'])
    bars=[]
    variants=[]
    for index in range(count):
        singing=[n for n in played if index+1 in played[n]]
        versions=[{index:played[n][index+1]} for n in singing]
        bar=deepcopy(versions[0][index])
        bar['lyric_numbers']=singing
        for voice in VOICES:
            sequences=[]
            lyric_maps=[]
            boundaries=set()
            for version in versions:
                sequence=[];lyrics={};at=0
                for note in version[index]['parts'][voice]:
                    sequence.append((at,at+note['duration'],note))
                    boundaries.update((at,at+note['duration']))
                    if 'lyric' in note: lyrics[at]=note['lyric']
                    at+=note['duration']
                sequences.append(sequence);lyric_maps.append(lyrics)
            grid=sorted(boundaries)
            merged=[]
            for start,end in zip(grid,grid[1:]):
                originals=[next(n for a,b,n in sequence if a<=start<b) for sequence in sequences]
                if len({n['pitch'] for n in originals})!=1:
                    raise ValueError(f"{voice}, measure {index+1}: a pitch variant needs separate notation")
                first_end=next(b for a,b,n in sequences[0] if a<=start<b)
                note=deepcopy(originals[0])
                note['duration']=end-start
                note['tie']=note['pitch']!='R' and (end<first_end or originals[0]['tie'])
                note.pop('lyric',None)
                note['lyrics']=[deepcopy(lyrics.get(start)) for lyrics in lyric_maps]
                merged.append(note)
                # Only the engraving splits a sustained base note; its sounding duration is retained.
                if end<first_end and note['pitch']!='R':
                    stanzas=[number for number,sequence in zip(singing,sequences)
                             if any(a==end for a,b,n in sequence)]
                    variants.append(dict(voice=voice,measure=index+1,beat=end,verses=stanzas))
                    note['annotation']='*'
            bar['parts'][voice]=merged
        bars.append(bar)

    # Verses may reach a measure at different times: the printed edition lays measures out once,
    # in source order, so give them consecutive start positions.
    at=0
    for bar in bars:
        offset=at-bar['start']
        bar['start']=at
        for notes in bar['parts'].values():
            for note in notes:
                if 'start' in note: note['start']+=offset
        at+=bar['duration']

    organ = organ_staves(song)
    if organ:
        for bar in bars: bar['parts'].update(deepcopy(organ[bar['measure'] - 1]))

    # Layout choices live in each song's optional `compact` block.
    layout=song.get('compact',{})
    refrain=layout.get('refrain_measures')
    shared=song.get('shared_lyrics',False)
    sections=[]
    for bar in bars:
        m=bar['measure']
        chorus=bool(refrain) and refrain[0]<=m<=refrain[1]
        part='chorus' if chorus else 'verse'
        last=sections[-1] if sections else None
        same_refrain=chorus and layout.get('merge_refrain_systems',False)
        numbers=[] if chorus or len(song['verses'])==1 else bar['lyric_numbers']
        if (last is None or last['part']!=part or (last['system']!=bar['system'] and not same_refrain)
                or last['lyric_numbers']!=numbers):
            sections.append(dict(system=bar['system'],part=part,bars=[],lyric_numbers=numbers))
        sections[-1]['bars'].append(bar)
        for voice,notes in bar['parts'].items():
            if voice in ORGAN: continue
            for note in notes:
                if chorus:
                    note['lyrics']=note['lyrics'][:1]
                    for rule in layout.get('lyric_replace',[]):
                        if rule['measure']==m and note['lyrics'][0] and note['lyrics'][0]['text']==rule['from']:
                            note['lyrics'][0]['text']=rule['to']
                elif m in layout.get('refrain_pickup_measures',[]):
                    # A common refrain pickup is printed once rather than on every stanza row.
                    first=note['lyrics'][0] if note['lyrics'] else None
                    for lyric in note['lyrics'][1:]:
                        if lyric and first and lyric['text']==first['text'] and first['syllabic']==lyric['syllabic']:
                            lyric.clear()
                own=layout.get('voice_lyrics',{}).get(voice)
                if shared and voice!='soprano' and not (own and own[0]<=m<=own[1]):
                    # The words and their timing are shared by all voices: one readable set is enough,
                    # except where the print gives a part its own staggered words.
                    note['lyrics']=[]
        for mark in layout.get('annotations',[]):
            if mark['measure']!=m: continue
            notes=bar['parts'][mark.get('voice','soprano')]
            if 'beat' in mark:
                at=0
                for note in notes:
                    if at==mark['beat']: note['annotation']=mark['text']
                    at+=note['duration']
            else: notes[mark.get('note',0)]['annotation']=mark['text']

    instructions=layout.get('instructions','')
    notes=[]
    names={'soprano':'Soprano','alto':'Contralto','tenor':'Tenore','bass':'Basso'}
    # One footnote per group of stanzas: list voices only when not all four rearticulate.
    groups={}
    for variant in variants:
        groups.setdefault(tuple(variant['verses']),{}).setdefault(variant['measure'],[]).append(variant['voice'])
    for verses,measures in groups.items():
        by_voices={}
        for measure,group in measures.items():
            by_voices.setdefault(tuple(v for v in names if v in group),[]).append(measure)
        for voices,numbers in by_voices.items():
            who='Tutte le voci' if len(voices)==4 else ', '.join(names[v] for v in voices)
            where=('battuta ' if len(numbers)==1 else 'battute ')+' e '.join(map(str,sorted(numbers)))
            notes.append(f"* {who}, {where}: nella strofa {', '.join(map(str,verses))} non si esegue "
                         f"la legatura: le due note sono riarticolate.")
    notes+=layout.get('notes',[])
    return dict(bars=bars,sections=sections,variants=variants,instructions=instructions,notes=notes)
