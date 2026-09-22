"""Prova di scripts/importa_formazioni.py: una pagina ricostruita dalla rosa vera
(dati/base.json) deve ridare gli stessi Id; pagine non plausibili devono
fermarsi senza scrivere niente.

Uso: python prove/formazioni.py
"""
import importlib.util, json, os, sys

REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('importa_formazioni', os.path.join(REPO, 'scripts', 'importa_formazioni.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
with open(os.path.join(REPO, 'dati', 'base.json'), encoding='utf-8') as f:
    base = json.load(f)

esiti = falliti = 0
def verifica(nome, cond, dettaglio=''):
    global esiti, falliti
    esiti += 1
    falliti += not cond
    print(('  ok   ' if cond else '  NO   ') + nome + (f'  ->  {dettaglio}' if dettaglio != '' else ''))

def fallisce(f, cosa=None):
    try:
        f()
        return False, 'nessun errore'
    except ValueError as e:
        return (cosa is None or cosa in str(e)), str(e).splitlines()[0]

rosa_me = [p for p in base['p'] if p[4] == base['me']]
altra_squadra = next(s for s in {p[4] for p in base['p']} if s != base['me'])
rosa_altra = [p for p in base['p'] if p[4] == altra_squadra]

def scegli(rosa, d, c, a):
    """11 titolari (1 P + d D + c C + a A, nell'ordine della rosa) e il resto in panchina."""
    per_ruolo = {r: [p for p in rosa if p[3] == r] for r in 'PDCA'}
    titolari = per_ruolo['P'][:1] + per_ruolo['D'][:d] + per_ruolo['C'][:c] + per_ruolo['A'][:a]
    panchina = [p for p in rosa if p not in titolari]
    return titolari, panchina

def pagina(nome_a, modulo_a, titolari_a, panchina_a, nome_b, modulo_b, titolari_b, panchina_b, non_schierata=False):
    """Il testo di una pagina round/<giornata>, come lo restituisce get_page_text
    (solo l'articolo della partita): intestazione, titolari, «Panchina», panchina."""
    righe = [nome_a, 'Proprietario A', 'Non schierata' if non_schierata else modulo_a]
    if not non_schierata:
        righe += ['1', '70', '-', '1', '65']
    righe += [nome_b, 'Proprietario B', 'Non schierata' if non_schierata else modulo_b]
    if non_schierata:
        righe.append('Formazione non inserita')
    else:
        for p in titolari_a + titolari_b:
            righe += [p[1], '6', '6']
        righe.append('Panchina')
        for p in panchina_a + panchina_b:
            righe.append(p[1])            # nessun voto: come chi non è entrato
    righe += ['Totale parziali', '65', 'solo voti', '65', 'con bonus/malus', '65']
    return '\n'.join(righe)

print('\n1. Pagina vera (dalla rosa reale), modulo 4-3-3')
tit, panc = scegli(rosa_me, 4, 3, 3)
tit_altra, panc_altra = scegli(rosa_altra, 4, 4, 2)
testo = pagina(base['me'], '4-3-3', tit, panc, altra_squadra, '4-4-2', tit_altra, panc_altra)
riga = mod.importa(testo, base)
verifica('modulo letto', riga['modulo'] == '4-3-3')
verifica('titolari giusti, nello stesso ordine della pagina', riga['titolari'] == [p[0] for p in tit], riga['titolari'])
verifica('panchina giusta', sorted(riga['panchina']) == sorted(p[0] for p in panc))

print('\n2. La tua squadra può comparire per prima o per seconda nella pagina')
testo2 = pagina(altra_squadra, '4-4-2', tit_altra, panc_altra, base['me'], '4-3-3', tit, panc)
riga2 = mod.importa(testo2, base)
verifica('stesso risultato, a prescindere dalla posizione', riga2 == riga)

print('\n3. Formazione non ancora inserita')
testo3 = pagina(base['me'], '', [], [], altra_squadra, '', [], [], non_schierata=True)
ok, msg = fallisce(lambda: mod.importa(testo3, base), 'non ancora inserita')
verifica('si ferma con un messaggio chiaro, non inventa niente', ok, msg)

print('\n4. Pagine non plausibili')
rotta = testo.replace(tit[0][1], 'Un Nome Mai Visto')
ok, msg = fallisce(lambda: mod.importa(rotta, base), 'non è nella rosa')
verifica('un nome non nella rosa: si ferma', ok, msg)

sballato = testo.replace('4-3-3', '4-5-1', 1)     # titolari letti restano 4 D, 3 C, 3 A
ok, msg = fallisce(lambda: mod.importa(sballato, base), 'non corrispondono al modulo')
verifica('titolari e modulo dichiarato non tornano: si ferma', ok, msg)

senza_panchina = '\n'.join(r for r in testo.splitlines() if r != 'Panchina')
ok, _ = fallisce(lambda: mod.importa(senza_panchina, base))
verifica('senza la sezione «Panchina»: si ferma', ok)

altrove = pagina('Una Squadra Mai Vista', '4-3-3', tit, panc, altra_squadra, '4-4-2', tit_altra, panc_altra)
ok, msg = fallisce(lambda: mod.importa(altrove, base), 'non compare')
verifica('la tua squadra non è in questa pagina (giornata sbagliata): si ferma', ok, msg)

base_rotta = {**base, 'p': [p for p in base['p'] if not (p[4] == base['me'] and p[3] == 'A')]}
ok, msg = fallisce(lambda: mod.importa(testo, base_rotta), 'invece di')
verifica('la tua rosa in base.json non è di 25: si ferma prima ancora di leggere la pagina', ok, msg)

print(f'\n{esiti - falliti}/{esiti} verifiche superate')
sys.exit(1 if falliti else 0)
