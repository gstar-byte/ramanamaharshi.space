// Ramana Maharshi Knowledge Base - Service Worker v13 (优化版)
const CACHE_NAME = 'ramana-kb-v13';

// 预缓存核心资源（合并后的 app.js 替代 script.js + search.js）
const CORE_ASSETS = [
  '/',
  '/index.html',
  '/styles.min.css',
  '/bundle.min.js',
  '/manifest.json'
];

// Install: 预缓存核心资源，使用 Promise.all 并行处理
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      console.log('[SW] Installing v13...');
      // 并行预缓存，提升安装速度
      await Promise.all(
        CORE_ASSETS.map(async (url) => {
          try {
            const resp = await fetch(url, { cache: 'no-cache' });
            if (resp.ok) {
              await cache.put(url, resp.clone());
              console.log('[SW] Pre-cached:', url);
            }
          } catch (err) {
            console.warn('[SW] Failed to pre-cache:', url, err.message);
          }
        })
      );
      console.log('[SW] Install complete');
      return self.skipWaiting();
    })
  );
});

// Activate: 删除旧缓存，接管所有客户端
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => {
          console.log('[SW] Deleting old cache:', key);
          return caches.delete(key);
        })
      );
    }).then(() => {
      console.log('[SW] Activate complete');
      return self.clients.claim();
    })
  );
});

// Fetch: 网络优先 + 缓存回退（含 HTML 页面）
self.addEventListener('fetch', (e) => {
  const { request } = e;
  const url = new URL(request.url);

  // 跳过非 GET / 非同域 / chrome-extension 请求
  if (request.method !== 'GET' ||
      url.origin !== self.location.origin ||
      url.protocol === 'chrome-extension:') {
    return;
  }

  // GA 请求直接跳过（不缓存不拦截）
  if (url.hostname === 'www.google-analytics.com' ||
      url.hostname === 'analytics.google.com' ||
      url.hostname === 'www.googletagmanager.com') {
    return;
  }

  // 判断是否为可缓存的静态资源
  const path = url.pathname;
  const isCacheable = (
    path.endsWith('/') ||
    path.endsWith('.html') ||
    path.endsWith('.css') ||
    path.endsWith('.js') ||
    path.endsWith('.json') ||
    path.endsWith('.png') ||
    path.endsWith('.jpg') ||
    path.endsWith('.jpeg') ||
    path.endsWith('.webp') ||
    path.endsWith('.svg') ||
    path.endsWith('.ico') ||
    path.endsWith('.woff2') ||
    path.endsWith('.woff')
  );

  if (!isCacheable) {
    return; // 不可缓存的请求直接透传
  }

  e.respondWith(
    fetch(request, { credentials: 'same-origin' })
      .then((resp) => {
        // 网络请求成功 → 动态缓存
        if (resp.ok) {
          const clone = resp.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, clone);
          });
        }
        return resp;
      })
      .catch(() => {
        // 网络失败 → 从缓存回退
        return caches.match(request).then((cached) => {
          if (cached) {
            console.log('[SW] Offline fallback from cache:', path);
            return cached;
          }
          // 对 HTML 请求，返回缓存的首页（比纯文本错误体验更好）
          if (path.endsWith('.html') || path.endsWith('/')) {
            return caches.match('/index.html').then((fallback) => {
              if (fallback) return fallback;
              return new Response(
                '<html><body><h2>离线模式</h2><p>请先联网访问本页面，以便离线缓存。</p><a href="/">返回首页</a></body></html>',
                { status: 200, headers: { 'Content-Type': 'text/html; charset=utf-8' } }
              );
            });
          }
          return new Response('', { status: 503 });
        });
      })
  );
});
