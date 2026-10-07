"""Configurazione delle leghe (multi-lega, 07/10/2026): legge dati/leghe.json.

Ogni lega ha una cartella dentro dati/ ('' per la prima, 'qi/' per la seconda) con i
suoi quattro file di lega (base, lega, consigli, formazioni). I dati di Serie A
(voti, orari, infortuni, statistiche, modello…) restano in dati/ e sono condivisi.
"""
import json, os, sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(RADICE, 'dati')
PROTETTI = ['base.json', 'lega.json', 'consigli.json', 'formazioni.json']


def tutte():
    with open(os.path.join(DATI, 'leghe.json'), encoding='utf-8') as f:
        return json.load(f)


def lega(id_=None):
    """La lega con questo id (o quella predefinita)."""
    conf = tutte()
    id_ = id_ or conf['predefinita']
    for l in conf['leghe']:
        if l['id'] == id_:
            return l
    raise SystemExit(f'lega «{id_}» non presente in dati/leghe.json')


def id_da_argomenti(argv=None):
    """Legge «--lega <id>» dagli argomenti e lo toglie dalla lista (sys.argv se non data)."""
    argv = sys.argv if argv is None else argv
    if '--lega' in argv:
        k = argv.index('--lega')
        id_ = argv[k + 1]
        del argv[k:k + 2]
        return id_
    return None


def cartella(cfg):
    """Percorso assoluto della cartella dei dati di lega ('' = dati/ stessa)."""
    return os.path.join(DATI, cfg['cartella'].strip('/')) if cfg['cartella'] else DATI


def percorso(cfg, nome):
    """Percorso assoluto di un file di lega (es. base.json) per questa lega."""
    return os.path.join(cartella(cfg), nome)


def nome_aad(cfg, nome):
    """Nome associato nel lucchetto: cartella + nome ('base.json' per la prima lega, 'qi/base.json')."""
    return cfg['cartella'] + nome
