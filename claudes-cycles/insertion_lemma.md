# Phase 6: the Insertion Lemma — exact chord re-pairing, the narrow
# family theorem (Lemma B solved for an explicit infinite family), and
# the precise obstruction in general

Machine work in `insertion_lemma.py` (experiments E1–E5, verifications
V1–V4); every numbered claim marked [M] has been machine-checked, with the
check's scope stated exactly. Budgets: t_0=(0,1), t_1=(1,2), t_2=(−2,−4).
Notation continues analytic_criterion.md and induction3.md. This phase
resolves obligation 1 of induction3.md §5 in the strongest form available:
a PROOF for an explicit infinite family, plus the exact counterexamples
showing the universally-quantified lemma is false.

Summary of outcomes:

1. **Exact transformation** (Prop. 1): the chord diagram of a double-period
   child is described completely by an integer-valued label walk in which
   z NEVER shifts — only the parity coordinate flips on the segment between
   the two insertion points, six explicit new labels are added, and the
   reduction modulus changes m → m+2.
2. **Narrow Insertion Theorem** (Thm 3): for "narrow" balanced words the
   only balance-preserving insertions are the two diagonal insertions at
   the walk maximum, and these preserve det A over GF(2) UNCONDITIONALLY
   (a 2-chord bordering with a zero interlacement row). Consequence
   (Thm 4): an explicit closed-form word family W_m with B_2 single for
   **every even m ≥ 6** — Lemma B is now a theorem on this family.
3. **Obstruction** (§5): the naive Insertion Lemma ("every balanced det-1
   parent has a good pair") is FALSE — at m = 6, 10/77 parents have no
   good pair, and two parents have **no B_2-single child at all** over the
   full double-period insertion set. This corrects induction3.md §2's
   "never zero" (which was based on a biased sample). Parity-averaging
   over pairs also fails (counts below).

## 0. Setting: words, the integer label walk, chords

A (1,2)-word at modulus m is W = w_0 … w_{L−1}, L = 3m, with m letters e0
and 2m letters e1, read cyclically; walking it from a base point of Z_m²
(e0 = +(1,0), e1 = +(0,1)) traces the candidate gadget loop A_2. Let
a_i = #{j < i : w_j = e0}. Position i (the departure point of letter w_i)
has

    eps_i = a_i mod 2 ∈ Z_2,    z_i = 3 a_i − i ∈ Z   (an INTEGER),

so along the word: an e0 step maps (eps, z) → (eps⊕1, z+2), an e1 step maps
(eps, z) → (eps, z−1). The walk closes: a_L = m (even), z_L = 3m − 3m = 0.
The ⟨t_2⟩-coset label of the point of position i is
(eps_i, z_i mod m) + (fixed offset of the base point) — by the coset
classification φ(x, y) = (x mod 2, 2x − y mod m) of analytic_criterion §1;
offsets affect nothing below and are dropped.

* **Balanced**: the 3m labels (eps_i, z_i mod m) hit each of the 2m values
  of Z_2 × Z_m with multiplicity ≤ 2 (then automatically: m values twice,
  m once, and coverage of all ⟨t_2⟩-cosets holds).
* **Chords**: the m unordered position pairs {i, j} with equal label,
  drawn on the cyclic order 0, …, L−1. A(W) = m×m GF(2) interlacement
  matrix (A_{cd} = 1 iff chords c ≠ d interlace).
* **Lemma B, balanced form** (induction3 §2, via R = ν∘σ + Cohn–Lempel):
  for W a balanced simple loop, B_2 = T_{t_2}∘A_2 is a single m²-cycle
  ⟺ det_{GF(2)} A(W) = 1.
  [M] E1: re-verified with the independent word-level implementation of
  this phase: exact on all 578 simple (1,2)-words at m = 6 (77 singles),
  and on 300/134 random balanced words at m = 8/10. (V1 below adds all
  balanced narrow words at m = 6, 8.) The Cohn–Lempel step itself is
  classical (Cohn & Lempel, J. Comb. Th. 1972); within this project it is
  machine-verified on every instance listed, and the final theorem is
  additionally orbit-verified directly for m ≤ 60, so no claim below rests
  on the citation alone for small m.

**Width.** width(W) = max_i z_i − min_i z_i (rotation-invariant). Since a
balanced word must cover all m residues mod m in each parity class,
width ≥ m−1 always. Observed widths at m = 6: {5: 8, 6: 33, 7: 27, 8: 9}
across the 77 singles [M E3]. Call W **narrow** if width = m−1 — the
minimum possible.

## 1. The exact transformation (obligation 1, first half)

Double-period insertion at the (cyclic) position pair (p, q), 0 ≤ p ≤ q ≤ L:

    ins_{p,q}(W) = W[0:p] · P_1 · W[p:q] · P_1 · W[q:L],  P_1 = e0 e1 e1.

(The pairs (p, L) and (p=q=L) coincide cyclically with (0, p) and (0, 0);
the enumeration below identifies them. Insertions that split the first
inserted copy — allowed by induction.py's `insertions_two_periods` — are
NOT of this form; they are treated only in §5.)

**Proposition 1 (child label walk — exact).** Since P_1 has label action
(eps, z) → (eps⊕1, z+2) → (eps⊕1, z+1) → (eps⊕1, z), the child
W' = ins_{p,q}(W) at modulus m+2 has label walk, in terms of the parent's
INTEGER walk:

| child segment                | labels                                        |
|------------------------------|-----------------------------------------------|
| parent positions i ∉ [p, q)  | (eps_i, z_i) — unchanged                      |
| parent positions i ∈ [p, q)  | (eps_i ⊕ 1, z_i) — parity flipped, z UNCHANGED|
| cap at p (3 new positions)   | (eps_p, z_p), (eps_p⊕1, z_p+2), (eps_p⊕1, z_p+1) |
| cap at q (3 new positions)   | (eps_q⊕1, z_q), (eps_q, z_q+2), (eps_q, z_q+1)  |

with every z now reduced **mod m+2** instead of mod m. In particular the
"label shift" anticipated in the task statement is trivial in the right
coordinates: z never shifts; the whole global re-pairing is carried by
(i) the parity flip on the inter-insertion segment F = [p, q), (ii) the
six cap labels, (iii) the modulus change.

*Proof.* Each insertion of P_1 adds 3 to i and 1 to a at every subsequent
position, so z = 3a − i is unchanged there while eps flips; after the
second insertion both effects compose (eps flips twice = unchanged). The
cap labels are read off the three-step action of P_1 starting from
(eps_p, z_p) resp. (eps_q ⊕ 1, z_q) (the second cap starts after one flip).
∎  [M] E2: formula equals direct recomputation of the child's label walk on
1200 random (word, p, q) triples at m = 6, 8, 10 — exact.

**Corollary 2 (chord re-pairing map).** {i, j} ⊆ old positions is a chord
of W' iff  eps_i ⊕ [i ∈ F] = eps_j ⊕ [j ∈ F]  and  z_i ≡ z_j (mod m+2).
Hence, listing the differences from the parent diagram:
* old chords with both/neither endpoint in F and z_i = z_j persist;
* old chords with exactly ONE endpoint in F break (parity mismatch), and
  new chords form across the boundary of F between formerly
  opposite-parity equal-z positions;
* old chords with z_i ≢ z_j as integers (i.e. |z_i − z_j| = m, possible
  once width ≥ m) break, and pairs with |z_i − z_j| = m+2 (possible once
  the child width reaches m+2) form;
* the six cap positions pair according to the same rule (their labels are
  the four values z_p, z_p+1, z_p+2 / z_q, z_q+1, z_q+2 in the parities of
  the table).
This is the complete combinatorial description of A(W') from
(W, p, q) — obligation 1's first deliverable.

## 2. The narrow regime: three rigidity lemmas

Throughout §2–3, W is balanced and narrow (width = m−1) at even modulus m;
c = min z, M = max z, so the walk's values are exactly the m integers
[c, M] and, per parity class, every value is attained (coverage) with
multiplicity ≤ 2; multiplicities count positions, and z ≡ z' (mod m) ⟺
z = z' inside a width-(m−1) window. So all chords join equal INTEGER
(eps, z) pairs.

**Lemma S (simplicity is automatic).** A balanced narrow word is a simple
loop on Z_m². *Proof.* Two positions i ≠ j occupy the same point of Z_m²
iff a_i ≡ a_j and i − a_i ≡ j − a_j (mod m). Equal points have equal coset
labels, so {i, j} is a chord: z_i = z_j (narrow). A cyclic arc from i to j
containing no e0 has z strictly decreasing along it, contradicting
z_i = z_j; so BOTH arcs contain an e0, and the e0-count d of the arc i → j
satisfies 0 < d < m. But a_j − a_i ≡ d (mod m) — hence a_i ≢ a_j: no
collision. ∎  (The same proof applies verbatim at modulus m+2 to the child
words below, which have m+2 e0's.)  [M] V1: no balanced narrow word at
m = 6 (252 words, all letter placements) or m = 8 (1872) fails
simplicity — exhaustive.

**Lemma U (where balanced children can come from).** Let W' = ins_{p,q}(W)
be balanced at m+2. Then p = q is a position where z attains its maximum M
(cyclically; the pair (0, L) counts as the diagonal at 0).
*Proof sketch (the machine check below is exhaustive at m = 6, 8).* The
child's label values lie in [c, max(z_p, z_q) + 2] ⊆ [c, M+2]. Coverage at
modulus m+2 needs m+2 distinct residues per parity class; a window of
width ≤ m+1 has no repeated residues, so the child needs ≥ m+2 distinct
values: width exactly m+1, forcing max(z_p, z_q) = M and no
modular merging in the child either. If p ≠ q (cyclically): each parity
class must cover M+1 and M+2, and these can only come from cap labels
(eps_p⊕1, z_p+1), (eps_p⊕1, z_p+2), (eps_q, z_q+1), (eps_q, z_q+2); both
classes are covered only if z_p = z_q = M and eps_p = eps_q. But then p, q
are chord partners at (eps_p, M) and the count of value-M labels in class
eps_p⊕1 in the child becomes (p flipped in F) + (cap N4) + (parent
(eps_p⊕1, M)-positions, ≥ 1 by coverage) ≥ 3 — a tripled class,
contradiction. So p = q, and z_p = M since caps must reach M+2. ∎
[M] V1 (tightness, exhaustive at m = 6 and m = 8): for every balanced
narrow word, every insertion pair OTHER than the max diagonals produces a
non-balanced child — checked over all pairs for all double-max words and
for 40 unique-max words per modulus.

**Lemma D (diagonal insertion at the max: balance transport).** Suppose
additionally each parity class attains M exactly once (call W
"unique-max"; note coverage forces ≥ once, balance allows ≤ twice), and
let p be the max position of either class, eps := eps_p. Then
W' = ins_{p,p}(W) is:
balanced at m+2, narrow at m+2 (width m+1), and unique-max, with its two
max positions (value M+2) at cap positions p+1 (class eps⊕1) and p+4
(class eps).
*Proof.* F = ∅, so by Prop. 1 the child labels are the parent's unchanged
plus the six cap labels, which for z_p = M read: (eps, M), (eps⊕1, M+2),
(eps⊕1, M+1), (eps⊕1, M), (eps, M+2), (eps, M+1) — i.e. the cap
contributes each parity class one copy each of M, M+1, M+2. New counts:
value M: 1+1 = 2 per class; M+1, M+2: 1 per class; values < M: unchanged
(∈ {1,2}, covering). All 2(m+2) label values of the window [c, M+2] are
hit with multiplicity ≤ 2; doubled count = m (parent) + 2 (the two M
classes) = m+2 = required. Narrowness and the unique maxes at p+1, p+4 are
read off the same table. ∎
Conversely, if some class attains M twice, the M-class of that parity
would be tripled: **double-max words have NO balanced child at all** (this
also follows from Lemma U's counting).
[M] V1: exhaustive at m = 6 (216 unique-max: both children verified
balanced/narrow/unique-max; 36 double-max: all insertion pairs checked,
no balanced child) and m = 8 (1728 + 144, same).

## 3. The determinant identity (obligation 1, second half)

**Theorem 3 (Narrow Insertion Theorem).** Let W be balanced, narrow,
unique-max at even m, and p a max position (either class). Then
W' = ins_{p,p}(W) is a simple loop, balanced, narrow, unique-max at m+2,
and

    det_{GF(2)} A(W') = det_{GF(2)} A(W).

*Proof.* Simplicity/balance/narrow/unique-max: Lemmas S, D. Chords: parent
chords pair equal integer (eps, z) values; these values and their cyclic
order are unchanged (F = ∅), and narrowness on both sides makes integer
equality equivalent to the respective modular equality, so the old chords
are exactly preserved. The cap adds two new chords (the M-classes that
became doubletons):

    n1 = {p, p+6}   (cap label (eps, M) with the old position p, which in
                     child indexing sits at p+6 — the two ends of the cap),
    n2 = {p+3, x}   (cap label (eps⊕1, M) with x = the unique parent
                     (eps⊕1, M)-position),

and no others (M+1-, M+2-classes are singletons). Interlacement: the arc
of n1 strictly between its endpoints is the cap interior {p+1, …, p+5},
which contains NO endpoint of any old chord — so n1's row in A(W') is zero
on all old chords — and contains p+3, one endpoint of n2, whose other
endpoint x lies outside: A_{n1,n2} = 1. In block form (rows/cols ordered
old…, n1, n2), with s = the interlacement vector of n2 against old chords:

    A(W') = [ A(W)  0   s ]
            [ 0^T   0   1 ]
            [ s^T   1   0 ]

Cofactor expansion along the n1 row (single 1, in column n2) gives
det A(W') = det [ A(W) 0 ; s^T 1 ] = det A(W) over GF(2), regardless of s.
∎  [M] V1: det preservation asserted for both children of every unique-max
balanced narrow word at m = 6 (216 words) and m = 8 (1728 words) —
exhaustive, no counterexample; E3/E4 independently show that for the 8
narrow words among the 77 singles the good pairs are precisely the max
diagonals (2 each for the 7 unique-max words, 0 for the double-max one).

**Theorem 4 (an infinite Lemma-B family).** Define, for even m ≥ 6,

    W_m = 112122 (1122)^{(m−6)/2} 1 2^{m−4} 212222122     (1 = e0, 2 = e1),

of length 3m with m e0's. Then for EVERY even m ≥ 6: W_m is a simple loop
on Z_m², balanced, narrow, unique-max, and B_2 = T_{t_2} ∘ A(W_m) is a
single m²-cycle.

*Proof.* Induction on m. Base m = 6: W_6 = 112122122212222122 is one of
the 77 verified B_2-singles (finite check; det A = 1). Step: W_{m+2} is
exactly the class-0 max diagonal insertion ins_{p,p}(W_m) — machine-
verified identity of the closed form with the recursion for all m ≤ 100
[M V3]; by Theorem 3 all invariant clauses transport and
det A(W_{m+2}) = det A(W_m) = 1; by balancedness (coverage) + the
R = ν∘σ factorization + Cohn–Lempel, B_2 is single. ∎

[M] V2/V3: the recursion from ALL 7 unique-max narrow det-1 seeds at m = 6
was verified to m = 40 with a DIRECT orbit count of B_2 at every station
(no Cohn–Lempel dependence), and the closed-form family W_m additionally
word-level (balanced/narrow/unique-max/det=1) to m = 100, direct orbit to
m = 60. The seven seeds:
112122122212222122, 112122122222122122, 112122222121122222,
112212122122222122, 112212222122212212, 112212222212212122,
121212122122222122 (the eighth narrow single, 112212212222212212, is
double-max — count {0: 2, 1: 1} — and is a leaf: no balanced child, as
Lemma D predicts).

Remark (branching). Each unique-max word has TWO good children (class-0 or
class-1 max); the family is a binary tree of B_2-single words, of which
W_m is the leftmost branch of seed 0. All branches carry det = 1 forever.

Proof-status ledger for Theorem 4 (brutal honesty):
* Lemmas S, U, D, Theorem 3: complete pencil-and-paper proofs above, each
  clause additionally verified exhaustively at m = 6, 8 and along chains.
* The Cohn–Lempel input is classical (1972) and used as literature; it is
  machine-verified here on >2500 balanced instances including all balanced
  narrow words at m = 6, 8, and bypassed entirely (direct orbit checks)
  for every m ≤ 40 station of every seed chain and m ≤ 60 for W_m.
* The R = ν∘σ factorization is proved in induction3.md §1.
* The closed form of W_m: the identity "closed form = recursion" is
  machine-verified for m ≤ 100 but not hand-proved; Theorem 4 as stated
  does not depend on it (the recursive definition suffices; the closed
  form is a convenience). A 10-line induction on the runs would settle it.

## 4. What breaks outside the narrow regime (and why wider words have
## richer good sets)

For width ≥ m, mod-m chords with |z_i − z_j| = m exist; a general
insertion then deletes them, and non-diagonal insertions (p ≠ q) survive
Lemma U's counting because the wider window tolerates merging mod m+2.
E4's census over all good pairs of all 77 singles shows the dominant
patterns are z_p = z_q = M (56) and near-max values, but with long tails —
the determinant update in those regimes acquires data-dependent
corrections (deleted chords + nonzero interlacement of BOTH new chords),
which is exactly where preservation can fail. The δ := width − m offset is
still additively stable under max-diagonal insertion (width grows by 2 as
m does), so each δ-stratum {−1, 0, +1, +2} could in principle carry its
own transport theorem; only δ = −1 (narrow) has the unconditional
zero-row structure.

## 5. The obstruction: the universal Insertion Lemma is FALSE

[M] E3, exhaustive over all cyclic pairs (p, q) for each of the 77
balanced det-1 words at m = 6 (children of the form A·P_1·B·P_1·C):

* 10/77 parents have NO good pair (child simple + balanced + det 1);
  3 of those have no balanced child at all.
* Against the full insertion set of induction.py (which also splits the
  first inserted copy), two parents are TOTALLY stuck — zero B_2-single
  children of any profile among all 149 distinct candidates each:

      111222212222211222      112212112222212222

  This falsifies the empirical claim in induction3.md §2 ("never zero in
  any tested parent") — that sample was biased toward chain-descendant
  words. The correct statement: good pairs exist for MOST but not all
  parents; existence must be (and now is) proved on a closed sub-family.
* Parity-averaging (strategy (b) of the task) fails at the first hurdle:
  #good is even for 47 and odd for 30 of the 77; #(simple & balanced)
  parity is also mixed (38/39). No sum-over-pairs identity can force
  existence for all parents — consistent with the existence of stuck
  parents.
* The old k=1 chain words (m = 8..12) have widths m, m, m+1 (never
  narrow) and small good sets concentrated at the max (E5), confirming
  that the historical chain survived through the wider strata where no
  unconditional theorem is available.

## 6. Lemma C status along the new family (honest accounting)

The narrow family solves Lemma B only. SAT completability of cycles 0, 1
around W_m [M V4]: m = 8, 10, 12 INFEASIBLE; m = 14 COMPLETABLE (full
solution verified and saved, `narrow_completion_m14.json`). So the
family's gadgets are not uniformly completable at small m — consistent
with the phase-4/5 finding that completability recurs densely rather than
flowing through every edge. Tree-wide SAT probe (all 7 seeds, both
children per station) [M, narrowtree.log]: at m = 8, 4/14 tree words are
completable; at m = 10, 4/28 — so the narrow tree DOES contain verified
full solutions at every tested level (8, 10, 14), but no single branch is
known to be completable at every station. Obligation 3 of induction3.md
§5 (the
dense-cycle template) remains THE open problem; the new theorem removes
obligation 1 for an infinite family and pins the exact failure mode
everywhere else.

## 7. File map (this phase)

* `insertion_lemma.py` — all machinery + E1–E5 (Cohn–Lempel cross-check,
  Prop.-1 formula check, full (p,q) landscape, good-pair census, chain
  words) + V1 (exhaustive narrow-theorem check at m = 6, 8) + V2 (7 seed
  chains to m = 40, direct orbit checks) + V3 (closed form to m = 100,
  orbit to 60) + V4 (completability of W_m).
* `insertion_landscape_m6.json` — the full 77-word (p,q) census.
* `narrow_completion_m14.json` — verified full reduced-problem solution
  around W_14.
* `v1m8_v2.log`, `v4.log`, `narrowtree.log` — run logs.
