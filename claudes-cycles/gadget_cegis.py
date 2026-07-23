#!/usr/bin/env python3
"""CEGIS for class-based gadget tables on the reduced problem, with the
constant budget family ((0,1),(1,2),(-2,-4)) mod m."""
import itertools, json, sys, time
from ortools.sat.python import cp_model
from reduced_gadget import MOVES, verify_gadget

PERMS = list(itertools.permutations(range(3)))

def budgets_of(m):
    return [(0, 1), (1, 2), ((-2) % m, (-4) % m)]

def make_cls(a, b):
    def cls(x, m):
        if x < a: return f"L{x}"
        if x >= m - b: return f"H{m-x}"
        return "GO" if x % 2 else "GE"
    return cls

def solve_joint(ms, a, b, time_limit=900, workers=4):
    cls = make_cls(a, b)
    model = cp_model.CpModel()
    combos = set()
    per_m = {}
    for m in ms:
        pts = list(itertools.product(range(m), repeat=2))
        keyed = [((i, j), (cls(i, m), cls(j, m))) for i, j in pts]
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
        for c, (ac, bc) in enumerate(budgets_of(m)):
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

def table_fields(table, m, a, b):
    cls = make_cls(a, b)
    return {(i, j): table[(cls(i, m), cls(j, m))]
            for i, j in itertools.product(range(m), repeat=2)}

def test_table(table, m, a, b):
    f = table_fields(table, m, a, b)
    return verify_gadget(m, budgets_of(m), f)

def run(a, b, tmax=60):
    ms = [6, 8, 10]
    for _ in range(10):
        t0 = time.time()
        status, table = solve_joint(ms, a, b)
        print(f"a={a} b={b} train={ms}: {status} ({time.time()-t0:.0f}s)", flush=True)
        if table is None:
            return False
        bad = None
        for mt in range(6, tmax + 1, 2):
            if not test_table(table, mt, a, b):
                bad = mt
                break
        if bad is None:
            fn = f"gadget_table_GENERAL_a{a}b{b}.json"
            json.dump({str(k): table[k] for k in table}, open(fn, "w"), indent=1)
            print(f"*** table generalizes to all even m in [6,{tmax}]; saved {fn} ***", flush=True)
            for k in sorted(table):
                print(f"   {k}: {table[k]}", flush=True)
            return True
        print(f"  fails at m={bad}; adding to training set", flush=True)
        if bad in ms:
            print("  already trained on it?!; abort", flush=True)
            return False
        ms.append(bad)
    return False

if __name__ == "__main__":
    for (a, b) in [(2, 2), (3, 3), (4, 4)]:
        if run(a, b):
            break
