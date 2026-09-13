// Manda sull'iPhone, tramite ntfy, gli stessi avvisi della scheda «Avvisi».
//
// Gira nel workflow dopo lo script dei dati: esegue il codice dell'app (come le
// prove) sui dati appena scaricati e invia solo gli avvisi mai inviati prima,
// segnati in dati/notifiche.json (solo i codici degli avvisi, niente di segreto).
// L'argomento ntfy è segreto: arriva dalla variabile NTFY_ARGOMENTO, cioè dai
// Secrets di GitHub, e non compare mai nel codice. Senza argomento non invia e
// non segna niente, così appena viene impostato arriva tutto.
//
// Uso: node scripts/notifiche.js
'use strict';
const fs = require('fs'), path = require('path'), vm = require('vm');

const REPO = path.join(__dirname, '..');
const REGISTRO = path.join(REPO, 'dati', 'notifiche.json');
const APP = 'https://manzochinaglia.github.io/JARVIS/';
const MASSIMO = 6;                                      // mai più di sei notifiche per giro
const PRIORITA = { urgente: 4, attenzione: 3, info: 2 };  // scala di ntfy: 1 minima, 5 massima
const ETICHETTE = { urgente: ['rotating_light'], attenzione: ['warning'], info: ['soccer'] };

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

async function main({ argomento = process.env.NTFY_ARGOMENTO, invia = fetch, adesso = Date.now(),
                      registro = REGISTRO, repo = REPO, dati = {} } = {}) {
  const lista = await avvisiDellApp({ repo, adesso, dati });
  const reg = leggiRegistro(registro), gia = new Set(reg.inviati || []);
  const nuovi = lista.filter(a => !gia.has(a.id)).slice(0, MASSIMO);
  if (!argomento) {
    console.log(`[notifiche] NTFY_ARGOMENTO non impostato: ${nuovi.length} avvisi nuovi non inviati.`);
    return { inviati: [], nuovi };
  }
  const fatti = [];
  for (const a of nuovi) {
    try {
      const r = await invia('https://ntfy.sh/', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: argomento, title: a.titolo, message: a.testo,
                               priority: PRIORITA[a.livello], tags: ETICHETTE[a.livello], click: APP })
      });
      if (r.ok) fatti.push(a.id); else console.log(`[notifiche] ntfy ha risposto ${r.status}: riprovo al prossimo giro.`);
    } catch (e) {
      console.log(`[notifiche] invio fallito (${e.message}): riprovo al prossimo giro.`);
    }
  }
  if (fatti.length) {
    reg.inviati = [...(reg.inviati || []), ...fatti].slice(-500);
    reg.aggiornato = new Date(adesso).toISOString();
    fs.writeFileSync(registro, JSON.stringify(reg));
  }
  console.log(`[notifiche] inviate ${fatti.length} su ${nuovi.length} nuove.`);
  return { inviati: fatti, nuovi };
}

if (require.main === module) {
  // le notifiche non devono mai far fallire il giro: i dati vanno salvati comunque
  main().catch(e => console.log('[notifiche] fallito:', e.message));
}
module.exports = { avvisiDellApp, main, MASSIMO };
