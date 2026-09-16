#!/usr/bin/env python3
"""
Aggiorna le rose della lega in dati/base.json dal file delle rose di Leghe
Fantacalcio, dopo uno scambio o durante il mercato. Accetta:
- il file dell'app, «<lega>-rosters-<numero>.xlsx»: un blocco di colonne per
  squadra (nome, «costo»), 25 giocatori in ordine P, D, C, A, riga «totale»
- rose.csv, con l'Id del listone per ogni giocatore

Uso: python scripts/importa_rose.py [percorso] [--prova] [--nomi-app]
Senza percorso prende il file delle rose più recente nella cartella Download.
Con --prova mostra cosa cambierebbe, senza scrivere niente.
Con --nomi-app adotta in tutto base.json i nomi di squadra del file dell'app.
Dopo l'importazione il file usato passa dalla cartella Download a archivio/rose
(fuori da Git): la cartella Download resta pulita e non si cancella niente.

- tocca solo le rose (squadra, prezzo, ruolo, nome, quotazione) e la data "v":
  calendario e sfide restano quelli di base.json
- partite, MV e FM vengono da dati/statistiche.json se c'è, altrimenti restano
  quelli di prima (0 per chi arriva adesso)
- controlla 10 squadre da 25 (3 P, 8 D, 8 C, 6 A) con i nomi del calendario:
  al primo problema si ferma e non scrive niente
- aggiunge al listone i giocatori nuovi, così lo script li riconosce nelle
  probabili e negli infortuni
"""
import csv, glob, json, os, re, shutil, sys, unicodedata
from collections import Counter
from datetime import date

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(RADICE, 'dati')
DOWNLOAD = os.path.join(os.path.expanduser('~'), 'Downloads')
ARCHIVIO = os.path.join(RADICE, 'archivio', 'rose')     # file già importati, esclusi da Git
RUOLI = {'P': 3, 'D': 8, 'C': 8, 'A': 6}
RUOLI_IN_ORDINE = ['P'] * 3 + ['D'] * 8 + ['C'] * 8 + ['A'] * 6   # come nei blocchi dell'app


def norm(s):
    """Per confrontare i nomi: senza accenti, maiuscole, spazi e punteggiatura."""
    s = unicodedata.normalize('NFD', str(s or '')).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]', '', s.lower())


def leggi_json(nome):
    with open(os.path.join(DATI, nome), encoding='utf-8') as f:
        return json.load(f)


def testo_json(dati):
    """Stesso formato dei file in dati/: compatto, su una riga, accenti leggibili."""
    return json.dumps(dati, ensure_ascii=False, separators=(',', ':'))


def trova_file(cartella):
    """Il file delle rose più recente: quello dell'app (…rosters….xlsx) o rose*.csv."""
    file = glob.glob(os.path.join(cartella, '*rosters*.xlsx')) + glob.glob(os.path.join(cartella, 'rose*.csv'))
    if not file:
        raise FileNotFoundError(f'nessun file delle rose (…rosters….xlsx o rose*.csv) in {cartella}')
    return max(file, key=os.path.getmtime)


def leggi_rosters(percorso):
    """Blocchi del file dell'app: [(nome della squadra, [(giocatore, costo), …]), …]."""
    import openpyxl                       # serve solo qui, e solo sul PC
    libro = openpyxl.load_workbook(percorso, read_only=True, data_only=True)
    try:
        righe = [list(r) for r in libro.worksheets[0].iter_rows(values_only=True)]
    finally:
        libro.close()                     # in sola lettura il file resta aperto, e Windows lo blocca
    testa, blocchi = righe[0], []
    for c in range(len(testa) - 1):
        if testa[c] and str(testa[c + 1] or '').strip().lower() == 'costo':
            giocatori = []
            for r in righe[1:]:
                nome = r[c] if c < len(r) else None
                if not nome or str(nome).strip().lower() == 'totale':
                    break
                giocatori.append((str(nome).strip(), int(r[c + 1] or 0)))
            blocchi.append((str(testa[c]).strip(), giocatori))
    if not blocchi:
        raise ValueError('nessun blocco «squadra / costo»: il file ha cambiato struttura')
    return blocchi


def righe_da_blocchi(blocchi, base, listone):
    """Righe come quelle di rose.csv, dai blocchi dell'app.

    Le squadre si riconoscono dai giocatori (almeno 13 su 25 in comune con una
    rosa attuale), perché nell'app i nomi possono essere diversi da quelli del
    calendario. I giocatori si riconoscono dal nome: prima nella rosa attuale
    della squadra, poi nel listone, dove ogni nome compare una volta sola.
    Restituisce le righe e le coppie (nome nel file, nome nel calendario) diverse.
    """
    attuali = {}
    for p in base['p']:
        attuali.setdefault(p[4], {})[norm(p[1])] = p
    per_nome = {}
    for x in listone:
        per_nome.setdefault(norm(x['nome']), []).append(x)

    righe, errori, diversi, usate = [], [], [], set()
    for nome_file, giocatori in blocchi:
        if len(giocatori) != 25:
            errori.append(f'«{nome_file}»: {len(giocatori)} giocatori invece di 25')
            continue
        chiavi = {norm(n) for n, _ in giocatori}
        comuni, squadra = max(((len(chiavi & set(r)), s) for s, r in attuali.items()), default=(0, None))
        if comuni < 13:
            squadra = next((s for s in attuali if norm(s) == norm(nome_file)), None)
        if not squadra or squadra in usate:
            errori.append(f'squadra «{nome_file}» non riconosciuta')
            continue
        usate.add(squadra)
        if squadra != nome_file:
            diversi.append((nome_file, squadra))
        for k, (nome, costo) in enumerate(giocatori):
            ruolo, noto = RUOLI_IN_ORDINE[k], attuali[squadra].get(norm(nome))
            if noto:
                i = noto[0]
                if noto[3] != ruolo:
                    errori.append(f'{nome} ({nome_file}): nel file è tra i {ruolo}, nel listone è {noto[3]}')
            else:
                cand = per_nome.get(norm(nome), [])
                if len(cand) != 1:
                    errori.append(f'{nome} ({nome_file}): ' + ('non è nel listone' if not cand else 'più giocatori con questo nome'))
                    continue
                i = cand[0]['id']
            righe.append({'Squadra': squadra, 'Nome': nome, 'Squadra_Appartenenza': '', 'Ruolo': ruolo,
                          'Prezzo': str(costo), 'Quotazione': '', 'Fantacalcio_Id': str(i)})
    if errori:
        raise ValueError('\n'.join(errori))
    return righe, diversi


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
        quot = (int(r['Quotazione']) if r.get('Quotazione', '').strip().isdigit()
                else s[3] if s else vecchio[6] if vecchio else 0)
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

    # ordine come nel file di prima (squadra, ruolo, posizione): differenze leggibili
    pos = {p[0]: k for k, p in enumerate(base['p'])}
    ordine_sq = {}
    for p in base['p']:
        ordine_sq.setdefault(p[4], len(ordine_sq))
    rose.sort(key=lambda p: (ordine_sq.get(p[4], 99), 'PDCA'.index(p[3]), pos.get(p[0], 10 ** 6)))

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


def rinomina(base, coppie):
    """Un base.json nuovo con i nomi di squadra del file dell'app, nel calendario e
    nelle rose. coppie: [(nome nel file, nome attuale)]. Il base.json dato non cambia."""
    mappa = {attuale: nuovo for nuovo, attuale in coppie}
    nuovo = dict(base)
    nuovo['g'] = [g[:3] + [[[mappa.get(a, a), mappa.get(b, b)] for a, b in g[3]]] + g[4:] for g in base['g']]
    nuovo['p'] = [p[:4] + [mappa.get(p[4], p[4])] + p[5:] for p in base['p']]
    nuovo['me'] = mappa.get(base['me'], base['me'])
    return nuovo


def archivia(percorso):
    """Sposta il file usato dalla cartella Download all'archivio. Solo i file che
    stanno in Download; se il nome c'è già, aggiunge un numero. Non cancella niente."""
    if os.path.dirname(os.path.abspath(percorso)) != os.path.abspath(DOWNLOAD):
        return None
    os.makedirs(ARCHIVIO, exist_ok=True)
    nome, est = os.path.splitext(os.path.basename(percorso))
    destinazione, k = os.path.join(ARCHIVIO, nome + est), 1
    while os.path.exists(destinazione):
        destinazione, k = os.path.join(ARCHIVIO, f'{nome}-{k}{est}'), k + 1
    shutil.move(percorso, destinazione)
    return destinazione


def main():
    argomenti = [a for a in sys.argv[1:] if not a.startswith('--')]
    prova = '--prova' in sys.argv
    percorso = argomenti[0] if argomenti else trova_file(DOWNLOAD)
    print(f'file: {percorso}')
    base, listone = leggi_json('base.json'), leggi_json('listone.json')
    try:
        stat = leggi_json('statistiche.json').get('giocatori')
    except (OSError, ValueError):
        stat = None
    try:
        if percorso.lower().endswith('.xlsx'):
            righe, diversi = righe_da_blocchi(leggi_rosters(percorso), base, listone)
            for dal_file, nel_calendario in diversi:
                print(f'  nel file «{dal_file}» è «{nel_calendario}» del calendario')
            if diversi and '--nomi-app' in sys.argv:
                base = rinomina(base, diversi)
                mappa = {attuale: nuovo for nuovo, attuale in diversi}
                for r in righe:
                    r['Squadra'] = mappa.get(r['Squadra'], r['Squadra'])
                print(f'  adotto i nomi dell\'app per {len(diversi)} squadre')
        else:
            righe = leggi_csv(percorso)
        nuovo, nuovo_listone, aggiunti = importa(righe, base, listone, stat)
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
    if prova:
        print('prova: nessun file scritto.')
        return

    with open(os.path.join(DATI, 'base.json'), 'w', encoding='utf-8') as f:
        f.write(testo_json(nuovo))
    if aggiunti:
        with open(os.path.join(DATI, 'listone.json'), 'w', encoding='utf-8') as f:
            f.write(testo_json(nuovo_listone))
    print(f'rose aggiornate: {len(nuovo["p"])} giocatori, 10 squadre.')
    spostato = archivia(percorso)
    if spostato:
        print(f'file spostato nell\'archivio: {spostato}')


if __name__ == '__main__':
    main()
