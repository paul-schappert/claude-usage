#!/usr/bin/env python3
"""Reduced gadget problem on Z_m^2 for the single-swap-fiber architecture.

Find move-fields A_0, A_1, A_2 on Z_m^2 (pointwise partition of
{id, +e0, +e1}) and budgets (a_c, b_c) with sum_c a_c = sum_c b_c = m-1,
such that B_c : p -> p + move_c(p) + (a_c, b_c) is a single m^2-cycle for
each c.  Each solution corresponds to a Hamilton decomposition of D_3(m)
whose fibers are uniform except one.

Search: outer enumeration of budgets, CP-SAT with AddCircuit for the fields.
Optionally minimize the number of non-idle points of cycle 0 ("minimal
gadget") to force structure.
"""
import itertools
import json
import sys
import time

from ortools.sat.python import cp_model

MOVES = [(0, 0), (1, 0), (0, 1)]  # id, e0, e1


def solve_gadget(m, budgets, time_limit=60.0, minimize=None, workers=4):
    """budgets: [(a0,b0),(a1,b1),(a2,b2)].  minimize: None or 'moves0'
    (minimize # points where cycle 0 doesn't idle)."""
    pts = list(itertools.product(range(m), repeat=2))
    pid = {p: i for i, p in enumerate(pts)}
    model = cp_model.CpModel()
    y = {}
    for p in pts:
        for c in range(3):
            for mv in range(3):
                y[p, c, mv] = model.NewBoolVar(f"y{pid[p]}_{c}_{mv}")
        for c in range(3):
            model.AddExactlyOne([y[p, c, mv] for mv in range(3)])
        for mv in range(3):
            model.AddExactlyOne([y[p, c, mv] for c in range(3)])
    for c, (ac, bc) in enumerate(budgets):
        arcs = []
        for p in pts:
            for mv, (dx, dy) in enumerate(MOVES):
                q = ((p[0] + dx + ac) % m, (p[1] + dy + bc) % m)
                if q == p:
                    # AddCircuit reads a chosen self-loop as "skip this node",
                    # which would silently break Hamiltonicity: forbid it.
                    model.Add(y[p, c, mv] == 0)
                else:
                    arcs.append((pid[p], pid[q], y[p, c, mv]))
        model.AddCircuit(arcs)
    if minimize == 'moves0':
        model.Minimize(sum(1 - y[p, 0, 0] for p in pts))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = workers
    st = solver.Solve(model)
    name = solver.StatusName(st)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        fields = {}
        for p in pts:
            fields[p] = tuple(next(mv for mv in range(3) if solver.Value(y[p, c, mv]))
                              for c in range(3))
        obj = solver.ObjectiveValue() if minimize else None
        return name, fields, obj
    return name, None, None


def verify_gadget(m, budgets, fields):
    """Independent check that each B_c is a single m^2-cycle and fields
    partition moves pointwise."""
    pts = list(itertools.product(range(m), repeat=2))
    for p in pts:
        if sorted(fields[p]) != [0, 1, 2]:
            return False
    for c, (ac, bc) in enumerate(budgets):
        start = (0, 0)
        cur = start
        cnt = 0
        while True:
            dx, dy = MOVES[fields[cur][c]]
            cur = ((cur[0] + dx + ac) % m, (cur[1] + dy + bc) % m)
            cnt += 1
            if cur == start:
                break
            if cnt > m * m:
                return False
        if cnt != m * m:
            return False
    return True


def budget_scan(m, time_limit=20.0):
    """Which budget triples admit gadgets?  Returns list of feasible ones."""
    t = m - 1
    comps = [(x, y_, t - x - y_) for x in range(t + 1) for y_ in range(t + 1 - x)]
    feas = []
    tried = 0
    for A in comps:
        for B in comps:
            budgets = list(zip(A, B))
            # canonical form under cycle relabeling to cut symmetry
            if budgets != min([sorted(budgets)[i:] + sorted(budgets)[:i]
                               for i in range(1)][0:1][0] if False else budgets):
                pass
            tried += 1
            name, fields, _ = solve_gadget(m, budgets, time_limit=time_limit)
            if fields is not None:
                assert verify_gadget(m, budgets, fields)
                feas.append(budgets)
    return feas, tried


if __name__ == "__main__":
    m = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    t0 = time.time()
    feas, tried = budget_scan(m)
    print(f"m={m}: {len(feas)}/{tried} budget triples feasible "
          f"({time.time()-t0:.0f}s)", flush=True)
    for b in feas:
        print("  ", b, flush=True)
    json.dump([[list(x) for x in b] for b in feas],
              open(f"budgets_m{m}.json", "w"))
