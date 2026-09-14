#!/usr/bin/env python3
"""
Aggiorna i dati vivi di Jarvis: infortunati, probabili formazioni, orari e
rendimento delle squadre.

Scrive cinque file in dati/:
  dati/infortuni.json   { "aggiornato": "...", "voci": { "<id>": {...} } }
  dati/titolari.json    { "aggiornato": "...", "giornata": 5, "squadre": [...],
                          "titolari": { "<id>": 97 }, "panchina": { "<id>": 30 },
                          "indisponibili": { "<id>": { "motivo": "Squalificato", "fino": "28/10" } } }
  dati/orari.json       { "aggiornato": "...", "giornate": { "<giornata Serie A>": {...} } }
  dati/squadre.json     { "aggiornato": "...", "squadre": { "<squadra>": {...} }, ... }
  dati/jarvis.ics       calendario da sottoscrivere: scadenze di schieramento
  dati/statistiche.json { "aggiornato": "...", "giocatori": { "<id>": [partite, MV, FM, quotazione,
                          gol, gol subiti, rigori parati, assist, ammonizioni, espulsioni] } }
  dati/voti.json        { "aggiornato": "...", "giornate": { "<n>": { "<id>": [voto, fantavoto] } } }

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

UA = {'User-Agent': 'Jarvis/1.0 (uso personale; aggiornamento 3 volte al giorno)'}
TIMEOUT = 30

URL_INFORTUNI = 'https://www.fantacalcio-online.com/it/infortunati-serie-a'
# probabili della singola giornata: media di quattro redazioni
URL_GIORNATA = 'https://www.fantacalcio-online.com/it/serie-a/2026-2027/probabili-formazioni/{}-giornata'
# formazioni tipo di stagione: servono solo per il modulo abituale, mai per la titolarita'
URL_SQUADRE_TIPO = 'https://www.fantacalcio-online.com/it/consigli-fantacalcio/probabili-formazioni-serie-a'
URL_ORARI = 'https://fixturedownload.com/feed/json/serie-a-2026'
# statistiche e quotazioni pubbliche di fantacalcio.it (senza login), con l'Id del listone nei link
URL_STATISTICHE = 'https://www.fantacalcio.it/statistiche-serie-a/2026-27/fantacalcio/riepilogo'
URL_QUOTAZIONI = 'https://www.fantacalcio.it/quotazioni-fantacalcio'
URL_VOTI = 'https://www.fantacalcio.it/voti-fantacalcio-serie-a/2026-27/{}'   # voti di ogni giornata
ORE_STATISTICHE = 20   # cambiano solo dopo le partite: basta un giro al giorno
URL_PRECEDENTE = 'https://fixturedownload.com/feed/json/serie-a-2025'

# nomi del feed delle partite che differiscono da quelli del listone
SQUADRE = {'Internazionale': 'Inter'}

URL_APP = 'https://manzochinaglia.github.io/JARVIS/'
DOMINIO = 'manzochinaglia.github.io'


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
    return trova_composto(listone, squadra, nome)


def iniziale(parole):
    """L'iniziale del nome, se l'ultima parola e' una lettera sola."""
    return parole[-1] if parole and len(parole[-1]) == 1 else None


def trova_composto(listone, squadra, nome):
    """Ripiego per cognomi composti o scritti in altro modo: "DEL PRATO E" e
    "Delprato", "MILINKOVIC V" e "Milinkovic-Savic V.", "NUNO TAVARES" e
    "Tavares N.". Solo dentro la squadra, mai con iniziali diverse, e solo se il
    candidato e' uno: meglio nessun abbinamento che uno sbagliato."""
    parti = norm(nome).split()
    ini = iniziale(parti)
    lungo = ''.join(w for w in parti if len(w) > 1)
    if len(lungo) < 4:
        return None
    candidati = []
    for p in listone:
        if norm(p['squadra']) != norm(squadra):
            continue
        pn = norm(p['nome']).split()
        pini = iniziale(pn)
        if ini and pini and ini != pini:
            continue
        suo = ''.join(w for w in pn if len(w) > 1)
        if len(suo) >= 4 and (suo in lungo or lungo in suo):
            candidati.append(p)
    return candidati[0] if len(candidati) == 1 else None


def scrivi(percorso, contenuto, minimo, etichetta, n=None):
    """Scrive solo se il risultato e' plausibile, altrimenti lascia il file com'e'.
    n: quante voci contare, se non e' la lunghezza della prima raccolta del file."""
    if n is None:
        voci = next((contenuto[k] for k in ('voci', 'stato', 'giornate', 'titolari', 'squadre') if k in contenuto), {})
        n = len(voci)
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


def leggi_nome(span):
    """"FALCONE <small>W</small>" -> "FALCONE W". Il trattino vuol dire nessuna iniziale."""
    cognome = ' '.join(''.join(span.find_all(string=True, recursive=False)).split())
    small = span.find('small')
    ini = small.get_text(strip=True) if small else ''
    return f'{cognome} {ini}' if ini and ini != '-' else cognome


def percentuale(td):
    m = re.search(r'(\d{1,3})\s*%', td.get_text(' ', strip=True)) if td else None
    return int(m.group(1)) if m else None


def giornata_da_seguire(lega, giornate, ora=None):
    """La giornata di Serie A della prossima giornata di lega: la prima non ancora
    finita. Stessa regola dell'app: finisce due ore dopo l'ultimo calcio d'inizio."""
    ora = ora or datetime.now(timezone.utc)
    for n in lega:
        g = giornate.get(str(n)) or {}
        if not g.get('ufficiale'):
            return n                      # orario non ancora fissato: e' futura
        if datetime.fromisoformat(g['fine']) + timedelta(hours=2) > ora:
            return n
    return None


def titolari(listone, n):
    """Probabili formazioni della giornata n: percentuale media di schierabilita'
    delle quattro redazioni, per i titolari e per la panchina.

    Le squadre per cui nessuna redazione ha ancora pubblicato restano fuori:
    l'app le mostra come "probabili non ancora uscite" invece di indovinare.
    """
    r = requests.get(URL_GIORNATA.format(n), headers=UA, timeout=TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')
    titolo = soup.title.get_text(strip=True) if soup.title else ''
    if not re.search(rf'\b{n}\s*[ªa°]?\s*giornata', titolo, re.I):
        raise ValueError(f'la pagina non e\' della giornata {n}: {titolo!r}')
    blocchi = soup.select('.prb-squadra')
    if len(blocchi) != 20:
        raise ValueError(f'{len(blocchi)} squadre invece di 20: la fonte ha cambiato struttura')

    tit, panca, indisp, pubblicate, mancati = {}, {}, {}, [], []
    for b in blocchi:
        squadra = b.select_one('.prb-squadra__nome').get_text(' ', strip=True)
        # indisponibili della giornata (infortunati e squalificati): escono prima delle probabili
        for riga in b.select('.prb-fuori__riga'):
            span = riga.select_one('.prb-nome')
            if not span:
                continue
            nome = leggi_nome(span)
            p = trova(listone, squadra, nome)
            if not p:
                mancati.append(f'{squadra} {nome}')
                continue
            etichetta = riga.select_one('.fco-etichetta')
            voce = {'motivo': etichetta.get_text(' ', strip=True) if etichetta else 'Indisponibile'}
            data = riga.select_one('.prb-fuori__data')
            fino = re.search(r'(\d{1,2})/(\d{1,2})', data.get_text()) if data else None
            if fino:
                voce['fino'] = f'{int(fino[1]):02d}/{int(fino[2]):02d}'
            indisp[str(p['id'])] = voce

        tabelle = b.select('table.prb-tabella')
        if not tabelle:
            continue                      # nessuna redazione ha ancora pubblicato
        for i, tabella in enumerate(tabelle[:2]):
            righe = tabella.select('tbody tr')
            if i == 0 and len(righe) != 11:
                raise ValueError(f'{squadra}: {len(righe)} titolari invece di 11')
            for tr in righe:
                span = tr.select_one('.prb-nome')
                perc = percentuale(tr.select_one('.prb-cella--media'))
                if not span or perc is None:
                    continue
                nome = leggi_nome(span)
                p = trova(listone, squadra, nome)
                if p:
                    (tit if i == 0 else panca)[str(p['id'])] = perc
                else:
                    mancati.append(f'{squadra} {nome}')
        pubblicate.append(squadra)

    if mancati:
        print('[titolari] non abbinati:', ', '.join(mancati))
    squalificati = sum(1 for v in indisp.values() if v['motivo'].lower().startswith('squalific'))
    print(f'[titolari] giornata {n}: {len(pubblicate)} squadre pubblicate su 20, '
          f'{len(indisp)} indisponibili ({squalificati} squalificati).')
    return {'aggiornato': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'giornata': n,
            'squadre': sorted(pubblicate), 'titolari': tit, 'panchina': panca, 'indisponibili': indisp}


def titolari_utili(t):
    """Si scrive se ci sono le probabili di almeno una squadra, oppure gli
    indisponibili della giornata, che escono giorni prima delle probabili."""
    return len(t['titolari']) >= 11 or len(t.get('indisponibili', {})) >= 5


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
            # ogni partita con il suo orario: l'app dice quando gioca ogni tuo giocatore
            'partite': [[c, f, q.isoformat()] for q, c, f in lista],
        }

    uff = sum(1 for g in giornate.values() if g['ufficiale'])
    print(f'[orari] {uff} giornate con orario ufficiale su {len(giornate)}.')
    return {'aggiornato': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'giornate': giornate}


def righe_con_id(url):
    """Righe della tabella principale di una pagina di fantacalcio.it: l'Id del
    listone viene dal link del giocatore (…/roma/svilar/5841), non dal nome."""
    r = requests.get(url, headers=UA, timeout=TIMEOUT)
    r.raise_for_status()
    tabella = BeautifulSoup(r.text, 'lxml').find('table')
    if not tabella:
        raise ValueError(f'nessuna tabella in {url}: la fonte ha cambiato struttura')
    intestazione = [c.get_text(' ', strip=True) for c in tabella.find_all('th')]
    righe = {}
    for tr in tabella.find_all('tr'):
        a = tr.find('a', href=re.compile(r'/\d+/?$'))
        if a:
            righe[int(a['href'].rstrip('/').rsplit('/', 1)[1])] = [c.get_text(' ', strip=True) for c in tr.find_all(['td', 'th'])]
    return intestazione, righe


def numero(testo):
    t = (testo or '').replace(',', '.').strip()
    return float(t) if re.fullmatch(r'-?\d+(\.\d+)?', t) else 0.0


BONUS = ['Gol', 'GS', 'Rig', 'RP', 'Ass', 'Amm', 'Esp']


def statistiche():
    """Partite a voto, media voto, fantamedia e quotazione di ogni giocatore, dalle
    pagine pubbliche: sostituiscono l'esportazione settimanale per le statistiche.
    Dalla stessa pagina anche bonus e malus: gol, gol subiti, rigori parati, assist,
    ammonizioni, espulsioni. Se cambiano solo quelle colonne si salvano le
    statistiche principali, senza i bonus: meglio un trattino che un numero sbagliato."""
    testa, stat = righe_con_id(URL_STATISTICHE)
    if testa[5:8] != ['PV', 'MV', 'FM']:
        raise ValueError(f'colonne delle statistiche inattese: {testa[5:8]}')
    bonus = testa[8:15] == BONUS
    if not bonus:
        print(f'[statistiche] colonne dei bonus inattese {testa[8:15]}: salvo senza gol e assist.')
    testaq, quot = righe_con_id(URL_QUOTAZIONI)
    if testaq[5:7] != ['QI', 'QA']:
        raise ValueError(f'colonne delle quotazioni inattese: {testaq[5:7]}')
    giocatori = {}
    for i in set(stat) | set(quot):
        s, q = stat.get(i), quot.get(i)
        riga = [int(numero(s[5])) if s else 0, round(numero(s[6]), 2) if s else 0.0,
                round(numero(s[7]), 2) if s else 0.0, int(numero(q[6])) if q else 0]
        if bonus:   # Gol, GS, RP, Ass, Amm, Esp (Rig, «segnati / calciati», non serve)
            riga += [int(numero(s[k])) if s and len(s) > k else 0 for k in (8, 9, 11, 12, 13, 14)]
        giocatori[str(i)] = riga
    print(f'[statistiche] {len(stat)} giocatori con statistiche, {len(quot)} con quotazione.')
    return {'aggiornato': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'giocatori': giocatori}


def voti_giornata(n):
    """Voto e fantavoto della redazione Fantacalcio di ogni giocatore della giornata n di
    Serie A, per Id (dal link del giocatore). Chi non ha preso voto non c'è. Nella riga
    il primo voto e il primo fantavoto sono della redazione Fantacalcio; poi vengono i
    voti di altre redazioni, che qui non servono."""
    r = requests.get(URL_VOTI.format(n), headers=UA, timeout=TIMEOUT)
    r.raise_for_status()
    voti = {}
    for tr in BeautifulSoup(r.text, 'lxml').select('table.grades-table tbody tr'):
        a = tr.find('a', href=re.compile(r'/\d+/?$'))
        v, fv = tr.find('span', class_='player-grade'), tr.find('span', class_='player-fanta-grade')
        if not (a and v and fv):
            continue
        try:
            voto = float(v.get('data-value', '').replace(',', '.'))
            fanta = float(fv.get('data-value', '').replace(',', '.'))
        except ValueError:
            continue                              # senza voto
        voti[str(int(a['href'].rstrip('/').rsplit('/', 1)[1]))] = [voto, fanta]
    return voti


def voti(giornate_orari, vecchie, ora=None):
    """I voti delle giornate di Serie A finite da almeno 6 ore: quelle nuove e, per tre
    giorni dalla fine, di nuovo (i voti si assestano). Una giornata con meno di 200 voti
    non si salva: la pagina non è ancora pronta o ha cambiato struttura."""
    ora = ora or datetime.now(timezone.utc)
    giornate = dict(vecchie)
    for n, g in sorted(giornate_orari.items(), key=lambda x: int(x[0])):
        if not g.get('ufficiale') or 'fine' not in g:
            continue
        passato = ora - datetime.fromisoformat(g['fine'])
        if passato < timedelta(hours=6) or (n in giornate and passato > timedelta(days=3)):
            continue
        v = voti_giornata(int(n))
        if len(v) >= 200:
            giornate[n] = v
        else:
            print(f'[voti] giornata {n}: solo {len(v)} voti, la salto.')
    return {'aggiornato': ora.isoformat(timespec='seconds'), 'giornate': giornate}


def recente(percorso, ore, ora=None):
    """Vero se il file è stato scritto da meno di `ore` ore."""
    try:
        with open(percorso, encoding='utf-8') as f:
            quando = datetime.fromisoformat(json.load(f)['aggiornato'])
    except (OSError, ValueError, KeyError):
        return False
    return (ora or datetime.now(timezone.utc)) - quando < timedelta(hours=ore)


def rendimento(partite):
    """Per squadra e per campo: [partite, gol fatti, gol subiti, porte inviolate]."""
    tab = {}
    for m in partite:
        if m.get('HomeTeamScore') is None or m.get('AwayTeamScore') is None:
            continue
        casa, fuori = SQUADRE.get(m['HomeTeam'], m['HomeTeam']), SQUADRE.get(m['AwayTeam'], m['AwayTeam'])
        gc, gf = int(m['HomeTeamScore']), int(m['AwayTeamScore'])
        for squadra, campo, fatti, subiti in ((casa, 'casa', gc, gf), (fuori, 'fuori', gf, gc)):
            s = tab.setdefault(squadra, {'casa': [0, 0, 0, 0], 'fuori': [0, 0, 0, 0]})[campo]
            s[0] += 1
            s[1] += fatti
            s[2] += subiti
            s[3] += int(subiti == 0)
    return tab


def somma(righe):
    return [sum(x) for x in zip(*righe)] if righe else [0, 0, 0, 0]


def moduli():
    """Modulo abituale di ogni squadra, dalla tabella delle formazioni tipo di stagione."""
    r = requests.get(URL_SQUADRE_TIPO, headers=UA, timeout=TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')
    out = {}
    for tr in soup.select('div.art-tabella tr'):
        celle = [td.get_text(' ', strip=True) for td in tr.find_all('td')]
        if len(celle) >= 2 and re.fullmatch(r'[3-5](-[1-5]){2,3}', celle[1]):
            out.setdefault(celle[0], celle[1])
    return out


def squadre(abituali):
    """Rendimento di ogni squadra in casa e fuori, quest'anno e l'anno scorso, e il
    suo modulo abituale. L'app mescola le due stagioni: con poche partite giocate i
    numeri di quest'anno sono rumore.

    Le neopromosse non hanno la Serie A dell'anno scorso: al loro posto si usa la
    media delle tre retrocesse, segnata come stima.
    """
    attuale = requests.get(URL_ORARI, headers=UA, timeout=TIMEOUT)
    attuale.raise_for_status()
    passata = requests.get(URL_PRECEDENTE, headers=UA, timeout=TIMEOUT)
    passata.raise_for_status()
    partite, vecchie = attuale.json(), passata.json()
    if len(vecchie) != 380 or any(m.get('HomeTeamScore') is None for m in vecchie):
        raise ValueError('stagione precedente incompleta: la fonte ha cambiato struttura')

    elenco = sorted({SQUADRE.get(m['HomeTeam'], m['HomeTeam']) for m in partite})
    ora, prima = rendimento(partite), rendimento(vecchie)
    retrocesse = sorted(s for s in prima if s not in elenco)
    if len(elenco) != 20 or len(retrocesse) != 3:
        raise ValueError(f'{len(elenco)} squadre e {len(retrocesse)} retrocesse: la fonte ha cambiato struttura')
    stima = {c: [round(x / 3, 2) for x in somma([prima[s][c] for s in retrocesse])] for c in ('casa', 'fuori')}

    out = {}
    for s in elenco:
        voce = {'attuale': ora.get(s) or {'casa': [0, 0, 0, 0], 'fuori': [0, 0, 0, 0]}}
        if s in prima:
            voce['precedente'] = prima[s]
        else:
            voce['precedente'], voce['neopromossa'] = stima, True
        if abituali.get(s):
            voce['modulo'] = abituali[s]
        out[s] = voce

    return {'aggiornato': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'squadre': out,
            'campionato_precedente': {c: somma([prima[s][c] for s in prima]) for c in ('casa', 'fuori')},
            'retrocesse': retrocesse}


# definizione standard di Europe/Rome, per i client che non la conoscono gia'
FUSO_ROMA = [
    'BEGIN:VTIMEZONE', 'TZID:Europe/Rome',
    'BEGIN:DAYLIGHT', 'TZOFFSETFROM:+0100', 'TZOFFSETTO:+0200', 'TZNAME:CEST',
    'DTSTART:19700329T020000', 'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU', 'END:DAYLIGHT',
    'BEGIN:STANDARD', 'TZOFFSETFROM:+0200', 'TZOFFSETTO:+0100', 'TZNAME:CET',
    'DTSTART:19701025T030000', 'RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU', 'END:STANDARD',
    'END:VTIMEZONE',
]


def testo_ics(s):
    """Testo di una proprieta' iCalendar: barra rovescia, ; , e a capo vanno protetti."""
    return str(s).replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')


def piega(riga):
    """Righe di al massimo 75 byte; le continuazioni iniziano con uno spazio (RFC 5545)."""
    pezzi, corrente = [], ''
    for c in riga:
        if len((corrente + c).encode('utf-8')) > (74 if pezzi else 75):
            pezzi.append(corrente)
            corrente = c
        else:
            corrente += c
    pezzi.append(corrente)
    return '\r\n '.join(pezzi)


def utc_ics(d):
    return d.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')


def calendario(base, giornate, ora=None):
    """Calendario da sottoscrivere sull'iPhone.

    Una scadenza per ogni giornata di lega con orario ufficiale, 15 minuti prima
    del primo anticipo, con un avviso 2 ore prima; le altre non ci sono, perche'
    l'orario sarebbe inventato. (Il promemoria del martedi' per esportare la Lista
    calciatori e' stato tolto: le statistiche ora sono automatiche.)

    Gli UID sono stabili: un orario cambiato aggiorna l'evento, non lo duplica.
    Restituisce il testo e il numero di scadenze.
    """
    stamp = utc_ics(ora or datetime.now(timezone.utc))
    me = base['me']
    eventi, scadenze = [], 0
    for n, sa, _, partite in (g[:4] for g in base['g']):
        o = giornate.get(str(sa)) or {}
        if not o.get('ufficiale'):
            continue
        avv = next(((b, True) if a == me else (a, False) for a, b in partite if me in (a, b)), None)
        inizio = datetime.fromisoformat(o['inizio'])
        titolo = f'Schiera la formazione · G{n}' + (f' contro {avv[0]}' if avv else '')
        nota = (f'Si chiude 15 minuti prima del primo anticipo, {o["prima"]}.'
                + (f'\nGiochi {"in casa" if avv[1] else "in trasferta"}.' if avv else '')
                + f'\nApri Jarvis: {URL_APP}')
        eventi += ['BEGIN:VEVENT', f'UID:jarvis-scadenza-g{n}@{DOMINIO}', f'DTSTAMP:{stamp}',
                   f'DTSTART:{utc_ics(inizio - timedelta(minutes=15))}', f'DTEND:{utc_ics(inizio)}',
                   f'SUMMARY:{testo_ics(titolo)}', f'DESCRIPTION:{testo_ics(nota)}', f'URL:{URL_APP}',
                   'BEGIN:VALARM', 'ACTION:DISPLAY', 'TRIGGER:-PT2H',
                   f'DESCRIPTION:{testo_ics("Tra 2 ore si chiude la formazione")}', 'END:VALARM',
                   'END:VEVENT']
        scadenze += 1

    righe = (['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Jarvis//Fantacalcio//IT', 'CALSCALE:GREGORIAN',
              'METHOD:PUBLISH', f'X-WR-CALNAME:{testo_ics("Jarvis · fantacalcio")}', 'X-WR-TIMEZONE:Europe/Rome',
              'REFRESH-INTERVAL;VALUE=DURATION:PT6H', 'X-PUBLISHED-TTL:PT6H']
             + FUSO_ROMA + eventi + ['END:VCALENDAR'])
    return '\r\n'.join(piega(r) for r in righe) + '\r\n', scadenze


def main():
    listone = carica_listone()
    print(f'listone: {len(listone)} calciatori')
    uscita = 0

    try:
        scrivi(os.path.join(DATI, 'infortuni.json'), infortuni(listone), 5, 'infortuni')
    except Exception as e:
        print('[infortuni] fallito:', e)
        uscita = 1

    percorso = os.path.join(DATI, 'orari.json')
    try:
        scrivi(percorso, orari(precedenti(percorso, 'giornate')), 38, 'orari')
    except Exception as e:
        print('[orari] fallito:', e)
        uscita = 1

    # i voti di ogni giornata finita: «com'è andata» e l'andamento dei giocatori.
    # Il file si riscrive solo se cambia qualcosa, per non fare un commit a ogni giro.
    percorso_voti = os.path.join(DATI, 'voti.json')
    try:
        vecchie = precedenti(percorso_voti, 'giornate')
        v = voti(precedenti(percorso, 'giornate'), vecchie)
        if v['giornate'] != vecchie:
            scrivi(percorso_voti, v, 1, 'voti')
        else:
            print('[voti] niente di nuovo.')
    except Exception as e:
        print('[voti] fallito:', e)
        uscita = 1

    # le probabili della giornata che interessa la lega, secondo gli orari salvati
    try:
        with open(os.path.join(DATI, 'base.json'), encoding='utf-8') as f:
            lega = [g[1] for g in json.load(f)['g']]
        n = giornata_da_seguire(lega, precedenti(percorso, 'giornate'))
        if n is None:
            print('[titolari] campionato finito, niente da scaricare.')
        else:
            t = titolari(listone, n)
            if titolari_utili(t):
                scrivi(os.path.join(DATI, 'titolari.json'), t, 0, 'titolari',
                       n=len(t['titolari']) + len(t['panchina']) + len(t['indisponibili']))
            else:
                print('[titolari] né probabili né indisponibili per questa giornata: tengo il file precedente.')
    except Exception as e:
        print('[titolari] fallito:', e)
        uscita = 1

    percorso_st = os.path.join(DATI, 'statistiche.json')
    try:
        if recente(percorso_st, ORE_STATISTICHE):
            print(f'[statistiche] aggiornate da meno di {ORE_STATISTICHE} ore: salto.')
        else:
            st = statistiche()
            scrivi(percorso_st, st, 400, 'statistiche', n=len(st['giocatori']))
    except Exception as e:
        print('[statistiche] fallito:', e)
        uscita = 1

    # senza nessuna scadenza il file non si riscrive: l'iPhone cancellerebbe gli eventi
    try:
        with open(os.path.join(DATI, 'base.json'), encoding='utf-8') as f:
            testo, scadenze = calendario(json.load(f), precedenti(percorso, 'giornate'))
        if scadenze == 0:
            print('[calendario] nessuna scadenza con orario ufficiale: non aggiorno, tengo il file precedente.')
        else:
            with open(os.path.join(DATI, 'jarvis.ics'), 'w', encoding='utf-8', newline='') as f:
                f.write(testo)
            print(f'[calendario] scritte {scadenze} scadenze.')
    except Exception as e:
        print('[calendario] fallito:', e)
        uscita = 1

    try:
        try:
            abituali = moduli()
        except Exception as e:
            print('[moduli] fallito, proseguo senza:', e)
            abituali = {}
        scrivi(os.path.join(DATI, 'squadre.json'), squadre(abituali), 20, 'squadre')
    except Exception as e:
        print('[squadre] fallito:', e)
        uscita = 1

    sys.exit(uscita)


if __name__ == '__main__':
    main()
