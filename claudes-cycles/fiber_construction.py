#!/usr/bin/env python3
"""Parametrized fiber construction for Hamilton decompositions of D_3(m).

Architecture: slice (Z_m)^3 by s = (i+j+k) mod m into fibers isomorphic to
Z_m^2 (coordinates (i,j); k = s-i-j).  Every arc maps fiber s to fiber s+1:
  bump k : (i,j) -> (i,j)      (idle)
  bump i : (i,j) -> (i+1,j)
  bump j : (i,j) -> (i,j+1)

Per fiber s we choose:
  - idler[s] in {0,1,2}: the cycle that bumps k everywhere on this fiber
  - kind[s] in {'U','S'}:
      'U' (uniform): the two movers translate; orient[s] decides which mover
          bumps i (the other bumps j).
      'S' (serpentine): movers use the anti-diagonal pair with offset c[s]:
          H_c: bump j iff i+j == c (mod m), else bump i
          C_c: bump i iff i+j == c (mod m), else bump j
          orient[s] decides which mover takes H_c (the other takes C_c).

Both H_c and C_c are single m^2-cycles on Z_m^2 for every m >= 2, and they
are pointwise complementary, so all local (arc-partition) constraints hold by
construction.  The only thing to check is that each cycle's first-return map
is a single m^2-cycle -- equivalently that the assembled cycles are
Hamiltonian, which we verify with the independent checker.
"""
import itertools
import json
import sys

from torus_decomp import check


def build(m, idler, kind, orient, offset):
    """Build perm[v] = (dir of cycle 0, dir of cycle 1, dir of cycle 2).
    idler, kind, orient, offset: lists of length m indexed by fiber s."""
    perm = {}
    for i, j, k in itertools.product(range(m), repeat=3):
        s = (i + j + k) % m
        movers = [c for c in range(3) if c != idler[s]]
        # orient flips which mover is "first"
        if orient[s]:
            movers = movers[::-1]
        p = [None, None, None]
        p[idler[s]] = 2  # bump k
        if kind[s] == 'U':
            p[movers[0]] = 0  # bump i
            p[movers[1]] = 1  # bump j
        else:  # serpentine pair with offset c
            on_diag = (i + j) % m == offset[s]
            # H: bump j on diagonal else bump i ; C: complement
            p[movers[0]] = 1 if on_diag else 0
            p[movers[1]] = 0 if on_diag else 1
        perm[(i, j, k)] = tuple(p)
    return perm


def try_params(m, idler, kind, orient, offset):
    perm = build(m, idler, kind, orient, offset)
    ok, msg = check(3, m, perm)
    return ok, msg, perm


def scan(m, n_special=3, verbose=False):
    """Scan a reduced parameter space:
    - special fibers at s = 0..n_special-1, generic uniform elsewhere
    - idler at special fiber t is cycle t (mod 3)
    - generic fibers: idler pattern parameter: 'const r' or 's mod 3'
    - offsets in Z_m at special fibers, orientations everywhere reduced:
      orientation constant o_g on generic fibers, free on special fibers.
    Yields working parameter sets."""
    hits = []
    generic = list(range(n_special, m))
    for gen_idler_mode in range(4):  # 0,1,2 = const; 3 = s mod 3
        for o_g in (0, 1):
            for sp_orients in itertools.product((0, 1), repeat=n_special):
                for offs in itertools.product(range(m), repeat=n_special):
                    idler = [0] * m
                    kind = ['U'] * m
                    orient = [0] * m
                    offset = [0] * m
                    for t in range(n_special):
                        idler[t] = t % 3
                        kind[t] = 'S'
                        orient[t] = sp_orients[t]
                        offset[t] = offs[t]
                    for s in generic:
                        idler[s] = (s % 3) if gen_idler_mode == 3 else gen_idler_mode
                        orient[s] = o_g
                    ok, msg, _ = try_params(m, idler, kind, orient, offset)
                    if ok:
                        hit = dict(m=m, gen_idler_mode=gen_idler_mode, o_g=o_g,
                                   sp_orients=sp_orients, offs=offs)
                        hits.append(hit)
                        if verbose:
                            print(f"  HIT {hit}", flush=True)
    return hits


if __name__ == "__main__":
    ms = [int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else "4,6").split(",")]
    all_hits = {}
    for m in ms:
        hits = scan(m)
        all_hits[m] = hits
        print(f"m={m}: {len(hits)} working parameter sets", flush=True)
        for h in hits[:10]:
            print("   ", h, flush=True)
    # look for parameter families working across all m scanned
    if len(ms) > 1 and all(all_hits[m] for m in ms):
        def sig(h):
            return (h['gen_idler_mode'], h['o_g'], h['sp_orients'], h['offs'])
        common = set(sig(h) for h in all_hits[ms[0]])
        for m in ms[1:]:
            common &= set(sig(h) for h in all_hits[m])
        print(f"parameter sets common to all m in {ms}: {sorted(common)[:20]}",
              flush=True)
