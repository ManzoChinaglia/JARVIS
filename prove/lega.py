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

def file_calendario(cartella, nomi_giornata, nome='Calendario_Sborra-league.xlsx'):
    """Come il file vero: titolo, indirizzo, riga vuota, poi coppie di blocchi
    affiancati (dispari a sinistra, pari a destra), 5 partite per blocco.
    nomi_giornata: {giornata: [(casa, fp_casa, fp_fuori, fuori, risultato), ...]}."""
    libro = openpyxl.Workbook()
    ws = libro.active
    ws.title = 'Calendario'
    ws.append(['Calendario Sborra league'])
    ws.append(['https://leghe.fantacalcio.it/rivoluzione-fantacalcio'])
    ws.append([])
    for dispari in range(1, 34, 2):
        pari = dispari + 1
        ws.append([f'{dispari}ª Giornata lega', None, f'{4+dispari}ª Giornata serie a', None, None,
                   None, f'{pari}ª Giornata lega', None, f'{4+pari}ª Giornata serie a', None, None])
        for (c1, pc1, pf1, f1, r1), (c2, pc2, pf2, f2, r2) in zip(nomi_giornata[dispari], nomi_giornata[pari]):
            ws.append([c1, pc1, pf1, f1, r1, None, c2, pc2, pf2, f2, r2])
    p = os.path.join(cartella, nome)
    libro.save(p)
    return p

def partite_da_base(risultato_per_giornata=None):
    """Le partite di ogni giornata come le scrive Leghe, dai vincoli di base.json:
    non giocate ('-') salvo quelle indicate in risultato_per_giornata,
    {giornata: {(casa, fuori): (fp_casa, fp_fuori, gol_casa, gol_fuori)}}."""
    risultato_per_giornata = risultato_per_giornata or {}
    nomi_giornata = {}
    for g in base['g']:
        gio, sfide = g[0], g[3]
        noti = risultato_per_giornata.get(gio, {})
        righe = []
        for casa, fuori in sfide:
            if (casa, fuori) in noti:
                pc, pf, gc, gf = noti[(casa, fuori)]
                righe.append((casa, pc, pf, fuori, f'{gc}-{gf}'))
            else:
                righe.append((casa, 0, 0, fuori, '-'))
        nomi_giornata[gio] = righe
    return nomi_giornata

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

print('\n5. Calendario e risultati')
with tempfile.TemporaryDirectory() as d:
    G1 = {('FC FRINGUELLI', 'AS Quell'): (65.5, 58, 2, 1),
          ('Dinastia Fontana', 'Palle Sudate'): (70, 70, 1, 1),
          ('Ostia Liedholm', 'saddam hussein'): (55.5, 60.5, 0, 2),
          ('GOD BLESS THE DOC', 'BURKINA FASO'): (62, 75.5, 1, 3),
          ('OPENDA LEGS', 'Dua Lipsia'): (58, 58, 0, 0)}

    def rinomina(nomi_giornata, mappa):
        return {g: [(mappa.get(c, c), pc, pf, mappa.get(f, f), r) for c, pc, pf, f, r in righe]
                for g, righe in nomi_giornata.items()}

    print('\n5.1 File come quello vero (a inizio stagione, tutto a "-")')
    nomi_giornata = partite_da_base()
    p = file_calendario(d, nomi_giornata)
    giornate = mod.leggi_calendario(p)
    verifica('34 giornate lette', sorted(giornate) == list(range(1, 35)), len(giornate))
    risultati, diversi = mod.risultati_da_calendario(giornate, base)
    verifica('nessuna giornata giocata: nessun risultato', risultati == {} and diversi == [])

    print('\n5.2 Una giornata giocata')
    nomi_giornata = partite_da_base({1: G1})
    giornate = mod.leggi_calendario(file_calendario(d, nomi_giornata))
    risultati, diversi = mod.risultati_da_calendario(giornate, base)
    attesa = [[c, pc, f, pf, gc, gf] for (c, f), (pc, pf, gc, gf) in G1.items()]
    verifica('giornata 1 letta con fantapunti e gol', risultati.get('1') == attesa, risultati.get('1'))
    verifica('le altre 33 restano senza risultato', len(risultati) == 1, sorted(risultati))
    verifica('nessun nome diverso, nessuna ridenominazione', diversi == [])

    print('\n5.3 Più squadre con un nome diverso da quello dell\'app, insieme (non solo una, come la classifica)')
    mappa_vera = {'Palle Sudate': 'Squadra Vera Uno', 'AS Quell': 'Nome Vero Due', 'Dua Lipsia': 'Nome Vero Tre'}
    nomi_giornata = rinomina(partite_da_base({1: G1}), mappa_vera)
    giornate = mod.leggi_calendario(file_calendario(d, nomi_giornata))
    risultati, diversi = mod.risultati_da_calendario(giornate, base)
    verifica('le tre ridenominazioni si ricavano dalla posizione', dict(diversi) == {v: k for k, v in mappa_vera.items()}, diversi)
    verifica('i risultati usano i nomi dell\'app, non quelli del file',
             {r[0] for r in risultati['1']} | {r[2] for r in risultati['1']} <= set(SQUADRE), risultati['1'])

    print('\n5.4 File non plausibili: si fermano, senza salvare niente')
    # risultato non "N-N" (formato mai visto su una giornata vera)
    rotto = partite_da_base({1: G1})
    rotto[1][0] = (rotto[1][0][0], rotto[1][0][1], rotto[1][0][2], rotto[1][0][3], 'V')
    for nome, ng in [('risultato non "N-N"', rotto)]:
        giornate = mod.leggi_calendario(file_calendario(d, ng))
        try:
            mod.risultati_da_calendario(giornate, base)
            verifica(nome + ': deve fermarsi', False)
        except ValueError as e:
            verifica(nome + ': si ferma', True, str(e).splitlines()[0])

    # solo alcune partite della giornata hanno un risultato: non tutte
    parziale = partite_da_base({1: G1})
    c, pc, pf, f, r = parziale[1][0]
    parziale[1][0] = (c, 0, 0, f, '-')
    giornate = mod.leggi_calendario(file_calendario(d, parziale))
    try:
        mod.risultati_da_calendario(giornate, base)
        verifica('giornata a metà giocata: deve fermarsi', False)
    except ValueError as e:
        verifica('giornata a metà giocata: si ferma', True, str(e).splitlines()[0])

    # una squadra nota comparsa dove non ci si aspettava: non è una ridenominazione, è un errore vero
    sbagliato = partite_da_base()
    sbagliato[2][0] = ('BURKINA FASO',) + sbagliato[2][0][1:]
    giornate = mod.leggi_calendario(file_calendario(d, sbagliato))
    try:
        mod.risultati_da_calendario(giornate, base)
        verifica('squadra nota nel posto sbagliato: deve fermarsi', False)
    except ValueError as e:
        verifica('squadra nota nel posto sbagliato: si ferma', True, str(e).splitlines()[0])

    print('\n5.5 main(): la classifica si salva anche se il calendario non è plausibile')
    scaricati, archivio2, dati2 = os.path.join(d, 'Downloads2'), os.path.join(d, 'archivio2'), os.path.join(d, 'dati2')
    os.makedirs(scaricati); os.makedirs(dati2)
    with open(os.path.join(dati2, 'base.json'), 'w', encoding='utf-8') as f:
        json.dump(base, f)
    mod.DOWNLOAD, mod.ARCHIVIO, mod.DATI = scaricati, archivio2, dati2
    file_classifica(scaricati, valide())
    file_calendario(scaricati, rotto)      # stesso "risultato non riconosciuto" di sopra
    vecchi_argv, sys.argv = sys.argv, ['importa_lega.py']
    try:
        mod.main()
    finally:
        sys.argv = vecchi_argv
    with open(os.path.join(dati2, 'lega.json'), encoding='utf-8') as f:
        lega = json.load(f)
    verifica('classifica scritta comunque', len(lega['classifica']) == 10)
    verifica('risultati assenti (il calendario non è stato letto)', lega.get('risultati', {}) == {})

    print('\n5.6 main(): un secondo giro aggiunge risultati, senza perdere quelli di prima')
    # prima un giro con la giornata 1 giocata, poi un secondo calendario con solo la 2: la 1 deve restare
    file_classifica(scaricati, valide())
    file_calendario(scaricati, partite_da_base({1: G1}))
    sys.argv = ['importa_lega.py']
    try:
        mod.main()
    finally:
        sys.argv = vecchi_argv
    G2 = {k: (v[0] - 1, v[1] + 1, v[2], v[3]) for k, v in
          {('Palle Sudate', 'FC FRINGUELLI'): (60, 60, 1, 1), ('BURKINA FASO', 'OPENDA LEGS'): (80, 40, 2, 0),
           ('saddam hussein', 'GOD BLESS THE DOC'): (50, 65, 0, 1), ('AS Quell', 'Ostia Liedholm'): (55, 55, 1, 1),
           ('Dua Lipsia', 'Dinastia Fontana'): (48, 72, 0, 2)}.items()}
    file_classifica(scaricati, valide())
    file_calendario(scaricati, partite_da_base({2: G2}))
    sys.argv = ['importa_lega.py']
    try:
        mod.main()
    finally:
        sys.argv = vecchi_argv
    with open(os.path.join(dati2, 'lega.json'), encoding='utf-8') as f:
        lega = json.load(f)
    verifica('giornata 1 (del giro precedente) ancora presente', '1' in lega.get('risultati', {}))
    verifica('giornata 2 (di questo giro) aggiunta', '2' in lega.get('risultati', {}))
    verifica('nessuna terza giornata inventata', sorted(lega.get('risultati', {})) == ['1', '2'])

print('\n6. I file veri scaricati da Leghe (solo sul PC, se sono in archivio)')
veri = sorted(glob.glob(os.path.join(REPO, 'archivio', 'lega', 'Classifica_*.xlsx')))
if veri:
    righe, diversi = mod.classifica(mod.leggi_classifica(veri[-1]), base)
    verifica('classifica letta: 10 squadre con i nomi di Jarvis', len(righe) == 10 and {r[1] for r in righe} == set(SQUADRE),
             os.path.basename(veri[-1]))
else:
    print('  --   nessuna classifica vera in archivio: prova saltata')
veri_cal = sorted(glob.glob(os.path.join(REPO, 'archivio', 'lega', 'Calendario_*.xlsx')))
if veri_cal:
    giornate = mod.leggi_calendario(veri_cal[-1])
    verifica('calendario letto: 34 giornate, 5 partite ciascuna', sorted(giornate) == list(range(1, 35))
             and all(len(p) == 5 for p in giornate.values()), os.path.basename(veri_cal[-1]))
    risultati, diversi = mod.risultati_da_calendario(giornate, base)
    verifica('le partite coincidono con base.json (a parte eventuali nomi diversi)', True)
    print(f'  {len(risultati)} giornate già giocate in questo file' + (f', nomi diversi: {diversi}' if diversi else '.'))
else:
    print('  --   nessun calendario vero in archivio: prova saltata')

print(f'\n{esiti - falliti}/{esiti} verifiche superate')
sys.exit(1 if falliti else 0)
