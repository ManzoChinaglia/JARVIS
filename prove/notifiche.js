// Prova di scripts/notifiche.js con un ntfy finto e dati controllati.
// Uso: node prove/notifiche.js
process.env.TZ = 'Europe/Rome';
const fs = require('fs'), os = require('os'), path = require('path');
const REPO = process.argv[2] || path.join(__dirname, '..');
const { main, MASSIMO } = require(path.join(REPO, 'scripts', 'notifiche.js'));

let esiti = 0, falliti = 0;
function verifica(nome, cond, dettaglio) {
  esiti++;
  if (!cond) falliti++;
  console.log((cond ? '  ok   ' : '  NO   ') + nome + (dettaglio !== undefined ? '  →  ' + dettaglio : ''));
}

const base = JSON.parse(fs.readFileSync(path.join(REPO, 'dati', 'base.json'), 'utf8'));
const orari = JSON.parse(fs.readFileSync(path.join(REPO, 'dati', 'orari.json'), 'utf8'));
const miei = base.p.filter(a => a[4] === base.me);
const venerdi = new Date('2026-09-18T10:00:00+02:00').getTime();   // scadenza alle 20:30
const fuori = (quanti) => {
  const indisponibili = {};
  miei.slice(0, quanti).forEach(a => { indisponibili[a[0]] = { motivo: 'Infortunato' }; });
  return { aggiornato: '2026-09-18T07:00:00+00:00', giornata: 5, squadre: [], titolari: {}, panchina: {}, indisponibili };
};
const dati = q => ({ 'titolari.json': fuori(q), 'infortuni.json': null, 'squadre.json': null, 'statistiche.json': null,
                     'orari.json': { ...orari, aggiornato: '2026-09-18T07:00:00+00:00' } });
function ntfyFinto(ok = true) {
  const inviati = [];
  const invia = async (url, opz) => { inviati.push({ url, ...JSON.parse(opz.body) }); return { ok, status: ok ? 200 : 500 }; };
  return { inviati, invia };
}

(async () => {
  const cartella = fs.mkdtempSync(path.join(os.tmpdir(), 'notifiche-'));
  const registro = path.join(cartella, 'notifiche.json');

  console.log('\n1. Argomento non impostato');
  let n = ntfyFinto();
  let r = await main({ argomento: '', invia: n.invia, adesso: venerdi, registro, dati: dati(1) });
  verifica('non invia niente', n.inviati.length === 0 && r.nuovi.length > 0, r.nuovi.length + ' avvisi in attesa');
  verifica('e non segna niente', !fs.existsSync(registro));

  console.log('\n2. Primo giro con l\'argomento');
  n = ntfyFinto();
  r = await main({ argomento: 'argomento-di-prova', invia: n.invia, adesso: venerdi, registro, dati: dati(1) });
  verifica('invia gli avvisi a ntfy.sh con l\'argomento', n.inviati.length === r.nuovi.length && n.inviati.every(x => x.url === 'https://ntfy.sh/'
           && x.topic === 'argomento-di-prova'), n.inviati.map(x => x.title).join(' | '));
  const scad = n.inviati.find(x => /^Formazione entro/.test(x.title));
  verifica('scadenza del giorno con priorità alta', scad && scad.priority === 4 && scad.click === 'https://manzochinaglia.github.io/JARVIS/');
  verifica('tuo giocatore fuori', n.inviati.some(x => x.title === miei[0][1] + ' non gioca'));
  const reg = JSON.parse(fs.readFileSync(registro, 'utf8'));
  verifica('registro con i soli codici, senza argomento', reg.inviati.length === n.inviati.length && !JSON.stringify(reg).includes('argomento-di-prova'));

  console.log('\n3. Giro successivo');
  n = ntfyFinto();
  r = await main({ argomento: 'argomento-di-prova', invia: n.invia, adesso: venerdi + 3600000, registro, dati: dati(1) });
  verifica('niente doppioni', n.inviati.length === 0, r.nuovi.length + ' nuovi');
  n = ntfyFinto();
  await main({ argomento: 'argomento-di-prova', invia: n.invia, adesso: new Date('2026-09-18T18:30:00+02:00').getTime(), registro, dati: dati(1) });
  verifica('sotto le 3 ore arriva l\'ultima chiamata', n.inviati.some(x => /^Ultima chiamata/.test(x.title)), n.inviati.map(x => x.title).join(' | '));

  console.log('\n4. Limiti ed errori');
  fs.rmSync(registro, { force: true });
  n = ntfyFinto();
  await main({ argomento: 'argomento-di-prova', invia: n.invia, adesso: venerdi, registro, dati: dati(10) });
  verifica(`mai più di ${MASSIMO} per giro`, n.inviati.length === MASSIMO, n.inviati.length);
  fs.rmSync(registro, { force: true });
  n = ntfyFinto(false);
  r = await main({ argomento: 'argomento-di-prova', invia: n.invia, adesso: venerdi, registro, dati: dati(1) });
  verifica('ntfy non risponde: niente segnato, si riprova', r.inviati.length === 0 && !fs.existsSync(registro));
  r = await main({ argomento: 'argomento-di-prova', invia: async () => { throw new Error('rete assente'); }, adesso: venerdi, registro, dati: dati(1) });
  verifica('rete assente: nessun errore, si riprova', r.inviati.length === 0);

  fs.rmSync(cartella, { recursive: true, force: true });
  console.log('\n' + (esiti - falliti) + '/' + esiti + ' verifiche superate');
  process.exit(falliti ? 1 : 0);
})().catch(e => { console.error('ERRORE', e); process.exit(2); });
