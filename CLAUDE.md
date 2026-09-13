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
dati/base.json          rose, calendario lega, calendario Serie A, statistiche
dati/infortuni.json     aggiornato automaticamente
dati/titolari.json      aggiornato automaticamente
dati/listone.json       elenco ufficiale, usato dagli script
scripts/aggiorna.py     scarica infortuni e probabili formazioni
.github/workflows/aggiorna.yml   esegue lo script martedì 08:00 e sabato 06:00 (ora italiana)
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

## Lavori aperti, in ordine di priorità

1. **Scadenza formazione.** Oggi è stimata al sabato alle 15. La regola vera è:
   **un quarto d'ora prima del primo anticipo della giornata di Serie A**.
   Serve un `dati/orari.json` con l'orario di inizio della prima partita di ogni
   giornata, popolato dallo script, e il conto alla rovescia va calcolato su quello.

2. **Arricchire il consiglio di formazione.** Oggi pesa solo: disponibilità,
   titolarità, fantamedia, piccolo malus trasferta. Va aggiunto:
   - forza difensiva dell'avversario (gol subiti, porte inviolate) — pesa molto
     per i difensori, vista la presenza del modificatore difesa
   - forza offensiva dell'avversario, per valutare il rischio dei difensori
   - casa/trasferta calcolato separatamente, non come media unica
   - modulo dell'avversario dalle probabili formazioni

   **Attenzione al campione:** a settembre ogni squadra ha giocato 3-4 partite.
   Qualsiasi statistica di forma è rumore. Fino a circa la decima giornata i dati
   di quest'anno vanno mescolati con quelli della stagione precedente, dando peso
   crescente all'attuale. Senza questo accorgimento Jarvis darà consigli sicuri
   di sé e sbagliati.

   **Da NON fare:** punteggi basati sul duello individuale (tizio marca caio su
   quella fascia). Il dato pubblico non dice in modo affidabile chi occupa quale
   lato, e il risultato sarebbe una precisione finta.

3. **Font.** `Barlow Condensed` da Google Fonts non si carica sul sito
   pubblicato e i titoli ricadono sul carattere di sistema. Capire perché.

4. **Calendario sottoscrivibile (.ics)** con le scadenze di schieramento e il
   promemoria di esportare la lista calciatori. Su iPhone le notifiche del
   calendario di sistema sono più affidabili delle notifiche push da app web.

5. **Comando Siri.** L'app accetta già una domanda dall'indirizzo
   (`?q=...`): manca solo la guida per creare il Comando Rapido.

## Come si prova

Non c'è una suite di test. Il metodo usato finora, da mantenere:
estrarre il blocco `<script>` da `index.html`, eseguirlo in Node con un
finto DOM e una `fetch` che legge i file da disco, e verificare i risultati
reali (undici generato, risposte alle domande, conteggi). Ha già intercettato
un errore sugli identificativi e una funzione cancellata per sbaglio.
