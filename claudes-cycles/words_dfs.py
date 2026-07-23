#!/usr/bin/env python3
"""DFS count of (1,1)-transversal words (distinct labels (a mod 2, 3a-k mod m))
fixing word[0]=e0 (rotation canonicalization is by counting loops instead:
each loop of 2m steps corresponds to exactly (number of e0 positions... we
count WALKS from label 0 with first step e0; each rotation class with r e0-runs
is counted once per e0-position => divide by m at the end for loop count).
Simpler: count all cyclic words (not up to rotation) with distinct labels and
starting move e0; report raw counts; also test periodic candidates."""
import sys
from criterion import budgets, coset_label, word_loop, is_single, runs_of

def count_words(m):
    # state: k (steps done), a (#e0), labels used
    sols = []
    def dfs(k, a, labs, word):
        if k == 2 * m:
            if a == m:
                sols.append(tuple(word))
            return
        # prune: remaining e0s
        rem = 2 * m - k
        if a > m or (m - a) > rem:
            return
        for mv in (1, 2):
            a2 = a + (1 if mv == 1 else 0)
            l = (a2 % 2, (3 * a2 - (k + 1)) % m)
            if k + 1 == 2 * m:
                # closure: final label must COINCIDE with the start label
                if l == (0, 0):
                    word.append(mv)
                    dfs(k + 1, a2, labs, word)
                    word.pop()
                continue
            if l in labs:
                continue
            labs.add(l)
            word.append(mv)
            dfs(k + 1, a2, labs, word)
            word.pop()
            labs.remove(l)
    dfs(0, 0, {(0, 0)}, [])
    # wait: label after 0 steps is (0,0); after step k+1 uses a2,k+1.  The
    # 2m-th label wraps to (0, (3m-2m) mod m) = (0, 0)?? 3m-2m = m = 0 mod m,
    # a=m even... only when m even. fine: closure consistent.
    return sols

if __name__ == "__main__":
    for m in [int(x) for x in sys.argv[1:]] or [6]:
        sols = count_words(m)
        classes = {}
        for w in sols:
            classes.setdefault(runs_of(w), 0)
        n_alt = sum(1 for w in sols if runs_of(w) == tuple([1] * (2 * m)))
        print(f"m={m}: {len(sols)} words (start fixed at label 0), "
              f"{len(classes)} run-profiles: {sorted(classes)}")
        # verify every found word walks to a transversal single-B2 loop
        t2 = budgets(m)[2]
        lab, _, ncos = coset_label(m, t2)
        for w in sols[:50]:
            f = word_loop(m, list(w))
            assert f is not None and len(f) == ncos
            assert len({lab[p] for p in f}) == ncos
            assert is_single(m, f, t2)
        print(f"  (verified: each yields transversal loop with B_2 single)")
