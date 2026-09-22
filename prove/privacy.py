"""Verifica che i dati committati usino solo i nomi delle squadre dell'app (da
dati/base.json), mai un nome "grezzo" preso da un file di Leghe. Una squadra
si è già chiamata, nel file vero scaricato da Leghe, con nome e cognome di
persone vere: se un nome così finisse per errore in dati/, il repository è
pubblico e resterebbe lì. Le squadre di dati/base.json sono la fonte di verità:
non serve un elenco di nomi da evitare, basta controllare che non compaia altro.

Dal 16/09/2026 anche il lucchetto: i dati della lega stanno nel repository solo
chiusi, e nei file pubblici (codice, prove, documentazione, calendario) non
compare il nome di nessun'altra squadra.

Uso: python prove/privacy.py   (dopo `node scripts/lucchetto.js apri`, se il lucchetto c'è)
"""
import json, os, subprocess, sys, zipfile

REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(REPO, 'dati')
PROTETTI = ['base.json', 'lega.json', 'consigli.json', 'formazioni.json']
TESTO = ('.html', '.js', '.py', '.md', '.yml', '.yaml', '.json', '.ics', '.txt', '.webmanifest', '.css')
OFFICE = ('.xlsx', '.xlsm', '.docx', '.pptx')

esiti = falliti = 0
def verifica(nome, cond, dettaglio=''):
    global esiti, falliti
    esiti += 1
    falliti += not cond
    print(('  ok   ' if cond else '  NO   ') + nome + (f'  ->  {dettaglio}' if dettaglio != '' else ''))

with open(os.path.join(DATI, 'base.json'), encoding='utf-8') as f:
    base = json.load(f)
SQUADRE = {s for g in base['g'] for sfida in g[3] for s in sfida}
verifica('dati/base.json: 10 squadre, la fonte di verità dei nomi', len(SQUADRE) == 10, len(SQUADRE))

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

# i file che stanno nella storia (pubblici): tutti meno i dati della lega da proteggere
try:
    tracciati = subprocess.run(['git', 'ls-files'], cwd=REPO, capture_output=True, text=True, check=True).stdout.split('\n')
except Exception:
    tracciati = None
if tracciati is None:
    print('  --   git non disponibile: prove sul repository saltate')
else:
    tracciati = [t for t in tracciati if t]
    lucchetto = os.path.join(DATI, 'lucchetto.json')
    if os.path.exists(lucchetto):
        in_chiaro = [n for n in PROTETTI if f'dati/{n}' in tracciati]
        verifica('col lucchetto i dati della lega in chiaro non stanno nella storia', not in_chiaro, in_chiaro)
        with open(lucchetto, encoding='utf-8') as f:
            lk = json.load(f)
        verifica('il lucchetto pubblico ha solo sale, iterazioni e la prova cifrata',
                 set(lk) == {'versione', 'sale', 'iterazioni', 'prova'} and lk['iterazioni'] >= 100000, sorted(lk))
        verifica('e ogni file della lega che c\'è ha la sua copia chiusa nella storia',
                 all(f'dati/{n[:-5]}.chiuso.json' in tracciati for n in PROTETTI if os.path.exists(os.path.join(DATI, n))))
    else:
        print('  --   lucchetto non ancora attivo: prove del lucchetto saltate')
    altre = sorted(s for s in SQUADRE if s != base['me'])
    trovati = []
    for t in tracciati:
        if t in [f'dati/{n}' for n in PROTETTI]:
            continue
        try:
            if t.endswith(TESTO):
                with open(os.path.join(REPO, t), encoding='utf-8') as f:
                    testo = f.read().lower()
            elif t.endswith(OFFICE):
                # un file Office è uno zip di XML: i nomi stanno dentro, non si vedono da fuori.
                # Il 16/09/2026 un file di prova con i nomi veri era passato proprio da qui
                with zipfile.ZipFile(os.path.join(REPO, t)) as z:
                    testo = ' '.join(z.read(n).decode('utf-8', 'ignore') for n in z.namelist() if n.endswith('.xml')).lower()
            else:
                continue
        except (OSError, UnicodeDecodeError, zipfile.BadZipFile):
            continue
        trovati += [f'{t}: {s}' for s in altre if s.lower() in testo]
    verifica('nei file pubblici nessun nome di un\'altra squadra (codice, prove, documenti, calendario, file Excel)',
             not trovati, len(trovati) and trovati[:5])

print(f'\n{esiti - falliti}/{esiti} verifiche superate')
sys.exit(1 if falliti else 0)
