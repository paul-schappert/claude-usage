#!/usr/bin/env python3
"""Phase 6: the insertion lemma (obligation 1 of induction3.md section 5).

Pure-word machinery for balanced (1,2)-gadgets:
  * integer label walk (eps_i, z_i), z_i = 3 a_i - i (step +2 on e0, -1 on e1)
  * chord diagram + interlacement matrix + GF(2) determinant (Cohn-Lempel)
  * EXACT child-label formula under double-period insertion (Prop 1 of
    insertion_lemma.md), machine-verified against direct recomputation
  * exploration of good pairs (p,q) across the m=6 landscape + chain words.

Experiments (run: python3 insertion_lemma.py E1 E2 E3 ...):
  E1  cross-check word-level Cohn-Lempel vs direct orbit count (m=6 all
      balanced words + random words m=8,10)
  E2  verify the child-label formula on random (word, p, q) triples
  E3  full (p,q) landscape for all 77 m=6 singles: counts, parity, widths
  E4  structure of good pairs (z_p, z_q, eps) relative to walk max
  E5  same for k=1 chain words at m=8..14
"""
import itertools, json, sys
from collections import Counter

SCR = "/tmp/claude-0/-home-user-claude-usage/e5933da4-9bfd-5e34-89c1-d01da7b77644/scratchpad/claudes-cycles"
P1 = (1, 2, 2)


# ---------- pure word machinery ----------

def walk(word):
    """Integer label walk: list of (eps_i, z_i) for i = 0..L-1, plus closing
    check data. z_i = 3 a_i - i; eps_i = a_i mod 2."""
    a = 0
    out = []
    for i, w in enumerate(word):
        out.append((a & 1, 3 * a - i))
        if w == 1:
            a += 1
    return out


def points(word, m):
    a = 0
    pts = []
    for i, w in enumerate(word):
        pts.append((a % m, (i - a) % m))
        if w == 1:
            a += 1
    return pts


def is_simple(word, m):
    pts = points(word, m)
    return len(set(pts)) == len(pts)


def labels(word, m):
    return [(e, z % m) for e, z in walk(word)]


def diagram(word, m):
    """(balanced, chords) - chords as position pairs (i<j) of doubleton
    labels; balanced iff every label mult <= 2 and all 2m labels hit."""
    lab = labels(word, m)
    by = {}
    for i, l in enumerate(lab):
        by.setdefault(l, []).append(i)
    if len(by) != 2 * m or any(len(v) > 2 for v in by.values()):
        return False, None
    chords = sorted(tuple(v) for v in by.values() if len(v) == 2)
    return True, chords


def gf2_det(chords):
    """1 iff interlacement matrix nonsingular over GF(2)."""
    n = len(chords)
    rows = []
    for (a, b) in chords:
        r = 0
        for j, (x, y) in enumerate(chords):
            if (a, b) != (x, y) and ((a < x < b) != (a < y < b)):
                r |= 1 << j
        rows.append(r)
    rank = 0
    for col in range(n):
        piv = next((i for i in range(rank, n) if rows[i] >> col & 1), None)
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for i in range(n):
            if i != rank and rows[i] >> col & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return 1 if rank == n else 0


def word_status(word, m):
    """(simple, balanced, det) with det None unless simple & balanced."""
    if not is_simple(word, m):
        return False, False, None
    bal, chords = diagram(word, m)
    if not bal:
        return True, False, None
    return True, True, gf2_det(chords)


def child(word, p, q):
    """Insert P1 before position p and before position q (p <= q <= L),
    i.e. word[:p] + P1 + word[p:q] + P1 + word[q:]."""
    w = list(word)
    return tuple(w[:p] + list(P1) + w[p:q] + list(P1) + w[q:])


def child_labels_formula(word, m, p, q):
    """EXACT child labels via Proposition 1: parent eps flipped on [p,q),
    z unchanged, six new points; z reduced mod m+2."""
    W = walk(word)
    m2 = m + 2
    out = []
    ep, zp = W[p] if p < len(W) else (len([w for w in word if w == 1]) & 1, 0)
    # careful: p may equal L (append at end); handle via closing label (0,0)
    def lab_at(i):
        if i < len(W):
            return W[i]
        return (0, 0)  # closing label: a_L = m even, z_L = 0
    ep, zp = lab_at(p)
    eq, zq = lab_at(q)
    for i in range(0, p):
        e, z = W[i]
        out.append((e, z % m2))
    out += [(ep, zp % m2), (ep ^ 1, (zp + 2) % m2), (ep ^ 1, (zp + 1) % m2)]
    for i in range(p, q):
        e, z = W[i]
        out.append((e ^ 1, z % m2))
    out += [(eq ^ 1, zq % m2), (eq, (zq + 2) % m2), (eq, (zq + 1) % m2)]
    for i in range(q, len(W)):
        e, z = W[i]
        out.append((e, z % m2))
    return out


# ---------- experiments ----------

def load_m6_singles():
    from criterion import budgets, word_loop, is_single
    from induction import all_words, classify
    words = all_words(6)
    cls = classify(6, words)
    return [c for c, (s, _) in cls.items() if s]


def e1_crosscheck():
    print("E1: word-level Cohn-Lempel vs direct orbit count")
    from criterion import budgets, word_loop, is_single
    import random
    m = 6
    t2 = budgets(m)[2]
    from induction import all_words, classify
    words = all_words(m)
    n = agree = 0
    for c, f in words.items():
        s, b, d = word_status(list(c), m)
        assert s  # all_words returns simple loops only
        direct = is_single(m, f, t2)
        pred = (b and d == 1)
        assert pred == direct, (c, b, d, direct)
        n += 1
    print(f"  m=6: {n} simple words, prediction (balanced & det=1) == "
          f"B_2-single: EXACT")
    for m in (8, 10):
        t2 = budgets(m)[2]
        rng = random.Random(99 + m)
        cnt = 0
        for _ in range(20000):
            w = [1] * m + [2] * (2 * m)
            rng.shuffle(w)
            f = word_loop(m, w)
            if f is None:
                continue
            s, b, d = word_status(w, m)
            direct = is_single(m, f, t2)
            if b:
                assert (d == 1) == direct, (w, d, direct)
                cnt += 1
            else:
                # unbalanced: C-L n/a; only sanity: balancedness itself
                pass
            if cnt >= 300:
                break
        print(f"  m={m}: {cnt} random balanced words agree (det=1 <=> single)")


def e2_formula():
    print("E2: child-label formula vs direct recomputation")
    import random
    rng = random.Random(7)
    tested = 0
    for m in (6, 8, 10):
        for _ in range(400):
            w = [1] * m + [2] * (2 * m)
            rng.shuffle(w)
            L = len(w)
            p = rng.randint(0, L)
            q = rng.randint(p, L)
            ch = child(w, p, q)
            direct = labels(ch, m + 2)
            form = child_labels_formula(w, m, p, q)
            assert direct == form, (m, w, p, q)
            tested += 1
    print(f"  formula exact on {tested} random (word, p, q) triples")


def zwidth(word):
    zs = [z for _, z in walk(word)]
    return max(zs) - min(zs), min(zs), max(zs)


def e3_landscape():
    print("E3: full (p,q) landscape, all 77 m=6 B_2-single words")
    singles = load_m6_singles()
    comp = {tuple(w) for w in json.load(open(f"{SCR}/m6_completable_words.json"))}
    m = 6
    L = 3 * m
    stats = []
    for c in singles:
        w = list(c)
        wd, zmin, zmax = zwidth(w)
        ngood = nsb = nsimple = 0
        good_pairs = []
        for p in range(L + 1):
            for q in range(p, L + 1):
                ch = child(w, p, q)
                s, b, d = word_status(ch, m + 2)
                if s:
                    nsimple += 1
                if s and b:
                    nsb += 1
                    if d == 1:
                        ngood += 1
                        good_pairs.append((p, q))
        stats.append((c, wd, nsimple, nsb, ngood, good_pairs))
    nzero = sum(1 for st in stats if st[4] == 0)
    print(f"  words with ZERO good pairs: {nzero}/77")
    wds = Counter(st[1] for st in stats)
    print(f"  z-widths: {dict(wds)}")
    par_sb = Counter(st[3] % 2 for st in stats)
    par_g = Counter(st[4] % 2 for st in stats)
    print(f"  parity of #(simple&balanced): {dict(par_sb)}; "
          f"parity of #good: {dict(par_g)}")
    for c, wd, ns, nsb, ng, gp in stats:
        tag = "COMP" if c in comp else "    "
        print(f"  {tag} {''.join(map(str,c))} width={wd} simple={ns} "
              f"bal={nsb} good={ng}")
    json.dump([[list(c), wd, ns, nsb, ng, gp]
               for c, wd, ns, nsb, ng, gp in stats],
              open(f"{SCR}/insertion_landscape_m6.json", "w"))
    return stats


def e4_structure(stats=None):
    print("E4: structure of good pairs (z_p, z_q, eps_p, eps_q) vs walk max")
    if stats is None:
        stats = [(tuple(c), wd, ns, nsb, ng, [tuple(g) for g in gp])
                 for c, wd, ns, nsb, ng, gp in
                 json.load(open(f"{SCR}/insertion_landscape_m6.json"))]
    pat = Counter()
    for c, wd, ns, nsb, ng, gp in stats:
        W = walk(list(c))
        L = len(c)
        lab_at = lambda i: W[i] if i < L else (0, 0)
        zmax = max(z for _, z in W)
        zmin = min(z for _, z in W)
        for (p, q) in gp:
            (ep, zp), (eq, zq) = lab_at(p), lab_at(q)
            pat[(zp - zmax, zq - zmax, ep ^ eq)] += 1
    for k, v in sorted(pat.items(), key=lambda kv: -kv[1]):
        print(f"  (zp-zmax, zq-zmax, eps_xor) = {k}: {v}")


def chain_words_k1():
    """k=1 chain gadget words at m=8..14 (from saved artifacts)."""
    from criterion import field_loops, budgets, word_loop, is_single
    out = []
    pairs = json.load(open(f"{SCR}/insertion_pairs_6_8.json"))
    for _, w8 in pairs[:3]:
        out.append((8, tuple(w8)))
    for fn, m in (("chain_completion_m10.json", 10),
                  ("chain_completion_m12_k1.json", 12)):
        d = json.load(open(f"{SCR}/{fn}"))
        tab = {tuple(map(int, k.strip('()').split(','))): v
               for k, v in d.items()}
        f = {p: tab[p][2] for p in tab if tab[p][2] != 0}
        loops = field_loops(m, f)
        assert len(loops) == 1
        loop = loops[0]
        word = tuple(f[p] for p in loop)
        out.append((m, word))
    return out


def e5_chain():
    print("E5: (p,q) landscape for k=1 chain words m=8..12")
    for m, w in chain_words_k1():
        s, b, d = word_status(list(w), m)
        L = len(w)
        wd, zmin, zmax = zwidth(list(w))
        ngood = nsb = 0
        gp = []
        for p in range(L + 1):
            for q in range(p, L + 1):
                ch = child(w, p, q)
                cs, cb, cd = word_status(ch, m + 2)
                if cs and cb:
                    nsb += 1
                    if cd == 1:
                        ngood += 1
                        gp.append((p, q))
        print(f"  m={m}: parent simple={s} bal={b} det={d} width={wd}; "
              f"children bal={nsb} good={ngood} "
              f"(parities {nsb%2},{ngood%2})")
        # structure
        W = walk(list(w))
        lab_at = lambda i: W[i] if i < L else (0, 0)
        pat = Counter()
        for (p, q) in gp:
            (ep, zp), (eq, zq) = lab_at(p), lab_at(q)
            pat[(zp - zmax, zq - zmax, ep ^ eq)] += 1
        top = sorted(pat.items(), key=lambda kv: -kv[1])[:8]
        print(f"    top patterns: {top}")


if __name__ == "__main__":
    which = sys.argv[1:] or ["E1", "E2"]
    stats = None
    for wname in which:
        if wname == "E1":
            e1_crosscheck()
        elif wname == "E2":
            e2_formula()
        elif wname == "E3":
            stats = e3_landscape()
        elif wname == "E4":
            e4_structure(stats)
        elif wname == "E5":
            e5_chain()
    print("DONE")


# ---------- narrow-family theorem verification ----------

def narrow_data(word, m):
    """(balanced, narrow, uniquemax, det, maxpos_by_class) for a word."""
    W = walk(word)
    zs = [z for _, z in W]
    wd = max(zs) - min(zs)
    bal, chords = diagram(word, m)
    if not bal:
        return False, wd == m - 1, None, None, None
    M = max(zs)
    maxpos = {0: [], 1: []}
    for i, (e, z) in enumerate(W):
        if z == M:
            maxpos[e].append(i)
    uniq = len(maxpos[0]) == 1 and len(maxpos[1]) == 1
    return True, wd == m - 1, uniq, gf2_det(chords), maxpos


def all_balanced_narrow(m):
    """Enumerate ALL words (all letter placements, not deduped by rotation)
    that are balanced and narrow at m.  Simplicity NOT assumed."""
    out = []
    n = 3 * m
    for pos in itertools.combinations(range(n), m):
        w = [2] * n
        for i in pos:
            w[i] = 1
        lab = walk(w)
        zs = [z for _, z in lab]
        if max(zs) - min(zs) != m - 1:
            continue
        by = Counter((e, z) for e, z in lab)   # integer values: narrow => residues distinct
        if len(by) != 2 * m or any(v > 2 for v in by.values()):
            continue
        out.append(w)
    return out


def v1_narrow_exhaustive(m):
    """Exhaustively verify every clause of the Narrow Insertion Theorem at
    modulus m (all balanced narrow words, no sampling)."""
    from criterion import budgets, word_loop, is_single
    print(f"V1(m={m}): exhaustive narrow-theorem check")
    words = all_balanced_narrow(m)
    print(f"  balanced narrow words (all placements): {len(words)}")
    t2 = budgets(m)[2]
    n_uniq = n_dbl = n_det1 = 0
    L = 3 * m
    for w in words:
        # (a) simplicity is automatic
        f = word_loop(m, w)
        assert f is not None, ("simplicity fails", w)
        # (b) det=1 <=> B_2 single (Cohn-Lempel, balanced coverage)
        bal, nar, uniq, det, maxpos = narrow_data(w, m)
        assert bal and nar
        assert (det == 1) == is_single(m, f, t2), ("C-L fails", w)
        n_det1 += det
        if uniq:
            n_uniq += 1
            for e in (0, 1):
                p = maxpos[e][0]
                ch = list(child(w, p, p))
                cbal, cnar, cuniq, cdet, cmaxpos = narrow_data(ch, m + 2)
                assert word_loop(m + 2, ch) is not None, ("child not simple", w, p)
                assert cbal, ("child not balanced", w, p)
                assert cnar, ("child not narrow", w, p)
                assert cuniq, ("child max not unique", w, p)
                assert cdet == det, ("det not preserved", w, p)
                # child's max positions are inside the cap: N2 at p+1, N5 at p+4
                assert sorted(cmaxpos[0] + cmaxpos[1]) == [p + 1, p + 4], \
                    ("cap max positions", w, p, cmaxpos)
        else:
            n_dbl += 1
            # tightness: NO insertion pair (p,q) gives a balanced child
            for p in range(L + 1):
                for q in range(p, L + 1):
                    ch = child(w, p, q)
                    s, b, d = word_status(ch, m + 2)
                    assert not b, ("double-max word has balanced child", w, p, q)
    # for unique-max words: no p<q pair and no off-max diagonal gives balance
    import random
    rng = random.Random(m)
    sample = [w for w in words if narrow_data(w, m)[2]]
    rng.shuffle(sample)
    for w in sample[:40]:
        _, _, _, _, maxpos = narrow_data(w, m)
        mp = {maxpos[0][0], maxpos[1][0]}
        for p in range(L + 1):
            for q in range(p, L + 1):
                if p == q and (p % L) in mp:
                    continue   # position L is cyclically position 0
                if p == 0 and q == L and 0 in mp:
                    continue   # (0, L) is cyclically the diagonal at 0
                s, b, d = word_status(child(w, p, q), m + 2)
                assert not b, ("non-max insertion balanced", w, p, q)
    print(f"  all pass: {n_uniq} unique-max (both children verified), "
          f"{n_dbl} double-max (no balanced child, exhaustive), "
          f"det=1 count {n_det1}; off-max non-balance checked on "
          f"{min(40, len(sample))} words x all pairs")


def v2_chain(mmax=40, verify_orbit_upto=40):
    """Iterate the deterministic narrow rule from all m=6 seeds; verify the
    invariant and direct B_2-singleness at every station."""
    from criterion import budgets, word_loop, is_single
    print(f"V2: narrow chains m=6 -> {mmax}")
    singles6 = load_m6_singles()
    seeds = []
    for c in singles6:
        bal, nar, uniq, det, maxpos = narrow_data(list(c), 6)
        if bal and nar and uniq:
            assert det == 1
            seeds.append(list(c))
    print(f"  seeds (narrow unique-max det=1 singles at m=6): {len(seeds)}")
    for si, seed in enumerate(seeds):
        w, m = seed, 6
        while m < mmax:
            _, _, _, _, maxpos = narrow_data(w, m)
            p = maxpos[0][0]          # deterministic: class-0 max
            w = list(child(w, p, p))
            m += 2
            bal, nar, uniq, det, maxpos2 = narrow_data(w, m)
            assert bal and nar and uniq and det == 1, (si, m)
            if m <= verify_orbit_upto:
                f = word_loop(m, w)
                assert f is not None
                assert is_single(m, f, budgets(m)[2]), (si, m)
        print(f"  seed {si}: chain verified to m={mmax} "
              f"(direct orbit check to {min(mmax, verify_orbit_upto)}); "
              f"final word len {len(w)}")
    return seeds


# ---------- closed form and Lemma C evidence ----------

def W_closed(m):
    """Closed form of the seed-0 narrow chain word:
    W_m = 112122 (1122)^{(m-6)/2} 1 2^{m-4} 212222122, even m >= 6."""
    j = (m - 6) // 2
    s = "112122" + "1122" * j + "1" + "2" * (m - 4) + "212222122"
    return [int(c) for c in s]


def v3_closed_form(mmax_word=100, mmax_orbit=60):
    """Verify W_closed == the deterministic chain from seed 0, and its
    invariant word-level to mmax_word, orbit-level to mmax_orbit."""
    from criterion import budgets, word_loop, is_single
    print(f"V3: closed form W_m; word-level to {mmax_word}, "
          f"orbit to {mmax_orbit}")
    # chain equality
    w, m = W_closed(6), 6
    while m < mmax_word:
        bal, nar, uniq, det, mp = narrow_data(w, m)
        assert bal and nar and uniq and det == 1, m
        assert len(w) == 3 * m and w.count(1) == m
        if m <= mmax_orbit:
            f = word_loop(m, w)
            assert f is not None and is_single(m, f, budgets(m)[2]), m
        w2 = list(child(w, mp[0][0], mp[0][0]))
        m += 2
        assert w2 == W_closed(m), ("closed form mismatch", m)
        w = w2
    print(f"  closed form == chain, invariant + det=1 word-level to "
          f"m={mmax_word}, B_2-single verified by direct orbit to "
          f"m={mmax_orbit}")


def v4_completability(ms=(8, 10, 12), tl=1800.0):
    """SAT-test completability (Lemma C) of the closed-form family words."""
    from criterion import budgets, word_loop, is_single, sat_completion
    print("V4: completability of W_m (closed form)")
    for m in ms:
        w = W_closed(m)
        f = word_loop(m, w)
        assert f is not None and is_single(m, f, budgets(m)[2])
        st, sol = sat_completion(m, f, require=("B0", "B1"), time_limit=tl)
        line = f"  m={m}: {st}"
        if sol:
            A0, A1 = sol
            ts = budgets(m)
            assert is_single(m, A0, ts[0]) and is_single(m, A1, ts[1])
            json.dump({str(p): [A0[p], A1[p], f.get(p, 0)]
                       for p in itertools.product(range(m), repeat=2)},
                      open(f"{SCR}/narrow_completion_m{m}.json", "w"))
            line += " (verified + saved)"
        print(line, flush=True)
