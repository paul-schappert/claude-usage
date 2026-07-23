#!/usr/bin/env python3
"""Greedy existence driver under family F: at each level, census narrow-tree
words (shuffled, dedup) until one completes; assemble + 3D-verify; stop."""
import itertools, json, random, sys, time
SCR = "/tmp/claude-0/-home-user-claude-usage/e5933da4-9bfd-5e34-89c1-d01da7b77644/scratchpad/claudes-cycles"
sys.path.insert(0, SCR)
from criterion import word_loop, is_single
from induction import canon
from dense_template2 import census2
from narrow_censusF import famF, tree_level, full_check_and_assemble


def run(ms):
    for m in ms:
        ts, a, bb = famF(m)
        level = tree_level(m)
        rng = random.Random(m)
        rng.shuffle(level)
        seen = set()
        t0 = time.time()
        tried = 0
        done = False
        for si, br, w in level:
            c = canon(list(w))
            if c in seen:
                continue
            seen.add(c)
            f = word_loop(m, list(c))
            assert f is not None and is_single(m, f, ts[2])
            nc, nb0, nboth, exh, sols = census2(m, f, ts, time_cap=7200.0,
                                                want_sols=1)
            assert exh, (m, si, br)
            tried += 1
            if nboth > 0:
                bsol, A0, A1 = sols[0]
                full_check_and_assemble(m, f, bsol, A0, A1, ts, a, bb,
                                        f"seed {si} branch {br}")
                print(f"m={m}: found after {tried} words "
                      f"[{time.time()-t0:.1f}s]", flush=True)
                done = True
                break
        if not done:
            print(f"m={m}: NO completable word found in the whole level "
                  f"({tried} canon words) [{time.time()-t0:.1f}s]", flush=True)


if __name__ == "__main__":
    run([int(x) for x in sys.argv[1:]] or [26, 28, 30, 32])
