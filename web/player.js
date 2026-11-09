/* A local score player. Audio, the score marker, and lyric cues share one beat clock. */
const $ = id => document.getElementById(id);
const voices = ['soprano', 'alto', 'tenor', 'bass'];
const selected = new Set(voices);
let songs = [], song, performanceData, segments = [];
let audio, master, backingBus, playing = false, starting = false, position = 0;
let anchorTime = 0, anchorBeat = 0, scheduledUntil = 0, timer, playRequest = 0, loadRequest = 0;
let sounding = [], activeSystem, displayedSegment = -1, followScore = true;
const previewNotes = new Map();  // voice → held starting-note handle
let transpose = 0;  // semitones; every song starts at its printed key
let lyricSpans = [], zoom = 1, previousTempo = 96;
let emphasizedVoice = null, voiceBuses = {}, digitalView = null, digitalKey = '';
const secondsPerBeat = () => 60 / Number($('tempo').value);
const currentBeat = () => playing ? anchorBeat + (audio.currentTime - anchorTime) / secondsPerBeat() : position;
const formatTime = seconds => `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
const stanzaLabel = number => t('stanza', {n:number, total:song.verses.length});

function clearAudio() {
  for (const handle of sounding) handle.stop();
  sounding = []; previewNotes.clear(); renderKeys();
}

function voiceWeight(voice) {
  // "X in evidenza": the lead stays at gain 1, the other voices drop to .25 (about −12 dB),
  // quiet enough to follow the lead yet still heard as a mix.
  return selected.has(voice) ? (emphasizedVoice && voice !== emphasizedVoice ? .25 : 1) : 0;
}
// Organ (backing track) volume from the options sheet: 0–150%, remembered on this device.
let organVolume = 1, backingKind = 'organ', backingOnly = false;
try { organVolume = Math.min(1.5, Math.max(0, Number(localStorage.getItem('organVolume') ?? 1))); } catch {}
function showOrganVolume() {
  $('organ-control').hidden = !song?.backing_track;
  document.querySelectorAll('#voice .backing-mode').forEach(option => option.hidden = option.disabled = !song?.backing_track);
  if (!song?.backing_track && $('voice').value.startsWith('backing:')) { $('voice').value = 'all'; $('voice').onchange(); }
  $('organ-volume').value = Math.round(organVolume * 100); $('organ-value').textContent = `${Math.round(organVolume * 100)}%`;
}
$('organ-volume').oninput = () => {
  organVolume = Number($('organ-volume').value) / 100; showOrganVolume();
  try { localStorage.setItem('organVolume', organVolume); } catch {}
  updateAudioMix();
};
function updateAudioMix() {
  if (!audio || !master) return;
  const backingLevel = performanceData?.backing_events?.length ? .38 * organVolume : 0;
  const energy = voices.reduce((sum,voice) => sum+voiceWeight(voice)**2,0) + backingLevel**2;
  for (const voice of voices) {
    voiceBuses[voice].gain.cancelScheduledValues(audio.currentTime);
    voiceBuses[voice].gain.setTargetAtTime(voiceWeight(voice),audio.currentTime,.025);
  }
  backingBus.gain.cancelScheduledValues(audio.currentTime);
  backingBus.gain.setTargetAtTime(backingLevel,audio.currentTime,.025);
  master.gain.cancelScheduledValues(audio.currentTime);
  master.gain.setTargetAtTime(.65/Math.sqrt(Math.max(1,energy)),audio.currentTime,.025);
}
function tone(note, start, duration, voice, preview = false) {
  const handle = Sounds.play(audio, preview ? audio.destination : voiceBuses[voice], {
    midi:note.midi + transpose, start, duration, kind:'piano', level:preview ? .085 : .11});
  sounding.push(handle);
  handle.onended = () => {
    sounding = sounding.filter(item => item !== handle);
    if (previewNotes.get(voice) === handle) { previewNotes.delete(voice); renderKeys(); }
  };
  return handle;
}
function backingTone(note, start, duration) {
  const handle = Sounds.play(audio, backingBus, {
    midi:note.midi + transpose, start, duration, kind:backingKind, level:backingKind === 'piano' ? .12 : .09});
  sounding.push(handle);
  handle.onended = () => { sounding = sounding.filter(item => item !== handle); };
  return handle;
}

function schedule() {
  if (!playing) return;
  const now = audio.currentTime;
  const end = Math.min(performanceData.duration, anchorBeat + (now + .16 - anchorTime) / secondsPerBeat());
  for (const voice of voices) for (const note of performanceData.events[voice]) {
    if (note.start < scheduledUntil || note.start >= end) continue;
    const at = anchorTime + (note.start - anchorBeat) * secondsPerBeat();
    const noteEnd = at + note.duration * secondsPerBeat();
    if (noteEnd > now) tone(note, Math.max(now, at), Math.max(.01, noteEnd - Math.max(now, at)), voice);
  }
  for (const note of performanceData.backing_events || []) {
    if (note.start < scheduledUntil || note.start >= end) continue;
    const at = anchorTime + (note.start - anchorBeat) * secondsPerBeat();
    const noteEnd = at + note.duration * secondsPerBeat();
    if (noteEnd > now) backingTone(note, Math.max(now, at), Math.max(.01, noteEnd - Math.max(now, at)));
  }
  scheduledUntil = end;
}

/* iPhone: Web Audio is silenced by the ring/silent switch unless the page also plays
   "media". Ask for a playback audio session (Safari 17+) and keep a silent <audio>
   element playing; both must start inside a user gesture (click/touchend). */
let silentMedia;
function silentWav() {
  const rate = 8000, samples = rate / 2, bytes = new Uint8Array(44 + samples), view = new DataView(bytes.buffer);
  const text = (at, value) => [...value].forEach((c, i) => bytes[at + i] = c.charCodeAt(0));
  text(0, 'RIFF'); view.setUint32(4, 36 + samples, true); text(8, 'WAVEfmt ');
  view.setUint32(16, 16, true); view.setUint16(20, 1, true); view.setUint16(22, 1, true);
  view.setUint32(24, rate, true); view.setUint32(28, rate, true); view.setUint16(32, 1, true); view.setUint16(34, 8, true);
  text(36, 'data'); view.setUint32(40, samples, true); bytes.fill(128, 44);
  return URL.createObjectURL(new Blob([bytes], {type:'audio/wav'}));
}
function unlockAudio() {
  try { if (navigator.audioSession) navigator.audioSession.type = 'playback'; } catch (_) {}
  // Start the silent media first: it moves iOS into the "playback" category before Web Audio runs.
  if (!silentMedia) {
    silentMedia = new Audio(silentWav()); silentMedia.loop = true;
    silentMedia.setAttribute('playsinline', ''); silentMedia.preload = 'auto';
  }
  if (silentMedia.paused) silentMedia.play().catch(() => {});
  const Context = window.AudioContext || window.webkitAudioContext;
  audio ||= new Context();
  if (audio.state !== 'running') audio.resume().catch(() => {});
}
// The first tap anywhere unlocks audio, so the piano keys (pointerdown) also sound on iOS.
for (const type of ['touchend', 'click']) document.addEventListener(type, unlockAudio, {passive:true});
document.addEventListener('visibilitychange', () => { if (document.hidden) silentMedia?.pause(); });
async function startAudio() {
  unlockAudio();
  await audio.resume();
  if (!master) {
    master = audio.createGain(); master.connect(audio.destination);
    for (const voice of voices) { voiceBuses[voice] = audio.createGain(); voiceBuses[voice].connect(master); }
    backingBus = audio.createGain(); backingBus.connect(master);
    updateAudioMix();
  }
}
async function play() {
  if (playing || starting) { pause(); return; }
  if (!selected.size && !backingOnly) { showError(t('selectVoice')); return; }
  clearAudio();
  const request = ++playRequest;
  starting = true;
  try {
    await startAudio();
    if (request !== playRequest) return;
    updateAudioMix();
    if (position >= performanceData.duration) position = 0;
    anchorBeat = position; anchorTime = audio.currentTime + .04; scheduledUntil = position;
    playing = true; starting = false; followScore = true;
    closeSheets();
    for (const voice of voices) for (const note of performanceData.events[voice]) {
      if (note.start < position && note.start + note.duration > position)
        tone(note, anchorTime, (note.start + note.duration - position) * secondsPerBeat(), voice);
    }
    for (const note of performanceData.backing_events || []) {
      if (note.start < position && note.start + note.duration > position)
        backingTone(note, anchorTime, (note.start + note.duration - position) * secondsPerBeat());
    }
    renderPlayButton(); $('error').hidden = true;
    schedule(); timer = setInterval(schedule, 40);
    // If the clock does not move, the browser is still blocking sound: say so instead of staying mute.
    const startedAt = audio.currentTime;
    setTimeout(() => { if (playing && request === playRequest && audio.currentTime <= startedAt) showError(t('audioBlocked')); }, 900);
    updatePosition(true);
  } catch (error) {
    if (request !== playRequest) return;
    pause(); showError(t('audioError', {error:error.message}));
  }
}

function pause() {
  if (playing) position = Math.max(0, Math.min(currentBeat(), performanceData.duration));
  playing = false; starting = false; ++playRequest;
  clearInterval(timer); clearAudio(); renderPlayButton();
}
function renderPlayButton() {
  const icon = document.createElement('span'); icon.setAttribute('aria-hidden','true'); icon.textContent = playing ? 'Ⅱ ' : '▶ ';
  const label = document.createElement('span'); label.className = 'play-label'; label.textContent = t(playing ? 'pause' : 'play');
  $('play').replaceChildren(icon, label);
}
function seek(beat, resume = playing) {
  pause(); position = Math.max(0, Math.min(beat, performanceData.duration));
  updatePosition(true);
  if (resume) { followScore = true; play(); }
}
function showError(message) { $('error').textContent = message; $('error').hidden = false; }

function renderVerseOptions() {
  const value = $('verse').value || 'all';
  $('verse').replaceChildren(new Option(t('allVerses'), 'all'),
    ...song.verses.map(v => new Option(`${t('verseShort',{n:v.number})}${v.incipit ? ` · “${v.incipit}”` : ''}`, String(v.number))));
  $('verse').value = value;
  // A single text needs no stanza choice.
  $('verse').closest('label').hidden = song.verses.length < 2;
}
function preparePerformance(data) {
  performanceData = data;
  updateAudioMix();
  position = 0; segments = [];
  data.bars.forEach((bar, index) => {
    const last = segments.at(-1);
    if (!last || last.system !== bar.system || last.verse !== bar.verse || last.final_return !== bar.final_return) {
      segments.push({system:bar.system, verse:bar.verse, final_return:bar.final_return, start:bar.start, end:bar.start});
    }
    const segment = segments.at(-1);
    segment.end = bar.start + bar.duration;
    bar.segment = segments.length - 1;
  });
  if (activeSystem) activeSystem.hidden = true;
  activeSystem = null; displayedSegment = -1; digitalKey = ''; digitalView = null;
  $('seek').max = data.duration;
  renderKeys();
  updatePosition(true);
}

function chooseSong() {
  ++loadRequest; pause();
  song = songs[Number($('song').value)];
  $('verse').value = 'all'; renderVerseOptions(); $('verse').value = 'all';
  $('verse').disabled = false;
  transpose = 0; renderTransposeOptions();
  $('tempo').value = song.tempo; previousTempo = song.tempo;
  zoom = 1; renderScore(); renderDownloads(); preparePerformance(song.performance);
  $('play').disabled = false; $('stop').disabled = false;
  renderLibrary(); renderSummary(); showOrganVolume();
}
async function chooseVerse() {
  const request = ++loadRequest, id = song.id, verse = $('verse').value;
  const resume = playing; pause(); $('play').disabled = true;
  try {
    let data = song.performance;
    if (verse !== 'all') {
      const response = await fetch(`api/performance/${encodeURIComponent(id)}/${verse}.json`);
      if (!response.ok) throw Error(t('loadError'));
      data = await response.json();
    }
    if (request !== loadRequest) return;
    preparePerformance(data); renderSummary(); $('error').hidden = true; $('play').disabled = false;
    if (resume) play();
  } catch (error) {
    if (request !== loadRequest) return;
    // Retain the last usable performance if a request fails.
    $('play').disabled = false; showError(error.message);
  }
}

function renderScore() {
  $('score').replaceChildren();
  song.systems.forEach((system, systemIndex) => {
    const container = document.createElement('div'); container.className = 'system is-digital'; container.hidden = true;
    container.dataset.system = systemIndex;
    const digital = document.createElement('div'); digital.className = 'digital-notation'; container.append(digital);
    const marker = document.createElement('span'); marker.className = 'digital-cursor'; container.append(marker);
    $('score').append(container);
  });
}
function renderDownloads() {
  if (!song) return;
  // One light digital edition per song; original scans stay private.
  const link = $('download');
  link.href = `exports/${encodeURIComponent(song.id)}-digital.pdf`;
  link.download = `${song.id}.pdf`;
  link.title = t('downloadPDF'); link.setAttribute('aria-label', t('downloadPDF'));
}
function soundingPitch(note) {
  if (!transpose) return note.pitch;
  // Spell transposed pitches with flats in flat keys, sharps otherwise.
  const midi = note.midi + transpose, flats = song.key_fifths < 0 || (transpose < 0 && song.key_fifths === 0);
  const names = flats ? ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B'] : ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'];
  return names[midi % 12] + (Math.floor(midi / 12) - 1);
}
function pitchName(pitch) {
  const names = {C:'Do',D:'Re',E:'Mi',F:'Fa',G:'Sol',A:'La',B:'Si'};
  const named = language === 'it' ? pitch.replace(/^[A-G]/,p => names[p]) : pitch;
  return named.replace('#','♯').replace(/(?<=[A-Za-z])b(?=\d)/,'♭');
}
/* Starting notes behave like piano keys: hold to sustain, several at once for a chord. */
function renderKeys() {
  const group = document.querySelector('.keys');
  if (!group.querySelector('.key')) {
    for (const voice of voices) {
      const key = document.createElement('button'); key.type = 'button'; key.className = 'key'; key.dataset.voice = voice;
      key.innerHTML = '<b></b><small></small>';
      key.addEventListener('pointerdown', event => {
        event.preventDefault(); try { key.setPointerCapture(event.pointerId); } catch (_) {}
        pressKey(voice);
      });
      for (const type of ['pointerup','pointercancel']) key.addEventListener(type, () => releaseKey(voice));
      key.addEventListener('keydown', event => { if ((event.key === ' ' || event.key === 'Enter') && !event.repeat) { event.preventDefault(); pressKey(voice); } });
      key.addEventListener('keyup', event => { if (event.key === ' ' || event.key === 'Enter') releaseKey(voice); });
      key.addEventListener('contextmenu', event => event.preventDefault());
      group.append(key);
    }
  }
  for (const key of group.querySelectorAll('.key')) {
    const voice = key.dataset.voice, note = performanceData?.events[voice]?.[0];
    key.disabled = !note;
    key.querySelector('b').textContent = t(voice)[0];
    key.querySelector('small').textContent = note ? pitchName(soundingPitch(note)) : '';
    key.setAttribute('aria-pressed', String(previewNotes.has(voice)));
    key.setAttribute('aria-label', note ? t('firstNoteOf', {voice:t(voice), pitch:pitchName(soundingPitch(note))}) : t(voice));
    key.title = t('keyHint');
  }
}
const pressedAt = new Map();  // voice → audio time of the key press
const minimumCue = 1.6;  // a quick tap still rings long enough to find the pitch
async function pressKey(voice) {
  const note = performanceData?.events[voice]?.[0];
  if (!note) return;
  if (playing || starting) pause();  // pause without seeking
  pressedAt.set(voice, null);
  try {
    await startAudio();
    previewNotes.get(voice)?.release();
    const at = audio.currentTime + .01, released = pressedAt.get(voice) === undefined;
    // The voice's first sounding pitch, independent of the current mix or cursor.
    const handle = tone(note, at, 12, voice, true);
    previewNotes.set(voice, handle); renderKeys(); $('error').hidden = true;
    if (released) handle.release(at + minimumCue); else pressedAt.set(voice, at);
  } catch (error) { showError(t('audioError',{error:error.message})); }
}
function releaseKey(voice) {
  if (!pressedAt.has(voice)) return;
  const at = pressedAt.get(voice); pressedAt.delete(voice);
  if (at === null) return;  // released before audio started: pressKey schedules the cue
  previewNotes.get(voice)?.release(Math.max(audio.currentTime, at + minimumCue));
}
function stopPreviews() { for (const handle of previewNotes.values()) handle.release(); previewNotes.clear(); renderKeys(); }
function renderSummary() {
  if (!song) return;
  $('summary-song').textContent = song.title;
  const verse = song.verses.length < 2 ? '' : ($('verse').value === 'all' ? t('allVerses') : `${t('verse')} ${$('verse').value}`) + ' · ';
  const shift = transpose ? ` · ${transpose > 0 ? '+' : '−'}${Math.abs(transpose)}` : '';
  $('summary-detail').textContent = `${verse}${$('voice').selectedOptions[0]?.textContent || ''}${shift}`;
  $('selection-summary').setAttribute('aria-label', `${song.title}, ${$('summary-detail').textContent}. ${t('changeSelection')}`);
}
function sectionAt(measure, beat) {
  let name = 'verse';
  for (const section of song.sections || []) {
    const [m,b] = section.at;
    if (measure > m || (measure === m && beat >= b)) name = section.name;
  }
  return name === 'verse' ? 'verseSection' : name;
}

// Lyrics run as one sliding line: the sung syllable stays near the left third, so the words of
// the next bars are always visible ahead of it (read-ahead for singers).
let lyricTimeline = null, lyricIndex = -2;
function renderLyrics() {
  const voice = lyricVoice();
  const timeline = performanceData.lyrics[voice];
  if (timeline === lyricTimeline) return;
  lyricTimeline = timeline; lyricIndex = -2;
  $('lyric-rows').replaceChildren(); lyricSpans = [];
  const text = document.createElement('div'); text.className = 'lyric-text';
  let join = false;
  timeline.forEach((cue, index) => {
    if (index && !join) text.append(document.createTextNode(cue.verse !== timeline[index-1].verse ? ' · ' : ' '));
    const span = document.createElement('span'); span.className = 'syllable';
    span.textContent = cue.text.replace(/-$/, ''); span.dataset.start = cue.start; span.dataset.end = cue.end;
    text.append(span); lyricSpans.push(span); join = cue.text.endsWith('-');
  });
  if (!timeline.length) text.textContent = t('noLyrics');
  $('lyric-rows').append(text);
}

function slideLyrics(beat) {
  let index = -1;
  for (let i = 0; i < lyricSpans.length && Number(lyricSpans[i].dataset.start) <= beat; i++) index = i;
  lyricSpans.forEach((span, i) => {
    const start = Number(span.dataset.start), end = Number(span.dataset.end);
    span.classList.toggle('current', beat >= start && beat < end);
    span.classList.toggle('sung', beat >= end);
  });
  if (index === lyricIndex) return;
  lyricIndex = index;
  const text = $('lyric-rows').firstChild, anchor = lyricSpans[Math.max(index, 0)];
  if (!text || !anchor) return;
  const offset = Math.max(0, anchor.offsetLeft - $('lyric-rows').clientWidth * .25);
  text.style.transform = `translateX(${-offset}px)`;
  $('lyric-rows').classList.toggle('scrolled', offset > 0);  // fade the left edge only once text has left it
}

function resizeScore() {
  if (!activeSystem || $('practice-panel').hidden) return;
  const width = Math.max($('score-viewport').clientWidth, 780) * zoom;
  activeSystem.style.width = `${width}px`;
  const segment = segments[displayedSegment];
  const visibleVoices = voices.filter(voice => selected.has(voice));
  if (!visibleVoices.length) visibleVoices.push(...voices);
  const key = [song.id,segment.start,width/zoom,zoom,language,transpose,visibleVoices.join(',')].join(':');
  if (key !== digitalKey) {
    const bars = performanceData.bars.filter(bar => bar.start >= segment.start && bar.start < segment.end);
    // Shared words are printed once, under the top staff, leaving more room for the music.
    const options = {paddingtop:8, transpose, ...(song.shared_lyrics ? {lyricVoices:visibleVoices.slice(0,1), staffsep:40} : {})};
    digitalView = ScoreNotation.render(activeSystem.querySelector('.digital-notation'),song,bars,
      visibleVoices,Object.fromEntries(voices.map(v => [v,t(v)])),width/zoom,note => seek(note.start,true),options);
    digitalKey = key;
  }
  let height = width*digitalView.height/digitalView.width;
  // Phones: shrink (never below 60%) so score, lyrics and controls fit without scrolling.
  const room = innerHeight - document.querySelector('.player-dock').offsetHeight - $('score-viewport').getBoundingClientRect().top
    - document.querySelector('.lyrics-panel').offsetHeight - 6 + scrollY;
  const fit = matchMedia('(max-width:700px)').matches && zoom === 1 && height > room ? Math.max(.6, room/height) : 1;
  if (fit < 1) { activeSystem.style.width = `${width*fit}px`; height *= fit; }
  activeSystem.style.height = `${height}px`;
  $('zoom-out').disabled = zoom <= .7; $('zoom-in').disabled = zoom >= 1.6;
}
function panToMarker(fraction) {
  const viewport = $('score-viewport');
  const target = fraction * activeSystem.getBoundingClientRect().width - viewport.clientWidth * .45;
  // Near the start of a line keep the clef and voice names visible.
  viewport.scrollLeft = target < 60 ? 0 : target;
}
function updatePosition(forcePan = false) {
  if (!performanceData) return;
  let beat = Math.max(0, currentBeat());
  if (playing && beat >= performanceData.duration) { pause(); position = performanceData.duration; beat = position; }
  $('seek').value = beat;
  const barIndex = Math.max(0,performanceData.bars.findLastIndex(bar => bar.start <= beat));
  const bar = performanceData.bars[barIndex], segment = segments[bar.segment];
  const section = sectionAt(bar.measure, beat-bar.start);
  const text = `${t('verse')} ${bar.verse} · ${t('measure', {n:bar.measure})}${beat >= performanceData.duration ? ' · '+t('finished') : ''}`;
  if ($('position').textContent !== text) $('position').textContent = text;
  // Only informative parts: the stanza when there are several, a named section when the song has them.
  $('section-name').textContent = [song.verses.length > 1 ? stanzaLabel(bar.verse) : '',
    song.sections?.length ? t(section) : ''].filter(Boolean).join(' · ');
  $('time').textContent = `${formatTime(beat * secondsPerBeat())} / ${formatTime(performanceData.duration * secondsPerBeat())}`;
  if (bar.segment !== displayedSegment) {
    if (activeSystem) activeSystem.hidden = true;
    activeSystem = document.querySelector(`[data-system="${bar.system}"]`);
    activeSystem.hidden = false; displayedSegment = bar.segment;
    $('line-position').textContent = t('line', {n:bar.system+1,total:song.systems.length});
    $('previous-line').disabled = bar.segment === 0; $('next-line').disabled = bar.segment === segments.length-1;
    renderLyrics(); resizeScore(); forcePan = true;
  }
  const fraction = digitalView?.update(beat,emphasizedVoice);
  const cursor = activeSystem.querySelector('.digital-cursor');
  cursor.style.left = `${(fraction || 0)*100}%`; cursor.hidden = fraction == null;
  if (fraction != null && (forcePan || (playing && followScore))) panToMarker(fraction);
  slideLyrics(beat);
}

// The words shown are always those of the voice being listened to (soprano for all voices).
function lyricVoice() { return emphasizedVoice || (selected.size === 1 ? [...selected][0] : 'soprano'); }
function changeVoices() {
  updateAudioMix();
  renderSummary();
  resizeScore();
  renderLyrics();
  updatePosition(true);
}
$('voice').onchange = () => {
  const voice = $('voice').value, kind = voice === 'backing:piano' ? 'piano' : 'organ';
  // Accompaniment-only modes: no choir parts; the backing track plays as organ or piano.
  backingOnly = voice.startsWith('backing:');
  if (kind !== backingKind) { backingKind = kind; if (playing) { pause(); play(); } }
  if (backingOnly) { emphasizedVoice = null; selected.clear(); changeVoices(); return; }
  emphasizedVoice = voice.startsWith('lead:') ? voice.split(':')[1] : null;
  selected.clear(); (voice === 'all' || emphasizedVoice ? voices : [voice]).forEach(v => selected.add(v));
  changeVoices();
};
$('play').onclick = play;
$('stop').onclick = () => seek(0, false);
$('song').onchange = chooseSong;
$('verse').onchange = chooseVerse;
$('seek').oninput = () => seek(Number($('seek').value));
$('previous-line').onclick = () => seek(segments[Math.max(0, displayedSegment-1)].start);
$('next-line').onclick = () => seek(segments[Math.min(segments.length-1, displayedSegment+1)].start);
$('zoom-out').onclick = () => { zoom = Math.max(.7, Math.round((zoom-.15)*100)/100); resizeScore(); updatePosition(true); };
$('zoom-in').onclick = () => { zoom = Math.min(1.6, Math.round((zoom+.15)*100)/100); resizeScore(); updatePosition(true); };
// Only a deliberate drag disables follow; a tap on a measure keeps it enabled.
let dragStart;
$('score-viewport').addEventListener('pointerdown', event => { dragStart = event.clientX; });
$('score-viewport').addEventListener('pointermove', event => {
  if (dragStart !== undefined && Math.abs(event.clientX-dragStart) > 12 && playing) followScore = false;
});
window.addEventListener('pointerup', () => { dragStart = undefined; });
window.addEventListener('resize', () => { resizeScore(); updatePosition(true); });
$('tempo').onfocus = () => previousTempo = Number($('tempo').value);
$('tempo').onchange = () => {
  const next = Math.max(40, Math.min(220, Number($('tempo').value) || song.tempo));
  const resume = playing;
  $('tempo').value = previousTempo;
  pause(); $('tempo').value = next; previousTempo = next;
  updatePosition(); if (resume) play();
};
function renderLibrary() {
  $('song-list').replaceChildren(...songs.map((item,index) => {
    const li = document.createElement('li');
    const button = document.createElement('button'); button.className = 'song-card'; button.type = 'button';
    if (item.id === song?.id) button.setAttribute('aria-current','true');
    const icon = document.createElement('span'); icon.className = 'song-icon'; icon.textContent = item.emoji || '🎵'; icon.setAttribute('aria-hidden','true');
    const copy = document.createElement('span'); copy.className = 'song-copy';
    const title = document.createElement('span'); title.className = 'song-title'; title.textContent = item.title;
    const arrow = document.createElement('span'); arrow.className = 'song-arrow'; arrow.textContent = '›'; arrow.setAttribute('aria-hidden','true');
    copy.append(title); button.append(icon,copy,arrow);
    const openPractice = () => {
      if (song?.id !== item.id) { $('song').value = String(index); chooseSong(); }
      showTab('practice'); $('selection-summary').focus();
    };
    li.append(button);
    if (!item.recordings) { button.onclick = openPractice; return li; }
    // Songs with real rehearsal recordings offer a choice between the two ways to practise.
    button.setAttribute('aria-expanded','false');
    const choices = document.createElement('div'); choices.className = 'song-choices'; choices.hidden = true;
    const practice = document.createElement('button'); practice.type = 'button'; practice.textContent = t('modeInteractive'); practice.onclick = openPractice;
    const recordings = document.createElement('button'); recordings.type = 'button'; recordings.textContent = t('modeRecordings');
    recordings.onclick = () => showRecordings(item);
    choices.append(practice, recordings); li.append(choices);
    button.onclick = () => {
      const open = choices.hidden;
      document.querySelectorAll('.song-choices').forEach(el => { el.hidden = true; el.previousElementSibling.setAttribute('aria-expanded','false'); });
      choices.hidden = !open; button.setAttribute('aria-expanded', String(open));
    };
    return li;
  }));
  Booklet.render(songs);
}
$('booklet-make').onclick = () => Booklet.make();
$('booklet-all').onchange = event => Booklet.selectAll(event.target.checked);
function youtubeId(url) {
  const match = /(?:youtu\.be\/|[?&]v=|\/embed\/)([\w-]{11})/.exec(url);
  return match && match[1];
}
function showRecordings(item) {
  $('recordings-title').textContent = item.title;
  $('recordings-list').replaceChildren(...voices.filter(voice => item.recordings[voice]).map(voice => {
    const li = document.createElement('li'), heading = document.createElement('h3'), url = item.recordings[voice];
    heading.textContent = t(voice); li.append(heading);
    const id = youtubeId(url);
    if (id) {
      const frame = document.createElement('iframe');
      frame.src = `https://www.youtube-nocookie.com/embed/${id}`; frame.title = `${item.title} · ${t(voice)}`;
      frame.loading = 'lazy'; frame.allow = 'encrypted-media; picture-in-picture'; frame.allowFullscreen = true;
      li.append(frame);
    } else {
      const player = document.createElement('audio'); player.controls = true; player.preload = 'metadata'; player.src = url;
      // One voice at a time: starting a recording pauses the others.
      player.onplay = () => document.querySelectorAll('#recordings-list audio').forEach(other => other !== player && other.pause());
      li.append(player);
    }
    return li;
  }));
  showTab('recordings'); $('recordings-panel').focus();
}
function showTab(name) {
  const library = name === 'library', recordings = name === 'recordings';
  if (name !== 'practice') { pause(); stopPreviews(); closeSheets(); }
  // Leaving the recordings removes the players, which stops any audio or video.
  if (!recordings) $('recordings-list').replaceChildren();
  $('recordings-panel').hidden = !recordings;
  $('library-panel').hidden = !library; $('practice-panel').hidden = name !== 'practice';
  $('library-back').hidden = library;
  document.querySelector('.player-dock').hidden = name !== 'practice';
  document.body.classList.toggle('library-open',library || recordings);
  if (name === 'practice') { resizeScore(); updatePosition(true); }
}
$('library-back').onclick = () => { showTab('library'); $('library-panel').focus(); };
function renderTransposeOptions() {
  const options = [];
  for (let n = 6; n >= -6; n--) {
    const label = n ? t(Math.abs(n) === 1 ? 'semitone' : 'semitones', {n:(n > 0 ? '+' : '−')+Math.abs(n)}) : t('originalKey');
    options.push(new Option(label, String(n)));
  }
  $('transpose').replaceChildren(...options); $('transpose').value = String(transpose);
}
$('transpose').onchange = () => {
  transpose = Number($('transpose').value);
  renderKeys(); renderSummary(); digitalKey = ''; resizeScore(); updatePosition(true);
  // Reschedule from the current beat so the new key applies at once without moving the transport.
  if (playing) seek(currentBeat(), true);
};
/* The phone selection panel is a small sheet rather than permanent controls. */
function openSheet(name, open) {
  const sheet = $(name), button = $('selection-summary');
  if (open) closeSheets(name);
  document.body.classList.toggle(`${name}-open`, open);
  button.setAttribute('aria-expanded', String(open));
  // Focus the panel, not its first <select>: on iOS a focused select opens the native picker at once.
  if (open) { sheet.tabIndex = -1; sheet.focus({preventScroll:true}); }
}
function closeSheets(except) {
  for (const name of ['selection']) if (name !== except && document.body.classList.contains(`${name}-open`)) openSheet(name, false);
}
$('selection-summary').onclick = () => openSheet('selection', !document.body.classList.contains('selection-open'));
document.querySelectorAll('[data-close]').forEach(button => button.onclick = () => openSheet(button.dataset.close, false));
document.addEventListener('keydown', event => { if (event.key === 'Escape') closeSheets(); });
document.addEventListener('pointerdown', event => {
  if (!event.target.closest('.sheet, #selection-summary, .selection')) closeSheets();
});
function renderThemeButton() {
  const mode = appearance.mode;
  const labels = {system:t('themeSystem'), light:t('themeLight'), dark:t('themeDark')};
  const icons = {system:'◐', light:'☀', dark:'☾'};
  $('theme').dataset.mode = mode;
  $('theme').querySelector('span').textContent = icons[mode];
  const label = `${t('theme')}: ${labels[mode]}`;
  $('theme').title = label; $('theme').setAttribute('aria-label', label);
}
$('theme').onclick = () => {
  const modes = ['system','light','dark'];
  appearance.set(modes[(modes.indexOf(appearance.mode)+1) % modes.length]);
  renderThemeButton();
};
if ('serviceWorker' in navigator && isSecureContext) navigator.serviceWorker.register('sw.js').catch(() => {});
function frame() { updatePosition(); requestAnimationFrame(frame); }
translatePage(); renderThemeButton(); renderPlayButton(); renderKeys();
fetch('api/songs.json').then(response => { if (!response.ok) throw Error(t('loadError')); return response.json(); }).then(data => {
  songs = data.sort((a,b) => new Intl.Collator('it', {sensitivity:'base', numeric:true}).compare(a.title,b.title)); if (!songs.length) throw Error(t('noScores'));
  $('song').replaceChildren(...songs.map((s, i) => new Option(s.title, i)));
  $('song').disabled = false;
  // The catalogue is the home page and must not depend on successfully engraving
  // the preloaded practice score.
  renderLibrary(); showTab('library');
  try { chooseSong(); } catch (error) { showError(error.message); }
  frame();
}).catch(error => showError(error.message));
