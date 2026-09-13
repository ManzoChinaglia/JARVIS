"""Prova di orari() e scrivi() di scripts/aggiorna.py con una fonte finta.

Uso: python prove/orari.py
"""
import importlib.util, json, os, sys, tempfile
from datetime import datetime, timedelta, timezone

REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('aggiorna', os.path.join(REPO, 'scripts', 'aggiorna.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

esiti = falliti = 0
def verifica(nome, cond, dettaglio=''):
    global esiti, falliti
    esiti += 1
    falliti += not cond
    print(('  ok   ' if cond else '  NO   ') + nome + (f'  ->  {dettaglio}' if dettaglio != '' else ''))

SQ = ['Internazionale', 'Monza', 'Roma', 'Lazio', 'Milan', 'Napoli', 'Juventus', 'Torino', 'Genoa', 'Lecce',
      'Como', 'Parma', 'Udinese', 'Venezia', 'Bologna', 'Atalanta', 'Fiorentina', 'Sassuolo', 'Cagliari', 'Frosinone']

def feed(ufficiali=12, togli=None, rinvio=None):
    """38 giornate da 10 partite: le prime `ufficiali` con orario, le altre a mezzanotte UTC."""
    partite, base = [], datetime(2026, 8, 21, 18, 45, tzinfo=timezone.utc)
    for n in range(1, 39):
        for i in range(10):
            if togli == n and i == 9:
                continue
            if n <= ufficiali:
                q = base + timedelta(weeks=n - 1, hours=18 * i)
                if rinvio == n and i == 9:
                    q += timedelta(weeks=3)
            else:
                q = (base + timedelta(weeks=n - 1)).replace(hour=0, minute=0)
            partite.append({'RoundNumber': n, 'DateUtc': q.strftime('%Y-%m-%d %H:%M:%SZ'),
                            'HomeTeam': SQ[2 * i], 'AwayTeam': SQ[2 * i + 1]})
    return partite

class Risposta:
    def __init__(self, dati): self.dati = dati
    def raise_for_status(self): pass
    def json(self): return self.dati

def con(dati):
    mod.requests.get = lambda *a, **k: Risposta(dati)

print('\n1. Fonte normale: 12 giornate con orario, 26 a mezzanotte')
con(feed())
g = mod.orari({})['giornate']
verifica('38 giornate', len(g) == 38, len(g))
verifica('12 ufficiali', sum(x['ufficiale'] for x in g.values()) == 12)
verifica('giornata 13 senza orario inventato', g['13'] == {'ufficiale': False}, g['13'])
verifica('inizio = prima partita', g['1']['inizio'] == '2026-08-21T18:45:00+00:00', g['1']['inizio'])
verifica('Internazionale diventa Inter', g['1']['prima'] == 'Inter-Monza', g['1']['prima'])

print('\n2. La fonte perde un orario gia\' noto')
con(feed(ufficiali=12))
vecchie = {'13': {'ufficiale': True, 'inizio': 'X', 'fine': 'Y', 'prima': 'A-B'}}
g = mod.orari(vecchie)['giornate']
verifica('tengo l\'orario precedente', g['13'] == vecchie['13'], g['13'])

print('\n3. Recupero spostato di tre settimane')
con(feed(rinvio=4))
g = mod.orari({})['giornate']
fine = datetime.fromisoformat(g['4']['fine']) - datetime.fromisoformat(g['4']['inizio'])
verifica('la fine giornata ignora il recupero', fine < timedelta(days=4), fine)

print('\n4. Fonte con struttura cambiata (9 partite in una giornata)')
con(feed(togli=7))
try:
    mod.orari({})
    verifica('deve fermarsi', False)
except ValueError as e:
    verifica('si ferma con errore', True, e)

print('\n5. Controllo di plausibilita\' in scrittura')
with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, 'orari.json')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump({'giornate': {'1': 'vecchio'}}, f)
    scritto = mod.scrivi(p, {'giornate': {str(n): {} for n in range(1, 30)}}, 38, 'orari')
    with open(p, encoding='utf-8') as f:
        verifica('con 29 giornate non scrive', not scritto and json.load(f)['giornate'] == {'1': 'vecchio'})

print(f'\n{esiti - falliti}/{esiti} verifiche superate')
sys.exit(1 if falliti else 0)
