#!/usr/bin/env python3
"""
Un solo giro per la «formazione schierata» (PROCEDURE.md): apre il lucchetto,
importa una o più giornate, richiude e lancia le prove. Non tocca Leghe (il testo
delle pagine lo cattura Claude dal Chrome dell'utente, con la sua conferma) e non
fa commit.

Uso:
  python scripts/schiera.py --mancanti
      elenca le giornate finite da almeno due ore, già in lega.json, di cui manca la tua
      formazione; non scrive niente. Se la lega ha giocato una giornata senza che tu
      abbia inserito la formazione, Leghe dice «Formazione non inserita»: non c'è nulla
      da recuperare.
  python scripts/schiera.py <giornata>=<file di testo> [<giornata>=<file> ...] [--prova]
      importa ogni giornata con importa_formazioni.py; con --prova non scrive.
      Se una giornata non passa i controlli, si ferma: le precedenti restano
      salvate, i dati di prima non si perdono, e il lucchetto viene comunque richiuso.
"""
import json, os, subprocess, sys
from datetime import datetime, timedelta, timezone

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATI = os.path.join(RADICE, 'dati')


def esegui(comando):
    return subprocess.run(comando, cwd=RADICE).returncode


def lucchetto(azione):
    return esegui(['node', 'scripts/lucchetto.js', azione])


def carica(nome):
    try:
        with open(os.path.join(DATI, nome), encoding='utf-8') as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def mancanti(ora=None):
    ora = ora or datetime.now(timezone.utc)
    schierate = set((carica('formazioni.json').get('giornate') or {}))
    giocate = set((carica('lega.json').get('risultati') or {}))   # la lega le ha giocate
    esito = []
    for n, g in (carica('orari.json').get('giornate') or {}).items():
        if not g.get('ufficiale'):
            continue
        if datetime.fromisoformat(g['fine']) + timedelta(hours=2) <= ora and n in giocate and n not in schierate:
            esito.append(int(n))
    return sorted(esito)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    prova = '--prova' in sys.argv
    if '--mancanti' not in sys.argv and not args:
        print(__doc__)
        sys.exit(1)

    if lucchetto('apri') != 0:
        sys.exit('lucchetto non aperto: mi fermo.')
    esito = 0
    try:
        if '--mancanti' in sys.argv:
            m = mancanti()
            print('formazione mancante per le giornate: ' + (', '.join(map(str, m)) or 'nessuna'))
            return
        coppie = []
        for a in args:
            n, _, percorso = a.partition('=')
            if not n.isdigit() or not percorso:
                sys.exit(f'argomento non valido «{a}»: serve <giornata>=<file>')
            coppie.append((n, percorso))
        for n, percorso in coppie:
            comando = [sys.executable, 'scripts/importa_formazioni.py', percorso, n]
            if prova:
                comando.append('--prova')
            if esegui(comando) != 0:
                esito = 1
                break
    finally:
        if '--mancanti' not in sys.argv and not prova:
            lucchetto('chiudi')          # dopo ogni import, prima del commit
    if esito == 0 and '--mancanti' not in sys.argv and not prova:
        for prova_py in ('prove/formazioni.py', 'prove/privacy.py'):
            if esegui([sys.executable, prova_py]) != 0:
                esito = 1
    sys.exit(esito)


if __name__ == '__main__':
    main()
