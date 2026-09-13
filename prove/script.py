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

def riga_fuori(p, etichetta, data=None):
    cognome, ini = come_pagina(p['nome'])
    return (f'<li class="prb-fuori__riga"><span class="role">X</span>'
            f'<span class="prb-nome">{cognome} <small>{ini}</small></span>'
            f'<span class="fco-etichetta fco-etichetta--fare">{etichetta}</span>'
            + (f'<span class="prb-fuori__data">{data}</span>' if data else '') + '</li>')

def pagina(n, pubblicate, titolari=11, blocchi=20):
    sezioni = []
    for sq in SQUADRE20[:blocchi]:
        rosa = [p for p in listone if p['squadra'] == sq]
        if sq in pubblicate:
            corpo = (f'<table class="prb-tabella"><tbody>{"".join(riga(p, 90) for p in rosa[:titolari])}</tbody></table>'
                     f'<table class="prb-tabella"><tbody>{"".join(riga(p, 30) for p in rosa[titolari:titolari + 2])}</tbody></table>')
        else:
            corpo = '<div class="prb-vuoto">Nessuna redazione ha ancora pubblicato la formazione di questa squadra.</div>'
        if sq == 'Roma':   # uno squalificato e un infortunato con data di rientro
            corpo += ('<div class="prb-fuori"><ul class="prb-fuori__elenco">' + riga_fuori(rosa[15], 'Squalificato')
                      + riga_fuori(rosa[16], 'Infortunato', 'fino al 28/10') + '</ul></div>')
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
roma = [p for p in listone if p['squadra'] == 'Roma']
verifica('indisponibili letti anche senza probabili',
         t['indisponibili'].get(str(roma[15]['id'])) == {'motivo': 'Squalificato'}
         and t['indisponibili'].get(str(roma[16]['id'])) == {'motivo': 'Infortunato', 'fino': '28/10'}, t['indisponibili'])
verifica('2 indisponibili e niente probabili: non si scrive', not mod.titolari_utili(t))
verifica('con le probabili di una squadra si scrive', mod.titolari_utili({'titolari': {str(i): 90 for i in range(11)}, 'indisponibili': {}}))
verifica('con 5 indisponibili si scrive anche senza probabili',
         mod.titolari_utili({'titolari': {}, 'indisponibili': {str(i): {'motivo': 'Infortunato'} for i in range(5)}}))
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

print('\n6bis. Statistiche e quotazioni pubbliche')
def tabella(intestazione, righe):
    """Pagina finta di fantacalcio.it: tabella con l'Id nel link del giocatore."""
    th = ''.join(f'<th>{h}</th>' for h in intestazione)
    tr = ''.join(f'<tr><td></td><td></td><td></td><th><a href="https://www.fantacalcio.it/serie-a/squadre/x/{n.lower()}/{i}">{n}</a></th>'
                 + ''.join(f'<td>{c}</td>' for c in celle) + '</tr>' for i, n, celle in righe)
    return Risposta(f'<table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>')
TESTA_ST = ['Calciatore', '', '', '', 'Sq', 'PV', 'MV', 'FM', 'Gol']
TESTA_QU = ['Calciatore', '', '', '', 'Sq', 'QI', 'QA', 'FVM / 1000']
servi({mod.URL_STATISTICHE: tabella(TESTA_ST, [(5841, 'Svilar', ['ROM', '3', '6,5', '7,17', '0']),
                                                (5585, 'Malen', ['ROM', '4', '7,0', '12,33', '5'])]),
       mod.URL_QUOTAZIONI: tabella(TESTA_QU, [(5841, 'Svilar', ['ROM', '18', '18', '83']),
                                               (5585, 'Malen', ['ROM', '34', '37', '445']),
                                               (9999, 'Nuovo', ['ROM', '5', '6', '10'])])})
st = mod.statistiche()['giocatori']
verifica('partite, media voto, fantamedia e quotazione per Id', st['5841'] == [3, 6.5, 7.17, 18] and st['5585'] == [4, 7.0, 12.33, 37], st)
verifica('chi ha solo la quotazione (nuovo arrivo) c\'è con 0 partite', st['9999'] == [0, 0.0, 0.0, 6], st.get('9999'))
servi({mod.URL_STATISTICHE: tabella(['Calciatore', '', '', '', 'Sq', 'Pres', 'MV', 'FM'], [(5841, 'Svilar', ['ROM', '3', '6,5', '7,17'])]),
       mod.URL_QUOTAZIONI: tabella(TESTA_QU, [])})
try:
    mod.statistiche()
    verifica('colonne cambiate: deve fermarsi', False)
except ValueError as e:
    verifica('colonne cambiate: si ferma', True, e)
with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, 'statistiche.json')
    ora = datetime(2026, 9, 14, 12, tzinfo=timezone.utc)
    verifica('file assente: da aggiornare', not mod.recente(p, 20, ora))
    with open(p, 'w', encoding='utf-8') as f:
        json.dump({'aggiornato': '2026-09-14T00:00:00+00:00'}, f)
    verifica('scritto 12 ore fa: si salta', mod.recente(p, 20, ora))
    verifica('scritto 21 ore fa: si aggiorna', not mod.recente(p, 20, ora + timedelta(hours=9)))

print('\n7. Calendario')
base_finta = {'me': 'BURKINA FASO', 'g': [
    [1, 5, '2026-09-20', [['CF FRINGUELLI', 'As Quel'], ['God Bless The Doc', 'BURKINA FASO']]],
    [2, 6, '2026-10-11', [['BURKINA FASO', 'OPENDA LEGS']]],
    [3, 7, '2026-10-14', [['FC TETTENHAM', 'BURKINA FASO']]],     # turno infrasettimanale
    [4, 8, '2026-10-18', [['BURKINA FASO', 'Dua Lipsia']]]]}
orari_finti = {'5': {'ufficiale': True, 'inizio': '2026-09-18T18:45:00+00:00', 'fine': '2026-09-20T18:45:00+00:00',
                     'prima': 'Monza-Sassuolo'},
               '6': {'ufficiale': True, 'inizio': '2026-10-10T13:00:00+00:00', 'fine': '2026-10-12T18:45:00+00:00',
                     'prima': 'Genoa-Fiorentina'},
               '7': {'ufficiale': False}, '8': {'ufficiale': False}}
testo, scad = mod.calendario(base_finta, orari_finti, datetime(2026, 9, 13, 12, tzinfo=timezone.utc))
righe = testo.split('\r\n')
verifica('2 scadenze: solo le giornate con orario ufficiale', scad == 2 and 'jarvis-scadenza-g3' not in testo, scad)
verifica('G1: dalle 18:30 alle 18:45 UTC, 15 minuti prima del primo anticipo',
         'DTSTART:20260918T183000Z' in testo and 'DTEND:20260918T184500Z' in testo)
verifica('titolo con l\'avversario', 'SUMMARY:Schiera la formazione · G1 contro God Bless The Doc' in righe)
verifica('un avviso 2 ore prima per ogni scadenza', testo.count('TRIGGER:-PT2H') == 2)
verifica('niente più promemoria di esportazione', 'jarvis-esporta' not in testo and 'Lista calciatori' not in testo
         and testo.count('BEGIN:VEVENT') == 2)
verifica('fuso orario Europe/Rome dichiarato', 'BEGIN:VTIMEZONE' in righe and 'TZID:Europe/Rome' in righe)
verifica('righe CRLF di al massimo 75 byte', all(len(r.encode('utf-8')) <= 75 for r in righe)
         and '\n' not in testo.replace('\r\n', ''))
verifica('testo protetto', mod.testo_ics('a,b;c\nd\\') == 'a\\,b\\;c\\nd\\\\', mod.testo_ics('a,b;c\nd\\'))
lunga = mod.piega('DESCRIPTION:' + 'è' * 60)
verifica('le righe lunghe si ripiegano senza spezzare le lettere',
         lunga.replace('\r\n ', '') == 'DESCRIPTION:' + 'è' * 60
         and all(len(x.encode('utf-8')) <= 75 for x in lunga.split('\r\n')))
_, zero = mod.calendario(base_finta, {'5': {'ufficiale': False}})
verifica('senza orari ufficiali: zero scadenze, e il file non si riscrive', zero == 0)
try:
    import icalendar
    cal = icalendar.Calendar.from_ical(testo)
    ev = [e for e in cal.walk('VEVENT')]
    prima = next(e for e in ev if 'scadenza-g1' in str(e['UID']))
    verifica('letto da icalendar: 2 eventi, G1 alle 18:30 UTC', len(ev) == 2 and prima.decoded('DTSTART')
             == datetime(2026, 9, 18, 18, 30, tzinfo=timezone.utc), len(ev))
except ImportError:
    print('  (icalendar non installato: salto la lettura con una libreria esterna)')

print(f'\n{esiti - falliti}/{esiti} verifiche superate')
sys.exit(1 if falliti else 0)
