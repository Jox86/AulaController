const CACHE = 'aulacontrol-shell-v1';
const ASSETS = ['/', '/manifest.webmanifest'];
self.addEventListener('install', event => event.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS))));
self.addEventListener('activate', event => event.waitUntil(self.clients.claim()));
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET' || new URL(event.request.url).origin !== self.location.origin) return;
  event.respondWith(caches.match(event.request).then(hit => hit || fetch(event.request).then(res => {
    const copy = res.clone(); caches.open(CACHE).then(c => c.put(event.request, copy)); return res;
  }).catch(() => caches.match('/'))));
});