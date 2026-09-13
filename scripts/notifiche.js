// Manda sull'iPhone gli stessi avvisi del pannello «Avvisi» di Jarvis.
//
// Gira nel workflow dopo lo script dei dati: esegue il codice dell'app (come le
// prove) sui dati appena scaricati e invia solo gli avvisi mai inviati prima,
// segnati in dati/notifiche.json (solo i codici degli avvisi, niente di segreto).
//
// Due canali:
// - notifiche di Jarvis (Web Push): arrivano con l'icona di Jarvis e toccandole si
//   apre l'app sulla Home (un link, anche da ntfy, sull'iPhone apre sempre Safari).
//   Servono l'iscrizione dell'iPhone (PUSH_ISCRIZIONE, l'utente la copia dall'app)
//   e la chiave privata (PUSH_CHIAVE), tutte e due nei Secrets di GitHub; la chiave
//   pubblica è CHIAVE_PUSH in index.html.
// - ntfy, di riserva: se le notifiche di Jarvis non sono attive, se un invio
//   fallisce o se l'iPhone ha chiuso l'iscrizione. L'argomento (NTFY_ARGOMENTO) è
//   segreto e sta solo nei Secrets.
// Senza nessun canale non invia e non segna niente, così appena se ne imposta uno
// arriva tutto. Un errore non fa mai fallire il giro.
//
// Uso: node scripts/notifiche.js   (con PROVA_NOTIFICHE=true aggiunge una notifica di prova)
'use strict';
const crypto = require('crypto'), fs = require('fs'), path = require('path'), vm = require('vm');

const REPO = path.join(__dirname, '..');
const REGISTRO = path.join(REPO, 'dati', 'notifiche.json');
const APP = 'https://manzochinaglia.github.io/JARVIS/';
const MASSIMO = 6;                                      // mai più di sei notifiche per giro
const PRIORITA = { urgente: 4, attenzione: 3, info: 2 };  // scala di ntfy: 1 minima, 5 massima
const ETICHETTE = { urgente: ['rotating_light'], attenzione: ['warning'], info: ['soccer'] };
const RIATTIVA = { id: 'riattiva', livello: 'urgente', titolo: 'Riattiva le notifiche di Jarvis',
  testo: 'L\'iPhone ha chiuso l\'iscrizione. Apri Jarvis dalla Home → campanella → «Attiva le notifiche», ' +
         'copia il codice e mettilo su GitHub nel Secret PUSH_ISCRIZIONE. Intanto gli avvisi arrivano qui.' };

/* Gli avvisi calcolati dall'app sui file di dati/. dati: file da sostituire (prove). */
async function avvisiDellApp({ repo = REPO, adesso = Date.now(), dati = {} } = {}) {
  const html = fs.readFileSync(path.join(repo, 'index.html'), 'utf8');
  const codice = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].pop()[1];
  const VeraData = Date;
  class Orologio extends VeraData {
    constructor(...a) { a.length ? super(...a) : super(adesso); }
    static now() { return adesso; }
  }
  const nodi = {};
  const nodo = () => ({ textContent: '', innerHTML: '', value: '', style: {}, dataset: {},
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    addEventListener() {}, click() {}, focus() {}, blur() {} });
  const ctx = {
    Date: Orologio, console: { log() {}, error() {}, warn() {} }, URLSearchParams, Promise, Object, String, Math, Set, JSON,
    setInterval() {}, setTimeout: () => 0, clearTimeout() {},
    localStorage: { getItem: () => null, setItem() {} },
    location: { search: '', host: 'manzochinaglia.github.io', pathname: '/JARVIS/' },
    document: { getElementById: id => nodi[id] || (nodi[id] = nodo()), querySelector: () => nodo(), querySelectorAll: () => [] },
    fetch: async url => {
      const f = url.split('?')[0], nome = f.replace(/^dati\//, '');
      if (nome in dati) {
        const v = dati[nome];
        return v === null ? { ok: false, status: 404 } : { ok: true, status: 200, json: async () => JSON.parse(JSON.stringify(v)) };
      }
      const p = path.join(repo, f);
      if (!fs.existsSync(p)) return { ok: false, status: 404 };
      const testo = fs.readFileSync(p, 'utf8');
      return { ok: true, status: 200, json: async () => JSON.parse(testo) };
    }
  };
  ctx.window = ctx;
  vm.createContext(ctx);
  vm.runInContext(codice + '\n;globalThis.__pronto = () => !!D && mia.length > 0;' +
                  'globalThis.__avvisi = () => avvisi(prossima());', ctx);
  for (let i = 0; i < 100 && !ctx.__pronto(); i++) await new Promise(r => setTimeout(r, 20));
  if (!ctx.__pronto()) throw new Error('l\'app non ha caricato i dati');
  return ctx.__avvisi();
}

function leggiRegistro(file) {
  try { return JSON.parse(fs.readFileSync(file, 'utf8')); } catch (e) { return { inviati: [] }; }
}
/* chiave pubblica delle notifiche: una sola copia, in index.html */
function chiavePubblica(repo = REPO) {
  const m = fs.readFileSync(path.join(repo, 'index.html'), 'utf8').match(/const CHIAVE_PUSH = '([A-Za-z0-9_-]+)'/);
  return m ? m[1] : null;
}
/* l'iscrizione copiata dall'app: JSON con indirizzo e chiavi, altrimenti niente */
function leggiIscrizione(testo) {
  if (!testo) return null;
  try {
    const s = JSON.parse(testo);
    return s && s.endpoint && s.keys && s.keys.p256dh && s.keys.auth ? s : null;
  } catch (e) { return null; }
}
/* impronta dell'iscrizione per il registro, che è pubblico: dice se è cambiata senza rivelarla */
const impronta = s => crypto.createHash('sha256').update(s.endpoint).digest('hex').slice(0, 12);

function opzioniPush(messaggio, { chiave, pubblica }) {
  return { vapidDetails: { subject: APP, publicKey: pubblica, privateKey: chiave },
           TTL: 24 * 3600, urgency: messaggio.livello === 'urgente' ? 'high' : 'normal' };
}
async function spedisciPush(iscrizione, messaggio, chiavi) {
  const webpush = require('web-push');                  // installato dal workflow solo per questo passo
  return webpush.sendNotification(iscrizione, JSON.stringify(messaggio), opzioniPush(messaggio, chiavi));
}
async function ntfy(invia, argomento, a) {
  try {
    const r = await invia('https://ntfy.sh/', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic: argomento, title: a.titolo, message: a.testo,
                             priority: PRIORITA[a.livello], tags: ETICHETTE[a.livello], click: APP })
    });
    if (r.ok) return true;
    console.log(`[notifiche] ntfy ha risposto ${r.status}: riprovo al prossimo giro.`);
  } catch (e) {
    console.log(`[notifiche] invio con ntfy fallito (${e.message}): riprovo al prossimo giro.`);
  }
  return false;
}

async function main({ argomento = process.env.NTFY_ARGOMENTO, iscrizione = process.env.PUSH_ISCRIZIONE,
                      chiave = process.env.PUSH_CHIAVE, prova = process.env.PROVA_NOTIFICHE === 'true',
                      invia = fetch, spedisci = spedisciPush, adesso = Date.now(),
                      registro = REGISTRO, repo = REPO, dati = {} } = {}) {
  const lista = await avvisiDellApp({ repo, adesso, dati });
  const reg = leggiRegistro(registro), gia = new Set(reg.inviati || []);
  let nuovi = lista.filter(a => !gia.has(a.id));
  if (prova) nuovi.unshift({ id: 'prova-' + new Date(adesso).toISOString(), livello: 'info', titolo: 'Notifica di prova',
                             testo: 'Le notifiche funzionano. Toccala: si apre Jarvis.' });
  nuovi = nuovi.slice(0, MASSIMO);

  const sub = leggiIscrizione(iscrizione), pubblica = chiavePubblica(repo);
  if (iscrizione && !sub) console.log('[notifiche] PUSH_ISCRIZIONE non è un\'iscrizione valida: uso ntfy.');
  let daJarvis = !!(sub && chiave && pubblica) && reg.push_scaduta !== impronta(sub);
  if (!daJarvis && !argomento) {
    console.log(`[notifiche] nessun canale impostato: ${nuovi.length} avvisi nuovi non inviati.`);
    return { inviati: [], nuovi, daJarvis: 0 };
  }

  const fatti = [];
  let conJarvis = 0, scaduta = false;
  for (const a of nuovi) {
    let ok = false;
    if (daJarvis) {
      try {
        await spedisci(sub, { id: a.id, livello: a.livello, titolo: a.titolo, testo: a.testo }, { chiave, pubblica });
        ok = true; conJarvis++;
      } catch (e) {
        if (e.statusCode === 404 || e.statusCode === 410) {
          scaduta = true; daJarvis = false;
          console.log('[notifiche] l\'iPhone ha chiuso l\'iscrizione alle notifiche di Jarvis: passo a ntfy.');
        } else {
          console.log(`[notifiche] notifica di Jarvis non inviata (${e.statusCode || e.message}): uso ntfy.`);
        }
      }
    }
    if (!ok && argomento) ok = await ntfy(invia, argomento, a);
    if (ok) fatti.push(a.id);
  }
  /* iscrizione chiusa: la si segna per non riprovarla a ogni giro e lo si dice una volta sola */
  if (scaduta) {
    reg.push_scaduta = impronta(sub);
    if (argomento) await ntfy(invia, argomento, RIATTIVA);
  }
  if (fatti.length || scaduta) {
    reg.inviati = [...(reg.inviati || []), ...fatti].slice(-500);
    reg.aggiornato = new Date(adesso).toISOString();
    fs.writeFileSync(registro, JSON.stringify(reg));
  }
  console.log(`[notifiche] inviate ${fatti.length} su ${nuovi.length} nuove ` +
              `(${conJarvis} da Jarvis, ${fatti.length - conJarvis} con ntfy).`);
  return { inviati: fatti, nuovi, daJarvis: conJarvis };
}

if (require.main === module) {
  // le notifiche non devono mai far fallire il giro: i dati vanno salvati comunque
  main().catch(e => console.log('[notifiche] fallito:', e.message));
}
module.exports = { avvisiDellApp, main, MASSIMO, opzioniPush, chiavePubblica, leggiIscrizione };
