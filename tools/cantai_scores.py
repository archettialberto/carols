"""Scores for a singing synthesizer (MuseScore Studio + Cantai): one SATB MusicXML per song.

    python tools/cantai_scores.py [song-id ...]      # default: every English song

Writes scratch/<song-id>.musicxml (gitignored) from exports/<song-id>.musicxml, which already
unfolds every verse in playback order. Only the sung parts are kept (no organ). The export puts
each stanza on its own lyric line; Cantai sings only line 1 (later stanzas came out as "aah"), so
every syllable moves to line 1. A syllable held over following notes (melisma) gets an extender,
the notation Cantai reads as "keep singing it". A syllable on a tied-over note (a tie in one voice
under words another voice sings) breaks that tie, so the syllable is sung instead of skipped.
Rerun after `python tools/export.py`.

LATE lists syllables the printed score staggers between voices that should sound together in the
render: the note carrying the syllable is split, the first part continuing the previous vowel and
only the last part singing it (Ding Dong: "ri-" of Gloria only on the last sixteenth before "a", in every voice).
VOWEL gives every note of a long melisma its own vowel syllable ("Glo-o-o-…-ri-a"), so each voice
sings exactly "Glo", then only the vowel, then the next syllable on its own note, with nothing for
the synthesizer to redistribute. A_CAPPELLA songs are rendered for unaccompanied voices: a held
note (tied chain) sounds at most one full bar, the last note of each part at most two, the rest
becomes rests, and bars where no voice sings (organ intros and interludes) are dropped, their key,
time and tempo carried to the next kept bar. The app and the printed PDF keep the score as printed.
"""
import copy
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
VOICES = ('Soprano', 'Alto', 'Tenor', 'Bass')
NOT_ENGLISH = {'dio-ci-benedira'}  # Italian: render on its own with Cantai's language set to Italian
# song → {(part name, syllable): quarter beats the syllable keeps at the end of its note}
LATE = {'ding-dong': {(voice, 'ri'): .25 for voice in VOICES}}  # "ri" only on the last 16th before "a"
# song → {syllable: vowel sung on each following note until the next syllable}
VOWEL = {'ding-dong': {'Glo': 'o'}}
A_CAPPELLA = {'dio-ci-benedira'}
# Cantai now sings Italian (experimental; language chosen in the Cantai window under the singer's
# name, for the whole score). Songs listed here would instead be respelled for its Latin voice.
AS_LATIN = set()
TYPES = {.25: '16th', .5: 'eighth', .75: 'eighth', 1: 'quarter', 1.5: 'quarter', 2: 'half', 3: 'half', 4: 'whole'}


def note_type(note, beats):
    for dot in note.findall('dot'):
        note.remove(dot)
    note.find('type').text = TYPES[beats]
    if beats in (.75, 1.5, 3):
        note.insert(list(note).index(note.find('type')) + 1, ET.Element('dot'))


def sing_late(root, late):
    """Split each note carrying one of `late`'s syllables: the vowel before goes on, the syllable
    takes only the last part."""
    divisions = int(root.find('.//divisions').text)
    names = {sp.get('id'): sp.findtext('part-name') for sp in root.find('part-list') if sp.tag == 'score-part'}
    for part in root.findall('part'):
        for measure in part.findall('measure'):
            for note in list(measure.findall('note')):
                lyric = note.find('lyric')
                keep = late.get((names[part.get('id')], lyric.findtext('text') if lyric is not None else None))
                total = int(note.findtext('duration'))
                if not keep or total <= keep * divisions:
                    continue
                first = copy.deepcopy(note)
                first.remove(first.find('lyric'))
                first.find('duration').text = str(total - int(keep * divisions))
                note_type(first, (total - keep * divisions) / divisions)
                note.find('duration').text = str(int(keep * divisions))
                note_type(note, keep)
                for element in (first, note):
                    for beam in element.findall('beam'):
                        element.remove(beam)
                measure.insert(list(measure).index(note), first)


def untie(note, kind):
    for tie in note.findall(f"tie[@type='{kind}']"):
        note.remove(tie)
    for notations in note.findall('notations'):
        for tied in notations.findall(f"tied[@type='{kind}']"):
            notations.remove(tied)
        if not len(notations):
            note.remove(notations)


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
        previous = None  # the last sounding note
        for note in part.iter('note'):
            if note.find('rest') is not None:
                previous = None; continue
            if previous is not None and note.find('lyric') is not None and note.find("tie[@type='stop']") is not None:
                untie(previous, 'start'); untie(note, 'stop')
            previous = note
    for part in root.findall('part'):
        last = None  # lyric of the syllable being sung
        for note in part.iter('note'):
            if note.find('rest') is not None:
                last = None
            elif note.find('lyric') is not None:
                last = note.find('lyric')
            elif last is not None and last.find('extend') is None and last.findtext('syllabic') in ('single', 'end'):
                ET.SubElement(last, 'extend')


def sing_vowel(root, vowels):
    for part in root.findall('part'):
        held = None  # the vowel continuing the current syllable, until the next one
        for note in part.iter('note'):
            lyric = note.find('lyric')
            if note.find('rest') is not None:
                continue  # the printed melisma runs on across rests (lower voices re-enter on "o")
            if lyric is not None:
                held = vowels.get(lyric.findtext('text'))
                if held:
                    lyric.find('syllabic').text = 'begin'
                    for extend in lyric.findall('extend'):
                        lyric.remove(extend)
            elif held and note.find("tie[@type='stop']") is None:
                vowel = ET.SubElement(note, 'lyric', number='1')
                ET.SubElement(vowel, 'syllabic').text = 'middle'
                ET.SubElement(vowel, 'text').text = held


def to_rest(note):
    """Turn a held-over note into a rest of the same length."""
    for tag in ('pitch', 'tie', 'notations', 'lyric', 'beam'):
        for element in note.findall(tag):
            note.remove(element)
    note.insert(0, ET.Element('rest'))


def a_cappella(root, final_bars=2):
    parts = root.findall('part')
    for part in parts:
        bar = {}  # note → length of the bar it starts in
        for measure in part.findall('measure'):
            length = sum(int(n.findtext('duration')) for n in measure.findall('note'))
            for note in measure.findall('note'):
                bar[note] = length
        chains, chain = [], []
        for note in bar:
            if note.find('rest') is not None:
                continue
            if not chain or chain[-1].find("tie[@type='start']") is None:
                chain = [note]; chains.append(chain)
            else:
                chain.append(note)
        for i, chain in enumerate(chains):
            limit = bar[chain[0]] * (final_bars if i == len(chains) - 1 else 1)
            held = 0
            for note in chain:
                duration = int(note.findtext('duration'))
                if held >= limit:
                    to_rest(note)
                elif held + duration > limit:
                    untie(note, 'start')
                    rest = copy.deepcopy(note)
                    to_rest(rest)
                    note.find('duration').text = str(limit - held)
                    rest.find('duration').text = str(held + duration - limit)
                    divisions = int(root.find('.//divisions').text)
                    note_type(note, (limit - held) / divisions)
                    note_type(rest, (held + duration - limit) / divisions)
                    siblings = [m for m in part.findall('measure') if note in list(m)][0]
                    siblings.insert(list(siblings).index(note) + 1, rest)
                elif held + duration == limit:
                    untie(note, 'start')
                held += duration
    # drop bars where every voice rests, carrying their notation to the next kept bar
    measures = list(zip(*(p.findall('measure') for p in parts)))
    carried = [[] for _ in parts]
    kept = []
    for column in measures:
        silent = all(n.find('rest') is not None for m in column for n in m.findall('note'))
        for k, (part, measure) in enumerate(zip(parts, column)):
            if silent:
                carried[k] += [e for e in measure if e.tag in ('attributes', 'direction', 'barline')]
                part.remove(measure)
                continue
            for element in carried[k]:
                if element.tag == 'barline':
                    continue
                if element.tag == 'attributes' and measure.find('attributes') is not None:
                    own = measure.find('attributes')
                    for i, child in enumerate(element):
                        if own.find(child.tag) is None:
                            own.insert(i, child)
                    continue
                measure.insert(1 if measure[0].tag == 'attributes' and element.tag == 'direction' else 0, element)
            carried[k] = [e for e in carried[k] if e.tag == 'barline']
        if not silent:
            kept.append(column)
    for k, part in enumerate(parts):
        last = part.findall('measure')[-1]
        for barline in carried[k]:
            if last.find('barline') is None:
                last.append(barline)
    for number, column in enumerate(kept, 1):
        for measure in column:
            measure.set('number', str(number))


def latin_spelling(text):
    """Italian lyric text that Cantai's Latin voice pronounces as Italian: no accents, "gli" as "li",
    elisions joined into one syllable, and a silent h where two vowels would make a Latin diphthong."""
    import unicodedata
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    text = text.replace('gli', 'li').replace('’', '').replace("'", '')
    text = re.sub(r'([aeiou])‿([aeiou])', lambda m: m[1] + ('h' if m[1] + m[2] in ('ae', 'oe', 'au') else '') + m[2], text)
    return text.replace('‿', '')


def main(songs):
    out = ROOT/'scratch'
    out.mkdir(exist_ok=True)
    for song in songs:
        root = ET.parse(ROOT/'exports'/f'{song}.musicxml').getroot()
        prepare(root)
        sing_late(root, LATE.get(song, {}))
        sing_vowel(root, VOWEL.get(song, {}))
        if song in A_CAPPELLA:
            a_cappella(root)
        if song in AS_LATIN:
            for text in root.iter('text'):
                text.text = latin_spelling(text.text or '')
        ET.ElementTree(root).write(out/f'{song}.musicxml', encoding='UTF-8', xml_declaration=True)
        print(f'scratch/{song}.musicxml')


if __name__ == '__main__':
    main(sys.argv[1:] or sorted(p.stem for p in (ROOT/'exports').glob('*.musicxml') if p.stem not in NOT_ENGLISH))
