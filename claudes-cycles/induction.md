# Induction in m: the double-period insertion move

Session 2, phase 4. Machine work in `induction.py`, `induction2.py`; all
completions cited below were re-verified by independent orbit checks
(Latin + bijective + three single m²-cycles) before being saved.
Budgets throughout: t_0 = (0,1), t_1 = (1,2), t_2 = (−2,−4).

## 1. Exhaustive base-case landscape (m = 6, winding (1,2))

All C(18,6) letter placements, deduplicated by rotation [M I1]:

* 578 simple-loop rotation classes;
* **77 are B_2-single, and every one of them has coset profile exactly
  {1: 6, 2: 6}** (m singletons, m doubletons). So at m = 6, balanced
  profile is *necessary* for B_2-singleness — strong support for the
  Lemma-B target of winding_law.md §3. (Caveat: not necessary in general —
  helix12 at m = 8 is single with profile {1:10, 2:4, 3:2}.)
* exactly **7 completable words** (CP-SAT on all 77; complete list in
  `m6_completable_words.json`):
  112112221222221222, 112122122221222212, 112122221222212212,
  112122221222221122, 112122222122211222, 112211222221222212,
  112221122212222212.

## 2. The extension rule

**Rule R_k (double-period insertion).** Given a (k, k+1)-word W of length
(2k+1)m, insert the slope period P_k = e0^k e1^{k+1} at two (arbitrary,
possibly equal) positions. The result has winding (k, k+1) over m+2 —
exactly the letter counts needed for the next even modulus.

Search protocol: from a parent word, generate all ≈ ((2k+1)m)² /2
double-insertions, keep those that walk to simple loops with B_2 single at
m+2 (cheap orbit checks), then CP-SAT a sample for completability of
cycles 0, 1.

### Verified transitions (every completion orbit-checked)

| transition | single children | completable (tested) | artifact |
|------------|-----------------|----------------------|----------|
| (6,1) → (8,1), all 7 parents | 2–17 per parent | 7 / 20 | `insertion_pairs_6_8.json` |
| (8,1) → (10,1) | 16 | 2 / 10 | `chain_completion_m10.json` |
| (10,1) → (12,1), narrow frontier | 5 | 0 / 5 | — |
| (10,1) → (12,1), widened frontier (all 16 (10,1) singles) | 38 | **1 / 1** | `chain_completion_m12_k1.json` |
| (12,1) → (14,1) | 10 | **1 / 2** | (word logged; completion re-derivable) |
| (12,2) → (14,2) | 10 | **1 / 1** | `chain_completion_m14_k2.json` |
| (14,2) → (16,2) | 29 | **1 / 1** | `chain_completion_m16_k2.json` |

Base words for the k=2 chain: the verified (12,2) gadget of
`wlaw_completion_m12_k2.json`.

### Key corrections to the winding-law picture

* **The ridge law is a density law, not an existence law.** Random sampling
  suggested (1,2)-words die by m ≥ 14; the insertion chain produces
  B_2-single (1,2)-words at m = 12 (5), m = 14 (10) easily, and **m = 14,
  k = 1 is completable** — far off the 2k+1 ≈ m/2 ridge. Structured
  insertion beats random sampling by orders of magnitude.
* **Completability is not inherited branch-wise but recurs densely.** The
  completable (14,1) word descends from *non-completable* (12,1) words.
  So the invariant robustly preserved by R_k is B_2-singleness-of-some-
  children; completability re-emerges along the tree rather than flowing
  through every edge. The (12,1) cell, initially 0/5 from a 2-parent
  frontier, resolved to COMPLETABLE on the first candidate once the
  frontier was widened to all 16 (10,1) singles — the chain is unbroken:
  **(6,1) → (8,1) → (10,1) → (12,1) → (14,1)**, every station a verified
  full solution reachable by iterated R_1.

### Return-map behaviour of the insertion [M I4]

Multiplicity itinerary of the first-return cycle (sequence of coset
multiplicities visited), for a rule-related completable pair:

    m=6 parent: 121121 222222212212
    m=8 child:  121121 212222211222222212

Shared prefix, inserted motif in the middle — the insertion acts as a
localized splice in the return cycle. This is the concrete handle for the
insertion lemma (below), but no conjugacy proof yet.

## 3. The k-jump obstruction

Deterministic winding jumps (1,2) → (2,3) at fixed m — insert (e1,e0) or
(e0,e1) after/before every e0 (rules J1, J2, J3) — **fail universally: the
walk self-intersects in every one of 30 tests** (7 words at m=6, plus
verified gadgets at m=8, 10) [M induction2.jump]. A local-per-strand jump
rule, if one exists, needs position-adaptive insertions. However, the chain
data (k=1 alive at m=14, k=2 at m=16) suggests k-jumps may be unnecessary:
fixed-k chains persist far beyond the density ridge.

## 4. Status of the induction programme

What the machine now certifies: a single uniform move (R_k) connects
verified full solutions at

    (6,1) → (8,1) → (10,1) → (12,1) → (14,1)   and
    (12,2) → (14,2) → (16,2),

with every station's solution orbit-verified. What is missing for a proof:

* **Obligation 1 (Insertion Lemma / Lemma B).** Characterize the insertion
  position pairs that preserve B_2-singleness and prove at least one exists
  for every parent (empirical rate ≈ 1–2% of position pairs, never zero in
  any tested parent). Attack: the label walk of the child equals the label
  walk of the parent with two spliced P_k-segments *and* all labels
  reinterpreted mod m+2; the I4 itinerary locality suggests the return
  cycle is the parent's with a bounded splice when the two insertion points
  lie in "compatible" cosets. This is now a finite, sharply-posed
  combinatorial question.
* **Obligation 2 (Completion inheritance / Lemma C).** The dense fields at
  consecutive stations come from independent SAT runs and show no forced
  relation. Targeted experiment (not yet run): re-solve at m+2 with the
  parent completion as CP-SAT hints and minimized Hamming distance to a
  canonical lift, to reveal whether *local* completion-extensions exist.
  If they do, the induction closes with a second insertion lemma for the
  partition (I_0, I_1, I_2).
* **Obligation 3 (base/edge bookkeeping).** RESOLVED for m ≤ 16: verified
  full decompositions of the reduced problem now exist at every even
  m ∈ [6, 16], each reachable from the m = 6 base by iterated R-moves
  (k=1 chain to 14; k=2 chain to 16).
* **Obligation 4.** Extend the verified chain beyond m = 16 (SAT cost grows;
  m = 18 k=2 is the next station; nothing suggests an obstruction).

## 5. File map (this phase)

* `induction.py` — I1 exhaustive m=6 landscape + SAT; I2 insertion scan
  6→8; I3 chain driver; I4 return-map itinerary diff.
* `induction2.py` — k=2 chain (12→14), deterministic k-jump tests,
  m=14 k=1 edge SAT; inline: 14→16 extension, widened m=12 probe.
* `m6_completable_words.json` — all 7 completable (6,1) words.
* `insertion_pairs_6_8.json` — verified completable parent→child pairs.
* `chain_completion_m10.json`, `chain_completion_m14_k2.json`,
  `chain_completion_m16_k2.json` (+ `chain_completion_m12_k1.json` if the
  probe succeeds) — verified full solutions along the chains.
