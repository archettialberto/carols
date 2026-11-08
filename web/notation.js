/* Convert the same timed notes used by the player into engraved SVG with abcjs. */
const ScoreNotation = (() => {
  const allVoices = ['soprano','alto','tenor','bass'];
  const lengths = {.25:'/4', .5:'/2', .75:'3/4', 1:'', 1.5:'3/2', 2:'2', 3:'3', 4:'4'};
  const keys = {'-7':'Cb','-6':'Gb','-5':'Db','-4':'Ab','-3':'Eb','-2':'Bb','-1':'F',0:'C',1:'G',2:'D',3:'A',4:'E',5:'B',6:'F#',7:'C#'};
  function pitchToken(pitch, voice, keyFifths, state = new Map(), record = true) {
    if (pitch === 'R') return 'z';
    let octave = Number(pitch.at(-1));
    // treble-8 prints written pitches; the canonical note and Web Audio stay at sounding pitch.
    if (voice === 'tenor') octave++;
    let letter = octave >= 5 ? pitch[0].toLowerCase() : pitch[0];
    letter += octave > 5 ? "'".repeat(octave-5) : octave < 4 ? ','.repeat(4-octave) : '';
    const expected = keyFifths > 0 ? 'FCGDAEB'.slice(0,keyFifths) : 'BEADGCF'.slice(0,-keyFifths);
    const inKey = expected.includes(pitch[0]) ? (keyFifths > 0 ? '#' : 'b') : '';
    const wanted = pitch.includes('#') ? '#' : pitch.includes('b') ? 'b' : '';
    const current = state.has(letter) ? state.get(letter) : inKey;
    const accidental = wanted === current ? '' : wanted === '#' ? '^' : wanted === 'b' ? '_' : '=';
    // abcjs does not let a tied-over note's accidental affect the rest of the bar.
    if (record) state.set(letter,wanted);
    return accidental + letter;
  }
  function build(song, bars, voices = allVoices, names = {}, options = {}) {
    const lines = ['X:1', `M:${song.meter.join('/')}`, 'L:1/4',
      '%%stretchlast 1', `%%staffsep ${options.staffsep || 55}`, '%%vocalfont Georgia 13', '%%annotationfont Georgia 11',
      `%%score [${voices.map((v,i) => v.startsWith('organ') ? '' : 'V'+i).filter(Boolean).join(' ')}]${voices.some(v => v.startsWith('organ')) ? ' {'+voices.map((v,i) => v.startsWith('organ') ? 'V'+i : '').filter(Boolean).join(' ')+'}' : ''}`];
    const clefOf = voice => voice === 'bass' || voice === 'organ_lh' ? 'bass' : voice === 'tenor' ? 'treble-8' : 'treble';
    // A system opens in the key of its first bar; later changes are inline (see below).
    const startKey = bars.length ? (bars[0].key_fifths ?? song.key_fifths) : song.key_fifths;
    voices.forEach((voice,i) => lines.push(`V:V${i} clef=${clefOf(voice)} name="${names[voice] || voice}"`));
    if (options.measureNumbers && bars.length) {
      // Number the first bar of each system with its source measure number.
      lines.push('%%measurenb 0', `%%setbarnb ${bars[0].measure}`);
    }
    lines.push(`K:${keys[startKey]}`);
    let abc = lines.join('\n')+'\n';
    const mapping = new Map(), notes = [];
    voices.forEach((voice,vi) => {
      abc += `[V:V${vi}] `;
      const lyricRows = [];
      let tiedIn = false;
      bars.forEach((bar,mi) => {
        const key = bar.key_fifths ?? song.key_fifths;
        // An inline K: must repeat the clef, otherwise abcjs resets the voice to treble.
        if (key !== (mi ? (bars[mi-1].key_fifths ?? song.key_fifths) : startKey)) abc += `[K:${keys[key]} clef=${clefOf(voice)}] `;
        let at = bar.start;
        const accidentals = new Map();
        // Beam eighths and shorter within one beat group (a half note in 2/2, a dotted quarter
        // in compound 6/8, 9/8, 12/8, else a quarter): abcjs beams notes written without a space.
        const compound = song.meter[1] === 8 && song.meter[0] % 3 === 0;
        const group = song.meter[1] === 2 ? 2 : compound ? 1.5 : 1, measureStart = bar.start;
        const beamed = (a, b, start) => a && b && a.pitch !== 'R' && b.pitch !== 'R' && a.duration < 1 && b.duration < 1 &&
          Math.floor((start - measureStart) / group + 1e-9) === Math.floor((start + a.duration - measureStart) / group + 1e-9);
        bar.parts[voice].forEach((note,ni) => {
          const info = {voice, voiceIndex:vi, measureIndex:mi, noteIndex:ni, measure:bar.measure,
            start:at, end:at+note.duration, pitch:note.pitch, lyrics:note.lyrics === undefined ? [note.lyric] : note.lyrics};
          mapping.set(abc.length,info); notes.push(info);
          const head = note.pitches?.length > 1 ? '['+note.pitches.map(p => pitchToken(p,voice,key,accidentals,!(tiedIn && ni === 0))).join('')+']' : pitchToken(note.pitch,voice,key,accidentals,!(tiedIn && ni === 0));
          abc += (note.annotation ? `"^${note.annotation}"` : '')+head+lengths[note.duration]+(note.tie ? '-' : '')+(beamed(note, bar.parts[voice][ni+1], at) ? '' : ' ');
          // Multiple w: fields share notes. A nonbreaking blank (~) keeps empty
          // cells aligned: abcjs can consume * skips on leading rests.
          if (note.pitch !== 'R' && (!options.lyricVoices || options.lyricVoices.includes(voice))) {
            const lyrics = note.lyrics === undefined ? [note.lyric] : note.lyrics;
            lyrics.forEach((lyric,row) => {
              lyricRows[row] ||= [];
              lyricRows[row].push(lyric?.text ? lyric.text.replace(/_/g,'\\_')+(['begin','middle'].includes(lyric.syllabic) ? '-' : '') : '~');
            });
          }
          at += note.duration; tiedIn = !!note.tie;
        });
        abc += '| ';
      });
      abc += '\n';
      lyricRows.forEach((tokens,row) => {
        const label = options.lyricNumbers?.[row];
        const numbered = tokens.slice();
        const first = numbered.findIndex(token => token !== '~');
        // Keep the stanza number within a syllable: a separate token consumes a note.
        if (label && first >= 0) numbered[first] = label+'.~'+numbered[first];
        abc += 'w: '+numbered.join(' ')+'\n';
      });
    });
    return {abc,mapping,notes};
  }
  function render(target,song,bars,voices,names,width,onSelect,options = {}) {
    const source = build(song,bars,voices,names,options);
    const visual = ABCJS.renderAbc(target,source.abc,{
      staffwidth:Math.max(320,width-36), paddingtop:options.paddingtop ?? 20, paddingbottom:18, paddingleft:18, paddingright:18,
      responsive:'resize', add_classes:true, visualTranspose:options.transpose || 0, staffsep:options.staffsep || 55, showDebug:[],
      ariaLabel:song.title, selectionColor:'#315d49',
      clickListener:element => {
        // abcjs includes leading whitespace for the first note after a bar/voice marker.
        const note = [...source.mapping].find(([at]) => at >= element.startChar && at < element.endChar)?.[1];
        if (note && onSelect) onSelect(note);
      },
    })[0];
    const svg = target.querySelector('svg');
    // abcjs may place a final lyric slightly past its nominal staff width.
    // Include the actual ink bounds so neither the live view nor PDF clips it.
    const ink = svg.getBBox();
    const bounds = svg.viewBox.baseVal;
    const fullWidth = Math.max(bounds.width,ink.x+ink.width+18);
    const fullHeight = Math.max(bounds.height,ink.y+ink.height+12);
    svg.setAttribute('viewBox',`0 0 ${fullWidth} ${fullHeight}`);
    svg.parentElement.style.paddingBottom = `${fullHeight/fullWidth*100}%`;
    const viewBox = svg.viewBox.baseVal;
    const positions = source.notes.map(note => {
      const query = `.abcjs-${note.pitch === 'R' ? 'rest' : 'note'}.abcjs-v${note.voiceIndex}.abcjs-m${note.measureIndex}.abcjs-n${note.noteIndex}`;
      const elements = [...svg.querySelectorAll(query)];
      const box = elements[0]?.getBBox();
      return {...note,elements,x:box ? box.x+Math.min(box.width,12)/2 : null};
    });
    return {
      visual, source, svg, positions, width:viewBox.width, height:viewBox.height,
      update(beat, emphasized) {
        let x = null;
        for (const note of positions) {
          const active = note.pitch !== 'R' && beat >= note.start && beat < note.end;
          for (const element of note.elements) {
            element.classList.toggle('playing-note',active);
            element.classList.toggle('lead-voice',note.voice === emphasized);
            element.classList.toggle('backing-voice',!!emphasized && note.voice !== emphasized);
          }
          if (beat >= note.start && beat < note.end && note.x !== null && (x === null || note.voice === emphasized)) x = note.x;
        }
        return x === null ? null : x / viewBox.width;
      },
    };
  }
  return {build,render,pitchToken};
})();
