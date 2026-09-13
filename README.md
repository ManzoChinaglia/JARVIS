# Jarvis

Assistente per il fantacalcio, stagione 2026/27 — lega *Sborra league*, squadra **BURKINA FASO**.

Applicazione web, pensata per iPhone. Si apre da Safari e si aggiunge alla schermata Home:
da lì funziona a schermo intero, come un'app.

---

## Struttura

```
index.html                    l'app (codice, nessun dato dentro)
dati/
  base.json                   rose, calendario lega, calendario Serie A, statistiche
  infortuni.json              chi è fuori e fino a quando        [automatico]
  titolari.json               chi è dato titolare                [automatico]
  orari.json                  orari delle giornate di Serie A    [automatico]
  listone.json                elenco ufficiale, serve agli script
scripts/
  aggiorna.py                 scarica infortuni, probabili formazioni e orari
.github/workflows/
  aggiorna.yml                esegue lo script tre volte a settimana
prove/
  app.js                      prova l'app in Node:     node prove/app.js
  orari.py                    prova la logica orari:   python prove/orari.py
```

Il codice e i dati sono separati di proposito: si aggiorna l'uno senza toccare l'altro.

---

## Da dove arrivano i dati

| Dato | Fonte | Aggiornamento |
|---|---|---|
| Rose delle 10 squadre | esportazione da Leghe Fantacalcio | a ogni scambio |
| Calendario della lega | esportazione da Fantalab | una volta |
| Calendario Serie A | date ufficiali | una volta |
| Statistiche giocatori (PGv, MV, FM) | esportazione «Lista calciatori» | **manuale, 1 volta a settimana** |
| Infortunati con data di rientro | pagina pubblica | automatico |
| Probabili formazioni | pagina pubblica | automatico |
| Orari delle partite di Serie A | feed pubblico fixturedownload.com | automatico |

La scadenza per schierare la formazione è un quarto d'ora prima del primo anticipo
della giornata. Finché la Lega Serie A non fissa gli orari di una giornata, Jarvis
scrive «orario non ancora ufficiale» invece di stimarla.

L'unico passaggio manuale è l'esportazione settimanale della lista calciatori:
richiede il login alla lega e per questo non è automatizzabile in modo pulito.

---

## Le finestre di aggiornamento

Impostate in `.github/workflows/aggiorna.yml`, ora italiana (con l'ora solare, un'ora prima):

- **martedì 08:00** — dopo l'ultima partita della giornata appena conclusa
- **venerdì 10:00** — prima degli anticipi del venerdì sera
- **sabato 06:00** — prima delle partite del sabato pomeriggio

Si può lanciare anche a mano: scheda **Actions** del repository → *Aggiorna Jarvis* → *Run workflow*.

Se una fonte non risponde o cambia struttura, i dati precedenti **restano intatti**:
meglio un dato di tre giorni fa che un file vuoto la domenica mattina.

---

## Come si aggiorna la formazione consigliata

La difesa è **sempre a quattro**. Il modulo cambia solo nei reparti avanzati
(4-3-3, 4-4-2, 4-5-1) dal selettore sopra il campo.

Il punteggio con cui Jarvis ordina i giocatori tiene conto di:

1. disponibilità — chi è infortunato alla data della giornata è escluso
2. titolarità secondo le ultime probabili formazioni
3. fantamedia personale
4. trasferta (piccolo malus)

Da aggiungere: forza difensiva e offensiva dell'avversario, casa/trasferta pesata
per ruolo, modulo avversario.

---

## Manutenzione settimanale

1. Da Leghe Fantacalcio → Menu → Lista calciatori → **Scarica**
   (verificare che il filtro includa tutte e 10 le squadre)
2. Rigenerare `dati/base.json` dal file scaricato
3. Caricare su GitHub

Il resto va da sé.
