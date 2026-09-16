// Prova di scripts/lucchetto.js: cifratura, password, apri e chiudi su una cartella finta.
// Uso: node prove/lucchetto.js
const fs = require('fs'), os = require('os'), path = require('path');
const REPO = process.argv[2] || path.join(__dirname, '..');
const L = require(path.join(REPO, 'scripts', 'lucchetto.js'));

let esiti = 0, falliti = 0;
function verifica(nome, cond, dettaglio) {
  esiti++;
  if (!cond) falliti++;
  console.log((cond ? '  ok   ' : '  NO   ') + nome + (dettaglio !== undefined ? '  →  ' + dettaglio : ''));
}
const fallisce = async f => { try { await f(); return false; } catch (e) { return true; } };
const PW = 'una password di prova lunga', ITER = 1000;     // poche iterazioni: è una prova

(async () => {
  console.log('\n1. Cifrare e aprire');
  const { lk, chiave } = await L.nuovoLucchetto(PW, ITER);
  const testo = JSON.stringify({ me: 'SQUADRA', p: [[1, 'Nome', 'Club', 'D']] });
  const b1 = await L.chiudi(chiave, 'base.json', testo), b2 = await L.chiudi(chiave, 'base.json', testo);
  verifica('si riapre uguale', await L.apri(chiave, 'base.json', b1) === testo);
  verifica('nel file chiuso non si legge niente del contenuto', !/SQUADRA|Nome|Club/.test(b1) && JSON.parse(b1).lucchetto === 1);
  verifica('lo stesso testo chiuso due volte dà due file diversi (IV casuale)', b1 !== b2);
  const altra = (await L.nuovoLucchetto('un\'altra password lunga', ITER)).chiave;
  verifica('con un\'altra chiave non si apre', await fallisce(() => L.apri(altra, 'base.json', b1)));
  verifica('spacciato per un altro file non si apre (nome come dato associato)', await fallisce(() => L.apri(chiave, 'lega.json', b1)));
  const rotto = JSON.parse(b1); rotto.dati = rotto.dati.replace(/^./, c => c === 'A' ? 'B' : 'A');
  verifica('un file manomesso non si apre', await fallisce(() => L.apri(chiave, 'base.json', rotto)));

  console.log('\n2. La password');
  verifica('quella giusta apre la prova del lucchetto', await L.verifica(await L.chiaveDa(PW, lk), lk));
  verifica('quella sbagliata no', !await L.verifica(await L.chiaveDa(PW + 'x', lk), lk));
  verifica('gli spazi ai lati non contano (il telefono può aggiungerne uno)', await L.verifica(await L.chiaveDa('  ' + PW + '\n', lk), lk));
  verifica('niente password corte', await fallisce(() => L.nuovoLucchetto('corta', ITER)));
  verifica('nel lucchetto pubblico né la password né la chiave', !JSON.stringify(lk).includes(PW) && lk.iterazioni === ITER && lk.sale.length > 10);
  const casa = fs.mkdtempSync(path.join(os.tmpdir(), 'casa-'));
  verifica('senza variabile né file: nessuna password', L.password({ env: {}, casa }) === null);
  fs.writeFileSync(path.join(casa, '.jarvis-chiave.txt'), '﻿' + PW + '\r\n');
  verifica('dal file fuori dal repository, anche con .txt e il BOM del Blocco note',
           await L.verifica(await L.chiaveDa(L.password({ env: {}, casa }), lk), lk));
  verifica('la variabile d\'ambiente vince sul file', L.password({ env: { JARVIS_CHIAVE: 'da-github' }, casa }) === 'da-github');

  console.log('\n3. Apri e chiudi su una cartella');
  const dati = fs.mkdtempSync(path.join(os.tmpdir(), 'lucchetto-'));
  fs.writeFileSync(path.join(dati, 'base.json'), testo);
  fs.writeFileSync(path.join(dati, 'lega.json'), '{"classifica":[]}');
  fs.writeFileSync(path.join(dati, 'voti.json'), '{"giornate":{}}');
  const chiusi = await L.inizia(dati, PW, ITER);
  verifica('inizia chiude solo i file protetti che ci sono', chiusi.join() === 'base.json,lega.json'
           && fs.existsSync(path.join(dati, 'base.chiuso.json')) && !fs.existsSync(path.join(dati, 'voti.chiuso.json')), chiusi.join());
  verifica('e non si fa due volte', await fallisce(() => L.inizia(dati, PW, ITER)));
  const ch = await L.chiaveDi(dati, PW);
  verifica('con la password sbagliata la cartella non si apre', await fallisce(() => L.chiaveDi(dati, 'sbagliata ma lunga abbastanza')));
  const c0 = fs.readFileSync(path.join(dati, 'base.chiuso.json'), 'utf8');
  verifica('chiudere senza cambiamenti non riscrive niente', (await L.chiudiTutti(dati, ch)).length === 0
           && fs.readFileSync(path.join(dati, 'base.chiuso.json'), 'utf8') === c0);
  fs.writeFileSync(path.join(dati, 'lega.json'), '{"classifica":[1]}');
  verifica('un file cambiato sì, solo lui', (await L.chiudiTutti(dati, ch)).join() === 'lega.json');
  fs.unlinkSync(path.join(dati, 'base.json'));
  let r = await L.apriTutti(dati, ch);
  verifica('apri rimette i file in chiaro mancanti, uguali', r.fatti.join() === 'base.json'
           && fs.readFileSync(path.join(dati, 'base.json'), 'utf8') === testo, r.fatti.join());
  // una modifica fatta qui dopo l'ultima chiusura (per esempio importa_lega.py) non si butta
  fs.writeFileSync(path.join(dati, 'lega.json'), '{"classifica":[2]}');
  const futuro = new Date(Date.now() + 60000);
  fs.utimesSync(path.join(dati, 'lega.json'), futuro, futuro);
  r = await L.apriTutti(dati, ch);
  verifica('un file in chiaro cambiato e non ancora chiuso non si sovrascrive', r.fermi.join() === 'lega.json'
           && fs.readFileSync(path.join(dati, 'lega.json'), 'utf8') === '{"classifica":[2]}');
  r = await L.apriTutti(dati, ch, { forza: true });
  verifica('con --forza sì', r.fatti.join() === 'lega.json' && fs.readFileSync(path.join(dati, 'lega.json'), 'utf8') === '{"classifica":[1]}');

  console.log('\n' + (esiti - falliti) + '/' + esiti + ' verifiche superate');
  process.exit(falliti ? 1 : 0);
})().catch(e => { console.log('  NO   errore: ' + e.stack); process.exit(1); });
