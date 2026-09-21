# Jarvis

Assistente per il fantacalcio, stagione 2026/27 — lega *Sborra league*, squadra **BURKINA FASO**.

Applicazione web, pensata per iPhone. Si apre da Safari e si aggiunge alla schermata Home:
da lì funziona a schermo intero, come un'app.

---

## Struttura

```
index.html                    l'app (codice, nessun dato dentro)
sw.js                         service worker: l'app funziona anche senza rete
manifest.webmanifest          nome, colori e icone per la Home
font/                         Barlow Condensed (600 e 700) e la sua licenza (OFL)
img/                          icona (Re Guyzo), sfondo (lo stemma), immagini d'avvio
dati/
  base.json                   rose, calendario lega, calendario Serie A, statistiche
  infortuni.json              chi è fuori e fino a quando          [automatico]
  titolari.json               probabili della giornata, in %       [automatico]
  orari.json                  orari di ogni partita di Serie A     [automatico]
  squadre.json                rendimento in casa e fuori           [automatico]
  statistiche.json            partite, MV, FM, bonus, quotazioni   [automatico]
  jarvis.ics                  calendario delle scadenze            [automatico]
  notifiche.json              avvisi già inviati                   [automatico]
  lega.json                   classifica della lega                [«dati di lega»]
  voti.json                   voto e fantavoto di ogni giornata    [automatico]
  consigli.json               undici consigliato prima della scadenza [automatico]
  listone.json                elenco ufficiale, serve agli script
scripts/
  aggiorna.py                 scarica infortuni, probabili, orari, squadre e statistiche
  notifiche.js                manda gli avvisi nuovi sull'iPhone (da Jarvis, ntfy di riserva)
  importa_rose.py             aggiorna le rose dal file di Leghe, dopo uno scambio
  importa_lega.py             aggiorna la classifica dal file di Leghe
.github/workflows/
  aggiorna.yml                esegue script e notifiche tre volte al giorno
prove/
  app.js                      prova l'app in Node:              node prove/app.js
  notifiche.js                prova le notifiche:               node prove/notifiche.js
  orari.py                    prova la logica degli orari:      python prove/orari.py
  script.py                   prova lo script:                  python prove/script.py
  rose.py                     prova l'import delle rose:        python prove/rose.py
  lega.py                     prova l'import della classifica:  python prove/lega.py
  dati/                       file di prova, con numeri inventati
```

Il codice e i dati sono separati di proposito: si aggiorna l'uno senza toccare l'altro.

---

## Da dove arrivano i dati

| Dato | Fonte | Aggiornamento |
|---|---|---|
| Rose delle 10 squadre | file delle rose di Leghe Fantacalcio («dati di lega») | a ogni scambio |
| Classifica della lega | file della classifica di Leghe Fantacalcio | ogni settimana, dal telefono o con «dati di lega» |
| Calendario della lega | esportazione da Fantalab | una volta |
| Calendario Serie A | date ufficiali | una volta |
| Statistiche giocatori (partite, MV, FM, gol, assist, cartellini) e quotazioni | pagine pubbliche di fantacalcio.it | automatico, 1 volta al giorno |
| Voti di ogni giornata | pagine pubbliche di fantacalcio.it | automatico, dopo ogni giornata |
| Infortunati con data di rientro | pagina pubblica | automatico |
| Probabili formazioni della giornata | pagina pubblica, media di 4 redazioni | automatico |
| Rendimento delle squadre | risultati dal feed fixturedownload.com | automatico |
| Orari delle partite di Serie A | feed pubblico fixturedownload.com | automatico |

La scadenza per schierare la formazione è un quarto d'ora prima del primo anticipo
della giornata. Finché la Lega Serie A non fissa gli orari di una giornata, Jarvis
scrive «orario non ancora ufficiale» invece di stimarla.

La lega è privata e richiede il login, quindi rose e classifica non si scaricano da
sole: le prende Claude dal tuo Chrome quando gli scrivi «dati di lega», oppure
importi la classifica dal telefono (vedi «Dati della lega»).

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

Cinque moduli, dalle tessere sopra il campo: 4-3-3, 4-4-2, 4-5-1, 3-5-2 e 3-4-3.
Su ogni tessera il totale atteso dell'undici (fantavoto più modificatore) e
«consigliato» su quello che rende di più. Con la difesa a tre il **modificatore non
scatta** (regola della lega: solo con quattro difensori), e la tessera lo dice: «NO MOD.».

Dal 15/09/2026 il punteggio con cui Jarvis ordina i giocatori è il **fantavoto
atteso** di un modello addestrato su 11 stagioni di voti (`scripts/modello.py`): la
storia del giocatore, la sua quotazione iniziale, il giocare in casa, l'avversario e
la forza della sua squadra, più la titolarità. Nella scheda di ogni giocatore c'è il
valore, quanto balla (±) e il perché. Il modello si usa solo dove, verificato sulle
ultime due stagioni, ordina meglio del calcolo di prima; dove no, resta quello.

Il calcolo di prima parte dalla fantamedia (con poche partite avvicinata a quella
attesa per la quotazione, così un gol fortunato o un esordio non contano troppo) e
tiene conto di:

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

Nel campo ogni giocatore ha la maglia del suo club e la fantamedia; il pallino
dice se è titolare (verde), in dubbio (giallo) o fuori dalle probabili (rosso).
Toccalo, in campo o in una lista, per la sua scheda: fantamedia, partite giocate
su quelle della squadra, gol, assist e il resto.

Sotto il campo, **«La sfida, sulla carta»**: il tuo undici contro il migliore del
tuo avversario, reparto per reparto, con la somma dei punteggi di Jarvis. È una
stima fatta sulle rose, non il risultato.

**Quando giocano i tuoi** mette in ordine le
partite della giornata con i tuoi giocatori, con la scadenza in cima; l'orario c'è
anche sotto ogni maglia e nella scheda del giocatore.

Dopo ogni giornata, fino alla scadenza della prossima, in cima alla Giornata c'è
**Com'è andata**: toccala e si apre a tutto schermo, con l'app sfocata dietro. Dentro:
il risultato vero della tua sfida e quanto avrebbe fatto l'undici di Jarvis, il
migliore e il peggiore, tutti i tuoi con voto e bonus o malus. La scheda
**Stagione** (in basso, tra Rosa e Lega): posizione in classifica, quanto si avvicina
Jarvis al massimo possibile, il grafico giornata per giornata (tocca una colonna per
vederla), gol, assist e ammonizioni della rosa e chi produce di più. Nella scheda di ogni giocatore
c'è l'andamento dei fantavoti e ci sono i prossimi 3 avversari (anche come pallini
sotto le maglie della Rosa). Nella scheda Lega il **Mercato, sulla carta**: scambi 1
contro 1 alla pari, che convengono a te senza togliere niente all'altro. Si chiude
con la X o trascinando in giù.

---

## Scadenze nel calendario dell'iPhone

Nella schermata Giornata, sotto il conto alla rovescia, tocca «Aggiungi le
scadenze al calendario dell'iPhone» e conferma l'iscrizione. Se compare l'opzione
«Rimuovi avvisi», disattivala: altrimenti l'iPhone non ti avvisa 2 ore prima.

Nel calendario trovi la scadenza di ogni giornata con orario ufficiale. Si
aggiorna da solo quando la Lega fissa nuovi orari.

---

## Notifiche sull'iPhone

Gli avvisi (campanella in alto a destra) arrivano anche come notifiche, ad app
chiusa. Meglio da **Jarvis stesso**: hanno la sua icona e toccandole si apre
l'app (un link, invece, sull'iPhone apre sempre Safari).

1. Apri Jarvis **dall'icona sulla Home** → campanella → **Attiva le notifiche** →
   Consenti → **Copia il codice**.
2. Su GitHub: repository → **Settings** → **Secrets and variables** → **Actions**
   → **New repository secret**, nome `PUSH_ISCRIZIONE`, valore il codice copiato.
   Serve anche il Secret `PUSH_CHIAVE`, con la chiave privata che ti ha dato Claude.
3. Prova: **Actions** → *Aggiorna Jarvis* → *Run workflow*, spunta «Manda anche
   una notifica di prova».

Di riserva c'è l'app gratuita **ntfy** (open source, niente account): se le
notifiche di Jarvis non funzionano, gli avvisi arrivano lì. Per attivarla:
installa ntfy, tocca **+** e iscriviti all'argomento che ti ha dato Claude; su
GitHub crea il Secret `NTFY_ARGOMENTO` con lo stesso argomento.

Con le notifiche attive, l'icona di Jarvis sulla Home mostra il numero degli
avvisi non ancora letti; aprendo la campanella si azzera. Il riquadro per
attivarle si nasconde: se un giorno non arrivano più, in fondo al pannello tocca
«Non arrivano più?».

Argomento, codice e chiave funzionano come password: non scriverli in nessun file
del progetto e non condividerli. Arrivano al massimo 6 notifiche per giro, mai la
stessa due volte.

---

## Senza rete

Jarvis si apre anche senza connessione, con gli ultimi dati visti: in quel caso
la riga sotto il titolo comincia con «senza rete». Appena la rete torna, si
aggiorna da solo. I dati si aggiornano anche riaprendo Jarvis dopo mezz'ora; per
aggiornarli a mano: campanella → «Aggiorna i dati».

---

## Icona sulla Home

L'icona è Re Guyzo, il busto dorato dello stemma. iOS non aggiorna le icone
da solo: per vederla, tieni premuto Jarvis sulla Home → Rimuovi app → Rimuovi
dalla schermata Home, poi da Safari apri il sito → Condividi → Aggiungi alla
schermata Home. In fondo alla schermata Giornata la riga «versione del …» dice
se l'iPhone sta mostrando l'ultima versione.

---

## Dati della lega: rose e classifica

Sul PC scrivi a Claude **«dati di lega»** (il martedì Jarvis te lo ricorda).
Claude apre Leghe Fantacalcio nel tuo Chrome, dove sei già collegato, e scarica
rose, calendario e classifica: niente password, e ogni download te lo chiede
prima. Poi aggiorna le rose se ci sono stati scambi (`scripts/importa_rose.py`,
che controlla 10 squadre da 25 con i ruoli giusti) e la classifica della scheda
Lega (`scripts/importa_lega.py`), fa le prove e ti chiede il via per pubblicare.
I file usati finiscono in `archivio/`, dentro la cartella del progetto: la
cartella Download resta pulita.

**Dal telefono, senza PC:** in Chrome sull'iPhone apri Leghe → Classifica →
«Scarica ora», poi in Jarvis scheda **Lega** → **Importa da Leghe** e scegli il
file. La classifica si aggiorna sul telefono; le rose, se hai fatto scambi, le
aggiorna Claude dal PC.

Statistiche e quotazioni si aggiornano da sole ogni giorno: niente più
esportazione settimanale.
