"""Le quote dei bookmaker come forza delle partite (STATO.md, cervello calcistico, passo 4).

Da football-data.co.uk: `I1.csv` (stagione in corso: partite giocate e quote medie prima della
chiusura) e `fixtures.csv` (prossime partite, tutti i campionati: si tiene solo Div == I1).
Dalle quote si ricavano i gol attesi di casa e trasferta (il totale dal più/meno 2,5, la
divisione dall'1X2, margine tolto normalizzando); mai le colonne di chiusura («...C...»).

Regole (13/10/2026):
- i CSV grezzi non entrano mai in Git (nessuna licenza scritta): ogni file scaricato si
  conserva in archivio/football-data/ con data e ora nel nome e non si cancella né si
  sovrascrive mai (storico e evoluzione delle quote);
- in dati/ solo numeri ricavati: dati/quote.json (giornata Serie A, casa, trasferta, gol
  attesi), agganciato alle partite di dati/orari.json (nessun calendario nuovo), e lo storico
  dati/quote-storico.json.gz che legge scripts/modello.py (gira anche su GitHub Actions,
  dove archivio/ non c'è);
- controllo di plausibilità: se il risultato non torna resta il file di prima.

Uso: python scripts/quote.py                 scarica I1.csv e fixtures.csv, aggiorna quote.json
     python scripts/quote.py --file X.csv... usa file già scaricati (nessuna rete)
     python scripts/quote.py --storico       ricostruisce dati/quote-storico.json.gz dall'archivio
Su questo PC (Norton intercetta HTTPS) lanciarlo con truststore, come aggiorna.py.
"""
import csv, glob, gzip, io, json, math, os, re, sys
from datetime import datetime, timezone

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)     # `from aggiorna import get` anche con runpy.run_path (truststore)
RADICE = os.path.dirname(QUI)
DATI = os.path.join(RADICE, 'dati')
ARCHIVIO = os.path.join(RADICE, 'archivio', 'football-data')
BASE = 'https://www.football-data.co.uk'
STAGIONE = '2627'
URL_I1 = f'{BASE}/mmz4281/{STAGIONE}/I1.csv'
URL_FIXTURES = f'{BASE}/fixtures.csv'
# nomi di football-data che differiscono da quelli di orari.json e dello storico
NOMI_FD = {'Spal': 'SPAL'}
LAMBDA_MIN, LAMBDA_MAX = 0.2, 5.0     # gol attesi a squadra: fuori da qui il file non torna
MINIMO_PARTITE = 1


def _pmf(l):
    return [math.exp(-l) * l ** k / math.factorial(k) for k in range(11)]


def lambda_da_quote(pH, pD, pA, po, pu):
    """Gol attesi (casa, trasferta) da quote medie 1X2 e più/meno 2,5 (None se manca qualcosa).
    Il totale T dal più/meno 2,5 (somma di due Poisson = Poisson(T)), la divisione dall'1X2
    (P(1) − P(2)), entrambi per bisezione."""
    if None in (pH, pD, pA, po, pu):
        return None
    s1 = 1 / pH + 1 / pD + 1 / pA
    h, a = (1 / pH) / s1, (1 / pA) / s1
    over = (1 / po) / (1 / po + 1 / pu)
    lo, hi = 0.3, 7.0
    for _ in range(40):
        T = (lo + hi) / 2
        if 1 - math.exp(-T) * (1 + T + T * T / 2) < over:
            lo = T
        else:
            hi = T
    T = (lo + hi) / 2
    lo, hi = 0.01, 0.99
    for _ in range(40):
        f = (lo + hi) / 2
        x, y = _pmf(T * f), _pmf(T * (1 - f))
        diff = sum(x[i] * y[j] * ((i > j) - (i < j)) for i in range(11) for j in range(11))
        if diff < h - a:
            lo = f
        else:
            hi = f
    f = (lo + hi) / 2
    return T * f, T * (1 - f)


def _num(v):
    try:
        return float(v) if v not in (None, '') else None
    except ValueError:
        return None


def leggi_csv(testo, div='I1'):
    """[(casa, trasferta, (lambda casa, lambda trasferta) o None, giocata)] delle righe di
    quel campionato. Quote medie pre-chiusura (Avg…, Bb… fino al 2018-19), mai le «C»."""
    out = []
    for x in csv.DictReader(io.StringIO(testo.lstrip('﻿'))):
        if (x.get('Div') or div) != div or not x.get('HomeTeam'):
            continue
        g = lambda k, b: _num(x.get(k)) or _num(x.get(b))
        lam = lambda_da_quote(g('AvgH', 'BbAvH'), g('AvgD', 'BbAvD'), g('AvgA', 'BbAvA'),
                              g('Avg>2.5', 'BbAv>2.5'), g('Avg<2.5', 'BbAv<2.5'))
        out.append((NOMI_FD.get(x['HomeTeam'], x['HomeTeam']), NOMI_FD.get(x['AwayTeam'], x['AwayTeam']),
                    lam, _num(x.get('FTHG')) is not None))
    return out


def aggancia(partite, orari):
    """Aggancia le partite al calendario di orari.json: la coppia (casa, trasferta) è unica in
    una stagione, quindi niente date (fusi orari, rinvii). Ritorna ({giornata: [[casa, trasf,
    lam casa, lam trasf]]}, [partite senza giornata], [partite senza quote])."""
    giornata = {}
    for g, v in (orari.get('giornate') or {}).items():
        for casa, trasf, *_ in v.get('partite') or []:
            giornata[(casa, trasf)] = g
    out, senza_g, senza_q = {}, [], []
    for casa, trasf, lam, _ in partite:
        g = giornata.get((casa, trasf))
        if g is None:
            senza_g.append((casa, trasf))
        elif lam is None:
            senza_q.append((casa, trasf))
        else:
            out.setdefault(g, []).append([casa, trasf, round(lam[0], 3), round(lam[1], 3)])
    return out, senza_g, senza_q


def plausibile(giornate):
    n = sum(len(v) for v in giornate.values())
    tutte = [x for v in giornate.values() for p in v for x in p[2:4]]
    return n >= MINIMO_PARTITE and all(LAMBDA_MIN <= x <= LAMBDA_MAX for x in tutte)


def costruisci(i1, fixtures, orari, adesso=None):
    """dati/quote.json: le partite giocate dal file di stagione (quote d'epoca), le prossime da
    fixtures.csv (solo quelle non già nel file di stagione). Ritorna (dizionario, avvisi)."""
    avvisi = []
    gia = {(p[0], p[1]) for p in i1 or []}
    prossime = [p for p in fixtures or [] if (p[0], p[1]) not in gia]
    giornate, avvisi_nomi = {}, []
    for fonte, partite in (('I1', i1 or []), ('fixtures', prossime)):
        g, senza_g, senza_q = aggancia(partite, orari)
        for k, v in g.items():
            giornate.setdefault(k, []).extend(p + [fonte] for p in v)
        avvisi_nomi += [f'{fonte}: senza giornata in orari.json: {c}-{t}' for c, t in senza_g]
        avvisi += [f'{fonte}: senza quote: {c}-{t}' for c, t in senza_q]
    avvisi = avvisi_nomi + avvisi
    return {'aggiornato': (adesso or datetime.now(timezone.utc)).isoformat(timespec='seconds'),
            'giornate': dict(sorted(giornate.items(), key=lambda kv: int(kv[0])))}, avvisi


def senza_ora(d):
    return {k: v for k, v in d.items() if k != 'aggiornato'}


def unisci(vecchio, nuovo):
    """I dati non si svuotano mai (regola 4): le partite nuove sostituiscono quelle con la stessa
    coppia (casa, trasferta), le vecchie non citate restano (una corsa col solo fixtures.csv non
    cancella le partite giocate)."""
    chiavi = {(c, t) for v in nuovo['giornate'].values() for c, t, *_ in v}
    giornate = {g: [p for p in v if (p[0], p[1]) not in chiavi] for g, v in (vecchio or {}).get('giornate', {}).items()}
    for g, v in nuovo['giornate'].items():
        giornate.setdefault(g, []).extend(v)
    return {'aggiornato': nuovo['aggiornato'],
            'giornate': dict(sorted(((g, v) for g, v in giornate.items() if v), key=lambda kv: int(kv[0])))}


def scrivi(percorso, nuovo):
    """Scrive solo se plausibile e diverso da quello che c'è (a parte la data), unendo il nuovo al vecchio."""
    if not plausibile(nuovo['giornate']):
        print('[quote] risultato non plausibile: resta il file di prima.')
        return False
    try:
        with open(percorso, encoding='utf-8') as f:
            vecchio = json.load(f)
        nuovo = unisci(vecchio, nuovo)
        if senza_ora(vecchio) == senza_ora(nuovo):
            print('[quote] niente di nuovo.')
            return False
    except (OSError, ValueError):
        pass
    with open(percorso, 'w', encoding='utf-8') as f:
        json.dump(nuovo, f, ensure_ascii=False, separators=(',', ':'))
    print(f'[quote] scritto: {sum(len(v) for v in nuovo["giornate"].values())} partite.')
    return True


def salva_copia(testo, nome, cartella=ARCHIVIO, adesso=None):
    """Conserva il file scaricato in `cartella` come <nome>_AAAA-MM-GG_HHMM.csv; non
    sovrascrive mai (se il nome c'è già aggiunge -2, -3…). Ritorna il percorso."""
    os.makedirs(cartella, exist_ok=True)
    quando = (adesso or datetime.now()).strftime('%Y-%m-%d_%H%M')
    k, percorso = 1, os.path.join(cartella, f'{nome}_{quando}.csv')
    while os.path.exists(percorso):
        k += 1
        percorso = os.path.join(cartella, f'{nome}_{quando}-{k}.csv')
    with open(percorso, 'w', encoding='utf-8', newline='') as f:
        f.write(testo)
    return percorso


def scarica(url):
    from aggiorna import get
    r = get(url)
    r.raise_for_status()
    return r.content.decode('utf-8-sig')


def storico_da_archivio(cartella=ARCHIVIO):
    """{stagione 'AAAA-AA': [[casa, trasferta, lam casa, lam trasf]]} da I1_<stagione>_*.csv
    (per ogni stagione il file più recente): i numeri ricavati che legge modello.py."""
    ultimi = {}
    for p in sorted(glob.glob(os.path.join(cartella, 'I1_????_*.csv'))):
        s = os.path.basename(p).split('_')[1]
        ultimi[s] = p
    out = {}
    for s, p in sorted(ultimi.items()):
        with open(p, encoding='utf-8-sig') as f:
            righe = [[c, t, round(lam[0], 3), round(lam[1], 3)] for c, t, lam, _ in leggi_csv(f.read()) if lam]
        if righe:
            out[f'20{s[:2]}-{s[2:]}'] = righe
    return out


def _leggi(percorso):
    with open(percorso, encoding='utf-8-sig') as f:
        return f.read()


def main(argv):
    with open(os.path.join(DATI, 'orari.json'), encoding='utf-8') as f:
        orari = json.load(f)
    if '--storico' in argv:
        st = storico_da_archivio()
        if len(st) < 5:
            print('[quote] storico non plausibile (meno di 5 stagioni): non scrivo.')
            return 1
        percorso = os.path.join(DATI, 'quote-storico.json.gz')
        with gzip.open(percorso, 'wt', encoding='utf-8') as f:
            json.dump(st, f, ensure_ascii=False, separators=(',', ':'))
        print(f'[quote] storico scritto: {len(st)} stagioni, {sum(len(v) for v in st.values())} partite.')
        return 0
    if '--file' in argv:
        file = [a for a in argv[argv.index('--file') + 1:] if not a.startswith('--')]
        testi = [(os.path.basename(p), _leggi(p)) for p in file]
        i1 = [x for n, t in testi if n.startswith('I1') for x in leggi_csv(t)]
        fx = [x for n, t in testi if n.startswith('fixtures') for x in leggi_csv(t)]
    else:
        testo_i1, testo_fx = scarica(URL_I1), scarica(URL_FIXTURES)
        for nome, t in (('I1_' + STAGIONE, testo_i1), ('fixtures', testo_fx)):
            print('[quote] salvato', salva_copia(t, nome))
        i1, fx = leggi_csv(testo_i1), leggi_csv(testo_fx)
    nuovo, avvisi = costruisci(i1, fx, orari)
    for a in avvisi:
        print('[quote] attenzione:', a)
    scrivi(os.path.join(DATI, 'quote.json'), nuovo)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
