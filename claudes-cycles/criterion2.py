#!/usr/bin/env python3
"""Follow-up experiments: transversal word landscape, completability of the
non-alternating m=6 transversal gadgets, structure of the ground-truth A_2
gadgets, and (1,2)-word gadget search at m=10."""
import itertools, json, random, sys
from collections import Counter
from criterion import (SCR, MOVES, budgets, apply_B, cycle_lengths, is_single,
                       coset_label, criterion, crit_single, field_loops,
                       windings, diag11, word_loop, load_surgery,
                       sat_completion, valid_words, runs_of, straight_sets)


def w1_word_landscape():
    print("W1: all (1,1)-transversal words (rotation classes), m=4..12")
    for m in (4, 6, 8, 10, 12):
        words = valid_words(m)
        profs = sorted(runs_of(w) for w in words)
        print(f"  m={m}: {len(words)} classes; run profiles: {profs}")


def w2_complete_m6_words():
    print("W2: SAT completion around every m=6 (1,1)-transversal gadget")
    m = 6
    for w in valid_words(m):
        f2 = word_loop(m, list(w))
        assert f2 is not None and is_single(m, f2, budgets(m)[2])
        st, sol = sat_completion(m, f2, require=("B0", "B1"), time_limit=300.0)
        print(f"  word runs {runs_of(w)}: {st}")
        if sol:
            A0, A1 = sol
            ts = budgets(m)
            ok = (is_single(m, A0, ts[0]) and is_single(m, A1, ts[1]))
            print(f"    verified: {ok}; windings A0={windings(m, A0)} "
                  f"A1={windings(m, A1)}; |I0|,|I1|="
                  f"{sum(1 for p in A0 if A0[p]==0)},"
                  f"{sum(1 for p in A1 if A1[p]==0)}; "
                  f"loops={len(field_loops(m, A0))},{len(field_loops(m, A1))}")
            full = {p: [A0[p], A1[p], f2.get(p, 0)]
                    for p in itertools.product(range(m), repeat=2)}
            json.dump({str(p): v for p, v in full.items()},
                      open(f"{SCR}/word_completion_m6_{'-'.join(map(str,runs_of(w)))}.json", "w"))


def w3_ground_truth_A2():
    print("W3: structure of ground-truth A_2 gadgets under the criterion")
    for m in (6, 8):
        A = load_surgery(m)
        f2 = A[2]
        t2 = budgets(m)[2]
        supp = {p for p in f2 if f2[p] != 0}
        loops = field_loops(m, f2)
        lab, o, ncos = coset_label(m, t2)
        mult = Counter(Counter(lab[p] for p in supp).values())
        cov, rc = criterion(m, f2, t2)
        h, v = straight_sets(m, f2)
        print(f"  m={m}: |supp|={len(supp)} winding={windings(m, f2)} "
              f"loops={len(loops)} coset multiplicity profile={dict(mult)} "
              f"rcycles={rc} straight pts: h={len(h)} v={len(v)}")
        # word of the loop
        loop = loops[0]
        word = tuple(f2[p] for p in loop)
        print(f"    loop word runs: {runs_of(word)}")


def w4_m10_search(seconds=1200):
    print("W4: (1,2)-winding 3m-word gadgets at m=10: find B_2-single ones,")
    print("    then try SAT completion (the step where helix12 dies).")
    m = 10
    t2 = budgets(m)[2]
    rng = random.Random(42)
    found = []
    tried = 0
    while len(found) < 30 and tried < 20000:
        tried += 1
        word = [1] * m + [2] * (2 * m)
        rng.shuffle(word)
        f = word_loop(m, word)
        if f is None:
            continue
        if is_single(m, f, t2):
            found.append(f)
    print(f"  tried {tried} random (1,2)-words: {len(found)} give B_2 single")
    random.Random(1).shuffle(found)
    for i, f2 in enumerate(found[:6]):
        st, sol = sat_completion(m, f2, require=("B0", "B1"),
                                 time_limit=float(seconds) / 6)
        loops = field_loops(m, f2)
        word = tuple(f2[p] for p in loops[0])
        print(f"  gadget {i} (runs {runs_of(word)}): {st}")
        if sol:
            A0, A1 = sol
            ts = budgets(m)
            ok = (is_single(m, A0, ts[0]) and is_single(m, A1, ts[1]))
            print(f"    verified: {ok}; windings A0={windings(m, A0)} "
                  f"A1={windings(m, A1)}")
            full = {p: [A0[p], A1[p], f2.get(p, 0)]
                    for p in itertools.product(range(m), repeat=2)}
            json.dump({str(p): v for p, v in full.items()},
                      open(f"{SCR}/word12_completion_m10_{i}.json", "w"))
            break


if __name__ == "__main__":
    which = sys.argv[1:] or ["1", "2", "3"]
    if "1" in which: w1_word_landscape()
    if "2" in which: w2_complete_m6_words()
    if "3" in which: w3_ground_truth_A2()
    if "4" in which: w4_m10_search()
    print("DONE")
