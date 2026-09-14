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
img/                    icona per la Home (Re Guyzo, dallo stemma), sfondo (lo stemma intero), avvio/ (immagini d'avvio)
manifest.webmanifest    nome, colori e icone dell'app per iPhone e browser
sw.js                   service worker: l'app funziona anche senza rete, con l'ultima copia
dati/base.json          rose, calendario lega, calendario Serie A, statistiche
dati/infortuni.json     aggiornato automaticamente
dati/titolari.json      aggiornato automaticamente: probabili della prossima giornata, in percentuale
dati/orari.json         aggiornato automaticamente: primo e ultimo calcio d'inizio di ogni giornata
dati/squadre.json       aggiornato automaticamente: rendimento casa/fuori, quest'anno e l'anno scorso
dati/jarvis.ics         generato dallo script: calendario da sottoscrivere sull'iPhone
dati/statistiche.json   aggiornato automaticamente: partite, MV, FM e quotazioni dalle pagine pubbliche
dati/listone.json       elenco ufficiale, usato dagli script
scripts/aggiorna.py     scarica infortuni, probabili, orari, rendimento delle squadre e statistiche
scripts/importa_rose.py aggiorna le rose di base.json dal file dell'app di Leghe, dopo scambi o mercato
scripts/importa_lega.py classifica della lega in dati/lega.json, dal file di Leghe (routine «dati di lega»)
scripts/notifiche.js    manda sull'iPhone gli avvisi nuovi: da Jarvis (Web Push) o con ntfy (gira nel workflow)
dati/notifiche.json     codici degli avvisi già inviati, per non mandarli due volte
dati/lega.json          classifica della lega (a mano, con la routine «dati di lega»)
archivio/               file delle rose già importati e vecchi file del fantacalcio (solo sul PC, escluso da Git)
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
gennaio). Dopo uno scambio l'utente scarica il file delle rose dal sito di Leghe
Fantacalcio, sul PC (dall'app dell'iPhone non si esporta niente;
«rivoluzione-fantacalcio-rosters-<numero>.xlsx», finisce nella
cartella Download) e dice «rose aggiornate». Si lancia prima
`python scripts/importa_rose.py --prova` (mostra gli scambi senza scrivere),
poi senza `--prova`; poi prove, commit e push come sempre. Il file usato passa
da Download a `archivio/rose` (escluso da Git): la cartella resta pulita e non si
cancella niente. I vecchi file del fantacalcio sono in `archivio/vecchi`.

Il file dell'app ha un blocco per squadra (nome, «costo», 25 giocatori in ordine
P, D, C, A, riga «totale») e **niente Id**: le squadre si riconoscono dai
giocatori in comune con la rosa attuale (almeno 13), perché i nomi possono
cambiare: il 13/09/2026 quattro erano diversi dal calendario di settembre e, su
scelta dell'utente, da allora Jarvis usa i nomi dell'app (`--nomi-app`, per
esempio Dinastia Fontana = ex FC TETTENHAM); i giocatori dal nome, prima
nella rosa attuale, poi nel listone (dove ogni nome è unico). Si accetta anche
`rose.csv`, che ha l'Id. Controlli: 10 squadre da 25 (3/8/8/6), ruoli coerenti,
nessun giocatore in due squadre. Serve `openpyxl` (`pip install openpyxl`), solo
sul PC.

La lega è privata (per renderla pubblica andrebbe rifatta): le rose richiedono il
login, e Claude non fa accessi con la password dell'utente (nemmeno tramite uno
script, nemmeno se cifrata, nemmeno con token o cookie copiati).

**Routine «dati di lega» (dal 14/09/2026, provata):** l'utente scrive «dati di
lega» (o «rose aggiornate»); Claude usa il **Chrome dell'utente** (estensione
Claude in Chrome) dove l'utente è **già collegato** a Leghe: niente password e
niente password salvate; se Leghe chiede l'accesso, lo fa l'utente. Ogni download
va confermato dall'utente. In Leghe solo lettura. Pagine e pulsanti:
- rose: `/rivoluzione-fantacalcio/view/rosters/<id>` → «Esporta XLSX»
  (`rivoluzione-fantacalcio-rosters-<numero>.xlsx`)
- calendario: `/rivoluzione-fantacalcio/calendario` → «SCARICA ORA»
  (`Calendario_Sborra-league.xlsx`)
- classifica: `/rivoluzione-fantacalcio/classifica` → «SCARICA ORA»
  (`Classifica_Sborra-league.xlsx`: Pos, Squadra, G, V, N, P, Gf, Gs, Dr, Pt.,
  Pt. Totali, con i nomi dell'app)

I pulsanti si cliccano sulle coordinate (il clic sul riferimento dell'albero non
scarica). Durante «Esporta XLSX» non fare screenshot per ~15 secondi: il 14/09 la
pagina si è bloccata ed è servita una scheda nuova. Poi `importa_rose.py --prova`
(e senza, se ci sono scambi) e `importa_lega.py`: classifica in `dati/lega.json`,
mostrata nella scheda Lega; il file e il calendario scaricato insieme passano in
`archivio/lega`, con la data nel nome. I crediti rimasti (500 − totale nel file
delle rose) all'utente non interessano: non si mostrano (scelta del 14/09/2026).

**Statistiche e quotazioni non si aggiornano più a mano**: lo script le prende
una volta al giorno dalle pagine pubbliche di fantacalcio.it
(`dati/statistiche.json`, abbinate per Id dal link del giocatore, almeno 400
giocatori per scrivere) e l'app le applica sopra `base.json`. L'esportazione
«Lista calciatori» non serve più (quella del 12/09 era filtrata su 5 squadre).
Dalla stessa pagina arrivano, dal 15/09/2026, gol, gol subiti, rigori parati,
assist, ammonizioni ed espulsioni (in coda a ogni riga di `statistiche.json`):
se cambiano solo quelle colonne si salvano le statistiche principali, senza bonus.

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

## Grafica

- Colori della bandiera del Burkina Faso in `:root` (`--bf-rosso`, `--bf-verde`,
  `--bf-stella`); l'accento dell'app (`--accento`) è il giallo della stella.
  «BURKINA FASO» è rosso sopra e verde sotto, con la stella gialla.
- Il titolo JARVIS è un disegno SVG: le lettere di Barlow Condensed tracciate con
  fonttools, così si vede uguale anche se il font non si carica.
- In fondo alla schermata Giornata «versione del …» (da `document.lastModified`):
  dice se l'iPhone ha l'ultima versione o una copia vecchia.
- Icona per la Home: **Re Guyzo**, il busto dorato in basso nello stemma
  (`img/icona-180.png`, `img/icona-512.png`, `manifest.webmanifest`). La stessa
  immagine è lo stemmino accanto a BURKINA FASO e l'avatar di «Chiedi». iOS non
  aggiorna l'icona da solo: bisogna togliere Jarvis dalla Home e rimetterlo.
- Sfondo: `img/sfondo.jpg`, lo stemma intero adattato allo schermo dell'iPhone
  (1080 × 2340, sopra e sotto la tinta scura della foto). Un velo scuro in CSS
  tiene leggibile il testo; lo sfondo si muove lentissimo.
- **Volti nel repository, che è pubblico** (scelta dell'utente del 14/09/2026,
  che sostituisce quella del 13/09): Re Guyzo si vede, i due ritratti dello
  stemma sono sfocati. La foto originale e l'altra foto restano solo sul PC.
- Le schede sono «vetro» (`--vetro`, con la sfocatura di ciò che sta dietro)
  sopra lo stemma.

## Campo, maglie e schede

Il campo ha le proporzioni di uno vero (68 × 100, `LINEE_CAMPO`) e l'erba a
strisce; i giocatori sono posizionati in percentuale da `posizione()`: portiere
in basso, attacco in alto, terzini, mezzali ed esterni un po' più avanti. Ogni
giocatore è una maglia disegnata in SVG con i colori di casa del suo club
(`MAGLIE` in `index.html`: tinta unita, righe, metà o croce), la fantamedia in
un'etichetta dorata, un pallino (verde titolare, giallo in dubbio, rosso fuori
dalle probabili) e un anello rosso che pulsa per chi rischia. Un club che non è
in `MAGLIE` ha la maglia grigia: quando sale una neopromossa va aggiunto (una
prova lo controlla sui club del calendario).

Toccando un giocatore, in campo o in una lista, sale la sua scheda
(`apriGiocatore`): fantamedia, media voto, quotazione, partite a voto su quelle
della sua squadra, gol e assist (per i portieri gol subiti e rigori parati),
cartellini, punteggio del consiglio, titolarità, partita e avversario, e la data
delle statistiche. Senza i bonus della fonte compare un trattino. Sotto il campo
nessuna scritta «tocca un giocatore»: per l'utente è intuitivo (15/09/2026). Il
modulo si sceglie con tre pulsanti sopra il campo.

## La sfida e gli stemmi

Sotto il campo, «La sfida, sulla carta» (`sfidaDati`, `renderSfida`): il tuo
undici contro il migliore dell'avversario della giornata, calcolato con lo stesso
motore sulle rose (`undiciDi`; per loro il modulo che rende di più, sempre con la
difesa a quattro), reparto per reparto, con la somma dei punteggi del consiglio e
un verdetto «sulla carta». La scheda dice che è una stima di Jarvis, non il
risultato, e che il modificatore difesa non è compreso. Toccando un nome si apre
la scheda del giocatore.

Stemmi (`stemma`): uno scudo per squadra, con Re Guyzo per BURKINA FASO e, per le
altre, le iniziali su un colore tutto suo (`COLORI_SQUADRE`, assegnati in ordine
alfabetico: dieci squadre, dieci colori). Sono nella testata della giornata, nella
sfida, in classifica e nel calendario. Scelti dall'utente il 14/09/2026.

## Orari dei tuoi e formazione da copiare

`orari.json` ha, per ogni giornata con orario ufficiale, anche `partite`:
`[casa, fuori, calcio d'inizio]` in ordine di orario (dal 14/09/2026). L'app lo usa
(`oraPartita`, `oraBreve`) sotto ogni maglia («sab 18:00»), nella scheda del
giocatore e in «Quando giocano i tuoi» (`renderQuando`): la scadenza in cima, poi
le partite dove gioca almeno un tuo giocatore disponibile, in grassetto chi è
nell'undici. Senza orari ufficiali non si mostra niente.

«Copia la formazione» (`testoFormazione`) copia l'undici per reparto e la panchina
numerata nell'ordine di Leghe, da tenere sotto gli occhi mentre la si inserisce:
Leghe non riceve formazioni da altre app, e sull'iPhone un'app web non può
compilarne un'altra. Senza appunti disponibili si apre la condivisione.

## Movimento e senza rete

Animazioni con solo CSS e JavaScript (scelta dell'utente, niente framework):
le linee del campo si tracciano e le maglie cadono in campo dal portiere
all'attacco (solo quando l'undici cambia: il campo si ridisegna solo se qualcosa
è cambiato e, finita l'entrata, la classe `entra` si toglie), barra del tempo
sotto il conto alla rovescia (verde, gialla nell'ultimo giorno, rossa nelle
ultime 3 ore) con un riflesso che scorre, il numero che scatta quando cambia,
stella che brilla, sfondo che respira, campanella che suona con avvisi nuovi,
cursori che scorrono (barra in basso e modulo), pannelli che salgono dal basso,
blocchi che salgono uno dopo l'altro cambiando scheda, barre che crescono,
segnaposto che luccicano durante il caricamento. Con «Riduci movimento»
dell'iPhone si spengono tutte. «Tira giù per aggiornare» è stato tolto il
15/09/2026 (all'utente disturbava): i dati si aggiornano da soli all'apertura, al
ritorno della rete e tornando nell'app dopo mezz'ora; a mano, dalla campanella.

Gesti da iPhone (14/09/2026): i pannelli si chiudono trascinandoli in giù
(`trascinaPerChiudere`); scorrendo a destra o a sinistra si cambia scheda (non dal
bordo, che su iPhone serve per tornare indietro, e non sul campo), e i contenuti
entrano dal lato verso cui ci si sposta (`data-verso`). All'apertura `#avvio`
ripete l'immagine d'avvio dell'iPhone (`img/avvio/`, una per schermo, con i
`media` in `index.html`, ridotte a 256 colori) e sfuma quando i dati sono pronti.
L'iPhone prende le immagini d'avvio solo aggiungendo di nuovo l'app alla Home.

`sw.js` è il service worker: **prima la rete, poi la copia salvata**. Con la rete
pagina e dati sono sempre freschi (mai una versione vecchia); senza rete si usa
l'ultima copia e l'intestazione scrive «senza rete». Se si cambia la lista dei
file fissi, cambiare anche il nome della cache (ora `jarvis-2`, poi `jarvis-3`).

## Avvisi e notifiche

Gli avvisi si aprono dalla **campanella in alto a destra**, con il pallino rosso
dei nuovi (fino al 14/09/2026 erano la quinta scheda in basso, che sull'iPhone
finiva fuori schermo). Sale un pannello: in cima lo stato dei dati e il pulsante
«Aggiorna i dati», poi l'elenco, dal più urgente: scadenza (3 giorni prima, sotto le 24 ore, «ultima chiamata» sotto le
3 ore), dati fermi, tuoi giocatori che saltano la giornata, probabili uscite,
giocatori dell'undici in panchina o fuori nelle probabili, il martedì il
promemoria per le rose (o le rose ferme da più di 3 settimane). Aperto il
pannello, gli avvisi diventano letti (salvati nel telefono con localStorage).

**Numero sull'icona** (Badging API, per le app della Home con il permesso delle
notifiche): l'app lo imposta al numero di avvisi non letti (`numeroIcona`) e lo
azzera aprendo il pannello; ad app chiusa `sw.js` lo aumenta di uno a ogni
notifica. Il numero condiviso sta nella cache `jarvis-numero`, che il service
worker non cancella quando cambia `CACHE`.

Le **stesse** notifiche arrivano sull'iPhone ad app chiusa: `scripts/notifiche.js`
gira nel workflow dopo lo script dei dati, esegue il codice dell'app sui dati
appena scaricati e invia solo gli avvisi mai inviati (codici in
`dati/notifiche.json`), al massimo 6 per giro. Due canali:

- **notifiche di Jarvis** (Web Push, dal 14/09/2026, scelta dell'utente): arrivano
  con l'icona di Jarvis e **toccandole si apre l'app sulla Home**. Con un link,
  anche da ntfy, l'iPhone apre sempre Safari: un'app della Home si apre solo dalle
  sue notifiche. Si attivano una volta dal pannello Avvisi («Attiva le notifiche»,
  solo dall'icona sulla Home, iOS 16.4 o più recente): l'iPhone dà un'iscrizione
  che l'utente copia nel Secret `PUSH_ISCRIZIONE`. Con le notifiche attive il
  riquadro si nasconde (pannello pulito, scelta dell'utente del 15/09): resta in
  fondo la riga «Non arrivano più?», che lo riapre. La chiave privata VAPID sta solo
  nel Secret `PUSH_CHIAVE` (generata da Claude e data in chat, mai scritta in un
  file); la pubblica è `CHIAVE_PUSH` in `index.html`. Se si rigenerano le chiavi
  cambiano tutte e due e va rifatta l'iscrizione. Il workflow installa `web-push`
  (3.6.7) solo per questo passo; `sw.js` mostra la notifica (`push`) e al tocco
  apre Jarvis (`notificationclick`).
- **ntfy**, di riserva (open source, niente account): se le notifiche di Jarvis
  non sono attive, se un invio fallisce, o se l'iPhone chiude l'iscrizione (404 o
  410: allora arriva anche «Riattiva le notifiche di Jarvis», una volta sola; nel
  registro resta solo un'impronta dell'iscrizione, per riprovare quando cambia).
  L'argomento sta solo nel Secret `NTFY_ARGOMENTO` e nell'app ntfy del telefono.

Argomento, iscrizione e chiave privata **mai nel codice o nei file**. Senza
nessun canale non invia e non segna niente; un errore non fa mai fallire il giro.
Per provare: Actions → *Aggiorna Jarvis* → *Run workflow*, con «Manda anche una
notifica di prova».

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

Il 15/09/2026 l'utente ha deciso di non usare Siri («Jarvis ha tutto»): la guida
è stata tolta dal README. Resta la risposta a una domanda nell'indirizzo
(`?q=...`), innocua e provata da `prove/app.js`: l'app risponde solo dopo aver
caricato i dati, poi toglie `?q=` dall'indirizzo.

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

2. **Parte grafica.** Il piano del 13/09/2026 è completo: nomi delle squadre
   dell'app, titolo disegnato, versione visibile, archivio dei file, colori e
   icona del Burkina Faso, sfondo velato, scheda «Avvisi» con ntfy, animazioni e
   funzionamento senza rete. Il 14/09 il rifacimento chiesto dall'utente: icona
   Re Guyzo, stemma intero sullo sfondo, campanella al posto della quinta scheda,
   campo con le maglie dei club, schede dei giocatori, vetro e animazioni. Altre
   migliorie si concordano con l'utente.

3. **Risultati e forma nella scheda Lega.** La classifica c'è (14/09/2026,
   `importa_lega.py` → `dati/lega.json`, routine «dati di lega», ricordata dal
   promemoria del martedì). Mancano i risultati di ogni giornata e la forma delle
   squadre, dal calendario scaricato insieme. Il file (`Calendario_<lega>.xlsx`)
   ha per ogni partita: squadra, due numeri, squadra, risultato; prima della
   prima giornata (20/09/2026) sono solo 0 e «-», quindi l'import va scritto sul
   primo file vero, senza indovinare le colonne. Può contenere nomi di persone
   (una squadra si chiamava «Francesco e Fabrizio Fontana»): il file resta in
   `archivio/`, nel repository vanno solo i dati, con i nomi dell'app.

## Come si prova

Le prove sono in `prove/` e vanno lanciate prima di ogni consegna:

```
node prove/app.js
python prove/orari.py
python prove/script.py
python prove/rose.py
python prove/lega.py
node prove/notifiche.js
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
