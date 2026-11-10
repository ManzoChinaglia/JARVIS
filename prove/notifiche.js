// Prova di scripts/notifiche.js con un Web Push finto e dati controllati.
// Uso: node prove/notifiche.js
process.env.TZ = 'Europe/Rome';
const fs = require('fs'), os = require('os'), path = require('path');
const REPO = process.argv[2] || path.join(__dirname, '..');
const { main, MASSIMO, opzioniPush, chiavePubblica } = require(path.join(REPO, 'scripts', 'notifiche.js'));

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
const iscr = e => JSON.stringify({ endpoint: 'https://web.push.apple.com/' + e, expirationTime: null,
                                   keys: { p256dh: 'chiave-p256dh', auth: 'chiave-auth' } });
function pushFinto(errore) {
  const spediti = [];
  const spedisci = async (sub, m, chiavi) => {
    if (errore === 'rete') throw new Error('rete assente');
    if (errore) { const e = new Error('rifiutata'); e.statusCode = errore; throw e; }
    spediti.push({ sub, ...m, chiavi });
  };
  return { spediti, spedisci };
}
/* esegue main() raccogliendo le righe di log */
async function conLog(opzioni) {
  const righe = [], vero = console.log;
  console.log = (...a) => righe.push(a.join(' '));
  try { return { r: await main(opzioni), righe }; } finally { console.log = vero; }
}

(async () => {
  const cartella = fs.mkdtempSync(path.join(os.tmpdir(), 'notifiche-'));
  const registro = path.join(cartella, 'notifiche.json');
  const canali = (p, altro = {}) => ({ iscrizione: iscr('uno'), chiave: 'chiave-privata', spedisci: p.spedisci, registro, ...altro });

  console.log('\n1. Notifiche di Jarvis non attive');
  let p = pushFinto();
  let r = await main({ ...canali(p, { iscrizione: '' }), adesso: venerdi, dati: dati(1) });
  verifica('senza iscrizione non invia niente', p.spediti.length === 0 && r.nuovi.length > 0, r.nuovi.length + ' avvisi in attesa');
  verifica('e non segna niente', !fs.existsSync(registro));
  r = await main({ ...canali(p, { chiave: '' }), adesso: venerdi, dati: dati(1) });
  verifica('senza chiave privata: non invia e non segna', p.spediti.length === 0 && !fs.existsSync(registro));
  r = await main({ ...canali(p, { iscrizione: 'incollata male' }), adesso: venerdi, dati: dati(1) });
  verifica('iscrizione incollata male: non invia e non segna', p.spediti.length === 0 && r.inviati.length === 0 && !fs.existsSync(registro));

  console.log('\n2. Primo giro con l\'iscrizione');
  p = pushFinto();
  r = await main({ ...canali(p), adesso: venerdi, dati: dati(1) });
  verifica('invia gli avvisi da Jarvis', p.spediti.length > 0 && p.spediti.length === r.nuovi.length && r.daJarvis === p.spediti.length,
           p.spediti.map(x => x.titolo).join(' | '));
  verifica('chiave pubblica presa dall\'app, privata dai Secrets', p.spediti.every(x => x.chiavi.chiave === 'chiave-privata'
           && /^B[A-Za-z0-9_-]{86}$/.test(x.chiavi.pubblica) && x.sub.endpoint.endsWith('/uno')));
  const scad = p.spediti.find(x => /^Formazione entro/.test(x.titolo));
  verifica('scadenza del giorno con livello urgente', scad && scad.livello === 'urgente');
  verifica('tuo giocatore fuori', p.spediti.some(x => x.titolo === miei[0][1] + ' non gioca'));
  const testoReg = fs.readFileSync(registro, 'utf8');
  verifica('registro con i soli codici, senza segreti', JSON.parse(testoReg).inviati.length === p.spediti.length
           && !/chiave-privata|web\.push\.apple\.com|chiave-auth/.test(testoReg));

  console.log('\n3. Giro successivo');
  p = pushFinto();
  r = await main({ ...canali(p), adesso: venerdi + 3600000, dati: dati(1) });
  verifica('niente doppioni', p.spediti.length === 0, r.nuovi.length + ' nuovi');
  p = pushFinto();
  await main({ ...canali(p), adesso: new Date('2026-09-18T18:30:00+02:00').getTime(), dati: dati(1) });
  verifica('sotto le 3 ore arriva l\'ultima chiamata', p.spediti.some(x => /^Ultima chiamata/.test(x.titolo)), p.spediti.map(x => x.titolo).join(' | '));

  console.log('\n4. Limiti ed errori');
  fs.rmSync(registro, { force: true });
  p = pushFinto();
  await main({ ...canali(p), adesso: venerdi, dati: dati(10) });
  verifica(`mai più di ${MASSIMO} per giro`, p.spediti.length === MASSIMO, p.spediti.length);
  fs.rmSync(registro, { force: true });
  p = pushFinto(500);
  r = await main({ ...canali(p), adesso: venerdi, dati: dati(1) });
  verifica('errore del servizio: niente segnato, si riprova al giro dopo', r.inviati.length === 0 && r.nuovi.length > 0 && !fs.existsSync(registro));
  const { righe } = await conLog({ ...canali(p), adesso: venerdi, dati: dati(1) });
  verifica('il log dice che si riprova, senza altri canali', righe.some(x => /riprovo al prossimo giro/.test(x)) && righe.every(x => /^\[notifiche\] /.test(x)), righe[0]);
  p = pushFinto('rete');
  r = await main({ ...canali(p), adesso: venerdi, dati: dati(1) });
  verifica('rete assente: nessun errore, niente segnato, si riprova', r.inviati.length === 0 && !fs.existsSync(registro));

  console.log('\n5. Iscrizione chiusa dall\'iPhone');
  fs.rmSync(registro, { force: true });
  p = pushFinto(410);
  const chiusa = await conLog({ ...canali(p), adesso: venerdi, dati: dati(1) });
  const avviso = chiusa.righe.filter(x => x.startsWith('::warning::'));
  verifica('410: nessun invio e nessun avviso segnato', chiusa.r.inviati.length === 0 && chiusa.r.nuovi.length > 0
           && JSON.parse(fs.readFileSync(registro, 'utf8')).inviati.length === 0);
  verifica('una sola riga di annotazione per GitHub Actions', avviso.length === 1 && /Secret PUSH_ISCRIZIONE/.test(avviso[0]) && chiusa.righe.length === 2, chiusa.righe.length + ' righe');
  const testoScad = fs.readFileSync(registro, 'utf8');
  verifica('nel registro solo un\'impronta dell\'iscrizione', /"push_scaduta":"[0-9a-f]{12}"/.test(testoScad) && !/web\.push/.test(testoScad));
  fs.rmSync(registro, { force: true });
  r = await main({ ...canali(pushFinto(404)), adesso: venerdi, dati: dati(1) });
  verifica('anche con 404 l\'iscrizione si segna scaduta', /"push_scaduta"/.test(fs.readFileSync(registro, 'utf8')) && r.inviati.length === 0);
  fs.rmSync(registro, { force: true });
  await main({ ...canali(pushFinto(410)), adesso: venerdi, dati: dati(1) });
  let chiamate = 0;
  const conta = { spedisci: async () => { chiamate++; } };
  const dopo = await conLog({ ...canali(conta), adesso: new Date('2026-09-18T18:30:00+02:00').getTime(), dati: dati(1) });
  verifica('la stessa iscrizione non si riprova: niente invio, niente segnato, «nessun canale»', chiamate === 0 && dopo.r.inviati.length === 0
           && dopo.r.nuovi.length > 0 && dopo.righe.some(x => /nessun canale impostato/.test(x)) && !dopo.righe.some(x => x.startsWith('::warning::')));
  r = await main({ ...canali(conta, { iscrizione: iscr('due') }), prova: true,
                   adesso: new Date('2026-09-18T18:40:00+02:00').getTime(), dati: dati(1) });
  verifica('iscrizione nuova: si torna a Jarvis', chiamate > 0 && chiamate === r.nuovi.length && r.inviati.length === r.nuovi.length, chiamate + ' invii');
  verifica('notifica di prova su richiesta', r.nuovi[0].titolo === 'Notifica di prova');

  console.log('\n5bis. Consiglio salvato prima della scadenza');
  fs.rmSync(registro, { force: true });
  const consigli = path.join(cartella, 'consigli.json');
  fs.rmSync(consigli, { force: true });
  p = pushFinto();
  await main({ ...canali(p, { iscrizione: '' }), adesso: venerdi, dati: dati(1) });
  let cs = JSON.parse(fs.readFileSync(consigli, 'utf8'));
  const c1 = cs.giornate && cs.giornate['1'];
  verifica('undici e panchina per ognuno dei sette moduli, anche senza canali di notifica', c1 && c1.sa === 5
           && Object.keys(c1.undici).length === 7 && Object.values(c1.undici).every(u => u.length === 11) && c1.panchina['3-5-2'].length > 0,
           c1 && Object.keys(c1.undici).join(', '));
  /* più leghe: la seconda ha i suoi consigli nella sua cartella e avvisi con prefisso */
  {
    const tmpQ = fs.mkdtempSync(path.join(require('os').tmpdir(), 'jarvis-qi-'));
    fs.mkdirSync(path.join(tmpQ, 'qi'));
    const r = await main({ iscrizione: '', adesso: Date.parse('2026-10-09T10:00:00Z'), registro: path.join(tmpQ, 'notifiche.json'), lega: 'qi' });
    const f = path.join(tmpQ, 'qi', 'consigli.json');
    const cq = fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, 'utf8')) : null;
    const g = cq && Object.values(cq.giornate || {})[0];
    verifica('seconda lega: consigli in dati/qi/, sette moduli, avvisi col prefisso della lega',
             !!g && Object.keys(g.undici).length === 7 && r.nuovi.every(a => a.id.startsWith('qi:') && a.titolo.startsWith('Fantalega QI')),
             g ? Object.keys(g.undici).join(', ') : 'nessun consiglio salvato');
  }
  verifica('con il modello, anche l\'undici del calcolo di prima (per il confronto)',
           !fs.existsSync(path.join(__dirname, '..', 'dati', 'modello.json'))
           || (c1 && c1.undici_vecchio && c1.undici_vecchio['4-3-3'].length === 11 && c1.panchina_vecchio['4-3-3'].length > 0));
  const primaVolta = c1.salvato;
  await main({ ...canali(p, { iscrizione: '' }), adesso: new Date('2026-09-18T21:00:00+02:00').getTime(), dati: dati(1) });
  cs = JSON.parse(fs.readFileSync(consigli, 'utf8'));
  verifica('dopo la scadenza resta l\'ultimo salvato prima', cs.giornate['1'].salvato === primaVolta);

  console.log('\n6. Richiesta vera per il servizio di Apple (con web-push installato)');
  let webpush = null;
  try { webpush = require('web-push'); } catch (e) { console.log('  --   web-push non installato qui: prova saltata (il workflow lo installa)'); }
  if (webpush) {
    const crypto = require('crypto');
    const telefono = crypto.createECDH('prime256v1'); telefono.generateKeys();
    const segreto = crypto.randomBytes(16);
    const sub = { endpoint: 'https://web.push.apple.com/QOprova',
                  keys: { p256dh: telefono.getPublicKey().toString('base64url'), auth: segreto.toString('base64url') } };
    const usaEGetta = webpush.generateVAPIDKeys();   // la chiave privata vera sta solo nei Secrets
    const m = { id: 'x', livello: 'urgente', titolo: 'Prova', testo: 'Ciao da Jarvis' };
    const det = webpush.generateRequestDetails(sub, JSON.stringify(m),
                                               opzioniPush(m, { chiave: usaEGetta.privateKey, pubblica: usaEGetta.publicKey }));
    verifica('richiesta cifrata e firmata come vuole il protocollo', det.endpoint === sub.endpoint
             && det.headers['Content-Encoding'] === 'aes128gcm' && /^vapid t=.+, k=/.test(det.headers.Authorization)
             && det.headers.Urgency === 'high' && det.headers.TTL === 86400, Object.keys(det.headers).join(', '));
    const firma = JSON.parse(Buffer.from(det.headers.Authorization.match(/t=([^,]+)/)[1].split('.')[1], 'base64url').toString());
    verifica('mittente: l\'indirizzo di Jarvis; destinatario: il servizio di Apple',
             firma.sub === 'https://manzochinaglia.github.io/JARVIS/' && firma.aud === 'https://web.push.apple.com', JSON.stringify(firma));
    let chiaro = null;
    try { chiaro = require('http_ece').decrypt(det.body, { version: 'aes128gcm', privateKey: telefono, authSecret: segreto }).toString(); }
    catch (e) { chiaro = 'errore: ' + e.message; }
    verifica('il telefono la decifra e legge titolo e testo', chiaro === JSON.stringify(m), chiaro);
    const valida = (() => { try { const k = crypto.createECDH('prime256v1'); k.generateKeys();
                                  k.computeSecret(Buffer.from(chiavePubblica(), 'base64url')); return true; }
                            catch (e) { return false; } })();
    verifica('la chiave pubblica dell\'app è una chiave P-256 valida', valida);
  }

  fs.rmSync(cartella, { recursive: true, force: true });
  console.log('\n' + (esiti - falliti) + '/' + esiti + ' verifiche superate');
  process.exit(falliti ? 1 : 0);
})().catch(e => { console.error('ERRORE', e); process.exit(2); });
