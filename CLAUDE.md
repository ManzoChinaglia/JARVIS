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

**Supabase, valutato e scartato (15/09/2026, lavoro da remoto).** L'utente ha
chiesto se integrarlo, per «alleggerire o boostare» il progetto, avendo già un
account. Controllato: `.git` pesa 3,2 MB con 47 commit, e `aggiorna.yml`
committa `dati/` solo se cambia qualcosa — la storia cresce di pochissimo,
niente da alleggerire oggi. In più richiederebbe una chiave (anche solo
«publishable», con RLS) lato client, contro la regola 2 qui sopra. Se un
giorno la storia diventasse davvero un problema, la via che resta senza
backend è spostare `dati/` su un branch separato azzerato periodicamente
(commit orfano), non Supabase. Non riaprire senza un problema vero da
risolvere.

**xG e statistiche avanzate, cercate e non trovate (15/09/2026, lavoro da
remoto).** L'utente voleva portare Jarvis al livello delle analisi moderne
(xG e simili). Verificate le fonti, una per una:
- **Understat**: il `robots.txt` vieta la raccolta automatica. Escluso — è un no
  del sito, non un ostacolo tecnico da aggirare.
- **FBref**: risponde **403 alle richieste automatiche** (anche al solo
  `robots.txt`). Protezione anti-bot, e un runner GitHub Actions ha un IP da
  datacenter: inaffidabile per un giro schedulato.
- **football-data.org** (gratuito, con chiave): niente xG, solo risultati e
  classifiche, roba che abbiamo già.
- Tutto il resto che si trova è commerciale a pagamento (Sportmonks, TheStatsAPI,
  FootyStats) o attori Apify che raschiano Understat, quindi col divieto a monte.

Conclusione: **xG vero, gratuito e lecitamente automatizzabile per la Serie A non
esiste.** E soprattutto **non è il dato che serve qui**: al fantacalcio il
bersaglio è il *fantavoto*, cioè voto del giornalista più bonus. xG prevede solo
la seconda metà, e solo per chi segna; 16 dei 25 giocatori della rosa sono
difensori e centrocampisti, il cui fantavoto è dominato dal voto. Con il
modificatore difesa il voto pesa ancora di più. La strada giusta non è comprare
xG, è costruire il suo equivalente su misura — il **fantavoto atteso** — sullo
storico dei voti. Non riaprire la caccia alle fonti xG senza un motivo nuovo.

**Lo storico dei voti, verificato e disponibile (15/09/2026).** L'archivio dei
voti di fantacalcio.it — la fonte che `aggiorna.py` già raschia ogni giorno per la
giornata corrente — è pubblico, senza login, e i menù di stagione arrivano indietro
fino al **2015/16**. Sono ~38 giornate × ~290 giocatori × 11 stagioni ≈ **120.000
righe giocatore-partita**. È la materia prima per il fantavoto atteso: il parser
c'è (`righe_voti`, che dal 15/09 legge l'Id anche dai link delle stagioni passate)
e il giro si fa con `scripts/storico.py`. Vedi B1 più sotto.

## Lavoro da remoto (sessioni cloud)

Dal 15/09/2026. Oltre a Claude Code sul PC, il progetto si porta avanti anche
da una sessione Claude nel cloud, da remoto: stesso repository, stesse regole
sopra, ma **senza poter fare push**.

Sul perché, con precisione (verificato il 15/09/2026, prima era scritto in modo
sbagliato): **GitHub in lettura si raggiunge benissimo** da una sessione cloud —
`git clone`, `git fetch` e `git ls-remote` su questo repository funzionano, ed è
pubblico. Quello che manca sono le **credenziali** per scrivere: nessun helper è
configurato, e un token non va chiesto né fatto passare per la chat. Push dunque
solo da Claude Code, che gira nativo su Windows e vede le credenziali di sistema.

La conseguenza utile: una sessione cloud **non deve tirare a indovinare sullo
stato del progetto**. Può clonare `origin/main` e guardare com'è messo davvero,
e soprattutto può **provare che le proprie patch si applichino pulite** su un
clone fresco prima di consegnarle, invece di dire «dovrebbero applicarsi». Fatto
per le prime 13 patch il 15/09: applicate in ordine su `c5ea986`, esito 0, e
tutte le prove verdi sul clone.

- La sessione cloud clona il repository e lavora su un branch
  `claude-cloud/<data>`, mai su `main` direttamente.
- Ogni intervento finito aggiorna anche **questo file** nello stesso commit,
  con una nota datata nella sezione giusta, come per ogni altra modifica:
  CLAUDE.md resta l'unica fonte di verità sullo stato del progetto, letta da
  chi riprende il lavoro — sul PC o da un'altra sessione cloud.
- Il lavoro si consegna come patch (`git format-patch`), da salvare in
  `remoto/patch/`: fuori da Git (come `archivio/`), è solo smistamento, non
  fa parte della storia del progetto.
- Con Claude Code: si applicano le patch in ordine (`git am
  remoto/patch/*.patch`), si fa push, poi si ripulisce `remoto/patch/` — le
  patch hanno già fatto il loro lavoro, restano solo i commit veri.
- Se una sessione cloud riparte e trova un proprio branch precedente non
  ancora applicato (la patch non è ancora arrivata su GitHub), lo dice
  invece di ripartire da capo o di rifare lo stesso lavoro.

**`remoto/patch/` è la cassetta della posta ufficiale** (regola dal 15/09/2026,
voluta dall'utente). Vale in tutte e due le direzioni:

- **Claude Code, a ogni inizio sessione, guarda lì dentro senza che glielo si
  chieda.** Se ci sono `.patch`, c'è lavoro svolto da remoto che non è ancora
  nella storia: si applica quello *prima* di mettersi a fare altro, altrimenti si
  lavora su una base vecchia e le patch poi non entrano più pulite. Cartella vuota
  = niente in sospeso, si procede normalmente.
- **La sessione cloud ce le scrive dentro da sé**, quando il computer dell'utente
  è collegato all'app Claude Desktop: non serve che l'utente scarichi niente a
  mano dalla chat. Se il computer non è collegato, restano i file in chat e la
  cartella la riempie l'utente.
- Le patch sono numerate e **vanno applicate in ordine**: sono commit consecutivi.
  Su conflitto: `git am --abort` e si riferisce, senza risolvere a naso.

**Regole di convivenza tra PC e cloud** (15/09/2026, concordate con l'utente dopo
la prima consegna da 14 patch):

- **Un solo cantiere per volta sugli stessi file.** Prima che una sessione cloud
  cominci, il lavoro del PC è già su GitHub; finché ci sono patch in cassetta, sul
  PC non si tocca il codice. In parallelo si lavora solo su file diversi (per
  esempio il PC su `scripts/`, il cloud su `index.html`), e in questo file ognuno
  scrive nella sezione del proprio lavoro: così `git am` entra pulito anche quando
  tutti e due toccano CLAUDE.md.
- **Con le patch, una nota di consegna** (`remoto/patch/CONSEGNA.md`): commit di
  partenza, elenco delle patch, totali attesi delle prove, e cosa è stato
  verificato davvero e cosa no. Claude Code la legge prima di `git am` e confronta
  i totali.
- **Chi fa cosa lo decide la rete.** Dal cloud fantacalcio.it, i feed degli orari
  e Leghe non si raggiungono: tutto ciò che scarica dati veri (`aggiorna.py`, lo
  storico dei voti, la routine «dati di lega», le formazioni dal Chrome) si fa dal
  PC. Al cloud: logica dell'app, grafica, prove, documentazione, analisi sui dati
  già su GitHub.
- **Il ritorno, dal PC al cloud**: tutto finisce su GitHub, che la sessione cloud
  rilegge ripartendo da `origin/main`. I messaggi puntuali (una patch che non
  entra, e perché) passano dall'utente o da una nota in `remoto/`, fuori da Git,
  che il cloud legge quando il PC è collegato.
- **`dati/` non si tocca mai da una patch**: lo riscrive il giro automatico tre
  volte al giorno.

**Trappola dei fine riga (CRLF), vista davvero il 15/09/2026.** Il repository sta
in una cartella OneDrive su Windows. Può capitare di trovare `git status` con
*tutti* i file modificati — `index.html`, `CLAUDE.md`, `prove/`, tutto — e un
diff con lo stesso identico numero di righe aggiunte e tolte. **Non è lavoro
perso e non è un conflitto: è solo il fine riga**, i file riscritti in CRLF
mentre in Git stanno in LF. Come accertarlo in un colpo:

```
git diff --ignore-cr-at-eol --stat     # se non stampa nulla: solo fine riga
```

Se non stampa nulla, il contenuto è identico e si ripulisce con `git restore .`
senza perdere niente. **Da fare prima di `git am`**: con l'albero sporco le patch
non si applicano. Dal 15/09 `.gitattributes` normalizza a LF per prevenirlo (con
l'eccezione di `dati/*.ics`, che per RFC 5545 vuole CRLF davvero).

Altra cosa vista lo stesso giorno: una sessione cloud che tocca il repository
attraverso il ponte del desktop **non può cancellare file** nella cartella
collegata, se l'utente non glielo concede. Git ci lascia allora un
`.git/index.lock` che blocca ogni operazione di scrittura. Lo si toglie da
Claude Code, che gira nativo e non ha quella restrizione. Meglio ancora: dalla
sessione cloud non si lanciano comandi git che scrivono, dentro quella cartella —
lì si consegnano file e basta, il git lo fa Claude Code.

## Il lucchetto (i dati della lega chiusi a chiave)

Dal 16/09/2026, scelta dell'utente («proteggerle senza inficiare Jarvis»). Il
repository è pubblico: i dati **della lega** — rose e calendario (`base.json`),
classifica e risultati (`lega.json`) e i consigli salvati (`consigli.json`) — ci stanno
solo **chiusi a chiave**, in
`dati/<nome>.chiuso.json`. I dati presi da fonti pubbliche (voti, statistiche, orari,
probabili, infortuni, squadre, storico, modello) restano in chiaro: sono pubblici
comunque, e così prove e sessioni cloud continuano a lavorarci.

- **Cifratura**: AES-GCM a 256 bit, IV casuale, il nome del file come dato associato
  (un file chiuso non si spaccia per un altro); chiave dalla password con
  PBKDF2-SHA256, 600.000 iterazioni, sale in `dati/lucchetto.json` (pubblico, con una
  «prova» cifrata per riconoscere la password giusta). Stesso formato in
  `scripts/lucchetto.js` (Node, `crypto.webcrypto`) e in `index.html` (Web Crypto di
  Safari): nessuna libreria.
- **La password** la sceglie e la conosce solo l'utente, almeno 12 caratteri (i file
  chiusi restano pubblici per sempre: una password corta si indovinerebbe). Sta in tre
  posti, messi da lui: l'app Password dell'iPhone (Jarvis, dopo la prima volta, tiene la
  chiave derivata, mai la password); il Secret `JARVIS_CHIAVE` su GitHub; sul PC il file
  `C:\Users\<utente>\.jarvis-chiave` (fuori dal repository e da OneDrive; va bene anche
  il `.txt` del Blocco note) o la variabile `JARVIS_CHIAVE`. **Mai in chat, mai nel
  codice, mai stampata**: Claude lancia gli script che la leggono da lì, senza vederla.
- Le copie in chiaro (`dati/base.json` …) sono in `.gitignore`: stanno solo sul PC e
  dentro i giri di GitHub. `node scripts/lucchetto.js apri` le ricrea dalle copie
  chiuse, `chiudi` richiude solo quelle cambiate (IV nuovo = file diverso = commit
  inutile), `stato` dice com'è messo, `inizia` una volta sola. `apri` non sovrascrive un
  file in chiaro cambiato dopo l'ultima chiusura (lavoro non ancora chiuso) senza `--forza`.
- **Sul PC, sempre**: dopo `git pull`, `apri`; dopo ogni import dei dati della lega
  (rose, «dati di lega»), `chiudi` prima del commit. Nel commit vanno solo le copie chiuse.
- Nei giri di GitHub: `aggiorna.yml` apre all'inizio e richiude prima
  del salvataggio (verificato sul primo giro vero, commit del 16/09 alle 12:45); `prova.yml` apre prima delle prove. Senza `dati/lucchetto.json`
  questi passi non fanno niente.
- Nell'app: all'avvio legge `dati/lucchetto.json`; se c'è, apre i file protetti con la
  chiave tenuta sul telefono (`chiaveSalvata`), altrimenti (o se la password è cambiata)
  mostra «Jarvis è chiuso a chiave» (`chiediPassword`, con i campi che l'iPhone
  riconosce per salvare la password). Nelle prove e in `notifiche.js` il lucchetto non si
  vede (`lucchetto.json` assente per finta): leggono le copie in chiaro.
- `dati/jarvis.ics` resta in chiaro (il Calendario dell'iPhone non sa aprire il
  lucchetto): da oggi senza il nome dell'avversario.
- `prove/privacy.py` controlla che i file in chiaro della lega non siano nella storia,
  che il lucchetto pubblico abbia solo sale, iterazioni e prova, e che **nei file
  pubblici non compaia il nome di nessun'altra squadra** (codice, prove, documenti,
  calendario). Per questo le prove ricavano i nomi dai dati (`base['g']`), e qui si
  scrive «una squadra», mai il nome.
- **Sessioni cloud**: senza la password non vedono i dati della lega, e le prove che li
  leggono (quasi tutte quelle dell'app) non girano. O l'utente mette `JARVIS_CHIAVE`
  nelle variabili d'ambiente della sessione cloud (dalle impostazioni, mai in chat), o
  il cloud si limita a codice e documenti e le prove le fa il PC prima del push.
- **La storia di git è stata azzerata il 16/09/2026** (scelta dell'utente): conservava
  le versioni in chiaro di prima del lucchetto (rose, classifica e calendario di
  settembre, e questo file con qualche nome). Ora su GitHub si parte da un commit solo,
  con un push forzato. La storia di prima sta solo sul PC, in
  `archivio/storia-fino-al-2026-09-16.bundle` (`git clone` del file per riaverla).
  **Azzerata una seconda volta il 17/09/2026**, sempre su scelta dell'utente: dentro il
  commit di ripartenza c'era ancora `prove/dati/classifica-prova.xlsx` con i nomi veri
  (vedi «Dal telefono, senza PC»). Copia di quella storia in
  `archivio/storia-fino-al-2026-09-17.bundle`.
  GitHub può tenere per un po' i commit vecchi raggiungibili dal loro codice, e una
  sessione cloud con un clone di prima deve ripartire da un clone nuovo.
- Stato: **attivo dal 16/09/2026** (Secret e file sul PC messi dall'utente, `inizia`
  fatto, file in chiaro tolti con `git rm --cached`). Verificato lo stesso giorno: la
  password del PC apre i file pubblicati su GitHub, e le prove su GitHub aprono il
  lucchetto col Secret. Al primo tentativo dall'iPhone l'utente non entrava (file e
  codice pubblicati erano a posto, provati da un browser): la schermata ora ha «Mostra»
  per vedere la password scritta, niente maiuscole automatiche né correttore, il campo
  non si svuota dopo un errore, e un errore di Safari si scrive invece di restare fermi
  su «Apro…».

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
dati/storico/           lo storico dei voti dal 2015-16, una stagione per file compresso (B1, non per l'iPhone)
scripts/storico.py      giro una tantum e ripartibile che riempie dati/storico/ (voti, quotazioni, calendari)
scripts/modello.py      addestra il modello del fantavoto atteso (B2) e scrive dati/modello.json, nel giro automatico
dati/modello.json       il modello: pesi per ruolo, verifica, e per ogni giocatore delle rose la parte che dipende solo da lui
dati/lucchetto.json     il lucchetto: sale, iterazioni e una prova cifrata (pubblico, niente di segreto)
dati/*.chiuso.json      base, lega e consigli chiusi a chiave: col lucchetto, nel repository ci sono solo questi
scripts/lucchetto.js    apre e chiude i dati della lega (stato | apri | chiudi | inizia)
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
esempio una squadra ha preso il nome che ha nell'app); i giocatori dal nome, prima
nella rosa attuale, poi nel listone (dove ogni nome è unico). Si accetta anche
`rose.csv`, che ha l'Id. Controlli: 10 squadre da 25 (3/8/8/6), ruoli coerenti,
nessun giocatore in due squadre. Serve `openpyxl` (`pip install openpyxl`), solo
sul PC. Dal 15/09/2026 `prove/privacy.py` controlla che in `dati/` non finisca
mai un nome «grezzo»: le uniche squadre ammesse sono quelle di `dati/base.json`.

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
prova: lo costruisce al momento `prove/app.js` (`xlsxProva`, uno zip minimo col solo
foglio), con numeri inventati e i nomi presi dai dati chiusi. Fino al 16/09/2026 stava nel
repository (`prove/dati/classifica-prova.xlsx`) con i nomi veri dentro, e nessun controllo
lo vedeva: tolto, e `prove/privacy.py` ora apre anche i file Office tracciati.

**Statistiche e quotazioni non si aggiornano più a mano**: lo script le prende
una volta al giorno dalle pagine pubbliche di fantacalcio.it
(`dati/statistiche.json`, abbinate per Id dal link del giocatore, almeno 400
giocatori per scrivere) e l'app le applica sopra `base.json`. L'esportazione
«Lista calciatori» non serve più (quella del 12/09 era filtrata su 5 squadre).
Dalla stessa pagina arrivano, dal 14/09/2026, gol, gol subiti, rigori parati,
assist, ammonizioni ed espulsioni (in coda a ogni riga di `statistiche.json`):
se cambiano solo quelle colonne si salvano le statistiche principali, senza bonus.
Dal 15/09/2026 `statistiche.json` ha anche `iniziali`, la quotazione iniziale di ogni
giocatore: la usa il modello (B2), perché quella attuale si muove con il rendimento.

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
ogni giornata, per «La stagione» (vedi «Stato dei lavori», aperti, punto 4).

## Calendario

`dati/jarvis.ics` si sottoscrive dall'iPhone con il link nell'app (`webcal://`).
Lo genera lo script a ogni giro: una scadenza per ogni giornata di lega con
orario ufficiale, 15 minuti prima del primo anticipo, con un avviso 2 ore prima
(scelta dell'utente). Dal 16/09/2026 il titolo non ha il nome dell'avversario
(«Schiera la formazione · G1»): il file è pubblico e il Calendario dell'iPhone non sa
aprire il lucchetto. Il promemoria settimanale per esportare la Lista calciatori
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
- **Colori delle squadre** (`COLORI_SQUADRE`, `coloreSquadra`): una tavolozza fissa di
  10 colori assegnati per posizione alfabetica, non per nome (cambia da solo se una
  squadra cambia nome). Rifatta il 15/09 (lavoro da remoto, dopo una revisione grafica
  vera: la pagina renderizzata in un browser con Playwright, non letta dal CSS) perché
  tre colori cadevano troppo vicini ai colori con un significato nell'app — oro
  dell'accento e della stella, rosso e verde di forma e disponibilità — e su un
  controllo con le 10 squadre vere una usciva con un ambra quasi identico
  all'oro. La nuova tavolozza tiene ogni colore lontano da quei quattro.
- **Focus visibile su «Chiedi»** (15/09, stesso giro): il campo toglie il proprio
  contorno (taglierebbe lo spigolo del vetro), ma `.chiedi-in:focus-within` illumina
  tutto il pillolo — prima non c'era nessun segno del fuoco.
- **Mercato, «per loro» sempre verde** (15/09, stesso giro): `perMe` e `perLoro` sono
  sempre ≥ 0 quando arrivano fin qui (`mercato()` scarta prima gli scambi che non
  convengono a uno dei due), ma un valore vicino allo zero restava bianco invece che
  verde: sembrava sfavorevole anche quando l'offerta era onesta. Ora sempre verde.
- **Condividi** (15/09, lavoro da remoto, scelta dell'utente — sfruttare l'iPhone 16
  Pro/iOS 26): `navigator.share()` (Web Share API, in Safari iOS anche da app
  installata da iOS 12.2), foglio nativo di condivisione dell'iPhone. Pulsante nella
  sovraimpressione (`apriSovra`, quarto parametro `testo`), acceso solo dove c'è
  qualcosa di sensato da mandare — «Com'è andata» e «La stagione» — e solo se il
  browser sa condividere (`condividi-sovra` resta `hidden` senza `navigator.share`,
  niente pulsante morto). «Mercato» non ha un testo da condividere: scelta di scopo,
  non dimenticanza. Verificato con Playwright: nascosto senza `navigator.share`,
  visibile simulandolo.
- **Cambio giornata in «La stagione», con dissolvenza** (15/09, stesso giro):
  `document.startViewTransition()` (Safari dal 2024, iOS 26 la ha) al posto dello
  scatto secco del grafico. `#st-grafico` ha un `view-transition-name` tutto suo e
  `::view-transition-group(root)` è azzerato, altrimenti l'intera schermata (testata,
  barra di navigazione) entrerebbe nella stessa dissolvenza invece del solo grafico.
  Rispetta «riduci movimento» (media query estesa anche agli pseudo-elementi della
  View Transition, che «*» non prende). Senza l'API (Safari più vecchio) l'aggiornamento
  resta immediato, mai un errore. Verificato: la funzione esiste in Chromium, nessun
  errore in console al cambio giornata.
- **Riquadro «La difesa», rifatto a righe** (15/09, lavoro da remoto, su richiesta
  dell'utente). La prima versione aveva una barra unica a segmenti e la legenda
  sotto: sei fasce, tre colori soli, e l'occhio doveva accoppiare segmento e
  percentuale da sé. Ora una riga per fascia, con etichetta e percentuale accanto
  alla propria barra — nessun accoppiamento da fare. **Una tinta sola** (l'oro),
  accesa sulla fascia più probabile e spenta sulle altre: la storia è dove cadi,
  non sei categorie da distinguere; l'ordine delle righe (dal +6 allo zero) porta
  già il senso di «più in alto è meglio». Le barre restano in scala assoluta
  (0-100%), non normalizzate al massimo: così si vede anche *quanto* sei sparso,
  cioè quanto è prevedibile la difesa. Ci sono sempre tutte e sei le fasce, anche
  quelle mai uscite nelle simulazioni: uno zero lì è un'informazione, non un buco.
  Il separatore disegnato tra i segmenti della vecchia barra è sparito: tra le
  barre va uno spazio, non un bordo.
- **`.blocco` è un velo bianco, non scuro** (15/09, lavoro da remoto): sta bene
  sulle zone scure dello sfondo, ma il riquadro «La difesa» cade sul centro chiaro
  dello stemma e il testo si perdeva (visto renderizzato, non dedotto dal CSS).
  Per quel riquadro c'è `.blocco.scuro`, con base scura e sfocatura. Se un domani
  altre schede finiscono su zone chiare, la stessa classe è già pronta; non è stata
  applicata a tutte per non cambiare l'aspetto dell'app intera senza chiederlo.
- **Panchina compatta** (16/09/2026, lavoro da remoto, scelta dell'utente): ogni
  panchinaro prendeva quattro o cinque righe, con dentro la frase lunga
  sull'avversario («Frosinone (4-2-3-1) segna 1,0 gol a partita in casa, media 1,3 ·
  neopromossa, stima») e la barra della titolarità. Otto giocatori così erano una parete
  di testo per una lista che si guarda di sfuggita — e quel ragionamento **c'è già** in
  «Il consiglio» e nella scheda del giocatore, quindi lì era ripetizione. Ora `riga()`
  accetta `magra`: niente frase dell'avversario, niente barra, niente miniatura
  dell'andamento, e la forma breve «vs Genoa» invece di «in casa con Genoa», che mandava
  a capo mezza lista. Misurato sulla lega finta: **da 873 a 413 pixel**, meno della metà.
  Il resto della sezione (`kobox`, «Non disponibili») è rimasto com'era: proposto
  all'utente e non voluto.
- **«Quando giocano i tuoi», proposta respinta** (16/09, stesso giro): provata una
  versione raggruppata per giorno, con i nomi dei tuoi in evidenza e la partita come
  contorno. La prima stesura era pure **più alta** dell'originale (688 contro 582 px: le
  intestazioni dei giorni costavano più della ripetizione che toglievano), la seconda
  arrivava a 550. All'utente non è piaciuta: lasciata com'era. Non riproporla senza una
  richiesta nuova.
- **Sfocatura vetro (`backdrop-filter`), lasciata com'è** (15/09, stesso giro): idea
  valutata insieme alle altre due ma non applicata. Su iPhone più vecchi molte
  sfocature sovrapposte possono pesare sul render, ma sull'iPhone 16 Pro dell'utente
  (chip A18 Pro) non c'è un problema vero da correggere — cambiare qualcosa che non è
  rotto, sulla base di un timore generico e non di un rallentamento osservato, sarebbe
  stato un dato inventato.

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
  (B4, livello 4). Per le giornate di lega arriva la notifica «Giornata N: com'è andata».
- **Andamento** (`graficoVoti` nella scheda, `miniLinea` nell'elenco della Rosa):
  fantavoto giornata per giornata; «s.v.» se la sua squadra ha giocato e lui non ha
  preso voto.
- **Calendario dei tuoi** (`prossimi3`, `pallini3`): i prossimi 3 avversari sotto
  ogni maglia della Rosa e nella scheda del giocatore, verde facile, giallo nella
  media, rosso difficile, con lo stesso calcolo dell'avversario nel consiglio
  (`forzaSa`).
- **Mercato, sulla carta** (`mercato`, nella scheda Lega), rifatto il 15/09 perché
  il primo proponeva di prendere senza dare («quella squadra non mi darebbe mai
  Malen»), e di nuovo lo stesso giorno perché «ragiona troppo per numeri»: deve
  pensare come una persona in un fantacalcio vero («quella squadra non mi darà mai
  uno dei suoi due top attaccanti per Hermoso»). **La rosa resta legale** (regola
  corretta il 15/09, lavoro da remoto: la lega è ad asta a ruoli, rosa fissa 3
  portieri-8 difensori-8 centrocampisti-6 attaccanti, uguale su tutte e 10 le
  squadre in `dati/base.json` — verificato sui dati veri, non un'ipotesi. Prima
  qui c'era scritto «1 contro 1 anche tra ruoli diversi»: sbagliato, un pezzo
  solo per lato non può cambiare la composizione senza sbilanciare la rosa):
  **1 contro 1 sempre stesso ruolo**; **2 contro 2 stessi due ruoli dati e
  ricevuti** (uguali, D+D per D+D, o diversi, C+A per C+A, mai un ruolo che
  compare solo da un lato) — è così che un top di un reparto si scambia con un
  top di un altro reparto, col secondo giocatore di ogni lato scelto apposta a
  pareggiare il ruolo, non a caso. Un top (`intoccabili`: i due più quotati di
  ogni reparto, il portiere più quotato, i tre più quotati della rosa) **si può
  chiedere solo offrendone anche uno dei miei** (prima era sempre escluso: troppo
  rigido, un top per un top è una proposta vera); alla pari a vista, perché
  l'altro guarda quotazione e fantamedia (quotazioni entro il 15% o 2 punti, e chi
  dai non ha una fantamedia vera più bassa di oltre 0,5); serve a tutti e due (il
  tuo undici migliora di almeno 0,3, chi dai entra nel loro undici e il loro non
  peggiora). Prima gli scambi di esuberi (chi prendi da loro non giocava). Il valore è per la
  stagione (`valoreStagione`: fantamedia stimata e presenze, `presenze`; niente
  calendario), gli undici con `migliori11` (e, per fare in fretta, `perReparto`,
  `valore11`, `valoreDopo`). Anche **2 contro 2** (scelta dell'utente del 15/09): somme
  delle quotazioni vicine (15% o 3 punti), fantamedia vera media non più bassa di 0,5,
  il tuo undici migliora di almeno 0,5 e di almeno 0,2 più del miglior scambio singolo
  **legale** (stesso ruolo) tra quegli stessi giocatori che si potrebbe fare davvero
  (alla pari e buono anche per loro): il 15/09 il confronto con tutti i singoli, anche
  quelli impossibili, non lasciava passare nessun 2 contro 2, mentre spesso il secondo
  giocatore serve proprio a pareggiare le quotazioni. Al massimo 4 singoli e 3 doppi,
  mai lo stesso giocatore chiesto due volte; il risultato si tiene in memoria
  (`mercatoMemo`) finché non cambiano i dati o la giornata. Nella pagina una riga; in
  sovraimpressione (`apriMercato`) per ogni scambio chi dai e chi prendi, «per te» e
  «per loro», chi entra negli undici e la tabella voce per voce (per i 2 contro 2 i due
  insieme), in due gruppi: «1 contro 1» e «2 contro 2».
- **La stagione** (`stagione`, riga in cima alla Rosa, `apriStagione`): in cima il
  grafico giornata per giornata dei fantapunti dei tuoi migliori 11 (`graficoStagione`:
  una colonna per giornata, ★ sulla migliore, linea della media), che si tocca per
  aprire sotto la giornata (`scegliGiornata`, `dettaglioGiornata`: totale, «la
  migliore»/«la peggiore», porta, difesa, centrocampo, attacco e gli 11 con voto e
  bonus; frecce per le altre). Poi gol, assist, ammonizioni dei tuoi e «chi produce»,
  i fantapunti di ognuno in tutte le giornate, con media e bonus e malus. Scelta dell'utente: con le formazioni vere
  («Stato dei lavori», aperti, punto 4) dirà anche chi era schierato e chi ha prodotto il totale vero.
  **«Quanto si avvicina Jarvis»** (lavoro da remoto, 15/09/2026, uno dei consigli
  proposti dalla sessione cloud e approvati dall'utente insieme agli altri tre di
  questo elenco): per ogni giornata di lega con un consiglio salvato (`dati/consigli.json`,
  già scritto da `notifiche.js` a ogni giro, vedi sopra), `stagione()` calcola anche i
  punti che avrebbe fatto quell'undici (`puntiUndici`, stessa regola della lega di
  «Com'è andata») accanto al massimo possibile di quella giornata; in
  `dettaglioGiornata` una riga in più («Il consiglio di Jarvis: X, Y in meno del
  massimo»); in cima alla sovraimpressione un blocco riassuntivo
  (`accuratezzaConsiglio`) con consigliato, massimo possibile e vicinanza in
  percentuale su tutte le giornate valutabili. Niente dato nuovo da raccogliere: i
  file `dati/consigli.json` e `dati/voti.json` accumulano già tutta la stagione da
  soli, qui è solo una lettura in più di dati che ci sono già — e proprio per questo
  serve all'autocalibrazione dei `PESI` (B4, livello 4), per vedere a occhio quanto Jarvis si
  avvicina prima di cambiare i pesi.

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

**Dal 15/09/2026 il punteggio viene dal modello** (B2, scelta dell'utente): fantavoto
atteso se gioca (`attesoModello`, da `dati/modello.json`) più la titolarità, come
prima. Il calcolo descritto qui sotto (fantamedia stimata, titolarità, `PESI`) resta
come `punteggioVecchio`: vale per un ruolo dove il modello non ha battuto quel
calcolo nella verifica, quando manca il file, e per il confronto in «Quanto si
avvicina Jarvis». Vedi B2 più sotto.

Il calcolo di prima parte dalla **fantamedia stimata** e aggiunge:
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

**Il modificatore di difesa, calcolato** (15/09/2026, lavoro da remoto). La lega
usa la configurazione «Consigliata»: **portiere + i 3 migliori difensori**, sulla
**media voto** (tabella confermata dall'utente con una schermata delle
impostazioni). Gli scalini: `<6` → 0, `≥6` → +1, `≥6,25` → +2, `≥6,5` → +3,
`≥6,75` → +4,5, `≥7` → +6. Sono in `MODIFICATORE` in `index.html`, unica fonte di
verità (le due liste piatte accanto ne derivano, servono solo alla velocità).

Fino a oggi il modificatore non era calcolato: viveva come costante scritta a mano
in `PESI` (`D:0.8`), cioè «i difensori contano un po' di più». Adesso:
- **vive sui voti, non sui fantavoti**: un difensore da gol e assist ma voti
  mediocri non aiuta il modificatore, uno da 6,5 fisso sì. `votoAtteso()` stima il
  voto (media del giocatore mescolata con quella del ruolo, come per la
  fantamedia) e quanto balla (`BALLO`, misurato sui voti veri di tutta la lega
  messi insieme: con poche giornate il singolo non basta). **Senza voti misurati
  resta spento e l'undici si forma come prima**: niente incertezza inventata.
- **dal 15/09/2026 il voto atteso viene dal modello** (B2): `votoAtteso(p, g)` usa
  `attesoModello('voto', …)` con la partita e l'incertezza del giocatore, per i ruoli
  dove il modello batte il calcolo di prima; per i portieri no, resta quello sopra.
- **si simula invece di fare la media** (`modificatoreAtteso`, Monte Carlo con
  seme fisso, così lo stesso undici non balla da un tocco all'altro e le prove
  sono ripetibili). Sugli scalini la media è bugiarda: un blocco «da 2,8» non
  prende mai 2,8, prende +2 o +3. Quello che conta è con che probabilità.
- **la difesa si sceglie a blocco, non uno per uno** (`bloccoDifensivo`): vince la
  combinazione col totale più alto, fantapunti dei singoli più modificatore
  atteso. Candidati: i migliori per punteggio uniti ai migliori per voto atteso,
  perché uno «specialista del voto» va guardato anche se per fantamedia non
  spicca.
- Il riquadro **«La difesa»** ha l'atteso, la distribuzione per fascia e quanto
  manca allo scalino sopra — l'informazione che fa davvero cambiare un difensore.
  Dal 15/09/2026 sera sta nella vista «Il consiglio» (B5); nella Giornata ne resta
  il riassunto.

Una cosa contro-intuitiva, misurata e non supposta: con quattro difensori il
peggiore viene **scartato**, quindi verrebbe da pensare che uno da voti scarsi sia
gratis. Non lo è: costa comunque (circa 0,6 sui dati veri di settembre) perché una
volta su cinque non è lui il peggiore e il suo voto entra nella media. Il secondo
costa quasi il doppio. È la ragione per cui la scelta a blocco batte quella uno
per uno, ed è verificata in `prove/app.js` come invariante, non come numero fisso.

**Doppio conteggio, noto e lasciato lì apposta:** `PESI` continua a pesare di più
portiere e difensori anche per il modificatore, che ora è calcolato a parte. Non
sposta le scelte (il peso è uguale per tutti i difensori e il loro numero è fisso),
e ritoccarlo a sentimento sarebbe inventare un numero: si ritara quando il modello
dello storico darà coefficienti veri. Per questo il modificatore si mostra in un
riquadro suo e non è sommato nei totali già visibili.

**Velocità:** la ricerca a blocco costa ~6,5 ms a freddo e ~0,3 ms quando è già in
memoria (misurato, non stimato). Ci si arriva separando la **ricerca** (poche
simulazioni: il confronto tra combinazioni usa gli stessi campioni, quindi è
appaiato) dal **numero mostrato** (più simulazioni, una volta sola sul vincitore),
tenendo i campioni in `CAMPIONI` e i blocchi già risolti in `BLOCCHI` — tutti
svuotati da `stimaVoti()` quando i dati cambiano.

**L'avvio: il mercato fuori dal primo disegno** (16/09/2026, lavoro da remoto, su
segnalazione dell'utente «l'avvio è un po' troppo lento»). Col profilatore, la funzione
più cara dell'apertura era `ruoli2`, cioè il **mercato**: `renderMercato` girava dentro
il primo disegno e calcolava tutti gli scambi possibili fra le dieci rose (~150 ms) solo
per riempire il cartellino «N scambi alla pari» — in una scheda, la Lega, che all'apertura
non stai guardando. Ora passa da `dopoIlPrimoDisegno` e arriva un attimo dopo.

Misurato con la rete simulata (mediana di 5-7 aperture, fino al momento in cui l'undici è
in pagina): in locale **598 → 321 ms**, 4G buono (80 ms / 25 Mbps) **925 → 668**, 4G
lento (80 ms / 4 Mbps) **1779 → 1501**, rete lenta (150 ms / 10 Mbps) **1340 → 1090**.

Due strade **provate e scartate**, per non rifarle:
- *Leggere gli 11 file di dati in parallelo invece che in fila.* Sembra ovvio, non serve:
  misurato, ±30 ms (rumore), e su banda stretta **peggiora** (1779 → 1850), perché i dati
  finiscono a competere con lo sfondo e l'icona. L'avvio qui non è limitato dalla
  latenza ma dal lavoro della macchina.
- *Ricomprimere `img/icona-180.png`* (71 KB, alfa sprecata, scaricata due volte). A
  tavolozza scende a 29 KB con uno scarto medio dell'1%, ma su 767 KB totali e con
  l'avvio limitato dalla CPU sarebbe un guadagno da briciole in cambio di un'immagine
  degradata. Se un giorno servisse, il numero è quello.

Attenzione, per chi tocca il rinvio: nelle prove il finto ambiente ha `setTimeout: () => 0`,
uno stub che **non esegue nulla**. Perciò `dopoIlPrimoDisegno` usa `requestIdleCallback`
(Safari dalla 16.4) e le prove ne forniscono uno che parte subito; senza, il mercato non
verrebbe mai disegnato lì e la verifica «nella Lega solo una riga, che invita ad aprire»
fallirebbe senza una ragione visibile.

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

## Da fare: il cervello di Jarvis (piano preparato il 15/09/2026)

Piano concordato con l'utente in una sessione cloud e **lasciato da fare a Claude
Code sul PC**. Qui c'è tutto il necessario per eseguirlo senza rifare le indagini:
quelle sono già state fatte e i risultati stanno in «xG e statistiche avanzate» e
«Lo storico dei voti» più sopra. Leggerli prima di cominciare.

L'ordine sotto è anche l'ordine di esecuzione: B1 è la fondazione, B2 e B3 ci
stanno sopra, B4 è indipendente e può andare quando si vuole.

### B1 — Lo storico dei voti (la fondazione)

L'archivio di fantacalcio.it arriva al 2015/16, pubblico e senza login (verificato
il 15/09). ~120.000 righe giocatore-partita.

- **Verificato dal PC il 15/09/2026, prima del giro intero** (su 2024-25 G20,
  2021-22 G10, 2015-16 G1): le pagine vecchie hanno la stessa struttura di quelle
  correnti **tranne il link del giocatore**, che finisce con la stagione
  (`.../musso/2792/2021-22`): il parser di prima ci leggeva 0 voti, quindi «cambia
  solo l'indirizzo» non era vero. Corretto con `ID_GIOCATORE` in `aggiorna.py`; la
  lettura delle righe ora è `righe_voti()`, usata sia da `voti_giornata()` (per
  l'app, invariata) sia dallo storico. Ogni riga ha anche squadra, ruolo e **gli 8
  bonus e malus della giornata** (`BONUS_VOTI`: gol, gol subiti, autoreti, rigori
  segnati, sbagliati e parati, assist, migliore in campo), anche nella stagione in
  corso: per B3 le frequenze dei bonus non vanno più ricavate dai totali di
  stagione. Il `robots.txt` di fantacalcio.it non vieta le pagine dei voti
  (controllato lo stesso giorno).
- **Id stabili tra le stagioni, verificato**: sulle tre giornate di prova tutti gli
  Id presenti anche nel listone di oggi (170, 83 e 13) portano allo stesso
  giocatore nel link, nessun Id riusato per un altro. `storico.py` stampa alla
  fine, per ogni stagione, quanti giocatori con voto sono ancora nel listone di oggi.
- **`scripts/storico.py`** (fatto il 15/09): giro una tantum, **ripartibile** (salta
  le giornate già prese e salva dopo ognuna, così un'interruzione non fa
  ricominciare), educato con la fonte (2 secondi tra le richieste; 418 pagine, ~20
  minuti). Stesso controllo di plausibilità di `voti()`: sotto 200 voti la giornata
  non si salva. `--prova <stagione> <giornata>` legge una giornata e non scrive
  niente. Provato in `prove/script.py` (6quater) con pagine finte.
- Dove sta: **una stagione per file, compresso** (`dati/storico/<stagione>.json.gz`),
  per ogni giornata e ogni Id una riga nell'ordine di `CAMPI` (voto, fantavoto,
  ruolo, squadra, poi i bonus). Lo zip non contiene date né nomi di file: lo stesso
  contenuto dà sempre lo stesso file, e le stagioni chiuse si scrivono una volta e
  non gonfiano la storia di git. Lo storico grezzo **non va servito all'iPhone**:
  resta materia prima per l'addestramento.
- **Giro completo fatto il 15/09/2026**: 11 stagioni, 418 giornate su 418, nessuna
  saltata, **114.111 righe giocatore-partita**, 548 KB in tutto, nessun voto fuori
  scala. Giocatori con voto ancora nel listone di oggi, stagione per stagione: 28
  (2015-16), 35, 46, 58, 77, 87, 128, 157, 209, 271, 336 (2025-26). Per rifare una
  stagione (un file rovinato) basta `python scripts/storico.py <stagione>`, che
  riparte da dove era arrivato; a fine 2026-27 va aggiunta estendendo `STAGIONI`.

### B2 — Il fantavoto atteso (l'equivalente dell'xG, su misura)

Non si compra xG (vedi sopra il perché): si costruisce il bersaglio giusto.
Dato giocatore, ruolo, avversario, casa/fuori, forma e squadra intorno →
**distribuzione** del fantavoto, non un numero solo.

- **Avversario e casa/fuori delle partite passate** (verificato dal PC il 15/09/2026):
  lo storico ha solo la squadra di ogni giocatore; i calendari stanno nel feed di
  fixturedownload già usato per gli orari (`/feed/json/serie-a-<anno>`), che c'è
  **dal 2017-18 al 2025-26** (380 partite a stagione, con risultato). Il 2015-16 e
  il 2016-17 no (404): per quelle due stagioni niente avversario, restano buone per
  la storia del giocatore. Due trappole viste: il `RoundNumber` del feed non è
  sempre la giornata ufficiale (nel 2017-18 le partite rinviate stanno in una
  «giornata 39» o in giornate da 11-12 partite: abbinare squadra e giornata solo se
  l'abbinamento è unico, e scartare gli altri, che sono pochi), e una partita del
  2023-24 non ha risultato (Sassuolo–Frosinone, giornata 28). I nomi del feed vanno
  tradotti in quelli di fantacalcio.it: `AC Milan`→`Milan`, `Inter Milan` e
  `Internazionale`→`Inter`, `Hellas Verona`→`Verona`, `Chievoverona`→`Chievo`,
  `Spal`→`SPAL` (confronto fatto stagione per stagione dal 2017-18 al 2023-24; oggi
  `SQUADRE` in `aggiorna.py` ha solo `Internazionale`, perché serve alla stagione in
  corso).
- Addestramento **nelle GitHub Actions**, non sul telefono. Nel repository finisce
  solo il modello addestrato (`dati/modello.json`, qualche decina di coefficienti);
  l'app li applica offline, all'istante.
- Preferire un modello **lineare/ridge** a una foresta o simili: l'app deve poter
  dire *perché* («titolarità +0,8, avversario −0,3»), e una scatola nera non lo sa
  fare. Con un bersaglio così rumoroso la differenza di accuratezza è piccola, la
  differenza di spiegabilità è tutta.
- **Innesto già pronto**: `votoAtteso(p)` in `index.html` restituisce
  `{media, sd}`. Tutto il resto (`campioneVoti`, `modificatoreAtteso`,
  `bloccoDifensivo`) passa da lì e non sa da dove venga la stima. Sostituire il
  corpo di `votoAtteso` con il modello **non tocca nient'altro**: è il punto di
  innesto pensato apposta il 15/09.
- Con lo storico, `BALLO` smette di essere una dispersione unica per tutta la lega
  e diventa **per giocatore** (chi è regolare e chi è una lotteria). È il salto di
  qualità vero per B3.
- Onestà obbligatoria: niente numero secco con aria sicura. Il calcio è
  genuinamente casuale e anche l'xG vero di Opta, su una partita, ha barre
  d'errore larghe. Mostrare l'incertezza, non nasconderla.
- **Fatto il 15/09/2026** (scelte dell'utente: il modello sostituisce il calcolo di
  prima, quotazioni storiche di tutte le stagioni, scomposizione nella scheda):
  - dati: `storico.py` aggiunge a ogni stagione `quotazioni` ({Id: [iniziale, finale,
    ruolo]}, 630-684 a stagione) e `partite` (il calendario col risultato, dal
    2017-18); `aggiorna.py` salva la quotazione iniziale di oggi in
    `statistiche.json` → `iniziali`.
  - `scripts/modello.py`: un modello lineare (ridge, Python puro) per ruolo, per il
    fantavoto e per il voto, con le voci `VOCI`: storia del giocatore (media pesata
    sulle ultime ~33 presenze, peso `W/(W+K)`), quotazione iniziale (conta per chi ha
    poca storia), in casa, avversario, attacco e difesa della propria squadra —
    misurati **esattamente** come `forzaSa`/`perPartita` nell'app, così i pesi valgono
    dentro l'app. Solo informazioni note prima della partita (provato in
    `prove/modello.py`). La forma recente è stata misurata e lasciata fuori: non predice.
  - verifica automatica sulle ultime due stagioni contro un'imitazione del calcolo di
    prima, quotazione compresa. Il 15/09 la correlazione col fantavoto vero, modello
    contro prima: P .217/.203, D .189/.131, C .197/.183, A .165/.154, e l'errore è più
    basso in tutti i ruoli. Per il voto dei portieri no (.019/.095). Regola scritta nel
    file (`usa`): **un ruolo usa il modello solo se in verifica batte il calcolo di
    prima**, e si ricalcola a ogni addestramento.
  - incertezza: il ballo del giocatore mescolato con quello del ruolo, con `n0`
    presenze «di fiducia» ricavate da quanto il ballo si conserva tra le stagioni
    (fantavoto C .49, A .47, P .33, D .24; voto dei portieri .08).
  - `dati/modello.json` (~13 KB): pesi, verifica e per ognuno dei 250 giocatori delle
    rose [peso della storia, media fantavoto, media voto, ballo fantavoto, ballo voto,
    presenze, quotazione iniziale]. Si riaddestra a ogni giro automatico (passo
    «Aggiorna il modello del fantavoto», ~2 secondi); si riscrive solo se cambia e solo
    se plausibile, altrimenti resta quello di prima.
  - nell'app: `attesoModello(quale, p, g)` (base del giocatore più la partita),
    `punteggio` = fantavoto atteso + titolarità, `votoAtteso(p, g)` dal modello (va al
    modificatore), `punteggioVecchio` e `CALCOLO_VECCHIO` per il calcolo di prima. Nella
    scheda del giocatore «Fantavoto atteso, se gioca» con ± e la scomposizione (base,
    in casa, avversario, squadra). Il consiglio salvato da `notifiche.js` ha anche
    `undici_vecchio`, e «Quanto si avvicina Jarvis» mostra il calcolo di prima accanto.
  - misurato, da ricordare: i `PESI` di prima sopravvalutavano l'avversario (per gol a
    partita: D 0,8 → 0,16 nel modello, P 1,0 → 0,50, A 0,8 → 0,31, C 0,4 → 0,16), e il
    giocare in casa, che prima non contava, vale +0,14/+0,18.
  - chiuso il 15/09 sera: anche il mercato (`valoreStagione` → `baseStagione`, il
    fantavoto atteso senza la partita; nella tabella «Base Jarvis» con la fantamedia
    vera sotto) e «come sta X» in «Chiedi» («atteso se gioca 6,41 ± 1,2») usano il
    modello. `fmStimata` resta solo nel calcolo di prima.

### B3 — Centrocampo e attacco: **probabilità di vittoria**, non punti attesi

L'utente ha chiesto se si può fare per C e A quello che si è fatto per la difesa.
**Lo stesso algoritmo no, e la ragione è matematica**: il modificatore esiste
perché una regola di lega fa passare una statistica *di gruppo* (media voto di
portiere + 3 difensori) attraverso una funzione *a scalini*. Questo rende la scelta
non separabile: i 4 difensori migliori presi uno per uno non sono il blocco
migliore. Per centrocampo e attacco **non c'è nessuna regola di gruppo**: ogni
fantavoto si somma per conto suo, e con una somma di termini indipendenti prendere
i migliori uno per uno **è già la scelta ottima**. Un «algoritmo a blocco» lì
sarebbe scenografia.

Quello che invece è vero e non sfruttato: **è sbagliato l'obiettivo**. Jarvis
massimizza i punti attesi, ma alla giornata non vinci facendo più punti in media —
vinci battendo *quel* preciso avversario. Le due cose divergono appena conta la
varianza:
- se sei dato avanti, ti serve il **pavimento**: gente regolare, ridurre la
  probabilità di crollare;
- se sei dato sotto, i punti attesi non servono a niente: ti serve il **soffitto**,
  perché le uniche strade che portano alla vittoria sono le code.

**Massimizzare la probabilità di vittoria non è separabile** (quanta varianza
conviene dipende dall'undici intero contro quell'avversario): qui un giro sulle
combinazioni ci sta, come per la difesa, ma con un altro obiettivo.

Come farlo, con quello che c'è già:
- Serve la distribuzione del **fantavoto**, non del voto. Scomporre:
  `fantavoto = voto + bonus`. Il voto è già modellato (`votoAtteso`); i bonus sono
  eventi discreti, e le frequenze stanno in `dati/statistiche.json`
  (`[partite, MV, FM, quotazione, gol, gol subiti, rigori parati, assist,
  ammonizioni, espulsioni]`). Con 3 giornate sono frequenze fragili: **è B1 che le
  rende solide**, quindi B3 va fatto dopo, o fatto prima segnalando l'incertezza.
- L'undici avversario c'è già: `sfidaDati(g)` costruisce il suo migliore e i due
  totali.
- Simulare i due totali con la macchina già scritta (`casuale` col seme fisso,
  `campioneVoti` da estendere al fantavoto) e contare le vittorie.

Il guadagno più immediato e onesto: in `renderSfida` la barra della sfida usa oggi
`Math.max(10, Math.min(90, 50 + diff*4))`, con il commento che ammette «la barra
esagera il vantaggio, per vederlo». **È un segnaposto dichiarato: lì va la
probabilità di vittoria vera.** E il consiglio per C e A diventa «massimizza la
probabilità di vincere», che a volte dirà di lasciare in panchina chi ha la
fantamedia più alta — e avrà ragione, sapendo spiegare perché.

**Fatto il 15/09/2026 sera** (scelte dell'utente: suggerimento, non cambio automatico
dell'undici; niente fattore campo; le fasce dei gol da leggere su Leghe):
- `probabilitaSfida(g)`: 2000 simulazioni (`SIMULAZIONI`, semi fissi: ripetibile) dei
  due undici di `sfidaDati`; per ogni giocatore il voto (`campioneVoti`, lo stesso del
  modificatore) più i bonus (`campioneFantavoti`: media e ampiezza che rendono giusti
  fantavoto atteso e ballo del modello); per ogni squadra il suo modificatore; i gol
  con `golDa` e `REGOLE_GOL`. Esito: vittoria, pareggio, sconfitta. Solo col modello.
- **`REGOLE_GOL` = primo gol a 66, poi uno ogni 5** (66, 71, 76, … 101 per l'8°):
  verificato dall'utente nelle impostazioni della lega su Leghe il 15/09/2026, con
  una schermata. La prima stima era «ogni 6»: sbagliata.
- si suppone che giochino tutti gli undici: la titolarità resta nel consiglio.
- in «La sfida» la barra a tre colori (vinci, pareggi, perdi) al posto di quella che
  esagerava il vantaggio (che resta solo senza modello), e «Vinci il 45% · pareggi il
  25% · perdi il 31%» (dati del 15/09, contro l'avversario della giornata 1, con le
  fasce vere; con «ogni 6» era 42/28/30).
- la simulazione suppone che giochino tutti: un giocatore «peggiore» nel consiglio può
  non esserlo nella simulazione, se lo è solo per la titolarità (il 15/09 Neres: 6,98
  contro 7,57 di Maldini nel consiglio, ma 6,69 contro 6,61 se gioca). Le prove
  controllano la media dei totali, non la vittoria, che può salire anche con un
  giocatore peggiore se balla di più.
- `suggerimentoSfida(g)`: un panchinaro di C o A al posto di un titolare dello stesso
  ruolo, solo se la vittoria sale di almeno 2 punti (`SOGLIA_SUGGERIMENTO`), il motivo
  è la varianza (da favorito il più regolare, da sfavorito quello che balla di più) e
  i due sono vicini nel punteggio del consiglio (entro 0,5, titolarità compresa: mai
  uno che rischia di non giocare). Confronti sugli stessi campioni. Il 15/09 nessuno.
- veloce: ~3 ms la probabilità, ~2 ms il suggerimento (misurato nell'anteprima).

### B4 — La voce dell'utente: **rimossa** (16/09/2026, scelta dell'utente)

Fatta la mattina del 16/09 (livelli 1 e 2) e tolta lo stesso giorno, dopo che l'utente
l'ha provata: «il riquadro del mio peso specifico sulla scelta non mi convince, voglio
toglierlo definitivamente ripulendo tutto». La ragione merita di restare scritta, perché
vale anche per idee future: chiedeva un giudizio **a mano, giocatore per giocatore, prima
di ogni giornata**. Scaricava cioè sull'utente il lavoro di insegnare a Jarvis una cosa
che Jarvis può osservare da sé.

**Fatto (sessione cloud, 16/09):** tolta tutta dall'app. Il riquadro nella scheda, il
blocco in «Il consiglio», il pollice dentro `punteggio`, la riga «tuo pollice» nel perché
dell'undici, le note nelle righe, il caricamento di `voce.json`, l'invio su ntfy
(`argomentoVoce`), il rientro in `aggiorna`, il gestore dei tocchi, gli stili, e
`voce.json` fuori da `PROTETTI`. Attenzione a una trappola incontrata facendolo:
`SENZA_POLLICE` è scritto tutto maiuscolo e sfugge a un `grep` di «pollice» senza `-i`.

**Finito sul PC, 16/09 sera:** tolti `scripts/voce.js`, `.github/workflows/voce.yml`,
`prove/voce.js`, `dati/voce.chiuso.json`, il passo in `prova.yml`, `voce.json` da
`PROTETTI` (in `lucchetto.js` e `privacy.py`) e da `.gitignore`, `mandaUno` in
`notifiche.js` (serviva solo alla risposta), l'argomento ntfy in `lucchetto.js` e la sua
prova, il finto ntfy in `prove/app.js`, le righe di questo file. In `aggiorna.py` e
`rose.py` non c'era niente: lì «voce» è solo il nome di una variabile. La nota dell'utente
arrivata su GitHub è in `archivio/voce/` (solo sul PC). **La derivazione della chiave del
lucchetto resta a 512 bit** anche se la seconda metà non serve più: cambiarla cambierebbe
la chiave dei file già chiusi. Sul telefono non c'è niente da togliere: l'argomento ntfy
veniva calcolato dalla password e non è mai stato registrato nell'app ntfy; in
`localStorage` può restare `jarvis-voce`, che l'app non legge più.

**Al suo posto, un'idea dell'utente, da valutare quando ci saranno i dati.** Invece di un
giudizio dichiarato prima, un giudizio **rivelato dopo**: quando Jarvis scarica la
giornata giocata, confronta l'undici che aveva proposto con quello davvero schierato, e
impara da dove l'utente diverge. Non costa niente a chi gioca. Due vincoli, da tenere
bene in vista prima di entusiasmarsi:

1. **Il dato non c'è ancora.** Jarvis non sa quale formazione è stata schierata: leggerla
   dal Chrome dell'utente è già nei lavori aperti e non è fatto. Senza, il confronto non
   ha ingressi.
2. **Le scelte non sono indipendenti dal consiglio.** L'utente sceglie *dopo* aver visto
   Jarvis. Se lo segue quasi sempre non c'è divergenza da cui imparare; quando diverge, lo
   fa spesso per ragioni che Jarvis non può vedere (una notizia, un'ultima ora). Il segnale
   utile non è «stavolta avevi torto», è «su questo tipo di situazione l'utente mi scavalca
   sistematicamente, e ha ragione» — e si vede su molte giornate, non su una.

Quindi stessa tempistica dell'autocalibrazione dei `PESI` (non prima di fine novembre), e
stessa avvertenza: prima di allora non direbbe nulla di sensato.

### B5 — Una vista sola per tutto il consiglio

Richiesta dell'utente: raccogliere queste viste (difesa, centrocampo/attacco, il
ragionamento dietro l'undici) in **una sovraimpressione a tutto schermo**, con lo
stesso stile ed effetti delle altre — sfondo sfocato dietro, come «Com'è andata»,
«Mercato» e «La stagione».

Non serve inventare nulla: `apriSovra(k, titolo, html, testo)` fa già esattamente
questo, e il quarto parametro accende il pulsante di condivisione nativo. Il
riquadro «La difesa» oggi sta nella schermata Giornata (`renderDifesa`, contenitore
`#difesa`): decidere con l'utente se **spostarlo** dentro la vista nuova o
**lasciarne un riassunto** nella Giornata con il resto nella sovraimpressione — la
seconda probabilmente è meglio, il modificatore atteso è informazione da colpo
d'occhio.

**Fatto il 15/09/2026 sera** (scelta dell'utente: riassunto più vista). Nella
Giornata, al posto del riquadro, una riga-invito in `#difesa` (`renderDifesa`):
«Il consiglio · La difesa: +2,0 atteso · Fascia più probabile +2 (32%)»; senza
voti misurati, «Il perché dell'undici»; senza né difesa né probabilità, niente.
Toccandola, `apriConsiglio()` apre «Il consiglio» (giornata e modulo) con tre blocchi:
- **La difesa**: il riquadro di prima, uguale, da `bloccoDifesa(g)` (`{m, alta, html}`).
- **La sfida**: barra a tre colori, «Vinci il X% · pareggi il Y% · perdi il Z%» e il
  suggerimento se c'è, da `probabilitaHtml(g)` — la stessa funzione che usa
  `renderSfida`, così i due punti non possono dire cose diverse. Senza modello il
  blocco non c'è.
- **Il perché dell'undici** (`righePerche(g)`): per ogni titolare, reparto per
  reparto, il punteggio del consiglio scomposto — base, in casa, avversario, squadra
  e la titolarità col suo contributo (`−0,4 + 1,6·perc`, lo stesso di `punteggio`);
  senza modello il motivo in breve (`breve`). Toccando un nome sale la scheda.

Con il pulsante di condivisione: undici, modificatore atteso e probabilità in testo.
I contributi che arrotondano a zero si scrivono «0,0» senza segno (anche nella
scheda del giocatore): «−0,0» sembrava un malus.

## Stato dei lavori (aggiornato al 16/09/2026, notte)

**Per chi riprende, sul PC o da una sessione cloud (Cowork)**: leggere prima questa
sezione, poi «Il lucchetto» e «Lavoro da remoto». La storia di git è ripartita il 16/09
da un commit solo: **una sessione cloud deve clonare da capo `origin/main`**, un clone o
un branch di prima non combacia più. Senza la password il cloud non vede i dati della
lega e le prove che li leggono non girano (quasi tutta `prove/app.js`): o l'utente mette
`JARVIS_CHIAVE` nelle variabili d'ambiente della sessione cloud (dalle impostazioni, mai
in chat), o il cloud lavora su codice, grafica e documenti e le prove le fa il PC prima
del push. `remoto/patch/` resta la cassetta della posta.

### Fatto (pubblicato e verificato)
- **B1** lo storico dei voti dal 2015-16 (`dati/storico/`, 114.111 righe).
- **B2** il fantavoto atteso: `scripts/modello.py` → `dati/modello.json`, riaddestrato a
  ogni giro; lo usano consiglio, voto del modificatore, mercato e «Chiedi».
- **B3** la probabilità di vittoria nella sfida (fasce dei gol della lega: 1° a 66, poi
  uno ogni 5, verificate dall'utente) e il suggerimento per varianza.
- **B5** «Il consiglio» a tutto schermo (difesa, sfida, perché dell'undici); nella
  Giornata il riassunto.
- **B4, livelli 1 e 2** (la tua voce): fatti e **tolti** il 16/09 su scelta dell'utente,
  dall'app (patch 0015, cloud) e da tutto il resto (PC). Vedi la sezione B4.
- **Il lucchetto**, attivo: dati della lega cifrati, nomi delle altre squadre fuori dai
  file pubblici (controllato da `prove/privacy.py`, dal 16/09 sera anche dentro i file
  Excel), storia azzerata (copia sul PC).
- **Avvio più svelto** (patch 0016): il mercato fuori dal primo disegno, da 598 a 321 ms
  in locale. **Panchina compatta** (patch 0017), una riga per giocatore.
- Verificato il 16/09: le prove su GitHub aprono il lucchetto col Secret; l'utente è
  entrato dall'iPhone con la password; **il primo giro di `aggiorna.yml` col lucchetto
  (12:45) ha aperto e richiuso**, e nel commit non c'era nessun file della lega in chiaro.
  Le patch 0015-0017 provate sul PC coi dati veri, compresa la parte che il cloud non
  poteva coprire (mercato, import della classifica).

### Aperti, in ordine
1. **Dopo la prima giornata (20/09)**: al primo «dati di lega», il formato dei risultati
   del calendario (i gol, mai visto su una giornata vera; l'import si ferma da solo se non
   torna); poi la **formazione schierata** dal Chrome dell'utente, per «La stagione». Ora
   conta di più: è il dato su cui poggia l'idea che ha preso il posto della voce (vedi B4).
   Col lucchetto: `apri` prima, `chiudi` dopo gli import e prima del commit.
2. **Il parere dell'utente** su com'è andata, andamento e calendario dei tuoi (funzioni
   del 15/09; il mercato è già stato rivisto), su «Il consiglio», sull'avvio e sulla
   panchina nuova, e sulla scheda col fantavoto atteso.
3. **La grafica**: il piano del 13-14/09 è completo; altre migliorie si concordano (non
   riproporre «Non disponibili» compatti né «Quando giocano i tuoi» per giorno: l'utente
   li ha già scartati, vedi la sezione della patch 0017).

### Da vedere nel tempo
- **B4, livello 4: l'autocalibrazione dei `PESI`**, non prima di mezza stagione (fine
  novembre 2026). Materiale già raccolto da solo: «Quanto si avvicina Jarvis» in «La
  stagione» e i consigli salvati, anche col calcolo di prima. Assorbe il vecchio lavoro
  «verificare i pesi del consiglio».
- **Il modello (B2)** si riaddestra da solo: ogni tanto guardare la verifica in
  `dati/modello.json` (`usa` per ruolo: un ruolo usa il modello solo se batte il calcolo
  di prima).
- **Fine stagione 2026-27**: aggiungere la stagione allo storico (`STAGIONI` in
  `scripts/storico.py`).
- **Rose**: dopo scambi e mercato (soste, gennaio) la routine «rose aggiornate» dal PC,
  poi `chiudi`.
- **Cambiare la password del lucchetto**: oggi non c'è un comando (`inizia` rifiuta se il
  lucchetto c'è già). Se servirà: un `cambia` in `lucchetto.js` che apre con la vecchia e
  richiude tutto con la nuova, poi la nuova nei tre posti.
- **Il giudizio «rivelato»** (l'idea dell'utente al posto della voce, vedi B4): imparare
  da dove l'undici schierato si discosta da quello proposto. Non prima di avere la
  formazione schierata e un po' di giornate: stessa tempistica dell'autocalibrazione.

## Come si prova

Le prove sono in `prove/` e vanno lanciate prima di ogni consegna (dal
15/09/2026 girano anche da sole, a ogni push e pull request:
`.github/workflows/prova.yml`):

```
node scripts/lucchetto.js apri     # col lucchetto: prima le copie in chiaro
node prove/lucchetto.js
node prove/app.js
python prove/orari.py
python prove/script.py
python prove/rose.py
python prove/lega.py
node prove/notifiche.js
python prove/privacy.py
python prove/modello.py
```

**Il totale delle verifiche cambia col posto, ed è giusto così** (accertato il
15/09/2026). Alcune prove girano solo se ci sono i file veri esportati da Leghe,
che stanno in `archivio/` e sono fuori da Git. Quindi:

- **sul PC dell'utente** (che ha `archivio/`): `prove/app.js` 307/307 e
  `prove/lega.py` 34/34 (dal 16/09 sera: la voce tolta ha portato via 13 verifiche)
- **su un clone pulito o nella CI** (senza `archivio/`): 306/306 e 31/31, perché
  saltano «il file vero di Leghe si legge uguale (solo sul PC)» e le tre di
  `lega.py` sulla stessa cosa
- `prove/privacy.py` 5/5 finché il lucchetto non è attivo, 8/8 dopo (le tre sul
  lucchetto); `prove/lucchetto.js` 22/22

Un numero più basso lì **non è un guasto**: è una prova saltata perché manca il
file, non una fallita. Le fallite si contano a parte e si vedono come `NO`.

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
Sul PC `python3` è solo l'alias del Microsoft Store e non parte: si usa `python`.
Sul PC dell'utente Norton Antivirus intercetta le connessioni HTTPS con un suo
certificato, che Python non riconosce: si lancia con il pacchetto `truststore`,
senza toccare lo script.

```
python -c "import truststore, runpy; truststore.inject_into_ssl(); runpy.run_path('scripts/aggiorna.py', run_name='__main__')"
```
