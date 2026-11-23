/* Recording playlists, one "album" per voice. Each song plays the voice's own track, which
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
  const voiceName = voice => t({soprano:'albumSoprano', alto:'albumAlto', tenor:'albumTenor', bass:'albumBass'}[voice]);
  const albumName = album => album === 'choir' ? t('albumChoir')
    : album.startsWith('lead-') ? `${voiceName(UI.part(album))} ${t('inEvidence')}` : voiceName(album);
  const stepVoice = voice => ({all:t('voiceAll'), 'tenor-bass':t('voiceTenorBass')}[voice] || albumName(voice));
  let data = {}, voice = 'choir', steps = [], index = 0, queueVoice = null, onStart = () => {};
  const media = new Audio(); media.preload = 'auto'; media.setAttribute('playsinline', '');

  // Every album plays its songs in the choir's fixed order (music.SONG_ORDER), as Spartiti.
  const songs = v => data[v] || [];
  const length = item => item.tracks.reduce((sum, track) => sum + track.seconds, 0);
  const cover = v => UI.cover(v, voiceName(UI.part(v)) || albumName(v), (voiceName(UI.part(v)) || '')[0], v.startsWith('lead-'));

  /* Lock-screen artwork: the song's tile drawn large (a canvas, as Media Session needs an image). */
  const artwork = {};
  async function artworkFor(item, v = queueVoice) {
    const part = UI.part(v), key = `${item.id}:${part}`;
    if (artwork[key]) return artwork[key];
    try { await document.fonts.load('52px "IM Fell English"'); } catch {}
    const canvas = document.createElement('canvas'); canvas.width = canvas.height = 512;
    const g = canvas.getContext('2d');
    g.fillStyle = UI.ink[part]; g.fillRect(0, 0, 512, 512);
    g.strokeStyle = '#e6d29c'; g.lineWidth = 4; g.strokeRect(26, 26, 460, 460); g.lineWidth = 1.6; g.strokeRect(40, 40, 432, 432);
    g.textAlign = 'center'; g.textBaseline = 'middle';
    // iOS Safari draws no colour emoji with a gradient fill or a large system-ui size: use a
    // solid fill, the emoji fonts first, and scale a 96px glyph up.
    const glyph = document.createElement('canvas'); glyph.width = glyph.height = 128;
    const e = glyph.getContext('2d'); e.textAlign = 'center'; e.textBaseline = 'middle'; e.fillStyle = '#000';
    e.font = '96px "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", sans-serif';
    e.fillText(UI.season[part], 64, 70);  // the playlist's season, large and faint behind
    g.save(); g.globalAlpha = .12; g.drawImage(glyph, 56, 56, 400, 400); g.restore();
    e.clearRect(0, 0, 128, 128); e.fillText(item.emoji, 64, 70);
    g.drawImage(glyph, 256 - 84, 170 - 84, 168, 168);
    g.fillStyle = '#fbf3df'; g.font = '50px "IM Fell English", Georgia, serif';
    const lines = []; let line = '';
    for (const word of item.title.split(' ')) {
      const next = line ? `${line} ${word}` : word;
      if (g.measureText(next).width > 400 && line) { lines.push(line); line = word; } else line = next;
    }
    lines.push(line);
    lines.forEach((text, i) => g.fillText(text, 256, 350 + (i - (lines.length - 1) / 2) * 58));
    return artwork[key] = canvas.toDataURL('image/png');
  }

  // "Playlist completa" (the whole choir) and "Playlist per voce": every album is its cover alone.
  function renderAlbums() {
    const card = v => `<li><a class="album" href="#/playlist/${v}" aria-label="${UI.esc(albumName(v))}">${cover(v)}</a></li>`;
    el('album-full').innerHTML = card('choir');
    el('album-list').innerHTML = albumVoices.filter(v => v !== 'choir').map(card).join('');
  }

  function renderHead() {
    const list = songs(voice);
    el('playlist-cover').innerHTML = cover(voice);
    el('playlist-title').textContent = albumName(voice);
    const minutes = Math.round(list.reduce((sum, item) => sum + length(item), 0) / 60);
    el('playlist-detail').textContent = list.length
      ? `${list.length === 1 ? t('songCountOne') : t('songCount', {n:list.length})} · ${t('minutes', {n:minutes})}` : t('noRecordings');
    renderPlayButton();
  }
  /* The same rows as Spartiti, on the album's tile; a tap plays from that song. */
  function render() {
    renderHead();
    const list = el('playlist-tracks');
    list.innerHTML = songs(voice).map((item, i) => {
      // Only what the album name does not already say: the extra recordings and the length.
      const extra = item.tracks.map(track => stepVoice(track.voice)).filter(label => label !== albumName(voice));
      return `<li data-id="${UI.esc(item.id)}">${UI.row({tag:'button', attrs:`type="button" aria-label="${UI.esc(t('playFrom', {title:item.title}))}"`,
        number:i + 1, song:item, album:voice, meta:[...extra, UI.clock(length(item))].join(' · '),
        end:'<span class="eq" aria-hidden="true"><i></i><i></i><i></i></span>'})}</li>`;
    }).join('');
    list.querySelectorAll('li').forEach(li => { li.querySelector('.song-row').onclick = () => start(li.dataset.id); });
    markCurrent();
  }
  function open(v) {
    voice = albumVoices.includes(v) ? v : 'choir';
    render();
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
    index = i; media.src = steps[index].src;
    if (autoplay) resume();
    updateNowPlaying(); markCurrent();
  }
  function markCurrent() {
    const id = queueVoice === voice ? steps[index]?.item.id : null;
    el('playlist-tracks').querySelectorAll('li').forEach(li => li.querySelector('.song-row').toggleAttribute('aria-current', li.dataset.id === id));
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
    document.body.dataset.playlistPlaying = playingNow;
    el('playlist-play').dataset.playing = !!(ours && playingNow);
    el('playlist-play').querySelector('.label').textContent = ours && playingNow ? t('pause') : ours ? t('resume') : t('playAll');
    el('playlist-play').disabled = !songs(voice).length;
    el('mini-play').dataset.playing = playingNow;
    el('mini-play').setAttribute('aria-label', t(playingNow ? 'pause' : 'play'));
  }
  function renderProgress() {
    const duration = Number.isFinite(media.duration) ? media.duration : 0;
    el('mini-seek').max = duration || 1; el('mini-seek').value = media.currentTime;
    el('mini-seek').style.setProperty('--fill', `${duration ? media.currentTime / duration * 100 : 0}%`);
    if ('mediaSession' in navigator && duration) {
      try { navigator.mediaSession.setPositionState({duration, position:Math.min(duration, media.currentTime), playbackRate:1}); } catch {}
    }
  }
  async function updateNowPlaying() {
    const step = steps[index];
    document.dispatchEvent(new Event('playlistchange'));
    if (!step) return;
    el('mini-cover').innerHTML = UI.tile(step.item, queueVoice);
    el('mini-title').textContent = step.item.title;
    el('mini-open').href = `#/playlist/${queueVoice}`;
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
  // iOS reads these only once the <audio> is "Now Playing", and falls back to its own ±10 s otherwise:
  // they are registered again on every 'playing' (with the seek actions explicitly cleared).
  function registerActions() {
    if (!('mediaSession' in navigator)) return;
    const actions = {play:resume, pause, previoustrack:previous, nexttrack:next,
      seekto:details => { media.currentTime = details.seekTime; },
      // No ±10 s: without these handlers the lock screen shows previous / play-pause / next.
      seekbackward:null, seekforward:null};
    for (const [action, handler] of Object.entries(actions)) { try { navigator.mediaSession.setActionHandler(action, handler); } catch {} }
  }
  registerActions();
  media.addEventListener('playing', registerActions);

  el('playlist-play').onclick = toggleQueue;
  const toggle = () => media.paused ? resume() : pause();
  el('mini-play').onclick = toggle;
  el('mini-next').onclick = next;
  el('mini-previous').onclick = previous;
  el('mini-seek').oninput = () => { media.currentTime = Number(el('mini-seek').value); };
  // As in music apps: tapping the playing song opens its playlist (a link); × ends the playback.
  function close() {
    if (!steps.length) return;
    media.pause(); media.removeAttribute('src'); media.load();
    steps = []; index = 0; queueVoice = null;
    if ('mediaSession' in navigator) { navigator.mediaSession.metadata = null; navigator.mediaSession.playbackState = 'none'; }
    updateNowPlaying(); markCurrent(); renderPlayButton();
  }
  el('mini-close').onclick = close;

  async function load_() {
    const response = await fetch('api/recordings.json');
    if (!response.ok) throw Error(t('loadError'));
    data = await response.json(); renderAlbums();
    if (!el('playlist-panel').hidden) render();
  }
  return {
    load:load_, open, render, renderAlbums, pause, toggle, close,
    get hasQueue() { return steps.length > 0; },
    get playing() { return !media.paused; },
    set onStart(callback) { onStart = callback; },
  };
})();
