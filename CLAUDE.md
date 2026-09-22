# Contesto per Claude Code

Leggi questo file prima di toccare qualsiasi cosa. È la versione **snella** (dal
21/09/2026): regole, struttura, come si lavora. Lo stato di oggi (fatto, aperto, cosa
vedere nel tempo) sta in **`STATO.md`**, da aggiornare a ogni sessione. Il perché delle
scelte, le indagini fatte, le idee scartate e le date stanno in **`STORIA.md`**: non si
carica a ogni sessione, **si legge prima di riaprire una questione** o quando serve sapere
come mai qualcosa è fatto così; le note storiche nuove, datate, vanno in fondo lì.

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
  «Quando giocano i tuoi»**, **il promemoria della Lista calciatori**: tolti su richiesta.
- **Punteggi sul duello individuale** (chi marca chi): precisione finta, non farli.
- **Crediti rimasti**: all'utente non interessano, non si mostrano.
- **`backdrop-filter`** da alleggerire e **icona da ricomprimere**: valutati, lasciati.

## Il lucchetto (dati della lega cifrati)

Attivo dal 16/09/2026. I dati **della lega** — `base.json` (rose e calendario),
`lega.json` (classifica e risultati), `consigli.json` — nel repository stanno solo chiusi,
in `dati/<nome>.chiuso.json`. I dati da fonti pubbliche restano in chiaro.

- AES-GCM 256, IV casuale, nome del file come dato associato; chiave da PBKDF2-SHA256,
  600.000 iterazioni, sale e «prova» in `dati/lucchetto.json` (pubblico). Stesso formato in
  `scripts/lucchetto.js` (Node) e in `index.html` (Web Crypto), senza librerie. La
  derivazione resta a 512 bit: cambiarla cambierebbe la chiave dei file già chiusi.
- **La password** la conosce solo l'utente (≥ 12 caratteri): app Password dell'iPhone,
  Secret `JARVIS_CHIAVE` su GitHub, sul PC `C:\Users\<utente>\.jarvis-chiave` (anche
  `.txt`) o la variabile `JARVIS_CHIAVE`. **Mai in chat, mai nel codice, mai stampata.**
- Copie in chiaro in `.gitignore`. `node scripts/lucchetto.js apri | chiudi | stato |
  inizia`. **Sul PC: dopo `git pull`, `apri`; dopo ogni import della lega, `chiudi` prima
  del commit.** `apri` non sovrascrive un file in chiaro cambiato senza `--forza`.
- `aggiorna.yml` apre all'inizio e richiude prima del salvataggio; `prova.yml` apre prima
  delle prove. Nelle prove e in `notifiche.js` il lucchetto «non c'è» (leggono le copie in
  chiaro). Nell'app: `chiaveSalvata`, altrimenti `chiediPassword`.
- `dati/jarvis.ics` resta in chiaro, senza il nome dell'avversario.
- Storia di git azzerata il 16 e il 17/09 (c'erano dati in chiaro); copie in
  `archivio/storia-fino-al-2026-09-1{6,7}.bundle`. Un clone di prima non combacia più.
- Manca un comando per cambiare password (`inizia` rifiuta se il lucchetto c'è): se
  servirà, un `cambia` che apre con la vecchia e richiude con la nuova.

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
  riga (cartella OneDrive). Verifica: `git diff --ignore-cr-at-eol --stat` vuoto → `git
  restore .`. Da fare prima di `git am`. `.gitattributes` normalizza a LF (tranne
  `dati/*.ics`, CRLF per RFC 5545).
- Un `.git/index.lock` lasciato da una sessione cloud lo toglie Claude Code sul PC; dal
  cloud, dentro la cartella collegata, niente comandi git che scrivono.

## Struttura

```
index.html              app completa (HTML, CSS, JS in un file solo)
font/                   Barlow Condensed woff2 (600, 700) + licenza OFL: niente dipendenze esterne
img/                    icona (Re Guyzo), sfondo (lo stemma), avvio/ (immagini d'avvio)
manifest.webmanifest    nome, colori e icone
sw.js                   service worker: prima la rete, poi la copia salvata (cache `jarvis-3`;
                        se cambia la lista dei file fissi, `jarvis-4`)
dati/base.json          rose, calendario lega, calendario Serie A, statistiche (chiuso)
dati/lega.json          classifica e risultati di lega (chiuso)
dati/consigli.json      l'undici consigliato salvato prima di ogni scadenza (chiuso)
dati/infortuni.json     automatico
dati/titolari.json      automatico: probabili della prossima giornata e indisponibili
dati/orari.json         automatico: orari, primo e ultimo calcio d'inizio, `partite`
dati/squadre.json       automatico: rendimento casa/fuori, quest'anno e l'anno scorso
dati/statistiche.json   automatico: partite, MV, FM, quotazioni, bonus; `iniziali`
dati/voti.json          automatico: voto e fantavoto di ogni giornata finita
dati/listone.json       elenco ufficiale, per gli script
dati/notifiche.json     codici degli avvisi già inviati
dati/jarvis.ics         calendario da sottoscrivere sull'iPhone
dati/storico/           voti dal 2015-16, una stagione per file compresso (non per l'iPhone)
dati/modello.json       il modello del fantavoto atteso (B2)
dati/lucchetto.json     sale, iterazioni, prova cifrata
scripts/aggiorna.py     il giro automatico dei dati
scripts/importa_rose.py rose da Leghe (xlsx) in base.json
scripts/importa_lega.py classifica e risultati da Leghe in lega.json
scripts/notifiche.js    avvisi sull'iPhone (Web Push o ntfy) e salvataggio del consiglio
scripts/storico.py      giro una tantum e ripartibile dello storico (B1)
scripts/modello.py      addestra il modello (B2), nel giro automatico
scripts/lucchetto.js    apri | chiudi | stato | inizia
archivio/               file di Leghe già importati, bundle della storia (solo PC, fuori da Git)
prove/                  prove automatiche
.github/workflows/      aggiorna.yml (tre volte al giorno, dopo le probabili delle 11:30 e 19:30),
                        prova.yml (a ogni push e pull request)
```

Codice e dati separati di proposito: non reincorporare i dati nell'HTML.

## Identificativi

Ogni giocatore ha l'**Id ufficiale del listone Fantacalcio** (es. Svilar = 5841): unisce
rose, statistiche, infortuni, probabili, voti e storico. **Non introdurre altri
identificativi.** Gli Id sono stabili tra le stagioni (verificato).

## Dati a mano: rose e «dati di lega»

- **Rose** (dopo scambi e mercato): file `rivoluzione-fantacalcio-rosters-<numero>.xlsx`
  da Leghe (sul PC; dall'app iPhone non si esporta). `python scripts/importa_rose.py
  --prova` (mostra gli scambi senza scrivere), poi senza `--prova`, poi `chiudi`, prove,
  commit. Il file passa in `archivio/rose`. Nel file niente Id: le squadre si riconoscono
  dai giocatori in comune (≥ 13), i giocatori dal nome (rosa attuale, poi listone). Jarvis
  usa i nomi delle squadre dell'app di Leghe (`--nomi-app`). Controlli: 10 × 25 (3/8/8/6),
  ruoli coerenti, nessun doppione. Serve `openpyxl`, solo sul PC.
- **Routine «dati di lega»** (l'utente scrive «dati di lega» o «rose aggiornate»): dal
  **Chrome dell'utente** (Claude in Chrome), già collegato a Leghe:
  - rose: `/rivoluzione-fantacalcio/view/rosters/<id>` → «Esporta XLSX»
  - calendario: `/rivoluzione-fantacalcio/calendario` → «SCARICA ORA»
  - classifica: `/rivoluzione-fantacalcio/classifica` → «SCARICA ORA»

  I pulsanti si cliccano sulle **coordinate** (il riferimento dell'albero non scarica); dopo
  «Esporta XLSX» **niente screenshot per ~15 s** (la pagina si blocca). Poi
  `importa_rose.py --prova` e `importa_lega.py` (classifica e risultati, in upsert: le
  giornate già salvate non si perdono), file in `archivio/lega` con la data, `chiudi`.
  Il calendario può chiamare le squadre in modo diverso: `mappa_nomi_calendario` le
  ricava dalla posizione; il risultato si accetta solo scritto «N-N».
- **Dal telefono**: scheda Lega → «Importa da Leghe» (`leggiXlsx` con
  `DecompressionStream`, `classificaDaRighe`) salva **solo sul telefono** (localStorage
  `jarvis-lega`). Perché i risultati arrivino a GitHub serve «dati di lega» dal PC.

## Dati automatici (`scripts/aggiorna.py`)

- **Statistiche e quotazioni** dalle pagine pubbliche di fantacalcio.it (per Id dal link;
  ≥ 400 giocatori per scrivere), con gol, gol subiti, rigori parati, assist, cartellini e
  `iniziali` (quotazione iniziale, per il modello).
- **Voti** (`/voti-fantacalcio-serie-a/2026-27/N`): ogni giornata finita da ≥ 6 ore, voto
  e fantavoto della redazione Fantacalcio; riscaricata per tre giorni; < 200 voti non si
  salva. `righe_voti()` legge anche l'Id dai link delle stagioni passate (`ID_GIOCATORE`).
- **Probabili** da fantacalcio-online (`/it/serie-a/2026-2027/probabili-formazioni/N-giornata`):
  percentuale media di quattro redazioni, e gli **indisponibili della giornata**; usate
  **solo se la giornata coincide** con quella mostrata. La pagina `consigli-fantacalcio/...`
  dà solo le formazioni tipo: mai per la titolarità.
- **Orari** da fixturedownload.com: partite a mezzanotte UTC = orario non ufficiale
  (`"ufficiale": false`, l'app scrive «orario non ancora ufficiale», non stima).
  **Scadenza della formazione: 15 minuti prima del primo anticipo.** La giornata mostrata
  passa alla successiva due ore dopo l'ultimo calcio d'inizio.
- **`jarvis.ics`**: una scadenza per giornata con orario ufficiale, avviso 2 ore prima, UID
  stabili; senza scadenze il file non si riscrive (l'iPhone cancellerebbe gli eventi).
- **Rendimento delle squadre** (`squadre.json`): casa e fuori; il peso di quest'anno cresce
  fino alla decima partita; le neopromosse usano la media delle tre retrocesse (segnalata
  come stima).
- **Dati vecchi**: nel workflow il salvataggio ha `if: always()` e il giro fallito è rosso;
  nell'app l'intestazione diventa rossa oltre 4 giorni (`GIORNI_VECCHI`).
- **Notifiche** (`scripts/notifiche.js`, nel workflow): esegue il codice dell'app sui dati
  nuovi, manda solo gli avvisi mai inviati (≤ 6 per giro). Canale principale **Web Push**
  (Secret `PUSH_ISCRIZIONE`, `PUSH_CHIAVE`; pubblica `CHIAVE_PUSH` in `index.html`; al tocco
  apre Jarvis), di riserva **ntfy** (Secret `NTFY_ARGOMENTO`). Mai argomento, iscrizione o
  chiave privata nei file; un errore non fa fallire il giro. Prova: Actions → *Aggiorna
  Jarvis* → *Run workflow* con la notifica di prova.

## L'app, pagina per pagina

Barra in basso: **Giornata · Rosa · Stagione · Lega**, stile Liquid Glass (lente
trascinabile), campanella degli avvisi in alto a destra. Le sezioni che chiedono spazio si
aprono in **sovraimpressione** (`apriSovra(k, titolo, html, testo)`: il quarto parametro
accende «Condividi» se c'è `navigator.share`); nella pagina resta una riga-invito.

- **Giornata**: conto alla rovescia con barra del tempo; testata con il punteggio vero al
  posto di «VS» quando c'è il risultato (`risultatoLega`); **cinque tessere dei moduli**
  (`renderModuli`, `disegnoModulo`, totale atteso con `totaleModulo`, nastrino
  «consigliato» con `moduloConsigliato`, «NO MOD.» sulle difese a tre; all'apertura resta
  4-3-3); il **campo** (proporzioni vere, `posizione()`, maglie SVG da `MAGLIE` — un club
  nuovo va aggiunto, una prova lo controlla); **panchina** per reparto (`rigaPanchina`);
  **non disponibili** (`cartaKo`, `apriNonDisponibili`: quello che le fonti non dicono è
  scritto che manca); **Quando giocano i tuoi** (`renderQuando`); **La sfida, sulla carta**
  (`sfidaDati`, `renderSfida`, con la probabilità di vittoria); **Il consiglio**
  (`apriConsiglio`: la difesa, la sfida, il perché dell'undici); **Com'è andata**
  (`comeAndata`, `apriComeAndata`); in fondo «versione del …».
- **Scheda del giocatore** (`apriGiocatore`): statistiche, titolarità, partita, il riquadro
  del fantavoto atteso con ± e le sue voci (`cartaAtteso`), andamento (`graficoVoti`),
  prossimi 3 avversari (`prossimi3`).
- **Rosa**: vista maglie o elenco (`jarvis-rosa-vista`), filtri Tutti / Disponibili / In
  dubbio / Fuori (`statoRosa`), in fondo «La rosa in numeri» (`#rosa-numeri`).
- **Stagione** (`renderStagione`, `htmlStagione`): Affidabilità di Jarvis
  (`bloccoAffidabilita`, `accuratezzaConsiglio`, livelli in `LIVELLI_AFFIDABILITA`), In
  lega (`bloccoLega`, `posizioniLega`), Tu/Jarvis/massimo (`confrontoGiornata`), Giornate
  di lega (`graficoLega`, `stagioneSel`, `giornataLega`), Gli 11 della giornata
  (`apriUndiciGiornata`, `cellaVoto`), Chi produce (`apriProduttori`). Tocchi da
  `toccaStagione`; numeri interi senza «,0» (`numCorto`).
- **Lega**: classifica con la forma (`forma`, `esitoLega` dai gol, `pallinoForma`,
  `LETTERA_FORMA`: W verde, = giallo, L rosso), punti in `.cl-pt`, calendario, **Mercato**
  (`mercato`, `apriMercato`, disegnato dopo il primo disegno).
- **Avvisi** (campanella): stato dei dati, «Aggiorna i dati», elenco dal più urgente;
  numero sull'icona (Badging API, `numeroIcona`; cache `jarvis-numero` in `sw.js`).

**Grafica**: colori del Burkina Faso in `:root` (`--bf-rosso`, `--bf-verde`,
`--bf-stella`, accento `--accento`); titolo JARVIS in SVG; sfondo `img/sfondo.jpg` con velo
scuro; Liquid Glass (`--vetro-liquido`, `--vetro-bordo`, `--vetro-luce`, `--vetro-sfoca`)
su carte e riquadri; `.blocco.scuro` sulle zone chiare dello stemma; colori delle squadre
(`COLORI_SQUADRE`, per posizione alfabetica, lontani da oro, stella, rosso e verde) e
stemmi (`stemma`). Volti: Re Guyzo si vede, i ritratti dello stemma sono sfocati.
Animazioni solo CSS/JS, spente con «Riduci movimento»; gesti iPhone (trascinare per
chiudere, scorrere per cambiare scheda, non dal bordo). Le immagini d'avvio e l'icona
l'iPhone le riprende solo togliendo e rimettendo l'app sulla Home.

## Il motore del consiglio

- **Punteggio** = fantavoto atteso se gioca (`attesoModello`, da `dati/modello.json`) +
  titolarità (da −0,4 a +1,2, `−0,4 + 1,6·perc`; senza probabili si stima dalle presenze).
  Un ruolo usa il modello **solo se in verifica batte il calcolo di prima** (`usa` nel
  file); altrimenti, e senza il file, vale `punteggioVecchio` (fantamedia stimata
  `(partite·FM + 5·attesa)/(partite + 5)`, titolarità, avversario con `PESI`).
- **Modificatore di difesa** (configurazione «Consigliata»: portiere + i 3 migliori
  difensori, sulla **media voto**): `<6` → 0, `≥6` +1, `≥6,25` +2, `≥6,5` +3, `≥6,75` +4,5,
  `≥7` +6, in `MODIFICATORE` (unica fonte). Si **simula** (`modificatoreAtteso`, Monte
  Carlo a seme fisso) sul voto atteso (`votoAtteso(p, g)`, dal modello tranne che per i
  portieri) e la difesa si sceglie **a blocco** (`bloccoDifensivo`). Senza voti misurati
  resta spento. Cache `CAMPIONI` e `BLOCCHI`, svuotate da `stimaVoti()`.
- **Probabilità di vittoria** (`probabilitaSfida`, 2000 simulazioni a seme fisso): voto
  più bonus per ogni giocatore, modificatore per squadra, gol con `REGOLE_GOL` = **primo
  gol a 66, poi uno ogni 5** (verificato dall'utente). `suggerimentoSfida`: un cambio in C
  o A solo se la vittoria sale di ≥ 2 punti (`SOGLIA_SUGGERIMENTO`) e i due sono entro 0,5.
- **Difesa a tre** (`conModificatore(mod)` falso): difensori uno per uno, niente
  modificatore. Migliore a posteriori (`miglioreUndici`) e mercato restano sui moduli a
  quattro (`MODULI_4`).
- **Panchina**: se un titolare non prende voto entra il primo panchinaro **dello stesso
  ruolo** nell'ordine inserito (`panchina(g)`, `puntiUndici`).
- **Mercato**: rosa sempre legale; 1 contro 1 **stesso ruolo**; 2 contro 2 con gli stessi
  due ruoli dati e ricevuti; un top (`intoccabili`) solo offrendone uno dei miei; alla pari
  a vista (quotazioni entro 15% o 2 punti; fantamedia non più bassa di 0,5); serve a tutti
  e due. Valore per la stagione (`valoreStagione` → `baseStagione`). Dettagli in STORIA.md.
- **Avvio**: il mercato va fuori dal primo disegno (`dopoIlPrimoDisegno`, con
  `requestIdleCallback`; nelle prove `setTimeout` non esegue niente, per questo c'è quello);
  i file di dati si leggono tutti insieme in `carica`.
- Noto e lasciato apposta: `PESI` pesa di più P e D anche col modificatore calcolato (non
  sposta le scelte; si ritara con l'autocalibrazione).

## Il cervello di Jarvis (B1–B5), in breve

- **B1** storico dei voti dal 2015-16 in `dati/storico/` (114.111 righe, `storico.py`; a
  fine stagione aggiungere la 2026-27 in `STAGIONI`).
- **B2** fantavoto atteso: `scripts/modello.py`, ridge per ruolo, voci in `VOCI`, verifica
  sulle ultime due stagioni, `dati/modello.json` riaddestrato a ogni giro.
- **B3** probabilità di vittoria e suggerimento per varianza (sopra).
- **B4** la voce dell'utente: fatta e **tolta**. Resta l'idea del giudizio «rivelato»
  (imparare da dove l'undici schierato si discosta dal consiglio), che richiede la
  formazione schierata.
- **B5** «Il consiglio» a tutto schermo, con il riassunto nella Giornata.

## Come si prova

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

Totali: sul PC (con `archivio/`) `prove/app.js` 311/311 e `prove/lega.py` 34/34; su un
clone pulito o nella CI 310/310 e 31/31 (saltano le prove sui file veri di Leghe: non è un
guasto). `prove/privacy.py` 8/8, `prove/lucchetto.js` 22/22. Le fallite si vedono come `NO`.

`prove/app.js` estrae lo `<script>` da `index.html`, lo esegue in Node con un finto DOM e
una `fetch` che legge da disco, e verifica i risultati reali: **ogni funzione nuova
aggiunge qui le sue verifiche**, e **ogni prova passa i propri dati** invece di leggere i
file veri che cambiano (due prove si sono rotte così il 21/09). Date con orologio finto e
`TZ=Europe/Rome`.

Sul PC: `python` (non `python3`, che è l'alias dello Store), Python 3.14 come il workflow.
Norton intercetta HTTPS: gli script che scaricano si lanciano con `truststore`:

```
python -c "import truststore, runpy; truststore.inject_into_ssl(); runpy.run_path('scripts/aggiorna.py', run_name='__main__')"
```
