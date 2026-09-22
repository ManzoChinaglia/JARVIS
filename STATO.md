# Stato dei lavori — JARVIS

(al 22/09/2026)

**Fatto il 22/09:** la freccia dei posti guadagnati o persi in classifica (`movimentoLega`
in `index.html`, confronta con la giornata prima; senza almeno due giornate non compare,
niente inventato). Chiusi anche: lo snellimento delle pagine (l'utente ha visto l'app e va
bene così), il parere dell'utente sulle sezioni (risultato ottimo) e altre migliorie di
grafica non richieste (l'utente le chiede lui quando gli vengono in mente).

**Aperto:**
1. **La formazione schierata** da Leghe (chi hai schierato davvero, non solo i probabili):
   serve per «La stagione» (B4, il giudizio «rivelato»: imparare da dove l'undici
   schierato si discosta dal consiglio) — senza questo dato quell'idea resta ferma.
   **Trovata il 22/09/2026**: non dal link «Formazioni» del menu (resta 404 anche
   cliccandolo dal sito), ma da Menu → «Ultimi risultati» → clic sulla giornata, o diretto
   `.../rivoluzione-fantacalcio/view/competition/748699/round/<giornata>` (748699 è l'id
   di questa lega): modulo e titolari con ruolo, voto e fantavoto, per entrambe le squadre,
   per ogni giornata già giocata («Panchina» a parte, da aprire). **Da costruire ancora**:
   lo script che la scarica e la salva (rimandato su richiesta dell'utente, sapendo dove
   sta si riparte quando serve).

**Da vedere nel tempo:** autocalibrazione dei `PESI` (non prima di fine novembre 2026, sui
consigli salvati e «Quanto si avvicina Jarvis»); ogni tanto la verifica in
`dati/modello.json`; fine stagione: la 2026-27 nello storico; rose dopo soste e gennaio.
