#!/usr/bin/env python3
"""Phase 5: (N1) R = nu.sigma factorization + Cohn-Lempel reduction of
Lemma B to GF(2) interlacement nonsingularity; (N2) completion-inheritance
experiment along the k=1 chain; (N3) chain extension m=18, 20."""
import itertools, json, sys
from collections import Counter
from criterion import (SCR, MOVES, budgets, apply_B, is_single, coset_label,
                       criterion, field_loops, word_loop, sat_completion,
                       runs_of, windings)
from induction import canon, insertions_two_periods


# ---------- N1: R = nu.sigma and Cohn-Lempel ----------

def nu_sigma_cycles(m, f, t):
    """Cycle lengths of nu.sigma: sigma = loop successor, nu(q) = next
    support point strictly after q along q's <t>-coset orbit."""
    loops = field_loops(m, f)
    S = set(f)
    succ = {}
    for loop in loops:
        for a, b in zip(loop, loop[1:] + loop[:1]):
            succ[a] = b
    # coset orbit order
    lab, o, _ = coset_label(m, t)
    def nu(q):
        r = q
        for _ in range(o):
            r = ((r[0] + t[0]) % m, (r[1] + t[1]) % m)
            if r in S:
                return r
        raise AssertionError
    R = {p: nu(succ[p]) for p in S}
    seen, out = set(), []
    for p in S:
        if p in seen:
            continue
        n, q = 0, p
        while q not in seen:
            seen.add(q)
            q = R[q]
            n += 1
        out.append(n)
    return sorted(out)


def interlacement_rank(m, f, t):
    """For balanced profile {1:m, 2:m}: chords = doubleton-coset position
    pairs along the sigma-cycle; returns (m_chords, rank over GF(2))."""
    loops = field_loops(m, f)
    assert len(loops) == 1
    loop = loops[0]
    pos = {p: i for i, p in enumerate(loop)}
    lab, _, _ = coset_label(m, t)
    bycos = {}
    for p in loop:
        bycos.setdefault(lab[p], []).append(p)
    chords = []
    for l, ps in bycos.items():
        if len(ps) == 2:
            i, j = sorted(pos[p] for p in ps)
            chords.append((i, j))
        elif len(ps) != 1:
            return None  # not balanced
    n = len(chords)
    L = len(loop)

    def interlace(c, d):
        (a, b), (x, y) = c, d
        inx = lambda t_, lo, hi: lo < t_ < hi
        return (inx(x, a, b) != inx(y, a, b))
    rows = []
    for c in chords:
        r = 0
        for j, d in enumerate(chords):
            if c != d and interlace(c, d):
                r |= 1 << j
        rows.append(r)
    # GF(2) rank
    rank = 0
    for col in range(n):
        piv = None
        for i in range(rank, n):
            if rows[i] >> col & 1:
                piv = i
                break
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for i in range(n):
            if i != rank and rows[i] >> col & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return n, rank


def n1_verify():
    print("N1: R = nu.sigma, and Cohn-Lempel on balanced words")
    import random
    # (i) factorization on assorted gadgets (all profiles)
    cases = 0
    for m in (6, 8, 10, 12):
        t2 = budgets(m)[2]
        rng = random.Random(4 * m)
        words = []
        for _ in range(4000):
            w = [1] * m + [2] * (2 * m)
            rng.shuffle(w)
            f = word_loop(m, w)
            if f is not None:
                words.append(f)
            if len(words) >= 40:
                break
        for f in words:
            cov, rc = criterion(m, f, t2)
            if not cov:
                continue
            assert nu_sigma_cycles(m, f, t2) == rc, (m, "factorization fails")
            cases += 1
    print(f"  factorization R = nu.sigma verified on {cases} covered gadgets")
    # (ii) Cohn-Lempel: #cycles = m - rank + 1 on ALL m=6 balanced singles
    #      and on balanced non-singles
    m = 6
    t2 = budgets(m)[2]
    from induction import all_words, classify
    words = all_words(m)
    cls = classify(m, words)
    nb = ns = 0
    for c, (single, prof) in cls.items():
        if prof != {1: m, 2: m}:
            continue
        f = words[c]
        n, rank = interlacement_rank(m, f, t2)
        assert n == m
        cov, rc = criterion(m, f, t2)
        assert cov
        assert len(rc) == m - rank + 1, (c, rc, rank)
        nb += 1
        ns += single
        if single:
            assert rank == m
    print(f"  Cohn-Lempel verified on all {nb} balanced m=6 words "
          f"({ns} single <=> rank m): exact")
    # (iii) chain words m=8..16
    for fn, m in (("chain_completion_m10.json", 10),
                  ("chain_completion_m12_k1.json", 12),
                  ("chain_completion_m14_k2.json", 14),
                  ("chain_completion_m16_k2.json", 16)):
        d = json.load(open(f"{SCR}/{fn}"))
        tab = {tuple(map(int, k.strip('()').split(','))): v
               for k, v in d.items()}
        f = {p: tab[p][2] for p in tab if tab[p][2] != 0}
        t2 = budgets(m)[2]
        pr = interlacement_rank(m, f, t2)
        cov, rc = criterion(m, f, t2)
        if pr is None:
            print(f"  {fn}: profile not balanced (nu has longer cycles) -- "
                  f"C-L n/a; rcycles={rc}")
        else:
            n, rank = pr
            ok = len(rc) == n - rank + 1
            print(f"  {fn}: chords={n} rank={rank} rcycles={len(rc)} "
                  f"C-L holds: {ok}")
            assert ok


# ---------- N2: completion inheritance ----------

def sat_completion_min_dev(m, f2, parent, mp, time_limit=600.0):
    """Complete child gadget f2 at modulus m, minimizing deviation from the
    parent solution (fields at modulus mp < m) under coordinate embedding
    p -> p for p in [0,mp)^2.  Returns (status, fields, dev, devpts)."""
    from ortools.sat.python import cp_model
    ts = budgets(m)
    pts = list(itertools.product(range(m), repeat=2))
    pid = {p: i for i, p in enumerate(pts)}
    model = cp_model.CpModel()
    y = {}
    for p in pts:
        for c in (0, 1):
            for mv in range(3):
                y[p, c, mv] = model.NewBoolVar(f"y{pid[p]}_{c}_{mv}")
            model.AddExactlyOne([y[p, c, mv] for mv in range(3)])
        a2 = f2.get(p, 0)
        model.Add(y[p, 0, a2] == 0)
        model.Add(y[p, 1, a2] == 0)
        for mv in range(3):
            if mv != a2:
                model.AddExactlyOne([y[p, 0, mv], y[p, 1, mv]])
    for c in (0, 1):
        for q in pts:
            model.AddExactlyOne(
                [y[((q[0] - dx) % m, (q[1] - dy) % m), c, mv]
                 for mv, (dx, dy) in enumerate(MOVES)])
        ac, bc = ts[c]
        arcs = []
        for p in pts:
            for mv, (dx, dy) in enumerate(MOVES):
                q = ((p[0] + dx + ac) % m, (p[1] + dy + bc) % m)
                if q == p:
                    model.Add(y[p, c, mv] == 0)
                else:
                    arcs.append((pid[p], pid[q], y[p, c, mv]))
        model.AddCircuit(arcs)
    devs = []
    for p in itertools.product(range(mp), repeat=2):
        for c in (0, 1):
            pa = parent[c][p]
            devs.append(y[p, c, pa].Not())
            model.AddHint(y[p, c, pa], 1)
    model.Minimize(sum(devs))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = 8
    st = solver.Solve(model)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return solver.StatusName(st), None, None, None
    fields = []
    for c in (0, 1):
        fields.append({p: next(mv for mv in range(3)
                               if solver.Value(y[p, c, mv])) for p in pts})
    devpts = [p for p in itertools.product(range(mp), repeat=2)
              if fields[0][p] != parent[0][p] or fields[1][p] != parent[1][p]]
    return (solver.StatusName(st), fields, int(solver.ObjectiveValue()),
            devpts)


def n2_inheritance(tls=None):
    tls = tls or {8: 600.0, 10: 1500.0, 12: 3600.0, 14: 7200.0}
    print("N2: completion inheritance along a k=1 chain (coordinate "
          "embedding, minimized Hamming deviation)")
    pairs = json.load(open(f"{SCR}/insertion_pairs_6_8.json"))
    w6 = tuple(pairs[0][0])
    m = 6
    f6 = word_loop(m, list(w6))
    st, sol = sat_completion(m, f6, require=("B0", "B1"), time_limit=300.0)
    assert sol
    parent = [sol[0], sol[1], None]
    parent_word = w6
    chain_sols = {6: (f6, sol)}
    for m2 in (8, 10, 12, 14):
        t2 = budgets(m2)[2]
        # child words: singles among double-P1 insertions of parent_word
        childs = []
        seen = set()
        for w2 in insertions_two_periods(parent_word):
            c = canon(list(w2))
            if c in seen:
                continue
            seen.add(c)
            f = word_loop(m2, list(c))
            if f is not None and is_single(m2, f, t2):
                childs.append((c, f))
        if not childs:
            print(f"  m={m2}: no single children of this parent word; "
                  f"chain stalls")
            return
        best = None
        for c, f in childs[:6]:
            st, flds, dev, devpts = sat_completion_min_dev(
                m2, f, parent, m2 - 2, time_limit=tls[m2] / min(6, len(childs)))
            if flds is None:
                continue
            if best is None or dev < best[3]:
                best = (c, f, flds, dev, devpts, st)
        if best is None:
            print(f"  m={m2}: no completable child among first "
                  f"{min(6, len(childs))}")
            return
        c, f, flds, dev, devpts, st = best
        ts = budgets(m2)
        assert is_single(m2, flds[0], ts[0]) and is_single(m2, flds[1], ts[1])
        tot = 2 * (m2 - 2) ** 2
        print(f"  m={m2}: {len(childs)} single children; best deviation "
              f"{dev}/{tot} embedded cells ({st}); "
              f"devpts sample={sorted(devpts)[:12]}{'...' if len(devpts)>12 else ''}",
              flush=True)
        json.dump({str(p): [flds[0][p], flds[1][p], f.get(p, 0)]
                   for p in itertools.product(range(m2), repeat=2)},
                  open(f"{SCR}/inherit_completion_m{m2}.json", "w"))
        parent = [flds[0], flds[1], None]
        parent_word = c
        chain_sols[m2] = (f, flds)


# ---------- N3: chain extension ----------

def n3_extend(fn, m0, k, targets, tl=10000.0, width=8):
    from induction2 import insertions_two_P2, gadget_word
    ins = insertions_two_periods if k == 1 else insertions_two_P2
    m, w = gadget_word(fn)
    assert m == m0
    frontier = [tuple(w)]
    for m2 in targets:
        t2 = budgets(m2)[2]
        singles, seen = [], set()
        for w0 in frontier:
            for w2 in ins(w0):
                c = canon(list(w2))
                if c in seen:
                    continue
                seen.add(c)
                f = word_loop(m2, list(c))
                if f is not None and is_single(m2, f, t2):
                    singles.append((c, f))
        print(f"  k={k} chain -> m={m2}: {len(singles)} single children",
              flush=True)
        done = None
        for c, f in singles[:width]:
            st, sol = sat_completion(m2, f, require=("B0", "B1"),
                                     time_limit=tl)
            print(f"    SAT m={m2} k={k}: {st}", flush=True)
            if sol:
                A0, A1 = sol
                ts = budgets(m2)
                assert is_single(m2, A0, ts[0]) and is_single(m2, A1, ts[1])
                json.dump({str(p): [A0[p], A1[p], f.get(p, 0)]
                           for p in itertools.product(range(m2), repeat=2)},
                          open(f"{SCR}/chain_completion_m{m2}_k{k}.json", "w"))
                done = (c, f)
                break
        if done is None:
            print(f"  k={k}: no completion found at m={m2} in first {width}")
            return
        frontier = [done[0]]


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "N1"
    if which == "N1":
        n1_verify()
    elif which == "N2":
        n2_inheritance()
    elif which == "N3k2":
        n3_extend("chain_completion_m16_k2.json", 16, 2, (18, 20))
    elif which == "N3k1":
        n3_extend("chain_completion_m14_k2.json", 14, 2, (16,))
    print("DONE")
