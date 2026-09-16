#!/usr/bin/env python3
"""
Aggiorna la classifica della lega (dati/lega.json) dal file che Leghe Fantacalcio fa
scaricare dalla pagina Classifica, «Classifica_<lega>.xlsx», e i risultati delle
giornate già giocate dal «Calendario_<lega>.xlsx» scaricato insieme. La lega è
privata: i file li scarica l'utente, oppure Claude dal Chrome dell'utente già
collegato (routine «dati di lega» in CLAUDE.md), mai con la password.

Uso: python scripts/importa_lega.py [percorso della classifica] [--prova]
Senza percorso prende il file della classifica più recente nella cartella Download,
e cerca il calendario più recente nella stessa cartella. Con --prova mostra quello
che leggerebbe, senza scrivere niente. Dopo l'importazione i due file passano da
Download a archivio/lega con la data nel nome (fuori da Git): non si cancella niente.

dati/lega.json: {"aggiornato": "...", "colonne": [...], "classifica": [[posizione,
squadra, partite, vinte, pari, perse, gol fatti, gol subiti, differenza, punti,
fantapunti], ...], "risultati": {"<giornata>": [[casa, fantapunti, fuori,
fantapunti, gol casa, gol fuori], ...]}}. "risultati" ha solo le giornate già
giocate; le altre non ci sono ancora, e un calendario non leggibile lascia quelle
già salvate come sono (un aggiornamento non deve mai svuotare i dati).

Controlli della classifica: intestazione come quella di Leghe, 10 squadre del
calendario (i nomi dell'app), posizioni da 1 a 10, vinte + pari + perse = partite,
gol fatti - gol subiti = differenza. Del calendario: 34 giornate, le stesse
partite di dati/base.json (il calendario è fissato a inizio stagione). Al primo
problema ciascuno si ferma e non scrive niente di suo: la classifica letta bene si
salva anche se il calendario è illeggibile, e viceversa.

Il formato del «risultato» di ogni partita (i gol, oltre ai due fantapunti) non è
mai stato visto su una giornata vera al momento di scrivere questo script: si
accetta solo "N-N", altrimenti l'import del calendario si ferma con un messaggio
chiaro invece di indovinare. Verificare sulla prima giornata vera (dal 20/09/2026).
"""
import glob, json, os, re, shutil, sys
from datetime import date, datetime, timezone

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(RADICE, 'dati')
DOWNLOAD = os.path.join(os.path.expanduser('~'), 'Downloads')
ARCHIVIO = os.path.join(RADICE, 'archivio', 'lega')      # file già importati, esclusi da Git
TESTA = ['Pos', 'Squadra', '', 'G', 'V', 'N', 'P', 'Gf', 'Gs', 'Dr', 'Pt.', 'Pt. Totali']
COLONNE = ['posizione', 'squadra', 'partite', 'vinte', 'pari', 'perse',
           'gol_fatti', 'gol_subiti', 'differenza', 'punti', 'fantapunti']
RE_GIORNATA = re.compile(r'^(\d+)ª Giornata lega$')
RE_RISULTATO = re.compile(r'^(\d+)\s*-\s*(\d+)$')


def trova_file(cartella, schema='Classifica_*.xlsx'):
    """Il file più recente della cartella con quel nome."""
    file = glob.glob(os.path.join(cartella, schema))
    if not file:
        raise FileNotFoundError(f'nessun file {schema} in {cartella}')
    return max(file, key=os.path.getmtime)


def leggi_classifica(percorso):
    """Le righe della tabella: dopo l'intestazione, fino alla prima riga vuota."""
    import openpyxl                       # serve solo qui, e solo sul PC
    libro = openpyxl.load_workbook(percorso, read_only=True, data_only=True)
    try:
        righe = [['' if c is None else c for c in r] for r in libro.worksheets[0].iter_rows(values_only=True)]
    finally:
        libro.close()                     # in sola lettura il file resta aperto, e Windows lo blocca
    for k, r in enumerate(righe):
        if [str(c).strip() for c in r[:len(TESTA)]] == TESTA:
            break
    else:
        raise ValueError('intestazione della classifica non trovata: il file ha cambiato struttura')
    tabella = []
    for r in righe[k + 1:]:
        if not r or str(r[0]).strip() == '':
            break
        tabella.append(r)
    return tabella


def numero(x):
    """Intero se lo è (punti, partite), altrimenti decimale (fantapunti)."""
    if isinstance(x, bool) or str(x).strip() == '':
        raise ValueError(f'valore mancante: {x!r}')
    v = float(x) if isinstance(x, (int, float)) else float(str(x).replace(',', '.'))
    return int(v) if v.is_integer() else round(v, 2)


def classifica(tabella, base):
    """Le righe per dati/lega.json e le coppie (nome nel file, nome in Jarvis) diverse.
    Un solo nome sconosciuto si abbina all'unica squadra mancante; di più, no."""
    squadre = {s for g in base['g'] for sfida in g[3] for s in sfida}
    errori, righe = [], []
    for r in tabella:
        try:
            righe.append([numero(r[0]), str(r[1]).strip()] + [numero(c) for c in r[3:12]])
        except (ValueError, IndexError) as e:
            errori.append(f'riga {r[:2]}: {e}')
    if len(righe) != 10:
        errori.append(f'{len(righe)} squadre invece di 10')
    nomi = [r[1] for r in righe]
    ignoti, mancanti = [n for n in nomi if n not in squadre], sorted(squadre - set(nomi))
    diversi = []
    if len(ignoti) == 1 and len(mancanti) == 1:
        diversi = [(ignoti[0], mancanti[0])]
        for r in righe:
            if r[1] == ignoti[0]:
                r[1] = mancanti[0]
    elif ignoti:
        errori.append('squadre non riconosciute: ' + ', '.join(ignoti))
    if sorted(r[0] for r in righe) != list(range(1, len(righe) + 1)):
        errori.append('posizioni non da 1 a 10')
    for r in righe:
        s, g, v, n, p, gf, gs, dr = r[1:9]
        if v + n + p != g:
            errori.append(f'{s}: {v} vinte + {n} pari + {p} perse invece di {g} partite')
        if abs(gf - gs - dr) > 1e-9:
            errori.append(f'{s}: gol {gf}-{gs} con differenza {dr}')
    if errori:
        raise ValueError('\n'.join(errori))
    return sorted(righe, key=lambda r: r[0]), diversi


def leggi_calendario(percorso):
    """Le partite di ogni giornata di lega dal file «Calendario»: due colonne di
    blocchi affiancati (giornate dispari a sinistra, pari a destra), ciascuno con
    un'intestazione «Nª Giornata lega» seguita da 5 righe [casa, fantapunti casa,
    fantapunti fuori, fuori, risultato]. Restituisce {giornata: [(casa, fp_casa,
    fp_fuori, fuori, risultato), ...]}, risultato = '-' se non ancora giocata."""
    import openpyxl                       # serve solo qui, e solo sul PC
    libro = openpyxl.load_workbook(percorso, read_only=True, data_only=True)
    try:
        righe = [list(r) for r in libro.worksheets[0].iter_rows(values_only=True)]
    finally:
        libro.close()                     # in sola lettura il file resta aperto, e Windows lo blocca
    giornate = {}
    for i, r in enumerate(righe):
        for col in (0, 6):
            cella = r[col] if col < len(r) else None
            m = RE_GIORNATA.match(str(cella).strip()) if cella is not None else None
            if not m:
                continue
            gio = int(m.group(1))
            if gio in giornate:
                raise ValueError(f'giornata {gio}: intestazione ripetuta')
            partite = []
            for rr in righe[i + 1:i + 6]:
                if col + 4 >= len(rr) or rr[col] is None or rr[col + 3] is None:
                    raise ValueError(f'giornata {gio}: meno di 5 partite, il file ha cambiato struttura')
                casa, pc, pf, fuori, ris = (rr[col + k] for k in range(5))
                partite.append((str(casa).strip(), pc, pf, str(fuori).strip(),
                                 '-' if ris is None or str(ris).strip() == '' else str(ris).strip()))
            giornate[gio] = partite
    if sorted(giornate) != list(range(1, 35)):
        raise ValueError(f'{len(giornate)} giornate lette invece di 34: il file ha cambiato struttura')
    return giornate


def mappa_nomi_calendario(giornate, base):
    """Il calendario può usare nomi diversi da quelli dell'app per più di una squadra
    insieme (come le rose, non come la classifica: lì al massimo una). Si ricava dalla
    posizione: stessa giornata, stesso lato (casa/fuori), stesso avversario. Un nome
    già noto trovato dove non ce lo si aspetta è un errore vero, non una ridenominazione.
    Restituisce ({nome nel file: nome in Jarvis}, errori)."""
    squadre_base = {s for g in base['g'] for sfida in g[3] for s in sfida}
    attese = {g[0]: g[3] for g in base['g']}
    mappa, errori = {}, []
    for gio, partite in sorted(giornate.items()):
        b = attese.get(gio)
        if b is None or len(partite) != len(b):
            errori.append(f'giornata {gio}: {len(partite)} partite, {len(b) if b else 0} attese')
            continue
        for (casa, _, _, fuori, _), (bcasa, bfuori) in zip(partite, b):
            for grezzo, atteso in ((casa, bcasa), (fuori, bfuori)):
                if grezzo == atteso:
                    continue
                if grezzo in squadre_base:
                    errori.append(f'giornata {gio}: «{grezzo}» è una squadra nota, ma qui '
                                   f'ci si aspettava «{atteso}»: calendario cambiato?')
                elif grezzo in mappa and mappa[grezzo] != atteso:
                    errori.append(f'giornata {gio}: «{grezzo}» corrisponde sia a «{mappa[grezzo]}» che a «{atteso}»')
                else:
                    mappa[grezzo] = atteso
    return mappa, errori


def risultati_da_calendario(giornate, base):
    """Da {giornata: [(casa, fp_casa, fp_fuori, fuori, risultato), ...]} (leggi_calendario)
    alle sole giornate già giocate, nel formato di dati/lega.json → risultati, e le
    coppie (nome nel file, nome in Jarvis) diverse. Le coppie casa/fuori, con i nomi
    dell'app, si confrontano con dati/base.json (fissato a inizio stagione): se non
    coincidono il calendario è cambiato e ci si ferma, invece di salvare partite
    sbagliate."""
    mappa, errori = mappa_nomi_calendario(giornate, base)
    if errori:
        raise ValueError('\n'.join(errori))
    attese = {g[0]: [tuple(s) for s in g[3]] for g in base['g']}
    risultati = {}
    for gio, partite in sorted(giornate.items()):
        partite = [(mappa.get(c, c), pc, pf, mappa.get(f, f), r) for c, pc, pf, f, r in partite]
        if [(c, f) for c, _, _, f, _ in partite] != attese[gio]:
            errori.append(f'giornata {gio}: le partite non coincidono con base.json (calendario cambiato?)')
            continue
        giocate = [p for p in partite if p[4] != '-']
        if not giocate:
            continue
        if len(giocate) != 5:
            errori.append(f'giornata {gio}: {len(giocate)}/5 partite con un risultato, non tutte')
            continue
        righe = []
        for casa, pc, pf, fuori, ris in giocate:
            try:
                fp_casa, fp_fuori = numero(pc), numero(pf)
            except ValueError as e:
                errori.append(f'giornata {gio}, {casa}-{fuori}: fantapunti non validi ({e})')
                continue
            m = RE_RISULTATO.match(ris)
            if not m:
                errori.append(f'giornata {gio}, {casa}-{fuori}: risultato «{ris}» non riconosciuto '
                               '(formato mai visto su una giornata vera: da controllare a mano)')
                continue
            righe.append([casa, fp_casa, fuori, fp_fuori, int(m.group(1)), int(m.group(2))])
        if len(righe) == 5:
            risultati[str(gio)] = righe
    if errori:
        raise ValueError('\n'.join(errori))
    return risultati, sorted(mappa.items())


def archivia(percorso, oggi=None):
    """Sposta il file dalla cartella Download all'archivio, con la data nel nome.
    Solo i file che stanno in Download; se il nome c'è già aggiunge un numero."""
    if os.path.dirname(os.path.abspath(percorso)) != os.path.abspath(DOWNLOAD):
        return None
    os.makedirs(ARCHIVIO, exist_ok=True)
    nome, est = os.path.splitext(os.path.basename(percorso))
    nome = f'{nome}-{(oggi or date.today()).isoformat()}'
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
    with open(os.path.join(DATI, 'base.json'), encoding='utf-8') as f:
        base = json.load(f)
    try:
        righe, diversi = classifica(leggi_classifica(percorso), base)
    except ValueError as e:
        print('Classifica NON aggiornata, il file non è plausibile:\n' + str(e))
        sys.exit(1)
    for dal_file, in_jarvis in diversi:
        print(f'  nel file «{dal_file}» è «{in_jarvis}»')
    for r in righe:
        print(f'  {r[0]:>2}. {r[1]:<20} {r[2]} partite, {r[9]} punti, {r[10]} fantapunti')

    # il calendario, scaricato insieme alla classifica, nella stessa cartella: le
    # giornate già giocate diventano dati/lega.json → risultati. Un problema qui
    # non blocca la classifica.
    trovati = glob.glob(os.path.join(os.path.dirname(os.path.abspath(percorso)), 'Calendario_*.xlsx'))
    calendario = max(trovati, key=os.path.getmtime) if trovati else None
    risultati_nuovi = {}
    if not calendario:
        print('nessun file Calendario_*.xlsx accanto alla classifica: risultati non aggiornati.')
    else:
        print(f'calendario: {calendario}')
        try:
            risultati_nuovi, diversi_cal = risultati_da_calendario(leggi_calendario(calendario), base)
            for dal_file, in_jarvis in diversi_cal:
                print(f'  nel calendario «{dal_file}» è «{in_jarvis}»')
            if risultati_nuovi:
                print(f'  {len(risultati_nuovi)} giornate giocate lette.')
            else:
                print('  nessuna giornata ancora giocata nel calendario.')
        except ValueError as e:
            print('Risultati NON aggiornati, il calendario non è plausibile:\n' + str(e))

    if prova:
        print('prova: nessun file scritto.')
        return

    percorso_lega = os.path.join(DATI, 'lega.json')
    risultati = {}
    if os.path.exists(percorso_lega):
        try:
            with open(percorso_lega, encoding='utf-8') as f:
                risultati = json.load(f).get('risultati', {})
        except (json.JSONDecodeError, OSError):
            pass                          # lega.json non ancora valido: si riparte da vuoto
    risultati.update(risultati_nuovi)     # upsert: le giornate vecchie non lette di nuovo restano

    dati = {'aggiornato': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'colonne': COLONNE, 'classifica': righe, 'risultati': risultati}
    with open(percorso_lega, 'w', encoding='utf-8') as f:
        f.write(json.dumps(dati, ensure_ascii=False, separators=(',', ':')))
    print('classifica aggiornata.')
    # i file scaricati passano nell'archivio, letti bene o no: non si cancella niente
    for f in [percorso] + ([calendario] if calendario else []):
        spostato = archivia(f)
        if spostato:
            print(f'file spostato nell\'archivio: {spostato}')


if __name__ == '__main__':
    main()
