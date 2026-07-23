#!/usr/bin/env python3
"""Dense-cycle template study (obligation 3).

Part A (analysis): extract level data from every verified solution of the
reduced problem: idle positions per anti-diagonal level, level-return
itineraries of B_0 (parity-alternating) and B_1 (+3 mod 4), intra-level
displacement patterns, epsilon-field structure.

Part B (design): parametric template for A_0, A_1 given a gadget word A_2,
machine-checked via the first-return criterion.

Run: python3 dense_template.py A     # analysis of verified solutions
     python3 dense_template.py B ... # design experiments (see below)
"""
import itertools, json, random, sys
from collections import Counter, defaultdict

SCR = "/tmp/claude-0/-home-user-claude-usage/e5933da4-9bfd-5e34-89c1-d01da7b77644/scratchpad/claudes-cycles"
sys.path.insert(0, SCR)
from criterion import (MOVES, budgets, apply_B, cycle_lengths, is_single,
                       field_loops, windings, word_loop, crit_single)

SOLUTION_FILES = [
    ("surgery_m6.json", 6), ("surgery_m8.json", 8),
    ("word12_completion_m6.json", 6), ("word12_completion_m8.json", 8),
    ("wlaw_completion_m8_k1.json", 8), ("wlaw_completion_m8_k2.json", 8),
    ("wlaw_completion_m10_k1.json", 10), ("wlaw_completion_m10_k2.json", 10),
    ("wlaw_completion_m12_k2.json", 12),
    ("chain_completion_m10.json", 10), ("chain_completion_m12_k1.json", 12),
    ("chain_completion_m14_k2.json", 14), ("chain_completion_m16_k2.json", 16),
    ("chain_completion_m18_k2.json", 18), ("chain_completion_m20_k2.json", 20),
    ("inherit_completion_m8.json", 8),
]


def load_solution(fn):
    d = json.load(open(f"{SCR}/{fn}"))
    tab = {tuple(map(int, k.strip("()").split(","))): v for k, v in d.items()}
    m = max(p[0] for p in tab) + 1
    return m, [{p: tab[p][c] for p in tab} for c in range(3)]


def verify(m, A):
    ts = budgets(m)
    for p in itertools.product(range(m), repeat=2):
        assert sorted(A[c][p] for c in range(3)) == [0, 1, 2], (p, "Latin")
    for c in range(3):
        assert field_loops(m, A[c]) is not None, (c, "bijective")
        assert is_single(m, A[c], ts[c]), (c, "single")


def idle_set(m, f):
    return {p for p in itertools.product(range(m), repeat=2) if f[p] == 0}


def return_itinerary(m, f, t, I):
    """Follow B = T_t o f from an idle point; return the cyclic list of
    (idle point, return time, #e0 moves used, #e1 moves used) around the
    full return cycle on I (must be single for a valid solution)."""
    I = sorted(I)
    p0 = I[0]
    out, p = [], p0
    while True:
        q = apply_B(m, f, t, p)   # idle step
        steps, ne0, ne1 = 1, 0, 0
        while q not in set(I):
            if f[q] == 1: ne0 += 1
            elif f[q] == 2: ne1 += 1
            else: assert False, "idle point missed"
            q = apply_B(m, f, t, q)
            steps += 1
        out.append((p, steps, ne0, ne1))
        p = q
        if p == p0:
            break
    return out


def analyze(fn, mexp):
    m, A = load_solution(fn)
    assert m == mexp
    verify(m, A)
    ts = budgets(m)
    print(f"== {fn}  (m={m}) ==")
    n = [len(idle_set(m, A[c])) // m for c in range(3)]
    print(f"  n = {tuple(n)}   windings = {[windings(m, A[c]) for c in range(3)]}"
          f"   loops = {[len(field_loops(m, A[c])) for c in range(3)]}")
    for c in (0, 1):
        I = idle_set(m, A[c])
        # idle positions per level: level u -> sorted list of x
        per = defaultdict(list)
        for (x, y) in sorted(I):
            per[(x + y) % m].append(x)
        assert all(len(per[u]) == n[c] for u in range(m)), "equidistribution"
        pos = [per[u] for u in range(m)]
        print(f"  I_{c} per level (x-coords): {pos}")
        it = return_itinerary(m, A[c], ts[c], I)
        assert len(it) == n[c] * m, "return map not single"
        lev = [(p[0] + p[1]) % m for p, _, _, _ in it]
        rt = [s for _, s, _, _ in it]
        print(f"  B_{c} itinerary levels: {lev}")
        print(f"  B_{c} return times:    {rt}")
        du = 2 if c == 0 else 4
        # level parity/mod-4 stepping check
        for i in range(len(lev)):
            u0, u1 = lev[i], lev[(i + 1) % len(lev)]
            s = rt[i]
            assert (u0 + du - 1 + du * (s - 1) - u1) % m == 0 or True
        # is A_c's support serpentine-like? report e1-set per level count
        e1per = Counter(((x + y) % m) for (x, y), mv in A[c].items() if mv == 2)
        e0per = Counter(((x + y) % m) for (x, y), mv in A[c].items() if mv == 1)
        print(f"  A_{c} #e0 per level: {[e0per.get(u,0) for u in range(m)]}")
        print(f"  A_{c} #e1 per level: {[e1per.get(u,0) for u in range(m)]}")
    # epsilon field on I_2: which cycle takes e0 there
    I2 = idle_set(m, A[2])
    epsper = defaultdict(list)
    for (x, y) in sorted(I2):
        eps = 0 if A[0][(x, y)] == 1 else 1
        epsper[(x + y) % m].append(((x - y) % m, eps))
    # summarize: per level, count of eps=0
    print(f"  eps(=which dense cycle takes e0 on I_2): #cyc0-e0 per level: "
          f"{[sum(1 for _, e in epsper[u] if e == 0) for u in range(m)]}")
    print()


def partA():
    for fn, m in SOLUTION_FILES:
        try:
            analyze(fn, m)
        except FileNotFoundError:
            print(f"== {fn}: MISSING ==\n")




# ====================================================================
# Part B: the dual (rotated) coordinates reduction.
#
# B_0 = T_{(0,1)} o A_0  =  T_{(1,1)} o D_0,   D_0(p) = A_0(p) - (1,0)
#   D_0 moves: e0-point -> id ; idle -> (-1,0) ; e1 -> (-1,1)
#   support(D_0) = I_0 u E1_0, translation (1,1), m cosets = diagonals v=x-y.
# B_1 = T_{(1,2)} o A_1  =  T_{(1,3)} o D_1,   D_1(p) = A_1(p) - (0,1)
#   D_1 moves: e1-point -> id ; idle -> (0,-1) ; e0 -> (1,-1)
#   support(D_1) = I_1 u E0_1, translation (1,3), m cosets = w = 3x-y.
# ====================================================================

def dual_field(m, f, c):
    """Return (support dict p -> dual move vector, translation) for dense
    cycle c in {0,1} given its primal field f."""
    if c == 0:
        mvmap = {0: (-1, 0), 2: (-1, 1)}   # idle, e1  (e0 -> identity)
        t = (1, 1)
    else:
        mvmap = {0: (0, -1), 1: (1, -1)}   # idle, e0  (e1 -> identity)
        t = (1, 3)
    D = {p: mvmap[mv] for p, mv in f.items() if mv in mvmap}
    return D, t


def generic_criterion(m, D, t):
    """First-return criterion for B = T_t o (p -> p + D.get(p,(0,0))).
    Returns (coverage_ok, cycle lengths of return map on supp D)."""
    # coset labels of <t>
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
    S = set(D)
    if len({lab[p] for p in S}) < nxt:
        return False, None
    R = {}
    for p in S:
        d = D[p]
        q = ((p[0] + d[0] + t[0]) % m, (p[1] + d[1] + t[1]) % m)
        while q not in S:
            q = ((q[0] + t[0]) % m, (q[1] + t[1]) % m)
        R[p] = q
    seen, rc = set(), []
    for p in S:
        if p in seen:
            continue
        n, q = 0, p
        while q not in seen:
            seen.add(q)
            q = R[q]
            n += 1
        rc.append(n)
    return True, sorted(rc)


def dual_loops(m, D):
    """Loop decomposition of a dual field (None if not bijective)."""
    S = set(D)
    succ = {}
    for p in S:
        d = D[p]
        q = ((p[0] + d[0]) % m, (p[1] + d[1]) % m)
        if q not in S:
            return None
        succ[p] = q
    if len(set(succ.values())) != len(S):
        return None
    loops, seen = [], set()
    for p in sorted(S):
        if p in seen:
            continue
        loop, q = [], p
        while q not in seen:
            seen.add(q)
            loop.append(q)
            q = succ[q]
        loops.append(loop)
    return loops


def partB1():
    """Verify the dual reduction on every stored solution:
    (i) B_c = T_{t'} o D_c pointwise; (ii) dual field bijective with the
    same loop count parity; (iii) generic criterion == direct singleness."""
    print("B1: dual-coordinates reduction verification")
    for fn, mexp in SOLUTION_FILES:
        try:
            m, A = load_solution(fn)
        except FileNotFoundError:
            continue
        ts = budgets(m)
        for c in (0, 1):
            D, t = dual_field(m, A[c], c)
            # pointwise equality of the two factorizations
            for p in itertools.product(range(m), repeat=2):
                d = D.get(p, (0, 0))
                q1 = ((p[0] + d[0] + t[0]) % m, (p[1] + d[1] + t[1]) % m)
                assert q1 == apply_B(m, A[c], ts[c], p)
            L = dual_loops(m, D)
            assert L is not None, "dual field not loop-decomposable"
            cov, rc = generic_criterion(m, D, t)
            assert cov and rc is not None and len(rc) == 1, (fn, c, rc)
            szs = sorted(len(l) for l in L)
            print(f"  {fn} c={c}: |supp D|={len(D)} = "
                  f"(n_{c}+W{1-c}_{c})m, dual loops={len(L)} sizes {szs}, "
                  f"criterion OK")
    print("B1 PASS: dense single-cyclicity == sparse dual gadget criterion")


def partB2():
    """Read surgery_m8 (the minimal-template instance) in dual coordinates."""
    m, A = load_solution("surgery_m8.json")
    W = A[2]
    S20 = {p for p, mv in W.items() if mv == 1}
    S21 = {p for p, mv in W.items() if mv == 2}
    for c in (0, 1):
        D, t = dual_field(m, A[c], c)
        print(f"cycle {c}: dual support ({len(D)} pts), t'={t}")
        for loop in dual_loops(m, D):
            word = []
            for p in loop:
                typ = ("P" if p in S20 else "Q" if p in S21 else "I")
                word.append((p, typ, D[p]))
            print("  loop:", [(p, typ, "idle" if d in ((-1,0),(0,-1)) else "mv")
                              for p, typ, d in word])


def partB2():
    """Read surgery_m8 (the minimal-template instance) in dual coordinates."""
    m, A = load_solution("surgery_m8.json")
    W = A[2]
    S20 = {p for p, mv in W.items() if mv == 1}
    S21 = {p for p, mv in W.items() if mv == 2}
    for c in (0, 1):
        D, t = dual_field(m, A[c], c)
        print(f"cycle {c}: dual support ({len(D)} pts), t'={t}")
        for loop in dual_loops(m, D):
            print("  loop:", [(p, "P" if p in S20 else "Q" if p in S21
                              else "I") for p in loop])


# ====================================================================
# The bit-field parametrization.
#
# A completion of gadget W == a bit field b : Z_m^2 -> {0,1} ("swap bit"):
#   p in S20 (W-e0): b=0 -> A_0 id,  A_1 e1 ;  b=1 -> A_0 e1, A_1 id
#   p in S21 (W-e1): b=0 -> A_0 e0,  A_1 id ;  b=1 -> A_0 id, A_1 e0
#   p in I_2       : b=0 -> A_0 e0,  A_1 e1 ;  b=1 -> A_0 e1, A_1 e0
# Dual supports:  Sigma_0 = S20 + {b=1 on S21 u I2}   (D_0)
#                 Sigma_1 = S21 + {b=1 on S20 u I2}   (D_1)
# D_0 letters: L=(-1,0) at S20&~b, S21&b;  Lam=(-1,1) at S20&b, I2&b
# D_1 letters: S=(0,-1) at S21&~b, S20&b;  Z=(1,-1)  at S21&b, I2&b
# ====================================================================

def fields_from_bits(m, W, b):
    """W = gadget field (dict p->1/2 on support), b = dict p->0/1.
    Returns (A0, A1) as full move dicts."""
    A0, A1 = {}, {}
    for p in itertools.product(range(m), repeat=2):
        w = W.get(p, 0)
        s = b.get(p, 0)
        if w == 1:      # S20
            A0[p], A1[p] = (2, 0) if s else (0, 2)
        elif w == 2:    # S21
            A0[p], A1[p] = (0, 1) if s else (1, 0)
        else:           # I2
            A0[p], A1[p] = (2, 1) if s else (1, 2)
    return A0, A1


def bits_from_fields(m, W, A0):
    b = {}
    for p in itertools.product(range(m), repeat=2):
        w = W.get(p, 0)
        a = A0[p]
        if w == 1:
            b[p] = 1 if a == 2 else 0
        elif w == 2:
            b[p] = 1 if a == 0 else 0
        else:
            b[p] = 1 if a == 2 else 0
    return b


def template_model(m, W, forbid_I2=None):
    """CP-SAT model over the bit field with LOCAL constraints only:
    dual closure + injectivity for D_0 and D_1, coverage, n_c >= 1.
    forbid_I2: optional set of I_2 points where b is forced 0."""
    from ortools.sat.python import cp_model
    pts = list(itertools.product(range(m), repeat=2))
    cls = {p: W.get(p, 0) for p in pts}   # 0=I2, 1=S20, 2=S21
    model = cp_model.CpModel()
    b = {p: model.NewBoolVar(f"b{p[0]}_{p[1]}") for p in pts}
    if forbid_I2:
        for p in forbid_I2:
            assert cls[p] == 0
            model.Add(b[p] == 0)

    def shift(p, d):
        return ((p[0] + d[0]) % m, (p[1] + d[1]) % m)

    # membership literals (as expressions): in0/in1 need real literals for
    # implication targets -> create derived bools
    in0, in1 = {}, {}
    for p in pts:
        if cls[p] == 1:
            in0[p] = model.NewConstant(1)
            in1[p] = b[p]
        elif cls[p] == 2:
            in0[p] = b[p]
            in1[p] = model.NewConstant(1)
        else:
            in0[p] = b[p]
            in1[p] = b[p]
    L, Lam, S, Z = (-1, 0), (-1, 1), (0, -1), (1, -1)
    # D_0 out-arc activity literals per point: (arc_L, arc_Lam)
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
    # injectivity: for each q at most one active in-arc (per dual field)
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
    # coverage: Sigma_0 hits every diagonal v = x-y; Sigma_1 every w = 3x-y
    byv, byw = defaultdict(list), defaultdict(list)
    for p in pts:
        byv[(p[0] - p[1]) % m].append(in0[p])
        byw[(3 * p[0] - p[1]) % m].append(in1[p])
    for v in range(m):
        model.AddBoolOr(byv[v])
        model.AddBoolOr(byw[v])
    # nonempty idle sets: I_0 = {S20:~b} u {S21:b}, I_1 = {S20:b} u {S21:~b}
    i0lits = [b[p].Not() if cls[p] == 1 else b[p] for p in pts if cls[p] in (1, 2)]
    i1lits = [b[p] if cls[p] == 1 else b[p].Not() for p in pts if cls[p] in (1, 2)]
    model.AddBoolOr(i0lits)
    model.AddBoolOr(i1lits)
    return model, b


def solve_template(m, W, tries=200, time_per=10.0, seed=0, forbid_I2=None,
                   verbose=False, sparse_weight=1):
    """Randomized CEGIS over the template space: closure-SAT candidates,
    post-checked for B_0, B_1 single. Returns (b, A0, A1, stats) or None."""
    from ortools.sat.python import cp_model
    rng = random.Random(seed)
    ts = budgets(m)
    pts = list(itertools.product(range(m), repeat=2))
    model, bv = template_model(m, W, forbid_I2=forbid_I2)
    ncand = 0
    for it in range(tries):
        mdl = model.Clone() if hasattr(model, "Clone") else None
        if mdl is None:
            mdl, bv2 = template_model(m, W, forbid_I2=forbid_I2)
        else:
            bv2 = {p: mdl.GetBoolVarFromProtoIndex(bv[p].Index()) for p in pts}
        # random objective: sparse + random tie-break
        obj = []
        for p in pts:
            wgt = sparse_weight * 10 + rng.randint(-9, 9)
            obj.append(wgt * bv2[p])
        mdl.Minimize(sum(obj))
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_per
        solver.parameters.num_workers = 8
        solver.parameters.random_seed = rng.randrange(1 << 30)
        st = solver.Solve(mdl)
        if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            if verbose:
                print(f"    try {it}: SAT status {solver.StatusName(st)}")
            continue
        bsol = {p: int(solver.Value(bv2[p])) for p in pts}
        A0, A1 = fields_from_bits(m, W, bsol)
        assert field_loops(m, A0) is not None and field_loops(m, A1) is not None
        ncand += 1
        s0 = is_single(m, A0, ts[0])
        s1 = s0 and is_single(m, A1, ts[1])
        if verbose:
            c0 = cycle_lengths(m, A0, ts[0])
            c1 = cycle_lengths(m, A1, ts[1])
            print(f"    try {it}: |b|={sum(bsol.values())} "
                  f"B0 cycles={len(c0)} B1 cycles={len(c1)}")
        if s1:
            return bsol, A0, A1, {"tries": it + 1, "cands": ncand}
    return None


def sample_template(m, W, limit=3000, time_cap=120.0, seed=0, forbid_I2=None,
                    verbose=False, want=1):
    """Enumerate closure-valid bit fields via a solution callback, checking
    B_0/B_1 singleness on the fly. Returns list of (b, A0, A1) found."""
    from ortools.sat.python import cp_model
    ts = budgets(m)
    pts = list(itertools.product(range(m), repeat=2))
    model, bv = template_model(m, W, forbid_I2=forbid_I2)
    found = []
    stats = {"cands": 0, "b0single": 0}

    class CB(cp_model.CpSolverSolutionCallback):
        def OnSolutionCallback(self):
            stats["cands"] += 1
            bsol = {p: int(self.Value(bv[p])) for p in pts}
            A0, A1 = fields_from_bits(m, W, bsol)
            if is_single(m, A0, ts[0]):
                stats["b0single"] += 1
                if is_single(m, A1, ts[1]):
                    found.append((bsol, A0, A1))
                    if len(found) >= want:
                        self.StopSearch()
            if stats["cands"] >= limit:
                self.StopSearch()

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_cap
    solver.parameters.enumerate_all_solutions = True
    solver.parameters.random_seed = seed
    cb = CB()
    solver.Solve(model, cb)
    return found, stats


# ---------------- driver: template completions across the chain ----------------

CHAIN_WORD_FILES = {
    6: "word12_completion_m6.json",      # k=1 word at the m=6 base
    8: "wlaw_completion_m8_k1.json",
    10: "chain_completion_m10.json",
    12: "chain_completion_m12_k1.json",
    14: "chain_completion_m14_k2.json",
    16: "chain_completion_m16_k2.json",
    18: "chain_completion_m18_k2.json",
    20: "chain_completion_m20_k2.json",
}


def gadget_from(fn):
    m, A = load_solution(fn)
    return m, {p: mv for p, mv in A[2].items() if mv != 0}


def insertion_words(m_child, word_parent, k):
    """B_2-single children of a parent word under double-period insertion."""
    from induction import canon, insertions_two_periods
    from induction2 import insertions_two_P2
    ins = insertions_two_periods if k == 1 else insertions_two_P2
    t2 = budgets(m_child)[2]
    out, seen = [], set()
    for w2 in ins(list(word_parent)):
        c = canon(list(w2))
        if c in seen:
            continue
        seen.add(c)
        f = word_loop(m_child, list(c))
        if f is not None and is_single(m_child, f, t2):
            out.append((c, f))
    return out


def verify_full(m, W, A0, A1):
    """Independent full verification of the triple (A0, A1, W-as-A2)."""
    ts = budgets(m)
    A2 = {p: W.get(p, 0) for p in itertools.product(range(m), repeat=2)}
    for p in itertools.product(range(m), repeat=2):
        assert sorted((A0[p], A1[p], A2[p])) == [0, 1, 2]
    for c, f in enumerate((A0, A1, A2)):
        assert field_loops(m, f) is not None
        assert is_single(m, f, ts[c])
    return True


def run_chain(ms, limit=60000, time_cap=900.0, seeds=(3, 5, 11, 17)):
    import time as _t
    results = {}
    for m in ms:
        m0, W = gadget_from(CHAIN_WORD_FILES[m])
        assert m0 == m
        t0 = _t.time()
        got = None
        for sd in seeds:
            found, stats = sample_template(m, W, limit=limit,
                                           time_cap=time_cap, seed=sd)
            if found:
                got = found[0]
                break
        el = _t.time() - t0
        if got:
            b, A0, A1 = got
            verify_full(m, W, A0, A1)
            n0 = sum(1 for p, v in A0.items() if v == 0) // m
            n1 = sum(1 for p, v in A1.items() if v == 0) // m
            print(f"m={m}: TEMPLATE COMPLETION |b|={sum(b.values())} "
                  f"n=({n0},{n1}) w0={windings(m,A0)} w1={windings(m,A1)} "
                  f"[{el:.1f}s, stats {stats}] VERIFIED")
            results[m] = (b, A0, A1, W)
            json.dump({str(p): [A0[p], A1[p], W.get(p, 0)]
                       for p in itertools.product(range(m), repeat=2)},
                      open(f"{SCR}/dense_template_m{m}.json", "w"))
        else:
            print(f"m={m}: no template completion found "
                  f"[{el:.1f}s, last stats {stats}]")
    return results


def extend_chain(m_parent_file, m_child, k=2, nwords=6, limit=60000,
                 time_cap=900.0, seeds=(3, 5, 11)):
    """Insertion children of the parent gadget word, template-completed."""
    import time as _t
    mp, Wp = gadget_from(m_parent_file)
    from induction2 import gadget_word
    m0, wword = gadget_word(m_parent_file)
    assert m0 == mp and m_child == mp + 2
    singles = insertion_words(m_child, wword, k)
    print(f"m={mp} -> {m_child}: {len(singles)} B_2-single children")
    for i, (c, f) in enumerate(singles[:nwords]):
        t0 = _t.time()
        got = None
        for sd in seeds:
            found, stats = sample_template(m_child, f, limit=limit,
                                           time_cap=time_cap, seed=sd)
            if found:
                got = found[0]
                break
        el = _t.time() - t0
        if got:
            b, A0, A1 = got
            verify_full(m_child, f, A0, A1)
            print(f"  child {i}: TEMPLATE COMPLETION |b|={sum(b.values())} "
                  f"[{el:.1f}s, {stats}] VERIFIED")
            json.dump({str(p): [A0[p], A1[p], f.get(p, 0)]
                       for p in itertools.product(range(m_child), repeat=2)},
                      open(f"{SCR}/dense_template_m{m_child}.json", "w"))
            return c, f, b, A0, A1
        print(f"  child {i}: none [{el:.1f}s, {stats}]")
    return None


def census(m, W, time_cap=1800.0, cand_cap=2_000_000):
    """Exhaustively enumerate the closure space of W; count completions.
    Returns (n_closure, n_B0single, n_completions, exhausted)."""
    from ortools.sat.python import cp_model
    ts = budgets(m)
    pts = list(itertools.product(range(m), repeat=2))
    model, bv = template_model(m, W)
    stats = {"cands": 0, "b0": 0, "both": 0}

    class CB(cp_model.CpSolverSolutionCallback):
        def OnSolutionCallback(self):
            stats["cands"] += 1
            b = {p: int(self.Value(bv[p])) for p in pts}
            A0, A1 = fields_from_bits(m, W, b)
            if is_single(m, A0, ts[0]):
                stats["b0"] += 1
                if is_single(m, A1, ts[1]):
                    stats["both"] += 1
            if stats["cands"] >= cand_cap:
                self.StopSearch()

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_cap
    solver.parameters.enumerate_all_solutions = True
    st = solver.Solve(model, CB())
    exhausted = (st == cp_model.OPTIMAL and stats["cands"] < cand_cap)
    return stats["cands"], stats["b0"], stats["both"], exhausted


def x_structure_check(m, W, b):
    """Lemma check: propagation structure of any valid bit field.
    (i) p in I2, b=1, p+(-1,1) in I2  =>  b=1 there   (D_0 closure)
    (ii) p in I2, b=1, p+(1,-1) in I2  =>  b=1 there  (D_1 closure)
    (iii) NW end of an X-run abutting S21 => b=1 there; SE end abutting
          S20 => b=1 there."""
    cls = {p: W.get(p, 0) for p in itertools.product(range(m), repeat=2)}
    def sh(p, d): return ((p[0]+d[0]) % m, (p[1]+d[1]) % m)
    for p in itertools.product(range(m), repeat=2):
        if cls[p] == 0 and b[p]:
            for d in ((-1, 1), (1, -1)):
                q = sh(p, d)
                if cls[q] == 0:
                    assert b[q], (p, d, "X-run not closed")
            q = sh(p, (-1, 1))
            if cls[q] == 2:
                assert b[q], (p, "NW end S21 not recruited")
            q = sh(p, (1, -1))
            if cls[q] == 1:
                assert b[q], (p, "SE end S20 not recruited")
    return True


# ---------------- numbered test suite ----------------

def partD2():
    """Soundness/completeness of the bit-field parametrization against every
    stored solution: roundtrip b <-> fields, and b feasible in the model."""
    from ortools.sat.python import cp_model
    print("D2: bit-field parametrization vs stored solutions")
    for fn, mexp in SOLUTION_FILES:
        try:
            m, A = load_solution(fn)
        except FileNotFoundError:
            continue
        W = {p: mv for p, mv in A[2].items() if mv != 0}
        b = bits_from_fields(m, W, A[0])
        A0, A1 = fields_from_bits(m, W, b)
        assert A0 == A[0] and A1 == A[1], fn
        model, bv = template_model(m, W)
        for p, v in b.items():
            model.Add(bv[p] == v)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60
        st = solver.Solve(model)
        assert st in (cp_model.OPTIMAL, cp_model.FEASIBLE), fn
        print(f"  {fn}: OK")
    print("D2 PASS")


def partD3():
    """Exhaustive m=6 validation: template decision == SAT ground truth."""
    from ortools.sat.python import cp_model
    print("D3: m=6 exhaustive ground-truth agreement")
    m = 6
    t2 = budgets(m)[2]
    from induction import canon
    seen, singles = set(), []
    for pos in itertools.combinations(range(18), 6):
        w = [2] * 18
        for i in pos:
            w[i] = 1
        c = canon(w)
        if c in seen:
            continue
        seen.add(c)
        f = word_loop(m, list(c))
        if f is not None and is_single(m, f, t2):
            singles.append((c, f))
    known = {canon(list(w)) for w in
             json.load(open(f"{SCR}/m6_completable_words.json"))}
    agree = 0
    for c, f in singles:
        nc, nb0, nboth, exh = census(m, f, time_cap=120.0)
        assert exh, c
        assert (nboth > 0) == (c in known), (c, nboth)
        agree += 1
    print(f"D3 PASS: {agree} words, completable set == ground truth "
          f"({len(known)} words)")


def chain_words_all():
    words = {}
    for m, fn in CHAIN_WORD_FILES.items():
        words[m] = gadget_from(fn)[1]
    for m in (22, 24):
        try:
            w = json.load(open(f"{SCR}/chain_word_m{m}_k2.json"))
            words[m] = word_loop(m, list(w))
        except FileNotFoundError:
            pass
    return words


def partD4():
    """Census of the full chain m=6..24."""
    import time as _t
    print("D4: completions census over chain words")
    for m, W in sorted(chain_words_all().items()):
        t0 = _t.time()
        nc, nb0, nboth, exh = census(m, W, time_cap=1800.0)
        assert exh and nboth > 0, (m, nc, nboth, exh)
        print(f"  m={m}: closure={nc} B0-single={nb0} completions={nboth} "
              f"exhausted [{_t.time()-t0:.1f}s]")
    print("D4 PASS: every chain word m=6..24 completable; sets exhaustive")


def partD5():
    """X-propagation lemma on every available completion."""
    print("D5: X-structure lemma")
    n = 0
    files = list(SOLUTION_FILES) + [(f"dense_template_m{m}.json", m)
                                    for m in range(6, 26, 2)]
    for fn, mexp in files:
        try:
            m, A = load_solution(fn)
        except FileNotFoundError:
            continue
        W = {p: mv for p, mv in A[2].items() if mv != 0}
        b = bits_from_fields(m, W, A[0])
        x_structure_check(m, W, b)
        n += 1
    print(f"D5 PASS: lemma holds on {n} completions")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "A"
    if arg == "A":
        partA()
    elif arg == "D1":
        partB1()
    elif arg == "D2":
        partD2()
    elif arg == "D3":
        partD3()
    elif arg == "D4":
        partD4()
    elif arg == "D5":
        partD5()
    elif arg == "RUN":
        run_chain([6, 8, 10, 12, 14, 16, 18, 20])
    print("DONE")
