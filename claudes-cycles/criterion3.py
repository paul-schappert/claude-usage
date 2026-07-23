#!/usr/bin/env python3
"""W5: which (1,2)-winding 3m-word gadgets admit completions at m=6,8?
Collect completable words, look for a family uniform in m.  Also print the
exact cyclic words of the ground-truth A_2 gadgets."""
import itertools, json, random, sys
from collections import Counter
from criterion import (SCR, budgets, is_single, coset_label, criterion,
                       field_loops, windings, word_loop, load_surgery,
                       sat_completion, runs_of)


def loop_word(m, f):
    loops = field_loops(m, f)
    assert len(loops) == 1
    loop = loops[0]
    return loop[0], tuple(f[p] for p in loop)


def canon(word):
    rots = [tuple(word[i:] + word[:i]) for i in range(len(word))]
    return min(rots)


def w5_completable_words(m, n_candidates=40, tl=90.0, transpose_ok=True):
    t2 = budgets(m)[2]
    rng = random.Random(1000 + m)
    cands, seen = [], set()
    tried = 0
    while len(cands) < n_candidates and tried < 60000:
        tried += 1
        word = [1] * m + [2] * (2 * m)
        rng.shuffle(word)
        f = word_loop(m, word)
        if f is None:
            continue
        if not is_single(m, f, t2):
            continue
        c = canon(list(word))
        if c in seen:
            continue
        seen.add(c)
        cands.append((c, f))
    print(f"m={m}: {len(cands)} distinct B_2-single (1,2)-word gadgets "
          f"from {tried} tries; testing completability...")
    good, bad = [], []
    for c, f in cands:
        st, sol = sat_completion(m, f, require=("B0", "B1"), time_limit=tl)
        (good if sol else bad).append((c, st))
        tag = "OK " if sol else ("?? " if st == "UNKNOWN" else "no ")
        print(f"  {tag} runs={runs_of(c)} {st}", flush=True)
    print(f"m={m}: completable {len(good)} / {len(cands)}")
    return good, bad


if __name__ == "__main__":
    for m in (6, 8):
        A2 = load_surgery(m)[2]
        start, w = loop_word(m, A2)
        print(f"ground truth m={m}: A_2 word (canon) = {canon(list(w))} "
              f"winding={windings(m, A2)}")
    args = sys.argv[1:]
    m = int(args[0]) if args else 6
    n = int(args[1]) if len(args) > 1 else 40
    tl = float(args[2]) if len(args) > 2 else 90.0
    w5_completable_words(m, n, tl)
    print("DONE")
