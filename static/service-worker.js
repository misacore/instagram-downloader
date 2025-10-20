const CACHE_NAME = 'instagram-downloader-v3';

// نصب Service Worker
self.addEventListener('install', event => {
  console.log('Service Worker installing...');
  self.skipWaiting();
});

// فعال کردن Service Worker
self.addEventListener('activate', event => {
  console.log('Service Worker activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(cacheName => cacheName !== CACHE_NAME)
          .map(cacheName => caches.delete(cacheName))
      );
    }).then(() => {
      console.log('Service Worker activated');
      return clients.claim();
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
