# Main theorem file: Hamilton decompositions of D_3(m), even m — final
# phase: soundness audit, the realizability obstruction, the repaired
# pipeline, and the exact remaining gap

Session 4 (final phase). Verification driver: `main_theorem.py` (sections
T1–T6; a single run re-verifies every claim marked [M] below). Supporting
code this session: `assembler.py` (obstruction + fiber-schedule assembly),
`dense_template2.py` (budget-parametric closure census, P1–P3),
`narrow_census.py` / `narrow_census2.py` (abstract-tree census m ≤ 24),
`budget_scan2.py`, `narrow_censusF.py`, `greedyF.py` (realizable-family
census + 3D assembly). Everything runs on stock python3 + ortools.

## 0. Executive summary

1. **A soundness gap in phases 3–7 was found and machine-confirmed**: the
   "uniform budget family" t_0 = (0,1), t_1 = (1,2), t_2 = (−2,−4), on
   which all completability work since Result 5 was built, is
   **unrealizable in D_3(m) for every even m ≥ 6** — no Hamilton
   decomposition of the actual torus can induce those return maps (§2).
   All uniform-family "completions" at m ≥ 6 (chains, dense template,
   narrow census, mining at m = 6, 8) are solutions of an abstract
   permutation problem only.
2. **The pipeline was repaired**: for *balanced* gadget words the
   single-cycle criterion is direction-symmetric (§3), so the entire
   Narrow Insertion Theorem (Pillar 1) transfers verbatim to the budget
   t_2 = (+2,+4) — which IS realizable. A concrete realizable budget
   family F with t_2 = (2,4) was found under which the narrow tree is
   completable at every tested level (§4).
3. **Real, independently verified Hamilton decompositions of D_3(m) now
   exist for every even m in [4, M]** (M ≥ 22 at the time of writing; see
   `main_theorem.py T5` output for the exact frontier), each m ≥ 8 station
   assembled from a narrow-tree gadget completion through an explicit
   fiber-role schedule and checked by the independent 3D checker
   (`torus_decomp.check`) [M: T1, T5].
4. **The uniform-in-m theorem remains open.** The precise remaining gap
   (§6): prove that for every even m ≥ 8 some narrow-tree word admits a
   family-F completion. Edge-level inheritance of completability is
   FALSE (machine counterexample, both budget families); completability
   recurs at the *level* of the tree with growing density, and any proof
   must aggregate across the level.

## 1. Architecture and exact reduction (corrected statement)

Slice Z_m³ by s = i+j+k mod m; fibers ≅ Z_m² via (i,j). Cycle c's
transition F_s → F_{s+1} is an {id, e0, e1}-field; at each vertex the
three cycles use the three directions (Latin), and each transition field
must be bijective. A decomposition ⟺ all three return maps
R_c = M_{c,m−1} ∘ ⋯ ∘ M_{c,0} are single m²-cycles.

**Single-swap architecture.** All fibers s ≠ 0 uniform: fiber s assigns
{bump i, bump j, bump k} to the three cycles bijectively; fiber 0 carries
Latin bijective fields (A_0, A_1, A_2). Then R_c = T_{(a_c, b_c)} ∘ A_c
where a_c (resp. b_c) = #fibers where cycle c is the i-mover (j-mover).

**Realizability (Lemma R).** Integer matrices (a_c), (b_c) ≥ 0 arise from
a fiber-role schedule iff Σ_c a_c = Σ_c b_c = m−1 and a_c + b_c ≤ m−1 for
each c. Necessity: each of the m−1 uniform fibers has exactly one i-mover
and one j-mover, and they differ. Sufficiency: 3×3 zero-diagonal
transportation; the greedy scheduler in `assembler.py` constructs a
schedule and [M: T2/O2] the criterion is exhaustively exact against
search over all budget matrices at m = 6, 8; [M: T4] schedules are
constructed and validated for family F for all even m ∈ [8, 60].

**Assembly (machine bridge).** `assembler.assemble` builds the full
direction assignment on Z_m³ from (a, b, fields) and every claimed
decomposition below is re-verified by the independent checker
`torus_decomp.check` (arc-partition + three Hamiltonian cycles). [M: T5]

## 2. The obstruction theorem (why phases 3–7 needed repair)

**Theorem O.** For even m ≥ 6, no Hamilton decomposition of D_3(m) has a
cycle whose return map is T_{(−2,−4)} ∘ A with A an {id, e0, e1}-field.
In particular the uniform budget family of Result 5 is unrealizable.

*Proof.* A return path from p ∈ F_0 back to F_0 takes exactly m arc
steps, one per fiber, each bumping exactly one of i, j, k. Let x, y, z
be the numbers of i-, j-, k-bumps: x + y + z = m, all ≥ 0. The
displacement is (x, y) as integers, and x ≡ (t_2 + a(p))_x (mod m) with
x ∈ [0, m]. For t_2 = (−2,−4): if a(p) = 0 then x = m−2, y = m−4, so
z = 6 − m ≤ 0, forcing m = 6 and z = 0; if a(p) = e0 then x = m−1,
y = m−4, z = 5 − m < 0, impossible (a(p) = e1 symmetric). So for m ≥ 8
no point exists at all, and for m = 6 every point must be idle — A = id,
which is not bijectively completable to a decomposition (B_2 would be a
translation with m²/ord > 1 cycles). ∎  [M: T2/O1 checks the arithmetic
for all even m ∈ [6, 60] and exhaustively confirms no fiber schedule.]

Scope of the damage (all machine-reconfirmed this session): every
"completion" artifact under the uniform family at m ≥ 6 — the k=1/k=2
chains (m = 6..24), wlaw/word12/surgery reduced artifacts, the dense
template stations, the narrow-tree census, and the m = 6, 8 mining
corpora — is a solution of an abstract permutation problem that does not
correspond to D_3(m). The *analytic machinery* (first-return criterion,
ν∘σ factorization, Cohn–Lempel bridge, dual factorization, bit-field
closure system, insertion calculus, narrow-word theorems) is
budget-generic or word-level and survives intact. Base data (direct SAT
solutions m ≤ 10, swapsol artifacts, fiber_construction) was always real:
the genuine artifact `swapsol_m6_ff0.json` realizes the schedulable
budgets a = (1,4,0), b = (0,1,4) — not the uniform family.

## 3. Direction independence and the repaired Pillar 1

**Lemma D (direction symmetry for balanced words).** Let W be a balanced
gadget word (every ⟨t⟩-coset hit ≤ 2 times, all hit). Then
T_t ∘ A(W) is a single m²-cycle ⟺ T_{−t} ∘ A(W) is. *Proof.* Coverage is
direction-blind. R = ν ∘ σ (induction3 Thm 1.1), and on a balanced
support ν maps each doubleton-coset point to its partner and each
singleton to itself — the same involution for t and −t. So the return
maps coincide. ∎  [M: P1] all 122 balanced simple words at m = 6, exact
equivalence.

Note (−t vs t at the triple level): the pointwise involution
Ã_c(p) = −A_c⁻¹(−p) maps Latin bijective triples to Latin bijective
triples with all budgets negated (in-arcs of a Latin triple are Latin),
so the *abstract* problems for (t_c) and (−t_c) are isomorphic; but
realizability is not preserved (the residue sums flip from −1 to +1),
which is why the sign of t_2 matters physically.

**Theorem P1 (Pillar 1, realizable form).** For every even m ≥ 6 the
narrow tree (7 seeds at m = 6; both diagonal max-insertions at each
station) consists of balanced, narrow, unique-max words with
det_{GF(2)} A(W) = 1, and every tree word W at modulus m has
B_2 = T_{(2,4)} ∘ A(W) a single m²-cycle. In particular the closed-form
branch W_m = 112122 (1122)^{(m−6)/2} 1 2^{m−4} 212222122 works for every
even m ≥ 6.

*Proof.* The word-level clauses are the Narrow Insertion Theorem
(insertion_lemma.md Thm 3/4 — unchanged, it never referenced the budget).
Singleness under (2,4): balanced + coverage + Cohn–Lempel gives
singleness ⟺ det = 1 for the return map R = ν∘σ, which by Lemma D is the
same map as under (−2,−4). ∎  [M: T3] word-level (balanced / narrow /
unique-max / det 1 / closed-form recursion identity) to m = 60 and
DIRECT orbit verification of T_{(2,4)} ∘ A(W_m) to m = 40; [M: P2] same;
the tree-wide singleness at every censused level is asserted inside
`narrow_censusF.py` for every word before censusing.

## 4. Family F and the realizable completability landscape

**Family F**: residues t_0 = (1, −6), t_1 = (−4, 1), t_2 = (2, 4);
lifts a = (1, m−4, 2), b = (m−6, 1, 4). Realizable for every even m ≥ 8:
Σa = Σb = m−1, per-cycle sums (m−5, m−3, 6) ≤ m−1, and the explicit
schedule (c1→c2)×4, (c1→c0)×(m−8), (c0→c1)×1, (c2→c0)×2 works for all
m ≥ 8 [M: T4 constructs and validates schedules to m = 60].

Family F was selected by an exhaustive scan of ALL 22 schedulable budget
matrices with cycle-2 lifts (2,4) at m = 8 (`budget_scan2.py`): most
matrices admit completions of some narrow words (0–4 of 14); the two
best (4/14) extend to constant-residue schedulable families; F is one.

**Completion machinery (budget-parametric).** The swap-bit closure
system C(W; t_0, t_1) of dense_template.md carries over verbatim — the
dual alphabets are budget-independent, only the dual translations
(t_0 + e0, t_1 + e1) and their coverage cosets change
(`dense_template2.template_model2`). Under family F both dense cycles
have odd translation-coordinate sums (1 + (m−6), (m−4) + 1), so the
empty-idle case is killed by the u-parity argument and all model
constraints are *necessary*: the census verdict (completable or not) is
exact. [M: T6] verified against circuit SAT on all 14 narrow words at
m = 8, both verdict directions.

**Census results (family F, full narrow tree, exhaustive per word):**

| m  | words | completable | first assembled station        |
|----|-------|-------------|--------------------------------|
| 8  | 14    | 4           | seed 2, branch 1               |
| 10 | 28    | 4           | seed 0, branch 01              |
| 12 | 56    | 7           | seed 1, branch 001             |
| 14 | 112   | 19          | seed 0, branch 0000 (= W_14)   |
| 16 | 224   | 60          | seed 0, branch 00010           |
| 18 | 448   | 63          | seed 0, branch 000001          |
| 20 | 896   | 206         | seed 0, branch 0000111         |
| 22 | 1792  | 359         | seed 0, branch 0^8 (= W_22)    |
| 24 | 3584  | (census)    | seed 0, branch 000000110       |
| 26+| —     | greedy mode | see narrow_censusF/greedyF logs|

Every "first assembled station" is a full D_3(m) decomposition: reduced
completion verified (Latin, bijective, three single m²-cycles under F),
assembled through the fiber schedule, and accepted by the independent 3D
checker; artifacts `famF_completion_m{m}.json`, `famF_decomp3d_m{m}.json`.
[M: T5 re-verifies all stored stations end-to-end.]

**Main verified theorem.**

> **Theorem M.** D_3(m) admits a Hamilton arc-decomposition for every
> even m ∈ [4, M], where M is the largest stored station (run
> `python3 main_theorem.py T5`; M ≥ 22 as of this session, extension
> running). Certificates: m = 4, 6 direct artifacts; m ≥ 8 family-F
> narrow-tree completions, all independently 3D-checked.

## 5. The inheritance question (task 2): definitive negative + structure

The hoped-for induction step was: "if a narrow word W is completable,
some insertion child of W is completable" (possibly via a triple
(W, dual word 0, dual word 1) invariant). This is **FALSE** — machine
counterexamples in both budget worlds:

* family F: at m = 8 the completable set is {(2,'1'), (4,'1'), (6,'0'),
  (6,'1')}; ALL 8 of their children at m = 10 are non-completable
  (exhaustive closure censuses). The m = 10 completable set
  {(0,'01'), (1,'10'), (2,'00'), (5,'01')} consists of children of
  non-completable parents.
* abstract uniform family: identical phenomenon (4 completable at m = 8,
  zero completable children at m = 10).

Since the closure system captures ALL completions (Theorem D2,
budget-parametric, SAT-validated), no edge-level invariant of any kind
can exist: completability is simply not hereditary along tree edges.
What the data supports instead:

* **Level nonemptiness with growing density**: at every level
  m ∈ [8, 24] (abstract) / [8, 22+] (family F) some words complete;
  fraction grows from ~14 % to ~25 %.
* **Bounded-depth recurrence (empirical)**: with the m ≤ 24 abstract
  data, every completable word has a completable descendant within
  depth ≤ 4 wherever the horizon suffices (depth-3 fails: 4 words at
  m = 18 need depth ≥ 4 or more). Unproven; would give the uniform
  theorem by induction with finitely many base cases if proved for any
  fixed depth.
* The dual-gadget transformation under diagonal insertion is not
  word-local: the completion's dual supports Σ_0, Σ_1 change globally
  between parent and child completions (consistent with induction3 §3's
  "verdict GLOBAL" for the pointwise fields). The toggle boxes of parent
  and child closure systems have unrelated sizes (see census columns
  `closure` at consecutive stations of a fixed branch).
* Dual-word structure of actual family-F completions (m = 8, 14, 20
  extracted): each dual D_0, D_1 is a SINGLE loop (odd loop count, as the
  sign theory demands) but its coset profile over the dual translation is
  far from balanced (multiplicities up to ~m/2). So the "joint GF(2)
  rank" formulation of the two dense criteria would need the generalized
  (Traldi-type) interlacement for ν with long coset cycles — the plain
  Cohn–Lempel chord calculus applies to the gadget word only. This
  quantifies exactly how much harder the dual side is than Pillar 1.

## 6. Honest gap ledger (what a complete proof still needs)

1. **The one remaining mathematical gap** for "every even m ≥ 4":
   *for every even m ≥ 8, SOME narrow-tree word at level m admits a
   family-F completion.* Equivalent finite form (all machinery proven):
   the closure system C(W; F) of some level-m narrow word contains a
   bit field whose two dual return maps are single cycles. Status:
   machine-verified for every even m ∈ [8, M]; no per-level mechanism
   identified; edge-inheritance provably unavailable (§5). Candidate
   routes: (a) prove the depth-≤ k descendant recurrence for some fixed
   k; (b) aggregate parity/counting over a level (no invariant found so
   far: completion counts have both parities); (c) co-design an explicit
   word + bit-field family with periodic structure and prove both dual
   Cohn–Lempel determinants = 1 by transfer-matrix induction — the
   surgery_m8-style 2m-loop dual is the model case, now to be rebuilt
   inside family F.
2. Pillar 1 is proven for all even m ≥ 6 (word-level clauses by
   hand-proof + exhaustive m = 6, 8 verification; Cohn–Lempel used as
   literature but bypassed by direct orbit checks for every m ≤ 40).
   The closed-form/recursion identity for W_m is machine-verified to
   m = 60; a 10-line run-structure induction would close it for all m.
3. Realizability (Lemma R) sufficiency is machine-exhaustive at m = 6, 8
   and constructive (validated schedules) for family F to m = 60; the
   general 3×3 zero-diagonal transportation argument is routine but not
   written out.
4. The abstract-problem results of phases 3–7 stand as mathematics about
   T_{(−2,−4)} ∘ A but make no statement about D_3(m); findings.md
   Results 10–11 record the correction.

## 7. File map (this session)

* `main_theorem.py` — T1 base cases; T2 obstruction + schedulability;
  T3 Pillar 1 under (2,4); T4 family-F schedules; T5 station
  re-verification (reduced + 3D); T6 census-vs-SAT validation.
* `assembler.py` — obstruction checks O1–O3; schedule; assemble;
  m=4 reassembly demo.
* `dense_template2.py` — budget-parametric closure census; P1
  direction-independence; P2 Pillar-1 transfer; P3 validation.
* `budget_scan2.py`, `budget_scan2_m8.log` — the 22-matrix scan.
* `narrow_censusF.py`, `narrow_censusF.jsonl/.log`, `greedyF.py` —
  family-F censuses + assembled stations.
* `narrow_census.py`, `narrow_census(2).jsonl` — abstract-tree census
  m ≤ 24 (kept for the structural record).
* `famF_completion_m{m}.json`, `famF_decomp3d_m{m}.json` — certificates.
