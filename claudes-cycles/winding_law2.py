#!/usr/bin/env python3
"""Extended winding-law experiments.
E1: does winding (k,k+1) admit ANY B_2-single word at larger m?  Random-DFS
    generator that builds self-avoiding closed staircase loops (uniform-ish),
    so high windings get real samples.  Record existence fractions.
E2: SAT completability at m=12 (k=1 if a single word is found, k=2).
E3: coset multiplicity profiles of the B_2-single words (law hunting).
"""
import itertools, json, random, sys
from collections import Counter
from criterion import (SCR, MOVES, budgets, is_single, coset_label, criterion,
                       field_loops, windings, word_loop, sat_completion,
                       runs_of)


def rand_loop_dfs(m, k, rng, maxtries=400):
    """Random self-avoiding closed staircase with winding (k, k+1) via
    randomized DFS from (0,0)."""
    n0, n1 = m * k, m * (k + 1)
    for _ in range(maxtries):
        path = {}
        p = (0, 0)
        a = b = 0
        stack = []
        # iterative randomized greedy with limited backtracking
        ok = True
        while a + b < n0 + n1:
            choices = []
            if a < n0:
                choices.append(1)
            if b < n1:
                choices.append(2)
            rng.shuffle(choices)
            placed = False
            for mv in choices:
                dx, dy = MOVES[mv]
                q = ((p[0] + dx) % m, (p[1] + dy) % m)
                steps_left = n0 + n1 - (a + b) - 1
                if q in path and not (steps_left == 0 and q == (0, 0)):
                    continue
                if steps_left == 0 and q != (0, 0):
                    continue
                path[p] = mv
                p = q
                a += mv == 1
                b += mv == 2
                placed = True
                break
            if not placed:
                ok = False
                break
        if ok and p == (0, 0) and len(path) == n0 + n1:
            return path
    return None


def e1_existence(pairs, tries=300):
    print("E1: existence of B_2-single (k,k+1)-words (randomized-DFS loops)")
    for m, k in pairs:
        t2 = budgets(m)[2]
        rng = random.Random(31 * m + k)
        loops = singles = 0
        best = None
        for _ in range(tries):
            f = rand_loop_dfs(m, k, rng)
            if f is None:
                continue
            loops += 1
            if is_single(m, f, t2):
                singles += 1
                if best is None:
                    best = f
        prof = None
        if best is not None:
            lab, _, _ = coset_label(m, t2)
            prof = dict(Counter(Counter(lab[p] for p in best).values()))
        print(f"  m={m:2d} k={k}: singles {singles}/{loops} loops"
              + (f"   sample profile {prof}" if prof else ""), flush=True)


def e2_m12(tl=1200.0):
    print("E2: SAT completability at m=12")
    m = 12
    t2 = budgets(m)[2]
    for k in (2, 3):
        rng = random.Random(777 + k)
        got = []
        t = 0
        while len(got) < 3 and t < 4000:
            t += 1
            f = rand_loop_dfs(m, k, rng, maxtries=1)
            if f is not None and is_single(m, f, t2):
                got.append(f)
        print(f"  k={k}: found {len(got)} B_2-single words ({t} DFS tries)")
        for i, f in enumerate(got):
            st, sol = sat_completion(m, f, require=("B0", "B1"),
                                     time_limit=tl)
            print(f"    word {i}: {st}", flush=True)
            if sol:
                A0, A1 = sol
                ts = budgets(m)
                assert is_single(m, A0, ts[0]) and is_single(m, A1, ts[1])
                json.dump({str(p): [A0[p], A1[p], f.get(p, 0)]
                           for p in itertools.product(range(m), repeat=2)},
                          open(f"{SCR}/wlaw_completion_m12_k{k}.json", "w"))
                break


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "E1"
    if which == "E1":
        e1_existence([(12, 1), (14, 1), (16, 1),
                      (14, 2), (16, 2), (18, 2), (20, 2), (22, 2), (24, 2),
                      (12, 3), (16, 3), (20, 3), (24, 3),
                      (20, 4), (24, 4), (28, 4)])
    elif which == "E2":
        e2_m12()
    print("DONE")
