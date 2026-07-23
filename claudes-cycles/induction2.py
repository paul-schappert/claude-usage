#!/usr/bin/env python3
"""Induction phase 2: k=2 chain, k-jump rules, window-edge confirmation."""
import itertools, json, sys
from collections import Counter
from criterion import (SCR, budgets, is_single, coset_label, field_loops,
                       word_loop, sat_completion, runs_of, windings)
from induction import canon, insertions_two_periods

P2 = (1, 1, 2, 2, 2)


def gadget_word(fn):
    d = json.load(open(f"{SCR}/{fn}"))
    tab = {tuple(map(int, k.strip('()').split(','))): v for k, v in d.items()}
    m = max(p[0] for p in tab) + 1
    f = {p: tab[p][2] for p in tab if tab[p][2] != 0}
    loops = field_loops(m, f)
    assert len(loops) == 1
    return m, [f[p] for p in loops[0]]


def insertions_two_P2(word):
    n = len(word)
    outs = set()
    for p in range(n + 1):
        w1 = list(word[:p]) + list(P2) + list(word[p:])
        for q in range(len(w1) + 1):
            outs.add(tuple(w1[:q] + list(P2) + w1[q:]))
    return outs


def k2_chain(tl=5400.0, nsat=3):
    m0, w = gadget_word("wlaw_completion_m12_k2.json")
    assert m0 == 12 and w.count(1) == 24 and w.count(2) == 36
    m = 14
    t2 = budgets(m)[2]
    singles = []
    seen = set()
    for w2 in insertions_two_P2(w):
        c = canon(list(w2))
        if c in seen:
            continue
        seen.add(c)
        f = word_loop(m, list(c))
        if f is not None and is_single(m, f, t2):
            singles.append((c, f))
    print(f"k2 chain 12->14: {len(singles)} single children "
          f"from {len(seen)} candidates", flush=True)
    for c, f in singles[:nsat]:
        st, sol = sat_completion(m, f, require=("B0", "B1"), time_limit=tl)
        print(f"  SAT m=14 k=2: {st} runs={runs_of(c)}", flush=True)
        if sol:
            A0, A1 = sol
            ts = budgets(m)
            assert is_single(m, A0, ts[0]) and is_single(m, A1, ts[1])
            json.dump({str(p): [A0[p], A1[p], f.get(p, 0)]
                       for p in itertools.product(range(m), repeat=2)},
                      open(f"{SCR}/chain_completion_m14_k2.json", "w"))
            break


def jump_rules(tl=1800.0):
    """Deterministic k-jumps on completable (1,2)-words at m=8,10:
    J1: after each e0 insert (e1, e0)  -> winding (2,3)
    J2: after each e0 insert (e0, e1)  -> winding (2,3)
    J3: before each e0 insert (e1, e0) -> winding (2,3)
    J4: replace each period-aligned...: after each e1-run insert (e0, e1)?
        (adds one e0+e1 per e1-run; only winding-correct if #e1-runs = m --
        skipped unless run count matches)
    """
    def J1(w):
        out = []
        for x in w:
            out.append(x)
            if x == 1:
                out += [2, 1]
        return out

    def J2(w):
        out = []
        for x in w:
            out.append(x)
            if x == 1:
                out += [1, 2]
        return out

    def J3(w):
        out = []
        for x in w:
            if x == 1:
                out += [2, 1]
            out.append(x)
        return out

    sources = []
    for fn in ("wlaw_completion_m8_k1.json", "wlaw_completion_m10_k1.json",
               "chain_completion_m10.json"):
        try:
            sources.append((fn,) + gadget_word(fn))
        except FileNotFoundError:
            pass
    m6 = json.load(open(f"{SCR}/m6_completable_words.json"))
    for i, w in enumerate(m6):
        sources.append((f"m6_completable[{i}]", 6, w))
    for name, m, w in sources:
        t2 = budgets(m)[2]
        for rname, rule in (("J1", J1), ("J2", J2), ("J3", J3)):
            w2 = rule(list(w))
            assert w2.count(1) == 2 * m and w2.count(2) == 3 * m
            f = word_loop(m, w2)
            ok = f is not None and is_single(m, f, t2)
            tag = "SINGLE" if ok else ("notloop" if f is None else "split")
            line = f"  {name} m={m} {rname}: {tag}"
            if ok:
                st, sol = sat_completion(m, f, require=("B0", "B1"),
                                         time_limit=tl)
                line += f"  SAT: {st}"
                if sol:
                    A0, A1 = sol
                    ts = budgets(m)
                    assert is_single(m, A0, ts[0]) and is_single(m, A1, ts[1])
                    json.dump({str(p): [A0[p], A1[p], f.get(p, 0)]
                               for p in itertools.product(range(m), repeat=2)},
                              open(f"{SCR}/jump_completion_{rname}_m{m}.json",
                                   "w"))
            print(line, flush=True)


def m14_k1_edge(tl=3600.0, n=2):
    """SAT the m=14 k=1 chain singles (expected INFEASIBLE: ridge law)."""
    # regenerate the m=14 singles from the m=12 frontier as in I3
    from induction import insertions_two_periods as ins
    pairs = json.load(open(f"{SCR}/insertion_pairs_6_8.json"))
    frontier = [tuple(w8) for _, w8 in pairs]
    for m in (10, 12):
        t2 = budgets(m)[2]
        nxt, seen = [], set()
        for w in frontier:
            for w2 in ins(w):
                c = canon(list(w2))
                if c in seen:
                    continue
                seen.add(c)
                f = word_loop(m, list(c))
                if f is not None and is_single(m, f, t2):
                    nxt.append(c)
        frontier = nxt[:4]
    m = 14
    t2 = budgets(m)[2]
    singles, seen = [], set()
    for w in frontier:
        for w2 in ins(w):
            c = canon(list(w2))
            if c in seen:
                continue
            seen.add(c)
            f = word_loop(m, list(c))
            if f is not None and is_single(m, f, t2):
                singles.append((c, f))
    print(f"m=14 k=1: {len(singles)} chain singles", flush=True)
    for c, f in singles[:n]:
        st, _ = sat_completion(m, f, require=("B0", "B1"), time_limit=tl)
        print(f"  SAT m=14 k=1: {st} runs={runs_of(c)}", flush=True)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "jump"
    if which == "jump":
        jump_rules()
    elif which == "k2":
        k2_chain()
    elif which == "edge":
        m14_k1_edge()
    print("DONE")
