#!/usr/bin/env python3
"""
Aggiorna i dati vivi di Jarvis: infortunati, probabili formazioni e orari.

Scrive tre file in dati/:
  dati/infortuni.json   { "aggiornato": "...", "voci": { "<id>": {...} } }
  dati/titolari.json    { "aggiornato": "...", "stato": { "<id>": "t|c|r" } }
  dati/orari.json       { "aggiornato": "...", "giornate": { "<giornata Serie A>": {...} } }

Regole di sicurezza:
 - se una fonte non risponde o cambia struttura, il file esistente NON viene toccato
 - ogni scrittura avviene solo se il risultato supera un controllo di plausibilita'
"""
import json, os, re, sys, unicodedata
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(RADICE, 'dati')
LISTONE = os.path.join(DATI, 'listone.json')   # [{id, nome, squadra}, ...]

UA = {'User-Agent': 'Jarvis/1.0 (uso personale; aggiornamento 3 volte a settimana)'}
TIMEOUT = 30

URL_INFORTUNI = 'https://www.fantacalcio-online.com/it/infortunati-serie-a'
URL_PROBABILI = 'https://www.fantacalcio-online.com/it/consigli-fantacalcio/probabili-formazioni-serie-a'
URL_ORARI = 'https://fixturedownload.com/feed/json/serie-a-2026'

# nomi della fonte degli orari che differiscono da quelli del listone
SQUADRE = {'Internazionale': 'Inter'}


def norm(s):
    s = unicodedata.normalize('NFD', str(s)).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z ]', '', s.lower()).strip()


def carica_listone():
    with open(LISTONE, encoding='utf-8') as f:
        return json.load(f)


def trova(listone, squadra, nome):
    """Abbina un nome a un id del listone. Prima dentro la squadra, poi ovunque."""
    parti = norm(nome).split()
    if not parti:
        return None
    cognome, primo = parti[0], (parti[1] if len(parti) > 1 else None)
    pools = [[p for p in listone if norm(p['squadra']) == norm(squadra)], listone]
    for pool in pools:
        esatto = ripiego = None
        for p in pool:
            pn = norm(p['nome']).split()
            if not pn or pn[0] != cognome:
                continue
            resto = pn[1:]
            if primo:
                if resto and resto[0][0] == primo[0]:
                    esatto = p
                    break
                if not resto and ripiego is None:
                    ripiego = p
            else:
                if not resto:
                    esatto = p
                    break
                if ripiego is None:
                    ripiego = p
        scelto = esatto or ripiego
        if scelto:
            return scelto
    return None


def scrivi(percorso, contenuto, minimo, etichetta):
    """Scrive solo se il risultato e' plausibile, altrimenti lascia il file com'e'."""
    n = len(contenuto.get('voci') or contenuto.get('stato') or contenuto.get('giornate') or {})
    if n < minimo:
        print(f'[{etichetta}] solo {n} voci (minimo {minimo}): non aggiorno, tengo i dati precedenti.')
        return False
    os.makedirs(os.path.dirname(percorso), exist_ok=True)
    with open(percorso, 'w', encoding='utf-8') as f:
        json.dump(contenuto, f, ensure_ascii=False)
    print(f'[{etichetta}] scritte {n} voci.')
    return True


def infortuni(listone):
    r = requests.get(URL_INFORTUNI, headers=UA, timeout=TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')

    voci, mancati = {}, []
    for tr in soup.select('table tr'):
        celle = [td.get_text(' ', strip=True) for td in tr.find_all('td')]
        if len(celle) < 4:
            continue
        squadra, calciatore, motivo, rientro = celle[0], celle[1], celle[2], celle[3]
        if not re.match(r'\d{2}/\d{2}/\d{4}', rientro):
            continue
        p = trova(listone, squadra, calciatore)
        if p:
            voci[str(p['id'])] = {'rientro': rientro, 'motivo': motivo}
        else:
            mancati.append(f'{squadra} {calciatore}')

    if mancati:
        print('[infortuni] non abbinati:', ', '.join(mancati))
    return {'aggiornato': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'voci': voci}


def probabili(listone):
    r = requests.get(URL_PROBABILI, headers=UA, timeout=TIMEOUT)
    r.raise_for_status()
    testo = BeautifulSoup(r.text, 'lxml').get_text('\n', strip=True)

    stato, squadra = {}, None
    squadre = {norm(p['squadra']) for p in listone}
    for riga in testo.split('\n'):
        if norm(riga) in squadre:
            squadra = riga.strip()
            continue
        if not squadra:
            continue
        # righe con 11 nomi separati da virgola = formazione titolare
        if riga.count(',') >= 9:
            for nome in [x.strip() for x in riga.split(',')]:
                p = trova(listone, squadra, nome)
                if p:
                    stato[str(p['id'])] = 't'
            squadra = None

    return {'aggiornato': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'stato': stato}


def precedenti(percorso, chiave):
    """Il contenuto gia' salvato, per non perdere dati che la fonte non riporta piu'."""
    try:
        with open(percorso, encoding='utf-8') as f:
            return json.load(f).get(chiave) or {}
    except (OSError, ValueError):
        return {}


def orari(vecchie):
    """Primo e ultimo calcio d'inizio di ogni giornata di Serie A.

    La fonte mette a mezzanotte UTC le partite senza orario ufficiale: una
    giornata e' ufficiale solo se nessuna partita e' a mezzanotte. Per le altre
    non si salva nessun orario, perche' sarebbe inventato.
    """
    r = requests.get(URL_ORARI, headers=UA, timeout=TIMEOUT)
    r.raise_for_status()

    partite = {}
    for m in r.json():
        quando = datetime.strptime(m['DateUtc'], '%Y-%m-%d %H:%M:%SZ').replace(tzinfo=timezone.utc)
        casa, fuori = SQUADRE.get(m['HomeTeam'], m['HomeTeam']), SQUADRE.get(m['AwayTeam'], m['AwayTeam'])
        partite.setdefault(int(m['RoundNumber']), []).append((quando, casa, fuori))

    giornate = {}
    for n, lista in sorted(partite.items()):
        if len(lista) != 10:
            raise ValueError(f'giornata {n} con {len(lista)} partite: la fonte ha cambiato struttura')
        lista.sort()
        if any((q.hour, q.minute) == (0, 0) for q, _, _ in lista):
            vecchia = vecchie.get(str(n))
            if vecchia and vecchia.get('ufficiale'):
                print(f'[orari] giornata {n}: la fonte non ha piu\' l\'orario, tengo quello noto.')
                giornate[str(n)] = vecchia
            else:
                giornate[str(n)] = {'ufficiale': False}
            continue
        primo, casa, fuori = lista[0]
        # un recupero spostato di settimane non deve allungare la giornata
        vicine = [q for q, _, _ in lista if q - primo <= timedelta(days=4)]
        giornate[str(n)] = {
            'ufficiale': True,
            'inizio': primo.isoformat(),
            'fine': max(vicine).isoformat(),
            'prima': f'{casa}-{fuori}',
        }

    uff = sum(1 for g in giornate.values() if g['ufficiale'])
    print(f'[orari] {uff} giornate con orario ufficiale su {len(giornate)}.')
    return {'aggiornato': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'giornate': giornate}


def main():
    listone = carica_listone()
    print(f'listone: {len(listone)} calciatori')
    uscita = 0

    try:
        scrivi(os.path.join(DATI, 'infortuni.json'), infortuni(listone), 5, 'infortuni')
    except Exception as e:
        print('[infortuni] fallito:', e)
        uscita = 1

    try:
        scrivi(os.path.join(DATI, 'titolari.json'), probabili(listone), 150, 'titolari')
    except Exception as e:
        print('[titolari] fallito:', e)
        uscita = 1

    try:
        percorso = os.path.join(DATI, 'orari.json')
        scrivi(percorso, orari(precedenti(percorso, 'giornate')), 38, 'orari')
    except Exception as e:
        print('[orari] fallito:', e)
        uscita = 1

    sys.exit(uscita)


if __name__ == '__main__':
    main()
