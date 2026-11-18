"""Scores for a singing synthesizer (MuseScore Studio + Cantai): one SATB MusicXML per song.

    python tools/cantai_scores.py [song-id ...]      # default: every English song, and SUNG_AS ones

Writes scratch/<song-id>.musicxml (gitignored) from exports/<song-id>.musicxml, which already
unfolds every verse in playback order. Only the sung parts are kept (no organ). The export puts
each stanza on its own lyric line; Cantai sings only line 1 (later stanzas came out as "aah"), so
every syllable moves to line 1. A syllable held over following notes (melisma) gets an extender,
the notation Cantai reads as "keep singing it". A syllable on a tied-over note (a tie in one voice
under words another voice sings) breaks that tie, so the syllable is sung instead of skipped.
Rerun after `python tools/export.py`.

JOIN lists syllables the printed score staggers between voices that should sound together in the
render: the syllable is sung with the next one, on its note, and its own note keeps the vowel before,
its last eighth on a lead-in vowel (Ding Dong: Gloria's "…o-o-aw-ria", "aw" on beat 1½ and "ria" on
beat 2 in every voice; a "ri" on its own sixteenth came too early in the bass, and "ria" straight
after a long run of "o" syllables still started early in Cantai).
VOWEL gives every note of a long melisma its own vowel syllable ("Glo-o-o-…-o-ria"), so each voice
sings exactly "Glo", then only the vowel, then the next syllable on its own note, with nothing for
the synthesizer to redistribute. A_CAPPELLA songs are rendered for unaccompanied voices: a held
note keeps its printed length (cutting stanza-end chords to one bar made each stanza stop abruptly
and run straight into the next), but one held over a barline that runs straight into the next
phrase gives its last beat to a breath; the last note of each part sounds at most two bars, and bars where no voice sings (organ intros and interludes) are dropped, their key,
time and tempo carried to the next kept bar. The app and the printed PDF keep the score as printed.

SUNG_AS songs also get scratch/<song-id>-<language>.musicxml for an English-only voice: the words
in that language are respelled syllable by syllable so English letter-to-sound rules come out right
(Latin in the ecclesiastical, Italianate way: "ex-cel-sis" → "Eck-shell-cease"). The plain file
stays for a voice that sings the language itself. An English song in SUNG_AS ('english') gets the
same treatment from its ENGLISH entry, for words Cantai's English voice mispronounces.
"""
import copy
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
VOICES = ('Soprano', 'Alto', 'Tenor', 'Bass')
NOT_ENGLISH = {'dio-ci-benedira'}  # Italian: render with Cantai's language set to Latin (see AS_LATIN)
# song → {(syllable, next syllable)} sung together on the next syllable's note
# song → {(syllable, next syllable): vowel sung on the eighth before the two, sung together}
JOIN = {'ding-dong': {('ri', 'a'): 'aw'}}  # Gloria: "…o-o-aw-ria", "aw" on beat 1½ and "ria" on 2 in every voice
# song → {syllable: vowel sung on each following note until the next syllable}
VOWEL = {'ding-dong': {'Glo': 'o'}}
A_CAPPELLA = {'dio-ci-benedira'}
# Cantai sings only English and Latin (its FAQ, 2026-11). Church Latin is pronounced like Italian, so
# these Italian songs' plain file is respelled for Cantai's Latin voice (set the language to Latin).
AS_LATIN = {'dio-ci-benedira'}
SUNG_AS = {'angels-carol': 'latin', 'ding-dong': 'latin', 'dio-ci-benedira': 'italian',
           'we-wish-you-a-merry-christmas': 'english'}
# song → [(whole word, lower case without punctuation, as a regex; {syllable: respelling})], for
# Cantai's English voice (2026-11-18, We Wish You): "Christ" alone was sung "kraist", and "Kriss"
# still slid into the lower note of "mas" (the voiced m), so "Krist" (a stop before the next note)
# and "muss"; the din-don "di-ri" read "di-rai" ("dee-ree"). Matched words sing each syllable as its
# own word, so Cantai does not re-split them by English rules.
ENGLISH = {'we-wish-you-a-merry-christmas': [
    (r'christmas', {'christ': 'krist', 'mas': 'muss'}),
    (r'(diri)+(din)?', {'di': 'dee', 'ri': 'ree', 'din': 'din'}),
]}
# Latin word → {syllable: respelling}; "in" counts as Latin only right before "excelsis"
LATIN = {
    'gloria': {'glo': 'glo', 'o': 'o', 'aw': 'aw', 'ri': 'ree', 'a': 'ah', 'ria': 'ryah'},  # Ding Dong: Glo-o-…-o-aw-ria
    'in': {'in': 'een'},
    'excelsis': {'ex': 'eck', 'cel': 'shell', 'sis': 'cease'},
    'deo': {'de': 'deh', 'o': 'oh'},
    'hosanna': {'ho': 'oh', 'san': 'sahn', 'na': 'nah'},  # h silent
    'io': {'i': 'ee', 'o': 'oh'},  # Ding Dong's "i-o, i-o, i-o"
}
# Italian syllable → respelling: c/g soft before e/i, ch/gh hard ("keh", "gheh"), gn and gli as plain
# n and l (an English voice garbles "ny"/"ly"), z "ts", pure vowels ah/eh/ee/oh/oo, real English words
# where one fits ("chair", "pair"); two vowels on one note are joined by a y/w glide, never an
# h, which would be sounded ("deeyoh", "noween")
ITALIAN = {
    'a': 'ah', 'ar': 'ahr', 'be': 'beh', 'ca': 'kah', 'ce': 'cheh', 'cer': 'chair', 'che': 'keh',
    'chi‿è': 'keeyeh', 'ci': 'chee', 'ci‿a': 'chah', 'ci‿as': 'chahs', 'co': 'koh', 'col': 'kohl',
    'con': 'kohn', 'cuor': 'kwor', 'da': 'dah', 'dal': 'dahl', 'de': 'deh', 'di': 'dee',
    'dio': 'deeyoh', 'dri': 'dree', 'e': 'eh', 'fe': 'feh', 'fi': 'fee', 'fon': 'fohn', 'for': 'fohr',
    'fri': 'free', 'ghe': 'gheh', 'già': 'jah', 'gli': 'lee', 'gni': 'nee', 'gno': 'noh',
    'gui': 'gwee', 'i': 'ee', 'il': 'eel', 'iu': 'yoo', 'las': 'lahs', 'le': 'leh', 'li': 'lee',
    'lo': 'loh', 'lo‿e': 'loweh', 'l’a': 'lah', 'ma': 'mah', 'mi': 'mee', 'mo': 'moh', 'na': 'nah',
    'ne': 'neh', 'ni': 'nee', 'no': 'noh', 'not': 'nawt', 'no‿in': 'noween', 'o': 'oh', 'pa': 'pah',
    'per': 'pair', 'pre': 'preh', 'qui‿il': 'kweel', 'ra': 'rah', 're': 'reh', 're‿e': 'reh',
    'ri': 'ree', 'ro': 'roh', 'rà': 'rah', 'sem': 'sehm', 'si': 'see', 'sia': 'seeyah', 'so': 'soh',
    'sof': 'sohf', 'sul': 'zool', 'sù': 'soo', 'ta': 'tah', 'te': 'teh', 'to': 'toh', 'tro': 'troh',
    'tà': 'tah', 'va': 'vah', 'vin': 'veen', 'za‿in': 'tsayeen', 'zia': 'tsyah',
}
PUNCTUATION = '.,;:!?’‘\'"“”()'
TYPES = {.25: '16th', .5: 'eighth', .75: 'eighth', 1: 'quarter', 1.5: 'quarter', 2: 'half', 3: 'half', 4: 'whole'}


def note_type(note, beats):
    for dot in note.findall('dot'):
        note.remove(dot)
    note.find('type').text = TYPES[beats]
    if beats in (.75, 1.5, 3):
        note.insert(list(note).index(note.find('type')) + 1, ET.Element('dot'))


def join_late(root, pairs):
    """Sing each (syllable, next syllable) of `pairs` as one syllable on the next one's note. The
    note that carried the first goes on with the vowel before it, and its last eighth sings the
    pair's lead-in vowel, so every voice changes vowel on the same eighth before the joined syllable."""
    divisions = int(root.find('.//divisions').text)
    eighth = divisions // 2
    for part in root.findall('part'):
        lyrics = [n.find('lyric') for n in part.iter('note') if n.find('lyric') is not None]
        for this, after in zip(lyrics, lyrics[1:]):
            lead, core, _ = split(this.findtext('text'))
            _, next_core, trail = split(after.findtext('text'))
            vowel = pairs.get((core, next_core))
            if vowel is None:
                continue
            [measure] = [m for m in part.findall('measure') if any(n.find('lyric') is this for n in m.findall('note'))]
            [note] = [n for n in measure.findall('note') if n.find('lyric') is this]
            after.find('text').text = lead + core + next_core + trail
            total = int(note.findtext('duration'))
            if total > eighth:  # keep the vowel before on all but the last eighth
                first = copy.deepcopy(note)
                first.remove(first.find('lyric'))
                first.find('duration').text = str(total - eighth)
                note_type(first, (total - eighth) / divisions)
                note.find('duration').text = str(eighth)
                note_type(note, eighth / divisions)
                for element in (first, note):
                    for beam in element.findall('beam'):
                        element.remove(beam)
                measure.insert(list(measure).index(note), first)
            this.find('syllabic').text = 'middle'
            this.find('text').text = vowel
            for extend in this.findall('extend'):
                this.remove(extend)


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
        order = list(bar)
        divisions = int(root.find('.//divisions').text)
        for i, chain in enumerate(chains):
            total = sum(int(n.findtext('duration')) for n in chain)
            after = order[order.index(chain[-1]) + 1:order.index(chain[-1]) + 2]
            if i == len(chains) - 1:
                limit = min(total, bar[chain[0]] * final_bars)
            elif total >= bar[chain[0]] and after and after[0].find('rest') is None:
                limit = total - divisions  # a breath before the next phrase starts on the beat
            else:
                limit = total
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
    elisions joined into one syllable (a doubled vowel sung once: "qui‿il" → "quil"), split by a space where two vowels would make a Latin diphthong
    (ae, oe, au: "so-lo‿e" → "lo e", not "loe"; an h could be sung as Latin "k", as in "mihi")."""
    import unicodedata
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    text = text.replace('gli', 'li').replace('’', '').replace("'", '')
    text = re.sub(r'([aeiou])‿([aeiou])', lambda m: m[1] if m[1] == m[2] else m[1] + (' ' if m[1] + m[2] in ('ae', 'oe', 'au') else '') + m[2], text)
    return text.replace('‿', '')


def split(text):
    """(leading punctuation, word, trailing punctuation)"""
    core = text.strip(PUNCTUATION)
    start = text.index(core) if core else 0
    return text[:start], core, text[start + len(core):]


def respell_as(root, language, song=''):
    """Respell the words sung in `language` for an English voice, keeping punctuation and capitals."""
    for part in root.findall('part'):
        words, word = [], []  # each word: the lyric elements of its syllables
        for lyric in part.iter('lyric'):
            word.append(lyric)
            if lyric.findtext('syllabic') in ('single', 'end'):
                words.append(word); word = []
        for i, word in enumerate(words):
            texts = [split(lyric.findtext('text')) for lyric in word]
            if language == 'italian':
                table = ITALIAN
            elif language == 'english':
                name = ''.join(core for _, core, _ in texts).lower()
                table = next((t for pattern, t in ENGLISH.get(song, []) if re.fullmatch(pattern, name)), None)
                if table is None:
                    continue
            else:
                name = ''.join(core for _, core, _ in texts).lower()
                name = 'gloria' if re.fullmatch('glo+(aw)?ria', name) else name
                following = ''.join(split(l.findtext('text'))[1] for l in words[i + 1]).lower() if i + 1 < len(words) else ''
                if name not in LATIN or (name == 'in' and following != 'excelsis'):
                    continue
                table = LATIN[name]
            for lyric, (lead, core, trail) in zip(word, texts):
                sung = table[core.lower()]
                lyric.find('text').text = lead + (sung.capitalize() if core[:1].isupper() else sung) + trail
                if language in ('italian', 'english'):
                    # each syllable its own word: Cantai respells a whole word by English rules and
                    # spreads it over the notes, which put "di" of "be-ne-di-rà" and the middle of
                    # "pre-ghe-re-mo" early and made "e-sul-ta" "ee-ee-sul-ta"
                    lyric.find('syllabic').text = 'single'


def main(songs):
    out = ROOT/'scratch'
    out.mkdir(exist_ok=True)
    for song in songs:
        root = ET.parse(ROOT/'exports'/f'{song}.musicxml').getroot()
        prepare(root)
        join_late(root, JOIN.get(song, {}))
        sing_vowel(root, VOWEL.get(song, {}))
        if song in A_CAPPELLA:
            a_cappella(root)
        plain = copy.deepcopy(root)
        if song in AS_LATIN:
            for text in plain.iter('text'):
                text.text = latin_spelling(text.text or '')
        ET.ElementTree(plain).write(out/f'{song}.musicxml', encoding='UTF-8', xml_declaration=True)
        print(f'scratch/{song}.musicxml')
        if song in SUNG_AS:
            respell_as(root, SUNG_AS[song], song)
            ET.ElementTree(root).write(out/f'{song}-{SUNG_AS[song]}.musicxml', encoding='UTF-8', xml_declaration=True)
            print(f'scratch/{song}-{SUNG_AS[song]}.musicxml')


if __name__ == '__main__':
    main(sys.argv[1:] or sorted(p.stem for p in (ROOT/'exports').glob('*.musicxml') if p.stem not in NOT_ENGLISH or p.stem in SUNG_AS))
