"""Explicit A2 loop families and B2 single-cycle tests."""
from reduced_gadget import MOVES

def helix12(m):
    """3m-loop, winding (1,2), matching the m=8 SAT artifact exactly."""
    f = {}
    f[(0, 0)] = 1
    for j in range(m - 1):
        f[(1, j)] = 2
    f[(1, m - 1)] = 1
    f[(2, m - 1)] = 2
    f[(2, 0)] = 2
    for i in range(2, m - 1):
        f[(i, 1)] = 1
    f[(m - 1, 1)] = 2
    f[(m - 1, 2)] = 1
    for j in range(2, m):
        f[(0, j)] = 2
    return f

def transpose(f, m):
    return {(j, i): (2 if mv == 1 else 1 if mv == 2 else 0)
            for (i, j), mv in f.items()}

def helix21(m):
    return transpose(helix12(m), m)

def diag11(m):
    f = {}
    for i in range(m):
        f[(i, i)] = 1
        f[((i + 1) % m, i)] = 2
    return f

def check_loop(m, f):
    supp = [p for p, mv in f.items() if mv != 0]
    start, cur, seen = supp[0], supp[0], set()
    while True:
        if cur in seen:
            return False
        seen.add(cur)
        mv = f.get(cur, 0)
        if mv == 0:
            return False
        dx, dy = MOVES[mv]
        cur = ((cur[0] + dx) % m, (cur[1] + dy) % m)
        if cur == start:
            break
    return len(seen) == len(supp)

def b2_single_cycle(m, t2, f):
    ac, bc = t2
    start, cur, n = (0, 0), (0, 0), 0
    while True:
        mv = f.get(cur, 0)
        dx, dy = MOVES[mv]
        cur = ((cur[0] + dx + ac) % m, (cur[1] + dy + bc) % m)
        n += 1
        if cur == start:
            break
        if n > m * m:
            return False
    return n == m * m

if __name__ == "__main__":
    for m in range(4, 41, 2):
        t2 = ((-2) % m, (-4) % m)
        res = []
        for name, fam in (("helix12", helix12), ("helix21", helix21), ("diag11", diag11)):
            f = fam(m)
            ok = check_loop(m, f) and b2_single_cycle(m, t2, f)
            res.append(f"{name}={'YES' if ok else 'no'}")
        print(f"m={m}: " + "  ".join(res), flush=True)
