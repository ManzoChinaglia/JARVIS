"""Prova di scripts/importa_rose.py: un rose.csv ricostruito da base.json deve ridare
le stesse rose; file sbagliati devono fermarsi senza scrivere.

Uso: python prove/rose.py
"""
import copy, importlib.util, json, os, sys

REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('importa_rose', os.path.join(REPO, 'scripts', 'importa_rose.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
base = json.load(open(os.path.join(REPO, 'dati', 'base.json'), encoding='utf-8'))
listone = json.load(open(os.path.join(REPO, 'dati', 'listone.json'), encoding='utf-8'))

esiti = falliti = 0
def verifica(nome, cond, dettaglio=''):
    global esiti, falliti
    esiti += 1
    falliti += not cond
    print(('  ok   ' if cond else '  NO   ') + nome + (f'  ->  {dettaglio}' if dettaglio != '' else ''))

def riga(p):
    """Una riga di rose.csv ricostruita da una voce di base.json (sigla = prime 3 lettere del club)."""
    return {'Squadra': p[4], 'Nome': p[1], 'Squadra_Appartenenza': p[2][:3].upper(), 'Ruolo': p[3],
            'Ruoli_Mantra': '', 'Prezzo': str(p[5]), 'Quotazione': str(p[6]), 'Quotazione_Mantra': str(p[6]),
            'Fantacalcio_Id': str(p[0])}

def fallisce(righe, cosa):
    try:
        mod.importa(righe, base, listone)
        return False, 'nessun errore'
    except ValueError as e:
        return cosa in str(e), str(e).splitlines()[0]

print('\n1. Stesso file, stesse rose')
righe = [riga(p) for p in base['p']]
nuovo, nuovo_listone, aggiunti = mod.importa(righe, base, listone)
verifica('rose identiche a base.json', nuovo['p'] == base['p'])
verifica('calendario, sfide e squadra intatti', all(nuovo[k] == base[k] for k in ('me', 'g', 'f')) and list(nuovo) == list(base))
verifica('nessun giocatore nuovo nel listone', aggiunti == [] and nuovo_listone == listone)
testo = open(os.path.join(REPO, 'dati', 'base.json'), encoding='utf-8').read()
verifica('stesso formato del file (a parte la data)', mod.testo_json({**base}) == testo)
spazio = copy.deepcopy(righe)
spazio[0]['Squadra'] += ' '
verifica('spazio in fondo al nome della squadra ignorato', mod.importa(spazio, base, listone)[0]['p'] == base['p'])

print('\n2. Uno scambio e un nuovo arrivo')
mio = next(r for r in righe if r['Squadra'] == base['me'] and r['Ruolo'] == 'D')
altro = next(r for r in righe if r['Squadra'] != base['me'] and r['Ruolo'] == 'D')
scambiate = copy.deepcopy(righe)
for r in scambiate:
    if r['Fantacalcio_Id'] == mio['Fantacalcio_Id']:
        r['Squadra'] = altro['Squadra']
    elif r['Fantacalcio_Id'] == altro['Fantacalcio_Id']:
        r['Squadra'] = base['me']
nuovo, _, _ = mod.importa(scambiate, base, listone)
cambi, entrati, usciti = mod.scambi(base, nuovo)
verifica('lo scambio viene riconosciuto', len(cambi) == 2 and not entrati and not usciti, cambi)
arrivo = copy.deepcopy(righe)
uscente = next(r for r in arrivo if r['Squadra'] == base['me'] and r['Ruolo'] == 'C')
uscente.update({'Fantacalcio_Id': '999999', 'Nome': 'Nuovo Arrivo', 'Squadra_Appartenenza': 'INT', 'Quotazione': '9'})
nuovo, nuovo_listone, aggiunti = mod.importa(arrivo, base, listone)
p = next(x for x in nuovo['p'] if x[0] == 999999)
verifica('nuovo arrivo: club dalla sigla, statistiche a zero', p[2] == 'Inter' and p[7:] == [0, 0.0, 0.0], p)
verifica('nuovo arrivo aggiunto al listone', aggiunti == [{'id': 999999, 'nome': 'Nuovo Arrivo', 'squadra': 'Inter'}]
         and len(nuovo_listone) == len(listone) + 1)
_, entrati, usciti = mod.scambi(base, nuovo)
verifica('entrato e uscito elencati', len(entrati) == 1 and len(usciti) == 1, (entrati, usciti))
stat = {str(p[0]): [9, 6.0, 7.0, 20] for p in base['p']}
verifica('statistiche prese da statistiche.json', all(x[7:] == [9, 6.0, 7.0] for x in mod.importa(righe, base, listone, stat)[0]['p']))

print('\n3. File sbagliati: si ferma')
ok, msg = fallisce([r for r in righe if r is not mio], mio['Squadra'])
verifica('squadra da 24', ok, msg)
strano = copy.deepcopy(righe)
for r in strano:
    if r['Squadra'] == base['me']:
        r['Squadra'] = 'BURKINA FASSO'
ok, msg = fallisce(strano, 'non presente nel calendario')
verifica('nome di squadra sconosciuto', ok, msg)
ruoli = copy.deepcopy(righe)
next(r for r in ruoli if r['Squadra'] == base['me'] and r['Ruolo'] == 'D')['Ruolo'] = 'P'
ok, msg = fallisce(ruoli, 'invece di 3 P')
verifica('ruoli sbagliati', ok, msg)
doppio = copy.deepcopy(righe)
doppio[1]['Fantacalcio_Id'] = doppio[0]['Fantacalcio_Id']
ok, msg = fallisce(doppio, 'due squadre')
verifica('giocatore in due squadre', ok, msg)
sconosciuto = copy.deepcopy(righe)
sconosciuto[0].update({'Fantacalcio_Id': '999998', 'Squadra_Appartenenza': 'XYZ'})
ok, msg = fallisce(sconosciuto, 'club sconosciuto')
verifica('club che non si riesce a ricostruire', ok, msg)

print('\n4. File delle rose dell\'app (…rosters….xlsx)')
import tempfile, openpyxl
def file_app(p_list, ordine, cartella, cambia=None):
    """Un file come quello dell'app: blocchi «squadra / costo», 25 giocatori in ordine P, D, C, A, riga «totale»."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'ROSE'
    for b, squadra in enumerate(ordine):
        rosa = sorted((p for p in p_list if p[4] == squadra), key=lambda p: 'PDCA'.index(p[3]))
        c = b * 3 + 1
        ws.cell(1, c, NOMI_APP.get(squadra, squadra)); ws.cell(1, c + 1, 'costo')
        for r, p in enumerate(rosa, start=2):
            ws.cell(r, c, (cambia or {}).get(p[1], p[1])); ws.cell(r, c + 1, p[5])
        ws.cell(len(rosa) + 2, c, 'totale'); ws.cell(len(rosa) + 2, c + 1, sum(p[5] for p in rosa))
    percorso = os.path.join(cartella, 'rivoluzione-fantacalcio-rosters-1.xlsx')
    wb.save(percorso)
    return percorso
squadre = list(dict.fromkeys(p[4] for p in base['p']))
# nell'app due squadre hanno un nome diverso: una rinominata, una con le maiuscole cambiate
altre = [s for s in squadre if s != base['me']]
NOMI_APP = {altre[0]: altre[0] + ' Nuova', altre[1]: altre[1].swapcase()}
with tempfile.TemporaryDirectory() as d:
    f = file_app(base['p'], list(reversed(squadre)), d)
    blocchi = mod.leggi_rosters(f)
    verifica('10 blocchi da 25, riga «totale» esclusa', len(blocchi) == 10 and all(len(g) == 25 for _, g in blocchi))
    righe_app, diversi = mod.righe_da_blocchi(blocchi, base, listone)
    nuovo, _, aggiunti = mod.importa(righe_app, base, listone)
    verifica('stesse rose, nello stesso ordine di base.json', nuovo['p'] == base['p'] and not aggiunti)
    attesi = sorted((v, k) for k, v in NOMI_APP.items())
    verifica('squadre riconosciute dai giocatori anche col nome diverso', sorted(diversi) == attesi, diversi)
    # scambio: Wesley (BURKINA FASO) per Dimarco (OPENDA LEGS)
    scambiato = copy.deepcopy(base['p'])
    for p in scambiato:
        if p[1] == 'Wesley': p[4] = 'OPENDA LEGS'
        elif p[1] == 'Dimarco': p[4] = base['me']
    righe_app, _ = mod.righe_da_blocchi(mod.leggi_rosters(file_app(scambiato, squadre, d)), base, listone)
    cambi, entrati, usciti = mod.scambi(base, mod.importa(righe_app, base, listone)[0])
    verifica('scambio riconosciuto', sorted(c[0] for c in cambi) == ['Dimarco', 'Wesley'] and not entrati and not usciti, cambi)
    try:
        mod.righe_da_blocchi(mod.leggi_rosters(file_app(base['p'], squadre, d, {'Kamara H.': 'Pinco Pallino'})), base, listone)
        verifica('nome sconosciuto: deve fermarsi', False)
    except ValueError as e:
        verifica('nome sconosciuto: si ferma', 'non è nel listone' in str(e), str(e).splitlines()[0])

vero = mod.trova_file(mod.DOWNLOAD) if os.path.isdir(mod.DOWNLOAD) and (
    [x for x in os.listdir(mod.DOWNLOAD) if 'rosters' in x or x.startswith('rose')]) else None
if vero:
    print(f'\n5. Il file delle rose vero più recente: {os.path.basename(vero)}')
    righe_vere = mod.righe_da_blocchi(mod.leggi_rosters(vero), base, listone)[0] if vero.endswith('.xlsx') else mod.leggi_csv(vero)
    nuovo, _, _ = mod.importa(righe_vere, base, listone)
    diversi = [(a, b) for a, b in zip(nuovo['p'], base['p']) if a != b]
    verifica('ridà le rose di base.json (se non ci sono stati scambi)', not diversi and len(nuovo['p']) == len(base['p']),
             diversi[:2] or f'{len(nuovo["p"])} giocatori')

print('\n6. Nomi dell\'app e archivio')
t0 = altre[0]
rin = mod.rinomina(base, [(t0 + ' Nuova', t0)])
nomi_cal = {s for g in rin['g'] for m in g[3] for s in m}
verifica('squadra rinominata nel calendario e nelle rose', t0 + ' Nuova' in nomi_cal and t0 not in nomi_cal
         and sum(p[4] == t0 + ' Nuova' for p in rin['p']) == 25 and all(p[4] != t0 for p in rin['p']))
verifica('il base.json di partenza resta intatto', t0 in {p[4] for p in base['p']})
with tempfile.TemporaryDirectory() as d:
    dl, ar = os.path.join(d, 'Download'), os.path.join(d, 'archivio')
    os.makedirs(dl)
    vecchi = mod.DOWNLOAD, mod.ARCHIVIO
    mod.DOWNLOAD, mod.ARCHIVIO = dl, ar
    try:
        for k in range(2):
            f = os.path.join(dl, 'rivoluzione-fantacalcio-rosters-1.xlsx')
            open(f, 'w').close()
            dest = mod.archivia(f)
            verifica(f'file usato spostato nell\'archivio ({k + 1}ª volta)', bool(dest) and os.path.exists(dest)
                     and not os.path.exists(f), os.path.basename(dest or ''))
        fuori = os.path.join(d, 'altrove.xlsx')
        open(fuori, 'w').close()
        verifica('un file fuori da Download non si sposta', mod.archivia(fuori) is None and os.path.exists(fuori))
    finally:
        mod.DOWNLOAD, mod.ARCHIVIO = vecchi

print(f'\n{esiti - falliti}/{esiti} verifiche superate')
sys.exit(1 if falliti else 0)
