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
let lyricSpans = [], zoom = 1;
let emphasizedVoice = null, voiceBuses = {}, digitalView = null, digitalKey = '';
// Each song plays at its own tempo; "Lento" is the only speed control: 0.75× (piano exactly; the
// choir time-stretched, same pitch). There is no bpm field.
const slowRate = .75;
let slow = false;
try { slow = localStorage.getItem('score-slow') === '1'; } catch {}
const playRate = () => slow ? slowRate : 1;
const secondsPerBeat = () => 60 / ((song?.tempo || 96) * playRate());
const currentBeat = () => playing ? anchorBeat + (audio.currentTime - anchorTime) / secondsPerBeat() : position;
const formatTime = seconds => `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
const stanzaLabel = number => t('stanza', {n:number, total:song.verses.length});

function clearAudio() {
  for (const handle of sounding) handle.stop();
  sounding = []; previewNotes.clear(); renderKeys();
  stopChoir();
}

function voiceWeight(voice) {
  // "X in evidenza": the lead stays at gain 1, the other voices drop to .25 (about −12 dB) on piano,
  // quiet enough to follow the lead yet still heard as a mix; sung voices stand out more, so
  // with the recorded choir the others stay at .4 (about −8 dB, as in the playlists).
  const others = choirVoices.size ? .4 : .25;
  return selected.has(voice) ? (emphasizedVoice && voice !== emphasizedVoice ? others : 1) : 0;
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

/* Choir: the recorded parts (MuseScore + Cantai renders of the score, all verses, from measure 1
   beat 1) replace the piano for recorded voices. They play only at the tempo they were made at and
   in the printed key; another tempo or a transposition falls back to the piano. They go through the
   same voice buses, so "in evidenza" and solo modes work unchanged. */
let soundMode = 'choir', choirBuffers = {}, choirSong = null, choirLoading = null, choirSources = [], choirVoices = new Set();
let slowBuffers = {}, slowLoading = null;
const choirRate = 32000;  // plenty for voices, and it keeps phone memory low
const choirLevel = .6;
function choirAllowed() {
  return soundMode === 'choir' && !!song?.choir && transpose === 0 && song.tempo === song.choir.tempo
    && performanceData?.choirOffset != null;
}
function loadChoir() {
  if (!song?.choir) return Promise.resolve();
  if (choirSong === song.id) return choirLoading;
  const id = song.id, Offline = window.OfflineAudioContext || window.webkitOfflineAudioContext;
  choirSong = id; choirBuffers = {}; slowBuffers = {}; slowLoading = null;
  const decoder = new Offline(1, 1, choirRate);
  choirLoading = Promise.all(Object.entries(song.choir.files).map(async ([voice, file]) => {
    const response = await fetch(file);
    if (!response.ok) throw Error(file);
    const buffer = await decoder.decodeAudioData(await response.arrayBuffer());
    if (choirSong === id) choirBuffers[voice] = buffer;
  })).catch(error => console.error('choir', error));  // missing parts simply stay on piano
  return choirLoading;
}
/* Slowed choir: WSOLA time-stretch (40 ms Hann frames, half-frame output hop; each frame is taken
   within ±10 ms of its nominal place where it best continues the previous one), so the pitch stays
   and the parts stay aligned to within the search window. Computed once per song, off the beat. */
async function stretch(input, rate) {
  const n = Math.round(choirRate * .04) & ~1, hop = n / 2, tolerance = Math.round(choirRate * .01);
  const pad = tolerance + n, x = new Float32Array(input.length + 2 * pad); x.set(input, pad);
  const length = Math.ceil(input.length / rate), out = new Float32Array(length + n);
  const window = new Float32Array(n);
  for (let i = 0; i < n; i++) window[i] = .5 - .5 * Math.cos(2 * Math.PI * i / n);
  const similarity = (p, q, step) => { let sum = 0; for (let i = 0; i < hop; i += step) sum += x[p + i] * x[q + i]; return sum; };
  let previous = pad;
  for (let k = 0, at = 0; at < length; k++, at += hop) {
    let pos = pad + Math.round(k * hop * rate);
    if (k) {
      const natural = previous + hop;  // the input that would continue the last frame seamlessly
      let best = pos, score = -Infinity;
      for (let p = pos - tolerance; p <= pos + tolerance; p += 4) { const s = similarity(p, natural, 8); if (s > score) { score = s; best = p; } }
      for (let p = best - 3, around = best, top = -Infinity; p <= around + 3; p++) { const s = similarity(p, natural, 2); if (s > top) { top = s; best = p; } }
      pos = best;
    }
    for (let i = 0; i < n; i++) out[at + i] += x[pos + i] * window[i];
    previous = pos;
    if (k % 300 === 299) await new Promise(resolve => setTimeout(resolve));
  }
  return out.subarray(0, length);
}
function loadSlowChoir() {
  if (slowLoading) return slowLoading;
  const id = song.id;
  slowLoading = loadChoir().then(async () => {
    for (const [voice, buffer] of Object.entries(choirBuffers)) {
      const data = await stretch(buffer.getChannelData(0), slowRate);
      if (choirSong !== id) return;
      const slowed = new AudioBuffer({length:data.length, numberOfChannels:1, sampleRate:choirRate});
      slowed.copyToChannel(data, 0); slowBuffers[voice] = slowed;
    }
  }).catch(error => console.error('slow choir', error));
  return slowLoading;
}
// Beats into the full (all-verses) performance where the current performance starts.
function choirOffset(data) {
  if (!song?.choir) return null;
  const full = song.performance.bars, first = data.bars[0];
  if (data === song.performance) return 0;
  const at = full.findIndex(bar => bar.verse === first.verse && !bar.final_return);
  if (at < 0) return null;
  const same = data.bars.every((bar, i) => full[at + i]?.measure === bar.measure && full[at + i]?.duration === bar.duration);
  return same ? full[at].start - first.start : null;
}
function startChoir() {
  const buffers = slow ? slowBuffers : choirBuffers;
  choirVoices = new Set(choirAllowed() ? voices.filter(voice => buffers[voice]) : []);
  if (!choirVoices.size) return;
  const beat = 60 / (song.choir.tempo * playRate()), offset = (performanceData.choirOffset + position) * beat;
  const remaining = (performanceData.duration - position) * beat;
  // A single verse stops (with a short fade) where the next verse would begin; the end of the song keeps its tail.
  const last = performanceData.choirOffset + performanceData.duration >= song.performance.duration - 1e-6;
  for (const voice of choirVoices) {
    const buffer = buffers[voice];
    if (offset >= buffer.duration) continue;
    const source = audio.createBufferSource(), gain = audio.createGain();
    source.buffer = buffer; gain.gain.value = choirLevel;
    source.connect(gain); gain.connect(voiceBuses[voice]);
    if (last) source.start(anchorTime, offset);
    else {
      source.start(anchorTime, offset, remaining + .15);
      gain.gain.setValueAtTime(choirLevel, anchorTime + remaining);
      gain.gain.linearRampToValueAtTime(0, anchorTime + remaining + .15);
    }
    choirSources.push({source, gain});
  }
}
function stopChoir(fade = 0) {
  for (const {source, gain} of choirSources) {
    try {
      if (fade && audio) { gain.gain.cancelScheduledValues(audio.currentTime); gain.gain.setTargetAtTime(0, audio.currentTime, fade / 4); source.stop(audio.currentTime + fade); }
      else source.stop();
    } catch (_) {}
  }
  choirSources = []; choirVoices = new Set();
}
function renderSound() {
  $('sound-control').hidden = !song?.choir;
  $('sound').value = soundMode;
  renderSummary();
}

function schedule() {
  if (!playing) return;
  const now = audio.currentTime;
  const end = Math.min(performanceData.duration, anchorBeat + (now + .16 - anchorTime) / secondsPerBeat());
  for (const voice of voices) if (!choirVoices.has(voice)) for (const note of performanceData.events[voice]) {
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
/* Locking the phone: the synthesized score cannot keep exact time in the background (timers are
   throttled and iOS interrupts Web Audio), which garbled the notes. Pause cleanly instead; the
   recording playlists play through a media element and keep going with the screen locked. */
document.addEventListener('visibilitychange', () => {
  if (document.hidden) { if (playing || starting) pause(); stopPreviews(); silentMedia?.pause(); }
  else keepAwake();
});
/* Keep the screen on while the app is open (Screen Wake Lock: iOS 16.4+, Android Chrome). */
let wakeLock = null;
async function keepAwake() {
  if (document.hidden || !navigator.wakeLock || (wakeLock && !wakeLock.released)) return;
  try { wakeLock = await navigator.wakeLock.request('screen'); } catch (_) {}
}
for (const type of ['touchend', 'click']) document.addEventListener(type, keepAwake, {passive:true});
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
  clearAudio(); Playlist.pause();
  const request = ++playRequest;
  starting = true;
  try {
    await startAudio();
    if (choirAllowed()) { await loadChoir(); if (slow) await loadSlowChoir(); }
    if (request !== playRequest) return;
    updateAudioMix();
    if (position >= performanceData.duration) position = 0;
    anchorBeat = position; anchorTime = audio.currentTime + .04; scheduledUntil = position;
    playing = true; starting = false; followScore = true;
    closeSheets();
    startChoir(); updateAudioMix();
    for (const voice of voices) if (!choirVoices.has(voice)) for (const note of performanceData.events[voice]) {
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

function pause(atEnd = false) {
  if (playing) position = Math.max(0, Math.min(currentBeat(), performanceData.duration));
  playing = false; starting = false; ++playRequest;
  // At the end of the song the recorded choir rings out instead of stopping dead.
  if (atEnd) { stopChoir(2.5); }
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
  data.choirOffset = choirOffset(data);
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
  zoom = 1; renderScore(); renderDownloads(); preparePerformance(song.performance);
  $('play').disabled = false; $('stop').disabled = false;
  renderLibrary(); renderSummary(); showOrganVolume(); renderSound();
  if (soundMode === 'choir') loadChoir();  // decode in the background, ready for Play
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
  Playlist.pause();
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
  // Songs with a recorded choir: say when the piano plays instead (other tempo or key, or chosen).
  const sound = song.choir && !choirAllowed() ? ` · ${t('soundPiano')}` : '';
  $('summary-detail').textContent = `${verse}${$('voice').selectedOptions[0]?.textContent || ''}${shift}${sound}`;
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
  if (playing && beat >= performanceData.duration) { pause(true); position = performanceData.duration; beat = position; }
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
$('sound').onchange = () => {
  soundMode = $('sound').value; renderSummary();
  if (soundMode === 'choir') loadChoir();
  if (playing) seek(currentBeat(), true);
};
function renderSlow() { $('slow').setAttribute('aria-pressed', String(slow)); }
$('slow').onclick = () => {
  const resume = playing; pause();  // keeps the current beat
  slow = !slow; renderSlow();
  try { localStorage.setItem('score-slow', slow ? '1' : '0'); } catch {}
  updatePosition(true);
  if (slow && choirAllowed()) loadSlowChoir();
  if (resume) play();
};
renderSlow();
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
function renderLibrary() {
  // The same rows as the playlists: cover with the emoji, title and length.
  const clock = s => `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, '0')}`;
  $('song-list').replaceChildren(...songs.map((item,index) => {
    const li = document.createElement('li'); li.className = 'track-row';
    if (item.id === song?.id) li.classList.add('current');
    const button = document.createElement('button'); button.className = 'track-play'; button.type = 'button';
    if (item.id === song?.id) button.setAttribute('aria-current','true');
    // Exactly the Christmas Carols playlist's cover: evergreen with the faint tree behind.
    const cover = Playlist.cover(item, 'cover cover-small', 'choir'); cover.setAttribute('aria-hidden','true');
    const copy = document.createElement('span'); copy.className = 'track-copy';
    const title = document.createElement('span'); title.className = 'track-title'; title.textContent = item.title;
    const detail = document.createElement('span'); detail.className = 'track-detail';
    detail.textContent = clock(item.performance.duration * 60 / (item.tempo || 96));
    copy.append(title, detail); button.append(cover, copy);
    button.onclick = () => {
      Playlist.close();  // opening a score ends the playlist (the score is the interactive view)
      if (song?.id !== item.id) { $('song').value = String(index); chooseSong(); }
      showTab('practice'); $('selection-summary').focus();
    };
    li.append(button); return li;
  }));
  Booklet.render(songs);
}
$('booklet-make').onclick = () => Booklet.make();
$('booklet-all').onchange = event => Booklet.selectAll(event.target.checked);
/* Views: home (three choices), the song list and practice, the voice albums and one playlist, the
   PDF booklet. Each view is a history entry, so the phone's back gesture moves back through them. */
const views = {home:'home-panel', library:'library-panel', practice:'practice-panel', albums:'albums-panel', playlist:'playlist-panel', booklet:'booklet-panel'};
let view = 'home';
function showTab(name, push = true) {
  if (name !== 'practice') { pause(); stopPreviews(); closeSheets(); }
  if (push && name !== view) history.pushState({view:name}, '');
  view = name;
  for (const [key, id] of Object.entries(views)) $(id).hidden = key !== name;
  $('home-button').hidden = name === 'home';
  document.querySelector('.player-dock').hidden = name !== 'practice';
  document.body.classList.toggle('library-open', name !== 'practice');
  for (const key of Object.keys(views)) document.body.classList.toggle(`view-${key}`, key === name);
  renderMiniPlayer();
  if (name === 'practice') { resizeScore(); updatePosition(true); }
  scrollTo(0, 0);
}
// The recordings mini player stays available outside the score (the score has its own dock).
function renderMiniPlayer() {
  // The playing playlist stays reachable everywhere except inside a score (which has its own dock).
  const show = view !== 'practice' && Playlist.hasQueue;
  $('mini-player').hidden = !show; document.body.classList.toggle('mini-open', show);
}
document.addEventListener('playlistchange', renderMiniPlayer);
Playlist.onStart = () => { if (playing || starting) pause(); stopPreviews(); };
addEventListener('popstate', event => showTab(event.state?.view || 'home', false));
$('home-button').onclick = () => { showTab('home'); $('home-panel').focus({preventScroll:true}); };
$('open-library').onclick = () => { showTab('library'); $('library-panel').focus({preventScroll:true}); };
$('open-albums').onclick = () => { showTab('albums'); $('albums-panel').focus({preventScroll:true}); };
$('open-booklet').onclick = () => { showTab('booklet'); $('booklet-panel').focus({preventScroll:true}); };
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
// Desktop: Space plays/pauses the score, or the playlist elsewhere, even when a clicked button
// keeps the focus (it is not also pressed). Fields, selects, checkboxes and the S/A/T/B keys keep Space.
document.addEventListener('keydown', event => {
  if (event.key !== ' ' || event.repeat || event.ctrlKey || event.metaKey || event.altKey) return;
  if (event.target.closest?.('input:not([type="range"]), select, textarea, [contenteditable], .key')) return;
  if (view === 'practice') { event.preventDefault(); play(); }
  else if (Playlist.hasQueue) { event.preventDefault(); Playlist.toggle(); }
});
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
history.replaceState({view:'home'}, ''); showTab('home', false);
fetch('api/songs.json').then(response => { if (!response.ok) throw Error(t('loadError')); return response.json(); }).then(data => {
  songs = data.sort((a,b) => new Intl.Collator('it', {sensitivity:'base', numeric:true}).compare(a.title,b.title)); if (!songs.length) throw Error(t('noScores'));
  $('song').replaceChildren(...songs.map((s, i) => new Option(s.title, i)));
  $('song').disabled = false;
  // The catalogue is the home page and must not depend on successfully engraving
  // the preloaded practice score.
  renderLibrary();
  try { chooseSong(); } catch (error) { showError(error.message); }
  frame();
}).catch(error => showError(error.message));
Playlist.load().catch(error => console.error(error));
keepAwake();
