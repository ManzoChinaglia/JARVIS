# Stato dei lavori — JARVIS

**PROSSIMA SESSIONE (26/10 sera, sessione al limite):** 1) l'utente decide quale totale mostrare nella sfida (proposta: quello del modello, come tessera, probabilità e fascicolo); 2) riferimenti grafici scelti con lui; 3) ricollaudo MANZO giro 2, l'ultimo (se BOCCIATO decide l'utente), copia di prova `archivio/mockup/app-g8.html`; 4) rebase su origin (main avanti 2, indietro 3), push solo su PROMOSSO. `dati/modello.json` non committato: lo ricostruisce il workflow con `altre_rose` dopo il push.

**AGGIORNAMENTO 26/10 sera (fine sessione):** dati di lega BF G4 / QI G3 importati e pushati (`979c2b0`). Totale unico (fantavoti + modificatore) in tessera, sfida, fascicolo. Difetti MANZO giro 2 corretti (stima grezza senza modello → BOCA ha la probabilità; 1X2 del fascicolo a 100; Duello opaco max 520px; nota sul campo; --dim schiarito). Commit locali `a295a58`, `7e28153` NON pushati. Collaudo MANZO giro 3 LANCIATO e non ancora tornato: se PROMOSSO, chiedere l'ok all'utente per il push; se BOCCIATO, fermarsi e portargli i difetti (max 2 giri, regola 12). Grafica direzione A (Apple Sports) scelta ma non iniziata: serve il sì dell'utente per scaricare 3-4 immagini di riferimento (solo PC).

## Prossimo
<!-- pannello «Punti aperti»: max 3 punti, una riga ciascuno; si aggiorna a fine sessione -->
Stato: in corso
1. Formazioni G8 definitive importate il 23/10 (BF 4 4-3-3 con Perrone, QI 3 4-4-2 con Rowe). Dopo le partite della G8 (dom 25/10): «dati di lega» per entrambe (QI: `importa_lega.py --lega qi <classifica.txt> <calendario.txt>`, PROCEDURE.md). Poi: verificare da una sessione cloud che si apra www.fantacalcio.it (domini aggiunti dall'utente il 23/10) e solo allora aggiornare CLAUDE.md e skill dubbio. «Ragiona con Jarvis» v3 FATTO 23/10 (`6154f2b`, prove 359/359): il fascicolo porta l'altra lega (salvata in localStorage quando si apre la sua Giornata, accoppiata per giornata di Serie A) e l'incastro tra le leghe, più i controlli da fare sul web; la skill dubbio ha il modo di ragionare concordato (verdetto prima, quote 1X2, scommessa/protezione, coperture tra leghe). Da provare sull'iPhone: aprire tutte e due le leghe nello stesso posto (app Home e Safari hanno memorie separate).
2. Cervello calcistico a 360°: fase A + news PUSHATI il 22/10 (`8dca4de`, giro manuale verde). Il 23/10 dopo il giro delle 19:45: controllare che `statistiche.json` abbia i rigori (12 campi). B1 scartato; B2-B3 alla ricalibrazione di fine novembre.
3. Simulatore degli esiti / partita condivisa (26/10, commit locale, NON pushato): push solo col sì dell'utente (cambia il consiglio: QI G8 modulo 5-3-2 → 4-3-3; G9 ancora senza quote). Prova G8 «come se non giocata»: I1.csv scaricato il 26/10 00:22 arriva solo al 19/10 (G7): football-data aggiunge la G8 in settimana, riscaricare e rifare. Prova G7 «come se non giocata» (26/10, ultime 10 partite in archivio, λ dalle quote pre-partita): esito più probabile 7/10, risultato esatto 1/10 (Roma-Genoa 2-0), Brier 0.571 (media storica 0.567); sbagliate Venezia-Napoli 1-0, Udinese-Lecce 0-3, Juventus-Lazio 0-3. In linea col banco, nessuna sorpresa. quote.py --calibra: frecce tolte dalle stampe (crash su console Windows). **MANZO 26/10: BOCCIATO** (esiti visibili solo negli appunti; G9 senza quote; BOCA senza probabilità; totali incoerenti tra chip/sfida/dossier, preesistente). Quote G9: non è un guasto, fixtures.csv di football-data alle 00:34 del 26/10 elenca ancora la G8; il workflow le prende appena escono. Fatto: dossier dice «quote della giornata non ancora uscite» (app 368/368). Mockup `archivio/mockup/esiti-1.html` (fuori da git; `?d=A` barra 1X2, `B` dal lato dei tuoi con porta inviolata, `C` pillole, `vuoto` avviso senza quote), 2 giri di cattura col pilota. Utente 26/10: base B, «grafica un po' basic» → aggiunte `?d=B1` (Tabellone: righe 1/X/2 con barra nel colore squadra, scudo Lucide per l'inviolata, oro se ho P/D) e `?d=B2` (Duello: numeri grandi ai lati, barra a 3 colori squadra, inviolate sotto); 2 giri, nessun difetto del pilota. **Scelta B2 «Duello» (26/10), messa nell'app** (`esitiQuando`, `coloreClub`, CSS `.qd*`, avviso `.qe-avviso` senza quote). BOCA senza probabilità: causa vera = `modello.json` copriva solo le rose BF; ora `modello.py` aggiunge le rose delle altre leghe (`altre_rose`, numeri BF identici, 250→285 giocatori); nella sfida una nota elenca chi resta senza modello. Prove app 371/371, script 120/120, modello 27/27, privacy 8/8. Copia di prova `archivio/mockup/app-g8.html` (orologio al 23/10, fuori da git). **Ricollaudo MANZO giro 1: BOCCIATO** (esiti nell'app ok, BOCA ok, Duello ok; restano: totali incoerenti, tessera 71,4 = fantavoto del modello contro sfida 80,2 = somma di `punteggio`, e probabilità da modello che contraddice i totali della sfida; grafica senza riferimenti scelti; fondo illustrato che passa sotto il Duello; 45+28+28=101 corretto con `cento3`, prove 372/372). Decisioni all'utente: quale totale mostrare, riferimenti grafici. Riferimenti reali (Sofascore, FotMob, Apple Sports) non ancora scelti con l'utente. **Banco «Jarvis contro le quote» (26/10, 2729 partite fuori campione 1920-2627):** nessun segnale batte le quote pre-chiusura (riposo, finalizzazione, fase di stagione, neopromosse peggiorano; chiusura −1,2e-3 Brier non significativo; xG solo 70 partite, da rifare con 2 stagioni). Unico scarto costante: favorito forte in trasferta sottoquotato (prevista 0,62, vera 0,69, 8 stagioni su 8) e vittoria in casa sopravvalutata di 1-3 punti: piccolo, non dimostrato fuori campione. Script in scratchpad (non conservati). Sezione sotto. (Prima qui: «Ragiona con Jarvis» del 17/10, non verificato sull'iPhone se il link apre l'app Claude e la copia negli appunti)

Altri punti aperti: grafica wow e sfida in tempo reale pushate (`657ecee`), resta la prova sul telefono; sfida in tempo reale: non provato che Leghe mostri l'avversario PRIMA della scadenza (verificare alla prossima; nessun automatismo, lo legge Claude quando l'utente scrive «formazione schierata»); una squadra della QI senza stemma; probabili: i 15 non abbinati controllati il 17/10, listone completo (603 = pagina quotazioni), 13 non sono nel listone ufficiale (non acquistabili), Fernandez A. del Venezia non verificabile; Romero D. del Parma ora abbinato con alias (fonte «ROMERO J»), dal 17/10.

(al 17/10/2026 sera — campo ridisegnato con avversario, consiglio ridotto al solo banner del modificatore (non cliccabile; vista e `apriConsiglio` tolti), mercato tolto, stemmi delle altre squadre come data URI in `dati/lega.json` → `stemmi` (cifrato; `importa_lega.py` li conserva), podio in Lega; prove 339/339)

## SIMULATORE DEGLI ESITI DI SERIE A — idea dell'utente (Opus, 26/10/2026), aspetta la sua decisione

**Richiesta (26/10):** Jarvis calcola anche gli esiti delle partite di Serie A (simulazione su un campione), lo si
prova su una giornata già giocata e, se ci va vicino, diventa un peso per i singoli giocatori.
**Cosa c'è già:** gol attesi da 1X2 e Over/Under 2,5 (`lambda_da_quote`, `dati/quote.json`, storico 2017-26), serie
«con quote» del modello tenuta per ruolo solo se `--verifica` migliora; simulazione della sfida (`probabilitaSfida`,
2000 giri) e suggerimento pavimento/soffitto da favorito/sfavorito (B3).
**Cosa manca:** la simulazione estrae voti e bonus **indipendenti per giocatore** (`campioneVoti`, `campioneFantavoti`,
seme per id): non c'è un risultato della partita condiviso dai compagni di squadra.
**Misura sullo storico (26/10, 2017-26, scarto dal fantavoto medio stagionale del giocatore, coppie di compagni nella
stessa partita):** correlazione D-P 0,23, D-D 0,14, C-D 0,11, A-A 0,11, A-C 0,11, A-P 0,05. Nelle formazioni vere
(BF G1-G4, QI G1-G3) le coppie della stessa squadra sono 1-5, quindi la varianza del totale sale del 2-10%
(stima con correlazione media 0,11): sotto la soglia di 1,1 concordata con l'advisor, salvo la BF della G1.
L'utente ha scelto di farlo lo stesso («anche se pesa poco»).
**Fatto il 26/10 (non pushato, aspetta l'ok):** dallo storico, regressione dello scarto di voto e fantavoto sui gol
fatti e subiti della squadra (fantavoto per gol fatto/subito: A +0,91/−0,08, C +0,46/−0,15, D +0,24/−0,27, P 0/−1,13);
dopo i gol la correlazione fra compagni resta ~0 (−0,15/+0,01): i gol spiegano tutto. In `index.html` `partitaCondivisa`,
`parteGol`, `esitoPartita`, `quotePartita`, `BETA_PARTITA` (dettagli in RIFERIMENTO.md); fascicolo con «Esiti delle
partite». `quote.py --calibra`: 3478 partite 2017-27, Brier 1X2 dai gol attesi 0,5669, quote nude 0,5653, sole
frequenze 0,6547; esito più probabile 55%; gol casa attesi 1,52 veri 1,46 (leggera sovrastima), porta inviolata
nelle fasce 10-30% sovrastimata di 2-3 punti. G8 provata come se non giocata: archivio quote fermo al 13/10, va
riscaricato I1 (download da confermare) per vederla. Effetto sulla sfida BF G8 (banco con dati veri al 24/10, 20.000 simulazioni): vinco
46,0 → 45,7%, pari 25,5 → 25,9%, perdo 28,5 → 28,4%; ballo del totale 5,60 → 5,94; correlazione fra i due totali
−0,003 → +0,026 (5 partite in comune); nessun suggerimento in tutti e due i casi. Con 2000 simulazioni (quelle
mostrate) il rumore è ±1 punto: il salto 24,9 → 27,5 dei pareggi visto a 2000 era rumore. Consiglio: BF G8 e G9
uguali; QI G8 modulo consigliato 5-3-2 → 4-3-3 (modificatore col blocco difensivo correlato). QI G8: nel banco la probabilità non esce né prima né dopo (3 avversari senza modello: Hainaut, Comuzzo,
Adopo), da controllare. Prove: app 367/367, script 120/120, tutte le altre verdi. MANZO: il pilota c'è (~/.claude/manzo/pilota_web.py, 24/10, sezione in CLAUDE.md);
primo collaudo lanciato il 26/10.

## CERVELLO A 360° — piano (Opus, 22/10/2026; si esegue con Sonnet)

**Richiesta dell'utente (22/10):** Jarvis deve avere conoscenza calcistica a 360°, da chiudere il prima possibile.
**Atlante fuori da Jarvis (deciso con l'utente, 22/10):** `calcio-atlante` esiste (R2 fatto, 70,7/100) ma sono eventi
Wyscout 2017-18 su come si muove il pallone; non dice chi gioca oggi, chi è in forma, chi tira i rigori. Resta a THE CLUB.

**Diagnosi (inventario 22/10):** il motore (`modello.py`, `VOCI`) sa solo storia del fantavoto, quotazione, casa,
avversario, attacco/difesa squadra (o quote), più la titolarità dalle probabili. **Non sa:** chi tira i rigori (la colonna
«Rig» delle statistiche è scartata in `statistiche()`; lo storico 2015-26 ha invece `Rigori segnati/sbagliati` per partita),
forma recente leggibile, turno infrasettimanale e coppe (turnover), allenatore/crisi, piazzati. Il fascicolo
(`dossierDi`, v1) passa a Claude solo atteso e % di gioco; la skill `dubbio` dice già di cercare sul web, ma senza un
elenco fisso di cosa controllare. Con 60 squadre-giornata il backtest non vede effetti piccoli: tutto ciò che non si
può misurare va **a Claude come fatto**, non nel motore.

**Divisione:** numeri nel motore solo se migliorano `modello.py --verifica` (storico di 11 stagioni); il resto è
contesto per Claude (fascicolo + skill), che ragiona con l'utente e verifica sul web.

**Fase A — subito, prima della G8 (solo dati pubblici già nel repo):**
- A1. Fascicolo v2 (`dossierDi`): per ogni giocatore dell'undici e della panchina gli ultimi 3 voti (da `voti.json`),
  rigori della stagione se ne ha calciati, e una riga in testa sul calendario del club (giorni alla partita dopo: G9 è
  un turno infrasettimanale dal 27/10 → rischio turnover). Prova in `prove/app.js`.
- A2. Skill `dubbio`: elenco fisso dei controlli a 360° sul nodo della scelta (rigorista e piazzati, turnover per coppe e
  infrasettimanali, allenatore/crisi/esonero, motivazioni di classifica, squalifiche e diffidati, condizioni dopo la
  nazionale), con fonte e ora.
- A3. `statistiche()`: tenere anche «Rig» (segnati/calciati) per giocatore, senza cambiare gli indici di oggi; prova in
  `prove/`. Serve ad A1 e a B1.

**Fase B — numeri, con misura:**
- B1. Voce «rigorista» in `modello.py`: quota dei rigori della squadra calciati dal giocatore nella storia pesata
  (dallo storico). Si tiene solo se `--verifica` migliora (fantavoto per ruolo, soprattutto C e A). Al locale (dati sul PC).
- B2. Indisponibile → compagni di reparto (ipotesi del 17/10), al backtest.
- B3. Passo 2 (valore atteso vero) e news rifatti alla ricalibrazione dei PESI di fine novembre, con più giornate.

**Fatto il 22/10 (non pushato, aspetta l'ok):** A1 fascicolo v2 (`dossierDi`: «ultimi fv», «rigori S/C», «rigioca tra N gg»
se ≤ 4; visto sui dati veri di entrambe le leghe, nessun undefined), A2 sezione «I controlli a 360°» nella skill, A3
`statistiche()` aggiunge in fondo `[rigori segnati, calciati]` (da «S / C»), l'app li legge con `v.length>=12`.
I rigori nel fascicolo compaiono dopo il primo giro di `aggiorna.yml` successivo al push. Prove: app 348/348, script
115/115, privacy 8/8. Il service worker prende la pagina sempre dalla rete: nessun cambio di cache.
**B1 CHIUSO 22/10, scartato** (il locale Bonsai non ha prodotto nulla in 4 min, fatto dal cloud e poi tolto): quota
pesata dei rigori della squadra calciati dal giocatore, calcolata prima di ogni giornata, come voce in più. `--verifica` su
2024-25 e 2025-26 (92.770 righe): fantavoto C 0,197 → 0,199, A 0,165 → 0,166, D 0,189 → 0,188, P uguale; con quote
C 0,213 → 0,215, A 0,190 → 0,193. Differenze alla terza cifra: non si tiene. Probabile perché il rigorista ha già il
fantavoto alto nella sua storia. Il rigorista resta un fatto per Claude (fascicolo v2 e skill), non un numero del motore.
**A4 news nel fascicolo, fatto 22/10 (in chiaro, decisione dell'utente: dati pubblici).** `aggiorna.py --news conoscenza/news`
(passo di `aggiorna.yml` dopo le quote, mai bloccante) scrive `dati/news.json`: ultimi 3 giorni dell'archivio privato,
solo `[data, tag, link]` (link solo fantacalcio.it), max 3 per giocatore (tutti i giocatori, non solo le rose) e per
squadra (le news senza giocatori). Mai titoli né testi. Il fascicolo mette per giocatore «news: GG/MM tag link» (max 2)
e una riga «News dei club» (1 per club dell'undici): Claude apre i link. Visto sui dati veri: BF 6 righe news, QI 3,
nessun undefined, ~4.100 caratteri. Prove: app 351/351, script 119/119, privacy 8/8.
**Chiuso quando:** A1-A3 in produzione prima della G8 e B1 misurato (tenuto o scartato). B2-B3 restano alla
ricalibrazione. **Fuori:** Atlante, xG, riassunti delle news dal locale (più avanti).

## Voti in ritardo dopo la giornata (20/10/2026)
Dopo l'import G7 «Com'è andata», Stagione (Tu/Jarvis/massimo, Gli 11, Affidabilità, Chi produce) e il grafico dei voti restavano alla G6: non era l'import, mancavano in `dati/voti.json` i voti della G7 di Serie A. `voti()` li scarica solo 6 ore dopo l'ultimo calcio d'inizio (19/10 18:45 UTC → dal 20/10 00:45 UTC); l'ultimo giro completo era delle 22:37 del 19/10 e quello delle 10:45 UTC del 20/10 GitHub lo stava ritardando (il giro delle 17:45 del 19/10 è partito alle 22:37). Risolto lanciando a mano *Aggiorna Jarvis* dal cloud (`3f8450e`, 288 voti della G7). **Per velocizzare (fatto, provato su Actions il 20/10, run 39417391755 verde):** `aggiorna.py --solo-voti` (`voti_mancanti()`: giornate finite da 6 ore a 3 giorni senza voti) nel giro leggero `probabili.yml` ogni 30 minuti; salva e manda le notifiche se cambiano `titolari.json` o `voti.json`. Se le probabili falliscono, lucchetto e salvataggio dei voti partono lo stesso (`89636bc`). Prove: script 114/114, tutte verdi. Di riserva resta: Actions → *Aggiorna Jarvis* → *Run workflow*.

## Dati di lega G7 (20/10/2026, fatto)
**Lettore QI e giornate di lega (20/10/2026, fatto):** `importa_lega.py` legge anche il testo delle pagine (`leggi_testo_classifica`, `leggi_testo_calendario`, stessi controlli, testi copiati in archivio); `leggi_calendario` vuole le giornate della lega (`len(base['g'])`, BF 34, QI 33). `leghe.json`: BF `prima_giornata_serie_a: 5`. `schiera.mancanti()` controlla le 2 ore sulla giornata di Serie A = lega + prima − 1; controllo a inizio sessione corretto in CLAUDE.md e PROCEDURE.md. Prove: lega 47/47 (testo, main, mancanti), tutte verdi. Pushato (al 22/10 `main` allineato a `origin/main`).

BF: classifica e risultati fino alla giornata di lega 3, rose senza cambi; un'altra squadra ora si chiama diversamente su Leghe (mappata da sola; il 20/10 Jarvis ha adottato il nome nuovo nei dati chiusi). Formazione BF giornata 3 c'era già (16/10). QI: classifica e risultati fino alla giornata 2 letti dal testo delle pagine («Scarica ora» non scarica, vedi PROCEDURE.md); formazione giornata 2 importata (4-3-3); rose senza cambi. `importa_rose.py`: nuovo formato del sito `Rose_<slug>.xlsx` (`blocchi_sito`) e `--lega`. Prove: rose 28/28, app 344/344, tutte verdi.

## «Ragiona con Jarvis» (17/10/2026, fatto)

L'app è statica senza backend né chiave API: non può chiamare Claude. **Soluzione scelta dall'utente: solo un bottone** (Giornata, sotto la sfida, `#ragiona`). Copia negli appunti il fascicolo (`dossierDi(g)`: regole della lega, moduli e valori, undici consigliato con fantavoti e probabilità di giocare, panchina, avversario vero o stimato, probabilità di vittoria) e apre `https://claude.ai/code`. In chat, sessione Code sul repo JARVIS (anche a PC spento): incolla, manda gli screen di Leghe (formazioni vere, tempo reale) e ragiona con la skill `.claude/skills/dubbio/SKILL.md` (autosufficiente, nel cloud solo ragionamento: niente commit, niente decifratura). Di riserva Remote Control verso il PC acceso. Scartato su richiesta: campo del dubbio, incolla della scelta, parser SCELTA.

**Dati nel fascicolo:** escono solo per mano dell'utente verso il suo account Claude, mai in un URL. **Ogni tocco apre una nuova sessione cloud** (da telefono non si cancellano, solo archiviano). **Idea per dopo:** cronologia delle scelte contro il risultato vero (giudizio «rivelato», STORIA.md B4).

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

**Fatto il 07/10 sera (non committato, in attesa dell'ok):**
- Selettore di lega in cima (`#lega-chip` + `montaSelettoreLega()` in `index.html`): pillola a destra del sottotitolo,
  menu a vetro con le due leghe, salva `jarvis-lega` e ricarica. Verificato in anteprima (mobile, `?lega=qi`).
- Tema QI in `leghe.json` (`tema {a:#B3173F, b:#2347A8}`, `stemma img/stemma-qi.png`): nome squadra e stemma cambiano.
  **Da decidere con l'utente**: lo sfondo (resta quello con la figura del Burkina) e il simbolo accanto al nome (★).
- `importa_formazioni.py` e `schiera.py` con `--lega <id>` (moduli validi ora 7); `importa_lega.py` con `--lega` (fatto io: Bonsai non ha prodotto nulla).
- `notifiche.js`: `mainTutte()` un giro per lega (consigli in `dati/<lega>/consigli.json`, codici avvisi `qi:…`, titolo con
  il nome della lega); prova nuova «seconda lega». `aggiorna.py` non cambia (Serie A condivisa); `jarvis.ics` resta quello della prima lega.
- CLAUDE.md: regola 1 a sette moduli e sezione multilega. Prove: app 327/329 (2 rosse di prima), notifiche 27/27, il resto verde.

**Fatto il 07/10 notte (pushato):** BF: stemma = logo preso da Leghe (`img/stemma-bf.png`, 256 px), sfondo senza sfocatura sui due ritratti
(volti del logo 256 px ingranditi e fusi in `img/sfondo.jpg`: morbidi, l'originale non è sul PC). QI: `img/sfondo-qi.jpg` con lo stemma, peperoncino infiammato al posto della ★,
nome in rosa/azzurro chiari (`tema.nome_a/nome_b`) per leggersi. Selettore rifatto: fascia a vetro nei colori della lega + menu a schede. Tessere dei moduli più snelle.
**Bug trovato e corretto:** con la difesa a 5 il modificatore toglieva solo il peggiore e dividendo per 4 la media usciva gonfiata (5-3-2 e 5-4-1 sempre consigliati): ora `treMigliori()` (3 migliori difensori). Prova nuova in `prove/app.js` (328/330, 2 rosse di prima).

**Fatto l'08/10:** stemma QI nitido (originale 1600 px ritagliato dal marmo: `archivio/qi/stemma-originale.png` e `stemma-ritagliato.png`, solo PC), `img/sfondo-qi.jpg` e `img/stemma-qi.png` rifatti (approvati dall'utente). `aggiorna.py`: `get()` con 3 tentativi sui timeout e `guasto()` (un guasto di sola rete non fa fallire il job: era la causa delle mail di errore, fixturedownload.com in timeout). Controllo job: `aggiorna.yml` copre già le due leghe (Serie A condivisa; titolari dal calendario della prima lega, che include tutte le giornate della seconda; `jarvis.ics` = stesse scadenze; notifiche per lega; `git add dati/` copre `dati/qi/`).

**Fatto l'08/10 (grafica, approvata dall'utente):** tessere dei moduli su una riga (7), tutte uguali; «NO MOD.» (blu) e «CONSIGLIATA» (verde) come pillole sul bordo alto; peperoncino QI ridisegnato con fiamme animate; stella del Burkina sfaccettata (`STELLA`); barra e pulsanti di vetro tinti coi colori di marca (`--tema-a/b`, `color-mix`); selettore di lega con sfumata e swipe (`vai()`, `--verso`, `jarvis-verso`). Scartato: pallino «da schierare» per lega (stesse scadenze, formazione non visibile prima della giornata). Prove: app 332/332.

**Da fare, in ordine:**
1. (fatto 08/10) tema QI e 7 moduli.
2. (fatto) `importa_lega.py --lega qi`: da provare sui file veri della prima giornata.
3. RIFERIMENTO.md (multilega) e, se serve, `aggiorna.yml` (nessun passo nuovo: `git add dati/` copre `dati/qi/`).
4. Prima partita: ricavare con `schiera.py --lega qi` la formazione di BOCA NDUJORS dalla giornata 1 (dopo la scadenza).
5. (fatto) commit e push. Prossima sessione: consigli grafici proposti all'utente (tema di lega su barra/pulsanti, transizione e swipe nel selettore, pallino «da schierare» per lega, sfondi più nitidi se si trovano gli originali, griglia moduli a 7 colonne) — scegliere con lui, con mockup.
**Attenzione:** dopo un `git pull` fare SEMPRE `node scripts/lucchetto.js apri` PRIMA di `chiudi`, altrimenti `chiudi`
ricifra copie in chiaro vecchie sopra i file chiusi più nuovi (successo oggi con consigli.chiuso.json, ripristinato).

## AGGIORNAMENTI PIÙ FITTI + ARCHIVIO NEWS — piano (Opus, 09/10/2026; si esegue con Sonnet)

**Richiesta dell'utente (09/10):** probabili lette di continuo (cambiano in fretta); news di stampa raccolte in un
repository di conoscenza calcistica, dall'inizio di questo campionato in poi. Repo privato e Chrome approvati.
Pesi: «valutiamo l'utilizzo», quindi per ora non si tocca il consiglio.

**Verificato il 09/10 (curl, senza login):**
- `fantacalcio.it/probabili-formazioni-serie-a`: le percentuali sono nell'HTML grezzo («aggiornate in tempo reale»).
  robots.txt vieta `/homesheet` e `/probabiliformazioniseriea` (la home): **usare solo questa pagina, mai la home**.
- fantacalcio-online (la fonte di oggi) fa già la media di **Fantacalcio.it, Gazzetta, SOS Fanta, Sky**.
  Fantacalcio.it non va aggiunto come 5ª voce (conterebbe due volte). Serve solo come segnale più fresco, se serve.
- News: `fantacalcio.it/news/calcio-italia?page=N` è il flusso fitto (convocati, ultime, infortuni: ~2 pagine al giorno,
  pag. 10 = 02/10). `.../serie-a` ha solo le cronache delle partite. Link con data e id: `/news/calcio-italia/09_10_2026/<slug>-<id>`.
  La sitemap non serve (punta a host interni `awslocal`).

**Pezzo 1 — probabili fitte (prima: la QI parte il 10/10):**
- `aggiorna.py --solo-titolari`: scarica solo le probabili e le notifiche. Niente modello, voti, statistiche.
  Esce subito se non si è nella **finestra della giornata**, calcolata da `orari.json` (dalla vigilia alla scadenza),
  così prende anche i turni infrasettimanali.
- Nuovo workflow (o job) con cron ogni 30 minuti a minuti dispari (`7,37 * * * *`: GitHub ritarda :00/:30), stesso
  gruppo `concurrency`, commit solo se `dati/titolari.json` cambia.
- Da controllare: `notifiche.js` deve mandare **un avviso per cambio** di titolarità, non uno per giro.
- Prove: `prove/` verdi più una prova della finestra (dentro/fuori/infrasettimanale). Il giro completo 3 volte al giorno resta com'è.
- **Fatto il 09/10 (non pushato, aspetta l'ok):** `aggiorna.py --solo-titolari` (`giornata_in_finestra`: da 36 h prima del primo calcio a 1 h dopo, da `orari.json`, nessun lucchetto), `.github/workflows/probabili.yml` (cron `7,37 * * * *`, stesso gruppo `concurrency`; lucchetto, notifiche e commit solo se `titolari.json` cambia), id dell'avviso «Probabili uscite» ridotto a «alcune/tutte» (prima uno per ogni squadra nuova). Prove: script 83/83, app 332/332, notifiche 27/27. **Listone (09/10 sera, commit locale, non pushato):** `aggiorna_listone()` all'inizio del giro completo aggiunge dalle quotazioni di fantacalcio.it i giocatori arrivati dopo l'asta (69 subito: Alaba, Darmian, Leao, Lukaku…; nome senza «*», squadra dal link, mai toccati gli Id vecchi). Non abbinati nelle probabili: 23 → 17 (restano nomi che la fonte delle quotazioni non ha, es. Israel, Dabo). Prove: script 86/86. **Da fare dopo il push del pezzo 1:** `gh workflow run probabili.yml` due volte e leggere il log (la prima scrive o dice «nessun cambiamento», la seconda deve dire «nessun cambiamento»); la prova in locale non è possibile (Norton blocca il certificato della fonte). Limite noto: un giocatore che torna dubbio dopo essere stato titolare non rinnova l'avviso (un avviso per giocatore e giornata).

**Pezzo 2 — archivio news: FATTO il 10/10/2026.** Repo privato `ManzoChinaglia/JARVIS-conoscenza` (ramo `master`, locale `Progetti\JARVIS-conoscenza`). `scripts/news.py`: legge `news/calcio-italia?page=N`, annota squadre/giocatori (listone di JARVIS da raw GitHub o `$JARVIS_DATI`; cognome condiviso conta solo se la squadra è citata) e tag (parole chiave, 8 etichette: poco precise, sono per cercare), salva in `news/AAAA/MM/GG.jsonl` (idempotente per id). Workflow `news.yml`: ogni 6 ore (`17 */6`), prime 4 pagine, commit solo se cambia; a mano con campo `da` per l'arretrato. Prova: `python prove/lista.py` (parser su pagina vera, annotazione, salvataggio, arresto su pagina ripetuta). **Arretrato girato su Actions:** 72 pagine, 1355 notizie dal 21/08 al 09/10, nessun errore. Limite: la data è quella nel link; il tag `conferenza` non scatta se manca «conferenza/dichiarazioni» nel titolo.
- Repo **privato** `JARVIS-conoscenza` (ManzoChinaglia), separato da JARVIS, che è pubblico.
- Formato v1, un file per giorno, `news/AAAA/MM/GG.jsonl`. Una riga per notizia: `id, data, titolo, sommario`
  (l'occhiello della lista), `link, squadre, giocatori` (Id del listone via `norm()`/`trova()` di `aggiorna.py`),
  `tag` (parole chiave: infortunio, squalifica, convocati, mercato, ballottaggio…). **Niente testo integrale**
  (copyright) e **niente LLM nella v1**: Groq ha un limite di 200k token al giorno.
- Arretrato: pagine all'indietro fino al giorno prima della 1ª giornata (da `orari.json`), con una pausa tra le richieste.
  Poi un giro al giorno in GitHub Actions nel repo privato.
- Chi lo legge: Claude e le analisi sul PC. **L'app pubblica mai**: al massimo segnali derivati (es. «2 notizie di
  infortunio in 48 h»), mai testo di articoli.
- Più avanti, facoltativo: riassunti fatti dal modello locale sul PC, non da Groq.

**Pezzo 3 — pesi (solo valutazione, insieme alla ricalibrazione dei PESI di fine novembre):**
domanda da misurare: «un segnale delle news (infortunio/ballottaggio) prevede chi non parte titolare meglio delle sole
probabili?». Fino a quella prova non si costruisce nulla nel motore.

## CERVELLO CALCISTICO — piano (Opus, 13/10/2026; si esegue con Sonnet)

**Richiesta dell'utente (13/10):** Jarvis ragiona «solo a numeri». Esempio: BF giornata 7, 4-3-3 con Pellegrino **e** Beto
(alternativi nella Fiorentina) contro il Como, con la Fiorentina in crisi. L'utente pensava di collegarlo all'Atlante di THE CLUB.

**Perché NON l'Atlante (per ora):** l'Atlante (`THE CLUB/docs/realismo.md`) è fatto di eventi e tracking di stagioni vecchie
e partite d'esempio: dice come si gioca il calcio, non chi gioca oggi né chi è in forma. Non esiste ancora (R0 non partito).
Resta in coda per Jarvis solo se un giorno ne esce un ingresso concreto (es. xG per tipo di tiro); oggi nessuno.

**Diagnosi misurata sull'app (13/10, G7, probabili non ancora uscite):**
- Pellegrino 7,81 e Beto 7,33 nel punteggio: entrambi tra i 3 attaccanti. Senza probabili `titolarita()` usa le presenze
  (`pgv` su partite della squadra): **chi entra dalla panchina conta come titolare** (Pellegrino 6/6 = 100%, Beto 4/6 = 67%).
- Il fantavoto atteso **ignora quasi la stagione in corso**: Pellegrino ha media voto 5,75 ma `base` 6,57 (storia
  pluriennale con `DECAD` 0,97 ≈ 33 presenze, più la quotazione). Contro il Como: avversario −0,07, squadra −0,04: la crisi
  della Fiorentina e la forza del Como quasi non si vedono (con 6 partite l'anno scorso pesa ancora il 40%, `perPartita`).
- La titolarità entra come somma (−0,4…+1,2), non come probabilità di giocare: due alternativi al 50% valgono quasi come due titolari.

**Passi, in ordine (ognuno con prova in `prove/` e con la verifica sullo storico dove si può):**
1. **FATTO 13/10 (commit locale, da pushare):** `registra_storico()` in `aggiorna.py` → `dati/titolari-storico.json` (G5-G6 recuperate dal git; si riempie a ogni giro); in `index.html` `titolaritaStorico()` (media pesata 3-2-1 delle ultime 3 probabili, «ultime probabili X%») e tetto dei posti del modulo abituale (`tenutiInsieme`, ballottaggi). Effetto G7: Beto fuori dal 4-3-3, Pellegrino resta al 67%. Prove: app 341/341, script 89/89. Limite: la fonte delle statistiche non dà le partite da titolare, quindi si usano le probabili (previsioni, non formazioni vere). Originale: **Titolarità senza probabili:** da presenze a **partite da titolare** (o minuti), se la fonte delle statistiche li dà
   (controllare `statistiche()` in `aggiorna.py`); altrimenti dalla storia delle probabili nel git di `dati/titolari.json`.
   Più la regola dei **ballottaggi**: due della stessa squadra e ruolo che si alternano non si contano titolari entrambi.
2. **CHIUSO 13/10, scartato: non migliora il backtest** (Modulo consigliato: −0,83 ± 0,50 fantapunti a squadra-giornata fuori campione, +0,17 ± 0,41 anche calibrando sulle stesse giornate; 60 squadre-giornata). Tornato al calcolo del passo 1 (`index.html` e `prove/app.js` di `f9d28e9`, 341/341). Misure, esito e sintomo del 5-4-1 (difetto di `sostituto`, ora moot) in **STORIA.md, 13/10/2026**. Il banco di prova è `prove/backtest.js` (`--confronta` per le differenze a coppie); l'esperimento resta nella storia di git. Rifare il test al passo 6.
   Originale: **Valore atteso vero:** punteggio = P(gioca) × fantavoto atteso + (1 − P) × chi entra dalla panchina, invece della somma.
   Si verifica sulle giornate salvate (consigli contro formazioni e voti veri, 2 leghe).
3. **CHIUSO 13/10, scartato: non abbassa l'errore** (`modello.py --verifica` su 2024-25 e 2025-26). Le voci «media delle ultime 5» e «stagione in corso», da sole o insieme, e `DECAD` da 0,99 a 0,80 spostano correlazione e rmse solo alla terza cifra, anche sulle sole prime 8 presenze della stagione (il caso della G7); attaccanti un po' peggio. Backtest delle formazioni non fatto: differenze così piccole non si vedono su 60 squadre-giornata (±0,5) e integrarle in `index.html` costerebbe codice per misurare rumore. Nessun file del progetto toccato tranne STATO e STORIA. Numeri in **STORIA.md, 13/10/2026 (passo 3)**.
   Originale: **Forma della stagione in corso:** misurare sullo storico (le stagioni tenute da parte in `modello.py --verifica`) se una
   voce «media delle ultime 5» e un peso della stagione in corso più alto abbassano l'errore. Si tiene solo se migliora.
4. **MISURATO 13/10: le quote MIGLIORANO il modello, da integrare (prossima sessione).** R0 fatto: nessuna licenza scritta («My data is free»); `robots.txt` aperto ai programmi generici ma blocca i crawler AI (ClaudeBot compreso, «Block major AI training models»): l'utente ha deciso di procedere (uso personale, modello lineare, non addestramento). **CSV grezzi MAI nel repository pubblico**: stanno in `archivio/football-data/` (I1 2017-18…2026-27, più `patch.py`/`patch2.py` dell'esperimento); in `dati/` solo numeri ricavati. Gol attesi per squadra dalle quote medie pre-chiusura (`Avg*`, `BbAv*` fino al 2018-19; mai le `C` di chiusura): totale dal più/meno 2,5, divisione dall'1X2. Verifica (fantavoto, corr): P 0,217 → 0,266, D 0,189 → 0,210, C 0,197 → 0,213, A 0,165 → 0,190; voto D/C/A +0,02-0,04; uguale sulle prime 8 presenze. «Al posto» di avversario/attacco/difesa ≈ «in aggiunta». Dettagli in STORIA.md 13/10 (passo 4).
   **Piano di integrazione (da fare, poi backtest):** (a) `scripts/quote.py` (truststore, controllo di plausibilità): scarica `I1.csv` della stagione e `fixtures.csv`, calcola i gol attesi, scrive `dati/quote.json` (giornata, casa, trasferta, gol attesi: solo numeri ricavati); storico 2017-26 calcolato una volta da `archivio/` in un file ricavato che legge `modello.py`; (b) **DECISO (Opus 13/10): due serie di coefficienti in `modello.json`**, «con quote» (variante «sost»: voci «attacco quote», «difesa quote» al posto di avversario/attacco/difesa) e «senza quote» (quella di oggi); l'app sceglie partita per partita secondo cosa c'è, `usa` calcolato per ognuna. Senza quote (quasi tutta la settimana) l'app resta identica a oggi: niente ripiego mai provato. Verifica divisa per stagione già fatta: il guadagno c'è sia nel 2024-25 (fantavoto P 0,233 → 0,301, A 0,177 → 0,198) sia nel 2025-26 (P 0,198 → 0,232, A 0,147 → 0,180), in tutti i ruoli; (c) `index.html` legge `dati/quote.json`; (d) backtest G5-G6 con le quote d'epoca del file 2026-27; (e) orari: quote del venerdì entro le 17 UK (18 in Italia), martedì entro le 13 per i turni infrasettimanali: il giro di `aggiorna.yml` delle 19:45 (ora legale; 18:45 con la solare, cioè 17:45 UK) cade dopo le quote e prima dell'anticipo delle 20:45: va bene; con l'ora solare il margine è stretto (le quote «entro» le 17 UK). Prima di allora vale la serie «senza quote»; (f) il workflow automatico scarica da GitHub Actions: va bene (user agent normale), ma decidere con l'utente.
   **Indicazioni dell'utente (13/10):** (g) mostrare sempre la differenza «senza quote → con quote» (come nell'esempio di Bonny e Martinez L. in STORIA, passo 4), con le quote aggiornate; (h) le quote si agganciano alle partite del calendario Serie A che c'è già (`dati/orari.json`: giornata, casa, trasferta), niente calendario nuovo; (i) **sul PC si conservano tutti i file scaricati, mai cancellare i vecchi**: ogni `fixtures.csv` e `I1.csv` salvato in `archivio/football-data/` con data e ora nel nome, per avere lo storico e l'evoluzione delle quote (fuori da Git).
   **FATTO 13/10 sera (non committato, aspetta l'ok):** (a) `scripts/quote.py` (offline provato sul file 2026-27; il download `I1.csv` + `fixtures.csv` aspetta l'ok dell'utente; copie in `archivio/football-data/` come `<nome>_AAAA-MM-GG_HHMM.csv`, mai sovrascritte) → `dati/quote.json` (60 partite G1-G6, aggancio per coppia casa-trasferta a `orari.json`, nomi tutti corrispondenti) e `dati/quote-storico.json.gz` (2017-26, per `modello.py` su Actions; NON in `dati/storico/`: il glob delle stagioni lo leggerebbe). (b) `modello.py`: `fantavoto_quote`/`voto_quote` accanto alle serie di sempre (che non cambiano), `verifica_quote` a coppie sulle stesse partite, `usa` per ruolo; riproduce i numeri di STORIA (P 0,217 → 0,267, D 0,189 → 0,210, C 0,197 → 0,213, A 0,165 → 0,190). `index.html`: `contestoQuote`, `attesoModello` sceglie la serie per partita e restituisce `quote` e `senza`; senza quote.json o per una partita senza quote l'app è identica a prima. Prove: app 350/350, modello 27/27, script 102/102 (le 13 nuove di quote.py scritte dal cloud: Bonsai in 50 min non aveva prodotto nulla), privacy 8/8; `quote.py` non svuota mai `quote.json` (unisce per coppia) e parte anche con truststore/runpy. **(c) mockup mostrato 13/10, in attesa della scelta (A riga sotto le pillole, B nella testata).** (d) backtest sulle formazioni G5-G6 (−0,28 ± 0,48) **non valido**: `squadre.json` contiene i gol delle giornate provate e il calcolo di prima li usa (fuga a favore del vecchio), le quote no; vale solo il controllo fuori campione su G1-G6 (1234 righe, nessuna fuga): con quote pari o meglio in 6 celle su 8, guadagno piccolo (P +0,003, D +0,005, C +0,023, A −0,004). Scheda: con le quote niente pillola «avversario» (vale 0), al suo posto «partita (quote)». **Da fare:** scelta del mockup e grafica; download di `fixtures.csv` con l'ok; **DECISO 13/10 (utente): la serie con quote guida il consiglio** (era la scelta da fare;  guadagno di modello piccolo, non misurabile sulle formazioni); al primo download leggere gli avvisi (colonne `Avg*` di fixtures.csv non verificate: se mancano, tutto «senza quote» in silenzio); **CHIUSO 14/10 (mockup A fatto, download fatto, serie con quote nel consiglio, commit a286689).**
   **(f) DECISO 14/10 (utente): opzione 1, Actions scarica le quote da sola** (il PC non deve essere acceso). `python scripts/quote.py --automatico` (giro di `aggiorna.yml`): se una partita inizia entro 72 ore (orari veri di `orari.json`) scarica `I1.csv` e `fixtures.csv`, aggiorna `dati/quote.json` e conserva i CSV, con data e ora d'Italia nel nome, nel repo privato `ManzoChinaglia/JARVIS-conoscenza` (ramo `master`, cartella `football-data/`, segreto `CONOSCENZA_TOKEN`) e in un artefatto di 90 giorni; copia identica all'ultima = niente di nuovo. Un guasto (rete, blocco del sito, token scaduto) è solo un avviso, mai un giro rosso. Sul PC i CSV arrivano con `git pull` in `Progetti\JARVIS-conoscenza\football-data\` (il potatore non li tocca; i vecchi in `JARVIS\archivio\football-data\` restano). Prove: script 108/108. **Da fare dall'utente:** token fine-grained GitHub limitato a `JARVIS-conoscenza` (Contents: read/write) salvato come segreto `CONOSCENZA_TOKEN` nel repo JARVIS, con scadenza 01/09/2027 (rinnovare prima). Poi ok a commit/push e a un giro manuale (`workflow_dispatch`): prima del 16/10 alle 18:45 UTC deve saltare (nessuna partita entro 72 ore), dopo scaricare e archiviare; leggere il log una volta (colonne `Avg*` di `fixtures.csv` verificate: ci sono).
   Originale: **Forza delle partite «ad ampio spettro» (le quote):** le quote dei bookmaker riassumono tutto (forma, infortuni, crisi,
   tattica). Fonte candidata: football-data.co.uk (storico Serie A con quote, file delle prossime partite). Prima R0 come per
   THE CLUB: licenza e condizioni scritte, download controllato. Poi una voce «gol attesi dalle quote» in `modello.py`,
   verificata sullo storico 2015-2026: si tiene solo se batte la forza da gol fatti/subiti.
5. **Le news (JARVIS-conoscenza):** il «Pezzo 3» anticipato: misurare se `ballottaggio`/`infortunio` prevedono chi non parte
   titolare meglio delle sole probabili. Solo misura; nel motore solo se predice.
6. **Ricalibrazione dei PESI** a fine novembre, come già previsto, con i passi sopra dentro.
**Dopo:** grafica «wow» (liquid glass mantenuto, ispirazione dal lavoro di THE CLUB), cantiere a sé con mockup prima.

**Verificato il 17/10:** probabili ogni 30 min (`probabili.yml`) già in produzione e verdi; quote automatiche funzionanti (segreto `CONOSCENZA_TOKEN` presente, CSV archiviati in JARVIS-conoscenza); Form regole QI chiuso dall'utente. **Passo 5 misurato (17/10):** tra i probabili titolari (soglia 60-80%) con una news d'infortunio nei 3-5 giorni prima, restano senza voto 1 su 9-23 (4-11%) contro il 5-8% senza news: nessun segnale, ma campione minuscolo (G5-G6, proxy = nessun voto). Non si tocca il motore; rifare con più giornate alla ricalibrazione di fine novembre.
## GRAFICA «WOW» — piano (Opus, 17/10/2026; si esegue con Sonnet)

**Scelta dell'utente (17/10):** direzione **A «Notte di gala»** tra tre (B Medaglia, C Lavagna viva scartate).
Mockup: `archivio/mockup/wow-1.html` (fuori da git: contiene i nomi degli avversari; `?d=A`, `?lega=qi`), servito da
`jarvis-chiaro` (porta 8766) come `/archivio/mockup/wow-1.html`.

**Il linguaggio A (vale per ogni parte):**
- Buio con la luce che cade dall'alto: alone dei colori di lega in cima (`--tema-b` al 22%), sfondo con lo stemma più spento
  (opacità ~0,28), vignetta in basso. Carte di vetro scure (sfuma dall'alto al basso, raggio 26) con un filo di luce di 1 px in cima.
- Caratteri: Big Shoulders Display **pieno 800-900** per nomi e titoli, **sottile 300** per numeri grandi (voti, punteggi, percentuali,
  ore); Space Grotesk per le cifre piccole; Barlow Condensed maiuscoletto spaziato per le etichette, col loro punto d'oro acceso.
  Il nome della tua squadra nei colori `nome_a/nome_b`, l'avversario sottile e grigio.
- Oro solo per ciò che conta: anello della vittoria che si riempie (1,6 s, punto acceso in testa), tessera consigliata con riflesso
  che passa (5 s), voti sottili oro sul campo. Punto verde che respira (3 s) accanto all'aggiornamento.
- Campo notturno: **in prospettiva** (trapezio, fasce che si allargano verso il basso, maglie lontane più piccole, stessa proiezione per campo e maglie), linee che brillano nel `--tema-b`; sotto ogni maglia solo un'ombra scura (niente pozza di luce, niente anelli dorati); voto **sotto il nome** in Big Shoulders 300 (verde ≥7, bianco 6-7, rosso <6, stellina sul migliore), mai in pillola; niente linee tratteggiate; maglie che cadono in sequenza con rimbalzo.
- Restano (già approvati): 7 tessere su una riga, pillole NO MOD./CONSIGLIATA, peperoncino/stella animati, selettore con swipe,
  tema per lega. QI senza percentuali: «pari / sulla carta» nell'anello, mai numeri inventati.

**Passi, in ordine:**
1. **[FATTO e APPROVATO 17/10 sul giro 3: `archivio/mockup/wow-3.html`, riferimento unico per il codice]** **Giro 2 dei mockup** (stesso file o `wow-2.html`, dati veri, entrambe le leghe): le altre schermate in stile A
   (Rosa, Stagione, Lega, selettore aperto, lucchetto, panchina, «La sfida», «Quando giocano», «Il consiglio», scheda giocatore)
   e le micro-parti con tutti gli stati: carta della scadenza **aperta** (conto alla rovescia) e scaduta, tessera giocatore
   (titolare/in dubbio/fuori), tessera modulo (4 stati), campanella, barra in basso. Scelta dell'utente prima del codice.
   Decisioni del giro 3 (utente, 17/10): icona unica dell'app e del lucchetto = Re Guyzo (`img/icona-180.png`); **schermata di cambio lega** col proprio stemma
   (tondo), nome a lettere che compaiono, onde di luce, barra di caricamento, nei colori della lega di destinazione (oggi esce sempre Re Guyzo: da correggere);
   testata nuova (medaglione Re Guyzo con anello d'oro, JARVIS con riflesso, pillola LIVE, campanella SVG che suona, badge che pulsa); tessera modulo con
   linea di stacco tra modulo e punteggio; carta scadenza **senza icona calendario**: aperta = tre anelli giorni/ore/minuti + barra con punta luminosa + badge APERTA,
   chiusa = ora grande + badge CHIUSO (mai la scritta «scaduta»); classifica con **stemmi ufficiali scaricati da Leghe** dove esistono, iniziali altrimenti
   (da fare: scaricarli nello script di import, con controllo download); bottoni (primario oro con riflesso, vetro con bordo di luce, pressione con rimbalzo);
   barra in basso con pillola liquida che scorre e si allunga, icone SVG; schermate che entrano in sequenza; tutto fluido, `prefers-reduced-motion` ferma le animazioni.
2. **[FATTO 17/10, da provare sul telefono dall'utente: caratteri, blocco CSS «Notte di gala» in fondo a `<style>` (filo di luce, etichetta col punto, bottoni, tab con lente oro), testata con medaglione, scadenza ad anelli (`anello()`), moduli con stacco, campo in prospettiva con voto sotto il nome (`pianoCampo()`/`prospettiva()`), schermata di cambio lega con stemma e colori di destinazione (`avvioLega()` + `sessionStorage jarvis-tr`); prove 352/352. RESTA: stemmi ufficiali delle altre squadre nella classifica (vedi sotto: va deciso dove tenerli, perché i loghi possono contenere nomi di altre squadre e il repo è pubblico)]** **Fondamenta in `index.html`**: token CSS nuovi accanto a quelli di oggi; caratteri **in locale** (Big Shoulders Display
   300/800/900 e Space Grotesk, licenza OFL, cartella `font/`, cache del service worker se c'è); componenti riusabili:
   `anello()` SVG, filo di luce, pozza di luce, etichetta col punto. Prima cercare cosa esiste già (regola 7).
3. **Schermate una alla volta**, Giornata per prima, ognuna vista nell'anteprima 390×844 in tutte e due le leghe e approvata.
4. **Prestazioni iPhone:** non impilare `backdrop-filter` (una carta di vetro = un filtro), animazioni solo su transform/opacity,
   `prefers-reduced-motion` le ferma. Prove `prove/app.js` sempre verdi; residui CSS tolti nello stesso lavoro.

## Storico recente

**Fatto il 13/10 (non committato):** (1) «Tu, Jarvis e il massimo»: con Tu e Max vicini le etichette si sovrapponevano; ora `.cf.vicini` porta quella del massimo su una seconda riga. (2) «Il migliore che non hai schierato» non conta più chi è senza voto (prima Robinson s.v. prendeva l'8 di Mendy, il panchinaro che entra): `meglio()` in `htmlScelte`. Prove 334/334.
**Aperti (richiesta utente 13/10):** (a) Jarvis ragiona solo a numeri: consiglia insieme due giocatori che nella realtà sono alternativi (Pellegrino+Beto contro il Como) → collegare all'Atlante del calcio di THE CLUB (da pianificare con Opus); (b) grafica «wow» mantenendo il liquid glass.

**Fatto il 13/10:** dati di lega importati (BF giornate 1-2, QI giornata 1, formazioni). Regola «a tavolino» (3-0 a chi non schiera, solo BF): `forfait` in `leghe.json`, `forfaitLega()` in `index.html`; il tuo forfait non conta come risultato giocato. `prove/app.js` 334/334.

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
