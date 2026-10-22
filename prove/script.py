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
for squadra, nome in [('Venezia', 'FERNANDEZ A'), ('Napoli', 'ROMERO J')]:
    p = mod.trova(listone, squadra, nome)
    verifica(f'{squadra} {nome}: iniziale diversa, nessun abbinamento', p is None, p and p['nome'])
p = mod.trova(listone, 'Parma', 'ROMERO J')
verifica('Parma ROMERO J: alias verificato su Romero D. (17/10/2026)', p is not None and p['id'] == 7554, p and p['nome'])

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

# l'archivio delle probabili passate (registra_storico): una voce per giornata, l'ultima versione vince
vecchio_dati = mod.DATI
with tempfile.TemporaryDirectory() as d:
    mod.DATI = d
    pr = lambda n, tit: {'aggiornato': 'x', 'giornata': n, 'squadre': ['Roma'], 'titolari': tit, 'panchina': {'9': 30}}
    mod.registra_storico(pr(5, {'1': 90}))
    mod.registra_storico(pr(5, {'1': 70}))
    mod.registra_storico(pr(6, {'1': 80}))
    mod.registra_storico({'aggiornato': 'x', 'giornata': 7, 'squadre': [], 'titolari': {}, 'panchina': {}})
    with open(os.path.join(d, 'titolari-storico.json'), encoding='utf-8') as f:
        st = json.load(f)
    verifica('storico: una voce per giornata, ultima versione vince', st['giornate']['5']['t'] == {'1': 70} and set(st['giornate']) == {'5', '6'}, list(st['giornate']))
    verifica('storico: squadre, titolari e panchina', st['giornate']['6'] == {'squadre': ['Roma'], 't': {'1': 80}, 'p': {'9': 30}})
    verifica('storico: senza squadre pubblicate non si registra', '7' not in st['giornate'])
mod.DATI = vecchio_dati

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
verifica('le tre retrocesse, con i nomi di fantacalcio.it', s['retrocesse'] == ['Cremonese', 'Pisa', 'Verona'], s['retrocesse'])
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
rst = mod.statistiche()
st = rst['giocatori']
verifica('partite, media voto, fantamedia e quotazione per Id', st['5841'] == [3, 6.5, 7.17, 18] and st['5585'] == [4, 7.0, 12.33, 37], st)
verifica('la quotazione iniziale a parte, per il modello', rst['iniziali'] == {'5841': 18, '5585': 34, '9999': 5}, rst['iniziali'])
verifica('chi ha solo la quotazione (nuovo arrivo) c\'è con 0 partite', st['9999'] == [0, 0.0, 0.0, 6], st.get('9999'))
verifica('colonne dei bonus diverse: restano le statistiche principali, senza bonus', all(len(v) == 4 for v in st.values()))
TESTA_BONUS = ['Calciatore', '', '', '', 'Sq', 'PV', 'MV', 'FM', 'Gol', 'GS', 'Rig', 'RP', 'Ass', 'Amm', 'Esp']
servi({mod.URL_STATISTICHE: tabella(TESTA_BONUS, [(5841, 'Svilar', ['ROM', '3', '6,5', '7,17', '0', '2', '0 / 0', '1', '0', '0', '0']),
                                                   (5585, 'Malen', ['ROM', '4', '7,0', '12,33', '5', '0', '1 / 1', '0', '2', '1', '0'])]),
       mod.URL_QUOTAZIONI: tabella(TESTA_QU, [(5841, 'Svilar', ['ROM', '18', '18', '83']),
                                               (5585, 'Malen', ['ROM', '34', '37', '445'])])})
st = mod.statistiche()['giocatori']
verifica('bonus e malus: gol, gol subiti, rigori parati, assist, ammonizioni, espulsioni',
         st['5841'][:10] == [3, 6.5, 7.17, 18, 0, 2, 1, 0, 0, 0] and st['5585'][:10] == [4, 7.0, 12.33, 37, 5, 0, 0, 2, 1, 0], st)
verifica('rigori segnati e calciati in fondo, da «segnati / calciati»', st['5841'][10:] == [0, 0] and st['5585'][10:] == [1, 1], st)
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

print('\n6ter. Voti delle giornate')
def pagina_voti(voti):
    """Pagina finta dei voti: per ogni giocatore link con l'Id, voto e fantavoto della
    redazione Fantacalcio, poi il voto di un'altra redazione (da ignorare)."""
    righe = ''.join(f'<tr><td><div class="player-item"><a href="https://www.fantacalcio.it/serie-a/squadre/x/g/{i}">g</a></div></td>'
                    f'<td><span class="player-grade" data-value="{v}"></span><span class="player-fanta-grade" data-value="{fv}"></span>'
                    f'<span class="player-grade" data-value="9"></span></td></tr>' for i, (v, fv) in voti.items())
    return Risposta(f'<table class="grades-table"><thead><tr><th>Squadra</th></tr></thead><tbody>{righe}</tbody></table>')
tanti = {5000 + k: ('6,5', '7,5') for k in range(210)}
tanti[4431] = ('6', '4,5')
con_sv = dict(tanti)
con_sv[4999] = ('-', '-')
con_sv[4998] = ('55', '55')                  # così la pagina scrive «s.v.»
servi({mod.URL_VOTI.format(4): pagina_voti(con_sv)})
v4 = mod.voti_giornata(4)
verifica('voto e fantavoto della redazione Fantacalcio per Id; chi è senza voto non c\'è',
         v4['4431'] == [6.0, 4.5] and v4['5000'] == [6.5, 7.5] and '4999' not in v4 and len(v4) == 211, len(v4))
verifica('«s.v.» scritto come 55: non è un voto', '4998' not in v4)
ora = datetime(2026, 9, 15, 12, tzinfo=timezone.utc)
g_orari = {'3': {'ufficiale': True, 'fine': '2026-09-01T18:45:00+00:00'},
           '4': {'ufficiale': True, 'fine': '2026-09-14T18:45:00+00:00'},
           '5': {'ufficiale': True, 'fine': '2026-09-20T18:45:00+00:00'},
           '6': {'ufficiale': False}}
chieste = []
def chiedi_voti(url, *a, **k):
    chieste.append(url)
    return pagina_voti(tanti)
mod.requests.get = chiedi_voti
r = mod.voti(g_orari, {'3': {'1': [6.0, 6.0]}}, ora)
verifica('solo le giornate finite: la 3 già presa e stabile resta, la 4 si scarica, la 5 non è giocata',
         chieste == [mod.URL_VOTI.format(4)] and r['giornate']['3'] == {'1': [6.0, 6.0]} and len(r['giornate']['4']) == 211, chieste)
chieste.clear()
mod.voti(g_orari, {'3': {'1': [6.0, 6.0]}, '4': {'1': [6.0, 6.0]}}, ora)
verifica('nei tre giorni dopo la fine si riscarica (i voti si assestano)', chieste == [mod.URL_VOTI.format(4)], chieste)
mod.requests.get = lambda url, *a, **k: pagina_voti({1: ('6', '6')})
r = mod.voti(g_orari, {}, ora)
verifica('pagina con meno di 200 voti: la giornata non si salva', '4' not in r['giornate'] and '3' not in r['giornate'])

print('\n6quater. Storico dei voti (B1)')
def pagina_storico(quanti, stagione='2021-22'):
    """Pagina finta di una stagione passata: il link del giocatore finisce con la
    stagione, e ogni riga ha ruolo, voto e fantavoto di due redazioni e i bonus."""
    righe = ''.join(
        f'<tr><td><span class="role" data-value="d"></span>'
        f'<a href="https://www.fantacalcio.it/serie-a/squadre/atalanta/nome/{7000 + k}/{stagione}">n</a></td>'
        f'<td><div class="pill"><span class="player-grade" data-value="6,5"></span><span class="player-fanta-grade" data-value="9,5"></span></div>'
        f'<div class="pill"><span class="player-grade" data-value="5"></span><span class="player-fanta-grade" data-value="5"></span></div></td>'
        f'<td><span class="player-bonus" title="Gol segnati" data-value="1"></span>'
        f'<span class="player-bonus" title="Gol subiti" data-value="0"></span>'
        f'<span class="player-bonus" title="Assist" data-value="0"></span></td></tr>' for k in range(quanti))
    return Risposta(f'<table class="grades-table"><thead><tr><th>Atalanta</th><th>Voto</th></tr></thead><tbody>{righe}</tbody></table>')
rs = mod.righe_voti(pagina_storico(2).text)
verifica('stagioni passate: l\'Id anche dal link che finisce con la stagione', [x['id'] for x in rs] == ['7000', '7001'], rs[:1])
verifica('squadra, ruolo, voto e fantavoto della prima redazione, bonus in ordine fisso', rs[0]['squadra'] == 'Atalanta'
         and rs[0]['ruolo'] == 'D' and rs[0]['voto'] == 6.5 and rs[0]['fantavoto'] == 9.5
         and rs[0]['bonus'][mod.BONUS_VOTI.index('Gol segnati')] == 1 and rs[0]['bonus'][mod.BONUS_VOTI.index('Autoreti')] is None,
         rs[0]['bonus'])
spec_s = importlib.util.spec_from_file_location('storico', os.path.join(REPO, 'scripts', 'storico.py'))
sto = importlib.util.module_from_spec(spec_s)
spec_s.loader.exec_module(sto)
verifica('stagioni dalla 2015-16 alla 2025-26', sto.STAGIONI[0] == '2015-16' and sto.STAGIONI[-1] == '2025-26' and len(sto.STAGIONI) == 11)
sto.GIORNATE = 5
chieste_s = []
def finto_storico(url, *a, **k):
    chieste_s.append(url)
    n = int(url.rstrip('/').rsplit('/', 1)[1])
    if n == 5:
        raise sto.aggiorna.requests.ConnectionError('rete giù')
    return pagina_storico(250 if n <= 3 else 10)
sto.aggiorna.requests.get = finto_storico
with tempfile.TemporaryDirectory() as cartella:
    sto.scarica(['2021-22'], cartella=cartella, dormi=lambda s: None)
    d = sto.leggi('2021-22', cartella)
    verifica('giornate buone salvate; con meno di 200 voti o senza rete, no',
             sorted(d['giornate'], key=int) == ['1', '2', '3'], sorted(d['giornate']))
    riga = d['giornate']['1']['7000']
    verifica('una riga per giocatore: voto, fantavoto, ruolo, squadra e bonus, nell\'ordine dei campi',
             d['campi'] == sto.CAMPI and len(riga) == len(sto.CAMPI) and riga[:4] == [6.5, 9.5, 'D', 'Atalanta'], riga)
    chieste_s.clear()
    sto.scarica(['2021-22'], cartella=cartella, dormi=lambda s: None)
    # (quotazioni e calendario qui non sono pagine vere: non si salvano e si riprovano, come dopo un errore di rete)
    verifica('ripartibile: la seconda volta chiede solo le giornate che mancano',
             [u.rsplit('/', 1)[1] for u in chieste_s if 'voti-fantacalcio' in u] == ['4', '5'],
             [u.rsplit('/', 1)[1] for u in chieste_s if 'voti-fantacalcio' in u])
    prima = open(sto.percorso('2021-22', cartella), 'rb').read()
    sto.salva(sto.leggi('2021-22', cartella), cartella)
    verifica('stesso contenuto, stesso file compresso (niente data nello zip)',
             open(sto.percorso('2021-22', cartella), 'rb').read() == prima)
    # quotazioni e calendario della stagione, una volta sola
    righe_q = ''.join(f'<tr class="player-row" data-filter-role-classic="d"><th>'
                      f'<a class="player-link" href="https://www.fantacalcio.it/serie-a/squadre/atalanta/nome/{7000 + k}/2021-22">n</a></th>'
                      f'<td data-col-key="c_qi"> {10 + k % 5} </td><td data-col-key="c_qa"> 12 </td></tr>' for k in range(450))
    pagina_q = Risposta(f'<table><tbody>{righe_q}</tbody></table>')
    class Feed(Risposta):
        def __init__(self, dati, codice=200):
            super().__init__('', dati)
            self.status_code = codice
    feed = Feed([{'RoundNumber': 1 + k // 10, 'HomeTeam': 'Hellas Verona', 'AwayTeam': 'Inter Milan',
                  'HomeTeamScore': 1, 'AwayTeamScore': 2} for k in range(380)])
    def finto_tutto(url, *a, **k):
        chieste_s.append(url)
        if 'quotazioni-fantacalcio' in url:
            return pagina_q
        if 'fixturedownload' in url:
            return feed if '2021' in url else Feed(None, 404)
        return pagina_storico(250)
    sto.aggiorna.requests.get = finto_tutto
    sto.scarica(['2021-22', '2015-16'], cartella=cartella, dormi=lambda s: None)
    d = sto.leggi('2021-22', cartella)
    verifica('quotazioni della stagione per Id: iniziale, finale, ruolo',
             d['quotazioni'].get('7001') == [11, 12, 'D'] and len(d['quotazioni']) == 450, d['quotazioni'].get('7001'))
    verifica('calendario con i nomi di fantacalcio.it (Hellas Verona, Inter Milan)',
             d['partite'][0] == [1, 'Verona', 'Inter', 1, 2] and len(d['partite']) == 380, d['partite'][0])
    verifica('stagione senza calendario (404): segnata vuota', sto.leggi('2015-16', cartella)['partite'] == [])
    chieste_s.clear()
    sto.scarica(['2021-22', '2015-16'], cartella=cartella, dormi=lambda s: None)
    verifica('la seconda volta quotazioni e calendario non si richiedono',
             not any('quotazioni' in u or 'fixturedownload' in u for u in chieste_s), len(chieste_s))

print('\n7. Calendario')
base_finta = {'me': 'BURKINA FASO', 'g': [
    [1, 5, '2026-09-20', [['Squadra Uno', 'Squadra Due'], ['Squadra Tre', 'BURKINA FASO']]],
    [2, 6, '2026-10-11', [['BURKINA FASO', 'Squadra Quattro']]],
    [3, 7, '2026-10-14', [['Squadra Cinque', 'BURKINA FASO']]],     # turno infrasettimanale
    [4, 8, '2026-10-18', [['BURKINA FASO', 'Squadra Sei']]]]}
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
verifica('titolo senza il nome dell\'avversario (il file è pubblico)', 'SUMMARY:Schiera la formazione · G1' in righe
         and 'Squadra' not in testo)
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

print('\n8. Listone: giocatori arrivati dopo l\'asta')
def quotazioni_con_squadra(righe):
    tr = ''.join(f'<tr><td></td><td></td><td></td><th><a href="https://www.fantacalcio.it/serie-a/squadre/{sq}/{n.lower()}/{i}">{n}</a></th><td>X</td><td>5</td></tr>'
                 for i, n, sq in righe)
    return Risposta(f'<table><thead><tr><th>Calciatore</th><th></th><th></th><th></th><th>Sq</th><th>QI</th></tr></thead><tbody>{tr}</tbody></table>')
LISTONE_FINTO = [{'id': 1, 'nome': 'Svilar', 'squadra': 'Roma'}, {'id': 2, 'nome': 'Darmian', 'squadra': 'Inter'},
                 {'id': 9, 'nome': 'Altro', 'squadra': 'Udinese'}, {'id': 8, 'nome': 'Altro2', 'squadra': 'Milan'}]
servi({mod.URL_QUOTAZIONI: quotazioni_con_squadra([(1, 'Svilar', 'roma'), (2, 'Darmian', 'bologna'), (3, 'Alaba', 'udinese'),
                                                    (4, 'Leao *', 'milan'), (5, 'Ignoto', 'squadra-che-non-esiste')])})
nuovi = mod.listone_nuovi(LISTONE_FINTO)
verifica('i nuovi entrano con nome senza asterisco e squadra dal link',
         nuovi == [{'id': 3, 'nome': 'Alaba', 'squadra': 'Udinese'}, {'id': 4, 'nome': 'Leao', 'squadra': 'Milan'}], nuovi)
verifica("chi e' gia' nel listone non cambia (Darmian resta com'e': gli Id non si toccano)", all(p['id'] != 2 for p in nuovi))
verifica('squadra del link sconosciuta: non si aggiunge, non si inventa', all(p['id'] != 5 for p in nuovi))

print('\n9. Giro leggero delle probabili (finestra della giornata)')
GF = {'6': {'ufficiale': True, 'inizio': '2026-10-10T13:00:00+00:00', 'fine': '2026-10-12T18:45:00+00:00'},
      '7': {'ufficiale': True, 'inizio': '2026-10-16T18:45:00+00:00', 'fine': '2026-10-19T18:45:00+00:00'},
      '8': {'ufficiale': True, 'inizio': '2026-10-21T18:45:00+00:00', 'fine': '2026-10-21T21:00:00+00:00'}}
def alle(s): return datetime.fromisoformat(s)
verifica('36 ore prima del primo calcio: finestra aperta', mod.giornata_in_finestra(GF, alle('2026-10-09T01:30:00+00:00')) == 6)
verifica('37 ore prima: ancora chiusa', mod.giornata_in_finestra(GF, alle('2026-10-09T00:30:00+00:00')) is None)
verifica("un'ora dopo il primo calcio: ancora aperta", mod.giornata_in_finestra(GF, alle('2026-10-10T13:50:00+00:00')) == 6)
verifica('dopo la scadenza, durante la giornata: chiusa', mod.giornata_in_finestra(GF, alle('2026-10-11T12:00:00+00:00')) is None)
verifica('giornata finita: si passa alla successiva, ancora lontana', mod.giornata_in_finestra(GF, alle('2026-10-13T12:00:00+00:00')) is None)
verifica('vigilia della successiva: aperta', mod.giornata_in_finestra(GF, alle('2026-10-15T12:00:00+00:00')) == 7)
verifica('turno infrasettimanale: finestra della giornata 8', mod.giornata_in_finestra(GF, alle('2026-10-20T12:00:00+00:00')) == 8)
verifica('senza orari ufficiali: nessuna finestra', mod.giornata_in_finestra({'9': {'ufficiale': False}}, alle('2026-10-15T12:00:00+00:00')) is None)
verifica('voti mancanti: giornata finita da 6 ore senza voti', mod.voti_mancanti(GF, {'6': {}}, alle('2026-10-20T00:45:00+00:00')) == ['7'])
verifica('voti mancanti: meno di 6 ore dopo, ancora no', mod.voti_mancanti(GF, {'6': {}}, alle('2026-10-20T00:30:00+00:00')) == [])
verifica('voti mancanti: gia\' salvati, niente', mod.voti_mancanti(GF, {'6': {}, '7': {}}, alle('2026-10-20T12:00:00+00:00')) == [])
verifica('voti mancanti: oltre 3 giorni non si inseguono (resta il giro completo)', mod.voti_mancanti(GF, {}, alle('2026-10-20T12:00:00+00:00')) == ['7'])
verifica('voti mancanti: senza orario ufficiale, niente', mod.voti_mancanti({'9': {'ufficiale': False, 'fine': '2026-10-01T18:45:00+00:00'}}, {}, alle('2026-10-02T12:00:00+00:00')) == [])
verifica("l'ora di aggiornamento da sola non e' un cambiamento",
         mod.senza_ora({'aggiornato': 'a', 'x': 1}) == mod.senza_ora({'aggiornato': 'b', 'x': 1}) != mod.senza_ora({'aggiornato': 'a', 'x': 2}))

print('\n10. Quote (scripts/quote.py): gol attesi, aggancio, mai meno dati')
spq = importlib.util.spec_from_file_location('quote', os.path.join(REPO, 'scripts', 'quote.py'))
qt = importlib.util.module_from_spec(spq)
spq.loader.exec_module(qt)
pari = qt.lambda_da_quote(2.6, 3.4, 2.6, 1.9, 1.9)
verifica('quote simmetriche: gol attesi uguali', pari and abs(pari[0] - pari[1]) < 1e-3, pari)
fav = qt.lambda_da_quote(1.5, 4.2, 6.5, 1.8, 2.0)
verifica('favorita in casa: piu\' gol attesi in casa che fuori', fav and fav[0] > fav[1] > 0, fav)
verifica('totale coerente col piu\'/meno 2,5 (quota 1,9/1,9 = totale attorno a 2,5)', 2.0 < sum(pari) < 3.2, sum(pari))
verifica('manca una quota: nessun valore inventato', qt.lambda_da_quote(2.0, 3.0, None, 1.9, 1.9) is None)
CSV_Q = ('Div,HomeTeam,AwayTeam,FTHG,AvgH,AvgD,AvgA,Avg>2.5,Avg<2.5\n'
         'I1,Spal,Roma,1,2.6,3.4,2.6,1.9,1.9\n'
         'E0,Altra,Altra2,0,2.0,3.0,3.5,1.9,1.9\n'
         'I1,Milan,Inter,,2.0,3.3,3.8,1.9,1.9\n')
righe_q = qt.leggi_csv(CSV_Q)
verifica('solo il campionato giusto; Spal diventa SPAL; giocata se c\'e\' il risultato',
         [(c, t, g) for c, t, _, g in righe_q] == [('SPAL', 'Roma', True), ('Milan', 'Inter', False)], righe_q)
verifica('senza colonne delle quote: lambda None, mai le «C» (chiusura)',
         qt.leggi_csv('Div,HomeTeam,AwayTeam,FTHG,AvgCH,AvgCD,AvgCA\nI1,A,B,1,2,3,4\n')[0][2] is None)
ORARI_Q = {'giornate': {'1': {'partite': [['SPAL', 'Roma', 'x']]}, '2': {'partite': [['Milan', 'Inter', 'x']]}}}
gq, senza_g, senza_q = qt.aggancia(righe_q + [('Fantasma', 'Roma', (1.0, 1.0), False)], ORARI_Q)
verifica('aggancio per coppia (casa, trasferta) alla giornata di orari.json; sconosciute segnalate',
         sorted(gq) == ['1', '2'] and gq['1'][0][:2] == ['SPAL', 'Roma'] and senza_g == [('Fantasma', 'Roma')], (gq, senza_g))
verifica('plausibile: lambda fuori da 0,2-5 o file vuoto = no', qt.plausibile({'1': [['a', 'b', 1.2, 1.1]]})
         and not qt.plausibile({'1': [['a', 'b', 9.0, 1.1]]}) and not qt.plausibile({}))
vecchio_q = {'aggiornato': 'a', 'giornate': {'1': [['A', 'B', 1.2, 1.0, 'I1'], ['C', 'D', 1.0, 1.0, 'I1']],
                                                 '2': [['E', 'F', 1.1, 1.1, 'fixtures']]}}
nuovo_q = {'aggiornato': 'b', 'giornate': {'2': [['E', 'F', 1.3, 0.9, 'I1']], '3': [['G', 'H', 1.0, 1.0, 'fixtures']]}}
unito = qt.unisci(vecchio_q, nuovo_q)
verifica('unisci: le partite non citate restano (i dati non si svuotano)',
         ['A', 'B'] in [p[:2] for p in unito['giornate']['1']] and ['C', 'D'] in [p[:2] for p in unito['giornate']['1']])
verifica('unisci: stessa coppia = vince la nuova; nuove giornate aggiunte; data nuova',
         unito['giornate']['2'] == [['E', 'F', 1.3, 0.9, 'I1']] and '3' in unito['giornate'] and unito['aggiornato'] == 'b')
with tempfile.TemporaryDirectory() as td:
    pq = os.path.join(td, 'quote.json')
    qt.scrivi(pq, vecchio_q)
    qt.scrivi(pq, {'aggiornato': 'c', 'giornate': {'3': [['G', 'H', 1.0, 1.0, 'fixtures']]}})
    dopo = json.load(open(pq, encoding='utf-8'))
    verifica('una corsa col solo fixtures non cancella le partite giocate', sum(len(v) for v in dopo['giornate'].values()) == 4, dopo)
    qt.scrivi(pq, {'aggiornato': 'd', 'giornate': {'1': [['A', 'B', 99.0, 1.0, 'I1']]}})
    verifica('risultato non plausibile: il file di prima resta', json.load(open(pq, encoding='utf-8')) == dopo)
    ad = datetime(2026, 10, 13, 15, 30, tzinfo=timezone.utc)
    f1 = qt.salva_copia('uno', 'I1', td, ad)
    f2 = qt.salva_copia('due', 'I1', td, ad)
    verifica('copie dei CSV con data e ora nel nome, mai sovrascritte',
             f1 != f2 and '2026-10-13' in os.path.basename(f1) and open(f1).read() == 'uno' and open(f2).read() == 'due', (f1, f2))

ORA = datetime(2026, 10, 14, 17, 0, tzinfo=timezone.utc)
OR_P = {'giornate': {'6': {'partite': [['a', 'b', '2026-10-10T13:00:00+00:00']]},
                     '7': {'partite': [['A', 'B', '2026-10-16T18:45:00+00:00'], ['C', 'D', '2026-10-19T18:45:00+00:00']]},
                     '8': {'partite': [['E', 'F', '2026-10-21T18:45:00+00:00'], ['G', 'H', None]]}}}
verifica('finestra: una partita entro 72 ore = la giornata si scarica', qt.in_finestra(OR_P, ORA) == ['7'])
verifica("finestra: l'ultima partita di lunedi' conta ancora (la giornata e' gia' iniziata)",
         qt.in_finestra(OR_P, datetime(2026, 10, 18, 17, 0, tzinfo=timezone.utc)) == ['7'])
verifica('finestra: partite tutte lontane (oltre 72 ore) = niente', qt.in_finestra(OR_P, datetime(2026, 10, 11, 17, 0, tzinfo=timezone.utc)) == [])
verifica("finestra: tutto giocato, o orario mancante/non valido = niente, senza errori",
         qt.in_finestra(OR_P, datetime(2026, 11, 1, tzinfo=timezone.utc)) == [] and qt.in_finestra({}, ORA) == [])
verifica('ora italiana: il nome dei file sullo stesso orologio del PC anche da un server in UTC',
         qt.ora_italiana(datetime(2026, 10, 14, 17, 0, tzinfo=timezone.utc)).strftime('%H') == '19')
with tempfile.TemporaryDirectory() as td:
    ad = datetime(2026, 10, 14, 17, 0, tzinfo=timezone.utc)
    f1 = qt.salva_copia('uno', 'fixtures', td, ad)
    f2 = qt.salva_copia('uno', 'fixtures', td, ad + timedelta(hours=3))
    f3 = qt.salva_copia('due', 'fixtures', td, ad + timedelta(hours=6))
    verifica('copia identica all ultima: niente di nuovo; contenuto cambiato: file nuovo, il vecchio resta',
             f1 == f2 and f3 != f1 and open(f1).read() == 'uno' and open(f3).read() == 'due' and '_1900' in f1, (f1, f3))

print('\nNews recenti per il fascicolo (22/10/2026)')
with tempfile.TemporaryDirectory() as td:
    def giorno(data, righe):
        p = os.path.join(td, data[:4], data[5:7]); os.makedirs(p, exist_ok=True)
        with open(os.path.join(p, data[8:] + '.jsonl'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(json.dumps(r) for r in righe) + '\nnon json\n')
    L = 'https://www.fantacalcio.it/news/calcio-italia/'
    giorno('2026-10-22', [{'id': 1, 'data': '2026-10-22', 'titolo': 'T', 'sommario': 'S', 'link': L + 'a-1', 'squadre': ['Roma'],
                           'giocatori': [{'id': 5841, 'nome': 'Svilar', 'squadra': 'Roma'}], 'tag': ['infortunio']},
                          {'id': 2, 'data': '2026-10-22', 'titolo': 'T', 'sommario': 'S', 'link': L + 'b-2', 'squadre': ['Roma'], 'giocatori': [], 'tag': ['conferenza']},
                          {'id': 3, 'data': '2026-10-22', 'link': 'https://altro.it/x', 'squadre': ['Roma'], 'giocatori': [], 'tag': []}])
    giorno('2026-10-20', [{'id': 4, 'data': '2026-10-20', 'link': L + 'c-4', 'squadre': ['Roma'],
                           'giocatori': [{'id': 5841, 'nome': 'Svilar', 'squadra': 'Roma'}], 'tag': []}])
    giorno('2026-10-15', [{'id': 5, 'data': '2026-10-15', 'link': L + 'd-5', 'squadre': ['Roma'],
                           'giocatori': [{'id': 5841, 'nome': 'Svilar', 'squadra': 'Roma'}], 'tag': []}])
    nr = mod.news_recenti(td, datetime(2026, 10, 22, 12, tzinfo=timezone.utc))
    verifica('news del giocatore: solo gli ultimi 3 giorni, la più recente prima',
             nr['giocatori'].get('5841') == [['2026-10-22', ['infortunio'], L + 'a-1'], ['2026-10-20', [], L + 'c-4']], nr['giocatori'])
    verifica('news senza giocatori vanno alla squadra; link di altri siti scartati',
             nr['squadre'] == {'Roma': [['2026-10-22', ['conferenza'], L + 'b-2']]}, nr['squadre'])
    verifica('nessun titolo né sommario nel file pubblico: solo [data, tag, link]',
             all(len(v) == 3 and isinstance(v[1], list) and v[2].startswith(L) for d in (nr['giocatori'], nr['squadre']) for x in d.values() for v in x), nr)
    verifica('senza archivio: nessun errore, nessun file', mod.solo_news(os.path.join(td, 'manca')) == 0)

print(f'\n{esiti - falliti}/{esiti} verifiche superate')
sys.exit(1 if falliti else 0)
