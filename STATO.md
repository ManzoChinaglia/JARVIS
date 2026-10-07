# Stato dei lavori — JARVIS

(al 07/10/2026 sera)

## MULTILEGA — cantiere aperto, URGENTE (prima giornata della nuova lega: 6ª di Serie A, ~10/10/2026)

**Decisioni dell'utente (07/10):** una sola app con selettore di lega; il Burkina abilita anche i moduli
con difesa a 5 (5-3-2, 5-4-1) → ora **7 moduli** per entrambe; oro e liquid glass restano, cambiano
logo/colori di marca (tema bordeaux/blu/oro dallo stemma di BOCA NDUJORS: da decidere insieme, con mockup);
repo pubblico + lucchetto: si resta così (Pages è pubblico anche con repo privato, il lucchetto servirebbe
comunque; da verificare i piani GitHub solo se l'utente lo chiede). Le regole della nuova lega **possono
ancora cambiare** (l'utente è admin per la prima volta; «switch Plus» da lui già disattivato) → tutto in
`dati/leghe.json`, mai nel codice.

**La nuova lega:** Fantalega QI (Leghe, id 886465, slug `fantalega-qi`), competizione «QI VINCE?», 10 squadre,
la squadra dell'utente è **BOCA NDUJORS** (I Piccanti). Classic, 500 crediti, rosa 3/8/8/6, panchina 14 libera,
dalla 6ª alla 38ª di Serie A (33 giornate lega, calendario all'italiana), 3-1-0, nessun fattore campo,
modificatore difesa uguale al Burkina (≥4 difensori, portiere incluso), bonus/malus standard.
**Soglie gol: 66, 72, 76, 80, 84… (+4)** (non più «66 + passo 5»). Stemma: PNG 256×256 (bordeaux/blu/oro,
corona e foglie d'alloro) in `archivio/qi/stemma.png`. Nomi di altre squadre/manager: MAI in file pubblici.

**Fatto (commit locale `6b55825`, NON pushato):**
- `dati/leghe.json` (config pubblica: moduli, soglie_gol, modificatore, cartella, ids Leghe) e `scripts/lega_cfg.py`.
- Prima lega = `dati/` come prima; nuova lega = `dati/qi/` (base.json già creata e **chiusa**: `dati/qi/base.chiuso.json`,
  250 giocatori con Id, calendario 33 giornate). `scripts/crea_lega.py <id>` la rigenera da `archivio/qi/`
  (rosters xlsx, rose-asta.csv per gli Id, calendario.json: letto dalla pagina perché «Scarica ora» non scarica).
- `lucchetto.js`: PROTETTI per ogni cartella di lega (AAD = `qi/base.json`).
- `index.html`: `applicaLega()` (moduli, soglie gol, fasce modificatore, tema `--tema-a/--tema-b/--sfondo`,
  nome squadra, stemma da `LEGA.stemma`), scelta lega da `?lega=` o `localStorage 'jarvis-lega'`, caricamento per cartella,
  7 moduli (tessere 4 per riga: **da vedere su mockup**). `prove/app.js` 327/329 (le 2 rosse c'erano già: date delle prove).
- Fix workflow job falliti (08/10…): checkout `ref: main`, concurrency, conflitto di salvataggio = avviso, non errore (`8d40d0d`, pushato).

**Da fare, in ordine:**
1. Selettore di lega in cima (mockup approvato 23/09: artifact `jarvis_switcher_lega`) che salva `jarvis-lega` e ricarica.
2. Tema/stemma di QI in `leghe.json` (`tema:{a,b,sfondo,simbolo}`, `stemma:"img/stemma-qi.png"` ridotto), con mockup.
3. Verificare l'app con `?lega=qi` (preview) e la grafica dei 7 moduli.
4. Script di import per lega: **delegato al locale** (importa_lega/importa_formazioni/schiera con `--lega`, in
   `~/cantieri-locale/JARVIS-*`, esito non ancora arrivato): controllare con `prove/lega.py` e `prove/formazioni.py`.
5. `aggiorna.py`/`notifiche.js`/`aggiorna.yml`: giro per tutte le leghe (consigli per lega, codici avvisi con la lega).
6. Aggiornare CLAUDE.md (regola 1: moduli a 7, difesa a 5 col modificatore; regola 7 e struttura per più leghe) e RIFERIMENTO.md.
7. Dopo l'ok dell'utente: push (prima `git pull --rebase`, `apri`, prove, `chiudi`).
**Attenzione:** dopo un `git pull` fare SEMPRE `node scripts/lucchetto.js apri` PRIMA di `chiudi`, altrimenti `chiudi`
ricifra copie in chiaro vecchie sopra i file chiusi più nuovi (successo oggi con consigli.chiuso.json, ripristinato).

## Storico recente

**Fatto il 26/09: riquadro «In lega» (Stagione) sistemato.** Le cifre «0V 1N 0P · gol 1-1»
stavano sulla stessa riga dei pallini e finivano sotto il grafico: ora sono una riga a parte,
per esteso («Vinte · pari · perse», «Gol fatti · subiti»). Il grafico dell'andamento compare
dalla seconda giornata (con una sola era un punto e basta) e le etichette 1°/ultimo non si
sovrappongono più alle linee. `prove/app.js` 329/329 (1 nuova).

**Fatto il 22/09:** la freccia dei posti guadagnati o persi in classifica (`movimentoLega`
in `index.html`, confronta con la giornata prima; senza almeno due giornate non compare,
niente inventato). Chiusi anche: lo snellimento delle pagine (l'utente ha visto l'app e va
bene così), il parere dell'utente sulle sezioni (risultato ottimo) e altre migliorie di
grafica non richieste (l'utente le chiede lui quando gli vengono in mente).

**Fatto il 22/09 sera: lo script della formazione schierata.**
`scripts/importa_formazioni.py` legge il testo di una pagina
`.../view/competition/748699/round/<giornata>` (catturato da Claude col Chrome
dell'utente, `get_page_text`) e salva in `dati/formazioni.json` (ora nel lucchetto, come
base/lega/consigli): modulo e Id dei titolari e della panchina della tua sola squadra
(niente voto/fantavoto, già in `dati/voti.json`; niente avversari, non serve scoutarli).
Provato sul testo vero della giornata 1 (Id corretti, verificati a mano) e con
`prove/formazioni.py` (10/10, dalla rosa vera ma con pagine fabbricate: squadra in un
ordine o nell'altro, formazione non ancora inserita, nome sconosciuto, modulo che non
torna con i titolari, senza «Panchina», rosa non di 25). Aggiunto a `PROTETTI` in
`scripts/lucchetto.js` e a `prove/privacy.py`; `dati/formazioni.json` in `.gitignore`.
**Resta da fare**: non è ancora usato da niente (B4, il giudizio «rivelato», è
un'idea, non ancora costruita) — per ora si può richiamare la routine («formazione
schierata») giornata per giornata quando serve. Non ancora automatizzato dentro
`aggiorna.py` (il giro automatico non ha un Chrome collegato a Leghe).

**Fatto il 24/09: «formazione schierata» in un solo giro.** `scripts/schiera.py`:
`--mancanti` elenca le giornate finite e già in `lega.json` senza la tua formazione; `schiera.py N=file ...`
fa apri → import (anche più giornate, recupero dopo un salto) → chiudi → prove, senza
commit. Resta una sola conferma dell'utente per il giro (regola 9 invariata: Chrome suo,
sola lettura). Vedi PROCEDURE.md.

**Fatto il 23/09:** il controllo automatico a inizio sessione sul PC (CLAUDE.md, «Dati a
mano»): Claude propone «dati di lega»/«formazione schierata» quando una giornata sembra
pronta, invece di aspettare che l'utente lo chieda — resta lui a confermare (regola 9,
niente automazione vera: scartata, vedi STORIA.md 23/09). Tolto «Importa da Leghe» sul
telefono (non serviva più): bottone, CSS, funzioni (`leggiXlsx`, `classificaDaRighe`,
`importaClassifica`) e i 10 test che li coprivano in `prove/app.js` — non solo nascosto.
`prove/app.js` ora 306/306 (era 316/316, meno i 10 di quel bottone).

**Fatto il 23/09: il giudizio «rivelato» (B4)**, su mockup approvati dall'utente, dentro
le schermate che c'erano (niente tolto o cambiato, solo aggiunto):
- «Com'è andata»: «Dove non eravate d'accordo» (reparto per reparto, tu | Jarvis, totali)
  ed etichetta «Tu» accanto a «Jarvis» in «Tutti i tuoi».
- Stagione: sotto «Tu, Jarvis e il massimo» il bilancio della stagione (chi ha scelto
  meglio, pallini T/J/=, punti totali, «tutte le tue scelte ›»); blocco nuovo «Il tuo modo
  di scegliere»: fino a 6 giornate con la formazione mostra solo «n di 6», poi reparti,
  moduli e chi tieni anche quando Jarvis no.
- Per ora descrive soltanto: non tocca il consiglio. `prove/app.js` 328/328 (22 nuove).

**Fatto il 23/09 sera: workflow «Aggiorna Jarvis» fallito** per un 404 passeggero della
fonte infortuni (fantacalcio-online.com); `scripts/aggiorna.py` ora fa 3 tentativi (5 s di
pausa) su quel download. Rilancio a mano verde, prove e pagine verdi. Se rifallisce: la
fonte è davvero cambiata, vedere `[infortuni]` nel log.

**Aperto:** niente sul motore. Il giudizio «rivelato» cresce da solo, a patto di importare
la formazione ogni giornata (il controllo a inizio sessione lo ricorda).

**In lista, non prima di fine asta Fantalab:** Jarvis multi-lega. L'utente ha un'asta
nuova in arrivo su una lega a 10 su Fantalab (erano 8 fino al 25/09) (stesse regole di Rivoluzione Fantacalcio:
Classic + modificatore difesa; modificatore gol diverso, stesse 10 squadre). Non un
nuovo Jarvis: la stessa app, un selettore di lega in cima (mockup approvato il
23/09/2026, artifact `jarvis_switcher_lega`) che cambia solo il set di dati caricato
(`dati/base.json` ecc. → equivalenti per l'altra lega); motore e UI restano gli stessi.
Da guardare quando si riprende: se `REGOLE_GOL` va parametrizzato per lega (il
modificatore gol della lega Fantalab è diverso) e come tenere separati i lucchetti/le
chiavi delle due leghe.

**Da vedere nel tempo:** autocalibrazione dei `PESI` (non prima di fine novembre 2026, sui
consigli salvati e «Quanto si avvicina Jarvis»; lì si decide anche se far pesare sul
consiglio «Il tuo modo di scegliere»; da rivedere le sue soglie e frasi con 6+ giornate vere); ogni tanto la verifica in
`dati/modello.json`; fine stagione: la 2026-27 nello storico; rose dopo soste e gennaio.
