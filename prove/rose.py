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

vero = os.path.join(os.path.expanduser('~'), 'Downloads', 'rose.csv')
if os.path.exists(vero):
    print('\n4. Il rose.csv vero nella cartella Download')
    nuovo, _, aggiunti = mod.importa(mod.leggi_csv(vero), base, listone)
    diversi = [(a, b) for a, b in zip(nuovo['p'], base['p']) if a != b]
    verifica('ridà le rose di base.json (se non ci sono stati scambi)', not diversi and len(nuovo['p']) == len(base['p']),
             diversi[:2] or f'{len(nuovo["p"])} giocatori')

print(f'\n{esiti - falliti}/{esiti} verifiche superate')
sys.exit(1 if falliti else 0)
