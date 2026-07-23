# Problem contract: Hamilton decompositions of directed tori at even modulus

## Problem statement

For integers d ≥ 2 and m ≥ 2, let D_d(m) be the digraph with vertex set
(Z_m)^d and, for every vertex v and every coordinate b ∈ {0, …, d−1}, an arc
from v to v + e_b (addition mod m), where e_b is the b-th unit vector. D_d(m)
is d-regular (in and out); it has d·m^d arcs.

A *Hamilton decomposition* of D_d(m) is a partition of its arc set into d
arc-disjoint directed Hamiltonian cycles (each of length m^d).

**Goal: determine, with full proof, for which pairs (d, m) with m even the
digraph D_d(m) admits a Hamilton decomposition — in particular prove that a
decomposition exists for all d ≥ 3 and all even m ≥ 4 (if true), via an
explicit construction.**

## Known context (as of 2026-07)

- d = 3, odd m ≥ 3: solved (construction found by Claude Opus 4.6; proof by
  Knuth, "Claude's Cycles", 2026; Lean formalization by Kim Morrison).
- d = 3, m = 2: impossible (Aubert–Schneider 1982; re-verified here by SAT).
- All d ≥ 2, odd m ≥ 3: solved (arXiv 2603.24708, 2604.27140, 2605.00660,
  2605.04734, 2606.21583 — return-map / odometer / Latin-table methods; the
  authors note even modulus needs "a different table or splice mechanism").
- d = 3, even m ≥ 8: claimed by Ho Boon Suan (AI-assisted 14-page proof),
  NOT published on arXiv, NOT formalized, NOT independently verified, and not
  accessible from this environment. We treat the case as unsettled and aim
  for an independent, verifiable proof.
- Empirical: decompositions exist for D_3(m), 4 ≤ m ≤ 16 (Stappers) and for
  even m ≤ 2000 via an unproven generated construction (Ho).
- New empirical results from this project (CP-SAT, independently verified):
  D_4(2), D_5(2), D_6(2), D_2(4), D_2(6), D_2(8), D_3(4), D_3(6), D_4(4)
  all decompose. So the m = 2 impossibility is isolated to d = 3.

## What counts as a solution

Exactly one of:

1. **Affirmative:** an explicit construction (finite rule table / splice
   scheme) together with a complete, self-contained proof that it yields d
   arc-disjoint directed Hamiltonian cycles in D_d(m) for every pair (d, m)
   in the claimed range (at minimum: d = 3 and all even m ≥ 4; ideally all
   d ≥ 3, even m ≥ 4, plus a determination of the m = 2 line and d = 2 line).
2. **Negative:** a proof that some claimed-range pair admits no
   decomposition, exhibiting the obstruction.

## Weaker results that do NOT count

- Computational verification for any finite set of (d, m), however large.
- A construction "verified numerically" without proof of correctness.
- Reduction to another unproved statement of comparable strength.
- Asymptotic or density statements ("all sufficiently large even m" without
  an effective bound and coverage of the small cases by certificate).
- Probabilistic or heuristic arguments.

## Problem-specific traps and edge cases

- **Parity trap:** Knuth's odd-m proof tracks first returns to the hyperplane
  s = Σ coords ≡ 0 (mod m); a coordinate advances by +2 per revolution, and
  2 generates Z_m only for odd m. Any even-m construction must contain an
  explicit parity-breaking mechanism. An argument that silently reuses a
  "+2 generates" step is WRONG for even m.
- **Single-cycle vs. permutation:** the per-vertex direction assignment being
  a permutation of {0..d−1} guarantees arc-disjointness and in/out-degree 1,
  but NOT connectivity. Every cycle must be proved to be a single m^d-cycle.
- **m = 2 anomaly:** D_3(2) is impossible but D_d(2) for d = 4, 5, 6 exists.
  Any general even-m claim must handle m = 2 separately or exclude it
  explicitly.
- **Fiber/return-map arguments:** when quotienting by s = Σ coords mod m,
  Hamiltonicity is equivalent to the first-return map being a single
  m^{d−1}-cycle on the fiber — this equivalence must be stated and proved,
  not assumed.
- **Index arithmetic mod m:** off-by-one and mod-m wraparound errors in rule
  tables are the dominant failure mode; every rule table must be machine-
  checked for the base cases before proof effort is spent.

## Verification requirements

- Every candidate construction is machine-verified (independent checker, not
  the searcher) for all even m up to at least 40 in d = 3, and all feasible
  (d, m) with m^d ≤ 10^6 in higher d, before being believed.
- Every candidate lemma gets an adversarial pass: attempt to construct a
  counterexample (small m, boundary vertices, wraparound) before attempting
  a proof.
- Final target: Lean formalization against the statement
  `cube_hamiltonian_arc_decomposition_even` in google-deepmind/
  formal-conjectures (d = 3) and its d-dimensional generalization.

## Search management

Keep several routes alive: (a) class-based rule tables (Knuth-style, refined
by parity), (b) m → m+2 splice induction from a base case, (c) d → d+1
dimension lift compatible with even m, (d) direct return-map/odometer design.
Mark a route blocked if it merely reduces to another unproved statement.
