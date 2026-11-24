// 렛츠아트 디지털 액자 PWA 오프라인 캐시 서비스 워커
const CACHE_NAME = "letsart-cache-v1";
const BASE = new URL("./", self.location).pathname;

const ASSETS_TO_CACHE = [
  BASE,
  BASE + "index.html",
  BASE + "artwork.html",
  BASE + "admin.html",
  BASE + "manifest.webmanifest",
  BASE + "assets/icons/favicon-32.png",
  BASE + "assets/icons/apple-touch-icon.png",
  BASE + "assets/icons/icon-192.png",
  BASE + "assets/icons/icon-512.png"
];

self.addEventListener("install", (e) => {
  self.skipWaiting();
  e.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE).catch(() => {});
    })
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((k) => {
          if (k.startsWith("letsart-") && k !== CACHE_NAME) {
            return caches.delete(k);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  const url = new URL(req.url);

  // 같은 오리진 GET 요청만 처리 (외부 유튜브/CDN 대용량 이미지는 브라우저 기본 캐시 활용)
  if (req.method !== "GET" || url.origin !== self.location.origin) {
    return;
  }

  e.respondWith(
    fetch(req)
      .then((networkRes) => {
        if (networkRes && networkRes.status === 200) {
          const resClone = networkRes.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(req, resClone);
          });
        }
        return networkRes;
      })
      .catch(() => {
        return caches.match(req).then((cachedRes) => {
          if (cachedRes) return cachedRes;
          if (req.mode === "navigate") {
            return caches.match(BASE + "index.html");
          }
        });
      })
  );
});
