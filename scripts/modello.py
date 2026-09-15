"""Il modello del fantavoto atteso (CLAUDE.md, «Da fare: il cervello di Jarvis», B2).

Impara dallo storico dei voti (dati/storico/) quanto contano, ruolo per ruolo, la storia
del giocatore, la sua quotazione, il giocare in casa, l'avversario e la forza della sua
squadra, per il fantavoto e per il voto (che serve al modificatore di difesa). Scrive
dati/modello.json: i coefficienti e, per ogni giocatore delle rose, la parte che dipende
solo da lui. L'app ci aggiunge la partita (casa, avversario, squadra) e la titolarità.

Onestà del modello, verificata e da tenere:
- ogni cosa che vede di una partita era nota PRIMA della partita: la storia del
  giocatore fino alla giornata prima, la quotazione iniziale della stagione (non quella
  finale, che si muove col rendimento), la forza delle squadre misurata come fa l'app
  (casa e fuori separati, stagione in corso mescolata con quella prima fino alla decima
  partita, neopromosse come le retrocesse);
- si verifica da solo sulle ultime due stagioni tenute da parte, contro un'imitazione del
  calcolo di prima (fantamedia avvicinata alla quotazione, più PESI per l'avversario); i
  numeri finiscono nel file, in «verifica»;
- un modello lineare, così l'app può dire perché («in casa +0,2, avversario −0,3»).

Gira nel giro automatico dopo aggiorna.py: Python puro, nessuna libreria, pochi secondi.
Il file si riscrive solo se cambia qualcosa, e solo se il risultato è plausibile.

Uso: python scripts/modello.py              addestra e scrive dati/modello.json
     python scripts/modello.py --verifica   solo i numeri, non scrive niente
"""
import glob, gzip, json, math, os, sys
from collections import defaultdict
from datetime import datetime, timezone

QUI = os.path.dirname(os.path.abspath(__file__))
DATI = os.path.join(os.path.dirname(QUI), 'dati')
RUOLI = 'PDCA'
K = 5              # presenze «di fiducia»: con meno, conta di più la quotazione (come nell'app)
DECAD = 0.97       # memoria della storia del giocatore: circa le ultime 33 presenze
LAMBDA = 10.0      # ridge: tiene piccoli i coefficienti delle voci che dicono poco
PESI_APP = {'P': 1.0, 'D': 0.8, 'C': 0.4, 'A': 0.8}    # l'avversario nel calcolo di prima
PRIOR_VOTO_APP = 4                                        # votoAtteso di prima
VOCI = ['costante', 'storia', 'senza storia', 'quotazione', 'in casa', 'avversario',
        'attacco squadra', 'difesa squadra']
MINIMO_RIGHE = 20000
VERSIONE = 1
# senza la stagione prima nel feed (per il 2017-18 manca il 2016-17): medie tipiche della
# Serie A in casa e fuori, [partite, gol fatti, gol subiti] per partita
NEUTRO = {'casa': [1.0, 1.28, 1.15], 'fuori': [1.0, 1.15, 1.28]}


class Storia:
    """La storia di un giocatore: medie pesate (le presenze recenti contano di più) di
    fantavoto e voto, e quanto ballano."""
    __slots__ = ('W', 'Sf', 'Sv', 'Qf', 'Qv', 'n')

    def __init__(self):
        self.W = self.Sf = self.Sv = self.Qf = self.Qv = 0.0
        self.n = 0

    def aggiungi(self, voto, fv):
        d = DECAD
        self.W = d * self.W + 1
        self.Sf, self.Sv = d * self.Sf + fv, d * self.Sv + voto
        self.Qf, self.Qv = d * self.Qf + fv * fv, d * self.Qv + voto * voto
        self.n += 1

    def media(self, quale):
        return (self.Sf if quale == 'fv' else self.Sv) / self.W if self.W else None

    def ballo(self, quale):
        if self.n < 5:
            return None
        m = self.media(quale)
        return math.sqrt(max(0.0, (self.Qf if quale == 'fv' else self.Qv) / self.W - m * m))


def voci(storia, quale, qi, casa, avv, att, dif):
    """Le voci del modello, nell'ordine di VOCI. La storia pesa tanto più quante più
    presenze ha (lam); il resto lo fa la quotazione."""
    lam = storia.W / (storia.W + K) if storia else 0.0
    m = storia.media(quale) if storia else 0.0
    return [1.0, lam * m, 1.0 - lam, (1.0 - lam) * qi, float(casa), avv, att, dif]


# ---- forza delle squadre, come perPartita e forzaSa in index.html ----
def tabella(partite):
    """[partite, gol fatti, gol subiti] per squadra, in casa e fuori"""
    t = {}
    for _, h, a, gh, ga in partite:
        if gh is None or ga is None:
            continue
        for sq, campo, f, s in ((h, 'casa', gh, ga), (a, 'fuori', ga, gh)):
            x = t.setdefault(sq, {'casa': [0, 0, 0], 'fuori': [0, 0, 0]})[campo]
            x[0] += 1; x[1] += f; x[2] += s
    return t


def precedente(partite_prec, squadre):
    """La stagione prima di ogni squadra (neopromosse: la media delle retrocesse, come
    fa aggiorna.py) e la media del campionato, in casa e fuori."""
    if not partite_prec:
        return {sq: {c: v[:] for c, v in NEUTRO.items()} for sq in squadre}, {c: v[:] for c, v in NEUTRO.items()}
    t = tabella(partite_prec)
    lega = {c: [sum(v[c][k] for v in t.values()) for k in range(3)] for c in ('casa', 'fuori')}
    retro = [sq for sq in t if sq not in squadre]
    out = {}
    for sq in squadre:
        if sq in t:
            out[sq] = t[sq]
        else:
            fonte = retro or list(t)
            out[sq] = {c: [sum(t[r][c][k] for r in fonte) / len(fonte) for k in range(3)] for c in ('casa', 'fuori')}
    return out, lega


def per_partita(ora, prec, sq, campo, i):
    vuota = {'casa': [0, 0, 0], 'fuori': [0, 0, 0]}
    o = ora.get(sq, vuota)
    a, b = o[campo], prec.get(sq, NEUTRO)[campo]
    w = min(1.0, (o['casa'][0] + o['fuori'][0]) / 10) if a[0] else 0.0
    return w * (a[i] / a[0] if a[0] else 0.0) + (1 - w) * (b[i] / b[0])


def contesto(ora, prec, lega, sq, avv, casa, ruolo):
    """avversario (come forzaSa: positivo = favorevole), attacco e difesa della propria
    squadra, tutti come differenza dalla media del campionato prima, nel campo giusto"""
    c_avv = 'fuori' if casa else 'casa'
    dietro = ruolo in 'PD'
    i = 1 if dietro else 2
    media = lega[c_avv][i] / lega[c_avv][0]
    val = per_partita(ora, prec, avv, c_avv, i)
    d_avv = media - val if dietro else val - media
    c_mio = 'casa' if casa else 'fuori'
    att = per_partita(ora, prec, sq, c_mio, 1) - lega[c_mio][1] / lega[c_mio][0]
    dif = lega[c_mio][2] / lega[c_mio][0] - per_partita(ora, prec, sq, c_mio, 2)
    return d_avv, att, dif


def mediana(v):
    v = sorted(v)
    return v[len(v) // 2] if v else None


# ---- dalle stagioni alle righe di addestramento ----
def righe_e_storie(stagioni):
    """Una riga per ogni presenza con voto in una partita abbinata al calendario:
    (stagione, ruolo, fantavoto, voto, voci fv, voci voto, parti per il calcolo di prima).
    Le storie dei giocatori si aggiornano DOPO ogni giornata, mai prima."""
    storie, righe = {}, []
    for k, st in enumerate(stagioni):
        s, partite = st['stagione'], st.get('partite') or []
        quot = st.get('quotazioni') or {}
        qi_ruolo = {r: mediana([q[0] for q in quot.values() if q[2] == r]) or 10 for r in RUOLI}
        if partite:
            turno = defaultdict(list)
            for g, h, a, _, _ in partite:
                turno[(h, g)].append((a, 1)); turno[(a, g)].append((h, 0))
            squadre = {h for _, h, _, _, _ in partite} | {a for _, _, a, _, _ in partite}
            prec, lega = precedente(stagioni[k - 1].get('partite') if k else None, squadre)
            ora = {}
        stag = defaultdict(lambda: [0, 0.0, 0.0])     # presenze, somma fv, somma voto nella stagione
        for n in range(1, 39):
            g = st['giornate'].get(str(n), {})
            if partite:
                for i, r in g.items():
                    voto, fv, ruolo, sq = r[0], r[1], r[2], r[3]
                    m = turno.get((sq, n), []) if ruolo in RUOLI else []
                    if len(m) != 1:
                        continue                  # giornata del feed non abbinabile (rinvii): si scarta
                    avv, casa = m[0]
                    d_avv, att, dif = contesto(ora, prec, lega, sq, avv, casa, ruolo)
                    q = quot.get(i)
                    qi = q[0] if q else qi_ruolo[ruolo]
                    h = storie.get(i)
                    ns, sf, sv = stag[i]
                    righe.append((s, ruolo, fv, voto, voci(h, 'fv', qi, casa, d_avv, att, dif),
                                  voci(h, 'voto', qi, casa, d_avv, att, dif),
                                  (ns, sf / ns if ns else 0.0, sv / ns if ns else 0.0, qi, d_avv)))
            for i, r in g.items():
                if r[2] not in RUOLI:
                    continue
                storie.setdefault(i, Storia()).aggiungi(r[0], r[1])
                x = stag[i]; x[0] += 1; x[1] += r[1]; x[2] += r[0]
            if partite:
                for gg, h, a, gh, ga in partite:
                    if gg != n or gh is None or ga is None:
                        continue
                    for sq, campo, f, su in ((h, 'casa', gh, ga), (a, 'fuori', ga, gh)):
                        x = ora.setdefault(sq, {'casa': [0, 0, 0], 'fuori': [0, 0, 0]})[campo]
                        x[0] += 1; x[1] += f; x[2] += su
    return righe, storie


# ---- ridge in Python puro ----
def risolvi(A, b):
    n = len(b)
    M = [A[i][:] + [b[i]] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c and M[c][c]:
                f = M[r][c] / M[c][c]
                M[r] = [M[r][j] - f * M[c][j] for j in range(n + 1)]
    return [M[i][n] / M[i][i] for i in range(n)]


def ridge(X, y, lam=LAMBDA):
    k = len(X[0])
    A = [[0.0] * k for _ in range(k)]
    b = [0.0] * k
    for xi, yi in zip(X, y):
        for a in range(k):
            xa = xi[a]
            b[a] += xa * yi
            Aa = A[a]
            for c in range(a, k):
                Aa[c] += xa * xi[c]
    for a in range(k):
        for c in range(a):
            A[a][c] = A[c][a]
    for a in range(1, k):
        A[a][a] += lam
    return risolvi(A, b)


def prevedi(beta, x):
    return sum(b * v for b, v in zip(beta, x))


def correlazione(p, v):
    n = len(p)
    if n < 2:
        return None
    mp, mv = sum(p) / n, sum(v) / n
    cp = sum((a - mp) * (b - mv) for a, b in zip(p, v))
    d = math.sqrt(sum((a - mp) ** 2 for a in p) * sum((b - mv) ** 2 for b in v))
    return cp / d if d else None


def rmse(p, v):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p, v)) / len(p)) if p else None


def addestra(righe, quale, fuori=()):
    """{ruolo: {'coef', 'sd'}} addestrati sulle righe delle stagioni non in «fuori»"""
    j, t = (4, 2) if quale == 'fv' else (5, 3)
    out = {}
    for r in RUOLI:
        tr = [x for x in righe if x[1] == r and x[0] not in fuori]
        beta = ridge([x[j] for x in tr], [x[t] for x in tr])
        res = [x[t] - prevedi(beta, x[j]) for x in tr]
        out[r] = {'coef': beta, 'sd': math.sqrt(sum(e * e for e in res) / len(res))}
    return out


def verifica(righe, prova):
    """Addestra senza le stagioni «prova» e le usa come esame, contro il calcolo di prima."""
    esito = {'fantavoto': {}, 'voto': {}}
    for quale, nome, j, t in (('fv', 'fantavoto', 4, 2), ('voto', 'voto', 5, 3)):
        mod = addestra(righe, quale, prova)
        for r in RUOLI:
            tr = [x for x in righe if x[1] == r and x[0] not in prova]
            te = [x for x in righe if x[1] == r and x[0] in prova]
            if not te:
                continue
            vero = [x[t] for x in te]
            pm = [prevedi(mod[r]['coef'], x[j]) for x in te]
            if quale == 'fv':
                # la retta fantavoto ~ quotazione, come STIME nell'app, sulle righe di addestramento
                q = [x[6][3] for x in tr]; f = [x[2] for x in tr]
                mq, mf = sum(q) / len(q), sum(f) / len(f)
                sq = sum((a - mq) ** 2 for a in q)
                bq = max(0.0, sum((a - mq) * (b - mf) for a, b in zip(q, f)) / sq) if sq else 0.0
                aq = mf - bq * mq
                pa = [(x[6][0] * x[6][1] + K * (aq + bq * x[6][3])) / (x[6][0] + K) + PESI_APP[r] * x[6][4] for x in te]
            else:
                mv = sum(x[3] for x in tr) / len(tr)
                pa = [(x[6][0] * x[6][2] + PRIOR_VOTO_APP * mv) / (x[6][0] + PRIOR_VOTO_APP) for x in te]
            esito[nome][r] = {'righe': len(te),
                              'modello': {'corr': round(correlazione(pm, vero), 4), 'rmse': round(rmse(pm, vero), 4)},
                              'prima': {'corr': round(correlazione(pa, vero), 4), 'rmse': round(rmse(pa, vero), 4)}}
    return esito


def persistenza(stagioni, fino_a):
    """Quanto il «ballo» di un giocatore (deviazione in una stagione, almeno 15 presenze)
    si ritrova nella stagione dopo: la correlazione, per ruolo, di fantavoto e voto."""
    out = {'fantavoto': {}, 'voto': {}}
    for quale, idx in (('fantavoto', 1), ('voto', 0)):
        sd = {}
        for st in stagioni:
            if st['stagione'] > fino_a:
                continue
            acc = defaultdict(list)
            for g in st['giornate'].values():
                for i, r in g.items():
                    acc[(i, r[2])].append(r[idx])
            for (i, ruolo), v in acc.items():
                if len(v) >= 15:
                    m = sum(v) / len(v)
                    sd[(i, st['stagione'])] = (ruolo, math.sqrt(sum((x - m) ** 2 for x in v) / len(v)))
        nomi = sorted({s for _, s in sd})
        dopo = {a: b for a, b in zip(nomi, nomi[1:])}
        for r in RUOLI:
            coppie = [(v[1], sd[(i, dopo[s])][1]) for (i, s), v in sd.items()
                      if v[0] == r and s in dopo and (i, dopo[s]) in sd]
            out[quale][r] = correlazione([a for a, _ in coppie], [b for _, b in coppie]) if len(coppie) > 10 else None
    return out


def n0(corr):
    """Quante presenze servono perché il ballo del giocatore conti quanto quello del
    ruolo: tante più quanto meno il ballo si conserva da una stagione all'altra."""
    c = max(0.02, corr or 0.0)
    return round(min(1000.0, max(5.0, 25 * (1 - c) / c)), 1)


def costruisci(stagioni, voti_correnti, rose, iniziali, quot_attuali, adesso=None):
    """Tutto il modello, pronto per dati/modello.json."""
    righe, storie = righe_e_storie(stagioni)
    for sa in sorted(voti_correnti, key=int):
        for i, v in voti_correnti[sa].items():
            storie.setdefault(i, Storia()).aggiungi(v[0], v[1])
    con_partite = sorted({x[0] for x in righe})
    prova = con_partite[-2:]
    pers = persistenza(stagioni, con_partite[-1] if con_partite else '')
    modello = {'versione': VERSIONE, 'voci': VOCI, 'K': K,
               'addestramento': {'stagioni': con_partite, 'righe': len(righe), 'verifica_su': prova},
               'verifica': verifica(righe, prova)}
    for quale, nome in (('fv', 'fantavoto'), ('voto', 'voto')):
        mod = addestra(righe, quale)
        # il modello si usa per un ruolo solo se nella verifica ordina i giocatori meglio del
        # calcolo di prima: il 15/09/2026 per il voto dei portieri no (quasi imprevedibile)
        usa = lambda r: bool(modello['verifica'][nome].get(r)) and \
            modello['verifica'][nome][r]['modello']['corr'] >= modello['verifica'][nome][r]['prima']['corr']
        modello[nome] = {r: {'coef': [round(c, 5) for c in mod[r]['coef']], 'sd': round(mod[r]['sd'], 4),
                             'persistenza': None if pers[nome][r] is None else round(pers[nome][r], 3),
                             'n0': n0(pers[nome][r]), 'usa': usa(r)} for r in RUOLI}
    giocatori, qi_ruolo = {}, defaultdict(list)
    for pid, ruolo in rose:
        h = storie.get(pid)
        qi = iniziali.get(pid) or quot_attuali.get(pid) or None
        if qi:
            qi_ruolo[ruolo].append(qi)
        tondo = lambda x: None if x is None else round(x, 3)
        giocatori[pid] = [tondo(h.W) if h else 0, tondo(h.media('fv')) if h else None, tondo(h.media('voto')) if h else None,
                          tondo(h.ballo('fv')) if h else None, tondo(h.ballo('voto')) if h else None, h.n if h else 0, qi]
    modello['giocatori'] = giocatori
    modello['qi_ruolo'] = {r: mediana(qi_ruolo[r]) or 10 for r in RUOLI}
    modello['aggiornato'] = (adesso or datetime.now(timezone.utc)).isoformat(timespec='seconds')
    return modello


def plausibile(m):
    ok = m['addestramento']['righe'] >= MINIMO_RIGHE
    for nome in ('fantavoto', 'voto'):
        for r in RUOLI:
            x = m[nome][r]
            ok = ok and all(math.isfinite(c) for c in x['coef']) and 0.1 < x['sd'] < 5
    return ok and len(m['giocatori']) >= 200


def scrivi(percorso, m):
    """Scrive solo se plausibile e diverso da quello che c'è (a parte la data)."""
    if not plausibile(m):
        print('[modello] risultato non plausibile: resta il file di prima.')
        return False
    try:
        with open(percorso, encoding='utf-8') as f:
            vecchio = json.load(f)
        vecchio.pop('aggiornato', None)
        if vecchio == {k: v for k, v in json.loads(json.dumps(m)).items() if k != 'aggiornato'}:
            print('[modello] niente di nuovo.')
            return False
    except (OSError, ValueError):
        pass
    with open(percorso, 'w', encoding='utf-8') as f:
        json.dump(m, f, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
    print(f'[modello] scritto, {len(m["giocatori"])} giocatori.')
    return True


def leggi_json(nome):
    try:
        with open(os.path.join(DATI, nome), encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def stagioni_storico(cartella=os.path.join(DATI, 'storico')):
    out = []
    for p in sorted(glob.glob(os.path.join(cartella, '*.json.gz'))):
        with gzip.open(p, 'rt', encoding='utf-8') as f:
            out.append(json.load(f))
    return out


if __name__ == '__main__':
    base, st = leggi_json('base.json'), leggi_json('statistiche.json')
    m = costruisci(stagioni_storico(), (leggi_json('voti.json').get('giornate') or {}),
                   [(str(a[0]), a[3]) for a in base.get('p', [])], st.get('iniziali') or {},
                   {k: v[3] for k, v in (st.get('giocatori') or {}).items() if len(v) > 3 and v[3]})
    print(f'[modello] {m["addestramento"]["righe"]} righe, stagioni {m["addestramento"]["stagioni"][0]} - '
          f'{m["addestramento"]["stagioni"][-1]}, verifica su {", ".join(m["addestramento"]["verifica_su"])}')
    for nome in ('fantavoto', 'voto'):
        for r in RUOLI:
            v = m['verifica'][nome].get(r)
            if v:
                print(f'  {nome:<9} {r}: modello corr {v["modello"]["corr"]:.3f} rmse {v["modello"]["rmse"]:.3f}'
                      f'  |  prima corr {v["prima"]["corr"]:.3f} rmse {v["prima"]["rmse"]:.3f}'
                      f'  |  n0 {m[nome][r]["n0"]}')
    if '--verifica' not in sys.argv:
        ok = scrivi(os.path.join(DATI, 'modello.json'), m)
        sys.exit(0 if ok or plausibile(m) else 1)
