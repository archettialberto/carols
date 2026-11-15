/* Booklet: join the light PDF editions of the chosen songs into one PDF, in the chosen order.
   With "pagine pari" every song gets an even page count (a blank page is added when needed), so
   in double-sided printing each song starts on a right-hand page of a ring binder.
   pdf-lib (vendored) is loaded only when a booklet is made. Rows are the app's one song row. */
const Booklet = (() => {
  let order = [], chosen = new Set(), byId = {};
  const el = id => document.getElementById(id);
  function loadPdfLib() {
    if (window.PDFLib) return Promise.resolve();
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'vendor/pdf-lib-1.17.1.min.js'; script.onload = resolve; script.onerror = reject;
      document.head.append(script);
    });
  }
  function render(songs) {
    byId = Object.fromEntries(songs.map(s => [s.id, s]));
    if (!order.length) order = songs.map(s => s.id);
    const list = el('booklet-list');
    list.innerHTML = order.map((id, i) => {
      const song = byId[id];
      return `<li data-id="${UI.esc(id)}">${UI.row({tag:'label', number:i + 1, song,
        meta:UI.clock(song.performance.duration * 60 / (song.tempo || 96)),
        end:`<input class="song-check" type="checkbox" ${chosen.has(id) ? 'checked' : ''}>`})}${UI.grip(song.title)}</li>`;
    }).join('');
    list.onchange = event => {
      const id = event.target.closest('li').dataset.id;
      event.target.checked ? chosen.add(id) : chosen.delete(id); update();
    };
    list.querySelectorAll('.grip').forEach(grip => {
      grip.onpointerdown = event => UI.drag(event, grip.closest('li'), list, ids => {
        order = ids; list.querySelectorAll('.song-num').forEach((n, i) => { n.textContent = i + 1; });
      });
    });
    update();
  }
  function selectAll(checked) {
    checked ? order.forEach(id => chosen.add(id)) : chosen.clear();
    el('booklet-list').querySelectorAll('input').forEach(box => box.checked = checked);
    update();
  }
  function update(status) {
    el('booklet-all').checked = chosen.size === order.length && order.length > 0;
    el('booklet-all').indeterminate = chosen.size > 0 && chosen.size < order.length;
    el('booklet-make').disabled = !chosen.size;
    el('booklet-status').textContent = status ?? (chosen.size ? (chosen.size === 1 ? t('songCountOne') : t('songCount', {n:chosen.size})) : '');
  }
  async function make() {
    const button = el('booklet-make'); button.disabled = true; update(t('preparing'));
    try {
      await loadPdfLib();
      const out = await PDFLib.PDFDocument.create();
      for (const id of order.filter(id => chosen.has(id))) {
        const bytes = await (await fetch(`exports/${encodeURIComponent(id)}-digital.pdf`)).arrayBuffer();
        const doc = await PDFLib.PDFDocument.load(bytes);
        const pages = await out.copyPages(doc, doc.getPageIndices());
        pages.forEach(page => out.addPage(page));
        if (el('booklet-even').checked && pages.length % 2) out.addPage([pages.at(-1).getWidth(), pages.at(-1).getHeight()]);
      }
      const blob = new Blob([await out.save()], {type:'application/pdf'});
      const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = 'raccolta-canti.pdf';
      document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(link.href), 60000);
      update(t('pdfReady', {n:out.getPageCount()}));
    } catch (error) {
      update(t('pdfError')); console.error(error);
    } finally { button.disabled = !chosen.size; }
  }
  el('booklet-make').onclick = make;
  el('booklet-all').onchange = event => selectAll(event.target.checked);
  return {render, make, selectAll, _state:() => ({order, chosen})};
})();
