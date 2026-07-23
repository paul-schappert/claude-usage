#!/usr/bin/env python3
"""Narrow-tree completability census under the REALIZABLE budget family
F: t_0 = (1,-6), t_1 = (-4,1), t_2 = (2,4)
   (lifts a = (1, m-4, 2), b = (m-6, 1, 4), schedulable for even m >= 8).

For each level, censuses every branch word (dedup by canon); whenever a
level has a completable word, saves one completion, ASSEMBLES the full
D_3(m) decomposition through the fiber schedule and verifies it with the
independent 3D checker.

Run: python3 narrow_censusF.py m1 m2 ...
"""
import itertools, json, sys, time
SCR = "/tmp/claude-0/-home-user-claude-usage/e5933da4-9bfd-5e34-89c1-d01da7b77644/scratchpad/claudes-cycles"
sys.path.insert(0, SCR)
from insertion_lemma import narrow_data, child
from criterion import word_loop, is_single
from induction import canon
from dense_template2 import census2
from narrow_census import seeds_m6
from assembler import assemble
from torus_decomp import check


def famF(m):
    a = [1, m - 4, 2]
    b = [m - 6, 1, 4]
    ts = [(a[c] % m, b[c] % m) for c in range(3)]
    return ts, a, b


def tree_level(m):
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


def full_check_and_assemble(m, W, b, A0, A1, ts, a, bb, tag):
    """Independent verification of the reduced triple + 3D assembly."""
    A2 = {p: W.get(p, 0) for p in itertools.product(range(m), repeat=2)}
    for p in itertools.product(range(m), repeat=2):
        assert sorted((A0[p], A1[p], A2[p])) == [0, 1, 2]
    from criterion import field_loops
    for c, f in enumerate((A0, A1, A2)):
        assert field_loops(m, f) is not None
        assert is_single(m, f, ts[c])
    perm = assemble(m, a, bb, [A0, A1, A2])
    assert perm is not None
    ok, msg = check(3, m, perm)
    assert ok, (m, msg)
    json.dump({str(p): [A0[p], A1[p], A2[p]]
               for p in itertools.product(range(m), repeat=2)},
              open(f"{SCR}/famF_completion_m{m}.json", "w"))
    json.dump({str(v): list(perm[v]) for v in perm},
              open(f"{SCR}/famF_decomp3d_m{m}.json", "w"))
    print(f"   {tag}: D_3({m}) DECOMPOSITION ASSEMBLED + 3D-VERIFIED "
          f"(saved famF_decomp3d_m{m}.json)", flush=True)


def run_level(m, fout, time_cap=3600.0):
    ts, a, bb = famF(m)
    level = tree_level(m)
    cache = {}
    ncomp = 0
    got3d = False
    t0 = time.time()
    for si, br, w in level:
        c = canon(list(w))
        t1 = time.time()
        if c in cache:
            res, cached = cache[c], True
        else:
            f = word_loop(m, list(c))
            assert f is not None and is_single(m, f, ts[2])
            want = 1 if not got3d else 0
            nc, nb0, nboth, exh, sols = census2(m, f, ts, time_cap=time_cap,
                                                want_sols=want)
            assert exh, (m, si, br, "not exhausted")
            res, cached = (nc, nb0, nboth), False
            cache[c] = res
            if nboth > 0 and not got3d and sols:
                bsol, A0, A1 = sols[0]
                full_check_and_assemble(m, f, bsol, A0, A1, ts, a, bb,
                                        f"seed {si} branch {br}")
                got3d = True
        nc, nb0, nboth = res
        if nboth > 0:
            ncomp += 1
        fout.write(json.dumps(dict(m=m, seed=si, branch=br,
            canon="".join(map(str, c)), closure=nc, b0single=nb0,
            completions=nboth, cached=cached,
            time=round(time.time() - t1, 2))) + "\n")
        fout.flush()
    print(f"level m={m}: {len(level)} branch-words, {ncomp} completable "
          f"[famF] {time.time()-t0:.1f}s", flush=True)
    return ncomp


if __name__ == "__main__":
    ms = [int(x) for x in sys.argv[1:]] or [8, 10, 12, 14, 16, 18, 20]
    fout = open(f"{SCR}/narrow_censusF.jsonl", "a")
    for m in ms:
        run_level(m, fout)
    fout.close()
    print("DONE")
