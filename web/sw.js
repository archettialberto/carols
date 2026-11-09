/* Offline fallback for the installed app. Always tries the local server first, so
   updated songs and code win; the cache is used only when the server is unreachable.
   Browsers register service workers only on localhost or HTTPS (GitHub Pages is HTTPS,
   so there the installed app also works offline after a first visit). */
const CACHE = 'carol-choir-v7';
// Relative paths: the app may live in a sub-folder (e.g. GitHub Pages /<repo>/).
const SHELL = ['./', 'index.html', 'style.css', 'appearance.js', 'i18n.js', 'notation.js', 'sounds.js', 'player.js',
  'vendor/abcjs-basic-6.7.2.min.js', 'booklet.js', 'fonts/im-fell-english.woff2', 'manifest.webmanifest', 'icons/icon-192.png', 'api/songs.json'];
self.addEventListener('install', event => event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(SHELL)).then(() => self.skipWaiting())));
self.addEventListener('activate', event => event.waitUntil(
  caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim())));
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.origin !== location.origin) return;
  event.respondWith(fetch(event.request).then(response => {
    if (response.ok && !/\.(pdf|mp3)$/.test(url.pathname) && response.status === 200) {
      const copy = response.clone(); caches.open(CACHE).then(cache => cache.put(event.request, copy));
    }
    return response;
  }).catch(() => caches.match(event.request).then(hit => hit || caches.match('./'))));
});
