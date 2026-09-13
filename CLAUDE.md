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
dati/listone.json       elenco ufficiale, usato dagli script
scripts/aggiorna.py     scarica infortuni, probabili, orari e rendimento delle squadre
prove/                  prove automatiche (vedi «Come si prova»)
.github/workflows/aggiorna.yml   esegue lo script martedì 08:00, venerdì 10:00 e sabato 06:00
                                 (ora italiana legale; con l'ora solare un'ora prima)
```

Codice e dati sono separati di proposito. Non reincorporare i dati nell'HTML.

## Identificativi

Ogni giocatore ha l'**Id ufficiale del listone Fantacalcio** (campo `Id`,
es. Svilar = 5841). È la chiave che unisce rose, statistiche, infortuni e
probabili formazioni. Non introdurre altri identificativi: un disallineamento
qui ha già rotto un'app precedente in modo silenzioso.

## Dati che si aggiornano a mano

Una volta a settimana l'utente esporta la «Lista calciatori» da Leghe
Fantacalcio (richiede login, non automatizzabile in modo pulito) e da quella si
rigenera `dati/base.json`. Tutto il resto è automatico.

## Scadenza formazione

Regola della lega: **un quarto d'ora prima del primo anticipo della giornata di
Serie A**. Gli orari vengono da `dati/orari.json`, che lo script popola dal feed
pubblico di fixturedownload.com. La fonte mette a mezzanotte UTC le partite
senza orario ufficiale: quelle giornate sono salvate come `"ufficiale": false`,
senza orario, e l'app scrive «orario non ancora ufficiale» invece di stimare.
La giornata mostrata passa alla successiva due ore dopo l'ultimo calcio d'inizio.

## Calendario

`dati/jarvis.ics` si sottoscrive dall'iPhone con il link nell'app (`webcal://`).
Lo genera lo script a ogni giro:
- una scadenza per ogni giornata di lega con orario ufficiale, 15 minuti prima
  del primo anticipo, con un avviso 2 ore prima (scelta dell'utente)
- il promemoria del martedì alle 9, ora italiana, per esportare la Lista
  calciatori, solo nelle settimane in cui si è giocato

Le giornate senza orario ufficiale non ci sono: arrivano da sole quando la Lega
fissa gli orari. Gli UID sono stabili, così un orario cambiato aggiorna l'evento
invece di duplicarlo. Se non c'è nessuna scadenza il file non si riscrive,
altrimenti l'iPhone cancellerebbe gli eventi. Il file va servito con fine riga
CRLF: `.gitattributes` impedisce a Git di convertirlo.

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

La pagina `/it/consigli-fantacalcio/probabili-formazioni-serie-a` contiene le
formazioni tipo di stagione: serve solo per il modulo abituale, mai per la
titolarità. Fino al 13 settembre 2026 lo script la usava per errore come probabili.

## Consiglio di formazione

Il punteggio parte dalla fantamedia e aggiunge:
- **titolarità**: da −0,4 (fuori dalle probabili) a +1,2 (titolare sicuro), in
  proporzione alla percentuale; zero finché le probabili non escono
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

Il modulo abituale dell'avversario si mostra, ma non entra nel punteggio.

**Da NON fare:** punteggi basati sul duello individuale (tizio marca caio su
quella fascia). Il dato pubblico non dice in modo affidabile chi occupa quale
lato, e il risultato sarebbe una precisione finta.

## Lavori aperti, in ordine di priorità

1. **Verificare i pesi del consiglio.** I pesi della titolarità e
   dell'avversario (`PESI`) sono stime ragionevoli, non tarate. Dopo una decina
   di giornate vanno confrontati con i fantavoti reali e corretti.

2. **Pagina «Chiedi».** Dall'iPhone il microfono non funziona. La pagina va
   snellita e resa utile e reattiva: risposte sulle cose che servono davvero
   prima di schierare.

3. **Parte grafica.** Migliorie da concordare con l'utente, che ne ha già in
   mente alcune. Il font ora è nel repository (`font/`): verificare sull'iPhone
   che il titolo usi davvero Barlow Condensed.

## Come si prova

Le prove sono in `prove/` e vanno lanciate prima di ogni consegna:

```
node prove/app.js
python prove/orari.py
python prove/script.py
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
