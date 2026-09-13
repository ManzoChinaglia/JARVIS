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
const circa = (a, b) => Math.abs(a - b) < 1e-9;

// dati: file di dati/ da sostituire con un oggetto finto, o con null per "assente"
async function avvia({ adesso, senzaOrari = false, dati = {} }) {
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
    setInterval() {}, location: { search: '', host: 'manzochinaglia.github.io', pathname: '/JARVIS/' },
    document: { getElementById: nodo, querySelector: () => nodo('_q'), querySelectorAll: () => [] },
    fetch: async url => {
      const f = url.split('?')[0], nome = f.replace(/^dati\//, '');
      if (senzaOrari && nome === 'orari.json') return { ok: false, status: 404 };
      if (nome in dati) {
        const v = dati[nome];
        return v === null ? { ok: false, status: 404 }
                          : { ok: true, status: 200, json: async () => JSON.parse(JSON.stringify(v)) };
      }
      const p = path.join(REPO, f);
      if (!fs.existsSync(p)) return { ok: false, status: 404 };
      const testo = fs.readFileSync(p, 'utf8');
      return { ok: true, status: 200, json: async () => JSON.parse(testo) };
    }
  };
  ctx.window = ctx;
  vm.createContext(ctx);
  vm.runInContext(codice + '\n;globalThis.__t={get D(){return D},get mia(){return mia},get PESI(){return PESI},' +
    'prossima,scadenza,orario,undici,rispondi,quando,titolarita,forza,punteggio,avversarioClub};', ctx);
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
  verifica('link per iscriversi al calendario', el.ics.href === 'webcal://manzochinaglia.github.io/JARVIS/dati/jarvis.ics', el.ics.href);

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

  // da qui dati finti: i risultati non devono dipendere dal giorno in cui si prova
  const base = JSON.parse(fs.readFileSync(path.join(REPO, 'dati', 'base.json'), 'utf8'));
  const clubs = [...new Set(base.p.map(a => a[2]))];
  const [d1, d2, d3] = base.p.filter(a => a[4] === base.me && a[3] === 'D').map(a => a[0]);
  const P = id => t.mia.find(p => p.id === id);
  const prob5 = { aggiornato: '2026-09-17T09:30:00+00:00', giornata: 5, squadre: clubs,
                  titolari: { [d1]: 95 }, panchina: { [d2]: 40 } };
  const giovedi = '2026-09-17T12:00:00+02:00';

  console.log('\n8. Probabili della giornata giusta');
  ({ t, el } = await avvia({ adesso: giovedi, dati: { 'titolari.json': prob5, 'squadre.json': null, 'infortuni.json': null } }));
  g = t.prossima();
  let x = t.titolarita(P(d1), g);
  verifica('titolare al 95%', x && x.stato === 't' && x.perc === 95, JSON.stringify(x));
  x = t.titolarita(P(d2), g);
  verifica('in panchina', x && x.stato === 'c', JSON.stringify(x));
  x = t.titolarita(P(d3), g);
  verifica('squadra pubblicata, giocatore assente: 0%', x && x.stato === 'r' && x.perc === 0, JSON.stringify(x));
  verifica('titolare al 95% vale +1,12', circa(t.punteggio(P(d1), g) - P(d1).fm, 1.12), (t.punteggio(P(d1), g) - P(d1).fm).toFixed(2));
  verifica('fuori dalle probabili vale −0,40', circa(t.punteggio(P(d3), g) - P(d3).fm, -0.4), (t.punteggio(P(d3), g) - P(d3).fm).toFixed(2));
  verifica('la rosa mostra la percentuale', el.rosa.innerHTML.includes('titolare 95%'));
  verifica('intestazione', /probabili del/.test(el.stamp.textContent), el.stamp.textContent);
  verifica('risposta su un giocatore', /Titolare al 95%/.test(t.rispondi('come sta ' + P(d1).nome)), t.rispondi('come sta ' + P(d1).nome).replace(/\n/g, ' / '));

  console.log('\n9. Probabili di un\'altra giornata, o nel vecchio formato');
  for (const [nome, file] of [['giornata 4', { ...prob5, giornata: 4 }],
                              ['vecchio formato', { aggiornato: '2026-09-13T00:00:00+00:00', stato: { [d1]: 't' } }]]) {
    ({ t, el } = await avvia({ adesso: giovedi, dati: { 'titolari.json': file, 'squadre.json': null } }));
    g = t.prossima();
    verifica(nome + ': nessuna titolarità inventata', t.mia.every(p => t.titolarita(p, g) === null));
    verifica(nome + ': punteggio = fantamedia', t.mia.every(p => t.punteggio(p, g) === p.fm));
    verifica(nome + ': intestazione', /probabili non ancora uscite/.test(el.stamp.textContent), el.stamp.textContent);
  }

  console.log('\n10. Forza dell\'avversario');
  // tutte le squadre nella media: 1 gol fatto e 1 subito a partita, in entrambi gli anni
  const squadre = {};
  clubs.forEach(c => squadre[c] = { attuale: { casa: [2, 2, 2, 1], fuori: [2, 2, 2, 1] },
                                    precedente: { casa: [19, 19, 19, 5], fuori: [19, 19, 19, 5] } });
  const sq = { aggiornato: '2026-09-17T09:30:00+00:00', squadre,
               campionato_precedente: { casa: [190, 190, 190, 50], fuori: [190, 190, 190, 50] } };
  const senzaTit = { 'titolari.json': null, 'infortuni.json': null, 'squadre.json': sq };
  ({ t, el } = await avvia({ adesso: giovedi, dati: senzaTit }));
  g = t.prossima();
  const att = t.mia.find(p => p.ruolo === 'A');
  const avvD = t.avversarioClub(P(d1).club, g[1]), avvA = t.avversarioClub(att.club, g[1]);
  verifica('avversario nella media: nessun effetto', circa(t.forza(P(d1), g).delta, 0) && t.punteggio(P(d1), g) === P(d1).fm);
  // avversario che segna tanto e non subisce: 4 partite quest'anno, quindi 40% quest'anno e 60% l'anno scorso
  const forte = { attuale: { casa: [2, 6, 0, 2], fuori: [2, 6, 0, 2] },
                  precedente: { casa: [19, 38, 19, 5], fuori: [19, 38, 19, 5] }, modulo: '4-3-3' };
  squadre[avvD.avv] = forte; squadre[avvA.avv] = forte;
  ({ t, el } = await avvia({ adesso: giovedi, dati: senzaTit }));
  let f = t.forza(P(d1), g);
  verifica('difensore: l\'avversario segna 0,4·3 + 0,6·2 = 2,4', circa(f.val, 2.4), f.val);
  verifica('difensore: 0,8 · (1 − 2,4) = −1,12', circa(t.punteggio(P(d1), g) - P(d1).fm, -1.12), (t.punteggio(P(d1), g) - P(d1).fm).toFixed(2));
  verifica('campo dell\'avversario', f.campo === (avvD.casa ? 'fuori' : 'casa'), f.campo + (avvD.casa ? ' (noi in casa)' : ' (noi fuori)'));
  f = t.forza(att, g);
  verifica('attaccante: l\'avversario subisce 0,4·0 + 0,6·1 = 0,6', circa(f.val, 0.6), f.val);
  verifica('attaccante: 0,8 · (0,6 − 1) = −0,32', circa(t.punteggio(att, g) - att.fm, -0.32), (t.punteggio(att, g) - att.fm).toFixed(2));
  verifica('motivo leggibile nella rosa', el.rosa.innerHTML.includes(avvD.avv + ' (4-3-3) segna 2,4 gol a partita'), avvD.avv);
  verifica('domanda sui difensori', /in ordine di consiglio/.test(t.rispondi('chi schiero in difesa')), t.rispondi('chi schiero in difesa').split('\n')[0]);
  squadre[avvD.avv] = { ...forte, attuale: { casa: [5, 15, 0, 5], fuori: [5, 15, 0, 5] } };
  ({ t } = await avvia({ adesso: giovedi, dati: senzaTit }));
  verifica('dalla decima partita conta solo quest\'anno', circa(t.forza(P(d1), g).val, 3), t.forza(P(d1), g).val);
  squadre[avvD.avv] = { ...forte, neopromossa: true };
  ({ t, el } = await avvia({ adesso: giovedi, dati: senzaTit }));
  verifica('neopromossa segnalata come stima', el.rosa.innerHTML.includes('neopromossa, stima'));

  console.log('\n11. Senza squadre.json');
  ({ t } = await avvia({ adesso: giovedi, dati: { 'titolari.json': null, 'squadre.json': null } }));
  g = t.prossima();
  verifica('nessuna forza inventata', t.mia.every(p => t.forza(p, g) === null));
  verifica('undici completo lo stesso', Object.values(t.undici(g)).flat().length === 11);

  console.log('\n12. Font ospitato nel repository');
  verifica('nessuna richiesta a Google Fonts', !/fonts\.(googleapis|gstatic)\.com/.test(html));
  const fonti = [...html.matchAll(/url\("(font\/[^"]+\.woff2)"\)/g)].map(m => m[1]);
  verifica('tre spessori dichiarati', fonti.length === 3, fonti.join(', '));
  verifica('i file esistono e sono woff2', fonti.every(f => fs.existsSync(path.join(REPO, f)) &&
           fs.readFileSync(path.join(REPO, f)).subarray(0, 4).toString() === 'wOF2'));
  verifica('licenza inclusa', fs.existsSync(path.join(REPO, 'font', 'OFL.txt')));

  console.log('\n' + (esiti - falliti) + '/' + esiti + ' verifiche superate');
  process.exit(falliti ? 1 : 0);
})().catch(e => { console.error('ERRORE', e); process.exit(2); });
