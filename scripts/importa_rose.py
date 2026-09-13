#!/usr/bin/env python3
"""
Aggiorna le rose della lega in dati/base.json da rose.csv, il file che si scarica
da Leghe Fantacalcio dopo uno scambio o durante il mercato.

Uso: python scripts/importa_rose.py [percorso di rose.csv]
Senza percorso prende il rose*.csv più recente nella cartella Download.

- tocca solo le rose (squadra, prezzo, ruolo, nome, quotazione) e la data "v":
  calendario e sfide restano quelli di base.json
- partite, MV e FM vengono da dati/statistiche.json se c'è, altrimenti restano
  quelli di prima (0 per chi arriva adesso)
- controlla 10 squadre da 25 (3 P, 8 D, 8 C, 6 A) con i nomi del calendario:
  al primo problema si ferma e non scrive niente
- aggiunge al listone i giocatori nuovi, così lo script li riconosce nelle
  probabili e negli infortuni
"""
import csv, glob, json, os, sys
from collections import Counter
from datetime import date

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(RADICE, 'dati')
RUOLI = {'P': 3, 'D': 8, 'C': 8, 'A': 6}


def leggi_json(nome):
    with open(os.path.join(DATI, nome), encoding='utf-8') as f:
        return json.load(f)


def testo_json(dati):
    """Stesso formato dei file in dati/: compatto, su una riga, accenti leggibili."""
    return json.dumps(dati, ensure_ascii=False, separators=(',', ':'))


def trova_csv(cartella):
    """Il rose*.csv più recente nella cartella."""
    file = glob.glob(os.path.join(cartella, 'rose*.csv'))
    if not file:
        raise FileNotFoundError(f'nessun rose*.csv in {cartella}')
    return max(file, key=os.path.getmtime)


def leggi_csv(percorso):
    with open(percorso, encoding='utf-8-sig') as f:
        testo = f.read()
    prima = testo.splitlines()[0]
    return list(csv.DictReader(testo.splitlines(), delimiter=';' if prima.count(';') > prima.count(',') else ','))


def importa(righe, base, listone, stat=None):
    """Nuovo base.json e nuovo listone dalle righe di rose.csv.
    Solleva ValueError se le rose non sono plausibili."""
    squadre_calendario = {s for g in base['g'] for sfida in g[3] for s in sfida}
    prima = {p[0]: p for p in base['p']}
    noti = {p['id']: p for p in listone}
    # sigla del club (INT) → nome del listone (Inter), dai giocatori già noti
    sigle = {}
    for r in righe:
        i = int(r['Fantacalcio_Id'])
        if i in noti:
            sigle.setdefault(r['Squadra_Appartenenza'].strip(), noti[i]['squadra'])

    rose, errori = [], []
    for r in righe:
        i, nome = int(r['Fantacalcio_Id']), r['Nome'].strip()
        squadra, ruolo, sigla = r['Squadra'].strip(), r['Ruolo'].strip(), r['Squadra_Appartenenza'].strip()
        club = noti[i]['squadra'] if i in noti else sigle.get(sigla)
        if not club:
            errori.append(f'club sconosciuto per {nome} ({sigla})')
            continue
        s, vecchio = (stat or {}).get(str(i)), prima.get(i)
        pgv, mv, fm = (s[0], s[1], s[2]) if s else ((vecchio[7], vecchio[8], vecchio[9]) if vecchio else (0, 0.0, 0.0))
        quot = int(r['Quotazione']) if r.get('Quotazione', '').strip().isdigit() else (s[3] if s else 0)
        rose.append([i, nome, club, ruolo, squadra, int(r['Prezzo']), quot, pgv, mv, fm])

    conta = Counter(p[4] for p in rose)
    for s in sorted(set(conta) - squadre_calendario):
        errori.append(f'squadra «{s}» non presente nel calendario')
    if len(conta) != 10:
        errori.append(f'{len(conta)} squadre invece di 10')
    for s in sorted(conta):
        ruoli = dict(Counter(p[3] for p in rose if p[4] == s))
        if ruoli != RUOLI:
            errori.append(f'{s}: {ruoli} invece di 3 P, 8 D, 8 C, 6 A')
    if base['me'] not in conta:
        errori.append(f'manca la tua squadra, {base["me"]}')
    doppi = [i for i, n in Counter(p[0] for p in rose).items() if n > 1]
    if doppi:
        errori.append(f'giocatori in due squadre: {doppi}')
    if errori:
        raise ValueError('\n'.join(errori))

    nuovo = dict(base)                    # stesse chiavi, stesso ordine
    nuovo['v'] = date.today().isoformat()
    nuovo['p'] = rose
    aggiunti = [{'id': p[0], 'nome': p[1], 'squadra': p[2]} for p in rose if p[0] not in noti]
    return nuovo, listone + aggiunti, aggiunti


def scambi(prima, dopo):
    """Chi ha cambiato squadra, chi è entrato nelle rose e chi ne è uscito."""
    a, b = {p[0]: p for p in prima['p']}, {p[0]: p for p in dopo['p']}
    cambi = sorted((b[i][1], a[i][4], b[i][4]) for i in a.keys() & b.keys() if a[i][4] != b[i][4])
    entrati = sorted((b[i][1], b[i][4]) for i in b.keys() - a.keys())
    usciti = sorted((a[i][1], a[i][4]) for i in a.keys() - b.keys())
    return cambi, entrati, usciti


def main():
    percorso = sys.argv[1] if len(sys.argv) > 1 else trova_csv(os.path.join(os.path.expanduser('~'), 'Downloads'))
    print(f'file: {percorso}')
    base, listone = leggi_json('base.json'), leggi_json('listone.json')
    try:
        stat = leggi_json('statistiche.json').get('giocatori')
    except (OSError, ValueError):
        stat = None
    try:
        nuovo, nuovo_listone, aggiunti = importa(leggi_csv(percorso), base, listone, stat)
    except ValueError as e:
        print('Rose NON aggiornate, il file non è plausibile:\n' + str(e))
        sys.exit(1)

    cambi, entrati, usciti = scambi(base, nuovo)
    for nome, da, a in cambi:
        print(f'  scambio: {nome}, da {da} a {a}')
    for nome, s in entrati:
        print(f'  entrato: {nome} ({s})')
    for nome, s in usciti:
        print(f'  uscito:  {nome} ({s})')
    if not (cambi or entrati or usciti):
        print('  nessun cambio nelle rose')
    for p in aggiunti:
        print(f'  nuovo nel listone: {p["nome"]} ({p["squadra"]})')

    with open(os.path.join(DATI, 'base.json'), 'w', encoding='utf-8') as f:
        f.write(testo_json(nuovo))
    if aggiunti:
        with open(os.path.join(DATI, 'listone.json'), 'w', encoding='utf-8') as f:
            f.write(testo_json(nuovo_listone))
    print(f'rose aggiornate: {len(nuovo["p"])} giocatori, 10 squadre.')


if __name__ == '__main__':
    main()
