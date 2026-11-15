/* Shared drawing for every list and cover (Spartiti, playlists, PDF booklet, mini player):
   one song row, one song tile, one album cover. Rubrica: a Victorian hymnal printed in two inks. */
const UI = (() => {
  const esc = value => String(value).replace(/[&<>"]/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;'}[c]));
  const clock = seconds => `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
  // Deep inks per playlist: the whole choir black, then madder, ochre, pine and indigo, high to low.
  const ink = {choir:'#1e1a16', soprano:'#7f2232', alto:'#8a5d17', tenor:'#2c5440', bass:'#283a5e'};
  const gilt = '#e6d29c', fell = "font-family:'IM Fell English',Georgia,serif";
  // One season per voice, never a song's emoji. ☀ and ❄ need U+FE0F to draw in colour; inside SVG
  // they are centred by the text anchor, so the old off-centre problem of HTML layout does not apply.
  const season = {choir:'🎄', soprano:'🌸', alto:'\u2600\uFE0F', tenor:'🍂', bass:'\u2744\uFE0F'};
  const part = album => (album || 'choir').replace(/^lead-/, '');

  /* A song's tile: the playlist's ink (the choir's black outside playlists) with its emoji. */
  function tile(song, album = 'choir') {
    return `<svg class="cover" viewBox="0 0 200 200" aria-hidden="true"><rect width="200" height="200" fill="${ink[part(album)]}"/>
      <rect x="12" y="12" width="176" height="176" fill="none" stroke="${gilt}" stroke-width="4"/>
      <text x="100" y="138" text-anchor="middle" font-size="104">${song.emoji || '🎵'}</text></svg>`;
  }
  /* An album cover is a typographic title page on a 200×200 grid: deep ink, double gilt rule,
     corner lozenges, the voice initial and name in IM Fell, the season faint behind, and for the
     "in evidenza" albums those words in the same gilt. */
  function cover(album, name, initial, lead) {
    const p = part(album);
    const corners = [[22, 22], [178, 22], [22, 178], [178, 178]].map(([x, y]) => `<path d="M${x} ${y - 5}l5 5-5 5-5-5z" fill="${gilt}"/>`).join('');
    const title = p === 'choir'
      ? `<text x="100" y="96" text-anchor="middle" font-size="33" fill="#fbf3df" style="${fell}">Christmas</text>
         <text x="100" y="132" text-anchor="middle" font-size="31" font-style="italic" fill="#fbf3df" style="${fell}">Carols</text>`
      : `<text x="100" y="${lead ? 112 : 118}" text-anchor="middle" font-size="92" fill="#fbf3df" style="${fell}">${esc(initial)}</text>
         <text x="100" y="${lead ? 140 : 152}" text-anchor="middle" font-size="19" font-style="italic" fill="#efe1bb" style="${fell}">${esc(name)}</text>
         ${lead ? `<text x="100" y="171" text-anchor="middle" font-size="16" font-style="italic" fill="${gilt}" style="${fell}">${esc(t('inEvidence'))}</text>` : ''}`;
    return `<svg class="cover" viewBox="0 0 200 200" role="img" aria-label="${esc(lead ? `${name} ${t('inEvidence')}` : name)}">
      <rect width="200" height="200" fill="${ink[p]}"/>
      <text x="100" y="150" text-anchor="middle" font-size="150" opacity=".12">${season[p]}</text>
      <rect x="10" y="10" width="180" height="180" fill="none" stroke="${gilt}" stroke-width="1.6"/>
      <rect x="15" y="15" width="170" height="170" fill="none" stroke="${gilt}" stroke-width=".7"/>
      ${corners}${title}</svg>`;
  }
  /* The one song row: number, tile, title, length, and a trailing slot (equaliser or tick box).
     `tag` is the row element: a link (Spartiti), a button (playlists) or a label (PDF booklet). */
  function row({tag = 'a', attrs = '', number, song, album, meta, end = ''}) {
    return `<${tag} class="song-row" ${attrs}><span class="song-num" aria-hidden="true">${number}</span>
      <span class="song-art">${tile(song, album)}</span>
      <span class="song-title">${esc(song.title)}</span>
      <span class="song-meta">${esc(meta)}</span>${end}</${tag}>`;
  }
  const grip = title => `<button class="grip" type="button" aria-label="${esc(t('dragToSort'))}: ${esc(title)}"><svg class="ic"><use href="icons.svg#grip"/></svg></button>`;
  /* Drag a row by its grip (mouse or touch): rows reorder live under the pointer. */
  function drag(event, row, list, done) {
    event.preventDefault(); row.classList.add('dragging');
    const move = e => {
      const over = [...list.children].find(other => { if (other === row) return false; const b = other.getBoundingClientRect(); return e.clientY > b.top && e.clientY < b.bottom; });
      if (!over) return;
      const b = over.getBoundingClientRect();
      list.insertBefore(row, e.clientY < b.top + b.height / 2 ? over : over.nextSibling);
    };
    // Listen on the window: moving the row in the DOM would drop a pointer capture.
    const end = () => {
      row.classList.remove('dragging');
      removeEventListener('pointermove', move); removeEventListener('pointerup', end); removeEventListener('pointercancel', end);
      done([...list.children].map(li => li.dataset.id));
    };
    addEventListener('pointermove', move); addEventListener('pointerup', end); addEventListener('pointercancel', end);
  }
  return {esc, clock, ink, season, part, tile, cover, row, grip, drag};
})();
