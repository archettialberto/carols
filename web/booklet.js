/* Booklet: join the light PDF editions of the chosen songs into one PDF, in the chosen order.
   With “pagine pari” every song gets an even page count (a blank page is added when needed), so
   in double-sided printing each song starts on a right-hand page of a ring binder.
   pdf-lib (vendored) is loaded only when a booklet is made. */
const Booklet = (() => {
  let order = [], chosen = new Set();
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
    if (!order.length) order = songs.map(s => s.id);
    const byId = Object.fromEntries(songs.map(s => [s.id, s]));
    el('booklet-list').replaceChildren(...order.map((id, index) => {
      const li = document.createElement('li'); li.className = 'booklet-row';
      const label = document.createElement('label');
      const box = document.createElement('input'); box.type = 'checkbox'; box.checked = chosen.has(id);
      box.onchange = () => { box.checked ? chosen.add(id) : chosen.delete(id); update(); };
      const icon = document.createElement('span'); icon.className = 'booklet-icon'; icon.setAttribute('aria-hidden', 'true');
      icon.textContent = byId[id].emoji || '🎵';
      const title = document.createElement('span'); title.className = 'booklet-title'; title.textContent = byId[id].title;
      label.append(box, icon, title);
      const handle = document.createElement('span'); handle.className = 'booklet-handle'; handle.textContent = '⠿';
      handle.setAttribute('aria-hidden', 'true'); handle.title = 'Trascina per riordinare';
      handle.onpointerdown = event => drag(event, li, songs);
      li.dataset.id = id; li.append(label, handle);
      return li;
    }));
    update();
  }
  // Drag a row by its handle (mouse or touch): rows reorder live under the pointer.
  function drag(event, row, songs) {
    event.preventDefault();
    const list = el('booklet-list'); row.classList.add('dragging');
    const move = e => {
      const over = [...list.children].find(other => other !== row && (() => {
        const box = other.getBoundingClientRect(); return e.clientY > box.top && e.clientY < box.bottom; })());
      if (!over) return;
      const box = over.getBoundingClientRect();
      list.insertBefore(row, e.clientY < box.top + box.height / 2 ? over : over.nextSibling);
    };
    const end = () => {
      row.classList.remove('dragging');
      removeEventListener('pointermove', move); removeEventListener('pointerup', end);
      removeEventListener('pointercancel', end);
      order = [...list.children].map(li => li.dataset.id);
    };
    // Listen on the window: moving the row in the DOM would drop a pointer capture.
    addEventListener('pointermove', move); addEventListener('pointerup', end); addEventListener('pointercancel', end);
  }
  function selectAll(checked) {
    checked ? order.forEach(id => chosen.add(id)) : chosen.clear();
    el('booklet-list').querySelectorAll('input').forEach(box => box.checked = checked);
    update();
  }
  function update() {
    el('booklet-all').checked = chosen.size === order.length && order.length > 0;
    el('booklet-all').indeterminate = chosen.size > 0 && chosen.size < order.length;
    el('booklet-make').disabled = !chosen.size;
    el('booklet-status').textContent = chosen.size ? `${chosen.size} ${chosen.size === 1 ? 'brano' : 'brani'}` : '';
  }
  async function make() {
    const button = el('booklet-make'); button.disabled = true; el('booklet-status').textContent = 'Preparazione…';
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
      const blob = new Blob([await out.save()], {type: 'application/pdf'});
      const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = 'raccolta-canti.pdf';
      document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(link.href), 60000);
      el('booklet-status').textContent = `PDF pronto: ${out.getPageCount()} pagine`;
    } catch (error) {
      el('booklet-status').textContent = 'Impossibile creare il PDF.'; console.error(error);
    } finally { button.disabled = !chosen.size; }
  }
  return {render, make, selectAll, _state: () => ({order, chosen})};
})();
