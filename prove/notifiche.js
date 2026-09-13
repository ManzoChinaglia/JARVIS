// Prova di scripts/notifiche.js con un ntfy finto e dati controllati.
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

  console.log('\n5. Notifiche da Jarvis (Web Push)');
  const iscr = e => JSON.stringify({ endpoint: 'https://web.push.apple.com/' + e, expirationTime: null,
                                     keys: { p256dh: 'chiave-p256dh', auth: 'chiave-auth' } });
  function pushFinto(errore) {
    const spediti = [];
    const spedisci = async (sub, m, chiavi) => {
      if (errore) { const e = new Error('rifiutata'); e.statusCode = errore; throw e; }
      spediti.push({ sub, ...m, chiavi });
    };
    return { spediti, spedisci };
  }
  const canali = (p, nt, altro = {}) => ({ argomento: 'argomento-di-prova', iscrizione: iscr('uno'), chiave: 'chiave-privata',
                                           spedisci: p.spedisci, invia: nt.invia, registro, ...altro });
  fs.rmSync(registro, { force: true });
  let p = pushFinto(); n = ntfyFinto();
  r = await main({ ...canali(p, n), adesso: venerdi, dati: dati(1) });
  verifica('con l\'iscrizione arrivano da Jarvis, non da ntfy', p.spediti.length > 0 && p.spediti.length === r.nuovi.length
           && n.inviati.length === 0 && r.daJarvis === p.spediti.length, p.spediti.map(x => x.titolo).join(' | '));
  verifica('chiave pubblica presa dall\'app, privata dai Secrets', p.spediti.every(x => x.chiavi.chiave === 'chiave-privata'
           && /^B[A-Za-z0-9_-]{86}$/.test(x.chiavi.pubblica) && x.sub.endpoint.endsWith('/uno')));
  verifica('registro senza segreti', !/chiave-privata|web\.push\.apple\.com|chiave-auth/.test(fs.readFileSync(registro, 'utf8')));

  fs.rmSync(registro, { force: true });
  p = pushFinto(500); n = ntfyFinto();
  r = await main({ ...canali(p, n), adesso: venerdi, dati: dati(1) });
  verifica('errore del servizio: quegli avvisi arrivano con ntfy', n.inviati.length === r.nuovi.length && r.inviati.length === r.nuovi.length);
  verifica('e al giro dopo si riprova da Jarvis', !JSON.parse(fs.readFileSync(registro, 'utf8')).push_scaduta);

  fs.rmSync(registro, { force: true });
  p = pushFinto(410); n = ntfyFinto();
  r = await main({ ...canali(p, n), adesso: venerdi, dati: dati(1) });
  verifica('iscrizione chiusa dall\'iPhone: avvisi con ntfy e invito a riattivarle', r.inviati.length === r.nuovi.length
           && n.inviati.some(x => x.title === 'Riattiva le notifiche di Jarvis'), n.inviati.map(x => x.title).join(' | '));
  const testoReg = fs.readFileSync(registro, 'utf8');
  verifica('nel registro solo un\'impronta dell\'iscrizione', /"push_scaduta":"[0-9a-f]{12}"/.test(testoReg) && !/web\.push/.test(testoReg));
  let chiamate = 0;
  const conta = { spedisci: async () => { chiamate++; } };
  n = ntfyFinto();
  await main({ ...canali(conta, n), adesso: new Date('2026-09-18T18:30:00+02:00').getTime(), dati: dati(1) });
  verifica('la stessa iscrizione non si riprova e l\'invito non si ripete', chiamate === 0 && n.inviati.length > 0
           && !n.inviati.some(x => /^Riattiva/.test(x.title)), n.inviati.map(x => x.title).join(' | '));
  n = ntfyFinto();
  r = await main({ ...canali(conta, n, { iscrizione: iscr('due') }), prova: true,
                   adesso: new Date('2026-09-18T18:40:00+02:00').getTime(), dati: dati(1) });
  verifica('iscrizione nuova: si torna a Jarvis', chiamate === 1 && n.inviati.length === 0, chiamate + ' da Jarvis, ' + n.inviati.length + ' con ntfy');
  verifica('notifica di prova su richiesta', r.nuovi.length === 1 && r.nuovi[0].titolo === 'Notifica di prova');

  fs.rmSync(registro, { force: true });
  p = pushFinto(); n = ntfyFinto();
  r = await main({ ...canali(p, n, { argomento: '' }), adesso: venerdi, dati: dati(1) });
  verifica('solo Jarvis, senza ntfy: funziona lo stesso', p.spediti.length === r.nuovi.length && fs.existsSync(registro));
  fs.rmSync(registro, { force: true });
  r = await main({ ...canali(p, n, { argomento: '', iscrizione: 'incollata male' }), adesso: venerdi, dati: dati(1) });
  verifica('iscrizione incollata male e niente ntfy: non invia e non segna', r.inviati.length === 0 && !fs.existsSync(registro));

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
