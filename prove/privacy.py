"""Verifica che i dati committati usino solo i nomi delle squadre dell'app (da
dati/base.json), mai un nome "grezzo" preso da un file di Leghe. Una squadra
si è già chiamata «Francesco e Fabrizio Fontana» nel file vero scaricato da
Leghe: se un nome così finisse per errore in dati/, il repository è pubblico
e resterebbe lì. Le squadre di dati/base.json sono la fonte di verità: non
serve un elenco di nomi da evitare, basta controllare che non compaia altro.

Uso: python prove/privacy.py
"""
import json, os, sys

REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(REPO, 'dati')

esiti = falliti = 0
def verifica(nome, cond, dettaglio=''):
    global esiti, falliti
    esiti += 1
    falliti += not cond
    print(('  ok   ' if cond else '  NO   ') + nome + (f'  ->  {dettaglio}' if dettaglio != '' else ''))

with open(os.path.join(DATI, 'base.json'), encoding='utf-8') as f:
    base = json.load(f)
SQUADRE = {s for g in base['g'] for sfida in g[3] for s in sfida}
verifica('dati/base.json: 10 squadre, la fonte di verità dei nomi', len(SQUADRE) == 10, sorted(SQUADRE))

ignote = sorted({r[4] for r in base['p'] if r[4] not in SQUADRE})
verifica('dati/base.json: ogni giocatore in una delle 10 squadre note', not ignote, ignote)

p = os.path.join(DATI, 'lega.json')
if os.path.exists(p):
    with open(p, encoding='utf-8') as f:
        lega = json.load(f)
    ignote = sorted({r[1] for r in lega.get('classifica', []) if r[1] not in SQUADRE})
    verifica('dati/lega.json: classifica con nomi noti', not ignote, ignote)
    ignote = sorted({n for righe in lega.get('risultati', {}).values() for r in righe
                      for n in (r[0], r[2]) if n not in SQUADRE})
    verifica('dati/lega.json: risultati con nomi noti', not ignote, ignote)
else:
    print('  --   dati/lega.json non c\'è: prova saltata')

print(f'\n{esiti - falliti}/{esiti} verifiche superate')
sys.exit(1 if falliti else 0)
