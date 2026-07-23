#!/usr/bin/env python3
"""Scan ALL schedulable budget matrices with t_2 = (2,4) at m = 8, 10:
for each, run the parametric closure census on the narrow-tree words.
Goal: find (t_0, t_1) residue families under which narrow words complete."""
import itertools, json, sys, time
SCR = "/tmp/claude-0/-home-user-claude-usage/e5933da4-9bfd-5e34-89c1-d01da7b77644/scratchpad/claudes-cycles"
sys.path.insert(0, SCR)
from criterion import word_loop, is_single
from dense_template2 import census2
from narrow_census import seeds_m6
from insertion_lemma import narrow_data, child


def tree_words(m):
    level = [(si, "", w) for si, w in enumerate(seeds_m6())]
    mm = 6
    while mm < m:
        nxt = []
        for si, br, w in level:
            _, _, _, _, mp = narrow_data(list(w), mm)
            for e in (0, 1):
                p = mp[e][0]
                nxt.append((si, br + str(e), list(child(w, p, p))))
        level = nxt
        mm += 2
    return level


def all_budgets_t2(m, t2=(2, 4)):
    """All schedulable integer budget matrices with cycle-2 lifts = t2."""
    a2, b2 = t2
    out = []
    for a0 in range(m - 1 - a2 + 1):
        a1 = m - 1 - a2 - a0
        for b0 in range(m - 1 - b2 + 1):
            b1 = m - 1 - b2 - b0
            a = [a0, a1, a2]
            b = [b0, b1, b2]
            if any(a[c] + b[c] > m - 1 for c in range(3)):
                continue
            if any(a[c] == 0 and b[c] == 0 for c in range(3)):
                continue
            out.append((a, b))
    return out


def scan(m, nwords=None, time_cap=120.0):
    words = tree_words(m)
    if nwords:
        words = words[:nwords]
    buds = all_budgets_t2(m)
    print(f"m={m}: {len(words)} narrow words x {len(buds)} schedulable "
          f"budget matrices (t_2 = (2,4))", flush=True)
    results = {}
    for a, b in buds:
        ts = [(a[c] % m, b[c] % m) for c in range(3)]
        tot = 0
        percomp = []
        for si, br, w in words:
            f = word_loop(m, list(w))
            assert f is not None and is_single(m, f, ts[2])
            nc, nb0, nboth, exh, _ = census2(m, f, ts, time_cap=time_cap)
            if not exh:
                print(f"  ts={ts} word ({si},{br}): NOT EXHAUSTED "
                      f"(closure>= {nc})", flush=True)
            if nboth > 0:
                tot += 1
                percomp.append((si, br, nboth))
        results[str((tuple(a), tuple(b)))] = (tot, percomp)
        print(f"  a={a} b={b} ts={ts}: {tot}/{len(words)} words completable"
              + (f"  {percomp[:6]}" if percomp else ""), flush=True)
    json.dump(results, open(f"{SCR}/budget_scan2_m{m}.json", "w"))


if __name__ == "__main__":
    m = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    scan(m)
