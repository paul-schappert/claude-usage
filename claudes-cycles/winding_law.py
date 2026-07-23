#!/usr/bin/env python3
"""Phase 3: winding law for (k, k+1)-staircase gadgets, and budget redesign.

Part A (winding law, original budgets t0=(0,1), t1=(1,2), t2=(-2,-4)):
  canonical maximally-uniform (Christoffel) words of winding (k, k+1) and
  mirrors (k+1, k); for each even m in [6, 24], k in [1, m//2]:
    (a) coset coverage of <t2>, (b) B_2 single via the return map,
    (c) CP-SAT completability of cycles 0, 1 (m <= 10).
  Plus random-word statistics per (m, k) to separate "the word is wrong"
  from "the winding class is wrong".

Part B (budget freedom):
  B1: transversal dichotomy -- a winding-(w0,w1) loop can be a perfect
      transversal of <t> only if (w0+w1) | m and ord(t) = m/(w0+w1); so a
      FIXED winding works for all even m only for w0+w1 in {1, 2}, and
      w0+w1 = 1 (a plain row/column circle) is dead by the crossing identity.
      Hence (1,1) transversals + budget choice is the only uniform route.
  B2: architecture N: budgets tN = [(0, m-2), (1, 1), (m-2, 0)].
      diag11 is a perfect transversal of <(m-2, 0)> (labels (x mod 2, y)),
      so B_2 is single for every even m; the rigidity chain (which is
      budget-independent up to its last step) now forces {|I_0|, |I_1|} =
      {0, 2m} but NO parity contradiction: with t0 = (0, m-2) the empty-idle
      cycle 0 has constant level step Delta-u = -1 (a unit rotation), which
      is compatible with a single cycle.  SAT decides completability.
"""
import itertools, json, random, sys
from collections import Counter
from criterion import (SCR, MOVES, budgets, apply_B, cycle_lengths, is_single,
                       coset_label, criterion, crit_single, field_loops,
                       windings, diag11, word_loop, load_surgery,
                       sat_completion, runs_of)


# ---------------- Part A ----------------

def christoffel(m, k, mirror=False):
    """Maximally uniform cyclic word with m*k e0's and m*(k+1) e1's
    (mirror: swap letters)."""
    p, q = k, k + 1
    n = m * (p + q)
    w = []
    for i in range(n):
        e0_here = (((i + 1) * p * m) // n) > ((i * p * m) // n)
        w.append(1 if e0_here != mirror else 2)
    return w


def partA_table(mmax=24, verbose=True):
    print("A: (m, k) table for canonical Christoffel words, budgets "
          "(0,1),(1,2),(-2,-4)")
    tab = {}
    for m in range(6, mmax + 1, 2):
        t2 = budgets(m)[2]
        _, _, ncos = coset_label(m, t2)
        for k in range(1, m // 2 + 1):
            if m * (2 * k + 1) > m * m:
                continue
            for mirror in (False, True):
                w = christoffel(m, k, mirror)
                f = word_loop(m, w)
                if f is None:
                    res = "notloop"
                else:
                    cov, rc = criterion(m, f, t2)
                    if not cov:
                        res = "nocover"
                    elif len(rc) == 1:
                        res = "SINGLE"
                    else:
                        res = f"split{len(rc)}"
                tab[m, k, mirror] = res
        if verbose:
            row = "  ".join(
                f"k={k}:{tab.get((m,k,False),'-'):8s}/{tab.get((m,k,True),'-'):8s}"
                for k in range(1, m // 2 + 1) if (m, k, False) in tab)
            print(f"  m={m:2d}: {row}")
    return tab


def partA_random_stats(mmax=16, tries=4000):
    print("A2: random-word statistics: fraction of simple (k,k+1)-loops "
          "with B_2 single")
    for m in range(6, mmax + 1, 2):
        t2 = budgets(m)[2]
        row = []
        for k in range(1, m // 2 + 1):
            if m * (2 * k + 1) > m * m:
                continue
            rng = random.Random(97 * m + k)
            loops = singles = 0
            for _ in range(tries):
                w = [1] * (m * k) + [2] * (m * (k + 1))
                rng.shuffle(w)
                f = word_loop(m, w)
                if f is None:
                    continue
                loops += 1
                if is_single(m, f, t2):
                    singles += 1
            row.append(f"k={k}:{singles}/{loops}")
        print(f"  m={m:2d}: " + "  ".join(row))


def partA_sat(ms=(6, 8, 10), tl=300.0, tries=6000):
    print("A3: completability by winding class (SAT).  For each (m, k): "
          "take the Christoffel word if it is B_2-single, else up to 3 "
          "random B_2-single words of that winding; report completability.")
    for m in ms:
        t2 = budgets(m)[2]
        for k in range(1, m // 2 + 1):
            cands = []
            for mirror in (False, True):
                w = christoffel(m, k, mirror)
                f = word_loop(m, w)
                if f is not None and is_single(m, f, t2):
                    cands.append(("christoffel" + ("T" if mirror else ""), f))
            rng = random.Random(555 * m + k)
            got = 0
            t = 0
            while got < 3 and t < tries:
                t += 1
                w = [1] * (m * k) + [2] * (m * (k + 1))
                rng.shuffle(w)
                f = word_loop(m, w)
                if f is not None and is_single(m, f, t2):
                    cands.append((f"rand{got}", f))
                    got += 1
            if not cands:
                print(f"  m={m} k={k}: no B_2-single word found "
                      f"({t} tries)")
                continue
            outs = []
            done = False
            for name, f in cands:
                st, sol = sat_completion(m, f, require=("B0", "B1"),
                                         time_limit=tl)
                outs.append(f"{name}:{st}")
                if sol:
                    A0, A1 = sol
                    ts = budgets(m)
                    assert is_single(m, A0, ts[0]) and is_single(m, A1, ts[1])
                    json.dump({str(p): [A0[p], A1[p], f.get(p, 0)]
                               for p in itertools.product(range(m), repeat=2)},
                              open(f"{SCR}/wlaw_completion_m{m}_k{k}.json", "w"))
                    done = True
                    break
            print(f"  m={m} k={k}: " + "  ".join(outs) +
                  ("  [saved]" if done else ""), flush=True)


# ---------------- Part B ----------------

def tN(m):
    return [(0, m - 2), (1, 1), (m - 2, 0)]


def partB1():
    print("B1: transversal dichotomy (machine check of the order condition)")
    for m in range(6, 25, 2):
        # orders realizable by elements of Z_m^2 are divisors of m;
        # a (k,k+1) transversal needs ord(t) = m/(2k+1):
        poss = [k for k in range(1, m // 2 + 1) if m % (2 * k + 1) == 0]
        print(f"  m={m:2d}: windings (k,k+1) admitting a perfect transversal "
              f"budget: k in {poss if poss else 'NONE beyond (1,1)? '} "
              f"(k=... requires (2k+1)|m)")


def partB2_verify(mmax=40):
    print("B2: architecture N: diag11 under budgets tN(m) = "
          "[(0,m-2),(1,1),(m-2,0)]")
    for m in range(4, mmax + 1, 2):
        t2 = tN(m)[2]
        f = diag11(m)
        lab, o, ncos = coset_label(m, t2)
        assert o == m // 2 and ncos == 2 * m
        S = list(f)
        assert len({lab[p] for p in S}) == 2 * m, f"m={m}: not transversal"
        assert is_single(m, f, t2), f"m={m}: B_2 not single"
    print(f"  diag11 is a perfect transversal of <(m-2,0)> and B_2 is a "
          f"single m^2-cycle for every even m <= {mmax}  [verified]")
    # budget sanity: lifts sum to m-1 in both coordinates, no (0,0) pair
    for m in range(4, mmax + 1, 2):
        ts = tN(m)
        assert sum(a for a, b in ts) == m - 1 and sum(b for a, b in ts) == m - 1
        assert all(t != (0, 0) for t in ts)
    print("  budget lifts sum to (m-1, m-1); no (0,0) pair  [verified]")


def partB2_sat(ms=(6, 8), tl=600.0):
    print("B3: SAT completability of diag11 under budgets tN")
    for m in ms:
        f2 = diag11(m)
        st, sol = sat_completion(m, f2, require=("B0", "B1"),
                                 time_limit=tl, ts=tN(m))
        print(f"  m={m}: {st}", flush=True)
        if sol:
            A0, A1 = sol
            ts = tN(m)
            ok = (is_single(m, A0, ts[0]) and is_single(m, A1, ts[1])
                  and is_single(m, f2, ts[2]))
            i0 = sum(1 for p in A0 if A0[p] == 0)
            i1 = sum(1 for p in A1 if A1[p] == 0)
            l0 = field_loops(m, A0)
            l1 = field_loops(m, A1)
            print(f"    verified all single: {ok}; |I0|,|I1|={i0},{i1}; "
                  f"windings A0={windings(m, A0)} A1={windings(m, A1)}; "
                  f"loops={len(l0)},{len(l1)}")
            json.dump({str(p): [A0[p], A1[p], f2.get(p, 0)]
                       for p in itertools.product(range(m), repeat=2)},
                      open(f"{SCR}/archN_diag11_m{m}.json", "w"))


if __name__ == "__main__":
    which = sys.argv[1:] or ["A"]
    if "A" in which:
        partA_table()
    if "A2" in which:
        partA_random_stats()
    if "A3" in which:
        partA_sat()
    if "B" in which:
        partB1()
        partB2_verify()
    if "B3" in which:
        partB2_sat()
    if "B3big" in which:
        partB2_sat(ms=(10, 12), tl=1800.0)
    print("DONE")
