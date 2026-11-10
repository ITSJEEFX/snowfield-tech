/* SnowField Tech: guarda o app no aparelho para abrir sem internet. Versão gerada pelo build.py */
const VERSAO = 'snowfield-34f74de7ba';
const ARQUIVOS = ['./', './index.html', './manifest.webmanifest', './vendor/jspdf.umd.min.js', './fonts/inter-latin-400-normal.woff2', './fonts/inter-latin-500-normal.woff2', './fonts/inter-latin-600-normal.woff2', './fonts/inter-latin-700-normal.woff2', './icons/icon-192.png', './icons/icon-512.png', './icons/maskable-512.png', './icons/apple-touch-icon.png', './icons/favicon-32.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(VERSAO).then(c => c.addAll(ARQUIVOS)));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k.startsWith('snowfield-') && k !== VERSAO).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('message', e => { if (e.data === 'atualizar') self.skipWaiting(); });

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;
  if (req.mode === 'navigate') {
    /* página: usa a versão guardada desta instalação; a nova chega pelo aviso "Atualizar" */
    e.respondWith(caches.match('./index.html').then(r => r || fetch(req)));
    return;
  }
  e.respondWith(caches.match(req, { ignoreSearch: true }).then(r => r || fetch(req)));
});
