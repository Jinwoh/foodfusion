self.addEventListener('install', function(e) {
  console.log('Service Worker: Installed');
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
