/* Recording playlists, one "album" per voice. Each chosen song plays the voice's own track, which
   tools/recordings.py builds as one file (spoken title, first note and count-in, then the part),
   and then the shared recordings (tenors and basses, whole choir) when they exist.
   One <audio> element plays everything, so playback continues with the screen locked and the
   lock screen shows the song (Media Session) with play/pause and previous/next song. */
const Playlist = (() => {
  const el = id => document.getElementById(id);
  const albumVoices = ['soprano', 'alto', 'tenor', 'bass'];
  // One emoji per voice album, none shared with a song: the four seasons, high to low.
  const albumEmoji = {soprano:'🌸', alto:'☀️', tenor:'🍂', bass:'❄️'};
  const albumName = voice => t({soprano:'albumSoprano', alto:'albumAlto', tenor:'albumTenor', bass:'albumBass'}[voice]);
  const stepVoice = voice => ({all:t('voiceAll'), 'tenor-bass':t('voiceTenorBass')}[voice] || albumName(voice));
  const clock = s => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
  let data = {}, voice = 'soprano', steps = [], index = 0, queueVoice = null, onStart = () => {};
  const media = new Audio(); media.preload = 'auto'; media.setAttribute('playsinline', '');

  // Per-device choice and order of songs in each album (a convenience; never required).
  function saved(v) {
    try { return JSON.parse(localStorage.getItem(`playlist-${v}`)) || {}; } catch { return {}; }
  }
  function store(v, value) { try { localStorage.setItem(`playlist-${v}`, JSON.stringify(value)); } catch {} }
  function songs(v) {
    const items = data[v] || [], {order = [], off = []} = saved(v);
    const rank = id => { const i = order.indexOf(id); return i < 0 ? order.length : i; };
    return [...items].sort((a, b) => rank(a.id) - rank(b.id)).map(item => ({...item, on:!off.includes(item.id)}));
  }
  const length = item => item.tracks.reduce((sum, track) => sum + track.seconds, 0);

  /* Covers: the song title in IM Fell English with its emoji, on evergreen paper. */
  function cover(item, className = 'cover') {
    const box = document.createElement('div'); box.className = className;
    const icon = document.createElement('span'); icon.className = 'cover-emoji'; icon.textContent = item.emoji;
    const title = document.createElement('span'); title.className = 'cover-title'; title.textContent = item.title;
    box.append(icon, title); return box;
  }
  function album(v, className = 'album') {
    const box = document.createElement('div'); box.className = `${className} album-${v}`;
    const letter = document.createElement('span'); letter.className = 'album-letter'; letter.textContent = albumName(v)[0];
    const name = document.createElement('span'); name.className = 'album-name'; name.textContent = albumName(v);
    const tree = document.createElement('span'); tree.className = 'album-tree'; tree.textContent = albumEmoji[v];
    box.append(tree, letter, name); return box;
  }
  const artwork = {};
  async function artworkFor(item) {
    if (artwork[item.id]) return artwork[item.id];
    try { await document.fonts.load('52px "IM Fell English"'); } catch {}
    const canvas = document.createElement('canvas'); canvas.width = canvas.height = 512;
    const g = canvas.getContext('2d'), fill = g.createLinearGradient(0, 0, 512, 512);
    fill.addColorStop(0, '#2f6a4a'); fill.addColorStop(1, '#173b28');
    g.fillStyle = fill; g.fillRect(0, 0, 512, 512);
    g.strokeStyle = '#d6b25e'; g.lineWidth = 6; g.strokeRect(24, 24, 464, 464);
    g.textAlign = 'center'; g.textBaseline = 'middle';
    g.font = '150px system-ui, "Apple Color Emoji", "Segoe UI Emoji", sans-serif'; g.fillText(item.emoji, 256, 176);
    g.fillStyle = '#fff6e0'; g.font = '50px "IM Fell English", Georgia, serif';
    const lines = []; let line = '';
    for (const word of item.title.split(' ')) {
      const next = line ? `${line} ${word}` : word;
      if (g.measureText(next).width > 400 && line) { lines.push(line); line = word; } else line = next;
    }
    lines.push(line);
    lines.forEach((text, i) => g.fillText(text, 256, 340 + (i - (lines.length - 1) / 2) * 58));
    return artwork[item.id] = canvas.toDataURL('image/png');
  }

  function renderAlbums() {
    el('album-list').replaceChildren(...albumVoices.map(v => {
      const li = document.createElement('li'), button = document.createElement('button');
      button.type = 'button'; button.className = 'album-card';
      const count = (data[v] || []).length, caption = document.createElement('span'); caption.className = 'album-caption';
      caption.textContent = count === 1 ? t('songCountOne') : t('songCount', {n:count});
      button.append(album(v), caption);
      button.setAttribute('aria-label', `${albumName(v)}, ${caption.textContent}`);
      button.onclick = () => { voice = v; render(); showTab('playlist'); };
      li.append(button); return li;
    }));
  }

  // Header only (count, length, play button): ticking a song must not rebuild the rows under the finger.
  function renderHead() {
    const list = songs(voice), chosen = list.filter(item => item.on);
    el('playlist-cover').replaceChildren(album(voice, 'album album-large'));
    el('playlist-title').textContent = albumName(voice);
    const minutes = Math.round(chosen.reduce((sum, item) => sum + length(item), 0) / 60);
    el('playlist-detail').textContent = list.length
      ? `${t('chosenCount', {n:chosen.length, total:list.length})} · ${t('minutes', {n:minutes})}` : t('noRecordings');
    el('playlist-all').checked = chosen.length === list.length && list.length > 0;
    el('playlist-all').indeterminate = chosen.length > 0 && chosen.length < list.length;
    renderPlayButton();
  }
  function render() {
    renderHead();
    const list = songs(voice);
    el('playlist-tracks').replaceChildren(...list.map(item => {
      const li = document.createElement('li'); li.className = 'track-row'; li.dataset.id = item.id;
      if (queueVoice === voice && steps[index]?.item.id === item.id) li.classList.add('current');
      const box = document.createElement('input'); box.type = 'checkbox'; box.checked = item.on;
      box.setAttribute('aria-label', item.title);
      box.onchange = () => { toggle(item.id, box.checked); };
      const play = document.createElement('button'); play.type = 'button'; play.className = 'track-play';
      play.setAttribute('aria-label', t('playFrom', {title:item.title}));
      const copy = document.createElement('span'); copy.className = 'track-copy';
      const title = document.createElement('span'); title.className = 'track-title'; title.textContent = item.title;
      const detail = document.createElement('span'); detail.className = 'track-detail';
      const n = item.tracks.length;
      detail.textContent = `${item.tracks.map(track => stepVoice(track.voice)).join(' · ')} · ${clock(length(item))}`;
      if (n > 1) detail.title = t('recordingCount', {n});
      copy.append(title, detail); play.append(cover(item, 'cover cover-small'), copy);
      play.onclick = () => { if (!item.on) { box.checked = true; toggle(item.id, true); } start(item.id); };
      const handle = document.createElement('span'); handle.className = 'booklet-handle'; handle.textContent = '⠿';
      handle.title = t('dragToSort'); handle.setAttribute('aria-hidden', 'true');
      handle.onpointerdown = event => drag(event, li);
      li.append(box, play, handle); return li;
    }));
  }
  function toggle(id, on) {
    const state = saved(voice), off = new Set(state.off || []);
    on ? off.delete(id) : off.add(id); store(voice, {...state, off:[...off]}); renderHead();
  }
  function selectAll(on) {
    const state = saved(voice);
    store(voice, {...state, off:on ? [] : (data[voice] || []).map(item => item.id)});
    el('playlist-tracks').querySelectorAll('input').forEach(box => box.checked = on); renderHead();
  }
  function drag(event, row) {
    event.preventDefault();
    const list = el('playlist-tracks'); row.classList.add('dragging');
    const move = e => {
      const over = [...list.children].find(other => other !== row && (() => {
        const box = other.getBoundingClientRect(); return e.clientY > box.top && e.clientY < box.bottom; })());
      if (!over) return;
      const box = over.getBoundingClientRect();
      list.insertBefore(row, e.clientY < box.top + box.height / 2 ? over : over.nextSibling);
    };
    const end = () => {
      row.classList.remove('dragging');
      removeEventListener('pointermove', move); removeEventListener('pointerup', end); removeEventListener('pointercancel', end);
      store(voice, {...saved(voice), order:[...list.children].map(li => li.dataset.id)});
    };
    addEventListener('pointermove', move); addEventListener('pointerup', end); addEventListener('pointercancel', end);
  }

  /* The queue: one step per recording of each chosen song. */
  function buildQueue(v) {
    queueVoice = v;
    steps = songs(v).filter(item => item.on).flatMap(item => item.tracks.map((track, i) => ({item, src:track.file,
      label:stepVoice(track.voice) + (item.tracks.length > 1 ? ` · ${t('stepOf', {n:i + 1, total:item.tracks.length})}` : '')})));
  }
  function start(id) {
    buildQueue(voice);
    if (!steps.length) return;
    load(Math.max(0, steps.findIndex(step => step.item.id === id)), true);
  }
  function load(i, autoplay) {
    index = i; const step = steps[index];
    media.src = step.src;
    if (autoplay) resume();
    updateNowPlaying(); markCurrent();
  }
  function markCurrent() {
    const id = queueVoice === voice ? steps[index]?.item.id : null;
    el('playlist-tracks').querySelectorAll('.track-row').forEach(row => row.classList.toggle('current', row.dataset.id === id));
  }
  function resume() {
    if (!steps.length) { buildQueue(voice); if (!steps.length) return; load(0, true); return; }
    onStart();
    try { if (navigator.audioSession) navigator.audioSession.type = 'playback'; } catch {}
    media.play().catch(() => {});
  }
  function pause() { media.pause(); }
  function toggleQueue() {
    // The album on screen plays its own selection; tapping again pauses or resumes.
    if (queueVoice !== voice && !el('playlist-panel').hidden) { start(null); return; }
    media.paused ? resume() : pause();
  }
  function songStart(i) { const id = steps[i].item.id; return steps.findIndex(step => step.item.id === id); }
  function next() {
    const id = steps[index]?.item.id, i = steps.findIndex((step, n) => n > index && step.item.id !== id);
    if (i >= 0) load(i, true); else stop();
  }
  function previous() {
    const first = songStart(index);
    // Like a music player: restart the song, or go to the previous one at its very beginning.
    if (index > first || media.currentTime > 3 || first === 0) load(first, true);
    else load(songStart(first - 1), true);
  }
  function stop() { media.pause(); if (steps.length) { index = 0; media.src = steps[0].src; } updateNowPlaying(); markCurrent(); }
  media.addEventListener('ended', () => { if (index + 1 < steps.length) load(index + 1, true); else stop(); });
  for (const type of ['play', 'pause', 'playing']) media.addEventListener(type, () => { renderPlayButton(); updateNowPlaying(); });
  media.addEventListener('timeupdate', renderProgress);
  media.addEventListener('loadedmetadata', renderProgress);

  function renderPlayButton() {
    const ours = queueVoice === voice && steps.length, playingNow = !media.paused;
    el('playlist-play').textContent = ours && playingNow ? `Ⅱ ${t('pause')}` : `▶ ${t('playAll')}`;
    el('playlist-play').disabled = !songs(voice).some(item => item.on);
    el('mini-play').textContent = playingNow ? 'Ⅱ' : '▶';
    el('mini-play').setAttribute('aria-label', t(playingNow ? 'pause' : 'play'));
  }
  function renderProgress() {
    const duration = Number.isFinite(media.duration) ? media.duration : 0;
    el('mini-seek').max = duration || 1; el('mini-seek').value = media.currentTime;
    el('mini-time').textContent = `${clock(media.currentTime)} / ${clock(duration)}`;
    if ('mediaSession' in navigator && duration) {
      try { navigator.mediaSession.setPositionState({duration, position:Math.min(duration, media.currentTime), playbackRate:1}); } catch {}
    }
  }
  async function updateNowPlaying() {
    const step = steps[index];
    el('mini-player').dataset.ready = step ? 'true' : '';
    document.dispatchEvent(new Event('playlistchange'));
    if (!step) return;
    el('mini-cover').replaceChildren(cover(step.item, 'cover cover-mini'));
    el('mini-title').textContent = step.item.title;
    // The voice's own track needs no second label: "Tenori", but "Tenori · Tutto il coro".
    const status = step.label === albumName(queueVoice) ? step.label : `${albumName(queueVoice)} · ${step.label}`;
    el('mini-status').textContent = status;
    if (!('mediaSession' in navigator)) return;
    navigator.mediaSession.playbackState = media.paused ? 'paused' : 'playing';
    const src = await artworkFor(step.item);
    if (steps[index] !== step) return;
    navigator.mediaSession.metadata = new MediaMetadata({title:step.item.title, artist:status,
      album:'Christmas Carol Choir', artwork:[{src, sizes:'512x512', type:'image/png'}]});
  }
  if ('mediaSession' in navigator) {
    const actions = {play:resume, pause, previoustrack:previous, nexttrack:next,
      seekto:details => { media.currentTime = details.seekTime; },
      seekbackward:details => { media.currentTime = Math.max(0, media.currentTime - (details.seekOffset || 10)); },
      seekforward:details => { media.currentTime = Math.min(media.duration || 0, media.currentTime + (details.seekOffset || 10)); }};
    for (const [action, handler] of Object.entries(actions)) { try { navigator.mediaSession.setActionHandler(action, handler); } catch {} }
  }

  el('playlist-play').onclick = toggleQueue;
  el('mini-play').onclick = () => media.paused ? resume() : pause();
  el('mini-next').onclick = next;
  el('mini-previous').onclick = previous;
  el('mini-seek').oninput = () => { media.currentTime = Number(el('mini-seek').value); };
  el('playlist-all').onchange = event => selectAll(event.target.checked);

  async function load_() {
    const response = await fetch('api/recordings.json');
    if (!response.ok) throw Error(t('loadError'));
    data = await response.json(); renderAlbums();
  }
  return {
    load:load_, render, renderAlbums, pause,
    get hasQueue() { return steps.length > 0; },
    get playing() { return !media.paused; },
    set onStart(callback) { onStart = callback; },
  };
})();
