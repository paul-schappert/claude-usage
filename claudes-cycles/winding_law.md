# Winding law for staircase gadgets, budget freedom, and the transversal
# dead end

Session 2, phase 3. Machine-tested by `winding_law.py`, `winding_law2.py`
(plus inline checks logged below); notation and cited lemmas/theorems from
`analytic_criterion.md`. Budgets default to t_0 = (0,1), t_1 = (1,2),
t_2 = (−2,−4) unless stated.

## 1. The (m, k) experiments and the empirical winding law

A (k, k+1)-gadget is a single self-avoiding staircase loop of winding
(k, k+1) (support (2k+1)m), i.e. a cyclic word with mk e0's and m(k+1)
e1's; mirrors (k+1, k) analogous.

### 1.1 Canonical maximally-uniform words FAIL universally

For the canonical Christoffel word of slope k/(k+1) (maximally uniform run
structure) and its mirror, for every even m ∈ [6, 24] and every k ∈ [1, m/2]:
**not a single (m, k, mirror) triple gives B_2 single.** Failures are
`nocover` (a ⟨t_2⟩-coset missed) or `splitN` (return map splits into N
cycles); full table in the `partA_table` output. This is a strong negative
law: *maximal uniformity of the run structure is anti-correlated with
single-cyclicity* — uniform words have (near-)periodic label walks, and
periodicity factors the return map (same mechanism that splits helix12 for
m ≡ 0 mod 4, m ≥ 12). The ground-truth gadget words are conspicuously
irregular (runs (3,4,4,1,5,1) at m=6, (1,1,6,1,7,1,2,5) at m=8).

### 1.2 Where B_2-single (k,k+1)-words exist (random sampling)

Two independent samplers (uniform word shuffles; randomized-DFS
self-avoiding loops), ~300–4000 simple loops per cell:

| winding | m=6 | 8 | 10 | 12 | 14 | 16 | 18 | 20 | 22 | 24 | 28 |
|---------|-----|---|----|----|----|----|----|----|----|----|----|
| k=1 (1,2) | 13% | 3% | 0.5% | ~0.03% | 1/300 | 0 | – | – | – | – | – |
| k=2 (2,3) | n/a | 22% | 13% | 3.5% | 2.7% | 0.7% | 0/300 | 1% | 0/300 | 0/300 | – |
| k=3 (3,4) | n/a | n/a | n/a | 10% | – | 2% | – | 1% | – | 0/300 | – |
| k=4 (4,5) | | | | | | | | 1% | – | 1.3% | 0/300 |

(0/300 = none found, not proof of nonexistence.) The density ridge tracks
**2k+1 ≈ m/2**, i.e. |S(A_2)| ≈ m²/2. Fixed k dies as m grows (k=1 is
extinct-or-nearly by m ≥ 14; k=2 fading by m ≥ 18). The known solutions sit
exactly on the ridge: m=10 solution has A_2 winding (2,3), support
5m = m²/2; m=8 has (1,2)/(3,2) variants, 3m–5m.

### 1.3 Completability of cycles 0, 1 (CP-SAT, original budgets)

For each (m, k), up to 3–30 random B_2-single words tested:

| m | k=1 | k=2 | k=3 |
|---|-----|-----|-----|
| 6 | **YES** (5/30 words) | no single words | – |
| 8 | **YES** (7/30; also 1/2 in A3) | **YES** | no single words |
| 10 | **YES** (1/3) | **YES** (1/1) | no single words |
| 12 | untested (singles too rare) | **YES** (1/3) | 0/3 words completed |

All found completions independently re-verified (Latin, bijective, three
single m²-cycles) and saved as `wlaw_completion_m{m}_k{k}.json`.
**Correction of the previous phase:** the earlier "0/6 completable at
m = 10, k=1" was a sampling artifact; `wlaw_completion_m10_k1.json` is a
verified completion around a (1,2)-gadget.

### 1.4 The law

No *fixed* k works for all m. The data supports a **scaling law**:

    winding (k, k+1) with 2k+1 = nearest odd number to m/2,
    i.e. k(m) ≈ (m − 2)/4;    |S(A_2)| ≈ m²/2.

Consistent with every confirmed cell (m=6: 2k+1=3; m=8: 3 or 5; m=10: 5
(= m/2, the ground truth); m=12: 5) and with the existence-density ridge up
to m = 24. Not a proof; the completability data thins out at m = 12 (SAT
cost) and existence beyond m = 24 is unsampled.

## 2. Budget freedom and the transversal dichotomy (why no budget choice
## rescues a fixed winding)

**Theorem 2.1 (dichotomy).** A winding-(w0, w1) loop can be a perfect
transversal of ⟨t_2⟩ only if s := w0 + w1 divides m and ord(t_2) = m/s
(counting: |S| = ms must equal m²/ord). Hence a *fixed* winding usable for
all even m must have s ∈ {1, 2}:
* s = 1: A_2 is a plain row (or column) circle. Dead for every budget: the
  crossing identity forces (for a row circle at y = y₀, using
  I_0 ⊔ I_1 = S(A_2) and the forced e1-moves of the movers on the row)
  W1_0 = m − |I_0| with |I_0| ∈ {0, m}; either way one of A_0, A_1
  degenerates to the global e1-shift, whose B_c is a translation — never a
  single m²-cycle. (Machine: consistent with the "budget pair (0,0)
  infeasible" scan finding; the same argument is in analytic_criterion
  §3.4-style reasoning.)
* s = 2: the 2m-point (1,1)-loops — settled below.

**Theorem 2.2 (u-measurability lemma; exact).** A bijective field with FULL
support (no idle points) has its move constant on every anti-diagonal
u = x + y; conversely each of the 2^m level-profiles σ: Z_m → {e0, e1}
gives a bijective field. *Proof.* Injectivity fails iff some p has
a(p) = e0 and a(p + e0 − e1) = e1 (both would map onto p + e0). Since
p + e0 − e1 is the successor of p along its anti-diagonal (v ↦ v + 2 with u
fixed), the constraint says the e0-indicator is monotone around each cyclic
anti-diagonal, hence constant on it. Conversely a u-measurable full field is
injective because colliding pre-images lie on the same anti-diagonal. ∎
[M] SAT enumeration at m = 6 finds *exactly* 64 = 2^6 full-support
bijective fields, all u-measurable; 200/200 at m = 8.

**Lemma 2.3 (skew criterion for nowhere-idle cycles).** If A is full-support
(so u-measurable with profile σ) and t = (a, b), then B = T_t ∘ A has
constant level-step g = a + b + 1 and fiber return map F(x) = x + W0 on any
level (W0 = #{u : σ(u) = e0}); B is a single m²-cycle iff gcd(g, m) = 1 and
gcd(W0, m) = 1. (Lemma 1.1 with the section = one level.) ∎

**Theorem 2.4 (universal rigidity of diag11 — all budgets).** For every even
m ≥ 4 and EVERY budget triple (t_0, t_1, t_2) (any translations whatsoever),
the Latin triple (A_0, A_1, diag11) with A_0, A_1 bijective and B_0, B_1, B_2
single m²-cycles does not exist. *Proof.* Steps 1–6 of the rigidity theorem
(analytic_criterion Thm 3.6) are budget-independent: the crossing identity
forces balanced windings for A_0, A_1, whence 2m | |I_0|, |I_1| and
{|I_0|, |I_1|} = {0, 2m}. The cycle with empty idle set is full-support,
hence u-measurable (Thm 2.2); diag11 forces its level profile to alternate
(σ = e1 on even levels — from the D points, e0 on odd levels — from D'), so
W0 = m/2 and gcd(W0, m) = m/2 ≥ 2: by Lemma 2.3 its B is not a single cycle,
for any (a, b). ∎
[M] SAT: diag11 completion INFEASIBLE at m = 6, 8 under the architecture-N
budgets [(0, m−2), (1,1), (m−2, 0)] (chosen precisely to defuse the old
u-parity step — the empty-idle cycle would have had g = m−1, coprime to m),
and under three further random budget triples at m = 6.

**Uniqueness of transversal words is t_2-dependent but always ≈ diag11.**
For t_2 = (m−2, 0) (order m/2, coset labels (x mod 2, y)) the transversal
condition on the word is "no e0-run of length ≥ 2", which with m e0's and
m e1's forces the alternating word: **diag11 is the unique transversal class
for every even m ∈ [4, 14]** [M], and by Theorem 2.4 it is rigid. For
t_2 = (−2, −4) the classification (analytic_criterion §2) gives diag11 plus
three period-6 families only when 3 | m (all SAT-infeasible at m = 6).

**Conclusion (transversal route closed).** No budget triple makes any fixed
winding a perfect transversal for all even m except via 2m-point
(1,1)-loops, and those are diag11-or-nothing (up to the sporadic 3|m
families), and diag11 is universally rigid. The uniform family, if it
exists, is **non-transversal**: its return-map lemma cannot be outsourced to
Theorem 2.1 (perfect transversal) and must be proved parametrically.

## 3. Proof skeleton for a scaling family, and the gap list

Target shape: for each even m, a word W(m) of winding (k(m), k(m)+1),
k(m) ≈ (m−2)/4, plus completions (A_0(m), A_1(m)).

* **Lemma A (coverage, parametric).** Status: METHOD PROVEN, FAMILY MISSING.
  For any word family with run structure given by finitely many arithmetic
  progressions in m, the label walk φ(step) ∈ {(1, 2), (0, −1)} is an
  explicit function, and coverage of all 2m cosets reduces to finitely many
  congruence checks per residue class of m — exactly as done for helix12
  (the (0, m−1) equation, analytic_criterion §4). Gap: no candidate W(m)
  yet; the canonical uniform words fail (§1.1), so W(m) must carry
  controlled irregularity.

* **Lemma B (return map single, parametric).** Status: THE HARD GAP.
  Prop 1.2 reduces B_2-singleness to a permutation of the (2k+1)m support
  points, computable from the word alone; uniformity in m needs algebraic
  structure. Two proven models exist: diag11 (R = loop successor;
  transversal — now known unreachable) and helix12 (R analyzed exactly, but
  single only for m ≤ 8). Most promising provable target: words whose coset
  multiset over the 2m classes is exactly {m singletons, m doubletons}
  (the m=6 ground truth realizes this: profile {1: 6, 2: 6}); then R is
  "label successor + m binary races", and the race outcomes are determined
  by translation distances that a designed word can make constant in m.
  Gap: such a word family with all races resolving consistently has not
  been constructed; the scaling k(m) means the word length grows like m²/2,
  so the family must be described by a rule, not a fixed word.

* **Lemma C (completion of the dense cycles 0, 1).** Status: EMPIRICAL ONLY.
  Everywhere a B_2-single gadget existed with m ≤ 12 and 2k+1 ∈ {3, 5},
  CP-SAT found completions (7 verified artifacts; m=12 k=3 resisted in 3
  tries). Necessary conditions are proven (equidistribution, n_0, n_1 ≥ 1,
  odd loop counts, crossing identities) but no sufficiency argument exists.
  The dense reformulation (analytic_criterion §5: return maps on the idle
  sets; level-parity alternation for cycle 0, +3 mod 4 stepping for cycle 1)
  is the intended proof vehicle. Gap: entire lemma.

* **Verification ≤ 40.** BLOCKED on a family. What IS verified for all even
  m ≤ 40: diag11's B_2 (single, but rigid — now moot); budget-lift sanity of
  architecture N. All completions m ≤ 12 verified by independent orbit
  check.

## 4. Corrections and adversarial notes

* Previous phase's "0/6 completable at m=10" — RETRACTED (sampling
  artifact); (1,2) completes at m = 10.
* Christoffel canonicalization — falsified as a design principle (§1.1).
* Architecture N (budget redesign to evade the u-parity kill) — falsified
  by SAT, then *explained* by the stronger Theorem 2.4; the u-parity step
  of the original rigidity proof was inessential, the real kill is
  u-measurability + gcd(m/2, m) > 1.
* The DFS word enumerator initially pruned the closing label and reported 0
  words; fixed (words_dfs.py) and cross-validated against the independent
  combination enumerator.

## 5. File map (this phase)

* `winding_law.py` — parts A (table), A2 (random stats), A3 (SAT by winding
  class), B1 (dichotomy), B2 (architecture N verification), B3 (SAT).
* `winding_law2.py` — E1 (DFS existence sampling), E2 (m=12 SAT).
* `wlaw_completion_m{8,10,12}_k{1,2}.json` — verified full solutions.
* Inline logged checks: u-measurability enumeration; random-budget diag11
  SAT; (m−2,0)-transversal word uniqueness (m ≤ 14).
