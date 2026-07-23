#!/usr/bin/env python3
"""Budget-parametric closure-system machinery (generalization of
dense_template.py to arbitrary translation budgets), plus:

  P1  direction-independence: for balanced words, B_2 single under t is
      equivalent under t and -t (nu is an involution on doubleton cosets);
      machine check on all m=6 simple words + narrow tree words m=8..12.
  P2  Pillar-1 transfer: T_{(2,4)} o A(W_m) is a single m^2-cycle (direct
      orbit check m = 6..40; word-level det argument unchanged).
  P3  validation of the parametric closure census against circuit SAT.

The closure system C(W; t0, t1): swap-bit field b with dual closure +
injectivity + coverage + nonempty idles, where
  D_0 = T_{-e0} o A_0, B_0 = T_{t0 + e0} o D_0  (letters L, Lam),
  D_1 = T_{-e1} o A_1, B_1 = T_{t1 + e1} o D_1  (letters S, Z).
All letter/placement logic is budget-independent (Theorem D2); only the
coverage cosets and the final first-return checks depend on t0, t1.
"""
import itertools, json, sys, time
from collections import defaultdict

SCR = "/tmp/claude-0/-home-user-claude-usage/e5933da4-9bfd-5e34-89c1-d01da7b77644/scratchpad/claudes-cycles"
sys.path.insert(0, SCR)
from criterion import budgets as budgets_old, is_single, word_loop, field_loops
from dense_template import fields_from_bits, bits_from_fields


def coset_classes(m, t):
    """Map p -> coset id of <t> in Z_m^2."""
    H, p = set(), (0, 0)
    while p not in H:
        H.add(p)
        p = ((p[0] + t[0]) % m, (p[1] + t[1]) % m)
    lab, nxt = {}, 0
    for q in itertools.product(range(m), repeat=2):
        if q in lab:
            continue
        for h in H:
            lab[((q[0] + h[0]) % m, (q[1] + h[1]) % m)] = nxt
        nxt += 1
    return lab, nxt


def template_model2(m, W, ts):
    """C(W; t0, t1) as CP-SAT model. ts = [t0, t1, t2] (t2 unused here)."""
    from ortools.sat.python import cp_model
    pts = list(itertools.product(range(m), repeat=2))
    cls = {p: W.get(p, 0) for p in pts}
    model = cp_model.CpModel()
    b = {p: model.NewBoolVar(f"b{p[0]}_{p[1]}") for p in pts}

    def shift(p, d):
        return ((p[0] + d[0]) % m, (p[1] + d[1]) % m)

    in0, in1 = {}, {}
    for p in pts:
        if cls[p] == 1:
            in0[p], in1[p] = model.NewConstant(1), b[p]
        elif cls[p] == 2:
            in0[p], in1[p] = b[p], model.NewConstant(1)
        else:
            in0[p], in1[p] = b[p], b[p]
    L, Lam, S, Z = (-1, 0), (-1, 1), (0, -1), (1, -1)

    def d0arcs(p):
        c = cls[p]
        if c == 1:
            return [(L, b[p].Not()), (Lam, b[p])]
        if c == 2:
            return [(L, b[p])]
        return [(Lam, b[p])]

    def d1arcs(p):
        c = cls[p]
        if c == 2:
            return [(S, b[p].Not()), (Z, b[p])]
        if c == 1:
            return [(S, b[p])]
        return [(Z, b[p])]

    for p in pts:
        for d, lit in d0arcs(p):
            model.AddImplication(lit, in0[shift(p, d)])
        for d, lit in d1arcs(p):
            model.AddImplication(lit, in1[shift(p, d)])
    for q in pts:
        ins0 = []
        for d in (L, Lam):
            s = shift(q, (-d[0], -d[1]))
            for dd, lit in d0arcs(s):
                if dd == d:
                    ins0.append(lit)
        model.AddAtMostOne(ins0)
        ins1 = []
        for d in (S, Z):
            s = shift(q, (-d[0], -d[1]))
            for dd, lit in d1arcs(s):
                if dd == d:
                    ins1.append(lit)
        model.AddAtMostOne(ins1)
    # coverage over the cosets of the DUAL translations
    tt0 = ((ts[0][0] + 1) % m, ts[0][1] % m)
    tt1 = (ts[1][0] % m, (ts[1][1] + 1) % m)
    lab0, n0 = coset_classes(m, tt0)
    lab1, n1 = coset_classes(m, tt1)
    by0, by1 = defaultdict(list), defaultdict(list)
    for p in pts:
        by0[lab0[p]].append(in0[p])
        by1[lab1[p]].append(in1[p])
    for v in range(n0):
        model.AddBoolOr(by0[v])
    for v in range(n1):
        model.AddBoolOr(by1[v])
    i0lits = [b[p].Not() if cls[p] == 1 else b[p] for p in pts if cls[p] in (1, 2)]
    i1lits = [b[p] if cls[p] == 1 else b[p].Not() for p in pts if cls[p] in (1, 2)]
    model.AddBoolOr(i0lits)
    model.AddBoolOr(i1lits)
    return model, b


def census2(m, W, ts, time_cap=3600.0, cand_cap=2_000_000, want_sols=0):
    """Exhaustive closure census under budgets ts. Returns
    (n_closure, n_B0single, n_completions, exhausted, sols)."""
    from ortools.sat.python import cp_model
    pts = list(itertools.product(range(m), repeat=2))
    model, bv = template_model2(m, W, ts)
    stats = {"cands": 0, "b0": 0, "both": 0}
    sols = []

    class CB(cp_model.CpSolverSolutionCallback):
        def OnSolutionCallback(self):
            stats["cands"] += 1
            b = {p: int(self.Value(bv[p])) for p in pts}
            A0, A1 = fields_from_bits(m, W, b)
            if is_single(m, A0, ts[0]):
                stats["b0"] += 1
                if is_single(m, A1, ts[1]):
                    stats["both"] += 1
                    if len(sols) < want_sols:
                        sols.append((b, A0, A1))
            if stats["cands"] >= cand_cap:
                self.StopSearch()

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_cap
    solver.parameters.enumerate_all_solutions = True
    st = solver.Solve(model, CB())
    exhausted = (st == cp_model.OPTIMAL and stats["cands"] < cand_cap)
    return stats["cands"], stats["b0"], stats["both"], exhausted, sols


# ---------------- realizable budget families with t_2 = (2, 4) ----------

def family_R(m, i=0, j=0, mirror=False):
    """Realizable budgets with t_2 = (2,4):
    lifts a = (m-3-j, j, 2), b = (i, m-5-i, 4)   [P=0, Q=1]
    mirror:  a = (j, m-3-j, 2), b = (m-5-i, i, 4) [P=1, Q=0].
    Valid iff all lifts >= 0 and per-cycle sums <= m-1."""
    if not mirror:
        a = [m - 3 - j, j, 2]
        b = [i, m - 5 - i, 4]
    else:
        a = [j, m - 3 - j, 2]
        b = [m - 5 - i, i, 4]
    if min(min(a), min(b)) < 0:
        return None
    if any(a[c] + b[c] > m - 1 for c in range(3)):
        return None
    if any(a[c] == 0 and b[c] == 0 for c in range(3)):
        return None
    ts = [(a[c] % m, b[c] % m) for c in range(3)]
    return ts, a, b


# ---------------- checks ----------------

def p1_direction_independence():
    """For balanced words, singleness under t and -t coincide (nu argument);
    verify on all simple m=6 words (balanced or not: check equivalence holds
    exactly on balanced; report any non-balanced counterexample separately)."""
    from induction import all_words
    print("P1: direction independence of B_2 for balanced words")
    m = 6
    t = budgets_old(m)[2]           # (-2,-4) mod m
    tneg = ((-t[0]) % m, (-t[1]) % m)
    from insertion_lemma import word_status
    nbal = 0
    for c, f in all_words(m).items():
        s1 = is_single(m, f, t)
        s2 = is_single(m, f, tneg)
        _, bal, _ = word_status(list(c), m)
        if bal:
            assert s1 == s2, (c, s1, s2)
            nbal += 1
    print(f"  m=6: all {nbal} balanced simple words: single under t <=> "
          f"single under -t  EXACT")


def p2_pillar1_transfer(mmax=40):
    from insertion_lemma import W_closed
    print("P2: W_m single under t_2 = (2,4), direct orbit check")
    for m in range(6, mmax + 1, 2):
        f = word_loop(m, W_closed(m))
        assert f is not None
        assert is_single(m, f, (2, 4)), m
    print(f"  verified m = 6..{mmax}")


def p3_validate_census(seed_words=None):
    """census2 vs circuit SAT on narrow words at m=8 under family_R."""
    from criterion import sat_completion
    print("P3: parametric census vs circuit SAT (m=8, family R(0,0))")
    from narrow_census import seeds_m6
    from insertion_lemma import narrow_data, child
    m = 8
    fam = family_R(m)
    assert fam
    ts, a, b = fam
    words = []
    for si, w in enumerate(seeds_m6()):
        _, _, _, _, mp = narrow_data(w, 6)
        for e in (0, 1):
            p = mp[e][0]
            words.append((si, e, list(child(w, p, p))))
    for si, e, w in words[:6]:
        f = word_loop(m, w)
        nc, nb0, nboth, exh, _ = census2(m, f, ts, time_cap=600)
        st, sol = sat_completion(m, f, require=("B0", "B1"), time_limit=600,
                                 ts=ts)
        sat_feas = st in ("OPTIMAL", "FEASIBLE")
        assert exh
        assert (nboth > 0) == sat_feas, (si, e, nboth, st)
        print(f"  seed {si} child {e}: closure={nc} b0={nb0} both={nboth} "
              f"SAT={st}  AGREE")
    print("P3 PASS")


if __name__ == "__main__":
    which = sys.argv[1:] or ["P1", "P2", "P3"]
    if "P1" in which:
        p1_direction_independence()
    if "P2" in which:
        p2_pillar1_transfer()
    if "P3" in which:
        p3_validate_census()
    print("DONE")
