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
// avversario della giornata 1 preso dai dati: i nomi delle squadre possono cambiare
const BASE0 = JSON.parse(fs.readFileSync(path.join(REPO, 'dati', 'base.json'), 'utf8'));
const AVV1 = BASE0.g[0][3].map(([a, b]) => a === BASE0.me ? b : b === BASE0.me ? a : null).find(Boolean);

// dati: file di dati/ da sostituire con un oggetto finto, o con null per "assente"
// orari.json e infortuni.json veri vengono "aggiornati" al giorno simulato, così
// l'avviso dei dati vecchi non dipende dal giorno in cui si lanciano le prove
// memoria: il localStorage finto, da passare uguale per simulare la riapertura dell'app
async function avvia({ adesso, senzaOrari = false, dati = {}, search = '', sr, memoria = {}, nav }) {
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
    addEventListener() {}, click() {}, focus() {}, blur() {}
  });
  const ctx = {
    Date: FintaData, console, URLSearchParams, Promise, Object, String, Math, Set, JSON,
    setInterval() {}, setTimeout: () => 0, clearTimeout() {}, webkitSpeechRecognition: sr,
    localStorage: { getItem: k => (k in memoria ? memoria[k] : null), setItem: (k, v) => { memoria[k] = String(v); } },
    location: { search, host: 'manzochinaglia.github.io', pathname: '/JARVIS/' },
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
      if (nome === 'orari.json' || nome === 'infortuni.json') {
        const o = JSON.parse(testo);
        o.aggiornato = new RealDate(fisso).toISOString();
        return { ok: true, status: 200, json: async () => o };
      }
      return { ok: true, status: 200, json: async () => JSON.parse(testo) };
    }
  };
  if (nav) ctx.navigator = nav;          // un iPhone finto, per il numero sull'icona
  Object.assign(ctx, { Blob, Response, DecompressionStream, TextDecoder });   // per leggere i file Excel
  ctx.window = ctx;
  vm.createContext(ctx);
  vm.runInContext(codice + '\n;globalThis.__t={get D(){return D},get mia(){return mia},get PESI(){return PESI},' +
    'get players(){return players},get STIME(){return STIME},avvisi,apriAvvisi,renderGiornata,' +
    'prossima,scadenza,orario,undici,rispondi,quando,titolarita,forza,punteggio,avversarioClub,fmStimata,disponibile,panchina,' +
    'apriGiocatore,chiudiFogli,posizione,MAGLIE,undiciDi,sfidaDati,stemma,coloreSquadra,oraPartita,comeAndata,apriComeAndata,apriMercato,chiudiSovra,stagione,apriStagione,scegliGiornata,prossimi3,mercato,leggiXlsx,classificaDaRighe,importaClassifica,forma,risultatoLega,get ME(){return ME}};', ctx);
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
  const cognomeDi = p => p.nome.replace(/\s+\S{1,3}\.$/, '');
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
  verifica('titolare al 95% vale +1,12', circa(t.punteggio(P(d1), g) - t.fmStimata(P(d1)), 1.12), (t.punteggio(P(d1), g) - t.fmStimata(P(d1))).toFixed(2));
  verifica('fuori dalle probabili vale −0,40', circa(t.punteggio(P(d3), g) - t.fmStimata(P(d3)), -0.4), (t.punteggio(P(d3), g) - t.fmStimata(P(d3))).toFixed(2));
  verifica('la rosa mostra la percentuale', el.rosa.innerHTML.includes('titolare 95%'));
  verifica('intestazione', /probabili del/.test(el.stamp.textContent), el.stamp.textContent);
  verifica('risposta su un giocatore', /Titolare al 95%/.test(t.rispondi('come sta ' + P(d1).nome)), t.rispondi('come sta ' + P(d1).nome).replace(/\n/g, ' / '));

  console.log('\n9. Probabili di un\'altra giornata, o nel vecchio formato');
  for (const [nome, file] of [['giornata 4', { ...prob5, giornata: 4 }],
                              ['vecchio formato', { aggiornato: '2026-09-13T00:00:00+00:00', stato: { [d1]: 't' } }]]) {
    ({ t, el } = await avvia({ adesso: giovedi, dati: { 'titolari.json': file, 'squadre.json': null } }));
    g = t.prossima();
    verifica(nome + ': nessuna titolarità inventata', t.mia.every(p => t.titolarita(p, g) === null));
    verifica(nome + ': punteggio = fantamedia stimata', t.mia.every(p => t.punteggio(p, g) === t.fmStimata(p)));
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
  // senza probabili la titolarità si stima dalle presenze: la si toglie per isolare l'avversario
  const tit = p => { const y = t.titolarita(p, g); return y ? -0.4 + 1.6 * y.perc / 100 : 0; };
  const base1 = p => t.fmStimata(p) + tit(p);
  verifica('avversario nella media: nessun effetto', circa(t.forza(P(d1), g).delta, 0) && circa(t.punteggio(P(d1), g), base1(P(d1))));
  // avversario che segna tanto e non subisce: 4 partite quest'anno, quindi 40% quest'anno e 60% l'anno scorso
  const forte = { attuale: { casa: [2, 6, 0, 2], fuori: [2, 6, 0, 2] },
                  precedente: { casa: [19, 38, 19, 5], fuori: [19, 38, 19, 5] }, modulo: '4-3-3' };
  squadre[avvD.avv] = forte; squadre[avvA.avv] = forte;
  ({ t, el } = await avvia({ adesso: giovedi, dati: senzaTit }));
  let f = t.forza(P(d1), g);
  verifica('difensore: l\'avversario segna 0,4·3 + 0,6·2 = 2,4', circa(f.val, 2.4), f.val);
  verifica('difensore: 0,8 · (1 − 2,4) = −1,12', circa(t.punteggio(P(d1), g) - base1(P(d1)), -1.12), (t.punteggio(P(d1), g) - base1(P(d1))).toFixed(2));
  verifica('campo dell\'avversario', f.campo === (avvD.casa ? 'fuori' : 'casa'), f.campo + (avvD.casa ? ' (noi in casa)' : ' (noi fuori)'));
  f = t.forza(att, g);
  verifica('attaccante: l\'avversario subisce 0,4·0 + 0,6·1 = 0,6', circa(f.val, 0.6), f.val);
  verifica('attaccante: 0,8 · (0,6 − 1) = −0,32', circa(t.punteggio(att, g) - base1(att), -0.32), (t.punteggio(att, g) - base1(att)).toFixed(2));
  verifica('motivo leggibile nella rosa', el.rosa.innerHTML.includes(avvD.avv + ' (4-3-3) segna 2,4 gol a partita'), avvD.avv);
  verifica('domanda sui difensori', /^In difesa/.test(t.rispondi('chi schiero in difesa')), t.rispondi('chi schiero in difesa').split('\n')[0]);
  squadre[avvD.avv] = { ...forte, attuale: { casa: [5, 15, 0, 5], fuori: [5, 15, 0, 5] } };
  ({ t } = await avvia({ adesso: giovedi, dati: senzaTit }));
  verifica('dalla decima partita conta solo quest\'anno', circa(t.forza(P(d1), g).val, 3), t.forza(P(d1), g).val);
  squadre[avvD.avv] = { ...forte, neopromossa: true };
  ({ t, el } = await avvia({ adesso: giovedi, dati: senzaTit }));
  verifica('neopromossa segnalata come stima', el.rosa.innerHTML.includes('neopromossa, stima'));

  console.log('\n10bis. Presenze finché non escono le probabili');
  const uniformi = {};
  clubs.forEach(c => uniformi[c] = { attuale: { casa: [2, 2, 2, 1], fuori: [2, 2, 2, 1] },
                                     precedente: { casa: [19, 19, 19, 5], fuori: [19, 19, 19, 5] } });
  const sq2 = { ...sq, squadre: uniformi };
  ({ t, el } = await avvia({ adesso: giovedi, dati: { 'titolari.json': null, 'infortuni.json': null, 'squadre.json': sq2 } }));
  g = t.prossima();
  const reg = t.mia.find(p => p.pgv === 3), zero = t.mia.find(p => p.pgv === 0 && p.ruolo !== 'P');
  x = t.titolarita(reg, g);
  verifica('3 partite su 4: presenze al 75%', x && x.stato === 's' && x.perc === 75, JSON.stringify(x));
  verifica('vale come titolarità al 75%: +0,80', circa(t.punteggio(reg, g) - t.fmStimata(reg), 0.8), (t.punteggio(reg, g) - t.fmStimata(reg)).toFixed(2));
  if (zero) {
    x = t.titolarita(zero, g);
    verifica('0 partite su 4: pesa come fuori dalle probabili', x && x.perc === 0 && circa(t.punteggio(zero, g) - t.fmStimata(zero), -0.4),
             zero.nome + ' ' + JSON.stringify(x));
    verifica('ed è tra le cose da tenere d\'occhio se entra', !Object.values(t.undici(g)).flat().includes(zero) ||
             t.rispondi('chi schiero').includes(zero.nome + ': ha giocato 0 partite su 4'));
  }
  verifica('la rosa mostra le presenze', el.rosa.innerHTML.includes('presenze 3/4'));
  ({ t } = await avvia({ adesso: giovedi, dati: { 'titolari.json': prob5, 'infortuni.json': null, 'squadre.json': sq2 } }));
  verifica('uscite le probabili, contano solo quelle', t.mia.every(p => t.titolarita(p, g).stato !== 's'));
  ({ t } = await avvia({ adesso: giovedi, dati: { 'titolari.json': { ...prob5, squadre: [] }, 'infortuni.json': null, 'squadre.json': sq2 } }));
  verifica('squadra non ancora pubblicata: si resta sulle presenze', t.mia.every(p => t.titolarita(p, g).stato === 's'));

  console.log('\n11. Senza squadre.json');
  ({ t } = await avvia({ adesso: giovedi, dati: { 'titolari.json': null, 'squadre.json': null } }));
  g = t.prossima();
  verifica('nessuna forza inventata', t.mia.every(p => t.forza(p, g) === null));
  verifica('undici completo lo stesso', Object.values(t.undici(g)).flat().length === 11);

  console.log('\n11bis. Fantamedia stimata con poche partite');
  // sui dati di base.json: le statistiche del giorno si provano a parte (11quinquies)
  ({ t } = await avvia({ adesso: giovedi, dati: { 'titolari.json': null, 'squadre.json': null, 'statistiche.json': null } }));
  // retta fantamedia ~ quotazione per ruolo, pesata per partite: ricalcolata qui da zero
  const retta = r => {
    const gg = base.p.filter(a => a[3] === r && a[7] > 0), W = gg.reduce((s, a) => s + a[7], 0);
    const mq = gg.reduce((s, a) => s + a[7] * a[6], 0) / W, mf = gg.reduce((s, a) => s + a[7] * a[9], 0) / W;
    const b = Math.max(0, gg.reduce((s, a) => s + a[7] * (a[6] - mq) * (a[9] - mf), 0) /
                          gg.reduce((s, a) => s + a[7] * (a[6] - mq) ** 2, 0));
    return { a: mf - b * mq, b };
  };
  const R = { P: retta('P'), D: retta('D'), C: retta('C'), A: retta('A') };
  const attesa = a => (a[7] * a[9] + 5 * (R[a[3]].a + R[a[3]].b * a[6])) / (a[7] + 5);
  verifica('stessa stima calcolata da zero, per tutti i giocatori delle rose',
           base.p.every(a => circa(t.fmStimata(t.players.find(p => p.id === a[0])), attesa(a))), base.p.length + ' giocatori');
  const mai = t.players.filter(p => p.pgv === 0);
  verifica('chi non ha ancora giocato non vale 0', mai.every(p => t.fmStimata(p) > 3),
           mai.slice(0, 3).map(p => p.nome + ' ' + t.fmStimata(p).toFixed(2)).join(', '));
  verifica('pendenza della quotazione mai negativa', Object.values(t.STIME).every(s => s && s.b >= 0));
  const alto = t.mia.filter(p => p.pgv <= 1 && p.ruolo === 'A').sort((a, b) => b.quot - a.quot);
  if (alto.length > 1) verifica('a parità di partite conta la quotazione', t.fmStimata(alto[0]) > t.fmStimata(alto[alto.length - 1]) ||
                                alto[0].fm < alto[alto.length - 1].fm, alto.map(p => p.nome + ' q' + p.quot + ' ' + t.fmStimata(p).toFixed(2)).join(', '));
  const nuovo = t.mia.find(p => p.pgv === 0 && p.ruolo !== 'P');
  if (nuovo) verifica('la scheda mostra la stima usata', /per il consiglio/.test(t.rispondi('come sta ' + cognomeDi(nuovo))),
                      t.rispondi('come sta ' + cognomeDi(nuovo)).split('\n')[1]);

  console.log('\n11ter. Squalificati e dati vecchi');
  const indisp5 = { aggiornato: '2026-09-15T09:00:00+00:00', giornata: 5, squadre: [], titolari: {}, panchina: {},
                    indisponibili: { [d1]: { motivo: 'Squalificato' }, [d2]: { motivo: 'Infortunato', fino: '28/10' } } };
  ({ t, el } = await avvia({ adesso: giovedi, dati: { 'titolari.json': indisp5, 'squadre.json': null, 'infortuni.json': null } }));
  g = t.prossima();
  verifica('lo squalificato non è disponibile e non entra nell\'undici', !t.disponibile(P(d1), g[2])
           && !Object.values(t.undici(g)).flat().includes(P(d1)));
  verifica('motivo nella rosa', el.rosa.innerHTML.includes('Squalificato, salta questa giornata'));
  verifica('infortunato dalla pagina di giornata, con la data', el.rosa.innerHTML.includes('Infortunato fino al 28/10'));
  verifica('«chi è infortunato?» li elenca', /Squalificato/.test(t.rispondi('chi è infortunato')) && /28\/10/.test(t.rispondi('chi è infortunato')));
  verifica('solo indisponibili: le probabili risultano non uscite', /probabili non ancora uscite/.test(el.stamp.textContent), el.stamp.textContent);
  ({ t } = await avvia({ adesso: giovedi, dati: { 'titolari.json': { ...indisp5, giornata: 4 }, 'squadre.json': null, 'infortuni.json': null } }));
  g = t.prossima();
  verifica('squalifica di un\'altra giornata: disponibile', t.disponibile(P(d1), g[2]));
  const orariVeri = JSON.parse(fs.readFileSync(path.join(REPO, 'dati', 'orari.json'), 'utf8'));
  ({ el } = await avvia({ adesso: '2026-09-20T12:00:00+02:00', dati: { 'orari.json': { ...orariVeri, aggiornato: '2026-09-13T08:00:00+00:00' } } }));
  verifica('script fermo da 7 giorni: avviso in rosso', /dati fermi da 7 giorni/.test(el.stamp.textContent)
           && el.stamp.classList.contains('vecchio'), el.stamp.textContent);
  ({ el } = await avvia({ adesso: '2026-09-20T12:00:00+02:00', dati: {
          'orari.json': { ...orariVeri, aggiornato: '2026-09-19T08:00:00+00:00' },
          'infortuni.json': { aggiornato: '2026-09-13T08:00:00+00:00', voci: {} } } }));
  verifica('infortuni fermi da 7 giorni', /infortuni fermi da 7 giorni/.test(el.stamp.textContent), el.stamp.textContent);
  ({ el } = await avvia({ adesso: '2026-09-20T12:00:00+02:00' }));
  verifica('dati freschi: nessun avviso', !el.stamp.classList.contains('vecchio'), el.stamp.textContent);

  console.log('\n11quater. Ordine della panchina');
  ({ t, el } = await avvia({ adesso: giovedi, dati: { 'titolari.json': indisp5, 'squadre.json': null, 'infortuni.json': null } }));
  g = t.prossima();
  const banco = t.panchina(g), ordine = r => 'PDCA'.indexOf(r);
  verifica('per ruolo e, dentro il ruolo, dal punteggio più alto', banco.every((p, i) => i === 0
           || ordine(banco[i - 1].ruolo) < ordine(p.ruolo)
           || (banco[i - 1].ruolo === p.ruolo && t.punteggio(banco[i - 1], g) >= t.punteggio(p, g))), banco.map(p => p.ruolo + ' ' + p.nome).join(', '));
  const koN = t.mia.filter(p => !t.disponibile(p, g[2])).length;
  verifica('tutti gli altri disponibili, nessun indisponibile', banco.length === 25 - 11 - koN && banco.every(p => t.disponibile(p, g[2])),
           banco.length + ' in panchina, ' + koN + ' fuori');
  verifica('numerata per ruolo', /<small>1°<\/small>/.test(el.panchina.innerHTML) && /<small>2°<\/small>/.test(el.panchina.innerHTML));
  verifica('«chi schiero?» dice anche la panchina', /\nPanchina, in ordine: P /.test(t.rispondi('chi schiero')),
           t.rispondi('chi schiero').split('\n').find(r => r.startsWith('Panchina')));

  console.log('\n11quinquies. Statistiche del giorno dalle pagine pubbliche');
  const stat = {};
  base.p.forEach(a => { stat[a[0]] = [a[7], a[8], a[9], a[6]]; });
  stat[d1] = [5, 6.5, 7.25, 21];
  for (let k = 0; k < 200; k++) stat[900000 + k] = [0, 0, 0, 1];   // il file vero ha tutta la Serie A
  ({ t } = await avvia({ adesso: giovedi, dati: { 'statistiche.json': { aggiornato: '2026-09-17T08:00:00+00:00', giocatori: stat },
                                                   'titolari.json': null, 'squadre.json': null } }));
  verifica('sostituiscono quelle di base.json', P(d1).pgv === 5 && P(d1).fm === 7.25 && P(d1).quot === 21,
           `${P(d1).nome}: ${P(d1).pgv} partite, FM ${P(d1).fm}, quotazione ${P(d1).quot}`);
  verifica('entrano nella fantamedia stimata', circa(t.fmStimata(P(d1)), (5 * 7.25 + 5 * (t.STIME.D.a + t.STIME.D.b * 21)) / 10));
  ({ t } = await avvia({ adesso: giovedi, dati: { 'statistiche.json': { aggiornato: 'x', giocatori: { [d1]: [9, 9, 9, 9] } },
                                                   'titolari.json': null, 'squadre.json': null } }));
  verifica('file sospetto (meno di 400 giocatori): restano quelle di base.json', P(d1).pgv === base.p.find(a => a[0] === d1)[7]);

  console.log('\n12. Siri non si usa');
  verifica('niente più domanda dall\'indirizzo (?q=), tolta nella pulizia', !/domandaDaIndirizzo|location\.search/.test(html));

  console.log('\n13. Pagina Chiedi');
  ({ t, el } = await avvia({ adesso: giovedi, dati: { 'titolari.json': null, 'squadre.json': null, 'infortuni.json': null } }));
  g = t.prossima();
  let r = t.rispondi('Chi schiero?');
  const scelti = Object.values(t.undici(g)).flat();
  verifica('«chi schiero?»: tutto l\'undici in poche righe', r.startsWith('Giornata 1 contro ' + AVV1)
           && scelti.every(p => r.includes(p.nome)) && r.split('\n').length <= 14, r.split('\n').length + ' righe');
  verifica('dice che le probabili non sono uscite', /non sono ancora uscite/.test(r));
  r = t.rispondi('chi schiero in difesa');
  verifica('per ruolo: i 4 del modulo, poi solo i nomi', /^In difesa \(4-3-3\):/.test(r)
           && r.split('\n').filter(x => x.startsWith('· ')).length === 4 && /\nPoi: /.test(r), r.split('\n').length + ' righe');
  verifica('domande pronte con un confronto vero', /Chi schiero\?/.test(el.esempi.innerHTML) && / o [^<]+\?/.test(el.esempi.innerHTML),
           el.esempi.innerHTML.replace(/<\/?button>/g, ' ').trim());
  el.esempi.onclick({ target: { closest: () => ({ textContent: 'Chi affronto?' }) } });
  verifica('toccare una domanda pronta risponde', new RegExp('affronti ' + AVV1).test(el.risposta.textContent));

  ({ t, el } = await avvia({ adesso: giovedi, dati: { 'titolari.json': prob5, 'squadre.json': null, 'infortuni.json': null } }));
  g = t.prossima();
  const [A, B] = [P(d1), P(d2)];
  r = t.rispondi(cognomeDi(A) + ' o ' + cognomeDi(B) + '?');
  const pa = t.punteggio(A, g), pb = t.punteggio(B, g);
  const atteso = Math.abs(pa - pb) < 0.25 ? 'Quasi pari' : 'Meglio ' + (pa > pb ? A : B).nome;
  verifica('confronto: verdetto dal punteggio, poi le due schede', r.startsWith(atteso) && r.includes(A.nome) && r.includes(B.nome), r.split('\n')[0]);
  verifica('«chi schiero?» segnala chi non è nelle probabili', /non nelle probabili/.test(t.rispondi('chi schiero')));
  verifica('ricerca senza maiuscole e con accenti', t.rispondi('come sta ' + cognomeDi(A).toUpperCase().replace(/[AEIOU]/, c => c + '̀')).startsWith(A.nome),
           cognomeDi(A).toUpperCase().replace(/[AEIOU]/, c => c + '̀'));
  const pezzo = t.mia.map(p => [p, cognomeDi(p).toLowerCase().slice(0, 5)])
    .find(([p, c]) => c.length === 5 && base.p.filter(a => a[1].toLowerCase().includes(c)).length === 1);
  if (pezzo) verifica('ricerca con parte del cognome', t.rispondi('come sta ' + pezzo[1]).startsWith(pezzo[0].nome), pezzo[1] + ' → ' + pezzo[0].nome);
  const perCognome = {};
  base.p.forEach(a => { const c = a[1].replace(/\s+\S{1,3}\.$/, '').toLowerCase(); (perCognome[c] = perCognome[c] || []).push(a); });
  const omonimi = Object.entries(perCognome).find(([c, l]) => l.length > 1 && !c.includes(' ') && c.length > 3
                                                              && l.filter(a => a[4] === base.me).length !== 1);
  if (omonimi) verifica('omonimi: chiede quale', /Quale\?/.test(t.rispondi('come sta ' + omonimi[0])), omonimi[0]);

  ({ t } = await avvia({ adesso: giovedi, dati: { 'titolari.json': null, 'squadre.json': null,
        'infortuni.json': { aggiornato: '2026-09-13T00:00:00+00:00', voci: { [d2]: { rientro: '30/12/2026', motivo: 'Infortunato' } } } } }));
  r = t.rispondi(cognomeDi(P(d1)) + ' oppure ' + cognomeDi(P(d2)));
  verifica('confronto con un infortunato', r.startsWith('Schiera ' + P(d1).nome), r.split('\n')[0]);

  ({ t, el } = await avvia({ adesso: giovedi }));
  el.mic.onclick();
  verifica('senza riconoscimento vocale: indica la tastiera', /microfono della tastiera/.test(el.risposta.textContent), el.risposta.textContent);
  class VoceOk { start() { this.onresult({ results: [[{ transcript: 'chi affronto' }]] }); this.onend(); } stop() {} }
  ({ t, el } = await avvia({ adesso: giovedi, sr: VoceOk }));
  el.mic.onclick();
  verifica('microfono: la frase dettata riceve risposta', new RegExp('affronti ' + AVV1).test(el.risposta.textContent), el.risposta.textContent.split('\n')[0]);
  class VoceNo { start() { this.onerror({ error: 'service-not-allowed' }); this.onend(); } stop() {} }
  ({ t, el } = await avvia({ adesso: giovedi, sr: VoceNo }));
  el.mic.onclick();
  verifica('microfono bloccato: spiega perché', /non è disponibile/.test(el.risposta.textContent) && /tastiera/.test(el.risposta.textContent),
           el.risposta.textContent.split('\n')[0]);

  console.log('\n14. Font ospitato nel repository');
  verifica('nessuna richiesta a Google Fonts', !/fonts\.(googleapis|gstatic)\.com/.test(html));
  const fonti = [...html.matchAll(/url\("(font\/[^"]+\.woff2)"\)/g)].map(m => m[1]);
  verifica('due spessori, 600 e 700 (il 500 non lo usava nessuno)', fonti.length === 2 && !fonti.some(f => /500/.test(f)), fonti.join(', '));
  verifica('i file esistono e sono woff2', fonti.every(f => fs.existsSync(path.join(REPO, f)) &&
           fs.readFileSync(path.join(REPO, f)).subarray(0, 4).toString() === 'wOF2'));
  verifica('licenza inclusa', fs.existsSync(path.join(REPO, 'font', 'OFL.txt')));
  verifica('titolo disegnato: si vede uguale anche senza font', /<h1 class="titolo" aria-label="JARVIS"><svg viewBox="0 -10 2867 722"/.test(html)
           && /<path fill="url\(#gradTitolo\)" d="M14 520V451/.test(html));

  console.log('\n15. Identità Burkina Faso');
  const png = f => fs.existsSync(f) && fs.readFileSync(f).subarray(1, 4).toString() === 'PNG';
  verifica('icona per la Home', /<link rel="apple-touch-icon" href="img\/icona-180.png">/.test(html) && png(path.join(REPO, 'img', 'icona-180.png')));
  const manifesto = JSON.parse(fs.readFileSync(path.join(REPO, 'manifest.webmanifest'), 'utf8'));
  verifica('manifest con icone che esistono', /<link rel="manifest" href="manifest.webmanifest">/.test(html)
           && manifesto.icons.every(i => png(path.join(REPO, i.src))), manifesto.icons.map(i => i.src).join(', '));
  verifica('colori della bandiera', /--bf-rosso:#EF2B2D/.test(html) && /--bf-verde:#009E49/.test(html) && /--bf-stella:#FCD116/.test(html)
           && !/var\(--rosa\)/.test(html));
  const sfondo = path.join(REPO, 'img', 'sfondo.jpg');
  verifica('sfondo: lo stemma intero, leggero per l\'iPhone', fs.existsSync(sfondo) && fs.statSync(sfondo).size < 400000
           && /url\("img\/sfondo.jpg"\)/.test(html), fs.existsSync(sfondo) ? Math.round(fs.statSync(sfondo).size / 1024) + ' KB' : 'manca');
  verifica('Re Guyzo anche dentro l\'app (stemma e Chiedi)', /<img class="avatar" src="img\/icona-180.png"/.test(html)
           && /<image href="img\/icona-180.png"/.test(html));

  console.log('\n16. Avvisi');
  // venerdì 18 settembre alle 10: scadenza alle 20:30 e un tuo difensore squalificato
  const datiAvvisi = { 'titolari.json': indisp5, 'squadre.json': null, 'infortuni.json': null };
  const memoria = {};
  ({ t, el } = await avvia({ adesso: '2026-09-18T10:00:00+02:00', dati: datiAvvisi, memoria }));
  g = t.prossima();
  let lista = t.avvisi(g);
  verifica('scadenza entro 24 ore: urgente', lista.some(a => a.id === 'scadenza-1-urgente' && a.livello === 'urgente'),
           lista.map(a => a.titolo).join(' | '));
  verifica('tuo giocatore squalificato', lista.some(a => a.id === 'fuori-' + d1 + '-5' && /Squalificato/.test(a.testo)));
  verifica('urgenti per primi', lista[0].livello === 'urgente');
  verifica('pallino con il numero dei nuovi', el['badge-avvisi'].textContent == lista.length && el['badge-avvisi'].classList.contains('on'),
           el['badge-avvisi'].textContent);
  t.apriAvvisi();
  verifica('aperta la scheda, il pallino sparisce', !el['badge-avvisi'].classList.contains('on'));
  ({ t, el } = await avvia({ adesso: '2026-09-18T10:05:00+02:00', dati: datiAvvisi, memoria }));
  verifica('riaprendo l\'app restano letti', !el['badge-avvisi'].classList.contains('on') && !/ nuovo/.test(el.avvisi.innerHTML));
  ({ t } = await avvia({ adesso: giovedi, dati: { 'titolari.json': prob5, 'squadre.json': null, 'infortuni.json': null } }));
  verifica('probabili uscite', t.avvisi(t.prossima()).some(a => a.titolo === 'Probabili uscite'));
  ({ t } = await avvia({ adesso: '2026-10-20T12:00:00+02:00', dati: { 'orari.json': { ...orariVeri, aggiornato: '2026-10-10T08:00:00+00:00' } } }));
  lista = t.avvisi(t.prossima());
  verifica('dati fermi tra gli avvisi', lista.some(a => a.titolo === 'Dati fermi' && a.livello === 'urgente'));
  verifica('rose vecchie di 3 settimane: promemoria', lista.some(a => a.id.startsWith('rose-')));
  ({ t, el } = await avvia({ adesso: '2026-09-13T12:00:00+02:00', dati: { 'titolari.json': null, 'infortuni.json': null } }));
  ({ t } = await avvia({ adesso: '2026-09-18T18:00:00+02:00', dati: datiAvvisi }));
  verifica('sotto le 3 ore: ultima chiamata', t.avvisi(t.prossima()).some(a => a.id === 'scadenza-1-ultima' && /^Ultima chiamata/.test(a.titolo)));
  ({ t } = await avvia({ adesso: '2026-09-15T12:00:00+02:00', dati: { 'titolari.json': null, 'infortuni.json': null } }));
  verifica('il martedì: promemoria per le rose', t.avvisi(t.prossima()).some(a => a.id === 'rose-martedi-2026-09-15'));
  ({ t, el } = await avvia({ adesso: '2026-09-13T12:00:00+02:00', dati: { 'titolari.json': null, 'infortuni.json': null } }));
  verifica('niente da segnalare: tutto tranquillo',/tutto tranquillo/.test(el.avvisi.innerHTML) && !el['badge-avvisi'].classList.contains('on'),
           t.avvisi(t.prossima()).map(a => a.titolo).join(' | ') || 'nessun avviso');

  console.log('\n17. Movimento e senza rete');
  ({ t, el } = await avvia({ adesso: '2026-09-18T10:00:00+02:00', dati: { 'titolari.json': prob5, 'squadre.json': null, 'infortuni.json': null } }));
  verifica('le maglie entrano al primo disegno', el.campo.classList.contains('entra'));
  el.campo.classList.remove('entra');
  t.renderGiornata();
  verifica('non rientrano a ogni aggiornamento del minuto', !el.campo.classList.contains('entra'));
  verifica('barra del tempo: 10 ore e mezza alla scadenza → 93,8% della settimana', el['barra-tempo-i'].style.width === '93.8%'
           && el['barra-tempo'].classList.contains('giorno'), el['barra-tempo-i'].style.width);
  verifica('barre della titolarità in rosa', el.rosa.innerHTML.includes('class="barra b-t"><i style="width:95%">'));
  ({ el } = await avvia({ adesso: '2026-09-18T19:00:00+02:00' }));
  verifica('ultime 3 ore: barra rossa', el['barra-tempo'].classList.contains('ore'));
  const sw = fs.readFileSync(path.join(REPO, 'sw.js'), 'utf8');
  verifica('senza rete: prima la rete, poi la copia salvata', /fetch\(r\)\.then/.test(sw) && /caches\.match\(chiave\)/.test(sw)
           && /index\.html/.test(sw) && /barlow-condensed-700\.woff2/.test(sw));
  verifica('service worker registrato solo se il browser lo supporta', /'serviceWorker' in navigator/.test(html));
  verifica('rispetta «Riduci movimento» dell\'iPhone', /prefers-reduced-motion: reduce/.test(html));
  verifica('cache nuova per i file fissi cambiati', /jarvis-3/.test(sw) && /img\/sfondo\.jpg/.test(sw) && !/stemma\.jpg|condensed-500/.test(sw));

  console.log('\n18. Campo, maglie e schede');
  ({ t, el } = await avvia({ adesso: giovedi, dati: { 'titolari.json': prob5, 'squadre.json': null, 'infortuni.json': null } }));
  g = t.prossima();
  const clubSA = [...new Set(Object.values(base.f).flat(2))];
  verifica('ogni club di Serie A ha la sua maglia', clubSA.every(c => t.MAGLIE[c]),
           clubSA.filter(c => !t.MAGLIE[c]).join(', ') || clubSA.length + ' club');
  const celle = el.campo.innerHTML.match(/class="gioc[^"]*" data-id="\d+"/g) || [];
  verifica('in campo 11 maglie, ognuna tocca e apre la scheda', celle.length === 11, celle.length);
  verifica('linee del campo disegnate', /class="linee"/.test(el.campo.innerHTML));
  const quota = ['P', 'D', 'C', 'A'].map(r => t.posizione(r, 0, 1).y);
  verifica('dal portiere in basso all\'attacco in alto', quota.every((y, i) => i === 0 || y < quota[i - 1]), quota.join(' > '));
  for (const [r, n] of [['D', 4], ['C', 5], ['A', 3]]) {
    const pp = [...Array(n).keys()].map(k => t.posizione(r, k, n));
    verifica(r + ' a ' + n + ': dentro il campo e senza sovrapposizioni', pp.every(p => p.x >= 10 && p.x <= 90)
             && pp.every((p, k) => k === 0 || p.x - pp[k - 1].x >= 18), pp.map(p => p.x + '/' + p.y).join(' '));
  }
  t.apriGiocatore(P(d1).id);
  verifica('scheda del giocatore: nome, fantamedia e titolarità', el['foglio-corpo'].innerHTML.includes(P(d1).nome)
           && /fantamedia/.test(el['foglio-corpo'].innerHTML) && /Titolare al 95%/.test(el['foglio-corpo'].innerHTML)
           && el.foglio.classList.contains('aperto') && el.velo.classList.contains('aperto'));
  t.chiudiFogli();
  verifica('la scheda si chiude', !el.foglio.classList.contains('aperto') && !el.velo.classList.contains('aperto'));
  const barraSotto = (html.match(/<nav>[\s\S]*?<\/nav>/) || [''])[0];
  verifica('avvisi dalla campanella in alto: in basso restano 4 schede', /id="campanella"/.test(html)
           && (barraSotto.match(/data-s="/g) || []).length === 4 && !/data-s="avvisi"/.test(html));
  verifica('«aggiorna» dentro il pannello degli avvisi, non nell\'intestazione',
           /<aside class="foglio" id="pannello"[\s\S]*id="refresh"[\s\S]*?<\/aside>/.test(html)
           && !/id="refresh"/.test((html.match(/<header>[\s\S]*?<\/header>/) || [''])[0]));
  verifica('nel pannello il dettaglio dei dati', /probabili del/.test(el['stamp-dett'].textContent), el['stamp-dett'].textContent);
  const sig = (el['avv-stemma'].innerHTML.match(/>([^<>]*)<\/text>/) || [])[1];
  verifica('stemma dell\'avversario con le sue iniziali', /^[A-Z0-9]{1,2}$/.test(sig || ''), sig);
  verifica('il tuo stemma è Re Guyzo', /img\/icona-180\.png/.test(el['mio-stemma'].innerHTML));

  console.log('\n19. Notifiche di Jarvis');
  verifica('chiave pubblica delle notifiche nell\'app, una sola', (html.match(/const CHIAVE_PUSH = 'B[A-Za-z0-9_-]{86}'/g) || []).length === 1);
  verifica('service worker: mostra la notifica e al tocco apre Jarvis', /addEventListener\('push'/.test(sw) && /showNotification/.test(sw)
           && /addEventListener\('notificationclick'/.test(sw) && /openWindow\('\.\/'\)/.test(sw));
  verifica('pulsante per attivarle e codice da copiare nel pannello degli avvisi', /id="push-attiva"/.test(html)
           && /id="push-copia"/.test(html) && /PUSH_ISCRIZIONE/.test(html));
  const wf = fs.readFileSync(path.join(REPO, '.github', 'workflows', 'aggiorna.yml'), 'utf8');
  verifica('workflow: iscrizione e chiave dai Secrets, notifica di prova a richiesta', /secrets\.PUSH_ISCRIZIONE/.test(wf)
           && /secrets\.PUSH_CHIAVE/.test(wf) && /inputs\.prova/.test(wf) && /web-push@\d+\.\d+\.\d+/.test(wf));
  verifica('pannello pulito: il riquadro per attivarle è nascosto finché serve', /id="push-carta" hidden/.test(html)
           && /id="push-nota" hidden/.test(html) && /id="push-mostra"/.test(html));

  console.log('\n20. Numero sull\'icona di Jarvis');
  const numeri = [];
  const iphone = { setAppBadge: async n => { numeri.push(n); }, clearAppBadge: async () => { numeri.push(0); } };
  ({ t, el } = await avvia({ adesso: '2026-09-18T10:00:00+02:00', dati: datiAvvisi, memoria: {}, nav: iphone }));
  const daLeggere = t.avvisi(t.prossima()).length;
  verifica('l\'icona mostra quanti avvisi non hai letto', daLeggere > 0 && numeri[numeri.length - 1] === daLeggere, numeri.join(', '));
  t.apriAvvisi();
  verifica('aperti gli avvisi, il numero sparisce', numeri[numeri.length - 1] === 0);
  verifica('senza il supporto dell\'iPhone non succede niente', (await avvia({ adesso: giovedi, nav: {} })).t.avvisi !== undefined);
  verifica('service worker: ogni notifica aumenta il numero, che sopravvive alle copie vecchie',
           /setAppBadge/.test(sw) && /aumentaNumero\(\)/.test(sw) && /n !== CACHE && n !== NUMERO/.test(sw));

  console.log('\n21. Pulizia e statistiche nella scheda');
  verifica('niente più «tira giù per aggiornare»', !/id="tira"/.test(html) && !/Tira giù per aggiornare/.test(html));
  verifica('niente più «tocca un giocatore» sotto il campo', !/tocca un giocatore/.test(html));
  verifica('tornando nell\'app dopo mezz\'ora i dati si aggiornano da soli', /visibilitychange/.test(html) && /30\*60000/.test(html));
  const statB = {};
  base.p.forEach(a => { statB[a[0]] = [a[7], a[8], a[9], a[6], 0, 0, 0, 0, 0, 0]; });
  statB[d1] = [3, 6.5, 7.25, 21, 2, 0, 0, 3, 1, 0];
  for (let k = 0; k < 200; k++) statB[900000 + k] = [0, 0, 0, 1];
  ({ t, el } = await avvia({ adesso: giovedi, dati: { 'statistiche.json': { aggiornato: '2026-09-17T08:00:00+00:00', giocatori: statB },
                                                     'titolari.json': null, 'infortuni.json': null, 'squadre.json': sq2 } }));
  t.apriGiocatore(P(d1).id);
  let sch = el['foglio-corpo'].innerHTML;
  verifica('scheda: partite a voto su quelle della squadra, gol e assist', sch.includes('<b class="cond">3/4</b><span>partite a voto</span>')
           && sch.includes('<b class="cond">2</b><span>gol</span>') && sch.includes('<b class="cond">3</b><span>assist</span>'), P(d1).nome);
  verifica('cartellini e data delle statistiche', /1 ammonizione/.test(sch) && /Statistiche di fantacalcio\.it del/.test(sch));
  statB[d1] = [5, 6.5, 7.25, 21, 2, 0, 0, 3, 1, 0];            // statistiche più fresche dei risultati
  ({ t, el } = await avvia({ adesso: giovedi, dati: { 'statistiche.json': { aggiornato: '2026-09-17T08:00:00+00:00', giocatori: statB },
                                                     'titolari.json': null, 'infortuni.json': null, 'squadre.json': sq2 } }));
  t.apriGiocatore(P(d1).id);
  verifica('fonti non allineate: mai più partite a voto che partite della squadra',
           el['foglio-corpo'].innerHTML.includes('<b class="cond">5/5</b><span>partite a voto</span>'));
  statB[d1] = [3, 6.5, 7.25, 21, 2, 0, 0, 3, 1, 0];
  const portiere = t.mia.find(p => p.ruolo === 'P');
  t.apriGiocatore(portiere.id);
  sch = el['foglio-corpo'].innerHTML;
  verifica('per il portiere gol subiti e rigori parati', /<span>gol subiti<\/span>/.test(sch) && /<span>rigori parati<\/span>/.test(sch)
           && !/<span>assist<\/span>/.test(sch), portiere.nome);
  ({ t, el } = await avvia({ adesso: giovedi, dati: { 'titolari.json': null, 'infortuni.json': null, 'squadre.json': null, 'statistiche.json': null } }));
  t.apriGiocatore(P(d1).id);
  verifica('senza i bonus della fonte un trattino, nessun numero inventato', el['foglio-corpo'].innerHTML.includes('<b class="cond">—</b><span>gol</span>'));

  console.log('\n22. La sfida della giornata e gli stemmi');
  ({ t, el } = await avvia({ adesso: giovedi, dati: { 'titolari.json': prob5, 'infortuni.json': null, 'squadre.json': sq2 } }));
  g = t.prossima();
  const sf = t.sfidaDati(g);
  const tutti = u => [].concat(u.P, u.D, u.C, u.A);
  verifica('avversario della giornata, undici completi da entrambe le parti', sf.avv === AVV1
           && tutti(sf.mio.u).length === 11 && tutti(sf.loro.u).length === 11, sf.avv);
  verifica('tuo undici uguale a quello consigliato', tutti(sf.mio.u).map(p => p.id).join() === tutti(t.undici(g)).map(p => p.id).join());
  verifica('il loro è il migliore dei tre moduli, sempre con la difesa a quattro', sf.loro.u.D.length === 4
           && ['4-3-3', '4-4-2', '4-5-1'].every(m => tutti(t.undiciDi(t.players.filter(p => p.team === AVV1), g, m))
                .reduce((s, p) => s + t.punteggio(p, g), 0) <= sf.loro.tot + 1e-9), sf.loro.modulo);
  verifica('solo giocatori loro e disponibili', tutti(sf.loro.u).every(p => p.team === AVV1 && t.disponibile(p, g[2])));
  const cartaSfida = el.sfida.innerHTML;
  verifica('scheda della sfida: totali, verdetto, 22 giocatori da toccare', /Sulla carta/.test(cartaSfida)
           && (cartaSfida.match(/data-id="\d+"/g) || []).length === 22 && cartaSfida.includes(AVV1), (cartaSfida.match(/data-id/g) || []).length);
  verifica('niente spiegazioni, solo i moduli', !/una stima di Jarvis/.test(cartaSfida) && /Tu 4-\d-\d · loro 4-\d-\d/.test(cartaSfida));
  const altre = [...new Set(t.players.map(p => p.team))].filter(x => x !== t.ME);
  verifica('nove avversari, nove colori diversi', new Set(altre.map(t.coloreSquadra)).size === altre.length, altre.length + ' squadre');
  verifica('stemmi in classifica e nel calendario', (el.squadre.innerHTML.match(/class="stemma"/g) || []).length === 10
           && /class="stemma"/.test(el.calendario.innerHTML));
  ({ t } = await avvia({ adesso: '2026-09-22T12:00:00+02:00', dati: { 'titolari.json': null, 'infortuni.json': null } }));
  const mar = t.avvisi(t.prossima()).find(a => a.id === 'rose-martedi-2026-09-22');
  verifica('dopo la prima giornata il martedì chiede i dati della lega: basta scrivere «dati di lega»',
           mar && mar.titolo === 'Dati della lega da aggiornare' && /«dati di lega»/.test(mar.testo) && /sul PC/i.test(mar.testo),
           mar && mar.titolo);

  console.log('\n23. Classifica della lega');
  ({ t, el } = await avvia({ adesso: giovedi, dati: { 'lega.json': null } }));
  verifica('senza il file della lega nessuna classifica inventata', el.classifica.innerHTML === '');
  const squadreLega = [...new Set(base.p.map(a => a[4]))];
  const finta = squadreLega.map((s, k) => [k + 1, s, 1, k < 5 ? 1 : 0, 0, k < 5 ? 0 : 1, 2, 1, 1, k < 5 ? 3 : 0, 70.5 - k]);
  ({ t, el } = await avvia({ adesso: giovedi, dati: { 'lega.json': { aggiornato: '2026-09-22T10:00:00+00:00', classifica: finta } } }));
  const cla = el.classifica.innerHTML;
  verifica('classifica vera: 10 squadre in ordine, con stemma, punti e fantapunti', (cla.match(/class="stemma"/g) || []).length === 10
           && cla.indexOf(squadreLega[0]) < cla.indexOf(squadreLega[9]) && cla.includes('70,5 fantapunti') && cla.includes('1 partita'));
  verifica('la tua squadra in evidenza', new RegExp('<div class="team io"><span class="pos cond">\\d+</span>').test(cla));
  verifica('nessun credito mostrato', !/credit/i.test(cla));
  ({ el } = await avvia({ adesso: giovedi, dati: { 'lega.json': { aggiornato: '2026-09-14T10:00:00+00:00',
          classifica: squadreLega.map((s, k) => [k + 1, s, 0, 0, 0, 0, 0, 0, 0, 0, 0]) } } }));
  verifica('prima della prima giornata niente spiegazioni, solo la data', !/Si comincia/.test(el.classifica.innerHTML)
           && /Aggiornata lun 14 set/.test(el.classifica.innerHTML));

  console.log('\n24. Avvio, gesti, orari dei tuoi, formazione da copiare');
  const avvii = [...html.matchAll(/<link rel="apple-touch-startup-image" media="[^"]+" href="(img\/avvio\/[^"]+\.png)">/g)].map(m => m[1]);
  verifica('immagini d\'avvio per gli iPhone, e i file ci sono', avvii.length >= 10 && avvii.every(f => png(path.join(REPO, f))), avvii.length + ' immagini');
  const senzaSorprese = { 'titolari.json': null, 'infortuni.json': null };
  ({ t, el } = await avvia({ adesso: giovedi, dati: senzaSorprese }));
  verifica('la schermata d\'apertura sfuma quando i dati sono pronti', el.avvio.classList.contains('via'));
  verifica('gesti: pannelli da trascinare in giù, schede da scorrere', /function trascinaPerChiudere/.test(html)
           && /dataset\.verso/.test(html) && /changedTouches/.test(html));
  g = t.prossima();
  verifica('niente più «Copia la formazione» (sul telefono si fa prima a mano)', !/copia-formazione|testoFormazione/.test(html));
  verifica('barra come su iOS 26: lente di vetro da trascinare col dito, sempre grande e fissa',
           /setPointerCapture/.test(html) && /pointermove/.test(html) && !/classList\.toggle\('mini'/.test(html)
           && (html.match(/<nav>[\s\S]*?<\/nav>/)[0].match(/<span>(Giornata|Rosa|Lega|Chiedi)<\/span>/g) || []).length === 4);
  const portiereU = t.undici(g).P[0];
  const conPartite = { ...orariVeri, aggiornato: '2026-09-17T08:00:00+00:00', giornate: { ...orariVeri.giornate,
    '5': { ...orariVeri.giornate['5'], partite: [[portiereU.club, 'Squadra finta', '2026-09-19T16:00:00+00:00']] } } };
  ({ t, el } = await avvia({ adesso: giovedi, dati: { ...senzaSorprese, 'orari.json': conPartite } }));
  verifica('sotto la maglia il giorno e l\'ora della partita', el.campo.innerHTML.includes('<span class="ora">sab 18:00</span>'));
  verifica('«Quando giocano i tuoi»: scadenza in cima, poi la partita con i tuoi', /Quando giocano i tuoi/.test(el.quando.innerHTML)
           && el.quando.innerHTML.indexOf('Scadenza della formazione') < el.quando.innerHTML.indexOf(portiereU.nome), portiereU.nome);
  t.apriGiocatore(portiereU.id);
  verifica('nella scheda anche l\'orario', /sab 18:00/.test(el['foglio-corpo'].innerHTML));
  ({ el } = await avvia({ adesso: giovedi, dati: { ...senzaSorprese, 'orari.json': { ...orariVeri, aggiornato: '2026-09-17T08:00:00+00:00',
          giornate: { ...orariVeri.giornate, '5': { ...orariVeri.giornate['5'], partite: undefined } } } } }));
  verifica('senza gli orari delle partite nessun orario inventato', el.quando.innerHTML === '' && !/class="ora"/.test(el.campo.innerHTML));

  console.log('\n25. Importa da Leghe sul telefono');
  const esempioXlsx = fs.readFileSync(path.join(__dirname, 'dati', 'classifica-prova.xlsx'));
  const buf = b => new Uint8Array(b).buffer;
  const memLega = {};
  ({ t, el } = await avvia({ adesso: giovedi, memoria: memLega }));
  const righeX = await t.leggiXlsx(buf(esempioXlsx));
  verifica('il file Excel si apre sul telefono, senza librerie', righeX.some(r => r[0] === 'Pos' && r[1] === 'Squadra'), righeX.length + ' righe');
  const importata = await t.importaClassifica(buf(esempioXlsx));
  verifica('classifica importata: 10 squadre in ordine, con i numeri del file', importata.length === 10
           && importata[0].slice(2).join() === '2,2,0,0,5,1,4,6,150.5', importata[0].join(' '));
  verifica('si vede subito nella scheda Lega, detto che viene dal telefono', el.classifica.innerHTML.includes('150,5 fantapunti')
           && /Importata sul telefono/.test(el.classifica.innerHTML));
  verifica('resta sul telefono', !!memLega['jarvis-lega'] && JSON.parse(memLega['jarvis-lega']).origine === 'telefono');
  ({ el } = await avvia({ adesso: giovedi, memoria: memLega }));
  verifica('riaprendo l\'app vale la più recente: quella del telefono', el.classifica.innerHTML.includes('150,5 fantapunti'));
  ({ el } = await avvia({ adesso: giovedi, memoria: memLega, dati: { 'lega.json': { aggiornato: '2026-09-30T10:00:00+00:00',
          classifica: squadreLega.map((s, k) => [k + 1, s, 0, 0, 0, 0, 0, 0, 0, 0, 0]) } } }));
  verifica('se quella del PC è più nuova vale quella', !el.classifica.innerHTML.includes('150,5'));
  const primaDelFileSbagliato = memLega['jarvis-lega'];
  let rifiuto = '';
  try { await t.importaClassifica(buf(Buffer.from('non sono un file Excel'))); } catch (e) { rifiuto = e.message; }
  verifica('file sbagliato: lo dice e non tocca niente', /non è un file Excel/.test(rifiuto) && memLega['jarvis-lega'] === primaDelFileSbagliato, rifiuto);
  const righeRotte = righeX.map(r => [...r]);
  righeRotte[righeRotte.findIndex(r => r[0] === 1)][4] = 7;
  try { t.classificaDaRighe(righeRotte); rifiuto = ''; } catch (e) { rifiuto = e.message; }
  verifica('numeri che non tornano: si ferma', /vinte \+ pari \+ perse/.test(rifiuto), rifiuto);
  try { t.classificaDaRighe([['Pos', 'Team']]); rifiuto = ''; } catch (e) { rifiuto = e.message; }
  verifica('file di un\'altra pagina: dice quale serve', /Classifica/.test(rifiuto), rifiuto);
  const veri = fs.existsSync(path.join(REPO, 'archivio', 'lega')) ?
    fs.readdirSync(path.join(REPO, 'archivio', 'lega')).filter(f => /^Classifica_.*\.xlsx$/.test(f)).sort() : [];
  if (veri.length) {
    const cv = t.classificaDaRighe(await t.leggiXlsx(buf(fs.readFileSync(path.join(REPO, 'archivio', 'lega', veri[veri.length - 1])))));
    verifica('il file vero di Leghe si legge uguale (solo sul PC)', cv.length === 10 && cv.every(r => squadreLega.includes(r[1])), veri[veri.length - 1]);
  }

  console.log('\n26. Liquid Glass');
  verifica('intestazione normale: niente capsula che si stringe scorrendo (non piaceva)', !/body\.scorso|'scorso'/.test(html));
  verifica('modulo con la lente da trascinare', /selettore\.addEventListener\('pointermove'/.test(html) && /function scegliModulo/.test(html));
  verifica('pannelli di vetro staccati dai bordi', /\.foglio\{left:8px; right:8px/.test(html));
  verifica('pulsanti di vetro che si illuminano al tocco', /\.luce::after/.test(html) && /--gx/.test(html));

  console.log('\n27. Rosa: maglie per reparto, elenco e filtri');
  const memRosa = {};
  ({ t, el } = await avvia({ adesso: giovedi, memoria: memRosa, dati: { 'titolari.json': indisp5, 'squadre.json': null, 'infortuni.json': null } }));
  const tessere = r => (r.match(/<button class="rc/g) || []).length;
  verifica('vista con le maglie: 25 giocatori per reparto, e l\'elenco con i dettagli pronto', el.rosa.dataset.vista === 'maglie'
           && tessere(el.rosa.innerHTML) === 25 && (el.rosa.innerHTML.match(/<div class="riga/g) || []).length === 25, tessere(el.rosa.innerHTML));
  const squalificato = el.rosa.innerHTML.match(new RegExp('<button class="rc fuori" data-id="' + d1 + '"[\\s\\S]*?</button>'));
  verifica('chi è fuori è sbiadito, con il motivo', !!squalificato && /Squalificato/.test(squalificato[0]));
  verifica('filtri con il numero di giocatori', /Fuori<b>2<\/b>/.test(el['rosa-comandi'].innerHTML) && /Tutti<b>25<\/b>/.test(el['rosa-comandi'].innerHTML),
           el['rosa-comandi'].innerHTML.replace(/<svg[\s\S]*?<\/svg>/g, '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim());
  const tocca = ds => el['rosa-comandi'].onclick({ target: { closest: () => ({ dataset: ds }) } });
  tocca({ filtro: 'fuori' });
  verifica('filtro «Fuori»: solo i due fuori', tessere(el.rosa.innerHTML) === 2 && el.rosa.innerHTML.includes('data-id="' + d1 + '"'));
  tocca({ filtro: 'tutti' });
  tocca({ vista: 'elenco' });
  verifica('vista a elenco, ricordata sul telefono', el.rosa.dataset.vista === 'elenco' && memRosa['jarvis-rosa-vista'] === 'elenco');
  ({ el } = await avvia({ adesso: giovedi, memoria: memRosa }));
  verifica('riaprendo l\'app resta l\'elenco', el.rosa.dataset.vista === 'elenco');

  console.log('\n28. Voti: com\'è andata, andamento, calendario dei tuoi, mercato');
  const martedi = '2026-09-15T12:00:00+02:00';
  ({ t } = await avvia({ adesso: martedi, dati: { 'titolari.json': null, 'infortuni.json': null, 'voti.json': null } }));
  const portieri = t.mia.filter(p => p.ruolo === 'P');
  const sa4 = {};
  t.mia.filter(p => p.ruolo !== 'P' || p === portieri[0]).forEach((p, k) => { sa4[p.id] = [6 + (k % 3) * 0.5, 5 + (k % 6)]; });
  const conVoti = { 'titolari.json': null, 'infortuni.json': null, 'consigli.json': null,
                    'voti.json': { aggiornato: '2026-09-15T08:00:00+00:00', giornate: { '4': sa4 } } };
  ({ t, el } = await avvia({ adesso: martedi, dati: conVoti }));
  let ca = t.comeAndata();
  verifica('prima della lega: com\'è andata la giornata 4 di Serie A', ca && ca.sa === 4 && !ca.g
           && /Serie A, giornata 4/.test(el.comeandata.innerHTML));
  verifica('nella Giornata solo una riga, che invita ad aprire', /class="invito"/.test(el.comeandata.innerHTML)
           && !/class="vr/.test(el.comeandata.innerHTML) && /Il migliore dei tuoi: .*, [\d,]+</.test(el.comeandata.innerHTML));
  t.apriComeAndata();
  let sc = el['sovra-corpo'].innerHTML;
  verifica('toccandola si apre in sovraimpressione, con tutti i tuoi', el.sovra.classList.contains('aperto')
           && (sc.match(/class="vr[ "]/g) || []).length === t.mia.length, (sc.match(/class="vr[ "]/g) || []).length);
  const conMalus = t.mia.find(p => sa4[p.id] && sa4[p.id][1] < sa4[p.id][0]);
  const f1 = x => x.toFixed(1).replace('.', ',');
  verifica('ogni fantavoto spiegato: voto e bonus o malus', conMalus
           && sc.includes('voto ' + f1(sa4[conMalus.id][0]) + ' · −' + f1(sa4[conMalus.id][0] - sa4[conMalus.id][1]) + ' di malus'), conMalus && conMalus.nome);
  verifica('prima della lega: nessun totale, nessuna spiegazione', !/massimo|non era ancora iniziata|Come si legge|class="chip/i.test(sc));
  t.chiudiSovra();
  verifica('e si chiude', !el.sovra.classList.contains('aperto'));
  // la stagione, con gli stessi voti
  verifica('la stagione: una riga nella Rosa', /class="invito"/.test(el.stagione.innerHTML) && /La stagione/.test(el.stagione.innerHTML)
           && /Chi produce di più: /.test(el.stagione.innerHTML));
  t.apriStagione();
  const st = t.stagione(), sst = el['sovra-corpo'].innerHTML;
  const piuAlto = Math.max(...t.mia.map(p => sa4[p.id] ? sa4[p.id][1] : 0));
  verifica('chi produce: tutti i tuoi, dal più prolifico', (sst.match(/class="vr prod"/g) || []).length === t.mia.length
           && Math.abs(st.righe[0].tot - piuAlto) < 1e-9 && st.righe.every((x, i) => !i || st.righe[i - 1].tot >= x.tot), st.righe[0].p.nome);
  verifica('con gol, assist e ammonizioni dei tuoi', ['Gol', 'Assist', 'Ammonizioni'].every(k => sst.includes(k)));
  t.chiudiSovra();
  // giornata per giornata, da navigare
  const sa3 = {};
  t.mia.forEach((p, k) => { sa3[p.id] = [6, 4 + (k % 3)]; });
  ({ t, el } = await avvia({ adesso: martedi, dati: Object.assign({}, conVoti, { 'voti.json': { aggiornato: 'x', giornate: { '3': sa3, '4': sa4 } } }) }));
  const st2 = t.stagione();
  verifica('giornata per giornata: i migliori 11 di ogni giornata, reparto per reparto', st2.per.length === 2 && st2.per.every(x =>
           x.scelti.length === 11 && x.scelti.filter(p => p.ruolo === 'D').length === 4
           && Math.abs(x.tot - ['P', 'D', 'C', 'A'].reduce((s, r) => s + x.reparti[r], 0)) < 1e-9), st2.per.map(x => x.tot).join(' e '));
  t.apriStagione();
  const piccoSt = st2.per.reduce((a, b) => b.tot > a.tot ? b : a), altraSt = st2.per.find(x => x !== piccoSt).sa;
  sc = el['sovra-corpo'].innerHTML;
  verifica('il grafico: una colonna per giornata, si apre sulla migliore', (sc.match(/class="st-col[ "]/g) || []).length === 2
           && sc.includes('class="st-col sel" data-sa="' + piccoSt.sa + '"') && /la migliore/.test(sc) && /★/.test(sc), 'giornata ' + piccoSt.sa);
  t.scegliGiornata(altraSt);
  verifica('toccando un\'altra giornata: chi ha fatto cosa quel giorno', el['st-grafico'].innerHTML.includes('class="st-col sel" data-sa="' + altraSt + '"')
           && (el['st-giornata'].innerHTML.match(/class="vr"/g) || []).length === 11 && /la peggiore/.test(el['st-giornata'].innerHTML)
           && ['Porta', 'Difesa', 'Centrocampo', 'Attacco'].every(k => el['st-giornata'].innerHTML.includes(k)));
  ({ t, el } = await avvia({ adesso: martedi, dati: conVoti }));    // di nuovo una giornata sola, per le prove che seguono
  const QM = [{ D: 4, C: 3, A: 3 }, { D: 4, C: 4, A: 2 }, { D: 4, C: 5, A: 1 }];
  const meglioAtteso = Math.max(...QM.map(q => ['P', 'D', 'C', 'A'].reduce((s, r) => s + t.mia
    .filter(p => p.ruolo === r && sa4[p.id]).map(p => sa4[p.id][1]).sort((a, b) => b - a)
    .slice(0, r === 'P' ? 1 : q[r]).reduce((x, y) => x + y, 0), 0)));
  verifica('il migliore possibile con i voti veri, difesa a quattro', Math.abs(ca.migliore.tot - meglioAtteso) < 1e-9
           && ca.migliore.scelti.filter(p => p.ruolo === 'D').length === 4, ca.migliore.tot);
  verifica('prima della lega nessuna notifica dei voti', !t.avvisi(t.prossima()).some(a => a.id.startsWith('voti-')));
  const conVotoC = t.mia.find(p => p.ruolo === 'C' && sa4[p.id]);
  t.apriGiocatore(conVotoC.id);
  verifica('andamento nella scheda del giocatore', /Fantavoto giornata per giornata/.test(el['foglio-corpo'].innerHTML)
           && el['foglio-corpo'].innerHTML.includes('Ultime: ' + sa4[conVotoC.id][1].toFixed(1).replace('.', ',')), conVotoC.nome);
  const senzaVoto = portieri.find(p => !sa4[p.id] && t.avversarioClub(p.club, 4));
  if (senzaVoto) {
    t.apriGiocatore(senzaVoto.id);
    verifica('chi non ha preso voto: s.v.', /s\.v\./.test(el['foglio-corpo'].innerHTML), senzaVoto.nome);
  }
  verifica('com\'è andata sparisce dopo la scadenza della giornata dopo',
           !(await avvia({ adesso: '2026-09-18T21:00:00+02:00', dati: conVoti })).t.comeAndata());
  // giornata 1 di lega (Serie A 5): consiglio salvato, un difensore titolare senza voto
  const perRuolo = r => t.mia.filter(p => p.ruolo === r);
  const titolariG1 = [...perRuolo('P').slice(0, 1), ...perRuolo('D').slice(0, 4), ...perRuolo('C').slice(0, 3), ...perRuolo('A').slice(0, 3)];
  const panchinaG1 = t.mia.filter(p => !titolariG1.includes(p));
  const sa5 = {};
  t.mia.forEach((p, k) => { sa5[p.id] = [6, 6 + (k % 4)]; });
  delete sa5[titolariG1[1].id];
  const entra = panchinaG1.find(p => p.ruolo === 'D');
  const attesoJ = titolariG1.filter(p => sa5[p.id]).reduce((s, p) => s + sa5[p.id][1], 0) + sa5[entra.id][1];
  ({ t, el } = await avvia({ adesso: '2026-09-22T12:00:00+02:00', dati: { 'titolari.json': null, 'infortuni.json': null,
          'voti.json': { aggiornato: 'x', giornate: { '4': sa4, '5': sa5 } },
          'consigli.json': { giornate: { '1': { sa: 5, undici: { '4-3-3': titolariG1.map(p => p.id) }, panchina: { '4-3-3': panchinaG1.map(p => p.id) } } } } } }));
  ca = t.comeAndata();
  verifica('giornata 1 di lega: l\'undici di Jarvis con la sostituzione della lega', ca && ca.g && ca.g[0] === 1 && ca.consiglio
           && Math.abs(ca.consiglio.tot - attesoJ) < 1e-9 && ca.consiglio.cambi === 1, ca && ca.consiglio && ca.consiglio.tot);
  verifica('nella Giornata una riga: l\'undici di Jarvis', /Con l'undici di Jarvis [\d,]+</.test(el.comeandata.innerHTML),
           (el.comeandata.innerHTML.match(/Con l'undici di Jarvis [^<]*/) || [])[0]);
  t.apriComeAndata();
  sc = el['sovra-corpo'].innerHTML;
  verifica('in sovraimpressione: l\'undici di Jarvis con la sostituzione, niente massimo', /Con l'undici di Jarvis \(4-3-3\)/.test(sc)
           && /1 titolare senza voto, sostituito dalla panchina/.test(sc) && !/massimo/i.test(sc)
           && (sc.match(/class="chip j"/g) || []).length === 11);
  // con il risultato vero, dal calendario di Leghe
  const conRisultato = { 'titolari.json': null, 'infortuni.json': null,
    'lega.json': { aggiornato: '2026-09-22T10:00:00+00:00', classifica: finta, risultati: { '1': [[AVV1, 66, t.ME, 70.5, 1, 2]] } },
    'voti.json': { aggiornato: 'x', giornate: { '4': sa4, '5': sa5 } },
    'consigli.json': { giornate: { '1': { sa: 5, undici: { '4-3-3': titolariG1.map(p => p.id) }, panchina: { '4-3-3': panchinaG1.map(p => p.id) } } } } };
  ({ t, el } = await avvia({ adesso: '2026-09-22T12:00:00+02:00', dati: conRisultato }));
  verifica('con il risultato di Leghe: il punteggio vero nella riga', /Finita 2-1, 70,5 a 66,0 · Jarvis [\d,]+</.test(el.comeandata.innerHTML),
           (el.comeandata.innerHTML.match(/Finita [^<]*/) || [])[0]);
  t.apriComeAndata();
  sc = el['sovra-corpo'].innerHTML;
  const scarto = attesoJ - 70.5;
  verifica('in sovraimpressione il risultato vero e, accanto, quanto avrebbe fatto Jarvis', sc.includes('70,5') && sc.includes('66,0')
           && sc.includes(AVV1) && sc.includes(f1(Math.abs(scarto)) + (scarto > 0 ? ' in più' : ' in meno')), f1(scarto));
  verifica('e la notifica «com\'è andata»', t.avvisi(t.prossima()).some(a => a.id === 'voti-5' && /^Giornata 1: com'è andata/.test(a.titolo)));
  // calendario dei tuoi e mercato
  ({ t, el } = await avvia({ adesso: giovedi, dati: { 'titolari.json': null, 'infortuni.json': null, 'squadre.json': sq2 } }));
  g = t.prossima();
  const p3 = t.prossimi3(t.mia[0], g);
  verifica('calendario dei tuoi: i prossimi 3 avversari, dalla giornata che si gioca', p3.length === 3 && p3[0].sa === g[1]
           && p3.every(x => ['facile', 'media', 'dura', 'nd'].includes(x.livello)), p3.map(x => x.avv + ' ' + x.livello).join(', '));
  verifica('squadre tutte nella media: pallini gialli', p3.some(x => x.livello === 'media') && p3.every(x => x.livello === 'media' || x.livello === 'nd'));
  verifica('pallini sotto ogni maglia della rosa', (el.rosa.innerHTML.match(/class="cal3"/g) || []).length === 25);
  t.apriGiocatore(t.mia[0].id);
  verifica('nella scheda la riga «Prossime 3»', /Prossime 3/.test(el['foglio-corpo'].innerHTML));
  const mk = t.mercato(g), singoli = mk.singoli, doppi = mk.doppi, tuttiMk = singoli.concat(doppi);
  const qSomma = l => l.reduce((s, p) => s + p.quot, 0);
  const fmMedia = l => l.every(p => p.pgv >= 2) ? l.reduce((s, p) => s + p.fm, 0) / l.length : null;
  const forti = sq => {
    const rosa = t.players.filter(p => p.team === sq), q = (a, b) => b.quot - a.quot, f = new Set(rosa.slice().sort(q).slice(0, 3));
    ['P', 'D', 'C', 'A'].forEach(r => rosa.filter(p => p.ruolo === r).sort(q).slice(0, r === 'P' ? 1 : 2).forEach(p => f.add(p)));
    return f;
  };
  verifica('mercato: 1 contro 1 e 2 contro 2, dai i tuoi e prendi i loro', singoli.length <= 4 && doppi.length <= 3
           && singoli.every(i => i.dai.length === 1 && i.prendi.length === 1) && doppi.every(i => i.dai.length === 2 && i.prendi.length === 2)
           && tuttiMk.every(i => i.dai.every(p => p.team === t.ME) && i.prendi.every(p => p.team === i.squadra) && i.squadra !== t.ME),
           tuttiMk.map(i => i.dai.map(p => p.nome).join('+') + ' per ' + i.prendi.map(p => p.nome).join('+')).join(', ') || 'nessuno');
  verifica('alla pari a vista: quotazioni vicine e fantamedia vera non nettamente più bassa', tuttiMk.every(i => {
    const a = fmMedia(i.dai), b = fmMedia(i.prendi);
    return Math.abs(qSomma(i.dai) - qSomma(i.prendi)) <= Math.max(i.dai.length === 1 ? 2 : 3, 0.15 * Math.max(qSomma(i.dai), qSomma(i.prendi)))
        && (a === null || b === null || a >= b - 0.5);
  }));
  verifica('i pezzi forti non si chiedono: mai i due più quotati del reparto, né i tre della rosa', tuttiMk.every(i => {
    const f = forti(i.squadra);
    return i.prendi.every(p => !f.has(p));
  }));
  verifica('serve a tutti e due: il tuo undici migliora, chi dai entra nel loro', tuttiMk.every(i =>
           i.perMe >= (i.dai.length === 1 ? 0.3 : 0.5) && i.perLoro >= 0 && i.entranoLoro.length > 0));
  verifica('un 2 contro 2 solo se rende più del miglior scambio singolo tra quei giocatori', doppi.every(i => i.perMe >= i.meglioSingolo + 0.2));
  verifica('prima gli scambi di esuberi', [singoli, doppi].every(l => l.every((i, k) => !k || l[k - 1].esubero >= i.esubero)));
  verifica('mai lo stesso giocatore chiesto due volte', new Set(tuttiMk.flatMap(i => i.prendi.map(p => p.id))).size
           === tuttiMk.reduce((s, i) => s + i.prendi.length, 0));
  verifica('nella Lega solo una riga, che invita ad aprire', /class="invito"/.test(el.mercato.innerHTML)
           && /Mercato, sulla carta/.test(el.mercato.innerHTML) && !/sc-coppia/.test(el.mercato.innerHTML));
  t.apriMercato(g);
  sc = el['sovra-corpo'].innerHTML;
  verifica('in sovraimpressione: chi dai, chi prendi, per te e per loro', el.sovra.classList.contains('aperto') && (tuttiMk.length
           ? (sc.match(/class="blocco mk"/g) || []).length === tuttiMk.length && ['Dai', 'Prendi', 'Per te', 'Valore Jarvis'].every(k => sc.includes(k))
             && /1 contro 1/.test(sc) === singoli.length > 0 && /2 contro 2/.test(sc) === doppi.length > 0
           : /Nessuno scambio/.test(sc)), singoli.length + ' singoli, ' + doppi.length + ' doppi');
  verifica('niente tutorial', !/Come si legge|stima di Jarvis|sovra-intro/i.test(sc));

  console.log('\n29. Tabellone e forma della lega');
  const sfidaG = gio => BASE0.g[gio - 1][3].find(([a, b]) => a === BASE0.me || b === BASE0.me);
  const risultatoG = (gio, fpMio, fpAvv, golMio = 1, golAvv = 1) => {
    const [a, b] = sfidaG(gio), casaMe = a === BASE0.me;
    return casaMe ? [a, fpMio, b, fpAvv, golMio, golAvv] : [a, fpAvv, b, fpMio, golAvv, golMio];
  };
  const vittoriaG1 = risultatoG(1, 70.5, 66, 2, 1), sconfittaG1 = risultatoG(1, 60, 75, 0, 3), pariG1 = risultatoG(1, 65, 65, 1, 1);
  const seiGiornate = { 1: [vittoriaG1], 2: [risultatoG(2, 60, 60, 1, 1)], 3: [risultatoG(3, 55, 65, 0, 2)],
    4: [risultatoG(4, 68, 50, 3, 1)], 5: [risultatoG(5, 72, 71, 1, 1)], 6: [risultatoG(6, 64, 64, 2, 2)] };
  ({ t, el } = await avvia({ adesso: giovedi, dati: { 'lega.json': { aggiornato: 'x', classifica: finta, risultati: seiGiornate } } }));
  verifica('la forma: esiti delle ultime 5 giornate già giocate, dalla più vecchia alla più recente',
           t.forma(t.ME).join('') === 'NPVVN', t.forma(t.ME).join(''));
  verifica('una squadra senza risultati: forma vuota, niente inventato', t.forma('Squadra Mai Vista').length === 0);
  verifica('i pallini della forma in classifica', (el.classifica.innerHTML.match(/class="forma"/g) || []).length > 0
           && /class="fp v"/.test(el.classifica.innerHTML) && /class="fp n"/.test(el.classifica.innerHTML)
           && /class="fp p"/.test(el.classifica.innerHTML));

  // il tabellone: il punteggio vero al posto di «VS» nella testata, finché resta questa la giornata mostrata
  ({ el } = await avvia({ adesso: '2026-09-20T22:40:00+02:00',
    dati: { 'lega.json': { aggiornato: 'x', classifica: finta, risultati: { 1: [vittoriaG1] } } } }));
  verifica('ancora giornata 1: il punteggio vero al posto di «VS»', el.vs.textContent === '70,5 - 66,0', el.vs.textContent);
  verifica('hai vinto: la testata festeggia', el['vs-riga'].classList.contains('vinta') && !el['vs-riga'].classList.contains('persa'));

  ({ el } = await avvia({ adesso: '2026-09-20T22:40:00+02:00',
    dati: { 'lega.json': { aggiornato: 'x', classifica: finta, risultati: { 1: [sconfittaG1] } } } }));
  verifica('hai perso: niente festeggiamento', el.vs.textContent === '60,0 - 75,0'
           && !el['vs-riga'].classList.contains('vinta') && el['vs-riga'].classList.contains('persa'), el.vs.textContent);

  ({ el } = await avvia({ adesso: '2026-09-20T22:40:00+02:00',
    dati: { 'lega.json': { aggiornato: 'x', classifica: finta, risultati: { 1: [pariG1] } } } }));
  verifica('pareggio: il punteggio si vede, né vinta né persa', el.vs.textContent === '65,0 - 65,0'
           && !el['vs-riga'].classList.contains('vinta') && !el['vs-riga'].classList.contains('persa'));

  ({ el } = await avvia({ adesso: '2026-09-20T22:50:00+02:00',
    dati: { 'lega.json': { aggiornato: 'x', classifica: finta, risultati: { 1: [vittoriaG1] } } } }));
  verifica('passata alla giornata 2, senza un suo risultato: torna «VS»', el.vs.textContent === 'VS'
           && !el['vs-riga'].classList.contains('vinta') && !el['vs-riga'].classList.contains('persa'), el.vs.textContent);

  ({ el } = await avvia({ adesso: giovedi, dati: { 'lega.json': null } }));
  verifica('senza il file della lega: niente forma, niente tabellone', el.vs.textContent === 'VS' && el.classifica.innerHTML === '');

  console.log('\n' + (esiti - falliti) + '/' + esiti + ' verifiche superate');
  process.exit(falliti ? 1 : 0);
})().catch(e => { console.error('ERRORE', e); process.exit(2); });
