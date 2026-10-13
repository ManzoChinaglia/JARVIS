"""Prova di scripts/modello.py (B2, il fantavoto atteso): prima su stagioni finte costruite
apposta, dove si sa cosa il modello deve ritrovare; poi sui dati veri di dati/storico/.

Uso: python prove/modello.py
"""
import importlib.util, json, os, random, sys, tempfile, time

REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location('modello', os.path.join(REPO, 'scripts', 'modello.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

esiti = falliti = 0
def verifica(nome, cond, dettaglio=''):
    global esiti, falliti
    esiti += 1
    falliti += not cond
    print(('  ok   ' if cond else '  NO   ') + nome + (f'  ->  {dettaglio}' if dettaglio != '' else ''))


print('\n1. Stagioni finte: il modello ritrova quello che ci abbiamo messo')
random.seed(7)
SQUADRE = ['Alfa', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta']
FORMA = 'PDDDDCCCAAA'
talento = {}
def stagione_finta(nome):
    """8 squadre da 11, 38 giornate. Fantavoto = 6 + talento + 0,6 in casa + rumore;
    voto = 6 + 0,3·talento + 0,2 in casa + rumore. La quotazione segue il talento."""
    giornate, partite, quot = {}, [], {}
    for k, sq in enumerate(SQUADRE):
        for j, ruolo in enumerate(FORMA):
            pid = str(1000 + 20 * k + j)
            talento.setdefault(pid, random.gauss(0, 0.5))
            quot[pid] = [round(15 + 10 * talento[pid]), 15, ruolo]
    for n in range(1, 39):
        giro = SQUADRE[n % 8:] + SQUADRE[:n % 8]
        g = {}
        for c in range(4):
            casa, fuori = (giro[c], giro[7 - c]) if n % 2 else (giro[7 - c], giro[c])
            partite.append([n, casa, fuori, random.randint(0, 3), random.randint(0, 3)])
            for sq, in_casa in ((casa, 1), (fuori, 0)):
                k = SQUADRE.index(sq)
                for j, ruolo in enumerate(FORMA):
                    pid = str(1000 + 20 * k + j)
                    t = talento[pid]
                    g[pid] = [6 + 0.3 * t + 0.2 * in_casa + random.gauss(0, 0.3), 6 + t + 0.6 * in_casa + random.gauss(0, 0.8),
                              ruolo, sq] + [0] * 8
        giornate[str(n)] = g
    return {'stagione': nome, 'giornate': giornate, 'partite': partite, 'quotazioni': quot}
finte = [stagione_finta(s) for s in ('2019-20', '2020-21', '2021-22')]
righe, storie = mod.righe_e_storie(finte)
verifica('una riga per ogni presenza con partita abbinata', len(righe) == 3 * 38 * 88, len(righe))
fv = mod.addestra(righe, 'fv')
casa = {r: fv[r]['coef'][mod.VOCI.index('in casa')] for r in mod.RUOLI}
verifica('ritrova l\'effetto «in casa» del fantavoto (0,6)', all(abs(v - 0.6) < 0.25 for v in casa.values()),
         {r: round(v, 2) for r, v in casa.items()})
voto = mod.addestra(righe, 'voto')
casa_v = {r: voto[r]['coef'][mod.VOCI.index('in casa')] for r in mod.RUOLI}
verifica('e quello del voto (0,2)', all(abs(v - 0.2) < 0.12 for v in casa_v.values()), {r: round(v, 2) for r, v in casa_v.items()})
verifica('la storia del giocatore conta (il talento resta da una stagione all\'altra)',
         all(fv[r]['coef'][mod.VOCI.index('storia')] > 0.2 for r in 'DCA'),
         {r: round(fv[r]['coef'][mod.VOCI.index('storia')], 2) for r in mod.RUOLI})
# niente sbirciate: il voto di una partita non entra mai nelle voci di quella stessa partita
cambiata = json.loads(json.dumps(finte))
cambiata[1]['giornate']['20']['1045'][1] = 30.0
righe2, _ = mod.righe_e_storie(cambiata)
diverse = [k for k, (a, b) in enumerate(zip(righe, righe2)) if a[2] != b[2]]
k = diverse[0] if len(diverse) == 1 else None
verifica('niente sbirciate: cambia il fantavoto di una partita, le voci di quella partita restano uguali',
         k is not None and righe[k][4] == righe2[k][4] and righe[:k] == righe2[:k], diverse[:3])
verifica('e cambiano solo le voci delle partite dopo', k is not None and any(a[4] != b[4] for a, b in zip(righe[k + 1:], righe2[k + 1:])))
rose = [(str(1000 + 20 * k + j), r) for k in range(8) for j, r in enumerate(FORMA)]
a = mod.costruisci(finte, {}, rose, {}, {}, adesso=mod.datetime(2026, 9, 15, tzinfo=mod.timezone.utc))
b = mod.costruisci(finte, {}, rose, {}, {}, adesso=mod.datetime(2026, 9, 15, tzinfo=mod.timezone.utc))
verifica('stessi dati, stesso modello', json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True))
verifica('si verifica da solo sulle ultime due stagioni', a['addestramento']['verifica_su'] == ['2020-21', '2021-22'],
         a['addestramento']['verifica_su'])
verifica('un giocatore per ogni membro delle rose, con storia, medie e quotazione', len(a['giocatori']) == 88
         and a['giocatori']['1001'][0] > 0 and a['giocatori']['1001'][5] == 3 * 38, a['giocatori']['1001'])
with tempfile.TemporaryDirectory() as cartella:
    p = os.path.join(cartella, 'modello.json')
    verifica('troppe poche righe: non si scrive (i dati non si svuotano mai)', not mod.scrivi(p, a) and not os.path.exists(p))
verifica('il ballo del giocatore conta di più dove si conserva tra le stagioni', mod.n0(0.5) < mod.n0(0.25) < mod.n0(0.05) <= 1000
         and mod.n0(None) == 1000, [mod.n0(0.5), mod.n0(0.25), mod.n0(0.05)])

print('\n2. Dati veri (dati/storico/)')
stagioni = mod.stagioni_storico(os.path.join(REPO, 'dati', 'storico'))
if not stagioni or not any(s.get('partite') for s in stagioni):
    print('  --   storico senza calendari: prova saltata')
else:
    leggi = lambda n: json.load(open(os.path.join(REPO, 'dati', n), encoding='utf-8')) if os.path.exists(os.path.join(REPO, 'dati', n)) else {}
    base, st = leggi('base.json'), leggi('statistiche.json')
    rose_vere = [(str(x[0]), x[3]) for x in base['p']]
    t0 = time.time()
    m = mod.costruisci(stagioni, leggi('voti.json').get('giornate') or {}, rose_vere, st.get('iniziali') or {},
                       {k: v[3] for k, v in (st.get('giocatori') or {}).items() if len(v) > 3 and v[3]})
    durata = time.time() - t0
    verifica('abbastanza righe e un risultato plausibile', mod.plausibile(m), m['addestramento']['righe'])
    fv_v = m['verifica']['fantavoto']
    verifica('fantavoto: in verifica il modello ordina meglio del calcolo di prima, in tutti i ruoli',
             all(fv_v[r]['modello']['corr'] > fv_v[r]['prima']['corr'] for r in mod.RUOLI),
             {r: (fv_v[r]['modello']['corr'], fv_v[r]['prima']['corr']) for r in mod.RUOLI})
    verifica('e sbaglia di meno', all(fv_v[r]['modello']['rmse'] < fv_v[r]['prima']['rmse'] for r in mod.RUOLI))
    verifica('il modello si usa solo dove batte il calcolo di prima', all(
        m[n][r]['usa'] == (m['verifica'][n][r]['modello']['corr'] >= m['verifica'][n][r]['prima']['corr'])
        for n in ('fantavoto', 'voto') for r in mod.RUOLI), {n: [r for r in mod.RUOLI if not m[n][r]['usa']] for n in ('fantavoto', 'voto')})
    verifica('ogni giocatore delle rose ha la sua riga', set(m['giocatori']) == {p for p, _ in rose_vere}, len(m['giocatori']))
    medie = [v[1] for v in m['giocatori'].values() if v[5] > 0]
    verifica('medie di fantavoto credibili per chi ha storia', medie and all(2 < x < 12 for x in medie), (min(medie), max(medie)))
    verifica('incertezza credibile per ruolo', all(0.3 < m[n][r]['sd'] < 3 for n in ('fantavoto', 'voto') for r in mod.RUOLI),
             {r: m['fantavoto'][r]['sd'] for r in mod.RUOLI})
    verifica('veloce: si può rifare a ogni giro automatico', durata < 60, f'{durata:.1f} s')

print('\n4. Due serie: senza quote e con quote (passo 4 del cervello calcistico)')
quote_finte = {st['stagione']: {(h, aw): (1.5, 1.0) for _, h, aw, _, _ in st['partite']} for st in finte}
senza_q = mod.costruisci(finte, {}, rose, {}, {}, adesso=mod.datetime(2026, 9, 15, tzinfo=mod.timezone.utc))
con_q = mod.costruisci(finte, {}, rose, {}, {}, adesso=mod.datetime(2026, 9, 15, tzinfo=mod.timezone.utc), quote=quote_finte)
verifica('senza quote: nessuna serie con quote, e il resto identico a prima',
         'fantavoto_quote' not in senza_q and 'verifica_quote' not in senza_q and all(con_q[k] == senza_q[k] for k in ('fantavoto', 'voto', 'verifica', 'giocatori')))
verifica('con quote: due serie, stesse voci e stesso ordine', all(len(con_q[n + '_quote'][r]['coef']) == len(mod.VOCI) for n in ('fantavoto', 'voto') for r in mod.RUOLI))
verifica("con quote l'avversario vale 0 (ingresso nullo: lo fanno i gol attesi)",
         all(con_q[n + '_quote'][r]['coef'][mod.VOCI.index('avversario')] == 0 for n in ('fantavoto', 'voto') for r in mod.RUOLI))
verifica('righe con quote contate e verifica a coppie sulle stesse partite',
         con_q['addestramento']['righe_quote'] == con_q['addestramento']['righe'] and con_q['verifica_quote']['fantavoto']['D']['righe'] > 0)
verifica("un ruolo usa le quote solo se in verifica ordina meglio della serie senza quote", all(
    con_q[n + '_quote'][r]['usa'] == (con_q['verifica_quote'][n][r]['con_quote']['corr'] >= con_q['verifica_quote'][n][r]['senza_quote']['corr'])
    for n in ('fantavoto', 'voto') for r in mod.RUOLI))
lega_q = {'casa': [10, 13, 11], 'fuori': [10, 11.5, 12.8]}
att, dif = mod.contesto_quote((1.5, 1.0), lega_q, True)
verifica('contesto_quote in casa: gol attesi propri meno media casa; media subiti meno gol attesi dell\'avversario',
         abs(att - 0.2) < 1e-9 and abs(dif - 0.1) < 1e-9, (att, dif))
att, dif = mod.contesto_quote((1.5, 1.0), lega_q, False)
verifica('contesto_quote fuori casa: gli stessi gol attesi letti dalla parte della trasferta, con la media fuori',
         abs(att - (-0.15)) < 1e-9 and abs(dif - (-0.22)) < 1e-9, (att, dif))
verifica("senza il file dello storico delle quote la serie non si addestra e non c'e' errore", mod.quote_storico('/non/esiste.gz') == {})

print(f'\n{esiti - falliti}/{esiti} verifiche superate')
sys.exit(1 if falliti else 0)
