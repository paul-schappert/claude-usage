# Phase 5: the nu-sigma factorization, Cohn-Lempel reduction of Lemma B,
# inheritance verdict, and the chain to m = 20

Machine work in `induction3.py` (N1/N2/N3); all cited completions verified
by independent orbit checks. Budgets: t_0=(0,1), t_1=(1,2), t_2=(−2,−4).

## 1. The return map has NO free parameters: R = ν ∘ σ

**Theorem 1.1 (factorization).** Let A be a bijective gadget field whose
support S meets every ⟨t⟩-coset. Let σ be the loop-successor map of A on S,
and for q ∈ S let ν(q) be the first point of S on the ray q+t, q+2t, …
(equivalently: the cyclic successor of q within S ∩ (q + ⟨t⟩) in t-order;
ν(q) = q iff q is alone in its coset). Then the first-return map of
B = T_t ∘ A on S is exactly

    R = ν ∘ σ.

*Proof.* R(p) is the first S-point on the ray from B(p) = p + a(p) + t
= σ(p) + t, i.e. the first S-point strictly after σ(p) in t-order, which is
ν(σ(p)). ∎

This retro-derives the perfect-transversal theorem (ν = id) and kills the
"race" language of earlier notes: the intra-coset outcome is deterministic
— the ray entering a multi-coset always continues to the *next* support
point cyclically, never back to σ(p) itself.
[M] N1: ν∘σ cycle structure equals the directly computed return-map cycle
structure on random covered gadgets, all 122 balanced m=6 words (via the
count formula below), and the chain gadget words.

## 2. Lemma B for balanced words is GF(2) linear algebra (Cohn-Lempel)

For a balanced word (coset profile {1: m, 2: m}) ν is a product of m
disjoint transpositions = m chords drawn on the σ-cycle (positions of the
two support points sharing a coset). The classical **Cohn-Lempel lemma**
gives

    #cycles(ν ∘ σ) = m − rank_{GF(2)} A(W) + 1,

where A(W) is the m×m interlacement matrix of the chords (A_{cd} = 1 iff
chords c, d interlace on the cycle). Hence:

**Lemma B (balanced form).** A balanced (k,k+1)-word W has B_2 single ⟺
A(W) is nonsingular over GF(2).

[M] N1: verified *exactly* on all 122 balanced m=6 words (77 single ⟺
rank = 6, 45 non-single with the cycle count matching the corank formula
in every case), and on the k=1 chain gadgets at m = 10, 12 (balanced, full
rank). Caveat: the k=2 chain gadgets at m = 14..20 are NOT balanced
(multiplicity-3 cosets ⇒ ν has 3-cycles); the generalized (Traldi-type)
interlacement formula would be needed there — not implemented.

**Insertion Lemma (precise candidate, as requested).** Let W be a balanced
(k,k+1)-word of modulus m with det_{GF(2)} A(W) = 1. Then there exists a
position pair (p, q) such that the double-period insertion
W' = ins_{p,q}(W; P_k) is (i) a simple loop, (ii) balanced at modulus m+2,
and (iii) det_{GF(2)} A(W') = 1.
Status and proof route: the parent chords are pairs of word positions with
equal label ℓ_i = (a_i mod 2, 3a_i − i mod m); the child's labels are the
spliced sequence *reinterpreted mod m+2*, so the chord diagram re-pairs
globally — A(W') is not a bordered A(W), and the first proof obligation is
to describe the re-pairing map. The empirical basis is solid: every parent
tested (dozens across m = 6..18) had good pairs, at ~1–2% of the ≈ L²/2
positions; never zero. A nonemptiness proof might average det_{GF(2)} A(W')
over (p, q) or exhibit one structured pair (e.g. both insertions inside a
long e1-run, where the local label pattern is arithmetic).

## 3. Completion inheritance: verdict GLOBAL

Protocol (N2): along a k=1 chain from the first verified (6,1) word, solve
each child's completion minimizing Hamming deviation from the parent's
dense fields under the coordinate embedding [0,m)² ⊂ [0,m+2)², parent
assignments as CP-SAT hints, deviation as the objective.

* Step 6→8: OPTIMAL deviation = **33 of 72 embedded cells (46%)** — the
  *closest possible* child completion is a global rewrite, not a local
  patch; deviations are spread across the torus, not concentrated at
  splice sites.
* The hinted chain also stalls at 10 for that particular parent (3 single
  children, none completable) — consistent with the phase-4 finding that
  completability recurs across wide frontiers rather than along every edge.

**Conclusion: the pointwise dense fields are the wrong inductive object.**
Even coarse invariants are not transported: the idle profiles (n_0, n_1,
n_2) along the verified chain read (1,2,5)@8 → … → (3,2,13)@18 →
(2,3,15)@20 (only the equidistribution law |I_c ∩ level| = n_c is
universal, as proved earlier).

**Proposed inductive invariant for the dense cycles:** the *level data* —
the partition profile (n_0, n_1, n_2), the idle-position sequences per
level, and the induced level-return maps (for B_0 a parity-alternating
m-cycle, for B_1 a +3 mod 4 stepping m-cycle; analytic_criterion §5). The
induction should re-*design* these from a parametric template at each m
(the same way the gadget word is designed), not transport a SAT artifact.
Equivalently: the inductive object is the triple of return-map itineraries,
with Theorem 1.1 as the computational bridge for cycle 2 and the idle-
section maps as the bridge for cycles 0, 1.

## 4. Chain extension (N3)

k=2 chain, frontier width 8, full SAT + orbit verification at each station:

    (12,2) → (14,2) → (16,2) → (18,2) → (20,2)      [all verified]

(at m=18 the first candidate was INFEASIBLE, the second OPTIMAL; at m=20
the first candidate completed). Artifacts `chain_completion_m18_k2.json`,
`chain_completion_m20_k2.json`. Combined with the k=1 chain (6→8→10→12→14):
**verified full solutions of the reduced gadget problem now exist at every
even m ∈ [6, 20], all generated by iterated double-period insertion from
the exhaustively-mapped m=6 base.**

## 5. Remaining proof obligations (sharpened)

1. **Chord re-pairing map**: describe how the balanced chord diagram of W
   maps to that of ins_{p,q}(W) mod m+2; then prove the Insertion Lemma
   (nonemptiness of good pairs) — now a GF(2) determinant statement.
2. **Balanced k=2 family**: the current k=2 chain words are unbalanced;
   either re-run the chain restricted to balanced children (search
   constraint: profile {2: m, 3: ...}-free — i.e. multiplicities ≤ 2), or
   implement generalized interlacement for ν with 3-cycles.
3. **Dense-cycle template**: construct the parametric level-data template
   (idle positions + bit field) realizing single level-return maps for
   B_0, B_1 compatibly with a given gadget word — replaces per-m SAT.
4. Chain continuation m ≥ 22 is bounded only by SAT cost; no obstruction
   observed at any station so far.

## 6. File map

* `induction3.py` — N1 (factorization + Cohn-Lempel), N2 (inheritance
  experiment), N3 (chain extension driver).
* `inherit_completion_m8.json` — the minimum-deviation child completion.
* `chain_completion_m18_k2.json`, `chain_completion_m20_k2.json` — new
  verified stations.
