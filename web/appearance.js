/* Apply before the page paints; "system" also follows live device changes. */
const appearance = (() => {
  const device = matchMedia('(prefers-color-scheme: dark)');
  let mode = 'system';
  try {
    const saved = localStorage.getItem('carols-theme');
    if (['light','dark','system'].includes(saved)) mode = saved;
  } catch (_) {}
  function apply() {
    const resolved = mode === 'system' ? (device.matches ? 'dark' : 'light') : mode;
    document.documentElement.dataset.theme = resolved;
    document.documentElement.style.colorScheme = resolved;
    document.querySelector('meta[name="theme-color"]').content = resolved === 'dark' ? '#101714' : '#f7f5ef';
    document.dispatchEvent(new CustomEvent('appearancechange',{detail:resolved}));
  }
  device.addEventListener('change', apply);
  apply();
  return {
    get mode() { return mode; },
    set(value) {
      if (!['light','dark','system'].includes(value)) return;
      mode = value;
      try { localStorage.setItem('carols-theme', mode); } catch (_) {}
      apply();
    },
  };
})();
