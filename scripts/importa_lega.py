#!/usr/bin/env python3
"""
Aggiorna la classifica della lega (dati/lega.json) dal file che Leghe Fantacalcio fa
scaricare dalla pagina Classifica, «Classifica_<lega>.xlsx». La lega è privata: il
file lo scarica l'utente, oppure Claude dal Chrome dell'utente già collegato
(routine «dati di lega» in CLAUDE.md), mai con la password.

Uso: python scripts/importa_lega.py [percorso] [--prova]
Senza percorso prende il file della classifica più recente nella cartella Download.
Con --prova mostra la classifica letta, senza scrivere niente.
Dopo l'importazione il file passa da Download a archivio/lega con la data nel nome
(fuori da Git), e con lui il calendario scaricato insieme: non si cancella niente.

dati/lega.json: {"aggiornato": "...", "colonne": [...], "classifica": [[posizione,
squadra, partite, vinte, pari, perse, gol fatti, gol subiti, differenza, punti,
fantapunti], ...]}

Controlli: intestazione come quella di Leghe, 10 squadre del calendario (i nomi
dell'app), posizioni da 1 a 10, vinte + pari + perse = partite, gol fatti - gol
subiti = differenza. Al primo problema si ferma e non scrive niente.
"""
import glob, json, os, shutil, sys
from datetime import date, datetime, timezone

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(RADICE, 'dati')
DOWNLOAD = os.path.join(os.path.expanduser('~'), 'Downloads')
ARCHIVIO = os.path.join(RADICE, 'archivio', 'lega')      # file già importati, esclusi da Git
TESTA = ['Pos', 'Squadra', '', 'G', 'V', 'N', 'P', 'Gf', 'Gs', 'Dr', 'Pt.', 'Pt. Totali']
COLONNE = ['posizione', 'squadra', 'partite', 'vinte', 'pari', 'perse',
           'gol_fatti', 'gol_subiti', 'differenza', 'punti', 'fantapunti']


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
    if prova:
        print('prova: nessun file scritto.')
        return
    dati = {'aggiornato': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'colonne': COLONNE, 'classifica': righe}
    with open(os.path.join(DATI, 'lega.json'), 'w', encoding='utf-8') as f:
        f.write(json.dumps(dati, ensure_ascii=False, separators=(',', ':')))
    print('classifica aggiornata.')
    # il calendario scaricato insieme resta in archivio: servirà per risultati e forma
    for f in [percorso] + glob.glob(os.path.join(DOWNLOAD, 'Calendario_*.xlsx')):
        spostato = archivia(f)
        if spostato:
            print(f'file spostato nell\'archivio: {spostato}')


if __name__ == '__main__':
    main()
