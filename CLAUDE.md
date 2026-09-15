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
font/                   Barlow Condensed in woff2 (600 e 700) e la sua licenza (OFL): da Google Fonts
                        sull'iPhone non si caricava, non reintrodurre dipendenze esterne
img/                    icona per la Home (Re Guyzo, dallo stemma), sfondo (lo stemma intero), avvio/ (immagini d'avvio)
manifest.webmanifest    nome, colori e icone dell'app per iPhone e browser
sw.js                   service worker: l'app funziona anche senza rete, con l'ultima copia
dati/base.json          rose, calendario lega, calendario Serie A, statistiche
dati/infortuni.json     aggiornato automaticamente
dati/titolari.json      aggiornato automaticamente: probabili della prossima giornata, in percentuale
dati/orari.json         aggiornato automaticamente: orario di ogni partita, primo e ultimo calcio d'inizio
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
dati/voti.json          aggiornato automaticamente: voto e fantavoto di ogni giornata di Serie A finita
dati/consigli.json      l'undici consigliato, salvato dal giro automatico prima di ogni scadenza
archivio/               file di rose, calendario e classifica già importati (solo sul PC, escluso da Git)
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
cancella niente. I vecchi file dei primi giorni (`archivio/vecchi`) sono andati nel
Cestino di Windows il 14/09/2026, con l'ok dell'utente.

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
mostrata nella scheda Lega, e — dal 15/09/2026, vedi «Risultati, forma e
tabellone» più sotto — anche i risultati delle giornate già giocate, dallo
stesso calendario. Il file e il calendario scaricato insieme passano in
`archivio/lega`, con la data nel nome. I crediti rimasti (500 − totale nel file
delle rose) all'utente non interessano: non si mostrano (scelta del 14/09/2026).

**Dal telefono, senza PC (dal 14/09/2026):** Chrome sull'iPhone scarica i file di
Leghe (l'app di Leghe no). In Jarvis, scheda Lega → «Importa da Leghe»:
`leggiXlsx` apre lo .xlsx (è uno zip di XML) con `DecompressionStream`, senza
librerie; `classificaDaRighe` fa gli stessi controlli di `importa_lega.py`;
`importaClassifica` salva sul telefono (localStorage `jarvis-lega`, origine
«telefono»). Vale la più recente tra quella del telefono e `dati/lega.json`. Le
rose restano col PC: servono anche alle notifiche, che girano su GitHub. File di
prova con numeri inventati: `prove/dati/classifica-prova.xlsx`.

**Statistiche e quotazioni non si aggiornano più a mano**: lo script le prende
una volta al giorno dalle pagine pubbliche di fantacalcio.it
(`dati/statistiche.json`, abbinate per Id dal link del giocatore, almeno 400
giocatori per scrivere) e l'app le applica sopra `base.json`. L'esportazione
«Lista calciatori» non serve più (quella del 12/09 era filtrata su 5 squadre).
Dalla stessa pagina arrivano, dal 14/09/2026, gol, gol subiti, rigori parati,
assist, ammonizioni ed espulsioni (in coda a ogni riga di `statistiche.json`):
se cambiano solo quelle colonne si salvano le statistiche principali, senza bonus.

## Scadenza formazione

Regola della lega: **un quarto d'ora prima del primo anticipo della giornata di
Serie A**. Gli orari vengono da `dati/orari.json`, che lo script popola dal feed
pubblico di fixturedownload.com. La fonte mette a mezzanotte UTC le partite
senza orario ufficiale: quelle giornate sono salvate come `"ufficiale": false`,
senza orario, e l'app scrive «orario non ancora ufficiale» invece di stimare.
La giornata mostrata passa alla successiva due ore dopo l'ultimo calcio d'inizio.

## Risultati, forma e tabellone

Dal 15/09/2026. La routine «dati di lega» (sopra) legge anche il calendario
scaricato insieme alla classifica: le giornate già giocate finiscono in
`dati/lega.json` → `risultati`, `{"<giornata>": [[casa, fantapunti, fuori,
fantapunti, gol casa, gol fuori], ...]}` (`scripts/importa_lega.py`,
`leggi_calendario` + `risultati_da_calendario`). Un aggiornamento non svuota mai
le giornate già salvate: si legge il `lega.json` esistente e si aggiungono solo
le giornate nuove (upsert). Il calendario può usare nomi diversi da quelli
dell'app per più squadre insieme, non solo una come nella classifica: si
ricavano dalla posizione di ogni partita, confrontata con `dati/base.json`
(`mappa_nomi_calendario`); una squadra nota trovata dove non ci si aspettava è
un errore vero (calendario cambiato), non una ridenominazione. Un calendario non
leggibile non blocca la classifica, che si salva comunque.

**Il formato del «risultato» (i gol) non è mai stato visto su una giornata
vera**: il file scaricato il 14/09/2026, prima dell'inizio stagione
(20/09/2026), ha tutte le partite ancora a «0, 0, -». Si accetta solo un
risultato scritto «N-N»; altrimenti l'import dei risultati si ferma con un
messaggio chiaro invece di indovinare. **Da controllare al primo giro dopo la
prima giornata vera.**

**Forma** (`forma` in `index.html`): gli esiti (V/N/P) delle ultime 5 giornate
di lega già giocate per una squadra, dalla più vecchia alla più recente,
confrontando i fantapunti di quella giornata. In classifica, sotto ogni
squadra, come pallini (verde/giallo/rosso, `.forma .fp`).

**Tabellone**: nella testata della Giornata, il punteggio vero al posto di
«VS» (`renderGiornata`, `risultatoLega(g[0])`), con un festeggiamento se hai
vinto (`.vs-riga.vinta`, animazione `festeggia`) e un colore spento se hai
perso. Resta finché quella resta la giornata mostrata: passata alla giornata
successiva (di solito senza ancora un suo risultato) torna «VS» da solo.

Non ancora fatto: leggere dal Chrome dell'utente la formazione schierata in
ogni giornata, per «La stagione» (lavoro aperto più sotto).

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
nessuna scritta «tocca un giocatore»: per l'utente è intuitivo (14/09/2026). Il
modulo si sceglie con tre pulsanti sopra il campo.

## Rosa

Due viste (la scelta resta sul telefono, `jarvis-rosa-vista`): **maglie** per
reparto, tre per riga, ognuna con colori del club, fantamedia, pallino della
titolarità, avversario e orario; chi è fuori è sbiadito, con il motivo
(`magliaRosa`); oppure **elenco** con i dettagli (titolarità, avversario, barre).
Filtri con il numero di giocatori: Tutti, Disponibili, In dubbio, Fuori
(`statoRosa`: fuori se non disponibile, in dubbio se in panchina, fuori dalle
probabili o sotto il 60%). Toccando maglia o riga sale la scheda del giocatore.
Scelta dell'utente del 15/09/2026.

## La sfida e gli stemmi

Sotto il campo, «La sfida, sulla carta» (`sfidaDati`, `renderSfida`): il tuo
undici contro il migliore dell'avversario della giornata, calcolato con lo stesso
motore sulle rose (`undiciDi`; per loro il modulo che rende di più, sempre con la
difesa a quattro), reparto per reparto, con la somma dei punteggi del consiglio e
un verdetto «sulla carta», e sotto i due moduli. Toccando un nome si apre la scheda
del giocatore.

Stemmi (`stemma`): uno scudo per squadra, con Re Guyzo per BURKINA FASO e, per le
altre, le iniziali su un colore tutto suo (`COLORI_SQUADRE`, assegnati in ordine
alfabetico: dieci squadre, dieci colori). Sono nella testata della giornata, nella
sfida, in classifica e nel calendario. Scelti dall'utente il 14/09/2026.

## Orari dei tuoi

`orari.json` ha, per ogni giornata con orario ufficiale, anche `partite`:
`[casa, fuori, calcio d'inizio]` in ordine di orario (dal 14/09/2026). L'app lo usa
(`oraPartita`, `oraBreve`) sotto ogni maglia («sab 18:00»), nella scheda del
giocatore e in «Quando giocano i tuoi» (`renderQuando`): la scadenza in cima, poi
le partite dove gioca almeno un tuo giocatore disponibile, in grassetto chi è
nell'undici. Senza orari ufficiali non si mostra niente.

«Copia la formazione» è stata tolta il 14/09/2026, lo stesso giorno in cui era
nata: per l'utente è più veloce passare da un'app all'altra, e Leghe non riceve
formazioni da altre app (sull'iPhone un'app web non può compilarne un'altra).

## Voti, com'è andata, calendario dei tuoi, mercato

Dal 15/09/2026 (quattro idee approvate dall'utente, fatte tutte insieme):
- **Voti**: `aggiorna.py` (`voti`, `voti_giornata`) scarica la pagina pubblica dei
  voti di ogni giornata di Serie A finita da almeno 6 ore
  (`/voti-fantacalcio-serie-a/2026-27/N`): per Id, dal link del giocatore, voto e
  fantavoto della redazione Fantacalcio (i primi della riga; seguono altre
  redazioni). Per tre giorni dalla fine si riscarica (i voti si assestano); una
  giornata con meno di 200 voti non si salva; il file si riscrive solo se cambia.
- **Consiglio salvato**: `notifiche.js`, a ogni giro prima della scadenza, salva in
  `dati/consigli.json` undici e panchina della giornata per i tre moduli; dopo la
  scadenza resta quello dell'ultimo giro prima.
- **Com'è andata** (`comeAndata`, in cima alla Giornata): l'ultima giornata con i
  voti, fino alla scadenza della successiva. Nella pagina una riga sola; toccandola,
  in sovraimpressione (`apriComeAndata`): per le giornate di lega in cima il
  risultato vero della tua sfida (`risultatoLega`, da `dati/lega.json` → `risultati`,
  appena l'import del calendario c'è) e, accanto, «con l'undici di Jarvis» nel modulo
  scelto (`puntiUndici`, con la regola della lega: chi non prende voto lascia il
  posto al primo panchinaro dello stesso ruolo) e quanto in più o in meno; poi il
  migliore e il peggiore e tutti i tuoi con voto e bonus o malus (`spiegaVoto`: «voto
  6,5 · +3,5 di bonus»), con il segno «Jarvis» su chi era nell'undici consigliato.
  Prima della lega niente totali (scelta dell'utente: non servono). Il «massimo
  possibile» (`miglioreUndici`) non si mostra più: resta per la verifica dei `PESI`
  (lavoro 1). Per le giornate di lega arriva la notifica «Giornata N: com'è andata».
- **Andamento** (`graficoVoti` nella scheda, `miniLinea` nell'elenco della Rosa):
  fantavoto giornata per giornata; «s.v.» se la sua squadra ha giocato e lui non ha
  preso voto.
- **Calendario dei tuoi** (`prossimi3`, `pallini3`): i prossimi 3 avversari sotto
  ogni maglia della Rosa e nella scheda del giocatore, verde facile, giallo nella
  media, rosso difficile, con lo stesso calcolo dell'avversario nel consiglio
  (`forzaSa`).
- **Mercato, sulla carta** (`mercato`, nella scheda Lega), rifatto il 15/09 perché
  il primo proponeva di prendere senza dare («Dinastia Fontana non mi darebbe mai
  Malen»), e di nuovo lo stesso giorno perché «ragiona troppo per numeri»: deve
  pensare come una persona in un fantacalcio vero («Palle Sudate non mi darà mai
  uno dei suoi due top attaccanti per Hermoso»). Scambi **1 contro 1, anche tra
  ruoli diversi** (regola della lega, confermata dall'utente; niente crediti):
  nessuno cede i pezzi forti (`intoccabili`: i due più quotati di ogni reparto, il
  portiere più quotato, i tre più quotati della rosa); alla pari a vista, perché
  l'altro guarda quotazione e fantamedia (quotazioni entro il 15% o 2 punti, e chi
  dai non ha una fantamedia vera più bassa di oltre 0,5); serve a tutti e due (il
  tuo undici migliora di almeno 0,3, chi dai entra nel loro undici e il loro non
  peggiora). Prima gli scambi di esuberi (chi prendi da loro non giocava). Il valore è per la
  stagione (`valoreStagione`: fantamedia stimata e presenze, `presenze`; niente
  calendario), gli undici con `migliori11` (e, per fare in fretta, `perReparto`,
  `valore11`, `valoreDopo`). Anche **2 contro 2** (scelta dell'utente del 15/09): somme
  delle quotazioni vicine (15% o 3 punti), fantamedia vera media non più bassa di 0,5,
  il tuo undici migliora di almeno 0,5 e di almeno 0,2 più del miglior scambio singolo
  tra quegli stessi giocatori che si potrebbe fare davvero (alla pari e buono anche per
  loro): il 15/09 il confronto con tutti i singoli, anche quelli impossibili, non
  lasciava passare nessun 2 contro 2, mentre spesso il secondo giocatore serve proprio
  a pareggiare le quotazioni. Al massimo 4 singoli e 3 doppi, mai lo stesso giocatore
  chiesto due volte; il risultato si tiene in memoria (`mercatoMemo`) finché non
  cambiano i dati o la giornata. Nella pagina una riga; in sovraimpressione (`apriMercato`) per
  ogni scambio chi dai e chi prendi, «per te» e «per loro», chi entra negli undici e
  la tabella voce per voce (per i 2 contro 2 i due insieme), in due gruppi: «1 contro
  1» e «2 contro 2».
- **La stagione** (`stagione`, riga in cima alla Rosa, `apriStagione`): in cima il
  grafico giornata per giornata dei fantapunti dei tuoi migliori 11 (`graficoStagione`:
  una colonna per giornata, ★ sulla migliore, linea della media), che si tocca per
  aprire sotto la giornata (`scegliGiornata`, `dettaglioGiornata`: totale, «la
  migliore»/«la peggiore», porta, difesa, centrocampo, attacco e gli 11 con voto e
  bonus; frecce per le altre). Poi gol, assist, ammonizioni dei tuoi e «chi produce»,
  i fantapunti di ognuno in tutte le giornate, con media e bonus e malus. Scelta dell'utente: con le formazioni vere
  (lavoro aperto 3) dirà anche chi era schierato e chi ha prodotto il totale vero.

**Sovraimpressione** (15/09/2026, scelta dell'utente, da usare per ogni sezione che
chiede spazio): nella pagina solo una riga-invito (`invito`); toccandola la sezione
si apre a tutto schermo (`apriSovra`, `chiudiSovra`), con l'app sfocata dietro, che
si chiude con la X, trascinando in giù o con Esc. Un giocatore toccato lì apre la sua
scheda sopra. Niente da incastrare nella pagina: più spazio, più chiarezza.

**Niente tutorial** (15/09/2026, scelta dell'utente): «quando mi sono chiare non
servono». Solo scritte con uno scopo (date dei dati, errori, dati che mancano). Tolti
«Come si legge», introduzioni, legenda sotto il campo, note della sfida, «in
grassetto chi è nell'undici», spiegazione dei pallini, istruzioni sotto «Importa da
Leghe», «Si comincia…» in classifica, messaggio iniziale di Chiedi. Non rimetterne.

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
14/09/2026 (all'utente disturbava): i dati si aggiornano da soli all'apertura, al
ritorno della rete e tornando nell'app dopo mezz'ora; a mano, dalla campanella.

Gesti da iPhone (14/09/2026): i pannelli si chiudono trascinandoli in giù
(`trascinaPerChiudere`); scorrendo a destra o a sinistra si cambia scheda (non dal
bordo, che su iPhone serve per tornare indietro, e non sul campo), e i contenuti
entrano dal lato verso cui ci si sposta (`data-verso`). All'apertura `#avvio`
ripete l'immagine d'avvio dell'iPhone (`img/avvio/`, una per schermo, con i
`media` in `index.html`, ridotte a 256 colori) e sfuma quando i dati sono pronti.
L'iPhone prende le immagini d'avvio solo aggiungendo di nuovo l'app alla Home.

Barra in basso in stile **Liquid Glass di iOS 26** (richiesta dell'utente,
14/09/2026): vetro chiaro con riflessi (anche campanella e selettore del modulo);
la «lente» della scheda attiva si trascina col dito da una scheda all'altra
(Pointer Events con `setPointerCapture`) e si allarga mentre la tieni; al rilascio,
o con un tocco semplice, si va alla scheda sotto il dito. La barra resta sempre
grande e fissa: il restringimento scorrendo è stato tolto lo stesso giorno, su
richiesta dell'utente. La rifrazione
vera del vetro sul web non si può fare (Safari non applica filtri SVG allo sfondo):
la lente la imita con sfocatura, saturazione, luminosità e riflessi.

Stesso stile, scelto dall'utente per il resto dell'app: selettore del modulo con
la lente da trascinare (`scegliModulo`), pannelli di vetro staccati dai bordi,
pulsanti di vetro che si illuminano nel punto toccato (`.luce`, `--gx`/`--gy`). Il
vetro va sui controlli che galleggiano, non sui contenuti. L'intestazione a
capsula che si stringeva scorrendo è stata tolta lo stesso giorno (non piaceva):
JARVIS scorre con la pagina.

`sw.js` è il service worker: **prima la rete, poi la copia salvata**. Con la rete
pagina e dati sono sempre freschi (mai una versione vecchia); senza rete si usa
l'ultima copia e l'intestazione scrive «senza rete». Se si cambia la lista dei
file fissi, cambiare anche il nome della cache (ora `jarvis-3`, poi `jarvis-4`).

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
  riquadro si nasconde (pannello pulito, scelta dell'utente del 14/09): resta in
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

Non si usa: il 14/09/2026 l'utente ha deciso di rinunciare a Siri («Jarvis ha
tutto»). La guida del README e la risposta alla domanda nell'indirizzo (`?q=`)
sono state tolte nella pulizia dello stesso giorno.

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

3. **Formazione schierata dal Chrome dell'utente, per «La stagione».** Risultati,
   forma e tabellone sono fatti (15/09/2026: vedi «Risultati, forma e tabellone»
   più sopra) e provati, ma il formato del «risultato» del calendario (i gol) non
   è ancora stato visto su una giornata vera: **da controllare al primo giro dopo
   la prima giornata (20/09/2026)**, con l'import che si ferma da solo se il
   formato non torna. Resta da leggere dal Chrome dell'utente (già collegato a
   Leghe, come per la routine «dati di lega») la **formazione schierata** in ogni
   giornata (pagina delle formazioni di Leghe, da vedere sul primo caso vero), per
   «La stagione»: chi era schierato e chi ha prodotto il totale.

4. **Rivedere con l'utente le quattro funzioni del 15/09** (com'è andata,
   andamento, calendario dei tuoi, mercato): le ha volute tutte insieme per
   guardarle in una volta e dire se «abbiamo esagerato». Niente quinta scheda in
   basso: sull'iPhone finiva fuori schermo.

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
