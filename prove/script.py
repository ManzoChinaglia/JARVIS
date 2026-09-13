"""Prova di scripts/aggiorna.py con fonti finte che imitano quelle vere: nomi,
probabili per giornata, giornata da seguire, rendimento delle squadre, moduli.

Uso: python prove/script.py
"""
import importlib.util, json, os, sys, tempfile
from datetime import datetime, timedelta, timezone

from bs4 import BeautifulSoup

REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('aggiorna', os.path.join(REPO, 'scripts', 'aggiorna.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
listone = mod.carica_listone()

esiti = falliti = 0
def verifica(nome, cond, dettaglio=''):
    global esiti, falliti
    esiti += 1
    falliti += not cond
    print(('  ok   ' if cond else '  NO   ') + nome + (f'  ->  {dettaglio}' if dettaglio != '' else ''))

class Risposta:
    def __init__(self, testo='', dati=None):
        self.text, self.dati = testo, dati
    def raise_for_status(self): pass
    def json(self): return self.dati

def servi(pagine):
    """requests.get finto: indirizzo -> Risposta."""
    mod.requests.get = lambda url, *a, **k: pagine[url]


print('\n1. Nomi scritti come nelle probabili')
for squadra, nome, atteso in [('Roma', 'SVILAR M', 5841), ('Parma', 'DEL PRATO E', 6664),
                              ('Napoli', 'MILINKOVIC V', 2170), ('Napoli', 'ANGUISSA A', 4220),
                              ('Monza', 'DANY MOTA', 5882), ('Lazio', 'NUNO TAVARES', 5620),
                              ('Milan', 'DA SILVA MOREIRA D', 6372)]:
    p = mod.trova(listone, squadra, nome)
    verifica(f'{squadra} {nome}', p is not None and p['id'] == atteso, p and f"{p['nome']} ({p['id']})")
for squadra, nome in [('Parma', 'ROMERO J'), ('Venezia', 'FERNANDEZ A')]:
    p = mod.trova(listone, squadra, nome)
    verifica(f'{squadra} {nome}: iniziale diversa, nessun abbinamento', p is None, p and p['nome'])

print('\n2. Nome letto dalla pagina')
for html, atteso in [('<span class="prb-nome">\n  FALCONE\n  <small>W</small>\n</span>', 'FALCONE W'),
                     ('<span class="prb-nome">DANY MOTA <small>-</small></span>', 'DANY MOTA'),
                     ('<span class="prb-nome">DEL PRATO <small>E</small></span>', 'DEL PRATO E')]:
    letto = mod.leggi_nome(BeautifulSoup(html, 'lxml').select_one('.prb-nome'))
    verifica(repr(atteso), letto == atteso, letto)

print('\n3. Probabili della giornata')
SQUADRE20 = sorted({p['squadra'] for p in listone})

def come_pagina(nome):
    """"Kamara H." -> ("KAMARA", "H"); "Svilar" -> ("SVILAR", "-")."""
    parti = nome.replace('.', '').split()
    if len(parti) > 1 and len(parti[-1]) <= 2:
        return ' '.join(parti[:-1]).upper(), parti[-1][0].upper()
    return nome.upper(), '-'

def riga(p, perc):
    cognome, ini = come_pagina(p['nome'])
    return (f'<tr><th class="prb-tabella__chi"><span class="role">X</span>'
            f'<span class="prb-nome">{cognome} <small>{ini}</small></span></th>'
            f'<td class="prb-cella"><span>{perc}%</span></td>'
            f'<td class="prb-cella prb-cella--media"><span>{perc}%</span></td></tr>')

def pagina(n, pubblicate, titolari=11, blocchi=20):
    sezioni = []
    for sq in SQUADRE20[:blocchi]:
        if sq in pubblicate:
            rosa = [p for p in listone if p['squadra'] == sq]
            corpo = (f'<table class="prb-tabella"><tbody>{"".join(riga(p, 90) for p in rosa[:titolari])}</tbody></table>'
                     f'<table class="prb-tabella"><tbody>{"".join(riga(p, 30) for p in rosa[titolari:titolari + 2])}</tbody></table>')
        else:
            corpo = '<div class="prb-vuoto">Nessuna redazione ha ancora pubblicato la formazione di questa squadra.</div>'
        sezioni.append(f'<section class="prb-squadra"><h2 class="prb-squadra__nome">{sq}</h2>{corpo}</section>')
    return Risposta(f'<html><head><title>Probabili Formazioni Serie A 2026/2027 - {n}ª Giornata</title></head>'
                    f'<body>{"".join(sezioni)}</body></html>')

url5 = mod.URL_GIORNATA.format(5)
servi({url5: pagina(5, ['Roma', 'Parma'])})
t = mod.titolari(listone, 5)
attesi = {str(p['id']) for sq in ('Parma', 'Roma') for p in [x for x in listone if x['squadra'] == sq][:11]}
verifica('giornata e squadre pubblicate', t['giornata'] == 5 and t['squadre'] == ['Parma', 'Roma'], (t['giornata'], t['squadre']))
verifica('i 22 titolari giusti, al 90%', set(t['titolari']) == attesi and set(t['titolari'].values()) == {90},
         f"{len(t['titolari'])} titolari, differenze {sorted(set(t['titolari']) ^ attesi)}")
verifica('4 in panchina al 30%', len(t['panchina']) == 4 and set(t['panchina'].values()) == {30}, len(t['panchina']))

servi({url5: pagina(5, [])})
t = mod.titolari(listone, 5)
verifica('nulla di pubblicato: nessun titolare', t['titolari'] == {} and t['squadre'] == [])
with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, 'titolari.json')
    with open(p, 'w', encoding='utf-8') as f:
        json.dump({'giornata': 4, 'titolari': {'1': 90}}, f)
    scritto = mod.scrivi(p, t, 11, 'titolari')
    with open(p, encoding='utf-8') as f:
        verifica('e il file della giornata prima resta com\'era', not scritto and json.load(f)['giornata'] == 4)

for nome, pag in [('pagina di un\'altra giornata', pagina(4, ['Roma'])),
                  ('19 squadre', pagina(5, ['Roma'], blocchi=19)),
                  ('10 titolari', pagina(5, ['Roma'], titolari=10))]:
    servi({url5: pag})
    try:
        mod.titolari(listone, 5)
        verifica(nome + ': deve fermarsi', False)
    except ValueError as e:
        verifica(nome + ': si ferma', True, e)

print('\n4. Giornata da seguire')
g = {'5': {'ufficiale': True, 'fine': '2026-09-20T18:45:00+00:00'},
     '6': {'ufficiale': True, 'fine': '2026-10-12T18:45:00+00:00'},
     '7': {'ufficiale': False}}
ora = datetime(2026, 9, 20, 20, 0, tzinfo=timezone.utc)
verifica('ultima partita da poco finita: resta la 5', mod.giornata_da_seguire([5, 6, 7], g, ora) == 5)
verifica('due ore dopo: passa alla 6', mod.giornata_da_seguire([5, 6, 7], g, ora + timedelta(hours=1)) == 6)
verifica('orario non ufficiale: e\' la prossima', mod.giornata_da_seguire([5, 6, 7], g, datetime(2026, 10, 20, tzinfo=timezone.utc)) == 7)
verifica('campionato finito', mod.giornata_da_seguire([5, 6], g, datetime(2026, 12, 1, tzinfo=timezone.utc)) is None)

print('\n5. Rendimento delle squadre')
COMUNI = ['Atalanta', 'Bologna', 'Cagliari', 'Como', 'Fiorentina', 'Genoa', 'Juventus', 'Lazio',
          'Lecce', 'Milan', 'Napoli', 'Parma', 'Roma', 'Sassuolo', 'Torino', 'Udinese']
PRIMA = COMUNI + ['Inter', 'Cremonese', 'Hellas Verona', 'Pisa']
ADESSO = COMUNI + ['Internazionale', 'Frosinone', 'Monza', 'Venezia']

def stagione(squadre, giocate):
    """Tutte le 380 partite; le prime `giocate` finite 2-1 per chi gioca in casa."""
    partite = []
    for i, c in enumerate(squadre):
        for j, f in enumerate(squadre):
            if i != j:
                finita = len(partite) < giocate
                partite.append({'HomeTeam': c, 'AwayTeam': f,
                                'HomeTeamScore': 2 if finita else None, 'AwayTeamScore': 1 if finita else None})
    return partite

servi({mod.URL_ORARI: Risposta(dati=stagione(ADESSO, 30)), mod.URL_PRECEDENTE: Risposta(dati=stagione(PRIMA, 380))})
s = mod.squadre({'Inter': '3-5-2'})
sq = s['squadre']
verifica('20 squadre, Internazionale diventa Inter', len(sq) == 20 and 'Inter' in sq and 'Internazionale' not in sq)
verifica('Inter ha la stagione scorsa', not sq['Inter'].get('neopromossa') and sq['Inter']['precedente']['casa'] == [19, 38, 19, 0],
         sq['Inter']['precedente'])
verifica('neopromosse segnate come stima', all(sq[x].get('neopromossa') for x in ('Frosinone', 'Monza', 'Venezia')))
verifica('le tre retrocesse', s['retrocesse'] == ['Cremonese', 'Hellas Verona', 'Pisa'], s['retrocesse'])
verifica('stima = media delle retrocesse', sq['Monza']['precedente']['fuori'] == [19, 19, 38, 0], sq['Monza']['precedente'])
verifica('partite di quest\'anno contate', sum(v['attuale']['casa'][0] + v['attuale']['fuori'][0] for v in sq.values()) == 60)
verifica('modulo abituale', sq['Inter'].get('modulo') == '3-5-2' and 'modulo' not in sq['Roma'])
verifica('totali del campionato scorso', s['campionato_precedente']['casa'] == [380, 760, 380, 0], s['campionato_precedente'])
servi({mod.URL_ORARI: Risposta(dati=stagione(ADESSO, 30)), mod.URL_PRECEDENTE: Risposta(dati=stagione(PRIMA, 380)[:-1])})
try:
    mod.squadre({})
    verifica('stagione scorsa incompleta: deve fermarsi', False)
except ValueError as e:
    verifica('stagione scorsa incompleta: si ferma', True, e)

print('\n6. Modulo abituale')
html = ('<div class="art-tabella"><table><tbody>'
        '<tr><td>Atalanta</td><td>4-3-3</td><td>Sarri</td><td>Carnesecchi, Scalvini</td><td>Rowe</td></tr>'
        '<tr><td>Genoa</td><td>3-4-1-2</td><td>Vieira</td><td>Leali, Vasquez</td><td>Ekhator</td></tr>'
        '</tbody></table></div>'
        '<div class="art-tabella"><table><tbody><tr><td>4-3-3</td><td>7</td><td>Atalanta, Lazio</td></tr></tbody></table></div>'
        '<div class="art-tabella"><table><tbody><tr><td>Inter</td><td>313</td><td>3-5-2</td></tr></tbody></table></div>')
servi({mod.URL_SQUADRE_TIPO: Risposta(html)})
m = mod.moduli()
verifica('solo dalla tabella delle formazioni', m == {'Atalanta': '4-3-3', 'Genoa': '3-4-1-2'}, m)

print(f'\n{esiti - falliti}/{esiti} verifiche superate')
sys.exit(1 if falliti else 0)
