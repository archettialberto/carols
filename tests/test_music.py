import copy
import unittest
import xml.etree.ElementTree as ET
from music import VOICES, ROOT, load_songs, parse_bar, performance, section_at, validate
from tools.export import midi, musicxml


class ScoresTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.songs={s['id']:s for s in load_songs()}

    def test_all_measures_and_scan_assets(self):
        for song in self.songs.values():
            validate(song)
            for system in song['systems']:
                # Scans and their crops are private (gitignored); check them where available.
                if (ROOT/song['source_pdf']).is_file():
                    self.assertTrue((ROOT/'web'/system['image']).is_file())
                lines=system['barlines']
                self.assertTrue(all(0<=x<=1 for x in lines))
                self.assertEqual(lines,sorted(set(lines)))

    def test_return_stops_at_fine_without_verse_pickup(self):
        song=self.songs['jingle-bells'];p=performance(song)
        self.assertEqual([b['measure'] for b in p['bars']],list(range(1,33))+list(range(1,17)))
        self.assertEqual(p['duration'],96)
        for voice in ('alto','tenor','bass'):
            self.assertNotEqual(p['bars'][15]['parts'][voice][-1]['pitch'],'R')
            self.assertEqual(p['bars'][-1]['parts'][voice][-1]['pitch'],'R')
        self.assertEqual(p['bars'][-1]['parts']['soprano'][-1]['pitch'],'R')

    def test_ties_sustain_but_repeated_notes_rearticulate(self):
        song=copy.deepcopy(self.songs['the-first-nowell'])
        song['parts']['soprano'][0]='A4:1~ A4:1 A4:1'
        notes=performance(song)['events']['soprano']
        self.assertEqual([(n['start'],n['duration']) for n in notes[:2]],[(0,2),(2,1)])
        song['parts']['soprano'][0]='A4:1~ B4:1 A4:1'
        with self.assertRaisesRegex(AssertionError,'broken tie'): validate(song)

    def test_malformed_measure_rejected(self):
        song=copy.deepcopy(self.songs['jingle-bells'])
        song['parts']['alto'][0]='G4:1'
        with self.assertRaisesRegex(AssertionError,'wrong duration'): validate(song)
        with self.assertRaises(ValueError): parse_bar('Q4:1')

    def test_musicxml_has_complete_parts_at_sounding_octaves(self):
        for song in self.songs.values():
            root=ET.fromstring(musicxml(song))
            parts=root.findall('part')
            self.assertEqual(len(parts),4+len(song.get('backing_track',{}).get('parts',{})))
            for voice,part in zip(VOICES,parts):
                self.assertEqual(len(part.findall('measure')),len(performance(song,'all')['bars']))
                expected=sum(4*n['duration'] for bar in performance(song,'all')['bars'] for n in bar['parts'][voice])
                self.assertEqual(sum(int(n.text) for n in part.findall('.//duration')),expected)
            first_tenor=next(n for bar in song['parts']['tenor'] for n in parse_bar(bar) if n['pitch']!='R')
            self.assertEqual(int(parts[2].find('.//pitch/octave').text),int(first_tenor['pitch'][-1]))
            self.assertEqual(parts[2].find('.//clef-octave-change').text,'-1')
            tracks=5+(1 if song.get('backing_track') else 0)  # tempo + SATB (+ organ)
            self.assertTrue(midi(song).startswith(b'MThd\x00\x00\x00\x06\x00\x01\x00'+bytes([tracks])+b'\x01\xe0'))


    def test_all_printed_verses_and_chorus_order(self):
        nowell=performance(self.songs['the-first-nowell'],'all')
        self.assertEqual(len(nowell['bars']),125)
        self.assertEqual([nowell['bars'][i*25]['verse'] for i in range(5)],list(range(1,6)))
        jingle=performance(self.songs['jingle-bells'],'all')
        self.assertEqual(len(jingle['bars']),112)
        self.assertEqual([jingle['bars'][i*32]['verse'] for i in range(3)],[1,2,3])
        self.assertEqual([b['measure'] for b in jingle['bars'][-16:]],list(range(1,17)))
        self.assertEqual(jingle['bars'][-1]['parts']['alto'][-1]['pitch'],'R')
        self.assertEqual(len(performance(self.songs['jingle-bells'],2)['bars']),48)
        with self.assertRaises(ValueError): performance(self.songs['jingle-bells'],99)

    def test_verse_and_voice_specific_lyric_entrances(self):
        jingle=performance(self.songs['jingle-bells'],1)
        self.assertTrue(any(c['start']==33.5 and c['text']=='A' for c in jingle['lyrics']['soprano']))
        self.assertTrue(any(c['start']==32 and c['text']=='Dash-' for c in jingle['lyrics']['alto']))
        nowell=performance(self.songs['the-first-nowell'],'all')
        self.assertTrue(any(c['start']==77 and c['text']=='They' and c['verse']==2 for c in nowell['lyrics']['soprano']))
        self.assertEqual(performance(self.songs['the-first-nowell'],2)['bars'][14]['parts']['tenor'][1]['lyric']['text'],'ued')

    def test_every_syllable_is_attached_to_a_sounding_note(self):
        for song in self.songs.values():
            perf=performance(song,'all')
            for voice in VOICES:
                attached=[]
                for bar in perf['bars']:
                    at=bar['start']
                    for note in bar['parts'][voice]:
                        if 'lyric' in note:
                            self.assertNotEqual(note['pitch'],'R')
                            attached.append((at,note['lyric']['text']))
                        at+=note['duration']
                expected=[(c['start'],c['text'].rstrip('-')) for c in perf['lyrics'][voice]]
                self.assertEqual(attached,expected)
                for cue in perf['lyrics'][voice]:
                    self.assertLess(cue['start'],cue['end'])
                    self.assertLessEqual(cue['end'],perf['duration'])
            root=ET.fromstring(musicxml(song))
            self.assertEqual(len(root.findall('.//lyric')),sum(len(c) for c in perf['lyrics'].values()))


    def test_lyric_on_a_rest_is_rejected(self):
        song=copy.deepcopy(self.songs['jingle-bells'])
        song['verses'][0]['lyrics']['soprano'][16]='0:Wrong'
        with self.assertRaisesRegex(AssertionError,'lyric without note onset'): validate(song)

    def test_form_and_sections_come_from_song_data(self):
        song=copy.deepcopy(self.songs['the-first-nowell'])
        # A final return replays its measures once, silencing a listed pickup.
        song['final_playback']=[{'measure':25,'silence_last':['bass']}]
        p=performance(song,'all')
        self.assertEqual(len(p['bars']),126)
        self.assertTrue(p['bars'][-1]['final_return'])
        self.assertEqual(p['bars'][-1]['parts']['bass'][-1]['pitch'],'R')
        self.assertEqual(p['bars'][-2]['parts']['bass'][-1]['pitch'],'D3')
        self.assertEqual(section_at(song,17,1),'verse')
        self.assertEqual(section_at(song,17,2),'chorus')
        self.assertEqual(section_at(self.songs['jingle-bells'],16,1),'chorus')
        self.assertEqual(section_at(self.songs['jingle-bells'],17),'verse')
        song['sections']=[{'at':[1,0],'name':'refrainish'}]
        with self.assertRaises(AssertionError): validate(song)

    def test_optional_organ_backing_track_is_validated_and_unfolded(self):
        song=copy.deepcopy(self.songs['the-first-nowell'])
        self.assertEqual(performance(song,2)['backing_events'],[])
        song['backing_track']={'instrument':'organ','parts':{
            'manual':list(song['parts']['soprano']),
            'pedal':list(song['parts']['bass']),
        }}
        validate(song)
        perf=performance(song,2)
        self.assertTrue(perf['backing_events'])
        self.assertEqual({event['instrument'] for event in perf['backing_events']},{'organ'})
        self.assertEqual({event['lane'] for event in perf['backing_events']},{'manual','pedal'})
        self.assertEqual(perf['backing_events'][0]['start'],perf['events']['soprano'][0]['start'])
        xml=ET.fromstring(musicxml(song,2))
        self.assertEqual(len(xml.findall('part')),6)
        self.assertEqual([p.find('part-name').text for p in xml.find('part-list').findall('score-part')][-2:],
                         ['Organ – Manual','Organ – Pedal'])
        midi_data=midi(song,2)
        self.assertEqual(int.from_bytes(midi_data[10:12],'big'),6)  # tempo + SATB + organ tracks
        self.assertIn(b'\x00\xc0\x00',midi_data)  # choir program: piano
        self.assertIn(b'\x00\xc4\x13',midi_data)  # accompaniment program: church organ
        broken=copy.deepcopy(song)
        broken['backing_track']['instrument']='piano'
        with self.assertRaisesRegex(AssertionError,'must use organ'): validate(broken)
        broken=copy.deepcopy(song)
        broken['backing_track']['parts']['manual'][0]='C4:1'
        with self.assertRaisesRegex(AssertionError,'wrong duration'): validate(broken)

    def test_sounding_events_carry_their_syllables(self):
        events=performance(self.songs['the-first-nowell'])['events']['soprano']
        # "The" spans F#4–E4: the melisma's second note carries no new syllable.
        self.assertEqual([(e['pitch'],e.get('syllable')) for e in events[:3]],[('F#4','The'),('E4',None),('D4','first')])


if __name__=='__main__': unittest.main()
