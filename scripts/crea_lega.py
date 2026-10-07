#!/usr/bin/env python3
"""
Crea i dati di una lega nuova (multi-lega, 07/10/2026): dati/<cartella>/base.json con
rose e calendario, dal file delle rose di Leghe (xlsx) e dal calendario letto dalla
pagina della lega (archivio/<cartella>/calendario.json, fuori da Git).

Uso: python scripts/crea_lega.py <id> [--prova]
  <id> è quello di dati/leghe.json (es. «qi»). Cerca in archivio/<cartella>/ il file
  rosters*.xlsx più recente, l'eventuale rose-asta.csv (Id del listone, per i nomi
  ambigui) e calendario.json. Con --prova non scrive niente.

Controlli come importa_rose.py: squadre del calendario, 25 giocatori per squadra con i
ruoli della lega, nessun doppione, la tua squadra presente. Al primo problema si ferma.
"""
import csv, glob, json, os, sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importa_rose as ir

RADICE = ir.RADICE
DATI = ir.DATI


def lega(id_):
    with open(os.path.join(DATI, 'leghe.json'), encoding='utf-8') as f:
        for l in json.load(f)['leghe']:
            if l['id'] == id_:
                return l
    raise SystemExit(f'lega «{id_}» non presente in dati/leghe.json')


def data_giornata(date_bf, orari, serie_a):
    """Data della giornata di Serie A: quella già usata nel calendario dell'altra lega
    (le giornate di Serie A sono le stesse); se manca, la domenica degli orari."""
    if serie_a in date_bf:
        return date_bf[serie_a]
    o = orari.get(str(serie_a))
    if not o or 'inizio' not in o:
        return None
    a, b = date.fromisoformat(o['inizio'][:10]), date.fromisoformat(o['fine'][:10])
    g = a
    while g <= b:
        if g.weekday() == 6:
            return g.isoformat()
        g += timedelta(days=1)
    return a.isoformat()


def id_da_csv(percorso):
    """(squadra, nome normalizzato) → Id, dal file delle rose dell'asta."""
    if not os.path.exists(percorso):
        return {}
    return {(ir.norm(r['Squadra']), ir.norm(r['Nome'])): r['Fantacalcio_Id'] for r in ir.leggi_csv(percorso)}


def main():
    argomenti = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not argomenti:
        raise SystemExit(__doc__)
    cfg = lega(argomenti[0])
    cartella = cfg['cartella'].strip('/')
    arch = os.path.join(RADICE, 'archivio', cartella)
    xlsx = max(glob.glob(os.path.join(arch, 'rosters*.xlsx')), key=os.path.getmtime)
    cal = json.load(open(os.path.join(arch, 'calendario.json'), encoding='utf-8'))
    listone = ir.leggi_json('listone.json')
    stat = ir.leggi_json('statistiche.json').get('giocatori')
    orari = ir.leggi_json('orari.json')['giornate']
    ids = id_da_csv(os.path.join(arch, 'rose-asta.csv'))

    base_bf = ir.leggi_json('base.json')
    date_bf = {g[1]: g[2] for g in base_bf['g']}
    seed = {'v': date.today().isoformat(), 'me': cfg['squadra'],
            'g': [[l, s, data_giornata(date_bf, orari, s)] + [p] for l, s, p in cal['giornate']],
            'f': base_bf['f'], 'p': []}

    per_nome = {}
    for x in listone:
        per_nome.setdefault(ir.norm(x['nome']), []).append(x)
    righe, errori = [], []
    for squadra, giocatori in ir.leggi_rosters(xlsx):
        if len(giocatori) != sum(cfg['rosa'].values()):
            errori.append(f'«{squadra}»: {len(giocatori)} giocatori invece di {sum(cfg["rosa"].values())}')
            continue
        for k, (nome, costo) in enumerate(giocatori):
            ruolo = ir.RUOLI_IN_ORDINE[k]
            i = ids.get((ir.norm(squadra), ir.norm(nome)))
            if i is None:
                cand = per_nome.get(ir.norm(nome), [])
                if len(cand) != 1:
                    errori.append(f'{nome} ({squadra}): ' + ('non è nel listone' if not cand else 'più giocatori con questo nome'))
                    continue
                i = cand[0]['id']
            righe.append({'Squadra': squadra, 'Nome': nome, 'Squadra_Appartenenza': '', 'Ruolo': ruolo,
                          'Prezzo': str(costo), 'Quotazione': '', 'Fantacalcio_Id': str(i)})
    if errori:
        raise SystemExit('Rose NON create:\n' + '\n'.join(errori))
    try:
        base, _, aggiunti = ir.importa(righe, seed, listone, stat)
    except ValueError as e:
        raise SystemExit('Rose NON create, il file non è plausibile:\n' + str(e))
    base['g'] = seed['g']
    print(f'{cfg["nome"]}: {len(base["p"])} giocatori, {len(set(p[4] for p in base["p"]))} squadre, '
          f'{len(base["g"])} giornate di calendario, nuovi nel listone: {len(aggiunti)}')
    if '--prova' in sys.argv:
        print('prova: nessun file scritto.')
        return
    os.makedirs(os.path.join(DATI, cartella), exist_ok=True)
    with open(os.path.join(DATI, cartella, 'base.json'), 'w', encoding='utf-8') as f:
        f.write(ir.testo_json(base))
    print(f'scritto dati/{cartella}/base.json')


if __name__ == '__main__':
    main()
