// Il lucchetto dei dati della lega (16/09/2026, scelta dell'utente).
//
// Il repository è pubblico: rose, classifica e consigli vi finiscono chiusi a chiave,
// con una password che conosce solo l'utente.
// I dati presi da fonti pubbliche (voti, statistiche, orari…) restano in chiaro.
//
// - dati/lucchetto.json (pubblico): sale, iterazioni e una «prova» cifrata per
//   riconoscere la password giusta. Niente di segreto.
// - per ogni file protetto, dati/<nome>.chiuso.json: AES-GCM a 256 bit, IV casuale, il
//   nome del file come dato associato (un file chiuso non si può spacciare per un altro).
// - la chiave: PBKDF2-SHA256 dalla password (spazi ai lati tolti, NFC), 512 bit: i primi
//   256 per AES. Gli altri servivano alla voce (B4, tolta il 16/09/2026): restano derivati
//   così com'erano, perché cambiare la derivazione cambierebbe la chiave dei file chiusi.
// - le copie in chiaro (dati/base.json…) sono in .gitignore: stanno solo sul PC e nei giri
//   di GitHub, mai nella storia. L'app sul telefono apre le copie chiuse da sé.
//
// La password non sta mai nel codice né in un file del repository: nel Secret
// JARVIS_CHIAVE di GitHub, sul PC nella variabile JARVIS_CHIAVE o nel file
// ~/.jarvis-chiave (fuori dal repository), sul telefono nell'app. Mai stampata.
//
// Uso: node scripts/lucchetto.js stato | apri [--forza] | chiudi | inizia
//   apri    le copie chiuse diventano file in chiaro (dopo git pull, all'inizio dei giri)
//   chiudi  i file in chiaro cambiati si richiudono (prima di ogni commit)
//   inizia  una volta sola: crea dati/lucchetto.json e chiude i file protetti
'use strict';
const fs = require('fs'), os = require('os'), path = require('path');
const { webcrypto } = require('crypto');
const subtle = webcrypto.subtle;

const DATI = path.join(__dirname, '..', 'dati');
const PROTETTI = ['base.json', 'lega.json', 'consigli.json'];
const ITERAZIONI = 600000;          // PBKDF2-SHA256, la soglia raccomandata da OWASP nel 2023
const LUNGHEZZA_MINIMA = 12;        // i file chiusi restano pubblici per sempre: niente password corte
const PROVA = 'jarvis';
const enc = new TextEncoder(), dec = new TextDecoder();
const a64 = u => Buffer.from(u).toString('base64');
const da64 = s => new Uint8Array(Buffer.from(s, 'base64'));
const chiusoDi = n => n.replace(/\.json$/, '.chiuso.json');

async function bitsDa(password, lk) {
  const k = await subtle.importKey('raw', enc.encode(password.trim().normalize('NFC')), 'PBKDF2', false, ['deriveBits']);
  return new Uint8Array(await subtle.deriveBits(
    { name: 'PBKDF2', hash: 'SHA-256', salt: da64(lk.sale), iterations: lk.iterazioni }, k, 512));
}
async function chiaveDaBits(bits) {
  return { aes: await subtle.importKey('raw', bits.slice(0, 32), 'AES-GCM', false, ['encrypt', 'decrypt']) };
}
const chiaveDa = async (password, lk) => chiaveDaBits(await bitsDa(password, lk));

async function chiudi(chiave, nome, testo) {
  const iv = webcrypto.getRandomValues(new Uint8Array(12));
  const dati = await subtle.encrypt({ name: 'AES-GCM', iv, additionalData: enc.encode(nome) }, chiave.aes, enc.encode(testo));
  return JSON.stringify({ lucchetto: 1, iv: a64(iv), dati: a64(new Uint8Array(dati)) });
}
async function apri(chiave, nome, busta) {
  const b = typeof busta === 'string' ? JSON.parse(busta) : busta;
  return dec.decode(await subtle.decrypt({ name: 'AES-GCM', iv: da64(b.iv), additionalData: enc.encode(nome) },
                                         chiave.aes, da64(b.dati)));
}
async function verifica(chiave, lk) {
  try { return await apri(chiave, 'lucchetto', lk.prova) === PROVA; } catch (e) { return false; }
}
async function nuovoLucchetto(password, iterazioni = ITERAZIONI) {
  if (password.trim().length < LUNGHEZZA_MINIMA)
    throw new Error(`password troppo corta: almeno ${LUNGHEZZA_MINIMA} caratteri`);
  const lk = { versione: 1, sale: a64(webcrypto.getRandomValues(new Uint8Array(16))), iterazioni };
  const chiave = await chiaveDa(password, lk);
  lk.prova = JSON.parse(await chiudi(chiave, 'lucchetto', PROVA));
  return { lk, chiave };
}

function leggiLucchetto(dati = DATI) {
  const p = path.join(dati, 'lucchetto.json');
  return fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, 'utf8')) : null;
}
/* la password: dalla variabile d'ambiente (GitHub) o dal file fuori dal repository (PC) */
function password({ env = process.env, casa = os.homedir() } = {}) {
  if (env.JARVIS_CHIAVE) return env.JARVIS_CHIAVE;
  for (const f of ['.jarvis-chiave', '.jarvis-chiave.txt']) {         // il Blocco note può aggiungere .txt
    const p = path.join(casa, f);
    if (fs.existsSync(p)) return fs.readFileSync(p, 'utf8').replace(/^﻿/, '');
  }
  return null;
}
async function chiaveDi(dati, pw) {
  const lk = leggiLucchetto(dati);
  if (!lk) return null;
  const chiave = await chiaveDa(pw, lk);
  if (!await verifica(chiave, lk)) throw new Error('password sbagliata: non apre dati/lucchetto.json');
  return chiave;
}

/* file in chiaro → copie chiuse, solo per quelli cambiati: un file uguale non si riscrive
   (IV nuovo = file diverso = un commit inutile a ogni giro) */
async function chiudiTutti(dati, chiave) {
  const fatti = [];
  for (const n of PROTETTI) {
    const p = path.join(dati, n), c = path.join(dati, chiusoDi(n));
    if (!fs.existsSync(p)) continue;
    const testo = fs.readFileSync(p, 'utf8');
    if (fs.existsSync(c)) {
      try { if (await apri(chiave, n, fs.readFileSync(c, 'utf8')) === testo) continue; } catch (e) {}
    }
    fs.writeFileSync(c, await chiudi(chiave, n, testo) + '\n');
    fatti.push(n);
  }
  return fatti;
}
/* copie chiuse → file in chiaro. Un file in chiaro più recente della sua copia chiusa e
   diverso da lei è lavoro non ancora chiuso (per esempio importa_lega.py sul PC): non si
   sovrascrive, a meno di --forza */
async function apriTutti(dati, chiave, { forza = false } = {}) {
  const fatti = [], fermi = [];
  for (const n of PROTETTI) {
    const p = path.join(dati, n), c = path.join(dati, chiusoDi(n));
    if (!fs.existsSync(c)) continue;
    const testo = await apri(chiave, n, fs.readFileSync(c, 'utf8'));
    if (fs.existsSync(p)) {
      if (fs.readFileSync(p, 'utf8') === testo) continue;
      if (!forza && fs.statSync(p).mtimeMs > fs.statSync(c).mtimeMs) { fermi.push(n); continue; }
    }
    fs.writeFileSync(p, testo);
    fatti.push(n);
  }
  return { fatti, fermi };
}
async function inizia(dati, pw, iterazioni = ITERAZIONI) {
  if (leggiLucchetto(dati)) throw new Error('il lucchetto c\'è già (dati/lucchetto.json)');
  const { lk, chiave } = await nuovoLucchetto(pw, iterazioni);
  fs.writeFileSync(path.join(dati, 'lucchetto.json'), JSON.stringify(lk, null, 1) + '\n');
  return chiudiTutti(dati, chiave);
}

async function principale(cmd, argomenti) {
  const lk = leggiLucchetto(DATI), pw = password();
  if (cmd === 'stato') {
    console.log('[lucchetto] ' + (lk ? 'attivo' : 'non attivo') + ' · password ' +
                (!pw ? 'non trovata' : !lk ? 'trovata' : (await verifica(await chiaveDa(pw, lk), lk)) ? 'giusta' : 'SBAGLIATA'));
    for (const n of PROTETTI)
      console.log(`  ${n}: ${fs.existsSync(path.join(DATI, n)) ? 'in chiaro' : '—'} · ` +
                  (fs.existsSync(path.join(DATI, chiusoDi(n))) ? 'chiuso' : 'non chiuso'));
    return;
  }
  if (!pw) throw new Error('manca la password: variabile JARVIS_CHIAVE o file ~/.jarvis-chiave');
  if (cmd === 'inizia') {
    console.log('[lucchetto] creato; chiusi: ' + (await inizia(DATI, pw)).join(', '));
    return;
  }
  if (!lk) { console.log('[lucchetto] non attivo: niente da fare.'); return; }
  const chiave = await chiaveDi(DATI, pw);
  if (cmd === 'apri') {
    const { fatti, fermi } = await apriTutti(DATI, chiave, { forza: argomenti.includes('--forza') });
    console.log('[lucchetto] aperti: ' + (fatti.join(', ') || 'nessuno (già in chiaro)'));
    if (fermi.length) {
      console.log('[lucchetto] NON aperti, cambiati qui e non ancora chiusi: ' + fermi.join(', ') +
                  ' (prima «chiudi», oppure «apri --forza» per buttare le modifiche)');
      process.exitCode = 1;
    }
  } else if (cmd === 'chiudi') {
    console.log('[lucchetto] chiusi: ' + ((await chiudiTutti(DATI, chiave)).join(', ') || 'nessuno (niente di cambiato)'));
  } else {
    throw new Error('uso: node scripts/lucchetto.js stato | apri [--forza] | chiudi | inizia');
  }
}

if (require.main === module) {
  principale(process.argv[2], process.argv.slice(3)).catch(e => { console.error('[lucchetto] ' + e.message); process.exit(1); });
}
module.exports = { PROTETTI, ITERAZIONI, LUNGHEZZA_MINIMA, chiusoDi, chiaveDa, chiaveDaBits, bitsDa, chiudi, apri,
                   verifica, nuovoLucchetto, leggiLucchetto, password, chiaveDi, chiudiTutti, apriTutti, inizia };
