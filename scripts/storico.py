"""Lo storico dei voti di fantacalcio.it, dalla stagione 2015-16 alla 2025-26: la
materia prima per il fantavoto atteso (CLAUDE.md, «Da fare: il cervello di Jarvis», B1).

Una stagione per file, compresso: dati/storico/<stagione>.json.gz, con per ogni
giornata e ogni giocatore (per Id) voto, fantavoto, ruolo, squadra e bonus e malus
(CAMPI). Le stagioni chiuse non cambiano più: si scrivono una volta, e lo zip non
contiene date, così lo stesso contenuto dà sempre lo stesso file. Lo storico non si
serve all'iPhone: resta materia prima per l'addestramento.

Il giro è ripartibile (salta le giornate già prese e salva dopo ognuna, così
un'interruzione non fa ricominciare) ed educato con la fonte (una pausa tra le
richieste). Una giornata con meno di 200 voti non si salva, come in aggiorna.py.

Uso, dal PC (con Norton serve truststore, vedi CLAUDE.md, «Come si prova»):
  python scripts/storico.py                       tutte le stagioni
  python scripts/storico.py 2021-22 2022-23       solo quelle
  python scripts/storico.py --prova 2021-22 10    una giornata: numeri a schermo, niente file
"""
import gzip, importlib.util, json, os, sys, time

QUI = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('aggiorna', os.path.join(QUI, 'aggiorna.py'))
aggiorna = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(aggiorna)

STAGIONI = [f'{a}-{(a + 1) % 100:02d}' for a in range(2015, 2026)]     # 2015-16 ... 2025-26
GIORNATE = 38
URL = 'https://www.fantacalcio.it/voti-fantacalcio-serie-a/{stagione}/{giornata}'
URL_QUOTAZIONI = 'https://www.fantacalcio.it/quotazioni-fantacalcio/{stagione}'
URL_CALENDARIO = 'https://fixturedownload.com/feed/json/serie-a-{anno}'
CARTELLA = os.path.join(aggiorna.DATI, 'storico')
PAUSA = 2.0                     # secondi tra una richiesta e l'altra
MINIMO = 200                    # sotto, la pagina non è pronta o ha cambiato struttura
MINIMO_QUOTAZIONI = 400         # una stagione ne ha 600-700
CAMPI = ['voto', 'fantavoto', 'ruolo', 'squadra'] + aggiorna.BONUS_VOTI


def percorso(stagione, cartella=CARTELLA):
    return os.path.join(cartella, stagione + '.json.gz')


def leggi(stagione, cartella=CARTELLA):
    """La stagione già salvata, o una vuota."""
    p = percorso(stagione, cartella)
    if not os.path.exists(p):
        return {'stagione': stagione, 'campi': CAMPI, 'giornate': {}}
    with gzip.open(p, 'rt', encoding='utf-8') as f:
        return json.load(f)


def salva(dati, cartella=CARTELLA):
    """Scrive la stagione compressa, prima in un file temporaneo: un'interruzione a metà
    non lascia mai un file rotto. Senza data né nome dentro lo zip."""
    os.makedirs(cartella, exist_ok=True)
    p = percorso(dati['stagione'], cartella)
    tmp = p + '.tmp'
    testo = json.dumps(dati, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
    with open(tmp, 'wb') as grezzo, gzip.GzipFile(filename='', mode='wb', fileobj=grezzo, mtime=0) as z:
        z.write(testo.encode('utf-8'))
    os.replace(tmp, p)


def giornata(stagione, n):
    """{Id: [voto, fantavoto, ruolo, squadra, bonus...]} di una giornata, nell'ordine di CAMPI."""
    r = aggiorna.requests.get(URL.format(stagione=stagione, giornata=n), headers=aggiorna.UA,
                              timeout=aggiorna.TIMEOUT)
    r.raise_for_status()
    return {x['id']: [x['voto'], x['fantavoto'], x['ruolo'], x['squadra']] + x['bonus']
            for x in aggiorna.righe_voti(r.text)}


def quotazioni(stagione):
    """{Id: [quotazione iniziale, quotazione finale, ruolo]} di una stagione, dalla pagina
    pubblica delle quotazioni (Classic). Per il modello conta l'iniziale: è nota prima
    delle partite, la finale invece si muove con il rendimento della stagione."""
    r = aggiorna.requests.get(URL_QUOTAZIONI.format(stagione=stagione), headers=aggiorna.UA,
                              timeout=aggiorna.TIMEOUT)
    r.raise_for_status()
    out = {}
    for tr in aggiorna.BeautifulSoup(r.text, 'lxml').select('tr.player-row'):
        a = tr.find('a', href=aggiorna.ID_GIOCATORE)
        qi, qa = tr.select_one('td[data-col-key="c_qi"]'), tr.select_one('td[data-col-key="c_qa"]')
        if not (a and qi and qa):
            continue
        try:
            out[aggiorna.ID_GIOCATORE.search(a['href']).group(1)] = [
                int(qi.get_text(strip=True)), int(qa.get_text(strip=True)),
                (tr.get('data-filter-role-classic') or '').upper() or None]
        except ValueError:
            continue
    return out


def calendario(stagione):
    """Le partite della stagione dal feed di fixturedownload: [giornata del feed, casa,
    fuori, gol casa, gol fuori], con i nomi di fantacalcio.it (aggiorna.SQUADRE). Una
    lista vuota se il feed di quella stagione non esiste (404: il 2015-16 e il 2016-17).
    Attenzione: la giornata del feed non è sempre quella ufficiale (rinvii), vedi
    CLAUDE.md, B2."""
    r = aggiorna.requests.get(URL_CALENDARIO.format(anno=stagione[:4]), headers=aggiorna.UA,
                              timeout=aggiorna.TIMEOUT)
    if r.status_code == 404:
        return []
    r.raise_for_status()
    nome = lambda x: aggiorna.SQUADRE.get(x, x)
    return [[x['RoundNumber'], nome(x['HomeTeam']), nome(x['AwayTeam']), x.get('HomeTeamScore'), x.get('AwayTeamScore')]
            for x in r.json()]


def scarica(stagioni, cartella=CARTELLA, pausa=PAUSA, dormi=time.sleep):
    """Scarica le giornate che mancano, e una volta sola le quotazioni e il calendario
    della stagione; {stagione: (giornate salvate, nuove, saltate)}."""
    esito = {}
    for s in stagioni:
        dati = leggi(s, cartella)
        nuove = saltate = 0
        for n in range(1, GIORNATE + 1):
            if str(n) in dati['giornate']:
                continue
            try:
                g = giornata(s, n)
            except Exception as e:
                print(f'[storico] {s} giornata {n}: {e}')
                saltate += 1
                dormi(pausa)
                continue
            if len(g) < MINIMO:
                print(f'[storico] {s} giornata {n}: solo {len(g)} voti, la salto.')
                saltate += 1
            else:
                dati['giornate'][str(n)] = g
                salva(dati, cartella)
                nuove += 1
            dormi(pausa)
        # un errore di rete non segna niente: al giro dopo si riprova
        if 'quotazioni' not in dati:
            try:
                q = quotazioni(s)
                if len(q) >= MINIMO_QUOTAZIONI:
                    dati['quotazioni'] = q
                    salva(dati, cartella)
                else:
                    print(f'[storico] {s}: solo {len(q)} quotazioni, le salto.')
            except Exception as e:
                print(f'[storico] {s} quotazioni: {e}')
            dormi(pausa)
        if 'partite' not in dati:
            try:
                c = calendario(s)
                if c == [] or len(c) >= 300:
                    dati['partite'] = c
                    salva(dati, cartella)
                else:
                    print(f'[storico] {s}: calendario con solo {len(c)} partite, lo salto.')
            except Exception as e:
                print(f'[storico] {s} calendario: {e}')
            dormi(pausa)
        esito[s] = (len(dati['giornate']), nuove, saltate)
        print(f'[storico] {s}: {len(dati["giornate"])}/{GIORNATE} giornate ({nuove} nuove, {saltate} saltate)')
    return esito


def copertura(stagioni, cartella=CARTELLA):
    """Quanti Id del listone di oggi compaiono in ogni stagione salvata. Se gli Id non
    fossero stabili tra le stagioni, il collegamento storia-giocatore salterebbe."""
    listone = {str(p['id']) for p in aggiorna.carica_listone()}
    for s in stagioni:
        ids = {i for g in leggi(s, cartella)['giornate'].values() for i in g}
        print(f'[storico] {s}: {len(ids)} giocatori con voto, {len(ids & listone)} ancora nel listone di oggi')


if __name__ == '__main__':
    argomenti = sys.argv[1:]
    if argomenti[:1] == ['--prova']:
        s, n = argomenti[1], int(argomenti[2])
        g = giornata(s, n)
        listone = {str(p['id']) for p in aggiorna.carica_listone()}
        print(f'{s} giornata {n}: {len(g)} voti, {len(set(g) & listone)} Id ancora nel listone di oggi')
        for i, riga in list(g.items())[:3]:
            print(' ', i, dict(zip(CAMPI, riga)))
    else:
        scelte = argomenti or STAGIONI
        scarica(scelte)
        copertura(scelte)
