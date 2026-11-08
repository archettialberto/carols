"""Printed verses share a note grid; unfolded playback retains its own timing."""
import unittest
from music import VOICES, load_songs, performance
from tools.compact_score import compact_score


class CompactScoreTest(unittest.TestCase):
    def test_source_measures_appear_once(self):
        for song in load_songs():
            compact=compact_score(song)
            count=len(song['parts']['soprano'])
            self.assertEqual([b['measure'] for b in compact['bars']],list(range(1,count+1)))
            self.assertEqual([b['measure'] for sec in compact['sections'] for b in sec['bars']],list(range(1,count+1)))
            if len(song['verses'])>1:
                self.assertLess(len(compact['bars']),len(performance(song,'all')['bars']))

    def test_shared_grid_preserves_base_sounding_music(self):
        for song in load_songs():
            # Songs whose verses use different measures are covered by the per-verse lyric checks.
            if any('playback' in v for v in song['verses']): continue
            compact=compact_score(song)
            base=performance(song)
            for voice in VOICES:
                actual=[];tie=False
                for bar in compact['bars']:
                    at=bar['start']
                    for note in bar['parts'][voice]:
                        if note['pitch']!='R':
                            if tie:
                                self.assertEqual(actual[-1]['pitch'],note['pitch'])
                                actual[-1]['duration']+=note['duration']
                            else: actual.append(dict(start=at,duration=note['duration'],pitch=note['pitch']))
                        tie=note['tie'];at+=note['duration']
                expected=[{key:n[key] for key in ('start','duration','pitch')} for n in base['events'][voice] if n['start']<len(compact['bars'])*base['beats_per_bar']]
                self.assertEqual(actual,expected)

    def test_numbered_stanzas_and_common_refrains(self):
        for song in load_songs():
            compact=compact_score(song)
            for sec in compact['sections']:
                if sec['part']=='verse':
                    # A single text is not numbered; several stanzas are numbered 1..n.
                    # Stanzas are numbered by the verses that actually sing the section.
                    first=sec['bars'][0]['measure']
                    singing=[v['number'] for v in song['verses']
                             if any(e['measure']==first for e in v.get('playback',song['playback']))]
                    numbers=singing if len(song['verses'])>1 else []
                    self.assertEqual(sec['lyric_numbers'],numbers)
                    for bar in sec['bars']:
                        for note in bar['parts']['soprano']:
                            self.assertEqual(len(note['lyrics']),len(singing))
                else:
                    self.assertEqual(sec['lyric_numbers'],[])
                    for bar in sec['bars']:
                        for note in bar['parts']['soprano']: self.assertEqual(len(note['lyrics']),1)

    def test_rhythm_exception_and_da_capo_are_explicit(self):
        songs={s['id']:s for s in load_songs()}
        nowell=compact_score(songs['the-first-nowell'])
        self.assertEqual(nowell['variants'],[dict(voice='tenor',measure=15,beat=1.0,verses=[2])])
        self.assertIn('battuta 15',nowell['notes'][0])
        self.assertTrue(nowell['bars'][14]['parts']['tenor'][0]['tie'])
        jingle=compact_score(songs['jingle-bells'])
        self.assertEqual(jingle['bars'][15]['parts']['soprano'][0]['annotation'],'Fine')
        self.assertEqual(jingle['bars'][-1]['parts']['soprano'][-1]['annotation'],'D.C. al Fine')
        self.assertIn('senza l’anacrusi',jingle['instructions'])


if __name__=='__main__': unittest.main()
