#!/usr/bin/env python3
"""CP-SAT search for Hamilton arc-decompositions of the directed d-torus D_d(m).

D_d(m): vertices (Z_m)^d, arcs v -> v + e_b (mod m) for each of the d unit
vectors e_b.  Goal: partition the d*m^d arcs into d arc-disjoint directed
Hamiltonian cycles.

Encoding: for each vertex v, each cycle c picks exactly one out-direction
x[v,c,b]; each direction b at v is used by exactly one cycle (so the per-vertex
assignment is a permutation of directions); AddCircuit forces each cycle's
functional digraph to be a single Hamiltonian circuit.

Every solution is re-verified by an independent pure-Python checker.
"""
import itertools
import json
import sys
import time

from ortools.sat.python import cp_model


def verts_of(d, m):
    return list(itertools.product(range(m), repeat=d))


def bump(v, b, m):
    w = list(v)
    w[b] = (w[b] + 1) % m
    return tuple(w)


def solve(d, m, time_limit=300.0, workers=4, fix_origin=True, log=False):
    """Return (status_str, perm) where perm maps vertex -> tuple p with
    p[c] = direction cycle c takes at that vertex, or None if no solution."""
    verts = verts_of(d, m)
    vid = {v: i for i, v in enumerate(verts)}
    model = cp_model.CpModel()
    x = {}
    for v in verts:
        for c in range(d):
            for b in range(d):
                x[v, c, b] = model.NewBoolVar(f"x{vid[v]}_{c}_{b}")
    for v in verts:
        for c in range(d):
            model.AddExactlyOne([x[v, c, b] for b in range(d)])
        for b in range(d):
            model.AddExactlyOne([x[v, c, b] for c in range(d)])
    # symmetry breaking: cycle c leaves the origin in direction c
    if fix_origin:
        origin = tuple([0] * d)
        for c in range(d):
            model.Add(x[origin, c, c] == 1)
    for c in range(d):
        arcs = []
        for v in verts:
            for b in range(d):
                arcs.append((vid[v], vid[bump(v, b, m)], x[v, c, b]))
        model.AddCircuit(arcs)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = workers
    if log:
        solver.parameters.log_search_progress = True
    status = solver.Solve(model)
    name = solver.StatusName(status)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        perm = {}
        for v in verts:
            p = []
            for c in range(d):
                dir_c = [b for b in range(d) if solver.Value(x[v, c, b])]
                assert len(dir_c) == 1
                p.append(dir_c[0])
            perm[v] = tuple(p)
        return name, perm
    return name, None


def check(d, m, perm):
    """Independent verifier: perm[v][c] = direction of cycle c at v.
    Checks (1) per-vertex direction assignment is a permutation,
    (2) each cycle is a single m^d-cycle, (3) arcs partition (implied by 1)."""
    verts = verts_of(d, m)
    n = m ** d
    for v in verts:
        if sorted(perm[v]) != list(range(d)):
            return False, f"vertex {v}: directions {perm[v]} not a permutation"
    for c in range(d):
        v = verts[0]
        seen = 0
        cur = v
        while True:
            cur = bump(cur, perm[cur][c], m)
            seen += 1
            if cur == v:
                break
            if seen > n:
                return False, f"cycle {c}: runaway"
        if seen != n:
            return False, f"cycle {c}: length {seen} != {n}"
    return True, "ok"


def main():
    cases = []
    for arg in sys.argv[1:]:
        dd, mm = arg.split(",")
        cases.append((int(dd), int(mm)))
    if not cases:
        cases = [(3, 4)]
    results = {}
    for d, m in cases:
        t0 = time.time()
        status, perm = solve(d, m)
        dt = time.time() - t0
        line = f"D_{d}({m}): {status} in {dt:.1f}s"
        if perm is not None:
            ok, msg = check(d, m, perm)
            line += f"  verified={ok} ({msg})"
            if ok:
                fn = f"solution_d{d}_m{m}.json"
                with open(fn, "w") as fh:
                    json.dump({str(v): perm[v] for v in perm}, fh)
                line += f"  saved={fn}"
        print(line, flush=True)
        results[(d, m)] = status
    return results


if __name__ == "__main__":
    main()
