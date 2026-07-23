# Findings — Hamilton decompositions of directed tori at even modulus

Working notes; session 1. Everything below is machine-verified where marked.

## Setup

D_d(m): vertices (Z_m)^d, arcs v → v+e_b. Decomposition = partition of arcs
into d directed Hamiltonian cycles ⟺ an assignment of a permutation of
directions to every vertex (cycle c at v moves in direction p_v(c)) such that
each cycle's functional digraph is a single m^d-cycle.

**Fiber view (d=3).** Slice by s = (i+j+k) mod m. Every arc maps fiber F_s to
F_{s+1}; fibers ≅ Z_m² via (i,j), k = s−i−j. Moves on fiber coordinates:
bump k = id, bump i = +e0, bump j = +e1. Cycle c is Hamiltonian ⟺ its
first-return map R_c = M_{c,m−1} ∘ ⋯ ∘ M_{c,0} is a single m²-cycle.
Conjugation by prefix maps shows only the cyclic composition order matters.

## Result 1: existence data (CP-SAT, independently verified)

Decompositions exist for: D_2(4), D_2(6), D_2(8), D_3(4), D_3(6), D_3(8),
D_3(10), D_4(4), D_4(6), D_4(2), D_5(2), D_6(2), D_7(2).
D_3(2) infeasible (reproves Aubert–Schneider 1982). D_5(4), D_8(2) timed out
(UNKNOWN). m=2 line for d≥4 likely follows from classical results (Stong;
Alspach–Bermond–Sotteau) — to be checked in detail.

## Result 2: rigid-class rule tables fail for even m (SAT-certified)

No Knuth-style table (direction permutation depending only on classes of
(i, j, s) with classes {0, generic, m−1}) works jointly for m = 4, 6, 8 —
CP-SAT proves infeasibility in seconds. Refining the generic class by parity
({0, GE, GO, m−1}) is also infeasible. (Knuth's theorem gives 760 such tables
for all odd m — the even case is structurally different, not just harder.)

## Result 3 (Lemma, proved + SAT-confirmed): uniform-idler obstruction

**Lemma.** Suppose a decomposition of D_3(m) has, on every fiber, one cycle
that idles (bumps k) at *every* vertex of the fiber. Then m is odd.

*Proof sketch.* (i) On such a fiber the two mover cycles split {e0, e1}
pointwise and both must be bijections; a collision analysis shows the split
must be measurable in u = (i+j) mod m (the bump-i set is a union of
anti-diagonals). (ii) Both moves increment u by 1, and idling preserves u, so
each return map R_c is a skew product over the rotation u → u + w_c of Z_m,
where w_c = #fibers where c moves. (iii) A skew product over u → u + w_c can
be a single m²-cycle only if gcd(w_c, m) = 1. (iv) For even m this forces
every w_c odd, hence every idle-count n_c = m − w_c odd; but n_0+n_1+n_2 = m
is even — contradiction. ∎

SAT confirmation: uniform-idler-constrained models are INFEASIBLE for
m = 4, 6 and FEASIBLE for m = 5, 7.

Interpretation: every even-m decomposition must swap the idler role *within*
some fiber. This is the precise locus of the "different splice mechanism"
that the odd-modulus torus papers anticipated.

## Result 4: a single swap fiber suffices (m = 4, 6; SAT + verified)

Constraining all fibers except fiber 0 to be uniform (single idler, uniform
e0/e1 mover split) still admits decompositions for m = 4 and m = 6. Hence
the entire even-m mechanism can be concentrated in ONE fiber gadget.

**Reduced problem (exact, by the conjugation reduction):** find move-fields
A_0, A_1, A_2 on Z_m² with
  (1) pointwise partition: at each p, {A_c moves} = {id, +e0, +e1};
  (2) each p ↦ A_c(p) is a bijection of Z_m²;
  (3) translation budgets: nonneg integers a_c, b_c with Σa_c = Σb_c = m−1
      (from the m−1 uniform fibers, which contribute translations);
  (4) each T_{(a_c, b_c)} ∘ A_c is a single m²-cycle.
Any solution yields a Hamilton decomposition of D_3(m); the search space is
now Z_m², not Z_m³.

Raw SAT gadgets for m = 4, 6 exist (swapsol_m4_ff0.json, swapsol_m6_ff0.json)
but are unstructured. Next: search the reduced problem with minimality/
symmetry objectives to force a generalizable gadget pattern.

## Useful gadget algebra (proved, small facts)

- The anti-diagonal serpentine pair on Z_m² — H_c: bump j iff i+j ≡ c else
  bump i; and its pointwise complement — are BOTH single m²-cycles for every
  m ≥ 2 (orbit closes only after m blocks of m steps). This gives the
  classical 2-cycle decomposition of D_2(m) for all m, matching our SAT data.
- A mover pair on a uniform-idler fiber is bijective iff its bump-i set is a
  union of anti-diagonals (collision/telescoping argument) — used in Lemma.
- Skew-product orbit criterion: (u,i) ↦ (u+w, i+g(u)) is a single m²-cycle
  iff gcd(w, m) = 1 and gcd(Σ_u g(u), m) = 1.

## Result 5: budget structure of the reduced problem (SAT, verified)

Scanning all translation-budget triples ((a_c, b_c), Σa_c = Σb_c = m−1):
- m=4: exactly 12/100 feasible — the rigid family {a_c} = {b_c} = {0,1,2}
  with b = a±1 (mod 3), up to cycle relabeling.
- m=6: 294/441 feasible. A budget pair (a_c, b_c) = (0, 0) is ALWAYS
  infeasible (105/105 of its occurrences) — no cycle can run on zero
  translation. 42 further infeasible triples remain uncharacterized.
- **Uniform budget family: t_0 = (0,1), t_1 = (1,2), t_2 = (−2,−4) mod m
  is feasible for m = 4, 6, 8, 10, 12** — constant translations independent
  of m. The whole problem now reduces to finding a uniform gadget pattern
  for this fixed budget family.

Additional impossibility notes (proved): gadget fields measurable in
u = i+j alone are impossible for all m (bijectivity forces a constant
idler-indicator along the u-cycle); fields measurable in v = i−j alone are
SAT-infeasible for m = 4, 6 across all budgets.

CP-SAT encoding caveat (cost a debugging round): AddCircuit interprets a
selected self-loop arc as "node excluded" — translation+move combinations
that wrap to the identity must be explicitly forbidden, not omitted.

## Result 6: sign obstruction (proved)

For even m an m²-cycle is an odd permutation and the family translations are
even permutations, so each gadget field A_c must be odd. Every nontrivial
{id,e0,e1}-staircase loop on Z_m² has even length m(w0+w1)... wait — length
is m·(w0+w1) which is even iff... for even m always even. Hence sgn(A_c) =
(−1)^{#loops}: each A_c needs an ODD number of staircase loops. Symmetric
patterns pair loops up — the likely root cause of every class-table failure.

## Result 7: three-curve reformulation and the surgery paradigm (mixed)

The pointwise-Latin condition is equivalent to: three closed monotone
staircase curves on the torus such that every vertex is visited by exactly
two curves — one stepping e0, one stepping e1 (the third cycle idles there).
The serpentine pair (H_d, C_d) realizes the double cover with A_2 = id —
forbidden (zero-translation/zero-gadget infeasibility). Findings:
- Minimal-deviation SAT gadgets: A_2 = single 3m-loop with winding parallel
  to the translation direction (1,2); (2,1) at m=6, (1,2) at m=8.
- The exact m=8 loop generalizes to an explicit family (helix12); it makes
  B_2 Hamiltonian for m = 4, 6, 8 ONLY.
- The diagonal staircase diag11 (winding (1,1), length 2m) makes B_2 a
  single m²-cycle for EVERY even m ≤ 40 — but admits NO completion of
  cycles 0, 1 (SAT-infeasible for m = 6, 8): the three cycles interlock;
  a gadget cannot be designed for one cycle in isolation.

## Result 8: no band-local mechanism (SAT)

Forcing all deviations from the serpentine background into a band of
v = i−j diagonals of width w: infeasible for all w ≤ 5 at m = 6 (band = 5/6
of the torus!) and m = 8, across all background offsets. Together with the
exhaustion of class-table schemes (boundary+parity classes in i, j, u, v up
to depth 3–4, both budget families): the even-m gadget is inherently GLOBAL.
The "local splice on an odd-style background" paradigm is ruled out.

## Road map (updated)

The next push is analytic, not search: derive the exact single-cycle
criterion for T ∘ A where A is a union of staircase loops (first-return /
interval-exchange analysis on the loop), then co-design the three curves
globally to satisfy all three criteria simultaneously. The helix12 family
and its m ≤ 8 successes give the test bed for the criterion.

## Open threads

1. Solve the reduced gadget problem uniformly in even m (design or forced
   pattern from minimal solutions for m = 4..12).
2. Prove the resulting construction for all even m ≥ 4 (orbit tracing on the
   piecewise-affine return maps).
3. Dimension lift d → d+1: at a special fiber, the d−1 movers can follow the
   d−1 cycles of an inductively-obtained decomposition of D_{d−1}(m)
   (pointwise-disjointness = the decomposition property). Base cases: d=2 all
   m (serpentine pair); d=3 as above. Needs the return-map analysis to
   survive the lift.
4. Structured-table search (scheme with explicit 1, m−2 classes) still
   running in background.
5. Settle D_5(4), D_8(2) with longer runs (low priority).

## Result 9 (Phase 6): the Insertion Lemma — proved for an explicit
## infinite family (Lemma B is now a theorem on that family)

Full mathematics in scratchpad `insertion_lemma.md`, code+verifications in
`insertion_lemma.py` (E1–E5, V1–V4). Highlights:

* **Exact transformation** of the chord diagram under double-period
  insertion at (p, q): in the integer label walk (eps, z) = (a mod 2,
  3a − i), z NEVER shifts — the entire global re-pairing is (i) a parity
  flip on the segment between the insertion points, (ii) six explicit cap
  labels, (iii) modulus change m → m+2. Machine-exact (1200 random
  triples).
* **Narrow Insertion Theorem** (proved + exhaustively verified at
  m = 6, 8): for balanced words of minimal z-width m−1, the ONLY
  balance-preserving insertions are the two diagonal insertions at the
  walk maximum (which must be unique per parity class), and these
  preserve det_{GF(2)} of the interlacement matrix UNCONDITIONALLY — the
  two new chords border the matrix with a zero interlacement row, so
  cofactor expansion kills the correction. Simplicity of narrow balanced
  loops is automatic (proved).
* **Theorem.** W_m = 112122 (1122)^{(m−6)/2} 1 2^{m−4} 212222122 is a
  balanced simple gadget word with B_2 = T_{(−2,−4)} ∘ A(W_m) a single
  m²-cycle for EVERY even m ≥ 6. (Induction via the narrow theorem +
  Cohn–Lempel; 7 seed chains verified by direct orbit count to m = 40,
  the closed form to m = 100 word-level / m = 60 orbit-level.)
* **Obstruction identified:** the universally-quantified insertion lemma
  is FALSE — at m = 6, 10/77 balanced det-1 parents have no good pair and
  two parents have NO B_2-single child at all over the full insertion set
  (corrects the "never zero" impression of phase 5, which was a biased
  sample); parity-averaging over pairs provably cannot work (mixed
  parities 47/30). Existence had to be — and now is — proved on a closed
  sub-family.
* **Lemma C honest status:** W_m completable at m = 14 (verified full
  solution saved) but INFEASIBLE at m = 8, 10, 12; tree-wide, 4/14
  narrow-tree words complete at m = 8 and 4/28 at m = 10. The dense-cycle
  template (obligation 3) is now the single remaining gap between the
  narrow family and a full uniform theorem.
