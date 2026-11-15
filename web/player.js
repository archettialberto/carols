/* The interactive score and the app's views. Audio, the score cursor and the lyric cues share one
   beat clock. The whole performance (repeats unfolded, every stanza) is engraved as one endless line
   that scrolls under a fixed cursor; Play from the beginning opens like a playlist track, with the
   starting note on the piano and a metronome count-in. */
const $ = id => document.getElementById(id);
const voices = ['soprano', 'alto', 'tenor', 'bass'];
const selected = new Set(voices);
let songs = [], song, performanceData;
let audio, master, backingBus, playing = false, starting = false, position = 0;
let anchorTime = 0, anchorBeat = 0, scheduledUntil = 0, timer, playRequest = 0;
let sounding = [], introNodes = [], intro = null, followScore = true;
let transpose = 0;  // semitones; every song starts at its printed key
let zoom = 1, emphasizedVoice = null, voiceBuses = {}, digitalView = null, digitalKey = '';
let mode = 'all';  // all · lead:<voice> · <voice> (solo) · backing:organ · backing:piano
// Each song plays at its own tempo; "Lento" (0.75×, in the options, off whenever the app opens) is the
// only speed control: the piano exactly, the choir time-stretched at the same pitch.
const slowRate = .75;
let slow = false;
const playRate = () => slow ? slowRate : 1;
const secondsPerBeat = () => 60 / ((song?.tempo || 96) * playRate());
// During the count-in the clock waits at the starting beat.
const currentBeat = () => playing ? anchorBeat + Math.max(0, audio.currentTime - anchorTime) / secondsPerBeat() : position;
const formatTime = UI.clock;

function clearAudio() {
  for (const handle of sounding) handle.stop();
  for (const node of introNodes) { try { node.stop(); } catch (_) {} }
  sounding = []; introNodes = []; intro = null;
  stopChoir();
}

function voiceWeight(voice) {
  // "X in evidenza": the lead stays at gain 1, the other voices drop to .25 (about −12 dB) on piano,
  // quiet enough to follow the lead yet still heard as a mix; sung voices stand out more, so
  // with the recorded choir the others stay at .4 (about −8 dB, as in the playlists).
  const others = choirVoices.size ? .4 : .25;
  return selected.has(voice) ? (emphasizedVoice && voice !== emphasizedVoice ? others : 1) : 0;
}
// Organ (backing track) volume from the options: 0–150%, remembered on this device.
let organVolume = 1, backingKind = 'organ', backingOnly = false;
try { organVolume = Math.min(1.5, Math.max(0, Number(localStorage.getItem('organVolume') ?? 1))); } catch {}
function showOrganVolume() {
  $('organ-control').hidden = !song?.backing_track;
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
  const energy = voices.reduce((sum, voice) => sum + voiceWeight(voice) ** 2, 0) + backingLevel ** 2;
  for (const voice of voices) {
    voiceBuses[voice].gain.cancelScheduledValues(audio.currentTime);
    voiceBuses[voice].gain.setTargetAtTime(voiceWeight(voice), audio.currentTime, .025);
  }
  backingBus.gain.cancelScheduledValues(audio.currentTime);
  backingBus.gain.setTargetAtTime(backingLevel, audio.currentTime, .025);
  master.gain.cancelScheduledValues(audio.currentTime);
  master.gain.setTargetAtTime(.65 / Math.sqrt(Math.max(1, energy)), audio.currentTime, .025);
}
function keep(handle) {
  sounding.push(handle);
  handle.onended = () => { sounding = sounding.filter(item => item !== handle); };
  return handle;
}
function tone(note, start, duration, voice) {
  return keep(Sounds.play(audio, voiceBuses[voice], {midi:note.midi + transpose, start, duration, kind:'piano', level:.11}));
}
function backingTone(note, start, duration) {
  return keep(Sounds.play(audio, backingBus, {midi:note.midi + transpose, start, duration, kind:backingKind, level:backingKind === 'piano' ? .12 : .09}));
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
  return soundMode === 'choir' && !!song?.choir && transpose === 0 && song.tempo === song.choir.tempo;
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
function startChoir() {
  const buffers = slow ? slowBuffers : choirBuffers;
  choirVoices = new Set(choirAllowed() ? voices.filter(voice => buffers[voice]) : []);
  if (!choirVoices.size) return;
  const offset = position * 60 / (song.choir.tempo * playRate());
  for (const voice of choirVoices) {
    const buffer = buffers[voice];
    if (offset >= buffer.duration) continue;
    const source = audio.createBufferSource(), gain = audio.createGain();
    source.buffer = buffer; gain.gain.value = choirLevel;
    source.connect(gain); gain.connect(voiceBuses[voice]);
    source.start(anchorTime, offset);  // the end of the song keeps the recording's tail
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
  scheduledUntil = Math.max(scheduledUntil, end);
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
for (const type of ['touchend', 'click']) document.addEventListener(type, unlockAudio, {passive:true});
/* Locking the phone: the synthesized score cannot keep exact time in the background (timers are
   throttled and iOS interrupts Web Audio), which garbled the notes. Pause cleanly instead; the
   recording playlists play through a media element and keep going with the screen locked. */
document.addEventListener('visibilitychange', () => {
  if (document.hidden) { if (playing || starting) pause(); silentMedia?.pause(); }
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

/* The count-in, only when playing from the beginning, exactly as in the playlist tracks
   (tools/recordings.py): the first note of the voices heard on the app's piano held 1.7 s; 0.35 s after its
   release a metronome tick per beat (a dotted quarter in 6/8-type metres, a half in 2/2), one bar,
   two when a bar has fewer than three beats; the music enters on the next beat. Always audible:
   straight to the output, whatever the mix. */
const cueHeld = 1.7, cueGap = .5 + .35;
function countIn() {
  const [beats, unit] = song.meter, compound = unit === 8 && beats % 3 === 0 && beats > 3;
  const beat = compound ? 1.5 : 4 / unit, perBar = compound ? beats / 3 : beats;
  return {beat, perBar, clicks:perBar * (perBar < 3 ? 2 : 1)};
}
function tick(at, accent) {
  // A short woodblock tick (fundamental and a 2.01× partial); the first beat of the bar is higher.
  const f = accent ? 1760 : 1320, out = audio.createGain();
  out.gain.setValueAtTime(0, at); out.gain.linearRampToValueAtTime(.38, at + .0008); out.gain.setTargetAtTime(0, at + .0008, .012);
  out.connect(audio.destination);
  return [[f, 1], [f * 2.01, .3]].map(([frequency, level]) => {
    const osc = audio.createOscillator(), gain = audio.createGain();
    osc.frequency.value = frequency; gain.gain.value = level; osc.connect(gain).connect(out);
    osc.start(at); osc.stop(at + .08); return osc;
  });
}
function cueVoices() {
  if (backingOnly) return [];
  return emphasizedVoice ? [emphasizedVoice] : voices.filter(voice => selected.has(voice));
}

async function play() {
  if (playing || starting) { pause(); return; }
  if (!selected.size && !backingOnly) { showError(t('selectVoice')); return; }
  clearAudio(); Playlist.pause();
  const request = ++playRequest;
  starting = true; renderPlayButton();
  try {
    await startAudio();
    if (choirAllowed()) { await loadChoir(); if (slow) await loadSlowChoir(); }
    if (request !== playRequest) return;
    updateAudioMix();
    if (position >= performanceData.duration) position = 0;
    // Only a start from the beginning of the song counts in; resuming after a pause, a jump to a
    // note or a stanza, or a change of voice, key or sound goes on at once.
    const start = audio.currentTime + .05;
    anchorTime = start;
    if (position === 0) {
      const notes = cueVoices().map(voice => performanceData.events[voice][0]).filter(Boolean);
      for (const note of notes) keep(Sounds.play(audio, audio.destination, {midi:note.midi + transpose, start, duration:cueHeld, kind:'piano', level:.16 / Math.sqrt(notes.length)}));
      const {beat, perBar, clicks} = countIn(), spacing = beat * secondsPerBeat(), ticks = start + cueHeld + cueGap;
      for (let i = 0; i < clicks; i++) introNodes.push(...tick(ticks + i * spacing, i % perBar === 0));
      intro = {ticks, spacing};
      anchorTime = ticks + clicks * spacing;
    }
    anchorBeat = position; scheduledUntil = position;
    playing = true; starting = false; followScore = true;
    closeSheet();
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
  if (atEnd) stopChoir(2.5);
  clearInterval(timer); clearAudio(); renderPlayButton(); renderCount();
}
function renderPlayButton() {
  const on = playing || starting;
  $('play').dataset.playing = on;
  $('play').setAttribute('aria-label', t(on ? 'pause' : 'play'));
}
/* The play button shows the count-in: ♪ during the starting note, then the beats 1 2 3… */
function renderCount() {
  let text = '';
  if (playing && intro && audio.currentTime < anchorTime) {
    text = audio.currentTime < intro.ticks ? '♪' : String(Math.floor((audio.currentTime - intro.ticks) / intro.spacing) + 1);
  }
  document.body.toggleAttribute('data-intro', !!text);
  const count = $('play').querySelector('.count');
  if (count.textContent !== text) count.textContent = text;
}
function seek(beat, resume = playing) {
  pause(); position = Math.max(0, Math.min(beat, performanceData.duration));
  updatePosition(true);
  if (resume) { followScore = true; play(); }
}
function showError(message) { $('error').textContent = message; $('error').hidden = false; }

function chooseSong(next) {
  pause();
  song = next; performanceData = song.performance;
  transpose = 0; zoom = 1; digitalKey = ''; digitalView = null; position = 0;
  $('song-title').textContent = song.title;
  $('seek').max = performanceData.duration;
  $('total').textContent = formatTime(performanceData.duration * secondsPerBeat());
  // One light digital edition per song; original scans stay private.
  $('download').href = `exports/${encodeURIComponent(song.id)}-digital.pdf`;
  $('download').download = `${song.id}.pdf`;
  $('download').title = t('downloadPDF'); $('download').setAttribute('aria-label', t('downloadPDF'));
  $('play').disabled = false;
  renderVoices(); renderVerses(); renderTranspose(); renderSound(); showOrganVolume(); renderLyrics(); markLibrary();
  if (soundMode === 'choir') loadChoir();  // decode in the background, ready for Play
}

/* Voices: Tutti and one key per part; one tap puts the part "in evidenza", a second isolates it, a
   third returns to all voices. Songs with an accompaniment add "Base" (organ, then piano, then off). */
function renderVoices() {
  const keys = [['all', t('allShort')], ...voices.map(voice => [voice, t(voice)[0]])];
  if (song.backing_track) keys.push(['backing', t('backingShort')]);
  $('voices').replaceChildren(...keys.map(([value, text]) => {
    const button = document.createElement('button'); button.type = 'button'; button.className = 'voice-chip'; button.dataset.voice = value;
    if (value === 'all' || value === 'backing') button.textContent = text;
    else { const b = document.createElement('b'); b.textContent = text; button.append(b); button.setAttribute('aria-label', t(`album${value[0].toUpperCase()}${value.slice(1)}`)); }
    button.onclick = () => {
      if (value === 'all') return setMode('all');
      if (value === 'backing') return setMode(mode === 'backing:organ' ? 'backing:piano' : mode === 'backing:piano' ? 'all' : 'backing:organ');
      setMode(mode === `lead:${value}` ? value : mode === value ? 'all' : `lead:${value}`);
    };
    return button;
  }));
  if (!song.backing_track && mode.startsWith('backing:')) mode = 'all';
  setMode(mode, false);
}
function setMode(next, render = true) {
  const kind = next === 'backing:piano' ? 'piano' : 'organ';
  mode = next; backingOnly = next.startsWith('backing:');
  if (kind !== backingKind) { backingKind = kind; if (playing) { pause(); play(); } }
  emphasizedVoice = next.startsWith('lead:') ? next.slice(5) : null;
  selected.clear();
  if (!backingOnly) (next === 'all' || emphasizedVoice ? voices : [next]).forEach(voice => selected.add(voice));
  for (const chip of $('voices').children) {
    const v = chip.dataset.voice;
    chip.dataset.mode = v === 'all' ? (next === 'all' ? 'on' : 'off') : v === 'backing' ? (backingOnly ? 'solo' : 'off')
      : next === v ? 'solo' : next === `lead:${v}` ? 'lead' : 'off';
    chip.setAttribute('aria-pressed', String(chip.dataset.mode !== 'off'));
  }
  renderSummary();
  if (!render) return;
  updateAudioMix(); renderLyrics(); updatePosition(true);
}
function modeLabel() {
  if (mode === 'all') return t('allVoices');
  if (mode === 'backing:organ') return t('backingOrgan');
  if (mode === 'backing:piano') return t('backingPiano');
  const voice = mode.replace('lead:', ''), name = t(`album${voice[0].toUpperCase()}${voice.slice(1)}`);
  return mode.startsWith('lead:') ? `${name} ${t('inEvidence')}` : t(`solo${voice[0].toUpperCase()}${voice.slice(1)}`);
}
function renderSummary() {
  // Songs with a recorded choir: say when the piano plays instead (another key, or chosen).
  const piano = song.choir && !choirAllowed() ? ` · ${t('soundPiano')}` : '';
  $('voice-label').textContent = modeLabel() + piano;
  $('options-button').setAttribute('aria-label', `${t('options')}: ${modeLabel()}`);
}

/* Stanzas: one chip each; a tap jumps to its first bar. The chip shows the opening words. */
function incipit(number) {
  const cues = Object.values(performanceData.lyrics).map(list => list.filter(cue => cue.verse === number && cue.section !== 'chorus')).find(list => list.length) || [];
  const words = []; let word = '';
  for (const cue of cues) {
    word += cue.text.replace(/-$/, '');
    if (!cue.text.endsWith('-')) { words.push(word); word = ''; }
    if (words.length >= 4) break;
  }
  return words.join(' ').replace(/^[“‘"']+/, '').replace(/[,.;:!?’”"']+$/, '');
}
function renderVerses() {
  $('verse-group').hidden = song.verses.length < 2;
  delete $('verses').dataset.verse;  // new chips: mark the current one again
  $('verses').replaceChildren(...song.verses.map(verse => {
    const button = document.createElement('button'); button.type = 'button'; button.className = 'verse-chip'; button.dataset.verse = verse.number;
    button.setAttribute('aria-pressed', 'false');
    button.innerHTML = `<span class="chip-num">${verse.number}</span><span class="chip-text">“${UI.esc(incipit(verse.number))}…”</span>`;
    // A stanza starts at its first bar, or earlier at its pickup (sung in the previous stanza's last bar).
    button.onclick = () => {
      const bar = performanceData.bars.find(b => b.verse === verse.number);
      const cues = Object.values(performanceData.lyrics).flat().filter(cue => cue.verse === verse.number).map(cue => cue.start);
      if (bar) seek(Math.min(bar.start, ...cues));
    };
    return button;
  }));
}

/* Options: Lento, Coro/Pianoforte (songs with recorded parts), transposition, the PDF. */
function renderSound() {
  $('sound-control').hidden = !song?.choir;
  const choir = choirAllowed();
  $('sound-choir').setAttribute('aria-pressed', String(choir));
  $('sound-piano').setAttribute('aria-pressed', String(!choir));
  $('sound-choir').disabled = !!song?.choir && (transpose !== 0 || song.tempo !== song.choir.tempo);
  renderSummary();
}
function setSound(next) {
  soundMode = next; renderSound();
  if (soundMode === 'choir') loadChoir();
  if (playing) seek(currentBeat(), true);
}
$('sound-choir').onclick = () => setSound('choir');
$('sound-piano').onclick = () => setSound('piano');
function renderTranspose() {
  $('transpose-value').textContent = transpose ? t(Math.abs(transpose) === 1 ? 'semitone' : 'semitones', {n:(transpose > 0 ? '+' : '−') + Math.abs(transpose)}) : t('originalKey');
  $('transpose-down').disabled = transpose <= -6; $('transpose-up').disabled = transpose >= 6;
}
function setTranspose(next) {
  transpose = Math.max(-6, Math.min(6, next));
  renderTranspose(); renderSound(); digitalKey = ''; renderScore(); updatePosition(true);
  // Reschedule from the current beat so the new key applies at once without moving the transport.
  if (playing) seek(currentBeat(), true);
}
$('transpose-down').onclick = () => setTranspose(transpose - 1);
$('transpose-up').onclick = () => setTranspose(transpose + 1);
$('slow').onclick = () => {
  const resume = playing; pause();  // keeps the current beat
  slow = !slow; $('slow').setAttribute('aria-pressed', String(slow));
  $('total').textContent = formatTime(performanceData.duration * secondsPerBeat());
  updatePosition(true);
  if (slow && choirAllowed()) loadSlowChoir();
  if (resume) play();
};

/* The engraving: the whole performance on one line, always the four staves (a solo part fades the
   others), fitted to the height the view leaves it (never below 60%), panned under the cursor. */
function renderScore() {
  const stage = $('score-viewport');
  if (!song || $('practice-panel').hidden) return;
  const dock = document.querySelector('.player-dock');
  if (dock.offsetHeight) document.documentElement.style.setProperty('--dock-h', `${dock.offsetHeight}px`);
  const bars = performanceData.bars, beats = bars.reduce((sum, bar) => sum + bar.duration, 0);
  // Upright phones space the notes tighter, so the current bar and the next one fit together; a phone
  // turned sideways has the width but little height, so it may shrink the staves further (45%).
  const narrow = matchMedia('(max-width: 760px)').matches, sideways = matchMedia('(max-height: 500px) and (pointer: coarse)').matches;
  const width = (narrow ? Math.max(stage.clientWidth, 100 + beats * 40) : Math.max(stage.clientWidth, 660, 130 + beats * 60)) * zoom;
  const sheet = $('score'), key = [song.id, Math.round(width), transpose].join(':');
  if (key !== digitalKey) {
    sheet.style.width = `${width}px`;
    // No words in the staves: they are read from the sliding line below, so the staves sit closer.
    digitalView = ScoreNotation.render(sheet.querySelector('.notation'), song, bars, voices,
      Object.fromEntries(voices.map(v => [v, t(v)])), width, note => seek(note.start, true), {paddingtop:8, transpose, lyricVoices:[], staffsep:44});
    digitalKey = key;
  }
  // Room = the view's height minus everything else in it (head, options, words): the words stay
  // right under the music and nothing is cut below, whatever the height of the engraving.
  let w = width, h = w * digitalView.height / digitalView.width;
  const view = $('practice-panel'), style = getComputedStyle(stage);
  const others = [...view.children].filter(child => child !== stage && child.offsetParent && !['fixed', 'absolute'].includes(getComputedStyle(child).position))
    .reduce((sum, child) => sum + child.offsetHeight, 0);
  const room = view.clientHeight - parseFloat(getComputedStyle(view).paddingTop) - others - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom) - 2;
  // At the default zoom the engraving fills the room: shrunk when tall (never below 60%), enlarged
  // when short (up to 130%), so on a phone the notes use the whole space above the words.
  if (zoom === 1 && room > 80) { const fit = Math.min(1.3, Math.max(sideways ? .45 : .6, room / h)); w *= fit; h *= fit; }
  sheet.style.width = `${w}px`; sheet.style.height = `${h}px`;
  $('zoom-out').disabled = zoom <= .7; $('zoom-in').disabled = zoom >= 1.6;
}
/* The line turns a bar at a time, like a page: the current bar sits near the left edge with the next
   ones visible ahead, and the view moves only when a new bar begins. A bar wider than the view turns
   within itself, still a page at a time. */
let pageLeft = null, pan = null;
function barStarts() {
  if (!digitalView.barX) {
    digitalView.barX = [];
    for (const note of digitalView.positions)
      if (note.x != null) digitalView.barX[note.measureIndex] = Math.min(digitalView.barX[note.measureIndex] ?? Infinity, note.x);
  }
  return digitalView.barX;
}
function panTo(barIndex, fraction, instant) {
  const stage = $('score-viewport'), sheet = $('score'), view = stage.clientWidth;
  const scale = sheet.offsetWidth / digitalView.width, cursor = fraction * sheet.offsetWidth;
  let left = (barStarts()[barIndex] ?? fraction * digitalView.width) * scale - Math.min(28, view * .06);
  while (cursor > left + view * .85) left += view * .7;
  if (barIndex === 0 || left < 60) left = 0;  // the first bar keeps the clefs and key in sight
  if (!instant && left === pageLeft) return;
  pageLeft = left;
  if (instant) { pan = null; stage.scrollLeft = left; }
  else { pan = {from:stage.scrollLeft, to:left, at:performance.now()}; stepPan(); }
}
// The turn is animated in the same frame as the cursor (not the browser's smooth scroll, which runs
// apart from it and showed the cursor stepping back for a frame).
function stepPan() {
  if (!pan) return;
  if (!followScore) { pan = null; return; }  // a drag takes over
  const k = Math.min(1, (performance.now() - pan.at) / 380);
  $('score-viewport').scrollLeft = pan.from + (pan.to - pan.from) * (1 - (1 - k) ** 3);
  if (k >= 1) pan = null;
}

// Lyrics run as one line that turns a bar at a time, like the score: the current bar's words start
// near the left edge, so the next bars are visible ahead (read-ahead). They follow the voice heard.
let lyricSpans = [], lyricTimeline = null, lyricOffset = -1;
function lyricVoice() { return emphasizedVoice || (selected.size === 1 ? [...selected][0] : 'soprano'); }
function renderLyrics() {
  const timeline = performanceData.lyrics[lyricVoice()] || [];
  if (timeline === lyricTimeline) return;
  lyricTimeline = timeline; lyricOffset = -1; lyricSpans = [];
  const line = document.createElement('div'); line.className = 'lyric-line';
  let join = true, verse = null;
  for (const cue of timeline) {
    if (cue.verse !== verse) {
      verse = cue.verse;
      if (song.verses.length > 1) { const mark = document.createElement('span'); mark.className = 'verse-mark'; mark.textContent = verse; line.append(' ', mark, ' '); join = true; }
    }
    if (!join) line.append(' ');
    const span = document.createElement('span'); span.className = 'syllable';
    span.textContent = cue.text.replace(/-$/, ''); span.dataset.start = cue.start; span.dataset.end = cue.end;
    span.onclick = () => seek(cue.start);
    line.append(span); lyricSpans.push(span); join = cue.text.endsWith('-');
  }
  if (!timeline.length) line.textContent = t('noLyrics');
  $('lyric-rows').replaceChildren(line);
}
function slideLyrics(beat, bar) {
  let index = -1;
  for (let i = 0; i < lyricSpans.length && Number(lyricSpans[i].dataset.start) <= beat; i++) index = i;
  lyricSpans.forEach(span => {
    const start = Number(span.dataset.start), end = Number(span.dataset.end);
    span.classList.toggle('current', beat >= start && beat < end);
    span.classList.toggle('sung', beat >= end);
  });
  const line = $('lyric-rows').firstChild;
  if (!line || !lyricSpans.length) return;
  // The bar's first syllable (or the next words, in a bar without any), with its stanza number.
  let first = lyricSpans.findIndex(span => Number(span.dataset.start) >= bar.start - 1e-6);
  if (first < 0) first = lyricSpans.length - 1;
  const anchor = lyricSpans[first], mark = anchor.previousElementSibling?.classList.contains('verse-mark') ? anchor.previousElementSibling : anchor;
  const width = $('lyric-rows').clientWidth, margin = Math.min(24, width * .05);
  let offset = mark.offsetLeft - margin;
  const now = lyricSpans[Math.max(index, first)];
  while (now.offsetLeft + now.offsetWidth > offset + width * .92) offset += width * .7;  // many words in one bar
  offset = Math.max(0, offset);
  if (offset === lyricOffset) return;
  lyricOffset = offset;
  line.style.transform = `translateX(${-offset}px)`;
  $('lyric-rows').classList.toggle('scrolled', offset > 0);  // fade the left edge only once text has left it
}

function sectionAt(measure, beat) {
  let name = 'verse';
  for (const section of song.sections || []) {
    const [m, b] = section.at;
    if (measure > m || (measure === m && beat >= b)) name = section.name;
  }
  return name;
}
let shownBeat = -1;
function updatePosition(forcePan = false) {
  if (!performanceData || $('practice-panel').hidden) return;
  let beat = Math.max(0, currentBeat());
  if (playing && beat >= performanceData.duration) { pause(true); position = performanceData.duration; beat = position; }
  renderCount();
  if (beat === shownBeat && !forcePan) return;
  shownBeat = beat;
  if (!digitalView) renderScore();
  $('seek').value = beat; $('seek').style.setProperty('--fill', `${beat / performanceData.duration * 100}%`);
  const barIndex = Math.max(0, performanceData.bars.findLastIndex(b => b.start <= beat)), bar = performanceData.bars[barIndex];
  const section = sectionAt(bar.measure, beat - bar.start);
  // Only informative parts: the stanza when there are several; the section unless that is just "verse".
  const several = song.verses.length > 1;
  $('verse-now').textContent = several ? t('stanzaShort', {n:bar.verse}) : '';
  $('section-name').textContent = (several || !song.sections?.length) && section === 'verse' ? '' : t(section === 'verse' ? 'verseSection' : section);
  if ($('verses').dataset.verse !== String(bar.verse)) {
    $('verses').dataset.verse = bar.verse;
    for (const chip of $('verses').children) chip.setAttribute('aria-pressed', String(Number(chip.dataset.verse) === bar.verse));
    // The chosen chip shows its first words, which may wrap the options: fit the line again.
    refit();
  }
  const text = `${t('verse')} ${bar.verse} · ${t('measure', {n:bar.measure})}${beat >= performanceData.duration ? ' · ' + t('finished') : ''}`;
  if ($('position').textContent !== text) $('position').textContent = text;
  $('time').textContent = formatTime(beat * secondsPerBeat());
  if (digitalView) {
    digitalView.update(beat, null);  // colours the sounding notes
    // The cursor follows the most recent onset, so a note held from long before never pulls the view
    // back while the other voices move on.
    // At that onset a note wins over a rest: a whole-bar rest is drawn mid-bar, away from the notes.
    let x = null, latest = -Infinity, rest = true;
    for (const note of digitalView.positions) {
      if (note.x == null || note.start > beat + 1e-6) continue;
      const isRest = note.pitch === 'R';
      if (note.start > latest + 1e-6) { latest = note.start; x = note.x; rest = isRest; }
      else if (note.start > latest - 1e-6 && (rest || !isRest)) { x = rest && !isRest ? note.x : Math.max(x, note.x); rest = rest && isRest; }
    }
    const fraction = x == null ? null : x / digitalView.width;
    const notation = digitalView.svg.parentElement, lead = emphasizedVoice || (selected.size === 1 ? [...selected][0] : null);
    const index = lead ? String(voices.indexOf(lead)) : '';
    if (notation.dataset.lead !== index) notation.dataset.lead = index;
    const cursor = $('score').querySelector('.cursor');
    cursor.hidden = fraction == null;
    if (fraction != null) {
      cursor.style.left = `${fraction * 100}%`;
      if (forcePan || (playing && followScore)) panTo(barIndex, fraction, forcePan);
    }
  }
  slideLyrics(beat, bar);
}

/* Views: Playlist (the albums and one album), Spartiti (the songs, then a score), PDF. Each is a
   URL hash, so the phone's back gesture moves back through them and a link opens the same view. */
const views = {albums:'albums-panel', playlist:'playlist-panel', library:'library-panel', practice:'practice-panel', booklet:'booklet-panel'};
let view = '';
function route() {
  const [name = '', arg = ''] = decodeURIComponent(location.hash.replace(/^#\/?/, '')).split('/');
  const next = {'':'albums', playlist:arg ? 'playlist' : 'albums', brani:'library', spartito:'practice', pdf:'booklet'}[name] || 'albums';
  if (next === 'practice') {
    if (!songs.length) return;
    const chosen = songs.find(item => item.id === arg) || song || songs[0];
    Playlist.close();  // opening a score ends the playlist (the score is the interactive view)
    if (chosen !== song) chooseSong(chosen);
  }
  if (next === 'playlist') Playlist.open(arg);
  showView(next);
}
function showView(name) {
  if (name !== 'practice') { pause(); closeSheet(); }
  view = name;
  for (const [key, id] of Object.entries(views)) $(id).hidden = key !== name;
  document.body.dataset.view = name;
  document.querySelector('.player-dock').hidden = name !== 'practice';
  document.querySelector('.make-bar').hidden = name !== 'booklet';
  const tab = {albums:'albums', playlist:'albums', library:'library', practice:'library', booklet:'booklet'}[name];
  document.querySelectorAll('.tabs a').forEach(a => a.dataset.nav === tab ? a.setAttribute('aria-current', 'page') : a.removeAttribute('aria-current'));
  document.title = name === 'practice' && song ? `${song.title} · Christmas Carol Choir` : 'Christmas Carol Choir';
  renderMiniPlayer();
  scrollTo(0, 0);
  if (name === 'practice') { renderScore(); shownBeat = -1; updatePosition(true); }
}
// The playing playlist stays reachable everywhere except inside a score (which has its own dock).
function renderMiniPlayer() {
  const show = view !== 'practice' && Playlist.hasQueue;
  $('mini-player').hidden = !show; document.body.classList.toggle('mini-open', show);
}
document.addEventListener('playlistchange', renderMiniPlayer);
Playlist.onStart = () => { if (playing || starting) pause(); };
addEventListener('hashchange', route);

/* Spartiti: the same rows as the playlists, on the choir's black tile. */
function renderLibrary() {
  $('song-list').innerHTML = songs.map((item, index) => `<li>${UI.row({attrs:`href="#/spartito/${encodeURIComponent(item.id)}"`, number:index + 1, song:item,
    meta:formatTime(item.performance.duration * 60 / (item.tempo || 96))})}</li>`).join('');
  markLibrary();
}
function markLibrary() {
  $('song-list').querySelectorAll('.song-row').forEach(row => row.toggleAttribute('aria-current', !!song && row.getAttribute('href') === `#/spartito/${encodeURIComponent(song.id)}`));
}

/* The phone options are a bottom sheet rather than permanent controls. */
function openSheet() {
  document.body.dataset.sheet = 'selection';
  $('options-button').setAttribute('aria-expanded', 'true');
  $('selection').tabIndex = -1; $('selection').focus({preventScroll:true});
}
function closeSheet() {
  if (!document.body.dataset.sheet) return;
  delete document.body.dataset.sheet;
  $('options-button').setAttribute('aria-expanded', 'false');
}
$('options-button').onclick = () => document.body.dataset.sheet ? closeSheet() : openSheet();
document.querySelector('[data-close]').onclick = closeSheet;
document.querySelector('.scrim').onclick = closeSheet;
document.addEventListener('keydown', event => { if (event.key === 'Escape') closeSheet(); });
// On a computer Space plays/pauses the score, or the playlist elsewhere, even when a clicked button
// keeps the focus (it is not also pressed). Fields and tick boxes keep Space.
document.addEventListener('keydown', event => {
  if (event.key !== ' ' || event.repeat || event.ctrlKey || event.metaKey || event.altKey) return;
  if (event.target.closest?.('input:not([type="range"]), select, textarea, [contenteditable]')) return;
  if (view === 'practice') { event.preventDefault(); play(); }
  else if (Playlist.hasQueue) { event.preventDefault(); Playlist.toggle(); }
});

$('play').onclick = play;
$('seek').oninput = () => seek(Number($('seek').value));
$('zoom-out').onclick = () => { zoom = Math.max(.7, Math.round((zoom - .15) * 100) / 100); digitalKey = ''; renderScore(); updatePosition(true); };
$('zoom-in').onclick = () => { zoom = Math.min(1.6, Math.round((zoom + .15) * 100) / 100); digitalKey = ''; renderScore(); updatePosition(true); };
// Only a deliberate drag stops the score following the music; a tap on a note keeps it.
let dragStart;
$('score-viewport').addEventListener('pointerdown', event => { dragStart = event.clientX; });
$('score-viewport').addEventListener('pointermove', event => {
  if (dragStart !== undefined && Math.abs(event.clientX - dragStart) > 12 && playing) followScore = false;
});
addEventListener('pointerup', () => { dragStart = undefined; });
let resizing;
const refit = () => { cancelAnimationFrame(resizing); resizing = requestAnimationFrame(() => { renderScore(); updatePosition(true); }); };
addEventListener('resize', refit);
// The fit depends on the head, options and words around the line: refit whenever they change size
// (fonts arriving, the options wrapping, another song's title); the engraving itself is not redrawn.
const around = new ResizeObserver(refit);
['practice-panel', 'selection', 'lyric-rows'].forEach(id => around.observe($(id)));
around.observe(document.querySelector('.score-head'));

/* Appearance: device, light, dark; the glyph shows the mode (half disc, sun, moon). */
function renderThemeButton() {
  const mode = appearance.mode, labels = {system:t('themeSystem'), light:t('themeLight'), dark:t('themeDark')};
  $('theme').dataset.mode = mode;
  $('theme').querySelector('use').setAttribute('href', `icons.svg#${{system:'theme', light:'sun', dark:'moon'}[mode]}`);
  const label = `${t('theme')}: ${labels[mode]}`;
  $('theme').title = label; $('theme').setAttribute('aria-label', label);
}
$('theme').onclick = () => {
  const modes = ['system', 'light', 'dark'];
  appearance.set(modes[(modes.indexOf(appearance.mode) + 1) % modes.length]);
  renderThemeButton();
};
if ('serviceWorker' in navigator && isSecureContext) navigator.serviceWorker.register('sw.js').catch(() => {});
function frame() { updatePosition(); stepPan(); requestAnimationFrame(frame); }
translatePage(); renderThemeButton(); renderPlayButton();
route();
fetch('api/songs.json').then(response => { if (!response.ok) throw Error(t('loadError')); return response.json(); }).then(data => {
  songs = data.sort((a, b) => new Intl.Collator('it', {sensitivity:'base', numeric:true}).compare(a.title, b.title));
  if (!songs.length) throw Error(t('noScores'));
  renderLibrary(); Booklet.render(songs);
  if (!song) chooseSong(songs[0]);  // the first song is ready for practice
  route();
  frame();
}).catch(error => showError(error.message));
Playlist.load().catch(error => console.error(error));
keepAwake();
