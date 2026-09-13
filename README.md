# Jarvis

Assistente per il fantacalcio, stagione 2026/27 — lega *Sborra league*, squadra **BURKINA FASO**.

Applicazione web, pensata per iPhone. Si apre da Safari e si aggiunge alla schermata Home:
da lì funziona a schermo intero, come un'app.

---

## Struttura

```
index.html                    l'app (codice, nessun dato dentro)
font/                         Barlow Condensed e la sua licenza (OFL)
dati/
  base.json                   rose, calendario lega, calendario Serie A, statistiche
  infortuni.json              chi è fuori e fino a quando        [automatico]
  titolari.json               probabili della giornata, in %     [automatico]
  orari.json                  orari delle giornate di Serie A    [automatico]
  squadre.json                rendimento in casa e fuori         [automatico]
  jarvis.ics                  calendario delle scadenze          [automatico]
  statistiche.json            partite, MV, FM, quotazioni        [automatico]
  listone.json                elenco ufficiale, serve agli script
scripts/
  aggiorna.py                 scarica infortuni, probabili, orari, squadre e statistiche
  importa_rose.py             aggiorna le rose da rose.csv, dopo uno scambio
.github/workflows/
  aggiorna.yml                esegue lo script tre volte a settimana
prove/
  app.js                      prova l'app in Node:     node prove/app.js
  orari.py                    prova la logica orari:   python prove/orari.py
  script.py                   prova lo script:         python prove/script.py
  rose.py                     prova l'import delle rose: python prove/rose.py
```

Il codice e i dati sono separati di proposito: si aggiorna l'uno senza toccare l'altro.

---

## Da dove arrivano i dati

| Dato | Fonte | Aggiornamento |
|---|---|---|
| Rose delle 10 squadre | file delle rose dall'app di Leghe Fantacalcio | a ogni scambio |
| Calendario della lega | esportazione da Fantalab | una volta |
| Calendario Serie A | date ufficiali | una volta |
| Statistiche giocatori (PGv, MV, FM) e quotazioni | pagine pubbliche di fantacalcio.it | automatico, 1 volta al giorno |
| Infortunati con data di rientro | pagina pubblica | automatico |
| Probabili formazioni della giornata | pagina pubblica, media di 4 redazioni | automatico |
| Rendimento delle squadre | risultati dal feed fixturedownload.com | automatico |
| Orari delle partite di Serie A | feed pubblico fixturedownload.com | automatico |

La scadenza per schierare la formazione è un quarto d'ora prima del primo anticipo
della giornata. Finché la Lega Serie A non fissa gli orari di una giornata, Jarvis
scrive «orario non ancora ufficiale» invece di stimarla.

L'unico passaggio manuale è scaricare `rose.csv` dopo uno scambio o durante il
mercato: la lega è privata e richiede il login.

---

## Le finestre di aggiornamento

Impostate in `.github/workflows/aggiorna.yml`: **tre giri al giorno**, alle 12:45,
19:45 e 20:45 con l'ora legale (un'ora prima con l'ora solare). Arrivano dopo gli
aggiornamenti delle probabili delle 11:30 e delle 19:30, così prima di ogni
scadenza, anche nei turni infrasettimanali, i dati sono freschi. GitHub può far
partire i giri con qualche minuto di ritardo.

Si può lanciare anche a mano: scheda **Actions** del repository → *Aggiorna Jarvis* → *Run workflow*.

Se una fonte non risponde o cambia struttura, i dati precedenti **restano intatti**:
meglio un dato di tre giorni fa che un file vuoto la domenica mattina.

Se lo script si ferma te ne accorgi in due modi: su GitHub il giro risulta rosso
(e di solito arriva un'email), e nell'app la riga sotto il titolo diventa rossa
quando i dati hanno più di 4 giorni.

---

## Come si aggiorna la formazione consigliata

La difesa è **sempre a quattro**. Il modulo cambia solo nei reparti avanzati
(4-3-3, 4-4-2, 4-5-1) dal selettore sopra il campo.

Il punteggio con cui Jarvis ordina i giocatori parte dalla fantamedia (con poche
partite avvicinata a quella attesa per la quotazione, così un gol fortunato o un
esordio non contano troppo) e tiene conto di:

1. **disponibilità** — chi è infortunato alla data della giornata è escluso
2. **titolarità** — la percentuale media delle quattro redazioni nelle probabili
   della giornata. Finché non escono si stima dalle presenze (partite giocate su
   quelle della squadra), e l'app lo dice
3. **avversario**, nel campo in cui gioca: per portiere e difensori quanti gol
   segna, per centrocampisti e attaccanti quanti ne subisce. Fino alla decima
   giornata i numeri di quest'anno si mescolano con quelli dell'anno scorso;
   per le neopromosse vale la media delle retrocesse, segnata come stima

Sotto ogni giocatore l'app scrive il motivo. Il modulo abituale dell'avversario
si vede, ma non entra nel punteggio.

La panchina è già in ordine: nella lega entra il primo panchinaro dello stesso
ruolo, quindi per ogni ruolo vengono prima quelli che rendono di più.

---

## Scadenze nel calendario dell'iPhone

Nella schermata Giornata, sotto il conto alla rovescia, tocca «Aggiungi le
scadenze al calendario dell'iPhone» e conferma l'iscrizione. Se compare l'opzione
«Rimuovi avvisi», disattivala: altrimenti l'iPhone non ti avvisa 2 ore prima.

Nel calendario trovi la scadenza di ogni giornata con orario ufficiale. Si
aggiorna da solo quando la Lega fissa nuovi orari.

---

## Notifiche sull'iPhone

Gli avvisi della scheda «Avvisi» arrivano anche come notifiche, ad app chiusa,
con l'app gratuita **ntfy** (open source, niente account):

1. Installa **ntfy** dall'App Store, tocca **+** e iscriviti all'argomento che ti
   ha dato Claude (server predefinito, ntfy.sh). Consenti le notifiche.
2. Su GitHub: repository → **Settings** → **Secrets and variables** → **Actions**
   → **New repository secret**, nome `NTFY_ARGOMENTO`, valore l'argomento.

L'argomento funziona come una password: non scriverlo in nessun file del
progetto e non condividerlo. Arrivano al massimo 6 notifiche per giro, mai la
stessa due volte.

---

## Icona sulla Home

L'icona è la bandiera del Burkina Faso con la stella. iOS non aggiorna le icone
da solo: per vederla, tieni premuto Jarvis sulla Home → Rimuovi app → Rimuovi
dalla schermata Home, poi da Safari apri il sito → Condividi → Aggiungi alla
schermata Home. In fondo alla schermata Giornata la riga «versione del …» dice
se l'iPhone sta mostrando l'ultima versione.

---

## La scheda Chiedi

Tocca una delle domande pronte o scrivi, per esempio:

- «chi schiero?» — l'undici in poche righe e i dubbi da controllare
- «chi schiero in difesa?» — chi gioca nel modulo scelto e perché
- «Kamara o Valle?» — chi schierare tra due, con il motivo
- «come sta Baturina?» — anche senza accenti o con parte del cognome
- «chi affronto?», «chi è infortunato?», «aggiorna i dati»

Il microfono dell'app su iPhone può non funzionare: se succede, Jarvis dice il
perché. Il microfono della tastiera funziona sempre.

---

## Chiedere a Jarvis con Siri

Jarvis risponde a una domanda passata nell'indirizzo, per esempio
`https://manzochinaglia.github.io/JARVIS/?q=chi affronto`. Con un Comando Rapido
basta dire «Ehi Siri, Jarvis» e fare la domanda a voce.

1. Apri l'app **Comandi** e tocca **+** in alto a destra.
2. Cerca «detta» e aggiungi l'azione **Detta testo** (*Dictate Text*), lingua italiano.
3. Cerca «codifica» e aggiungi **Codifica URL** (*URL Encode*): deve codificare il testo dettato.
4. Aggiungi l'azione **URL** e scrivi `https://manzochinaglia.github.io/JARVIS/?q=`,
   poi, subito dopo il segno `=`, inserisci la variabile del testo codificato.
5. Aggiungi **Apri URL** (*Open URLs*).
6. Tocca il nome del comando in alto e chiamalo **Jarvis**.

Da quel momento: «Ehi Siri, Jarvis» → «chi schiero in difesa?» → si apre Jarvis
con la risposta nella scheda Chiedi. Il comando apre Jarvis in Safari, non
nell'icona sulla Home: i dati sono gli stessi.

---

## Dopo uno scambio

1. Dall'app di Leghe Fantacalcio scarica il file delle rose
   («rivoluzione-fantacalcio-rosters-….xlsx»): finisce nella cartella Download,
   non serve spostarlo né rinominarlo.
2. Scrivi a Claude «rose aggiornate». Lancia `python scripts/importa_rose.py`,
   che riconosce le squadre anche se nell'app hanno un nome diverso, controlla il
   file (10 squadre da 25, ruoli giusti), aggiorna le rose ed elenca gli scambi
   trovati; poi prove e pubblicazione.
3. Il file usato viene spostato in `archivio/rose`, dentro la cartella del
   progetto: la cartella Download resta pulita.

Statistiche e quotazioni si aggiornano da sole ogni giorno: niente più
esportazione settimanale.
