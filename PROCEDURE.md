# Procedure a mano di Jarvis

Spostate da `CLAUDE.md` il 23/09/2026 (testo invariato). Si leggono quando l'utente scrive
«dati di lega», «rose aggiornate», «formazione schierata» o «giornata N schierata».

## Dati a mano: rose e «dati di lega»

- **Controllo a inizio sessione, sul PC** (non dal cloud: niente Chrome collegato a
  Leghe lì): guarda l'ultima giornata in `dati/orari.json` con `fine` passata da almeno
  due ore; se `dati/lega.json` → `risultati` non ha ancora quella giornata, o
  `dati/formazioni.json` non ha ancora la tua formazione di quella giornata, **proponi**
  all'utente «dati di lega» e/o «formazione schierata» invece di aspettare che le chieda
  — resta lui a confermare (regola 9), non partire da solo.
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
- **Formazione schierata** (l'utente scrive «formazione schierata» o «giornata N
  schierata»): niente file da esportare, il dato sta solo nella pagina. Dal **Chrome
  dell'utente**, già collegato: `.../rivoluzione-fantacalcio/view/competition/748699/
  round/<giornata>` (748699 è l'id di questa lega; le pagine «Formazioni» del menu
  restano 404). Si legge il testo con `get_page_text` (solo l'articolo della partita:
  niente login, niente dati altrui oltre ai nomi già pubblici in `base.json`), si salva
  in un file, e `python scripts/importa_formazioni.py <file> <giornata>` lo scrive in
  `dati/formazioni.json` (chiuso). Se la formazione di quella giornata non è ancora
  stata inserita su Leghe, lo script si ferma con un messaggio chiaro e non scrive
  niente. Serve solo alla tua squadra (`base['me']`): l'idea è il giudizio «rivelato»
  (B4 in STORIA.md), non scoutare gli avversari.
  **Un solo giro** (`scripts/schiera.py`): `python scripts/schiera.py --mancanti` elenca le
  giornate finite (≥ 2 ore) e già in `lega.json` senza la tua formazione (se Leghe dice «Formazione non inserita», non c'è nulla da recuperare); Claude, con **una sola conferma** dell'utente,
  legge dal Chrome le pagine di tutte quelle giornate (una scheda, poi la chiude), le salva in file
  temporanei e lancia `python scripts/schiera.py 2=g2.txt 3=g3.txt ...` (prima con `--prova`):
  `apri` → import di ogni giornata → `chiudi` (anche se una fallisce) → `prove/formazioni.py` e
  `prove/privacy.py`. Non fa commit: il commit (e il push) lo fa Claude dopo, coi totali delle prove.
