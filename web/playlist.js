/* Recording playlists, one "album" per voice. Each chosen song plays the voice's own track, which
   tools/recordings.py builds as one file (spoken title, first note and count-in, then the part),
   and then the shared recordings (tenors and basses, whole choir) when they exist.
   One <audio> element plays everything, so playback continues with the screen locked and the
   lock screen shows the song (Media Session) with play/pause and previous/next song. */
const Playlist = (() => {
  const el = id => document.getElementById(id);
  // "Christmas Carols" (the whole choir, songs only), each voice alone with its intro, then each
  // voice "in evidenza" (the full mix with that voice in front).
  const parts = ['soprano', 'alto', 'tenor', 'bass'];
  const albumVoices = ['choir', ...parts, ...parts.map(voice => `lead-${voice}`)];
  const partOf = album => album.replace(/^lead-/, '');
  // One emoji per voice, none shared with a song: the four seasons, high to low.
  const albumEmoji = {soprano:'🌸', alto:'🌞', tenor:'🍂', bass:'⛄'};
  const voiceName = voice => t({soprano:'albumSoprano', alto:'albumAlto', tenor:'albumTenor', bass:'albumBass'}[voice]);
  const albumName = album => album === 'choir' ? t('albumChoir')
    : album.startsWith('lead-') ? `${voiceName(partOf(album))} ${t('inEvidence')}` : voiceName(album);
  const stepVoice = voice => ({all:t('voiceAll'), 'tenor-bass':t('voiceTenorBass')}[voice] || albumName(voice));
  const clock = s => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;
  let data = {}, voice = 'soprano', steps = [], index = 0, queueVoice = null, onStart = () => {};
  const media = new Audio(); media.preload = 'auto'; media.setAttribute('playsinline', '');

  // Per-device order of songs in each album (a convenience; never required).
  function saved(v) {
    try { return JSON.parse(localStorage.getItem(`playlist-${v}`)) || {}; } catch { return {}; }
  }
  function store(v, value) { try { localStorage.setItem(`playlist-${v}`, JSON.stringify(value)); } catch {} }
  function songs(v) {
    const items = data[v] || [], {order = []} = saved(v);
    const rank = id => { const i = order.indexOf(id); return i < 0 ? order.length : i; };
    return [...items].sort((a, b) => rank(a.id) - rank(b.id));
  }
  const length = item => item.tracks.reduce((sum, track) => sum + track.seconds, 0);

  /* Covers: the song title in IM Fell English with its emoji, on evergreen paper. */
  // A song's cover in a playlist wears that playlist's background: its colour and season emoji.
  function cover(item, className = 'cover', v = voice) {
    const box = document.createElement('div'); box.className = className;
    const [a, b] = tones[partOf(v)];
    box.style.background = `linear-gradient(135deg,${a},${b})`;
    const season = document.createElement('span'); season.className = 'cover-season'; season.textContent = albumEmoji[partOf(v)];
    season.setAttribute('aria-hidden', 'true');
    const icon = document.createElement('span'); icon.className = 'cover-emoji'; icon.textContent = item.emoji;
    const title = document.createElement('span'); title.className = 'cover-title'; title.textContent = item.title;
    box.append(season, icon, title); return box;
  }
  /* Album covers are one SVG drawing on a fixed 200×200 grid, so they scale like an image and
     nothing can overlap at any size: the season's colour, a gold double frame, the voice initial in
     the period face, the season emoji large and faint behind, and a gold "in evidenza" band. */
  const tones = {choir:['#2f6a4a', '#123222'], soprano:['#c2566b', '#6a1f2e'], alto:['#cf9c3a', '#7a5212'], tenor:['#b46a33', '#5b2c10'], bass:['#4f6b7c', '#18262f']};
  albumEmoji.choir = '🎄';
  let coverCount = 0;
  function album(v, className = 'album') {
    const part = partOf(v), lead = v.startsWith('lead-'), id = `cover${++coverCount}`, [a, b] = tones[part];
    const svgNS = 'http://www.w3.org/2000/svg', svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('viewBox', '0 0 200 200'); svg.setAttribute('class', className); svg.setAttribute('role', 'img');
    svg.setAttribute('aria-label', albumName(v));
    const text = value => String(value).replace(/[&<>]/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;'}[c]));
    const letterY = lead ? 104 : 116, nameY = lead ? 136 : 160, choir = part === 'choir';
    svg.innerHTML = `
      <defs>
        <linearGradient id="${id}-bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${a}"/><stop offset="1" stop-color="${b}"/></linearGradient>
        <radialGradient id="${id}-glow" cx=".28" cy=".18" r=".6"><stop offset="0" stop-color="#fff6e0" stop-opacity=".26"/><stop offset="1" stop-color="#fff6e0" stop-opacity="0"/></radialGradient>
        <linearGradient id="${id}-band" x1="0" x2="1"><stop offset="0" stop-color="#c9a24e"/><stop offset=".5" stop-color="#ecd28c"/><stop offset="1" stop-color="#c9a24e"/></linearGradient>
        <filter id="${id}-shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#000" flood-opacity=".35"/></filter>
        <clipPath id="${id}-clip"><rect width="200" height="200" rx="12"/></clipPath>
      </defs>
      <g clip-path="url(#${id}-clip)">
        <rect width="200" height="200" fill="url(#${id}-bg)"/>
        <rect width="200" height="200" fill="url(#${id}-glow)"/>
        <text x="158" y="196" font-size="118" text-anchor="middle" opacity=".17" transform="rotate(-12 158 150)">${albumEmoji[part]}</text>
        <rect x="11" y="11" width="178" height="178" rx="8" fill="none" stroke="#d6b25e" stroke-opacity=".8" stroke-width="1.5"/>
        <rect x="16.5" y="16.5" width="167" height="167" rx="6" fill="none" stroke="#d6b25e" stroke-opacity=".45"/>
        ${choir ? `<text text-anchor="middle" font-family="'IM Fell English', Georgia, serif" fill="#fff6e0" filter="url(#${id}-shadow)">
          <tspan x="100" y="92" font-size="40">Christmas</tspan><tspan x="100" y="134" font-size="40">Carols</tspan></text>
        <line x1="64" x2="136" y1="152" y2="152" stroke="#d6b25e" stroke-opacity=".65"/>` : `
        <text x="100" y="${letterY}" text-anchor="middle" font-family="'IM Fell English', Georgia, serif" font-size="${lead ? 76 : 90}" fill="#fff6e0" filter="url(#${id}-shadow)">${text(voiceName(part)[0])}</text>
        ${lead ? '' : `<line x1="64" x2="136" y1="134" y2="134" stroke="#d6b25e" stroke-opacity=".65"/>`}
        <text x="100" y="${nameY}" text-anchor="middle" font-family="'IM Fell English', Georgia, serif" font-size="${lead ? 19 : 21}" letter-spacing=".6" fill="#fff6e0">${text(voiceName(part))}</text>`}
        ${lead ? `<rect x="0" y="152" width="200" height="24" fill="url(#${id}-band)"/>
        <text x="100" y="168.5" text-anchor="middle" font-family="system-ui, sans-serif" font-size="11" font-weight="650" letter-spacing="2.2" fill="#3a2a08">${text(t('inEvidence').toUpperCase())}</text>` : ''}
      </g>`;
    return svg;
  }
  const artwork = {};
  async function artworkFor(item, v = queueVoice) {
    const part = partOf(v || 'choir'), key = `${item.id}:${part}`;
    if (artwork[key]) return artwork[key];
    try { await document.fonts.load('52px "IM Fell English"'); } catch {}
    const canvas = document.createElement('canvas'); canvas.width = canvas.height = 512;
    const g = canvas.getContext('2d'), fill = g.createLinearGradient(0, 0, 512, 512), [a, b] = tones[part];
    fill.addColorStop(0, a); fill.addColorStop(1, b);
    g.fillStyle = fill; g.fillRect(0, 0, 512, 512);
    g.strokeStyle = '#d6b25e'; g.lineWidth = 6; g.strokeRect(24, 24, 464, 464);
    g.textAlign = 'center'; g.textBaseline = 'middle';
    // iOS Safari draws no colour emoji with a gradient fill or a large system-ui size: use a
    // solid fill, the emoji fonts first, and scale a 96px glyph up.
    const glyph = document.createElement('canvas'); glyph.width = glyph.height = 128;
    const e = glyph.getContext('2d'); e.textAlign = 'center'; e.textBaseline = 'middle'; e.fillStyle = '#000';
    e.font = '96px "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif';
    e.fillText(albumEmoji[part], 64, 70);  // the playlist's season, large and faint behind
    g.save(); g.globalAlpha = .17; g.translate(400, 400); g.rotate(-.21); g.drawImage(glyph, -150, -150, 300, 300); g.restore();
    e.clearRect(0, 0, 128, 128); e.fillText(item.emoji, 64, 70);
    g.drawImage(glyph, 256 - 84, 176 - 84, 168, 168);
    g.fillStyle = '#fff6e0'; g.font = '50px "IM Fell English", Georgia, serif';
    const lines = []; let line = '';
    for (const word of item.title.split(' ')) {
      const next = line ? `${line} ${word}` : word;
      if (g.measureText(next).width > 400 && line) { lines.push(line); line = word; } else line = next;
    }
    lines.push(line);
    lines.forEach((text, i) => g.fillText(text, 256, 340 + (i - (lines.length - 1) / 2) * 58));
    return artwork[key] = canvas.toDataURL('image/png');
  }

  // "Playlist completa": the whole choir; "Playlist per voce": each voice alone and "in evidenza".
  // Every album is the same card: only the cover, which carries the name.
  function albumCard(v) {
    const li = document.createElement('li'), button = document.createElement('button');
    button.type = 'button'; button.className = 'album-card';
    button.append(album(v));
    button.setAttribute('aria-label', albumName(v));
    button.onclick = () => { voice = v; render(); showTab('playlist'); };
    li.append(button); return li;
  }
  function renderAlbums() {
    el('album-full').replaceChildren(albumCard('choir'));
    el('album-list').replaceChildren(...albumVoices.filter(v => v !== 'choir').map(albumCard));
  }

  function renderHead() {
    const list = songs(voice);
    el('playlist-cover').replaceChildren(album(voice, 'album album-large'));
    el('playlist-title').textContent = albumName(voice);
    const minutes = Math.round(list.reduce((sum, item) => sum + length(item), 0) / 60);
    el('playlist-detail').textContent = list.length
      ? `${list.length === 1 ? t('songCountOne') : t('songCount', {n:list.length})} · ${t('minutes', {n:minutes})}` : t('noRecordings');
    renderPlayButton();
  }
  function render() {
    renderHead();
    const list = songs(voice);
    el('playlist-tracks').replaceChildren(...list.map(item => {
      const li = document.createElement('li'); li.className = 'track-row'; li.dataset.id = item.id;
      if (queueVoice === voice && steps[index]?.item.id === item.id) li.classList.add('current');
      const play = document.createElement('button'); play.type = 'button'; play.className = 'track-play';
      play.setAttribute('aria-label', t('playFrom', {title:item.title}));
      const copy = document.createElement('span'); copy.className = 'track-copy';
      const title = document.createElement('span'); title.className = 'track-title'; title.textContent = item.title;
      const detail = document.createElement('span'); detail.className = 'track-detail';
      const n = item.tracks.length;
      // Only what the album name does not already say: the extra recordings and the length.
      const extra = item.tracks.map(track => stepVoice(track.voice)).filter(label => label !== albumName(voice));
      detail.textContent = [...extra, clock(length(item))].join(' · ');
      if (n > 1) detail.title = t('recordingCount', {n});
      copy.append(title, detail); play.append(cover(item, 'cover cover-small'), copy);
      play.onclick = () => start(item.id);
      const handle = document.createElement('span'); handle.className = 'booklet-handle'; handle.textContent = '⠿';
      handle.title = t('dragToSort'); handle.setAttribute('aria-hidden', 'true');
      handle.onpointerdown = event => drag(event, li);
      li.append(play, handle); return li;
    }));
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

  /* The queue: one step per recording of each song, in the album's order. */
  function buildQueue(v) {
    queueVoice = v;
    steps = songs(v).flatMap(item => item.tracks.map((track, i) => ({item, src:track.file,
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
    el('playlist-play').disabled = !songs(voice).length;
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
    el('mini-cover').replaceChildren(cover(step.item, 'cover cover-mini', queueVoice));
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
      // No ±10 s: without these handlers the lock screen shows previous / play-pause / next.
      seekbackward:null, seekforward:null};
    for (const [action, handler] of Object.entries(actions)) { try { navigator.mediaSession.setActionHandler(action, handler); } catch {} }
  }

  el('playlist-play').onclick = toggleQueue;
  const toggle = () => media.paused ? resume() : pause();
  el('mini-play').onclick = toggle;
  el('mini-next').onclick = next;
  // As in music apps: tapping the playing song opens its playlist; × ends the playback.
  const openQueue = () => { if (!queueVoice) return; voice = queueVoice; render(); showTab('playlist'); };
  el('mini-cover').onclick = openQueue; el('mini-copy').onclick = openQueue;
  function close() {
    if (!steps.length) return;
    media.pause(); media.removeAttribute('src'); media.load();
    steps = []; index = 0; queueVoice = null;
    if ('mediaSession' in navigator) { navigator.mediaSession.metadata = null; navigator.mediaSession.playbackState = 'none'; }
    updateNowPlaying(); markCurrent(); renderPlayButton();
  }
  el('mini-close').onclick = close;
  el('mini-previous').onclick = previous;
  el('mini-seek').oninput = () => { media.currentTime = Number(el('mini-seek').value); };

  async function load_() {
    const response = await fetch('api/recordings.json');
    if (!response.ok) throw Error(t('loadError'));
    data = await response.json(); renderAlbums();
  }
  return {
    load:load_, render, renderAlbums, pause, toggle, close, cover,
    get hasQueue() { return steps.length > 0; },
    get playing() { return !media.paused; },
    set onStart(callback) { onStart = callback; },
  };
})();
