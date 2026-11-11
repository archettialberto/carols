"""Scores for a singing synthesizer (MuseScore Studio + Cantai): one SATB MusicXML per song.

    python tools/cantai_scores.py [song-id ...]      # default: every English song

Writes scratch/<song-id>.musicxml (gitignored) from exports/<song-id>.musicxml, which already
unfolds every verse in playback order. Only the sung parts are kept (no organ). The export puts
each stanza on its own lyric line; Cantai sings only line 1 (later stanzas came out as "aah"), so
every syllable moves to line 1. A syllable held over following notes (melisma) gets an extender,
the notation Cantai reads as "keep singing it". Rerun after `python tools/export.py`.
"""
import pathlib
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
VOICES = ('Soprano', 'Alto', 'Tenor', 'Bass')
NOT_ENGLISH = {'dio-ci-benedira'}  # Cantai sings English and Latin only


def prepare(root):
    plist = root.find('part-list')
    keep = {sp.get('id') for sp in plist if sp.tag == 'score-part' and sp.findtext('part-name') in VOICES}
    for element in [e for e in plist if e.tag != 'score-part' or e.get('id') not in keep]:
        plist.remove(element)
    for part in [p for p in root.findall('part') if p.get('id') not in keep]:
        root.remove(part)
    for ly in root.iter('lyric'):
        ly.set('number', '1')
    for part in root.findall('part'):
        last = None  # lyric of the syllable being sung
        for note in part.iter('note'):
            if note.find('rest') is not None:
                last = None
            elif note.find('lyric') is not None:
                last = note.find('lyric')
            elif last is not None and last.find('extend') is None and last.findtext('syllabic') in ('single', 'end'):
                ET.SubElement(last, 'extend')


def main(songs):
    out = ROOT/'scratch'
    out.mkdir(exist_ok=True)
    for song in songs:
        root = ET.parse(ROOT/'exports'/f'{song}.musicxml').getroot()
        prepare(root)
        ET.ElementTree(root).write(out/f'{song}.musicxml', encoding='UTF-8', xml_declaration=True)
        print(f'scratch/{song}.musicxml')


if __name__ == '__main__':
    main(sys.argv[1:] or sorted(p.stem for p in (ROOT/'exports').glob('*.musicxml') if p.stem not in NOT_ENGLISH))
