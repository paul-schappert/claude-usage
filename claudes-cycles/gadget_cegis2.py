#!/usr/bin/env python3
"""Gadget CEGIS round 2: diagonal-structured classifiers."""
import itertools, json, time
from ortools.sat.python import cp_model
from reduced_gadget import MOVES, verify_gadget

PERMS = list(itertools.permutations(range(3)))

def clsx(a, b, parity=True):
    def f(x, m):
        if x < a: return f"L{x}"
        if x >= m - b: return f"H{m-x}"
        return ("GO" if x % 2 else "GE") if parity else "G"
    return f

C22 = clsx(2, 2); C11 = clsx(1, 1); C33 = clsx(3, 3)

SCHEMES = {
    "ij_u":   lambda p, m: (C22(p[0], m), C22(p[1], m), C11((p[0]+p[1]) % m, m)),
    "ij_v":   lambda p, m: (C22(p[0], m), C22(p[1], m), C11((p[0]-p[1]) % m, m)),
    "uv":     lambda p, m: (C22((p[0]+p[1]) % m, m), C22((p[0]-p[1]) % m, m)),
    "v_ipar": lambda p, m: (C22((p[0]-p[1]) % m, m), p[0] % 2),
    "u_ipar": lambda p, m: (C22((p[0]+p[1]) % m, m), p[0] % 2),
    "uv_ipar": lambda p, m: (C22((p[0]+p[1]) % m, m), C22((p[0]-p[1]) % m, m), p[0] % 2),
    "kitchen": lambda p, m: (C33(p[0], m), C33(p[1], m), C22((p[0]+p[1]) % m, m), C22((p[0]-p[1]) % m, m)),
}

def budget_families(m):
    return {
        "fam1": [(0, 1), (1, 2), ((-2) % m, (-4) % m)],
        "fam2": [(0, 2), (2, 1), ((-3) % m, (-4) % m)],
    }

def solve_joint(ms, keyf, budf, time_limit=600, workers=4):
    model = cp_model.CpModel()
    combos = set()
    per_m = {}
    for m in ms:
        pts = list(itertools.product(range(m), repeat=2))
        keyed = [(p, keyf(p, m)) for p in pts]
        per_m[m] = keyed
        combos.update(k for _, k in keyed)
    t = {k: [model.NewBoolVar(f"t{k}_{p}") for p in range(6)] for k in combos}
    for k in combos:
        model.AddExactlyOne(t[k])
    for m in ms:
        pid = {p: i for i, (p, _) in enumerate(per_m[m])}
        y = {}
        for p, k in per_m[m]:
            for c in range(3):
                for mv in range(3):
                    lit = model.NewBoolVar(f"y{m}_{pid[p]}_{c}_{mv}")
                    sel = [t[k][pi] for pi in range(6) if PERMS[pi][c] == mv]
                    model.Add(sum(sel) == 1).OnlyEnforceIf(lit)
                    model.Add(sum(sel) == 0).OnlyEnforceIf(lit.Not())
                    y[p, c, mv] = lit
        for c, (ac, bc) in enumerate(budf(m)):
            arcs = []
            for p, _ in per_m[m]:
                for mv, (dx, dy) in enumerate(MOVES):
                    q = ((p[0]+dx+ac) % m, (p[1]+dy+bc) % m)
                    if q == p:
                        model.Add(y[p, c, mv] == 0)
                    else:
                        arcs.append((pid[p], pid[q], y[p, c, mv]))
            model.AddCircuit(arcs)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = workers
    st = solver.Solve(model)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return solver.StatusName(st), {k: PERMS[next(pi for pi in range(6) if solver.Value(t[k][pi]))] for k in combos}
    return solver.StatusName(st), None

def test_table(table, m, keyf, budgets):
    f = {}
    for p in itertools.product(range(m), repeat=2):
        k = keyf(p, m)
        if k not in table:
            return False
        f[p] = table[k]
    return verify_gadget(m, budgets, f)

def run():
    for famname in ("fam1", "fam2"):
        budf = lambda m, fn=famname: budget_families(m)[fn]
        for sname, keyf in SCHEMES.items():
            ms = [6, 8, 10]
            ok_scheme = True
            for _ in range(8):
                t0 = time.time()
                status, table = solve_joint(ms, keyf, budf)
                print(f"[{famname}/{sname}] train={ms}: {status} ({time.time()-t0:.0f}s)", flush=True)
                if table is None:
                    ok_scheme = False
                    break
                bad = None
                for mt in range(6, 61, 2):
                    if not test_table(table, mt, keyf, budf(mt)):
                        bad = mt
                        break
                if bad is None:
                    fn = f"gadget_GENERAL_{famname}_{sname}.json"
                    json.dump({str(k): v for k, v in table.items()}, open(fn, "w"), indent=1)
                    print(f"*** [{famname}/{sname}] GENERALIZES all even m in [6,60]; saved {fn} ***", flush=True)
                    for k in sorted(table):
                        print(f"    {k}: {table[k]}", flush=True)
                    return
                print(f"  fails at m={bad}; adding", flush=True)
                if bad in ms:
                    ok_scheme = False
                    break
                ms.append(bad)
            if not ok_scheme:
                continue
    print("round-2 schemes exhausted", flush=True)

if __name__ == "__main__":
    run()
