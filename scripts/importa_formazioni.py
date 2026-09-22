#!/usr/bin/env python3
"""
Salva la formazione schierata (titolari e panchina) della tua squadra in una
giornata di lega già giocata, in dati/formazioni.json: serve al giudizio
"rivelato" (STORIA.md, B4), non ancora costruito.

Il dato non si scarica: sta nella pagina di Leghe Fantacalcio
".../rivoluzione-fantacalcio/view/competition/<id lega>/round/<giornata>"
(niente pulsante «Esporta»; le pagine «Formazioni» del menu restano 404). La
legge Claude dal Chrome dell'utente già collegato, ne salva il testo (solo
l'articolo della partita, senza login né altro) in un file, e lo passa a
questo script.

Uso: python scripts/importa_formazioni.py <file di testo> <giornata> [--prova]
Con --prova mostra cosa leggerebbe, senza scrivere niente.

dati/formazioni.json: {"aggiornato": "...", "giornate": {"<giornata>":
{"modulo": "3-5-2", "titolari": [id, ...], "panchina": [id, ...]}}}. Solo la
tua squadra (base['me']): l'idea è il tuo giudizio "rivelato", non scoutare
gli avversari. Ruolo e nome di ogni Id si ricavano da dati/base.json (stesso
Id del listone, "Non introdurre altri identificativi"); voto e fantavoto
sono già in dati/voti.json, non si ripetono qui.

Non scrive niente se la formazione non risulta ancora inserita, o se
qualcosa non torna (un nome non riconosciuto, un modulo diverso dai cinque
validi, la rosa non corrisponde): i dati di prima restano (upsert per
giornata, non si svuota mai tutto).
"""
import json, os, re, sys, unicodedata
from datetime import datetime, timezone

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(RADICE, 'dati')
MODULI_VALIDI = {'4-3-3', '4-4-2', '4-5-1', '3-5-2', '3-4-3'}
N_TITOLARI = 11
N_PANCHINA = 14                       # una rosa è sempre 25 (3 P, 8 D, 8 C, 6 A): 25 - 11
RE_MODULO = re.compile(r'^\d-\d-\d$')
RE_VALORE = re.compile(r'^\d+(\.\d+)?$|^s\.v\.$')


def norm(s):
    """Per confrontare i nomi: senza accenti, maiuscole, spazi e punteggiatura."""
    s = unicodedata.normalize('NFD', str(s or '')).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]', '', s.lower())


def righe_utili(testo):
    """Le righe del testo dell'articolo, senza vuote né spazi ai lati."""
    return [r.strip() for r in testo.splitlines() if r.strip()]


def blocchi(righe, n):
    """Consuma n giocatori dall'inizio delle righe: un nome, poi fino a due
    valori (voto, fantavoto, anche "s.v.") se ci sono, scartati (non servono
    qui, sono già in dati/voti.json). Restituisce (nomi, resto)."""
    nomi, resto = [], list(righe)
    for _ in range(n):
        if not resto:
            raise ValueError(f'attesi {n} giocatori, trovati {len(nomi)}: la pagina ha cambiato struttura')
        nome = resto.pop(0)
        if RE_VALORE.match(nome):
            raise ValueError(f'atteso un nome, trovato «{nome}»: la pagina ha cambiato struttura')
        while resto and RE_VALORE.match(resto[0]) and resto.pop(0):
            pass
        nomi.append(nome)
    return nomi, resto


def estrai(testo, squadra):
    """(modulo, titolari, panchina) della tua squadra dal testo di una pagina
    round/<giornata>: solo i nomi mostrati da Leghe, non ancora Id. Le due
    squadre possono comparire in un ordine o nell'altro: si riconoscono le
    intestazioni dal modulo (o "Non schierata"), non dalla posizione."""
    righe = righe_utili(testo)
    intestazioni = [i for i, r in enumerate(righe) if i >= 2 and (RE_MODULO.match(r) or r == 'Non schierata')]
    if len(intestazioni) != 2:
        raise ValueError('struttura della pagina non riconosciuta (moduli non trovati)')
    squadre = {righe[i - 2]: (i, righe[i]) for i in intestazioni}
    if squadra not in squadre:
        raise ValueError(f'«{squadra}» non compare in questa pagina: giornata sbagliata?')
    idx_mio, modulo_mio = squadre[squadra]
    if any(m == 'Non schierata' for _, m in squadre.values()):
        raise ValueError('formazione non ancora inserita per questa giornata')
    if modulo_mio not in MODULI_VALIDI:
        raise ValueError(f'modulo non riconosciuto: «{modulo_mio}»')

    primo = idx_mio == min(i for i, _ in squadre.values())
    resto = righe[max(i for i, _ in squadre.values()) + 1:]
    titolari_1, resto = blocchi(resto, N_TITOLARI)
    titolari_2, resto = blocchi(resto, N_TITOLARI)
    if not resto or resto[0] != 'Panchina':
        raise ValueError('sezione «Panchina» non trovata: la pagina ha cambiato struttura')
    panchina_1, resto = blocchi(resto[1:], N_PANCHINA)
    panchina_2, resto = blocchi(resto, N_PANCHINA)
    titolari, panchina = (titolari_1, panchina_1) if primo else (titolari_2, panchina_2)
    return modulo_mio, titolari, panchina


def id_di(nomi, rosa):
    """Gli Id (dati/base.json → p) e i ruoli dei nomi mostrati da Leghe, nella
    rosa di una squadra: come le rose (importa_rose.py), dal nome."""
    per_nome = {}
    for r in rosa:
        per_nome.setdefault(norm(r[1]), []).append(r)
    ids, ruoli, errori = [], [], []
    for nome in nomi:
        cand = per_nome.get(norm(nome), [])
        if len(cand) != 1:
            errori.append(f'{nome}: ' + ('non è nella rosa' if not cand else 'più giocatori con questo nome'))
            continue
        ids.append(cand[0][0])
        ruoli.append(cand[0][3])
    if errori:
        raise ValueError('\n'.join(errori))
    return ids, ruoli


def importa(testo, base):
    """Riga da salvare in dati/formazioni.json → giornate[giornata], dal testo
    di una pagina round/<giornata>. Solleva ValueError se non è plausibile."""
    squadra = base['me']
    rosa = [p for p in base['p'] if p[4] == squadra]
    if len(rosa) != N_TITOLARI + N_PANCHINA:
        raise ValueError(f'{squadra}: {len(rosa)} giocatori in rosa invece di {N_TITOLARI + N_PANCHINA}')

    modulo, nomi_titolari, nomi_panchina = estrai(testo, squadra)
    ids_titolari, ruoli_titolari = id_di(nomi_titolari, rosa)
    d, c, a = (int(x) for x in modulo.split('-'))
    conta = {r: ruoli_titolari.count(r) for r in 'PDCA'}
    attesi = {'P': 1, 'D': d, 'C': c, 'A': a}
    if conta != attesi:
        raise ValueError(f'titolari {conta} non corrispondono al modulo {modulo} ({attesi})')
    ids_panchina, _ = id_di(nomi_panchina, rosa)

    tutti = ids_titolari + ids_panchina
    doppi = sorted({i for i in tutti if tutti.count(i) > 1})
    if doppi:
        raise ValueError(f'giocatori ripetuti tra titolari e panchina: {doppi}')
    return {'modulo': modulo, 'titolari': ids_titolari, 'panchina': ids_panchina}


def main():
    argomenti = [a for a in sys.argv[1:] if not a.startswith('--')]
    prova = '--prova' in sys.argv
    if len(argomenti) < 2:
        print('uso: python scripts/importa_formazioni.py <file di testo> <giornata> [--prova]')
        sys.exit(1)
    percorso, giornata = argomenti[0], argomenti[1]
    if not giornata.isdigit():
        print(f'giornata non valida: «{giornata}»')
        sys.exit(1)
    with open(percorso, encoding='utf-8') as f:
        testo = f.read()
    with open(os.path.join(DATI, 'base.json'), encoding='utf-8') as f:
        base = json.load(f)

    try:
        riga = importa(testo, base)
    except ValueError as e:
        print('Formazione NON salvata, la pagina non è plausibile:\n' + str(e))
        sys.exit(1)
    print(f'giornata {giornata}: modulo {riga["modulo"]}, {len(riga["titolari"])} titolari, '
          f'{len(riga["panchina"])} in panchina')
    if prova:
        print('prova: nessun file scritto.')
        return

    percorso_formazioni = os.path.join(DATI, 'formazioni.json')
    dati = {'aggiornato': '', 'giornate': {}}
    if os.path.exists(percorso_formazioni):
        try:
            with open(percorso_formazioni, encoding='utf-8') as f:
                dati = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass               # formazioni.json non ancora valido: si riparte da vuoto
    dati.setdefault('giornate', {})[giornata] = riga
    dati['aggiornato'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    with open(percorso_formazioni, 'w', encoding='utf-8') as f:
        f.write(json.dumps(dati, ensure_ascii=False, separators=(',', ':')))
    print('formazioni aggiornate.')


if __name__ == '__main__':
    main()
