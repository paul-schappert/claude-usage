#!/usr/bin/env python3
"""Search for class-based rule tables giving Hamilton decompositions of D_3(m)
for all even m simultaneously.

A rule table T assigns to each class-combo (class(i), class(j), class(s)) a
permutation p in S_3; cycle c at vertex (i,j,k) moves in direction p[c],
where s = (i+j+k) mod m.  Directions: 0 = bump i, 1 = bump j, 2 = bump k.

Class schemes classify a coordinate x in Z_m by:
  - explicit low values 0..a-1  -> 'L0','L1',...
  - explicit high values m-b..m-1 -> 'Hb',...,'H1'  (H1 = m-1)
  - generic middle split by parity -> 'GE' (even) / 'GO' (odd)
For even m all classes have consistent parity across different m, which is
what makes a single table potentially valid for every even m.

CP-SAT decides whether one table works jointly for a list of moduli.
"""
import itertools
import json
import sys
import time

from ortools.sat.python import cp_model

PERMS = list(itertools.permutations(range(3)))  # S_3, 6 elements


def make_classifier(a, b, parity):
    """Classify x in Z_m. a explicit low values, b explicit high values,
    generic middle split by parity (if parity=True)."""
    def cls(x, m):
        if x < a:
            return f"L{x}"
        if x >= m - b:
            return f"H{m - x}"
        return ("GO" if x % 2 else "GE") if parity else "G"
    return cls


def solve_table(ms, a, b, parity, time_limit=600.0, workers=4,
                use_k=False, verbose=False):
    """Find a table valid for all m in ms. Returns (status, table or None).
    Table keys: (ci, cj, cs) or (ci, cj, cs, ck) -> perm tuple."""
    cls = make_classifier(a, b, parity)
    model = cp_model.CpModel()

    # collect the class-combos actually inhabited for the given moduli
    combos = set()
    per_m_vertices = {}
    for m in ms:
        vs = []
        for i, j, k in itertools.product(range(m), repeat=3):
            s = (i + j + k) % m
            key = (cls(i, m), cls(j, m), cls(s, m)) + ((cls(k, m),) if use_k else ())
            vs.append(((i, j, k), key))
            combos.add(key)
        per_m_vertices[m] = vs

    t = {}  # t[key][pidx] bool
    for key in combos:
        t[key] = [model.NewBoolVar(f"t_{key}_{p}") for p in range(6)]
        model.AddExactlyOne(t[key])

    for m in ms:
        vid = {}
        verts = [v for v, _ in per_m_vertices[m]]
        for idx, v in enumerate(verts):
            vid[v] = idx
        # arc literals per cycle
        y = {}
        for (v, key) in per_m_vertices[m]:
            for c in range(3):
                for bdir in range(3):
                    lit = model.NewBoolVar(f"y{m}_{vid[v]}_{c}_{bdir}")
                    # lit == OR of t[key][p] for perms p with p[c]==bdir
                    sel = [t[key][p] for p in range(6) if PERMS[p][c] == bdir]
                    model.Add(sum(sel) == 1).OnlyEnforceIf(lit)
                    model.Add(sum(sel) == 0).OnlyEnforceIf(lit.Not())
                    y[v, c, bdir] = lit
        def bumpv(v, bdir):
            w = list(v)
            w[bdir] = (w[bdir] + 1) % m
            return tuple(w)
        for c in range(3):
            arcs = []
            for v in verts:
                for bdir in range(3):
                    arcs.append((vid[v], vid[bumpv(v, bdir)], y[v, c, bdir]))
            model.AddCircuit(arcs)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = workers
    if verbose:
        solver.parameters.log_search_progress = True
    status = solver.Solve(model)
    name = solver.StatusName(status)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        table = {}
        for key in combos:
            p = [pi for pi in range(6) if solver.Value(t[key][pi])]
            table[key] = PERMS[p[0]]
        return name, table
    return name, None


def simulate(table, m, a, b, parity, use_k=False):
    """Check the table's decomposition on D_3(m) directly. True if valid."""
    cls = make_classifier(a, b, parity)
    n = m ** 3
    for c in range(3):
        v = (0, 0, 0)
        cur = v
        cnt = 0
        while True:
            i, j, k = cur
            s = (i + j + k) % m
            key = (cls(i, m), cls(j, m), cls(s, m)) + ((cls(k, m),) if use_k else ())
            if key not in table:
                return False, f"m={m}: uninhabited combo {key} reached"
            d = table[key][c]
            w = list(cur)
            w[d] = (w[d] + 1) % m
            cur = tuple(w)
            cnt += 1
            if cur == v:
                break
            if cnt > n:
                return False, f"m={m} cycle {c}: runaway"
        if cnt != n:
            return False, f"m={m} cycle {c}: length {cnt} != {n}"
    return True, "ok"


def main():
    ms = [int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "4,6,8").split(",")]
    schemes = []
    for a, b, parity, use_k in [
        (1, 1, False, False),   # Knuth's original classes {0, G, m-1}
        (1, 1, True, False),    # + parity in the middle
        (2, 2, True, False),    # + explicit 1 and m-2
        (2, 2, True, True),     # + class(k)
        (3, 3, True, False),
        (3, 3, True, True),
    ]:
        schemes.append((a, b, parity, use_k))
    for a, b, parity, use_k in schemes:
        t0 = time.time()
        status, table = solve_table(ms, a, b, parity, use_k=use_k)
        dt = time.time() - t0
        tag = f"a={a} b={b} parity={parity} use_k={use_k}"
        print(f"[{tag}] ms={ms}: {status} in {dt:.1f}s", flush=True)
        if table is not None:
            # test generalization on larger even m
            good = []
            for mtest in range(4, 41, 2):
                ok, msg = simulate(table, mtest, a, b, parity, use_k)
                if not ok:
                    print(f"  generalization FAILS at {msg}", flush=True)
                    break
                good.append(mtest)
            else:
                print(f"  GENERALIZES for even m in {good}", flush=True)
                fn = f"table_a{a}b{b}p{int(parity)}k{int(use_k)}.json"
                with open(fn, "w") as fh:
                    json.dump({str(k): v for k, v in table.items()}, fh, indent=1)
                print(f"  saved {fn}", flush=True)
                return
            # save even failing tables for analysis
            fn = f"table_partial_a{a}b{b}p{int(parity)}k{int(use_k)}.json"
            with open(fn, "w") as fh:
                json.dump({str(k): v for k, v in table.items()}, fh, indent=1)


if __name__ == "__main__":
    main()
