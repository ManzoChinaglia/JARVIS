# Contesto per Claude Code

Leggi questo file prima di toccare qualsiasi cosa.

## Cos'è Jarvis

Assistente personale di fantacalcio per **un solo utente**, stagione 2026/27.
Lega *Sborra league*, 10 squadre, formato **Classic con modificatore difesa**,
500 crediti, rose da 25 (3 portieri, 8 difensori, 8 centrocampisti, 6 attaccanti).
La squadra dell'utente è **BURKINA FASO**.

Applicazione web statica pubblicata su GitHub Pages, usata **dall'iPhone**,
aggiunta alla schermata Home. Nessun backend, nessuna chiave segreta nel codice:
il repository è pubblico.

Indirizzo: https://manzochinaglia.github.io/JARVIS/

## Regole del progetto, non negoziabili

1. **La difesa è sempre a quattro.** Il modulo cambia solo nei reparti avanzati.
2. **Niente chiavi API nel codice.** Il repository è pubblico: qualunque chiave
   verrebbe trovata e usata a spese dell'utente.
3. **Nessun dato inventato.** Se una statistica non c'è, si dice che non c'è.
   Un consiglio sbagliato dato con sicurezza è peggio di nessun consiglio.
4. **Gli aggiornamenti automatici non devono mai svuotare i dati.**
   `scripts/aggiorna.py` scrive solo se il risultato supera un controllo di
   plausibilità; se la fonte cambia struttura, restano i dati precedenti.
5. **Tutto in italiano**: interfaccia, commenti, messaggi di commit.
6. **Provare prima di consegnare.** Questo progetto nasce dopo due app
   consegnate senza test sufficienti e rivelatesi difettose all'uso reale.

## Struttura

```
index.html              app completa (HTML, CSS, JS in un file solo)
font/                   Barlow Condensed in woff2 e la sua licenza (OFL): da Google Fonts
                        sull'iPhone non si caricava, non reintrodurre dipendenze esterne
dati/base.json          rose, calendario lega, calendario Serie A, statistiche
dati/infortuni.json     aggiornato automaticamente
dati/titolari.json      aggiornato automaticamente: probabili della prossima giornata, in percentuale
dati/orari.json         aggiornato automaticamente: primo e ultimo calcio d'inizio di ogni giornata
dati/squadre.json       aggiornato automaticamente: rendimento casa/fuori, quest'anno e l'anno scorso
dati/jarvis.ics         generato dallo script: calendario da sottoscrivere sull'iPhone
dati/statistiche.json   aggiornato automaticamente: partite, MV, FM e quotazioni dalle pagine pubbliche
dati/listone.json       elenco ufficiale, usato dagli script
scripts/aggiorna.py     scarica infortuni, probabili, orari, rendimento delle squadre e statistiche
scripts/importa_rose.py aggiorna le rose di base.json da rose.csv, dopo scambi o mercato
prove/                  prove automatiche (vedi «Come si prova»)
.github/workflows/aggiorna.yml   esegue lo script tre volte al giorno, dopo gli aggiornamenti
                                 delle probabili delle 11:30 e delle 19:30 (orari nel file)
```

Codice e dati sono separati di proposito. Non reincorporare i dati nell'HTML.

## Identificativi

Ogni giocatore ha l'**Id ufficiale del listone Fantacalcio** (campo `Id`,
es. Svilar = 5841). È la chiave che unisce rose, statistiche, infortuni e
probabili formazioni. Non introdurre altri identificativi: un disallineamento
qui ha già rotto un'app precedente in modo silenzioso.

## Dati che si aggiornano a mano

Solo le **rose**, che cambiano con scambi e mercato (soste per le nazionali,
gennaio). Dopo uno scambio l'utente scarica il file delle rose dall'app di Leghe
Fantacalcio («rivoluzione-fantacalcio-rosters-<numero>.xlsx», finisce nella
cartella Download) e dice «rose aggiornate». Si lancia prima
`python scripts/importa_rose.py --prova` (mostra gli scambi senza scrivere),
poi senza `--prova`; poi prove, commit e push come sempre.

Il file dell'app ha un blocco per squadra (nome, «costo», 25 giocatori in ordine
P, D, C, A, riga «totale») e **niente Id**: le squadre si riconoscono dai
giocatori in comune con la rosa attuale (almeno 13), perché nell'app quattro
squadre hanno un nome diverso dal calendario (AS Quell, Palle Sudate,
FC FRINGUELLI, Dinastia Fontana = FC TETTENHAM); i giocatori dal nome, prima
nella rosa attuale, poi nel listone (dove ogni nome è unico). Si accetta anche
`rose.csv`, che ha l'Id. Controlli: 10 squadre da 25 (3/8/8/6), ruoli coerenti,
nessun giocatore in due squadre. Serve `openpyxl` (`pip install openpyxl`), solo
sul PC.

La lega è privata: le rose richiedono il login, e Claude non fa accessi con la
password dell'utente (nemmeno tramite uno script, nemmeno se cifrata). Se un
giorno la lega diventa visibile a tutti, le rose si possono leggere senza login.

**Statistiche e quotazioni non si aggiornano più a mano**: lo script le prende
una volta al giorno dalle pagine pubbliche di fantacalcio.it
(`dati/statistiche.json`, abbinate per Id dal link del giocatore, almeno 400
giocatori per scrivere) e l'app le applica sopra `base.json`. L'esportazione
«Lista calciatori» non serve più (quella del 12/09 era filtrata su 5 squadre).

## Scadenza formazione

Regola della lega: **un quarto d'ora prima del primo anticipo della giornata di
Serie A**. Gli orari vengono da `dati/orari.json`, che lo script popola dal feed
pubblico di fixturedownload.com. La fonte mette a mezzanotte UTC le partite
senza orario ufficiale: quelle giornate sono salvate come `"ufficiale": false`,
senza orario, e l'app scrive «orario non ancora ufficiale» invece di stimare.
La giornata mostrata passa alla successiva due ore dopo l'ultimo calcio d'inizio.

## Calendario

`dati/jarvis.ics` si sottoscrive dall'iPhone con il link nell'app (`webcal://`).
Lo genera lo script a ogni giro: una scadenza per ogni giornata di lega con
orario ufficiale, 15 minuti prima del primo anticipo, con un avviso 2 ore prima
(scelta dell'utente). Il promemoria settimanale per esportare la Lista calciatori
è stato tolto il 13/09/2026, su richiesta dell'utente: le statistiche ora sono
automatiche.

Le giornate senza orario ufficiale non ci sono: arrivano da sole quando la Lega
fissa gli orari. Gli UID sono stabili, così un orario cambiato aggiorna l'evento
invece di duplicarlo. Se non c'è nessuna scadenza il file non si riscrive,
altrimenti l'iPhone cancellerebbe gli eventi. Il file va servito con fine riga
CRLF: `.gitattributes` impedisce a Git di convertirlo.

## Chiedi

La pagina risponde a: «chi schiero?» (l'undici in poche righe e le cose da
tenere d'occhio), un ruolo (chi gioca nel modulo scelto con il motivo, gli altri
solo per nome), un confronto «A o B?», un giocatore (anche senza accenti o con
parte del cognome; con più omonimi chiede quale), «chi affronto?», «infortunati»,
«aggiorna i dati». Le domande pronte si generano dai dati: una è sempre il
ballottaggio vero in difesa.

Microfono: su scelta dell'utente si usa il riconoscimento vocale del browser,
che su iPhone è poco affidabile, soprattutto dall'icona sulla Home. Ogni errore
ha un messaggio che dice il perché e ricorda la dettatura della tastiera, che
funziona sempre: dal messaggio riportato dall'utente si capisce la causa.

## Dati vecchi

Lo script può fallire senza che nessuno lo veda. Due difese:
- nel workflow il salvataggio ha `if: always()` e lo script non ha più
  `continue-on-error`: i dati buoni si salvano comunque, ma il giro risulta
  rosso su GitHub, che di norma avvisa per email
- nell'app l'intestazione diventa rossa se `orari.json` (riscritto a ogni giro)
  o gli infortuni hanno più di 4 giorni (`GIORNI_VECCHI`)

## Siri

Un Comando Rapido apre l'app con la domanda nell'indirizzo (`?q=...`). L'app
risponde solo dopo aver caricato i dati, poi toglie `?q=` dall'indirizzo. La
guida per creare il comando è nel README; `prove/app.js` verifica la risposta.

## Probabili formazioni

Vengono dalla pagina per giornata di fantacalcio-online
(`/it/serie-a/2026-2027/probabili-formazioni/N-giornata`): per ogni giocatore la
percentuale media di quattro redazioni (Fantacalcio.it, Gazzetta, SOS Fanta, Sky).
Lo script scarica la giornata di Serie A della prossima giornata di lega e salva
in `dati/titolari.json` anche il numero della giornata e le squadre già
pubblicate. L'app usa le percentuali **solo se la giornata coincide** con quella
mostrata; altrimenti scrive «probabili non ancora uscite».

La stessa pagina elenca gli **indisponibili della giornata** (infortunati e
squalificati, a volte con «fino al»), anche giorni prima delle probabili: lo
script li salva in `titolari.json` e scrive il file se ci sono le probabili di
almeno una squadra o almeno 5 indisponibili. La pagina degli infortuni non
riporta gli squalificati. Nell'app chi è indisponibile per la giornata non viene
consigliato, con il motivo.

La pagina `/it/consigli-fantacalcio/probabili-formazioni-serie-a` contiene le
formazioni tipo di stagione: serve solo per il modulo abituale, mai per la
titolarità. Fino al 13 settembre 2026 lo script la usava per errore come probabili.

## Consiglio di formazione

Il punteggio parte dalla **fantamedia stimata** e aggiunge:
- **titolarità**: da −0,4 (fuori dalle probabili) a +1,2 (titolare sicuro), in
  proporzione alla percentuale. Finché le probabili della sua squadra non escono
  si stima dalle presenze (partite giocate su quelle della squadra, «presenze
  3/3»): senza, chi non ha mai giocato entrerebbe nell'undici solo per la
  quotazione
- **avversario, nel campo in cui gioca** (casa e fuori separati): per portiere e
  difensori quanti gol segna, per centrocampisti e attaccanti quanti ne subisce,
  come differenza dalla media del campionato scorso nello stesso campo,
  moltiplicata per `PESI` in `index.html`. Portiere e difensori pesano di più per
  porta inviolata e modificatore difesa.

**Campione piccolo:** a settembre ogni squadra ha giocato 3-4 partite e ogni
statistica di forma è rumore. Il peso di quest'anno cresce in modo lineare fino
alla decima partita giocata; prima si mescola con la stagione precedente. Le
neopromosse non hanno la Serie A dell'anno scorso: si usa la media delle tre
retrocesse, e l'app la segnala come stima. I dati sono in `dati/squadre.json`,
calcolati dai risultati del feed di fixturedownload.com.

**Fantamedia stimata:** con poche partite la fantamedia è rumore, e chi non ha
ancora giocato avrebbe 0. Si parte dalla fantamedia attesa per la quotazione del
listone (una retta per ruolo, ricalcolata a ogni caricamento sulle rose, pesata
per partite giocate; se la pendenza viene negativa vale la media del ruolo) e ci
si avvicina alla fantamedia vera: `(partite·FM + 5·attesa) / (partite + 5)`.
Nelle liste si mostra la fantamedia vera; la scheda del giocatore mostra anche
quella usata per il consiglio.

Il modulo abituale dell'avversario si mostra, ma non entra nel punteggio.

**Panchina:** nella lega, se un titolare non prende voto, entra il primo
panchinaro dello stesso ruolo nell'ordine inserito (regola confermata
dall'utente). `panchina(g)` ordina per ruolo e, dentro il ruolo, per punteggio;
l'app la mostra numerata e «chi schiero?» la riassume.

**Da NON fare:** punteggi basati sul duello individuale (tizio marca caio su
quella fascia). Il dato pubblico non dice in modo affidabile chi occupa quale
lato, e il risultato sarebbe una precisione finta.

## Lavori aperti, in ordine di priorità

1. **Verificare i pesi del consiglio.** I pesi della titolarità e
   dell'avversario (`PESI`) sono stime ragionevoli, non tarate. Dopo una decina
   di giornate vanno confrontati con i fantavoti reali e corretti.

2. **Parte grafica.** Migliorie da concordare con l'utente, che ne ha già in
   mente alcune. Il font ora è nel repository (`font/`): verificare sull'iPhone
   che il titolo usi davvero Barlow Condensed.

## Come si prova

Le prove sono in `prove/` e vanno lanciate prima di ogni consegna:

```
node prove/app.js
python prove/orari.py
python prove/script.py
python prove/rose.py
```

`prove/app.js` segue il metodo usato finora, da mantenere: estrae il blocco
`<script>` da `index.html`, lo esegue in Node con un finto DOM e una `fetch`
che legge i file da disco, e verifica i risultati reali (undici generato,
risposte alle domande, conteggi, scadenze). Ogni nuova funzione aggiunge qui
le sue verifiche. `prove/orari.py` e `prove/script.py` provano lo script con
fonti finte che imitano le pagine vere. Ha già intercettato
un errore sugli identificativi e una funzione cancellata per sbaglio.
Per le date usare un orologio finto e `TZ=Europe/Rome`: la scadenza dipende
dall'ora legale.

Lo script si prova in locale con Python 3.14, la stessa versione del workflow.
Sul PC dell'utente Norton Antivirus intercetta le connessioni HTTPS con un suo
certificato, che Python non riconosce: si lancia con il pacchetto `truststore`,
senza toccare lo script.

```
python -c "import truststore, runpy; truststore.inject_into_ssl(); runpy.run_path('scripts/aggiorna.py', run_name='__main__')"
```
