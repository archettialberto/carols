"""Export the checked score data to portable MusicXML and MIDI, without packages."""
import struct
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from music import ROOT, VOICES, load_songs, parse_bar, performance


def element(parent, tag, value=None, **attributes):
    child=ET.SubElement(parent,tag,attributes)
    if value is not None: child.text=str(value)
    return child


def musicxml(song, verse='all'):
    root=ET.Element('score-partwise',version='4.0')
    element(element(root,'work'),'work-title',song['title'])
    ident=element(root,'identification')
    listing=element(root,'part-list')
    perf=performance(song,verse)
    for i,voice in enumerate(VOICES,1):
        part_id=f'P{i}'
        element(element(listing,'score-part',id=part_id),'part-name',voice.title())
        part=element(root,'part',id=part_id)
        previous_tie=False
        for index,bar in enumerate(perf['bars'],1):
            measure=element(part,'measure',number=str(index))
            if index==1:
                attrs=element(measure,'attributes')
                element(attrs,'divisions',4)
                element(element(attrs,'key'),'fifths',song['key_fifths'])
                time=element(attrs,'time')
                element(time,'beats',song['meter'][0]);element(time,'beat-type',song['meter'][1])
                clef=element(attrs,'clef')
                element(clef,'sign','F' if voice=='bass' else 'G')
                element(clef,'line',4 if voice=='bass' else 2)
                if voice=='tenor': element(clef,'clef-octave-change',-1)
                direction=element(measure,'direction')
                met=element(element(direction,'direction-type'),'metronome')
                element(met,'beat-unit','quarter');element(met,'per-minute',song['tempo'])
                element(direction,'sound',tempo=str(song['tempo']))
            elif bar['key_fifths']!=perf['bars'][index-2]['key_fifths']:
                element(element(element(measure,'attributes'),'key'),'fifths',bar['key_fifths'])
            if bar['final_return'] and bar['measure']==1:
                element(element(element(measure,'direction'),'direction-type'),'words','Return to chorus (D.C. al Fine)')
            for note in bar['parts'][voice]:
                n=element(measure,'note')
                if note['pitch']=='R': element(n,'rest')
                else:
                    p=element(n,'pitch');name=note['pitch']
                    element(p,'step',name[0])
                    if '#' in name or 'b' in name: element(p,'alter',1 if '#' in name else -1)
                    # MusicXML pitches remain sounding pitches even with an octave clef.
                    element(p,'octave',int(name[-1]))
                element(n,'duration',int(note['duration']*4))
                if previous_tie: element(n,'tie',type='stop')
                if note['tie']: element(n,'tie',type='start')
                types={.25:('16th',False),.5:('eighth',False),.75:('eighth',True),
                       1:('quarter',False),1.5:('quarter',True),2:('half',False),3:('half',True),4:('whole',False)}
                kind,dotted=types[note['duration']]
                element(n,'type',kind)
                if dotted: element(n,'dot')
                if previous_tie or note['tie']:
                    notations=element(n,'notations')
                    if previous_tie: element(notations,'tied',type='stop')
                    if note['tie']: element(notations,'tied',type='start')
                if 'lyric' in note:
                    lyric=element(n,'lyric',number=str(bar['verse']))
                    element(lyric,'syllabic',note['lyric']['syllabic'])
                    element(lyric,'text',note['lyric']['text'])
                previous_tie=note['tie']
            if index==len(perf['bars']): element(element(measure,'barline',location='right'),'bar-style','light-heavy')
    backing=song.get('backing_track')
    if backing:
        for lane_number,(lane,source_bars) in enumerate(backing['parts'].items(),len(VOICES)+1):
            part_id=f'P{lane_number}'
            element(element(listing,'score-part',id=part_id),'part-name',f'Organ – {lane.replace("_"," ").title()}')
            part=element(root,'part',id=part_id);previous_tie=False
            for index,bar in enumerate(perf['bars'],1):
                measure=element(part,'measure',number=str(index))
                if index==1:
                    attrs=element(measure,'attributes');element(attrs,'divisions',4)
                    element(element(attrs,'key'),'fifths',song['key_fifths'])
                    time=element(attrs,'time');element(time,'beats',song['meter'][0]);element(time,'beat-type',song['meter'][1])
                    clef=element(attrs,'clef');bass_clef='pedal' in lane.lower() or 'bass' in lane.lower()
                    element(clef,'sign','F' if bass_clef else 'G');element(clef,'line',4 if bass_clef else 2)
                for note in parse_bar(source_bars[bar['measure']-1]):
                    n=element(measure,'note')
                    if note['pitch']=='R': element(n,'rest')
                    else:
                        p=element(n,'pitch');name=note['pitch'];element(p,'step',name[0])
                        if '#' in name or 'b' in name: element(p,'alter',1 if '#' in name else -1)
                        element(p,'octave',int(name[-1]))
                    element(n,'duration',int(note['duration']*4))
                    if previous_tie: element(n,'tie',type='stop')
                    if note['tie']: element(n,'tie',type='start')
                    types={.25:('16th',False),.5:('eighth',False),.75:('eighth',True),
                           1:('quarter',False),1.5:('quarter',True),2:('half',False),3:('half',True),4:('whole',False)}
                    kind,dotted=types[note['duration']];element(n,'type',kind)
                    if dotted: element(n,'dot')
                    if previous_tie or note['tie']:
                        notations=element(n,'notations')
                        if previous_tie: element(notations,'tied',type='stop')
                        if note['tie']: element(notations,'tied',type='start')
                    previous_tie=note['tie']
                if index==len(perf['bars']): element(element(measure,'barline',location='right'),'bar-style','light-heavy')
    ET.indent(root)
    return ET.tostring(root,encoding='utf-8',xml_declaration=True)


def vlq(value):
    result=[value&127]
    while value>>7:
        value>>=7;result.insert(0,(value&127)|128)
    return bytes(result)


def chunk(kind,body):
    return kind+struct.pack('>I',len(body))+body


def midi(song, verse='all'):
    perf=performance(song,verse)
    tempo=round(60_000_000/song['tempo'])
    header=b'\x00\xff\x51\x03'+tempo.to_bytes(3,'big')
    header+=b'\x00\xff\x58\x04'+bytes([song['meter'][0],song['meter'][1].bit_length()-1,24,8])
    header+=b'\x00\xff\x59\x02'+bytes([song['key_fifths'] % 256,0])
    tracks=[chunk(b'MTrk',header+b'\x00\xff\x2f\x00')]
    for channel,voice in enumerate(VOICES):
        notes=[]
        for n in perf['events'][voice]:
            notes.append((round(n['start']*480),1,bytes([0x90+channel,n['midi'],78])))
            notes.append((round((n['start']+n['duration'])*480),0,bytes([0x80+channel,n['midi'],0])))
        name=voice.title().encode()
        body=b'\x00\xff\x03'+vlq(len(name))+name+b'\x00'+bytes([0xC0+channel,0])
        previous=0
        for tick,_,message in sorted(notes):
            body+=vlq(tick-previous)+message;previous=tick
        body+=vlq(round(perf['duration']*480)-previous)+b'\xff\x2f\x00'
        tracks.append(chunk(b'MTrk',body))
    if perf['backing_events']:
        channel=4;notes=[]
        for n in perf['backing_events']:
            notes.append((round(n['start']*480),1,bytes([0x90+channel,n['midi'],68])))
            notes.append((round((n['start']+n['duration'])*480),0,bytes([0x80+channel,n['midi'],0])))
        name=b'Organ';body=b'\x00\xff\x03'+vlq(len(name))+name+b'\x00'+bytes([0xC0+channel,19]);previous=0
        for tick,_,message in sorted(notes):
            body+=vlq(tick-previous)+message;previous=tick
        body+=vlq(round(perf['duration']*480)-previous)+b'\xff\x2f\x00'
        tracks.append(chunk(b'MTrk',body))
    return chunk(b'MThd',struct.pack('>HHH',1,len(tracks),480))+b''.join(tracks)


if __name__=='__main__':
    (ROOT/'exports').mkdir(exist_ok=True)
    for song in load_songs():
        (ROOT/'exports'/f"{song['id']}.musicxml").write_bytes(musicxml(song))
        (ROOT/'exports'/f"{song['id']}.mid").write_bytes(midi(song))
        print(f"{song['title']}: {len(song['parts']['soprano'])} source measures, "
              f"{len(performance(song,'all')['bars'])} played measures; MusicXML + MIDI exported")
