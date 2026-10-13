// Backtest del calcolo di Jarvis sulle giornate salvate (probabili d'epoca, voti veri, rose di tutte le squadre delle due leghe).
// Uso:  node prove/backtest.js [index.html] [uscita.json]     (index.html di un'altra versione: git show <commit>:index.html > file)
//       node prove/backtest.js --confronta vecchio.json nuovo.json
//       INS=1 ...  calibra anche sulle giornate stesse (tetto massimo, non è una prova fuori campione)
// Per ogni squadra-giornata: undici consigliato per ognuno dei 7 moduli, punteggio vero con le regole della lega (5 cambi,
// pari ruolo, ordine della panchina, 0 se non entra nessuno, modificatore difesa). Differenza a coppie tra due versioni.
// Limite: modello.json e squadre.json contengono già le giornate provate (i numeri assoluti sono ottimisti, il confronto regge).
// L'uscita .json contiene i nomi delle squadre: non va nel repository (si scrive in una cartella temporanea).
// Banco di prova come prove/app.js (vm + finto DOM), dati veri letti da JARVIS/dati, probabili d'epoca.
process.env.TZ = 'Europe/Rome';
const fs = require('fs'), path = require('path'), vm = require('vm');
const REPO = path.join(__dirname, '..');


const STOR = JSON.parse(fs.readFileSync(path.join(REPO, 'dati/titolari-storico.json'), 'utf8')).giornate;
if (process.argv[2] === '--confronta') {
const A=JSON.parse(fs.readFileSync(process.argv[3])),B=JSON.parse(fs.readFileSync(process.argv[4]));
const key=r=>[r.lega,r.regime,r.sa,r.team].join('|');const mods=['4-3-3','4-4-2','4-5-1','3-5-2','3-4-3','5-3-2','5-4-1'];
function st(d){const n=d.length,m=d.reduce((s,x)=>s+x,0)/n,v=d.reduce((s,x)=>s+(x-m)**2,0)/(n-1);return `n=${n} m=${m.toFixed(2)} se=${Math.sqrt(v/n).toFixed(2)} w/l=${d.filter(x=>x>0.01).length}/${d.filter(x=>x<-0.01).length}`}
for(const [nome,fl] of [['tutto',r=>true],['SA6 (solo storico vero)',r=>r.sa===6],['con probabili',r=>r.regime==='con'],['senza probabili',r=>r.regime==='senza']]){
 const S=B.filter(fl),a=r=>A.find(x=>key(x)===key(r));
 console.log(nome.padEnd(26),'cons',st(S.map(r=>r.reale-a(r).reale)),'| lineup',st(S.flatMap(r=>mods.map(m=>r[m]-a(r)[m]))));}

process.exit(0); }

const HTML = process.argv[2] || path.join(REPO, 'index.html');
const html = fs.readFileSync(HTML, 'utf8');
const codice = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].pop()[1];
const SOGLIE = [[7, 6], [6.75, 4.5], [6.5, 3], [6.25, 2], [6, 1]];

async function avvia(lega, dati, reale) {
  const RealDate = Date, fisso = new RealDate('2026-10-13T12:00:00+02:00').getTime();
  class FD extends RealDate { constructor(...a) { a.length ? super(...a) : super(fisso); } static now() { return fisso; } }
  const el = {};
  const nodo = id => el[id] || (el[id] = { id, textContent: '', innerHTML: '', value: '', style: {}, dataset: {},
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } }, addEventListener() {}, click() {}, focus() {}, blur() {} });
  dati = Object.assign(reale ? { 'lucchetto.json': null } : { 'lucchetto.json': null, 'infortuni.json': null, 'formazioni.json': null }, dati);
  const ctx = { Date: FD, console, URLSearchParams, Promise, Object, String, Math, Set, JSON, setInterval() {}, setTimeout: () => 0, clearTimeout() {},
    requestIdleCallback: f => { f(); return 0; }, localStorage: { getItem: () => null, setItem() {} }, sessionStorage: { getItem: () => null, setItem() {} },
    location: { search: '?lega=' + lega, host: 'x', pathname: '/JARVIS/' }, document: { getElementById: nodo, querySelector: () => nodo('_q'), querySelectorAll: () => [] },
    fetch: async url => {
      const f = url.split('?')[0], nome = f.replace(/^dati\//, '');
      if (nome in dati) { const v = dati[nome]; return v === null ? { ok: false, status: 404 } : { ok: true, status: 200, json: async () => JSON.parse(JSON.stringify(v)) }; }
      const p = path.join(REPO, f); if (!fs.existsSync(p)) return { ok: false, status: 404 };
      const o = JSON.parse(fs.readFileSync(p, 'utf8'));
      if (nome === 'orari.json') o.aggiornato = new RealDate(fisso).toISOString();
      return { ok: true, status: 200, json: async () => o };
    } };
  Object.assign(ctx, { Response, TextDecoder, TextEncoder, atob, btoa, crypto: require('crypto').webcrypto }); ctx.window = ctx;
  vm.createContext(ctx); vm.runInContext(codice, ctx);
  await new Promise(r => setTimeout(r, 80));
  const ev = s => vm.runInContext(s, ctx);
  return { ev };
}

function punteggioReale(app, rosaIds, u, g, sa) {
  const V = app.ev('D.voti')[String(sa)] || {};
  const voto = id => V[String(id)] || null;
  const pl = id => app.ev('players').find(p => p.id === id);
  const titolari = [].concat(u.P, u.D, u.C, u.A);
  const idT = new Set(titolari.map(p => p.id));
  const iso = g[2];
  // panchina: gli altri disponibili, ordinati per ruolo e punteggio (come panchina() dell'app)
  const rosa = app.ev('players').filter(p => rosaIds.has(p.id));
  const punt = app.ev('punteggio');
  const panca = rosa.filter(p => !idT.has(p.id) && app.ev('disponibile')(p, iso)).sort((a, b) => punt(b, g) - punt(a, g));
  const usati = new Set(); let cambi = 0, tot = 0, vuoti = 0; const finali = [];
  titolari.forEach(p => {
    const v = voto(p.id);
    if (v) { tot += v[1]; finali.push({ r: p.ruolo, voto: v[0] }); return; }
    const q = cambi < 5 ? panca.find(x => x.ruolo === p.ruolo && !usati.has(x.id) && voto(x.id)) : null;
    if (q) { usati.add(q.id); cambi++; tot += voto(q.id)[1]; finali.push({ r: q.ruolo, voto: voto(q.id)[0] }); } else vuoti++;
  });
  const dif = finali.filter(x => x.r === 'D').map(x => x.voto).sort((a, b) => b - a);
  const por = finali.find(x => x.r === 'P');
  let mod = 0;
  if (por && dif.length >= 4 - 1 && titolari.filter(p => p.ruolo === 'D').length >= 4 && dif.length >= 3) {
    const media = (por.voto + dif[0] + dif[1] + dif[2]) / 4;
    for (const [s, b] of SOGLIE) if (media >= s) { mod = b; break; }
  }
  return { tot: tot + mod, fp: tot, mod, vuoti, cambi };
}

(async () => {
  const out = [];
  for (const lega of ['bf', 'qi']) {
    for (const regime of ['con', 'senza']) {
      const base = JSON.parse(fs.readFileSync(path.join(REPO, lega === 'bf' ? 'dati/base.json' : 'dati/qi/base.json'), 'utf8'));
      for (const gg of base.g) {
        const sa = gg[1];
        const voti = JSON.parse(fs.readFileSync(path.join(REPO, 'dati/voti.json'), 'utf8')).giornate;
        if (!voti[String(sa)] || !STOR[String(sa)]) continue;
        const storPre = Object.fromEntries(Object.entries(STOR).filter(([k]) => Number(k) < sa));
        const dati = { 'titolari-storico.json': { giornate: process.env.INS ? STOR : storPre, aggiornato: 'x' } };
        const s = STOR[String(sa)];
        dati['titolari.json'] = regime === 'con' ? { aggiornato: 'x', giornata: sa, squadre: s.squadre, titolari: s.t, panchina: s.p, indisponibili: {} } : null;
        const app = await avvia(lega, dati);
        if (process.env.INS) app.ev('{const o = qEntra; qEntra = (p, s, sa) => o(p, s, 7);}');
        const g = app.ev('D.g').find(x => x[1] === sa);
        const squadre = [...new Set(app.ev('players').map(p => p.team))].filter(Boolean);
        for (const team of squadre) {
          const ids = new Set(app.ev('players').filter(p => p.team === team).map(p => p.id));
          app.ev(`mia = players.filter(p=>p.team===${JSON.stringify(team)})`);
          const cons = app.ev('moduloConsigliato')(g);
          const r = { lega, regime, sa, team, cons };
          for (const m of ['4-3-3', '4-4-2', '4-5-1', '3-5-2', '3-4-3', '5-3-2', '5-4-1']) {
            app.ev(`modulo = ${JSON.stringify(m)}`);   // il consiglio dell'app lavora col modulo scelto
            const u = app.ev('undiciDi')(app.ev('mia'), g, m);
            r[m] = punteggioReale(app, ids, u, g, sa).tot;
            r['att' + m] = app.ev('totaleModulo')(g, m).tot;
          }
          r.reale = r[cons];
          out.push(r);
        }
      }
    }
  }
  fs.writeFileSync(process.argv[3] || path.join(require('os').tmpdir(), 'backtest.json'), JSON.stringify(out));
  const agg = {};
  out.forEach(r => { const k = r.lega + '/' + r.regime; (agg[k] = agg[k] || []).push(r); });
  for (const [k, v] of Object.entries(agg)) {
    const m = a => a.reduce((s, x) => s + x, 0) / a.length;
    console.log(k, 'n=' + v.length, 'consigliato=' + m(v.map(r => r.reale)).toFixed(2),
      ['4-3-3', '4-4-2', '4-5-1', '3-5-2', '3-4-3', '5-3-2', '5-4-1'].map(x => x + ':' + m(v.map(r => r[x])).toFixed(1)).join(' '));
  }
})().catch(e => { console.error(e); process.exit(1); });
