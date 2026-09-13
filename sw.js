// Jarvis senza rete.
// Con la rete, pagina e dati arrivano sempre freschi dalla rete (così non si vede
// mai una versione vecchia) e se ne salva una copia. Senza rete si usa l'ultima
// copia salvata. Solo richieste dello stesso sito.
const CACHE = 'jarvis-1';
const FISSI = ['./', 'index.html', 'manifest.webmanifest', 'img/icona-180.png', 'img/stemma.jpg',
               'font/barlow-condensed-500.woff2', 'font/barlow-condensed-600.woff2', 'font/barlow-condensed-700.woff2'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FISSI)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(nomi => Promise.all(nomi.filter(n => n !== CACHE).map(n => caches.delete(n))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET' || new URL(r.url).origin !== location.origin) return;
  const chiave = r.url.split('?')[0];          // i dati si chiedono con ?cb=…: la copia vale per tutti
  e.respondWith(
    fetch(r).then(risposta => {
      if (risposta.ok) {
        const copia = risposta.clone();
        caches.open(CACHE).then(c => c.put(chiave, copia));
      }
      return risposta;
    }).catch(() => caches.match(chiave).then(c => c || caches.match('./')))
  );
});
