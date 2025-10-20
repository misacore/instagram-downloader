const CACHE_NAME = 'instagram-downloader-v2';
const urlsToCache = [
  '/app/',
  '/app/static/manifest.json'
];

// نصب Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache opened');
        return cache.addAll(urlsToCache);
      })
  );
  self.skipWaiting();
});

// فعال کردن Service Worker
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      ).then(() => self.clients.claim());
    })
  );
});

// درخواست‌های شبکه
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // اگر در کش بود، برگردان
        if (response) {
          return response;
        }
        // در غیر این صورت از شبکه بگیر
        return fetch(event.request);
      }
    )
  );
});
