#!/usr/bin/env python3
"""Induction in m: hunt for a local word-extension rule W(m) -> W(m+2)
preserving B_2-single (and completability of cycles 0,1).

I1: exhaustive (1,2)-word landscape at m=6 (and m=8): all C(3m, m)
    letter placements; classify simple / B_2-single / coset profile;
    SAT-test completability of every B_2-single rotation class at m=6.
I2: insertion scan: from each completable m=6 word, insert two copies of the
    slope period P_1 = [e0, e1, e1] (all position pairs, plus arbitrary
    6-letter blocks as fallback) -> candidate m=8 words; keep B_2-singles;
    SAT-test a sample; record which insertions preserve completability.
I3: iterate the surviving rule(s) m=8 -> 10 -> 12 -> 14, tracking
    B_2-singleness (cheap) and completability (SAT where affordable).
I4: return-map structure diff for rule-related pairs.
"""
import itertools, json, random, sys
from collections import Counter
from criterion import (SCR, MOVES, budgets, is_single, coset_label, criterion,
                       field_loops, windings, word_loop, sat_completion,
                       runs_of)

P1 = (1, 2, 2)


def canon(word):
    return min(tuple(word[i:] + word[:i]) for i in range(len(word)))


def all_words(m):
    """All (1,2)-winding words up to rotation that walk to simple loops."""
    n = 3 * m
    seen = {}
    for pos in itertools.combinations(range(n), m):
        w = [2] * n
        for i in pos:
            w[i] = 1
        c = canon(w)
        if c in seen:
            continue
        f = word_loop(m, list(c))
        seen[c] = f
    return {c: f for c, f in seen.items() if f is not None}


def classify(m, words):
    t2 = budgets(m)[2]
    lab, _, ncos = coset_label(m, t2)
    out = {}
    for c, f in words.items():
        single = is_single(m, f, t2)
        prof = Counter(Counter(lab[p] for p in f).values())
        out[c] = (single, dict(prof))
    return out


def i1_m6(tl=90.0):
    m = 6
    words = all_words(m)
    cls = classify(m, words)
    singles = [c for c, (s, _) in cls.items() if s]
    balanced = [c for c in singles if cls[c][1] == {1: m, 2: m}]
    print(f"I1 m=6: {len(words)} simple rotation classes, "
          f"{len(singles)} B_2-single, {len(balanced)} with profile "
          f"{{1:{m}, 2:{m}}}")
    profs = Counter(tuple(sorted(cls[c][1].items())) for c in singles)
    print(f"  profiles among singles: {dict(profs)}")
    comp = []
    for i, c in enumerate(singles):
        st, sol = sat_completion(m, words[c], require=("B0", "B1"),
                                 time_limit=tl)
        if sol:
            comp.append(c)
        print(f"  [{i+1}/{len(singles)}] {st:10s} profile={cls[c][1]} "
              f"runs={runs_of(c)}", flush=True)
    print(f"I1 m=6: completable {len(comp)} / {len(singles)}; "
          f"of which balanced-profile: "
          f"{sum(1 for c in comp if cls[c][1] == {1: m, 2: m})}")
    json.dump([list(c) for c in comp], open(f"{SCR}/m6_completable_words.json", "w"))
    return comp


def insertions_two_periods(word):
    """All distinct words obtained by inserting P1 at two positions."""
    n = len(word)
    outs = set()
    for p in range(n + 1):
        w1 = list(word[:p]) + list(P1) + list(word[p:])
        for q in range(len(w1) + 1):
            w2 = w1[:q] + list(P1) + w1[q:]
            outs.add(tuple(w2))
    return outs


def i2_insertion_scan(comp6, sat_budget=25, tl=150.0):
    m2 = 8
    t2 = budgets(m2)[2]
    lab, _, _ = coset_label(m2, t2)
    print("I2: two-period insertions m=6 -> m=8")
    results = []  # (parent, child) completable pairs
    all_children = {}
    for c in comp6:
        singles = set()
        for w in insertions_two_periods(c):
            cw = canon(list(w))
            if cw in all_children:
                continue
            f = word_loop(m2, list(cw))
            all_children[cw] = None
            if f is not None and is_single(m2, f, t2):
                singles.add(cw)
                all_children[cw] = f
        print(f"  parent runs={runs_of(c)}: {len(singles)} single children")
        results.append((c, singles))
    # SAT a sample of children (spread across parents)
    tested = comp_pairs = 0
    comp_children = []
    for c, singles in results:
        for cw in sorted(singles)[:max(1, sat_budget // max(1, len(results)))]:
            st, sol = sat_completion(m2, all_children[cw],
                                     require=("B0", "B1"), time_limit=tl)
            tested += 1
            if sol:
                comp_pairs += 1
                comp_children.append((list(c), list(cw)))
            print(f"    child of {runs_of(c)}: {st} runs={runs_of(cw)}",
                  flush=True)
    print(f"I2: {comp_pairs}/{tested} sampled children completable")
    json.dump(comp_children, open(f"{SCR}/insertion_pairs_6_8.json", "w"))
    return comp_children


def i3_chain(seed_words, ms=(10, 12, 14), sat_ms=(10, 12), tls=None,
             keep=4):
    """Iterate two-period insertion upward from verified m=8 words."""
    tls = tls or {10: 400.0, 12: 1200.0, 14: 3600.0}
    frontier = [tuple(w) for w in seed_words]
    print(f"I3: chain from {len(frontier)} m=8 words")
    for m in ms:
        t2 = budgets(m)[2]
        nxt = []
        seen = set()
        nsing = 0
        for w in frontier:
            for w2 in insertions_two_periods(w):
                cw = canon(list(w2))
                if cw in seen:
                    continue
                seen.add(cw)
                f = word_loop(m, list(cw))
                if f is not None and is_single(m, f, t2):
                    nsing += 1
                    nxt.append((cw, f))
        print(f"  m={m}: {nsing} B_2-single children from "
              f"{len(seen)} candidates", flush=True)
        if not nxt:
            print(f"  CHAIN BREAKS at m={m}: no single children")
            return
        surv = []
        if m in sat_ms:
            for cw, f in nxt[:10]:
                st, sol = sat_completion(m, f, require=("B0", "B1"),
                                         time_limit=tls[m])
                print(f"    SAT m={m}: {st} runs={runs_of(cw)}", flush=True)
                if sol:
                    A0, A1 = sol
                    ts = budgets(m)
                    assert is_single(m, A0, ts[0]) and is_single(m, A1, ts[1])
                    json.dump({str(p): [A0[p], A1[p], f.get(p, 0)]
                               for p in itertools.product(range(m), repeat=2)},
                              open(f"{SCR}/chain_completion_m{m}.json", "w"))
                    surv.append(cw)
                    if len(surv) >= keep:
                        break
            frontier = surv if surv else [cw for cw, _ in nxt[:keep]]
            print(f"  m={m}: completable among tested: {len(surv)}")
        else:
            frontier = [cw for cw, _ in nxt[:keep]]


def i4_return_map_diff(w_small, m_small, w_big, m_big):
    print("I4: return-map structure of rule-related pair")
    for w, m in ((w_small, m_small), (w_big, m_big)):
        f = word_loop(m, list(w))
        t2 = budgets(m)[2]
        lab, _, _ = coset_label(m, t2)
        cov, rc = criterion(m, f, t2)
        # R-cycle as the cyclic sequence of coset multiplicities visited
        from criterion import apply_B
        S = set(f)
        mult = Counter(lab[p] for p in f)
        p = next(iter(f))
        seq = []
        for _ in range(len(f)):
            seq.append(mult[lab[p]])
            q = apply_B(m, f, t2, p)
            k = 0
            while q not in S:
                q = ((q[0] + t2[0]) % m, (q[1] + t2[1]) % m)
                k += 1
            p = q
        print(f"  m={m}: rcycles={rc} multiplicity itinerary "
              f"(len {len(seq)}): {''.join(map(str, seq))}")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "I1"
    if which == "I1":
        i1_m6()
    elif which == "I2":
        comp6 = [tuple(w) for w in json.load(open(f"{SCR}/m6_completable_words.json"))]
        i2_insertion_scan(comp6)
    elif which == "I3":
        pairs = json.load(open(f"{SCR}/insertion_pairs_6_8.json"))
        seeds = [w8 for _, w8 in pairs]
        i3_chain(seeds)
    elif which == "I4":
        pairs = json.load(open(f"{SCR}/insertion_pairs_6_8.json"))
        w6, w8 = pairs[0]
        i4_return_map_diff(w6, 6, w8, 8)
    print("DONE")
