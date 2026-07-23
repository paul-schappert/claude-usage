# Solution-space mining: reduced gadget problem on Z_m^2

Setting: move-fields A_0, A_1, A_2 on Z_m^2, pointwise partition of {id, e0, e1},
each a bijection; B_c = T_{t_c} o A_c must be a single m^2-cycle. Uniform budget
family t_0 = (0,1), t_1 = (1,2), t_2 = (-2,-4) mod m; plus the m=4 rigid case
t = (0,1), (1,2), (2,0). Every collected solution was independently re-verified
with `verify_gadget`. Data: `mining_m6.json` (solutions + per-solution stats +
aggregates + post_analysis). Targeted SAT certificates: `targeted_tests.json`,
`winding_table_m6.json`.

Terminology: the "loops" of A_c are the cycles of the permutation p -> p+move
on its support (staircase loops; a loop of winding (w0,w1) has length m(w0+w1)
and visits every u = i+j diagonal exactly w0+w1 times). "Idle set" I_c = fixed
points of A_c. Coset structure: support(A_c) vs cosets of <t_c> in Z_m^2.

## Collection sizes

| case | budgets | collected | completeness | translation orbits |
|---|---|---|---|---|
| m=4 | (0,1),(1,2),(2,0) | **128** | COMPLETE enumeration | 8 free orbits of size 16 |
| m=6 | (0,1),(1,2),(4,2) | **2291** | capped enum (2000) + 430 random probes, deduped | 184 free orbits of size 36 |
| m=8 | (0,1),(1,2),(6,4) | **777** | capped enum (500) + 277 probes | 774 free orbits of size 64 |

The Z_m^2 translation action is free on every collected solution (no solution
has a nontrivial translation stabilizer).

## m=4 rigid case: complete characterization (all 128 solutions)

- Exactly 128 solutions = 8 free translation orbits.
- EVERY solution: each A_c is a SINGLE staircase loop; windings are FIXED:
  A_0: (2,1), A_1: (1,1), A_2: (1,2). Combined multiset always
  {(1,1),(1,2),(2,1)}. Idle sizes always (4,8,4).
- Idle u-profiles exactly balanced: (1,1,1,1) for c0,c2 and (2,2,2,2) for c1.
- support(A_c) covers all cosets of <t_c> in all 128 solutions; exact
  transversality NEVER occurs (support sizes 12,8,12 vs 4,4,8 cosets).
- Coset hit profiles constant for c1: (1,2,2,3) and c2: (1,1,1,1,2,2,2,2);
  c0 takes two values (3,3,3,3) / (2,3,3,4), 64 solutions each.
- Row/col/v idle profiles each take exactly 2 values (64/64 split).

## m=6: invariants across all 2291 solutions, several now SAT-CERTIFIED

Certified by targeted infeasibility runs (not just sample-invariant):

1. **No axis-parallel loop.** Forcing a (1,0) row loop or (0,1) column loop
   into any A_c is INFEASIBLE (6 runs; translation invariance covers all
   rows/columns; a winding-(k,0) loop is necessarily a straight row with k=1).
   Hence every loop has w0 >= 1 and w1 >= 1.
2. **No zero-idle cycle.** Forcing I_c empty is INFEASIBLE for each c. Hence
   W0+W1 <= 5 per cycle (support = m(W0+W1) <= 30).
3. **Every A_c is a single loop — CERTIFIED THEOREM at m=6.** By (1) each loop
   has support >= 2m = 12; three or more loops would need support >= 36 = m^2,
   i.e. zero idle, contradicting (2); two loops are excluded by the parity
   theorem (Result 6: odd number of loops). Sample agrees: loop_count_vector =
   (1,1,1) in all 2291 solutions.
4. **Exact per-cycle winding table** (42 SAT runs, all decided; O = feasible):

   | w | (1,1) | (1,2) | (1,3) | (1,4) | (2,1) | (2,2) | (2,3) | (3,1) | (3,2) | (4,1) |
   |---|---|---|---|---|---|---|---|---|---|---|
   | c0, t=(0,1) | O | X | X | X | O | X | O | O | O | O |
   | c1, t=(1,2) | O | O | O | O | O | X | O | O | O | X |
   | c2, t=(4,2) | X | O | O | O | O | X | O | O | O | X |

   The mined sample realized EXACTLY the feasible sets (6/8/7 winding values
   for c0/c1/c2) — the sample is winding-complete. Note: the non-primitive
   winding (2,2) is infeasible for every cycle; (1,1) is infeasible precisely
   for c2 (whose translation (4,2) is the non-primitive budget); c0 (budget
   (0,1)) admits no winding with w0 < w1 except (2,3).
5. **Winding-sum split.** Sum_c (W0+W1) = 2m = 12 always (trivial identity:
   every point donates e0 to exactly one cycle, so Sum w0 = Sum w1 = m).
   Splits observed: (5,4,3)-type (1733 solutions) and (5,5,2)-type (558).
   The (4,4,4) split (idle sizes (12,12,12)) is CERTIFIED INFEASIBLE.
   Consequently some cycle always has W0+W1 = 5 (idle size 6).
6. **No fully idle row or column** for any cycle (6 INFEASIBLE runs).
7. **Strict-alternation diagonal loops cannot coexist with anything.** Forcing
   the alternating (1,1) diagonal loop into A_c plus at least one extra support
   point: INFEASIBLE for all c (consistent with the earlier diag11
   no-completion result). Windings (1,1) do occur (558 solutions, always in
   c0 or c1) but always as non-alternating staircase words.

Sample-level invariants (true in all 2291, not separately certified):

- support(A_c) covers ALL cosets of <t_c> for every c (c0: 6 cosets of the
  order-6 group <(0,1)>; c1: 6 cosets of <(1,2)>; c2: 12 cosets of the
  order-3 group <(4,2)>).
- Exact coset transversality NEVER occurs for any cycle.
- Idle u-profile is always perfectly balanced: exactly m - (W0+W1) idle
  points on every u = i+j diagonal (this is a theorem: staircase loops visit
  each u-class w0+w1 times; verified on all solutions, all three m).
- Row / column / v-diagonal idle profiles are NOT balanced in general:
  balanced row profile occurs in 243 (c0) / 0 (c1) / 102 (c2) solutions;
  balanced column profile in 0 / 0 / 324; balanced v profile in 48 / 174 / 129.
  No idle set ever contains 6 points of one row (max observed 5, and a full
  idle row is certified infeasible).
- Combined winding multisets: exactly 6 occur:
  {(1,4),(2,1),(3,1)} x1104, {(1,1),(2,3),(3,2)} x538, {(1,2),(1,3),(4,1)} x276,
  {(1,2),(2,3),(3,1)} x206, {(1,3),(2,1),(3,2)} x147, {(1,1),(1,4),(4,1)} x20.
- c2 coset hit profiles (12 cosets): 7 profiles occur; dominant is
  {2:6, 3:6} (1448); the balanced {1:6, 2:6} occurs in exactly 159 solutions.

## m=6 sparse-A_2 regime (feeds the theory thread)

Conditioning on A_2 a single (1,2) or (2,1) loop (support 18): 159 solutions.

- In ALL 159, the c2 coset hit profile is EXACTLY the balanced {1:6, 2:6} —
  independent corroboration (from unconstrained mining) of the theory thread's
  proven necessity of the balanced profile.
- Joint dense-cycle windings (w_A0, w_A1): only 5 pairs occur:
  ((4,1),(1,3)) x40, ((3,1),(1,4)) x39, ((2,3),(3,1)) x30, ((3,2),(1,3)) x25,
  ((3,1),(2,3)) x25. Idle sizes of the dense pair are always {6,12}.
- Dense-cycle idle geometry: u-profiles balanced (theorem); row/col/v profiles
  vary but are highly constrained; e.g. c0 idle row profile is perfectly
  balanced (1,1,1,1,1,1) in the entire ((4,1),(1,3)) family (40/40), and c1
  col profile is near-balanced (1,2,2,2,2,3) in 45 cases. Full distributions
  in mining_m6.json (post_analysis / per-solution stats).

## m=8 sample (777 solutions) — multi-loop fields appear

- **Multi-loop A_c exist at m=8** (impossible at m=6): loop_count_vector is
  (3,1,1) x413, (1,3,1) x151, (1,1,3) x165, (1,1,1) x48. The 3-loop cycle's
  loops are ALWAYS three (1,1) loops (support 3*16 = 48 < 64, which is why
  m=8 can host them while m=6 cannot: 3*12 = 36 = 6^2 leaves zero idle).
  The (1,1) triples are irregular staircase words, NOT strict alternation.
- Certified at m=8: no axis loops (x6), no zero-idle cycle (x3). With the
  parity theorem this certifies loop counts in {1,3} at m=8, and at most one
  3-loop cycle is... NOT forced by counting ((3,3,1) needs support >= 112 <=
  128, so it is not excluded) — yet (3,3,*) never occurs in 777 samples.
- Dominant combined winding multiset: {(1,1)x3, (2,3), (3,2)} (716/777).
- Invariants matching m=6: covers_all_cosets always true (all c), exact
  transversality never, loop-count parity always odd, idle u-profiles exactly
  balanced, winding components always >= 1.

## Invariant summary (every collected solution, all three cases)

1. Odd number of loops per cycle (theory Result 6) — confirmed 3196/3196;
   at m=4 and m=6 the count is exactly 1 (certified at m=6).
2. Every loop winding has w0, w1 >= 1 (axis loops certified infeasible at
   m=6 and m=8).
3. Every cycle has a nonempty idle set (certified at m=6, m=8); idle sizes
   are multiples of m; idle u = i+j profile perfectly balanced (theorem).
4. support(A_c) meets every coset of <t_c>; NEVER an exact transversal.
5. Sum of windings = (m, m) (identity); at m=6 the per-cycle split is only
   ever (5,4,3) or (5,5,2), never (4,4,4) (certified).
6. Translation action is free: no solution has a translation symmetry.
7. Row/column/v-diagonal idle profiles are NOT invariants (they vary widely);
   only the u-profile is rigid.
