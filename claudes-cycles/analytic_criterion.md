# Analytic single-cycle machinery for the reduced gadget problem

Session 2 notes. Every numbered claim below marked [M] has been machine-tested
by `criterion.py` / `criterion2.py` / `words_dfs.py` in this directory
(tests T0–T7, W1–W5); tests abort on any failure and all pass.

## 0. Setting and conventions

Points p = (x, y) ∈ Z_m², m even. Moves id = (0,0), e0 = (1,0), e1 = (0,1).
A *field* A is a map p ↦ p + a(p) with a(p) ∈ {0, e0, e1}; its *support*
S(A) = {p : a(p) ≠ 0}; its *idle set* is the complement. The reduced problem
(findings.md, Result 5): find Latin fields A_0, A_1, A_2 (at each p the three
values a_c(p) are {0, e0, e1}), each bijective, with

    B_c = T_{t_c} ∘ A_c  a single m²-cycle,   t_0 = (0,1), t_1 = (1,2),
                                              t_2 = (−2,−4)  (mod m).

Write u = x + y (anti-diagonal level), v = x − y, z = 2x − y.

**Fact 0.1 (loops).** A is a bijection iff S(A) is closed under the successor
map σ(p) = p + a(p) and σ is injective on S(A); equivalently S(A) decomposes
into vertex-disjoint closed monotone staircase loops. *Proof.* If σ(p) = q ∉
S(A) then A(p) = q = A(q), p ≠ q, not injective. If S(A) is σ-closed and
σ|_S injective, then A permutes S(A) ⊔ (idle set) bijectively. ∎
A loop with winding vector (w0, w1) (w0, w1 ≥ 0, not both 0) has length
m(w0 + w1); a monotone loop cannot be null-homotopic. Write
(W0_c, W1_c) = (|{a_c = e0}|, |{a_c = e1}|)/m for the total winding of A_c
(integrality is forced: each loop contributes (w0, w1)).

**Fact 0.2 (sign; refines findings Result 6).** For even m and each of the
three budgets, sgn(T_{t_c}) = +1 (t_0, t_1: m cycles of odd length m−… of
length m each, sgn = ((−1)^{m−1})^m = +1; t_2: 2m cycles of length m/2,
sgn = ((−1)^{m/2−1})^{2m} = +1). A single m²-cycle is odd (m² even). Every
staircase loop has even length m(w0+w1), hence is an odd permutation. So each
B_c single forces **#loops(A_c) odd**.

---

## 1. The first-return criterion (Task 1)

**Lemma 1.1 (induced permutation).** Let B be a permutation of a finite set V
and ∅ ≠ Σ ⊆ V. If every cycle of B meets Σ, then the first-return time
r(p) = min{k ≥ 1 : B^k(p) ∈ Σ} is finite for p ∈ Σ, R = (p ↦ B^{r(p)}(p)) is
a permutation of Σ, and C ↦ C ∩ Σ is a bijection from cycles of B onto cycles
of R. Consequently, for any nonempty Σ:

    B is a single |V|-cycle  ⟺  every B-cycle meets Σ and R is a single
                                 |Σ|-cycle.

*Proof.* r(p) is finite because the B-cycle through p meets Σ and is
periodic. R is injective: if B^{r(p)}(p) = B^{r(q)}(q) with r(p) ≥ r(q) then
B^{r(p)−r(q)}(p) = q ∈ Σ, so r(p) = r(q) (minimality... precisely: if
r(p) > r(q) then B^{r(p)-r(q)}(p) = q ∈ Σ with 1 ≤ r(p)−r(q) < r(p),
contradicting minimality of r(p)), hence p = q. On the B-cycle C, R acts as
the successor map of the cyclically ordered set C ∩ Σ, a single |C ∩ Σ|-cycle;
distinct B-cycles give disjoint R-cycles, and every R-cycle arises this way.
The equivalence follows by counting cycles on both sides. ∎

**Proposition 1.2 (coset criterion).** Let B = T_t ∘ A with A a bijective
field, S = S(A) ≠ ∅. Then

    B is a single m²-cycle  ⟺
      (a) S meets every coset of ⟨t⟩ in Z_m², and
      (b) the first-return map R on the section Σ = S is a single |S|-cycle,

where R is explicitly computable from the loop data:
R(p) = p + a(p) + (1 + k(p))·t, with
k(p) = min{k ≥ 0 : p + a(p) + (1+k)·t ∈ S} (finite when (a) holds).

*Proof.* Off S, B is the translation T_t. A B-cycle disjoint from S is
therefore a ⟨t⟩-orbit, i.e. a full coset disjoint from S; conversely if a
coset C is disjoint from S, then B(C) = C + t = C, so C is a union of
B-cycles avoiding S. Hence "every B-cycle meets S" ⟺ (a). Apply Lemma 1.1
with Σ = S; between returns the dynamics is +t, giving the stated formula. ∎

[M] Test T1: 342 (field, translation) pairs — ground-truth fields with all
three (including mismatched) budgets, diag11/helix12 for m = 4..16 with six
translations each, and random unions of random-word staircase loops at
m ∈ {6, 8, 10, 12} with random translations. The criterion agreed with the
direct orbit count in every case, in both directions.

**Quotient coordinates for the three budgets** (even m):
- ⟨t_0⟩: order m; cosets ↔ x ∈ Z_m (columns).
- ⟨t_1⟩: order m; cosets ↔ z = 2x − y ∈ Z_m (z(t_1) = 0; the kernel of z is
  exactly ⟨(1,2)⟩).
- ⟨t_2⟩: order m/2 (ord(−2) = m/2 in Z_m, ord(−4) | m/2, lcm = m/2); there
  are exactly **2m cosets**, classified by φ(x,y) = (x mod 2, 2x − y mod m):
  φ(t_2) = (0, 0), φ is onto Z_2 × Z_m, and |ker φ| = m/2 = |⟨t_2⟩| forces
  ker φ = ⟨t_2⟩. [M] (T2)

---

## 2. Perfect transversals: why diag11 works for every even m (Task 2)

**Theorem 2.1 (perfect-transversal theorem).** Let B = T_t ∘ A and suppose
S(A) is a *perfect transversal* of the cosets of ⟨t⟩ (exactly one support
point in each coset; in particular |S| = m²/ord(t)). Then the first-return
map R equals the loop-successor map σ = A|_S. Hence

    B is a single m²-cycle  ⟺  A is a single loop.

*Proof.* Let φ: Z_m² → Z_m²/⟨t⟩ be the quotient map. For p ∈ S,
φ(B(p)) = φ(p + a(p) + t) = φ(p + a(p)) = φ(σ(p)). The return point R(p) lies
in S and in the same coset as B(p) (returns only add multiples of t), and
σ(p) ∈ S lies in that coset too; by transversality R(p) = σ(p). So R = σ,
whose cycles are exactly the loops of A; conclude by Proposition 1.2
(coverage is automatic). ∎

**Corollary 2.2 (diag11).** diag11 (a(i,i) = e0, a(i+1,i) = e1) is a single
2m-loop and its support is a perfect transversal of the 2m cosets of ⟨t_2⟩:
φ(i,i) = (i mod 2, i) runs over all labels (ε, v) with ε ≡ v (mod 2), and
φ(i+1,i) = (i+1 mod 2, i+2) over all labels with ε ≢ v (mod 2). Therefore
B_2 = T_{t_2} ∘ diag11 is a single m²-cycle for **every** even m. ∎
[M] T2, m = 4..40.

**Classification of 2m-point transversal gadgets.** A (w0, w1)-loop of length
2m has w0 + w1 = 2, and w1 = 0 (or w0 = 0) forces a plain length-m circle;
so a 2m-point loop is a (1,1)-staircase, i.e. a cyclic word
w ∈ {e0, e1}^{2m} with m of each letter (walked from any start). Its label
walk is ℓ_k = (a_k mod 2, (3a_k − k) mod m), a_k = #e0 among the first k
letters; the support is a perfect transversal iff ℓ_0, …, ℓ_{2m−1} are
pairwise distinct. [M] Exhaustive DFS enumeration (words_dfs.py, m ≤ 20):

- for m ≡ 2, 4 (mod 6): the **alternating word (diag11) is the only**
  transversal class (up to rotation ≙ translation of the loop);
- for m ≡ 0 (mod 6): exactly 4 classes — diag11 and three period-6 families
  with cyclic run profiles (2,1,1,2)^{...}, (2,2,1,1)^{...}, (3,3)^{...}.

(Conjecture, machine-verified m ≤ 20: this classification holds for all even
m. The collision equation "a_k − a_j even and 3(a_k − a_j) ≡ k − j (mod m)"
makes the special role of gcd(m, 3) visible.)

---

## 3. Why diag11 admits no completion — and neither does any other
      2m-point gadget (the hard question behind the SAT infeasibility)

### 3.1 Equidistribution (a new necessary condition)

**Lemma 3.1 (anti-diagonal equidistribution).** Suppose B = T_t ∘ A is a
single m²-cycle and the level increments u ↦ u + Δu of B take exactly two
consecutive values: Δu = s on the idle set I and Δu = s + 1 on S (both taken
mod m, with representatives ŝ, ŝ+1 ∈ {1, …, m}). Then I meets every level
{u = const} in exactly |I|/m points (and so does S, in m − |I|/m points).

*Proof.* Lift the cyclic u-itinerary of the single cycle to Z with the
positive step representatives. Total climb = ŝ·m² + |S|, so the itinerary
winds N = ŝ·m + |S|/m times (in particular m divides |S|; that much already
follows from Fact 0.1). On each wind, each level u₀ is either landed on or
skipped, so N = visits(u₀) + skips(u₀). Since the cycle is Hamiltonian,
visits(u₀) = |{p : u(p) = u₀}| = m. A step of size ŝ from level a skips
levels a+1, …, a+ŝ−1; a step of size ŝ+1 also skips a+ŝ. Hence
skips(u₀) = (ŝ−1)·m + |S ∩ level(u₀ − ŝ)|. Therefore
|S ∩ level(u₀ − ŝ)| = N − m − (ŝ−1)m = |S|/m, independent of u₀. ∎

All three budgets satisfy the hypothesis: for B_0, (Δu on I, Δu on S) =
(1, 2); for B_1, (3, 4); for B_2, (m−6, m−5) (for m = 6 the idle step is a
full wrap ŝ+... = 6 = m; the argument is unaffected). So:

**Corollary 3.2.** In every solution of the reduced problem, each idle set
I_c meets every anti-diagonal u = const in exactly n_c = |I_c|/m points, and
n_0 + n_1 + n_2 = m. [M] T4: surgery_m6 has (n_0,n_1,n_2) = (2,1,3),
surgery_m8 has (1,2,5); the gadget_family solutions for m = 8, 10, 12 all
comply ((3,2,3)·… checked per level).

**Lemma 3.3 (no empty idler for cycles 0, 1).** n_0 ≥ 1 and n_1 ≥ 1.
*Proof.* If I_0 = ∅ every B_0-step has Δu = 2, so u mod 2 is invariant
(well-defined since m is even) and B_0 has ≥ 2 cycles. If I_1 = ∅ every
B_1-step has Δu = 4: same conclusion. ∎ (No such argument for cycle 2:
Δu = −5 on S(A_2) is odd.)

### 3.2 The crossing identity

View the loops of the three fields as closed curves on the torus (each loop
uses the lattice edges p → σ(p)). By the Latin property no edge is used
twice, so two curve families intersect only at shared lattice vertices.

**Lemma 3.4 (in-edge dichotomy).** Let p ∈ S(A_c) ∩ S(A_{c'}), c ≠ c', say
a_c(p) = e0, a_{c'}(p) = e1. The in-edge of curve c at p is either the west
edge (from p − e0, if a_c(p − e0) = e0) or the south edge (from p − e1, if
a_c(p − e1) = e1) — and c, c' take one each. Moreover the third cycle c''
(the idler at p) owns neither in-edge.
*Proof.* If a_{c''}(p − e0) = e0 then A_{c''}(p − e0) = p = A_{c''}(p)
(c'' idles at p), contradicting bijectivity; same for p − e1. Each of the
curves c, c' has in-degree 1 at p, the two available in-edges are the west
and south edges, and they cannot share one (the point p − e0 has a unique
cycle moving e0 there). ∎

So at each shared point exactly two local configurations are possible:
* **(straight, straight)**: c runs west→east, c' runs south→north — a
  transversal crossing of intersection index +1 (with the orientation
  convention (e0-mover) × (e1-mover) = +1);
* **(corner, corner)**: c runs south→east, c' runs west→north — the two
  L-shaped corners touch without crossing, index 0.

**Proposition 3.5 (crossing identity).** For c ≠ c',

    W0_c·W1_{c'} − W1_c·W0_{c'}  =  X_{cc'} − X_{c'c},

where X_{cc'} = #{p : a_c(p) = e0 entered from the west and a_{c'}(p) = e1
entered from the south} (the (straight, straight) points with c as the
e0-mover). *Proof.* The left side is the homological intersection pairing of
the 1-cycles [A_c] = (W0_c, W1_c) and [A_{c'}]; the right side is the sum of
local indices over all intersection points, by Lemma 3.4 and the two-case
analysis. ∎ [M] T5: verified for all 6 ordered pairs on surgery_m6 and
surgery_m8 (nontrivially: windings (3,1),(1,4),(2,1) at m=6).

### 3.3 The rigidity theorem

**Theorem 3.6 (diag11 rigidity).** For every even m ≥ 4, there is **no**
Latin triple (A_0, A_1, diag11) with A_0, A_1 bijective and B_0, B_1 single
m²-cycles. (So the observed SAT infeasibility at m = 6, 8 is an instance of
a uniform obstruction — diag11 can never be completed.)

*Proof.* Write D = {(i,i)}, D' = {(i+1,i)}; S(diag11) = D ∪ D'.
1. Exactly one cycle idles at each point and diag11 idles off D ∪ D', so
   I_0 ⊔ I_1 = D ∪ D' and |I_0| + |I_1| = 2m.
2. Forced moves: at (i,i) the moves left for cycles 0, 1 are {id, e1}; at
   (i+1, i) they are {id, e0}. So whenever cycle 0 moves on D it moves e1,
   and on D' it moves e0 (same for cycle 1).
3. Forced in-edges: if (i,i) ∈ S(A_0), its A_0-in-edge comes from
   (i−1, i) (west): the alternative source (i, i−1) lies on D' where cycle 0
   cannot move e1 by step 2. Likewise the in-edge at (i+1, i) ∈ S(A_0) comes
   from (i+1, i−1) (south), since (i, i) ∈ D cannot move e0.
4. diag11's own curve is the tight staircase: at (i,i) it enters from the
   south and exits east; at (i+1,i) it enters from the west and exits north —
   every point of diag11 is a corner.
5. By 2–4, every shared point of curves(A_0) and diag11 is a
   (corner, corner) configuration, so by Proposition 3.5
   W0_0 − W1_0 = [A_0]·[diag11] = 0, i.e. W0_0 = W1_0; hence
   |S(A_0)| = m(W0_0 + W1_0) = 2m·W0_0 and |I_0| = m² − 2m·W0_0 ≡ 0
   (mod 2m), because m even makes m² ≡ 0 (mod 2m). Same for A_1.
6. With |I_0| + |I_1| = 2m this forces {|I_0|, |I_1|} = {0, 2m}.
7. But I_0 = ∅ makes B_0 preserve u mod 2 (Lemma 3.3), and I_1 = ∅ makes
   B_1 preserve u mod 2 — either way one of B_0, B_1 is not a single cycle.
∎

Remark (parity is essential): for odd m, m² ≡ m (mod 2m), so step 5 gives
|I_0| ≡ m (mod 2m) and |I_0| = |I_1| = m is *allowed* — consistent with the
solvability of the odd case.

[M] T6 cross-checks at m = 6, 8: (i) the full completion model is INFEASIBLE;
(ii) 40+ sampled Latin bijective completions (no single-cycle constraint) all
have W0_0 = W1_0, W0_1 = W1_1 and (|I_0|, |I_1|) ∈ {(0, 2m), (2m, 0)};
(iii) adding the constraint |I_0| = m to the bijectivity-only model is
already INFEASIBLE, exactly as step 5 predicts; (iv) sampled solutions with
I_0 = ∅ have B_0 split (u-parity classes), as step 7 predicts.

### 3.4 The full 2m-support dead end

**Proposition 3.7.** In any solution of the reduced problem (even m):
|S(A_2)| ≥ 2m, and if |S(A_2)| = 2m then A_2 is a single (1,1)-loop whose
support is a perfect transversal of the ⟨t_2⟩-cosets.
*Proof.* Coverage (Prop. 1.2(a)) needs |S(A_2)| ≥ #cosets = 2m. If equal:
the loop decomposition of a 2m-point support is either one (1,1)-loop or two
length-m circles; two loops contradict Fact 0.2 (odd loop count); coverage
with |S| = #cosets forces a transversal. ∎

Combining with the classification of Section 2 and Theorem 3.6:

* for even m ≢ 0 (mod 6), m ≤ 20: the only candidate is diag11 (up to
  translation, which conjugates the whole problem and preserves the budgets),
  and it is rigid ⇒ **every solution has |S(A_2)| ≥ 3m** (support sizes are
  multiples of m).
* for m = 6: the three non-alternating transversal gadgets exist but SAT
  shows **all of them are INFEASIBLE to complete** [M] W2 — this is *not*
  explained by Theorem 3.6 (those curves have straight points, so step 5
  fails); finding the invariant that kills them is an open problem (they
  only exist for m ≡ 0 mod 6, so it is not on the critical path).
* ground truth agrees: surgery_m6 has |S(A_2)| = 18 = 3m (winding (2,1)),
  surgery_m8 has 24 = 3m (winding (1,2)); the m = 10 artifact
  gadget_family_m10 has |S(A_2)| = 50 = 5m (winding (2,3)). [M] W3

---

## 4. The helix12 family: exact failure analysis (Task 3)

helix12(m) is a single 3m-loop of winding (1,2). Its support labels under
φ = (x mod 2, 2x − y):

| support piece            | labels (ε, v)                     |
|--------------------------|-----------------------------------|
| (0,0) e0                 | (0, 0)                            |
| (1, j), j = 0..m−1       | (1, 2−j): all labels with ε = 1 … |
| (2, m−1), (2, 0)         | (0, 5), (0, 4)                    |
| (i, 1), i = 2..m−1       | (i mod 2, 2i − 1)                 |
| (m−1, 2)                 | (1, m−4)                          |
| (0, j), j = 2..m−1       | (0, m−j): covers (0, 1..m−2)      |

Every label with ε = 1 is covered (the column x = 1 alone does it). For
ε = 0 the covered v-values are {0} ∪ {1, …, m−2} ∪ {4, 5} ∪
{2i − 1 : i even, 2 ≤ i ≤ m−2}. The label **(0, m−1) is covered iff either
m ≤ 8 (wraparound coincidences: (2, m−1) gives v = 5 = m−1 at m = 6, and
i = m/2 works at m = 4, 8) or 2i − 1 ≡ m−1 has an even solution i = m/2,
i.e. m ≡ 0 (mod 4).** This is the parameter equation that fails:

* **m ≡ 2 (mod 4), m ≥ 10:** the coset (x even, y ≡ 2x + 1) is disjoint from
  the support; by Proposition 1.2(a), B_2 contains the pure-translation
  (m/2)-cycle on that coset. Coverage fails at exactly this one coset.
  [M] T3: the single uncovered label is (0, m−1) for m = 10, 14, 18, 22.
* **m ≡ 0 (mod 4), m ≥ 12:** coverage holds but condition (b) fails: the
  first-return map on the 3m support points splits into cycles of lengths
  **[6 × (m−10)/2, 12, 18]** (machine-verified m = 12, 16, 20, 24; total
  3m ✓). The proliferating 6-cycles are anchored at the multiplicity-3
  cosets, whose count grows as (m−4)/2 while at m = 4, 8 the wraparound
  keeps the return orbit connected.

So helix12 fails coverage on half the residues and return-connectivity on
the other half — both are visible, parametric equations rather than
accidents, and both are exactly the two clauses of Proposition 1.2. [M] T3.

---

## 5. Dense cycles: reformulation via idle sets (Task 4)

Cycles 0 and 1 have supports of size m² − |I_c| = m² − n_c·m with small n_c
(ground truths: n_c ∈ {1, 2, 3, 5}); the section Σ = S of Proposition 1.2 is
useless there. Reformulation:

**Data.** A solution is equivalent to (i) the partition Z_m² = I_0 ⊔ I_1 ⊔
I_2 (who idles where) and (ii) one bit ε(p) at each point choosing which of
the two non-idling cycles takes e0 (the other takes e1).

**Necessary conditions on the partition (all proved above, all [M]):**
1. m | |I_c|; write n_c = |I_c|/m; n_0 + n_1 + n_2 = m.
2. Each I_c meets every anti-diagonal in exactly n_c points (Cor. 3.2).
3. n_0 ≥ 1 and n_1 ≥ 1 (Lemma 3.3).
4. Winding budget: Σ_c W0_c = Σ_c W1_c = m, with
   W0_c + W1_c = m − n_c.
5. Odd loop count for each A_c (Fact 0.2).
6. Crossing identities (Prop. 3.5) for the three pairs — these couple the
   winding imbalances W0_c − W1_c to the local straight/corner structure,
   and are the precise mechanism by which the *shape* of one cycle's curve
   constrains the *windings* of the others (Theorem 3.6 being the extreme
   case: an all-corner sparse curve forces both dense cycles to be balanced,
   which is arithmetically impossible).

**Single-cycle condition in dense form.** Apply Lemma 1.1 with Σ = I_c
(nonempty by 3.; for c = 2 use Σ = S(A_2) as before):

    B_c single  ⟺  (a′) no B_c-cycle avoids I_c, and
                   (b′) the first-return map R_c on I_c is a single
                        (n_c·m)-cycle.

Between visits to I_c the dynamics is the deterministic staircase-with-drift
flow q ↦ q + a_c(q) + t_c on S(A_c) — a monotone walk, so (b′) is a finite,
explicitly computable interval-exchange-like condition. Useful structure:
* For B_0, Δu = 2 on S(A_0): any trapped cycle (violating (a′)) preserves
  u mod 2. Leaving an idle point at level u, the next idle point reached
  lies at a level ≡ u + 1 (mod 2): **the return itinerary of B_0 alternates
  level parity.**
* For B_1, Δu = 4 on S(A_1): trapped cycles preserve u mod 2 again, and the
  return itinerary steps through level residues mod 4 as c → c+3 → c+2 →
  c+1 → c.
* In the minimal case n_c = 1 (which occurs in the ground truths), I_c
  contains exactly one point per level, so **(b′) becomes: an explicitly
  computable permutation of Z_m (levels) is a single m-cycle** — the same
  size as the design freedom (one idle position per level plus the ε-bits).
  This is the right object for a uniform-in-m design: cycle 0's return map
  alternates parity, cycle 1's steps by +3 mod 4, and both are determined
  by the interleaving of the idle positions ρ_c(u) with the ε-field.

---

## 6. Joint design directions (with supporting evidence)

**D1 — 3m-support winding-(1,2) gadgets for cycle 2 (primary).**
Proposition 3.7 + Theorem 3.6 prove that the sparse end of the design space
is |S(A_2)| = 3m (achieved by both ground truths). Such gadgets are cyclic
words with m e0's and 2m e1's; coverage says the 3m points hit all 2m cosets
(multiplicity profile then has ≥ m singleton cosets), and the return map is
"label successor with a race in the doubled cosets" — one deterministic
choice per doubled coset, i.e. an explicitly analyzable perturbation of
Theorem 2.1. Empirics [M] W4/W5: among random (1,2)-word gadgets with B_2
single, 5/30 admit completions at m = 6 and 7/30 at m = 8 (one completion
per m independently re-verified — Latin + bijective + all three B_c single —
and saved as word12_completion_m6.json / word12_completion_m8.json; e.g. the
m = 6 one has windings A_0 = (2,3), A_1 = (3,1), A_2 = (1,2)), but at m = 10
six out of six random ones were **INFEASIBLE** to complete, and the known
m = 10 solution uses a 5m-support (2,3)-loop instead. So the boundary of completability moves with
m: characterizing *which* (1,2)-words complete (via the necessary conditions
of Section 5 — especially how many straight points in which cosets the
crossing identities demand) is the sharpest open question this machinery can
now attack.

**D2 — co-design through the partition (I_0, I_1, I_2).**
Search/construct directly in the dense reformulation: choose n = (n_0, n_1,
n_2) (start with ground-truth patterns like (1, 2, m−3), n_2 ≡ largest),
place the idle points subject to equidistribution, and use the two skeletal
facts (parity alternation for cycle 0, +3 mod 4 stepping for cycle 1) to
force the level-return maps to be m-cycles by construction. The sign
condition (#loops odd) and the crossing identities are the two global
correction terms a uniform pattern must budget for.

**D3 — settle the two open classification claims.**
(i) Prove the transversal-word classification (only diag11 unless 3 | m)
from the collision equation — a short number-theoretic argument should do
it; (ii) find the invariant killing the three m ≡ 0 (mod 6) transversal
gadgets (all SAT-infeasible at m = 6 [M] W2). Both would upgrade
"|S(A_2)| ≥ 3m" from (proved for m ≤ 20, m ≢ 0 mod 6, plus m = 6 by SAT) to
all even m.

**Falsified along the way (adversarial log).**
* "Any run-word with one double run is a transversal": false — e.g.
  [1,1,2,2] + [1,2]^{m−2} is *not* a transversal for any even m ≤ 40 [M] T7.
* "diag11 fails only because it is all-corners": incomplete — the three
  straight-run transversal gadgets at m = 6 also fail [M] W2, so the 2m dead
  end is deeper than Theorem 3.6.
* "helix-style 3m gadgets always complete once B_2 is single": false at
  m = 10 [M] W4.

## 7. File map

* `criterion.py` — all machinery + tests T0–T7 (run `python3 criterion.py
  0 1 2 3 4 5` for the pure-analytic suite, `6`/`7` for the SAT suites).
* `criterion2.py` — W1 (word landscape), W2 (m=6 transversal completions),
  W3 (ground-truth A_2 structure), W4 (m=10 (1,2)-gadget search).
* `criterion3.py` — W5 ((1,2)-word completability statistics, m = 6, 8).
* `words_dfs.py` — exhaustive transversal-word enumeration (m ≤ 20).
* `word12_completion_m6.json`, `word12_completion_m8.json` — full verified
  solutions of the reduced problem around 3m-word gadgets (format identical
  to surgery_m*.json).
