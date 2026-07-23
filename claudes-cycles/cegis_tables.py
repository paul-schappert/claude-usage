#!/usr/bin/env python3
"""CEGIS loop for class-based rule tables: train jointly on a set of even
moduli, test generalization on even m up to TEST_MAX, add the first failing
modulus to the training set, repeat.  Escalates through class schemes."""
import json
import time

from structured_search import solve_table, simulate

TEST_MAX = 60
SCHEMES = [
    # (a, b, parity, use_k, time_limit)
    (2, 2, True, True, 900),
    (3, 3, True, False, 900),
    (3, 3, True, True, 900),
    (4, 4, True, True, 1800),
]


def run():
    for a, b, parity, use_k, tl in SCHEMES:
        ms = [4, 6, 8, 10]
        for rounds in range(8):
            tag = f"a={a} b={b} par={parity} k={use_k}"
            t0 = time.time()
            status, table = solve_table(ms, a, b, parity, use_k=use_k,
                                        time_limit=tl)
            dt = time.time() - t0
            print(f"[{tag}] train={ms}: {status} in {dt:.0f}s", flush=True)
            if table is None:
                break  # scheme exhausted (infeasible or timeout) -> escalate
            bad = None
            for mtest in range(4, TEST_MAX + 1, 2):
                ok, msg = simulate(table, mtest, a, b, parity, use_k)
                if not ok:
                    bad = mtest
                    print(f"  fails at m={mtest}: {msg}", flush=True)
                    break
            if bad is None:
                fn = f"table_GENERAL_a{a}b{b}p{int(parity)}k{int(use_k)}.json"
                with open(fn, "w") as fh:
                    json.dump({str(k): v for k, v in table.items()}, fh,
                              indent=1)
                print(f"  *** GENERALIZES to all even m <= {TEST_MAX}; "
                      f"saved {fn} ***", flush=True)
                return
            if bad in ms:
                print("  UNEXPECTED: failing m already in training set; "
                      "abort scheme", flush=True)
                break
            ms.append(bad)
    print("all schemes exhausted", flush=True)


if __name__ == "__main__":
    run()
