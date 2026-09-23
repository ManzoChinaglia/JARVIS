# Contesto per Claude Code

Leggi questo file prima di toccare qualsiasi cosa. È la versione **snella** (alleggerita il
23/09/2026): regole, struttura, come si lavora. Il resto sta in file letti solo quando servono:

- **`STATO.md`**: lo stato di oggi (fatto, aperto, cosa vedere nel tempo); da aggiornare a ogni sessione.
- **`STORIA.md`**: il perché delle scelte, le indagini, le idee scartate, le date. **Si legge prima
  di riaprire una questione**; le note storiche nuove, datate, vanno in fondo lì.
- **`RIFERIMENTO.md`**: descrizione tecnica (elenco dei file di `dati/`, dati automatici, app pagina
  per pagina, motore del consiglio, totali delle prove). **Leggilo prima di modificare
  `index.html`, `scripts/` o il motore del consiglio.**
- **`PROCEDURE.md`**: le routine a mano («dati di lega», rose, «formazione schierata»). Si legge
  quando l'utente le chiede o quando le proponi (vedi «Controllo a inizio sessione»).

## Cos'è Jarvis

Assistente personale di fantacalcio per **un solo utente**, stagione 2026/27. Lega a 10
squadre, formato **Classic con modificatore difesa**, 500 crediti, rose da 25 (3 P, 8 D,
8 C, 6 A), asta a ruoli. La squadra dell'utente è **BURKINA FASO**. App web statica su
GitHub Pages (https://manzochinaglia.github.io/JARVIS/), usata **dall'iPhone** (16 Pro,
iOS 26) dalla schermata Home. Nessun backend, nessuna chiave nel codice: il repository è
pubblico.

## Regole non negoziabili

1. **Cinque moduli: 4-3-3, 4-4-2, 4-5-1, 3-5-2, 3-4-3.** Con la difesa a tre la lega
   **non dà il modificatore** (scatta solo con quattro difensori). Difesa a cinque no.
2. **Niente chiavi API né segreti nel codice**: il repository è pubblico.
3. **Nessun dato inventato.** Se una statistica non c'è, si dice che non c'è.
4. **Gli aggiornamenti automatici non svuotano mai i dati**: si scrive solo se il
   risultato passa un controllo di plausibilità, altrimenti restano i dati di prima.
5. **Tutto in italiano**: interfaccia, commenti, messaggi di commit.
6. **Provare prima di consegnare** (le prove sotto, e l'anteprima per ciò che si vede).
7. **Privacy**: nei file pubblici **mai il nome di un'altra squadra** (si scrive «una
   squadra»; le prove ricavano i nomi dai dati, `base['g']`). Lo controlla `prove/privacy.py`.
8. **Grafica**: prima un mockup, poi il codice; l'utente vuole vedere e decidere.
   **Niente tutorial** né scritte di spiegazione: solo scritte con uno scopo (date dei dati,
   errori, dati che mancano).
9. **Leghe e account**: Claude non fa accessi con la password dell'utente (nemmeno via
   script, token o cookie). Su Leghe solo lettura, dal Chrome dove l'utente è già collegato;
   ogni download lo conferma l'utente.

## Decisioni chiuse (non riaprire senza un motivo nuovo; il perché in STORIA.md)

- **Supabase**: scartato (chiave lato client, contro la regola 2; la storia di git non pesa).
- **xG**: niente fonte gratuita e lecita per la Serie A, e non è il dato giusto: si è
  costruito il fantavoto atteso sullo storico (B2).
- **Siri**, **«Chiedi»** (tolta il 21/09), **la voce dell'utente** (B4, tolta il 16/09),
  **«Copia la formazione»**, **«Tira giù per aggiornare»**, **il riquadro della scadenza in
  «Quando giocano i tuoi»**, **il promemoria della Lista calciatori**, **«Importa da Leghe»
  sul telefono** (tolta il 22/09, non serviva più): tolti su richiesta.
- **Aggiornamento automatico dei dati di lega senza conferma**: scartato (23/09/2026): la
  regola 9 vieta accessi a Leghe con token o cookie salvati, e ogni download resta
  confermato dall'utente. A inizio sessione sul PC Claude *propone* «dati di lega» e
  «formazione schierata» se sembra pronta una giornata nuova, non parte da solo.
- **Punteggi sul duello individuale** (chi marca chi): precisione finta, non farli.
- **Crediti rimasti**: all'utente non interessano, non si mostrano.
- **`backdrop-filter`** da alleggerire e **icona da ricomprimere**: valutati, lasciati.
- **B4 «la voce dell'utente»**: fatta e tolta; al suo posto il giudizio «rivelato» (dal
  23/09/2026), che per ora **descrive soltanto** (dettagli in `RIFERIMENTO.md` e `STORIA.md`).

## Il lucchetto (dati della lega cifrati)

Attivo dal 16/09/2026. I dati **della lega** — `base.json` (rose e calendario), `lega.json`
(classifica e risultati), `consigli.json`, `formazioni.json` (la tua formazione schierata) —
nel repository stanno solo chiusi, in `dati/<nome>.chiuso.json`. I dati da fonti pubbliche
restano in chiaro. Cifratura AES-GCM con chiave da password (dettagli in `STORIA.md`).

- **La password** la conosce solo l'utente (≥ 12 caratteri): app Password dell'iPhone,
  Secret `JARVIS_CHIAVE` su GitHub, sul PC `C:\Users\<utente>\.jarvis-chiave` (anche
  `.txt`) o la variabile `JARVIS_CHIAVE`. **Mai in chat, mai nel codice, mai stampata.**
- Copie in chiaro in `.gitignore`. `node scripts/lucchetto.js apri | chiudi | stato |
  inizia`. **Sul PC: dopo `git pull`, `apri`; dopo ogni import della lega, `chiudi` prima
  del commit.** `apri` non sovrascrive un file in chiaro cambiato senza `--forza`.
- `aggiorna.yml` apre all'inizio e richiude prima del salvataggio; `prova.yml` apre prima
  delle prove. Nelle prove e in `notifiche.js` il lucchetto «non c'è» (leggono le copie in
  chiaro). `dati/jarvis.ics` resta in chiaro, senza il nome dell'avversario.
- La derivazione della chiave non si cambia: renderebbe illeggibili i file già chiusi.

## Lavoro da remoto (sessioni cloud) e cassetta delle patch

- Il cloud **legge** GitHub ma **non fa push** (niente credenziali, e un token non si
  chiede in chat). Clona sempre da capo `origin/main`, lavora su `claude-cloud/<data>`,
  consegna con `git format-patch` in **`remoto/patch/`** (fuori da Git) più una nota
  `remoto/patch/CONSEGNA.md` (commit di partenza, patch, totali attesi delle prove, cosa è
  verificato e cosa no). Prova che le patch entrino pulite su un clone fresco.
- **Claude Code sul PC, a ogni inizio sessione, guarda `remoto/patch/`**: se ci sono
  patch, si applicano *prima* di tutto (`git am remoto/patch/*.patch`, in ordine), si
  confrontano i totali, push, poi si svuota la cartella. Su conflitto `git am --abort` e si
  riferisce, senza risolvere a naso.
- **Un solo cantiere per volta sugli stessi file**; in parallelo solo su file diversi.
- **Chi fa cosa lo decide la rete**: dal cloud fantacalcio.it, i feed degli orari e Leghe
  non si raggiungono → tutto ciò che scarica dati veri si fa dal PC. `dati/` non si tocca
  mai da una patch.
- Senza `JARVIS_CHIAVE` il cloud non vede i dati della lega e quasi tutta `prove/app.js`
  non gira: o l'utente mette la variabile nelle impostazioni della sessione cloud (mai in
  chat), o le prove le fa il PC prima del push.
- **Fine riga (CRLF)**: `git status` con tutto modificato e diff simmetrico = solo fine
  riga. Verifica: `git diff --ignore-cr-at-eol --stat` vuoto → `git restore .`. Da fare
  prima di `git am`. `.gitattributes` normalizza a LF (tranne `dati/*.ics`, CRLF per RFC 5545).
- Un `.git/index.lock` lasciato da una sessione cloud lo toglie Claude Code sul PC; dal
  cloud, dentro la cartella collegata, niente comandi git che scrivono.

## Struttura (in breve; elenco completo di `dati/` in RIFERIMENTO.md)

```
index.html              app completa (HTML, CSS, JS in un file solo)
font/  img/             Barlow Condensed woff2 + licenza OFL; icona, sfondo, immagini d'avvio
manifest.webmanifest    nome, colori e icone
sw.js                   service worker: prima la rete, poi la copia salvata
dati/                   dati della lega (chiusi), automatici, storico/, modello.json, lucchetto.json, jarvis.ics
scripts/                aggiorna.py, importa_rose/lega/formazioni.py, notifiche.js, storico.py, modello.py, lucchetto.js
archivio/               file di Leghe già importati, bundle della storia (solo PC, fuori da Git)
prove/                  prove automatiche
.github/workflows/      aggiorna.yml (tre volte al giorno), prova.yml (a ogni push e pull request)
```

Codice e dati separati di proposito: non reincorporare i dati nell'HTML.

**Identificativi**: ogni giocatore ha l'**Id ufficiale del listone Fantacalcio** (es. Svilar =
5841): unisce rose, statistiche, infortuni, probabili, voti e storico. **Non introdurre altri
identificativi.**

## Controllo a inizio sessione (sul PC, non dal cloud)

Guarda l'ultima giornata in `dati/orari.json` con `fine` passata da almeno due ore; se
`dati/lega.json` → `risultati` non ha ancora quella giornata, o `dati/formazioni.json` non ha
ancora la tua formazione di quella giornata, **proponi** «dati di lega» e/o «formazione
schierata» invece di aspettare che le chieda. Resta l'utente a confermare (regola 9): non
partire da soli. Le routine passo passo sono in `PROCEDURE.md`.

## Come si prova

```
node scripts/lucchetto.js apri     # col lucchetto: prima le copie in chiaro
node prove/lucchetto.js
node prove/app.js
python prove/orari.py
python prove/script.py
python prove/rose.py
python prove/lega.py
python prove/formazioni.py
node prove/notifiche.js
python prove/privacy.py
python prove/modello.py
```

Totali attesi e come funziona `prove/app.js`: in `RIFERIMENTO.md`. **Ogni funzione nuova
aggiunge le sue verifiche, e ogni prova passa i propri dati.**

Sul PC: `python` (non `python3`, che è l'alias dello Store), Python 3.14 come il workflow.
Norton intercetta HTTPS: gli script che scaricano si lanciano con `truststore`:

```
python -c "import truststore, runpy; truststore.inject_into_ssl(); runpy.run_path('scripts/aggiorna.py', run_name='__main__')"
```
