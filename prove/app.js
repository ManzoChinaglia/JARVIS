// Prova dell'app: script estratto da index.html, finto DOM, fetch che legge
// da disco, orologio finto. Uso: node prove/app.js
process.env.TZ = 'Europe/Rome';   // la scadenza dipende dall'ora legale italiana
const fs = require('fs'), path = require('path'), vm = require('vm');
const REPO = process.argv[2] || path.join(__dirname, '..');
const html = fs.readFileSync(path.join(REPO, 'index.html'), 'utf8');
const codice = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].pop()[1];

let esiti = 0, falliti = 0;
function verifica(nome, cond, dettaglio) {
  esiti++;
  if (!cond) falliti++;
  console.log((cond ? '  ok   ' : '  NO   ') + nome + (dettaglio !== undefined ? '  →  ' + dettaglio : ''));
}

async function avvia({ adesso, senzaOrari = false }) {
  const RealDate = Date;
  const fisso = new RealDate(adesso).getTime();
  class FintaData extends RealDate {
    constructor(...a) { a.length ? super(...a) : super(fisso); }
    static now() { return fisso; }
  }
  const el = {};
  const nodo = id => el[id] || (el[id] = {
    id, textContent: '', innerHTML: '', value: '', style: {}, dataset: {},
    classList: { _s: new Set(), add(c) { this._s.add(c); }, remove(c) { this._s.delete(c); },
                 toggle(c, v) { (v === undefined ? !this._s.has(c) : v) ? this._s.add(c) : this._s.delete(c); },
                 contains(c) { return this._s.has(c); } },
    addEventListener() {}, click() {}
  });
  const ctx = {
    Date: FintaData, console, URLSearchParams, Promise, Object, String, Math, Set, JSON,
    setInterval() {}, location: { search: '' },
    document: { getElementById: nodo, querySelector: () => nodo('_q'), querySelectorAll: () => [] },
    fetch: async url => {
      const f = url.split('?')[0];
      if (senzaOrari && f.endsWith('orari.json')) return { ok: false, status: 404 };
      const p = path.join(REPO, f);
      if (!fs.existsSync(p)) return { ok: false, status: 404 };
      const testo = fs.readFileSync(p, 'utf8');
      return { ok: true, status: 200, json: async () => JSON.parse(testo) };
    }
  };
  ctx.window = ctx;
  vm.createContext(ctx);
  vm.runInContext(codice + '\n;globalThis.__t={get D(){return D},get mia(){return mia},prossima,scadenza,orario,undici,rispondi,quando};', ctx);
  await new Promise(r => setTimeout(r, 50));
  if (el['cd'] === undefined) throw new Error('avvio fallito: ' + (el['_q'] || {}).innerHTML);
  return { t: ctx.__t, el };
}

(async () => {
  // Giornata 5 di Serie A: primo anticipo Monza-Sassuolo, ven 18/9 18:45 UTC = 20:45 in Italia
  console.log('\n1. Domenica 13 settembre, mezzogiorno');
  let { t, el } = await avvia({ adesso: '2026-09-13T12:00:00+02:00' });
  let g = t.prossima();
  verifica('giornata di lega 1 (Serie A 5)', g[0] === 1 && g[1] === 5, 'G' + g[0] + ' / SA ' + g[1]);
  verifica('scadenza ven 18 set 20:30 ora italiana', t.scadenza(g).toISOString() === '2026-09-18T18:30:00.000Z', t.quando(t.scadenza(g)));
  verifica('conto alla rovescia', el.cdt.textContent === '5 giorni 8h', el.cdt.textContent);
  verifica('dettaglio sotto il conto', el.cdq.textContent.includes('Monza-Sassuolo'), el.cdq.textContent);
  verifica('etichetta', el.cdk.textContent === 'Schieri la formazione entro', el.cdk.textContent);
  verifica('non urgente a 5 giorni', !el.cd.classList.contains('urgente'));
  const u = t.undici(g), n = u.P.length + u.D.length + u.C.length + u.A.length;
  verifica('undici completo, difesa a 4', n === 11 && u.D.length === 4, n + ' giocatori, ' + u.D.length + ' difensori');
  verifica('risposta "chi affronto"', /Schieri entro ven 18 set/.test(t.rispondi('chi affronto')), t.rispondi('chi affronto').replace(/\n/g, ' / '));
  verifica('date dei dati leggibili in intestazione', !/Invalid/.test(el.stamp.textContent), el.stamp.textContent);

  console.log('\n2. Venerdì 18 settembre, 20:00 (mezz\'ora alla scadenza)');
  ({ t, el } = await avvia({ adesso: '2026-09-18T20:00:00+02:00' }));
  verifica('conto alla rovescia', el.cdt.textContent === '0h 30m', el.cdt.textContent);
  verifica('urgente', el.cd.classList.contains('urgente'));

  console.log('\n3. Venerdì 18 settembre, 20:31 (scaduta, giornata in corso)');
  ({ t, el } = await avvia({ adesso: '2026-09-18T20:31:00+02:00' }));
  g = t.prossima();
  verifica('resta la giornata 1', g[0] === 1, 'G' + g[0]);
  verifica('etichetta "Formazione chiusa"', el.cdk.textContent === 'Formazione chiusa', el.cdk.textContent);
  verifica('testo "scaduta"', el.cdt.textContent === 'scaduta', el.cdt.textContent);
  verifica('risposta a scadenza passata', /Formazione chiusa alle/.test(t.rispondi('chi affronto')), t.rispondi('chi affronto').replace(/\n/g, ' / '));

  // ultima partita della SA 5: Milan-Lecce dom 20/9 18:45 UTC; la giornata cambia 2 ore dopo
  console.log('\n4. Cambio di giornata attorno all\'ultima partita');
  ({ t } = await avvia({ adesso: '2026-09-20T22:40:00+02:00' }));
  verifica('alle 22:40 di domenica è ancora la giornata 1', t.prossima()[0] === 1, 'G' + t.prossima()[0]);
  ({ t, el } = await avvia({ adesso: '2026-09-20T22:50:00+02:00' }));
  g = t.prossima();
  verifica('alle 22:50 passa alla giornata 2 (Serie A 6)', g[0] === 2 && g[1] === 6, 'G' + g[0] + ' / SA ' + g[1]);
  verifica('scadenza G2 sab 10 ott 14:45', t.scadenza(g).toISOString() === '2026-10-10T12:45:00.000Z', t.quando(t.scadenza(g)));

  // SA 9 infrasettimanale, dopo il ritorno all'ora solare (25 ottobre)
  console.log('\n5. Turno infrasettimanale dopo il cambio d\'ora');
  ({ t } = await avvia({ adesso: '2026-10-26T09:00:00+01:00' }));
  g = t.prossima();
  verifica('giornata di lega 5 (Serie A 9)', g[0] === 5 && g[1] === 9, 'G' + g[0] + ' / SA ' + g[1]);
  verifica('scadenza mar 27 ott 18:15 (ora solare)', t.scadenza(g).toISOString() === '2026-10-27T17:15:00.000Z', t.quando(t.scadenza(g)));

  console.log('\n6. Giornata senza orari ufficiali (Serie A 13)');
  const g13 = (await avvia({ adesso: '2026-09-13T12:00:00+02:00' })).t.D.g.find(x => x[1] === 13);
  ({ t, el } = await avvia({ adesso: new Date(g13[2] + 'T09:00:00+01:00').getTime() - 5 * 86400000 }));
  g = t.prossima();
  verifica('è la giornata con la Serie A 13', g[1] === 13, 'G' + g[0] + ' / SA ' + g[1]);
  verifica('nessuna scadenza inventata', t.scadenza(g) === null);
  verifica('messaggio', el.cdt.textContent === 'orario non ancora ufficiale', el.cdt.textContent);
  verifica('non urgente', !el.cd.classList.contains('urgente'));
  verifica('risposta "chi affronto"', /non è ancora ufficiale/.test(t.rispondi('chi affronto')), t.rispondi('chi affronto').replace(/\n/g, ' / '));

  console.log('\n7. orari.json assente');
  ({ t, el } = await avvia({ adesso: '2026-09-13T12:00:00+02:00', senzaOrari: true }));
  verifica('l\'app parte comunque', !!t.D && t.mia.length === 25, t.mia.length + ' giocatori in rosa');
  verifica('lo dice invece di stimare', el.cdt.textContent === 'orari non disponibili', el.cdt.textContent);
  verifica('giornata dal calendario', t.prossima()[0] === 1, 'G' + t.prossima()[0]);

  console.log('\n' + (esiti - falliti) + '/' + esiti + ' verifiche superate');
  process.exit(falliti ? 1 : 0);
})().catch(e => { console.error('ERRORE', e); process.exit(2); });
