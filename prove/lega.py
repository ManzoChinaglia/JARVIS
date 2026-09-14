"""Prova di scripts/importa_lega.py con file finti fatti come quelli di Leghe.

Uso: python prove/lega.py
"""
import glob, importlib.util, json, os, sys, tempfile
from datetime import date

REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('importa_lega', os.path.join(REPO, 'scripts', 'importa_lega.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
import openpyxl

esiti = falliti = 0
def verifica(nome, cond, dettaglio=''):
    global esiti, falliti
    esiti += 1
    falliti += not cond
    print(('  ok   ' if cond else '  NO   ') + nome + (f'  ->  {dettaglio}' if dettaglio != '' else ''))

with open(os.path.join(REPO, 'dati', 'base.json'), encoding='utf-8') as f:
    base = json.load(f)
SQUADRE = sorted({s for g in base['g'] for sfida in g[3] for s in sfida})
TESTA = ['Pos', 'Squadra', None, 'G', 'V', 'N', 'P', 'Gf', 'Gs', 'Dr', 'Pt.', 'Pt. Totali']

def file_classifica(cartella, righe, testa=TESTA, nome='Classifica_Sborra-league.xlsx'):
    """Come il file vero: titolo, indirizzo della lega, riga vuota, intestazione, squadre."""
    libro = openpyxl.Workbook()
    ws = libro.active
    ws.title = 'Classifica'
    ws.append(['Classifica Sborra league'])
    ws.append(['https://leghe.fantacalcio.it/rivoluzione-fantacalcio'])
    ws.append([])
    ws.append(testa)
    for r in righe:
        ws.append(r)
    p = os.path.join(cartella, nome)
    libro.save(p)
    return p

def valide(nomi=SQUADRE):
    return [[k + 1, s, None, 2, 1, 1, 0, 3, 1, 2, 4, 150.5 - k] for k, s in enumerate(nomi)]

def leggi(cartella, righe, **k):
    return mod.classifica(mod.leggi_classifica(file_classifica(cartella, righe, **k)), base)

with tempfile.TemporaryDirectory() as d:
    print('\n1. File come quello di Leghe')
    righe, diversi = leggi(d, valide())
    verifica('10 squadre in ordine, con partite, punti e fantapunti', len(righe) == 10
             and righe[0] == [1, SQUADRE[0], 2, 1, 1, 0, 3, 1, 2, 4, 150.5] and not diversi, righe[0])
    verifica('numeri interi restano interi', all(isinstance(x, int) for x in righe[0][2:10]))
    zero = [[k + 1, s, None] + [0] * 9 for k, s in enumerate(SQUADRE)]
    righe, _ = leggi(d, zero)
    verifica('a inizio stagione, tutto a zero: va bene', len(righe) == 10 and all(r[2] == 0 for r in righe))
    sparsa = valide()
    sparsa.reverse()
    righe, _ = leggi(d, sparsa)
    verifica('righe in un altro ordine: si ordinano per posizione', [r[0] for r in righe] == list(range(1, 11)))

    print('\n2. Nomi')
    nomi = list(SQUADRE)
    nomi[3] = 'Nome Nuovo Di Una Squadra'
    righe, diversi = leggi(d, valide(nomi))
    verifica('un solo nome diverso: è l\'unica squadra mancante', diversi == [('Nome Nuovo Di Una Squadra', SQUADRE[3])]
             and righe[3][1] == SQUADRE[3], diversi)
    nomi[5] = 'Altro Nome'
    try:
        leggi(d, valide(nomi))
        verifica('due nomi sconosciuti: deve fermarsi', False)
    except ValueError as e:
        verifica('due nomi sconosciuti: si ferma', True, str(e).splitlines()[0])

    print('\n3. File non plausibili')
    for nome, righe_file, altro in [
            ('9 squadre', valide()[:9], {}),
            ('vinte + pari + perse diverso dalle partite', [r[:3] + [3] + r[4:] if k == 0 else r for k, r in enumerate(valide())], {}),
            ('differenza reti sbagliata', [r[:9] + [5] + r[10:] if k == 0 else r for k, r in enumerate(valide())], {}),
            ('posizioni ripetute', [[1] + r[1:] for r in valide()], {}),
            ('intestazione cambiata', valide(), {'testa': ['Pos', 'Team', None, 'G', 'V', 'N', 'P', 'Gf', 'Gs', 'Dr', 'Pt.', 'Pt. Totali']}),
            ('punti non numerici', [r[:10] + ['tanti'] + r[11:] if k == 0 else r for k, r in enumerate(valide())], {})]:
        try:
            leggi(d, righe_file, **altro)
            verifica(nome + ': deve fermarsi', False)
        except ValueError as e:
            verifica(nome + ': si ferma', True, str(e).splitlines()[0])

    print('\n4. Archivio')
    scaricati, archivio = os.path.join(d, 'Downloads'), os.path.join(d, 'archivio')
    os.makedirs(scaricati)
    mod.DOWNLOAD, mod.ARCHIVIO = scaricati, archivio
    p = file_classifica(scaricati, valide())
    a = mod.archivia(p, date(2026, 9, 22))
    verifica('dalla cartella Download all\'archivio, con la data nel nome', not os.path.exists(p)
             and os.path.basename(a) == 'Classifica_Sborra-league-2026-09-22.xlsx', a)
    p = file_classifica(scaricati, valide())
    a = mod.archivia(p, date(2026, 9, 22))
    verifica('stesso giorno: non sovrascrive', os.path.basename(a) == 'Classifica_Sborra-league-2026-09-22-1.xlsx', a)
    verifica('un file fuori da Download non si sposta', mod.archivia(file_classifica(d, valide())) is None)
    verifica('il più recente tra quelli scaricati', mod.trova_file(archivio).endswith('-1.xlsx'))

print('\n5. Il file vero scaricato da Leghe (solo sul PC, se è in archivio)')
veri = sorted(glob.glob(os.path.join(REPO, 'archivio', 'lega', 'Classifica_*.xlsx')))
if veri:
    righe, diversi = mod.classifica(mod.leggi_classifica(veri[-1]), base)
    verifica('letto: 10 squadre con i nomi di Jarvis', len(righe) == 10 and {r[1] for r in righe} == set(SQUADRE),
             os.path.basename(veri[-1]))
else:
    print('  --   nessun file vero in archivio: prova saltata')

print(f'\n{esiti - falliti}/{esiti} verifiche superate')
sys.exit(1 if falliti else 0)
