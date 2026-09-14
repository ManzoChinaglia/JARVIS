// Jarvis senza rete.
// Con la rete, pagina e dati arrivano sempre freschi dalla rete (così non si vede
// mai una versione vecchia) e se ne salva una copia. Senza rete si usa l'ultima
// copia salvata. Solo richieste dello stesso sito.
const CACHE = 'jarvis-2';
const NUMERO = 'jarvis-numero';   // avvisi non letti: il numero sull'icona (non si cancella con le copie vecchie)
const FISSI = ['./', 'index.html', 'manifest.webmanifest', 'img/icona-180.png', 'img/sfondo.jpg',
               'font/barlow-condensed-500.woff2', 'font/barlow-condensed-600.woff2', 'font/barlow-condensed-700.woff2'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FISSI)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(nomi => Promise.all(nomi.filter(n => n !== CACHE && n !== NUMERO).map(n => caches.delete(n))))
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

// Notifiche di Jarvis: il workflow manda {titolo, testo, id, livello}; l'iPhone vuole
// che ogni messaggio diventi una notifica visibile. Lo stesso id la sostituisce.
// a ogni notifica il numero sull'icona di Jarvis cresce di uno; aprendo gli avvisi l'app lo azzera
async function aumentaNumero() {
  try {
    const c = await caches.open(NUMERO), r = await c.match('numero');
    const n = (r ? parseInt(await r.text(), 10) || 0 : 0) + 1;
    await c.put('numero', new Response(String(n)));
    if (self.navigator && self.navigator.setAppBadge) await self.navigator.setAppBadge(n);
  } catch (err) {}
}
self.addEventListener('push', e => {
  let m = {};
  try { m = e.data ? e.data.json() : {}; } catch (err) { m = { testo: e.data ? e.data.text() : '' }; }
  e.waitUntil(Promise.all([
    self.registration.showNotification(m.titolo || 'Jarvis', {
      body: m.testo || '', tag: m.id || undefined, icon: 'img/icona-180.png', data: { id: m.id }
    }),
    aumentaNumero()
  ]));
});

// toccando la notifica si apre Jarvis (sull'iPhone l'app della Home, non Safari)
self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then(finestre => {
    const aperta = finestre.find(f => 'focus' in f);
    return aperta ? aperta.focus() : self.clients.openWindow('./');
  }));
});
