# Dense-cycle template (obligation 3): the dual-gadget reduction,
# bit-field rigidity, and the toggle box

Session 3 notes. Machine work in `dense_template.py` (tests D1–D5 plus the
drivers; every numbered claim marked [M] is asserted there and the suite
aborts on failure). Notation from `analytic_criterion.md`; budgets
t_0 = (0,1), t_1 = (1,2), t_2 = (−2,−4).

## 0. Outcome in one paragraph

The dense fields A_0, A_1 are NOT to be designed pointwise: after a change
of coordinates each dense cycle becomes a *sparse* staircase-gadget problem
of exactly the same type as cycle 2, and the entire completion of a gadget
word W is equivalent to a single bit field b on Z_m² subject to a *local*
closure system C(W). The solution set of C(W) is tiny (4–4096 elements for
every chain word, m ≤ 24) and has the structure of a (sub)box of disjoint
GF(2) "bridge toggles". Completability of W is decided exactly, in seconds,
by exhausting C(W) and applying the first-return criterion twice. This
replaces the m²-node AddCircuit SAT (hours at m = 18–20) by an exhaustive
procedure (< 3 s at m = 24) and yields verified template completions of
chain gadget words at every even m ∈ [6, 24], the m = 22, 24 stations being
new. The remaining gap for a uniform-in-m proof is precisely quantified in
§7.

## 1. Analysis of the verified solutions (task 1) — negative result first

Extraction of the level data of all 16 stored solutions (`partA`): idle
positions per anti-diagonal, B_0/B_1 return itineraries and times, per-level
winding histograms, ε-fields. Findings [M]:

* the proven invariants hold universally (equidistribution n_c per level;
  B_0's idle itinerary alternates u-parity; B_1's steps u by +3 mod 4 per
  return; loop counts odd) — and *nothing else is shared*. Idle profiles
  (n_0, n_1) ∈ {(1,2),(2,1),(2,3),(3,2),(2,1),(1,2)…}, windings, per-level
  histograms, return-time sequences and ε-fields differ arbitrarily across
  the artifacts, including between two solutions at the same m.
* Conclusion (consistent with induction3 §3): the pointwise dense fields
  carry no transportable structure; the design has to happen in better
  coordinates.

## 2. The dual factorization (the right coordinates)

**Theorem D1 (dual factorization).** Define for a completion (A_0, A_1) of
a gadget field A_2 = W:

    D_0 = T_{(−1,0)} ∘ A_0 ,     D_1 = T_{(0,−1)} ∘ A_1 .

Then D_0 is the field with move alphabet {id, L, Λ}, L = (−1,0), Λ = (−1,1):

    a_0(p) = e0 ⟹ D_0(p) = p (identity);  a_0(p) = id ⟹ move L;
    a_0(p) = e1 ⟹ move Λ,

and    B_0 = T_{(0,1)} ∘ A_0 = T_{(1,1)} ∘ D_0 .
Similarly D_1 has alphabet {id, S, Z}, S = (0,−1), Z = (1,−1):
e1 ↦ identity, id ↦ S, e0 ↦ Z, and B_1 = T_{(1,2)} ∘ A_1 = T_{(1,3)} ∘ D_1.

*Proof.* Pointwise: A_0(p) + (0,1) = (A_0(p) − (1,0)) + (1,1), and the move
table is a_0(p) − (1,0) ∈ {(−1,0), (0,0), (−1,1)}. Same for D_1 with
a_1(p) − (0,1). ∎

Structural consequences.
* supp(D_0) = Σ_0 := I_0 ∪ E1_0 (idle set and e1-set of A_0);
  supp(D_1) = Σ_1 := I_1 ∪ E0_1. Since ground-truth dense fields have
  |I_c| + |E·_c| ≪ m², **the dense cycles are sparse gadgets in dual
  coordinates**: B_0 is a translation off Σ_0, B_1 off Σ_1.
* A_0 bijective ⟺ D_0 bijective ⟺ Σ_0 with its L/Λ letters decomposes into
  closed "anti-staircase" loops (Fact 0.1 verbatim: both moves have
  Δx = −1, so the successor argument applies; each loop has length a
  multiple of m). Same for D_1 (Δy = −1).
* Proposition 1.2 applies verbatim to B_0 = T_{(1,1)} ∘ D_0 with section
  Σ_0: coverage of the m cosets of ⟨(1,1)⟩ (the diagonals v = x−y) plus
  single first-return map, computable as R = ν∘σ (induction3 Thm 1.1).
  For B_1 the translation (1,3) has order m and cosets labelled by
  w = 3x − y.
* The three move alphabets {e0,e1}, {L,Λ}, {S,Z} are the three adjacent
  pairs of lattice hexagon directions: with M = [[−1,−1],[1,0]] (order 3),
  M{e0,e1} = {Λ,L} and M{Λ,L} = {Z,S}. All three cycles are staircase-loop
  gadgets — the translations (t_2, (1,1), (1,3)) break the symmetry, the
  combinatorics does not.
* Sign bookkeeping transfers: sgn T_{(1,1)} = sgn T_{(1,3)} = +1 (m cycles
  of length m, m even ⟹ each odd permutation, even count... computed as
  ((−1)^{m−1})^m = +1), every dual loop has even length, so each D_c needs
  an odd loop count — observed 1 or 3 in every stored solution.

[M] Test D1: on all 16 stored solutions and both dense cycles, the
factorization holds pointwise, the dual fields are loop-decomposable with
odd loop counts, and (coverage + single return on Σ_c) ⟺ B_c single.
Dual support sizes range from 2m (surgery_m8, D_0: a single 2m-loop
threading W's e0-points, closed by an anti-diagonal bridge of length 5
through I_2 at level u ≡ 0 — the prototype of the template) up to ~m²/2
for the unstructured SAT artifacts.

## 3. The bit-field parametrization and the closure system C(W)

At every point exactly one cycle idles, so given W a completion is one bit
per point. Normalize it as the **swap bit** b : Z_m² → {0,1}:

| class of p        | b = 0                  | b = 1                  |
|-------------------|------------------------|------------------------|
| S₂⁰ (W moves e0)  | A_0 id, A_1 e1         | A_0 e1, A_1 id         |
| S₂¹ (W moves e1)  | A_0 e0, A_1 id         | A_0 id, A_1 e0         |
| I_2 (W idles)     | A_0 e0, A_1 e1         | A_0 e1, A_1 e0         |

**Theorem D2 (parametrization).** (A_0, A_1) ↦ b is a bijection between
Latin-compatible pairs for W and bit fields; under it

    Σ_0 = S₂⁰ ∪ {b = 1 on S₂¹ ∪ I_2},   D_0-letters: L on {S₂⁰, b=0} ∪
          {S₂¹, b=1};  Λ on {S₂⁰, b=1} ∪ {I_2, b=1};
    Σ_1 = S₂¹ ∪ {b = 1 on S₂⁰ ∪ I_2},   D_1-letters: S on {S₂¹, b=0} ∪
          {S₂⁰, b=1};  Z on {S₂¹, b=1} ∪ {I_2, b=1},

and (A_0, A_1) are both bijective iff b satisfies the **local closure
system C(W)**: for every point, the active out-arc of D_0 (resp. D_1) lands
in Σ_0 (resp. Σ_1), and every point has at most one active in-arc per dual
field. (Bijectivity of a finite total injective successor ⟹ permutation.)
Coverage of the v-cosets by Σ_0 and the w-cosets by Σ_1, and I_0 ≠ ∅ ≠ I_1,
are necessary conditions (Prop. 1.2(a), Lemma 3.3) also imposed in the
implemented model. Then

    (A_0, A_1) is a completion  ⟺  b ⊨ C(W) and both first-return maps are
                                    single cycles (checked directly, O(m²)).

*Proof.* The table is the Latin condition at each class; bijectivity ⟺ dual
loop decomposition (§2) ⟺ closure + injectivity, which are single-point and
two-point local constraints in b. ∎

[M] Test D2: for each of the 16 stored solutions, b roundtrips through the
table back to (A_0, A_1) exactly, and b is feasible for the implemented
C(W) — the encoding is not over-constrained.

Every constraint in C(W) is local (implications between b-literals at
lattice neighbours; at-most-one over ≤ 2 literals; m coverage clauses).
There is **no Hamiltonicity constraint in the model at all.**

## 4. Rigidity: the closure space is tiny, and its shape

**Lemma D3 (bridge propagation).** Let b ⊨ C(W), X = {p ∈ I_2 : b(p)=1}.
Then (i) X is a union of *full* maximal anti-diagonal segments of I_2:
p ∈ X and p ± (−1,1)... precisely, if p ∈ X and p + (−1,1) ∈ I_2 then
p + (−1,1) ∈ X (D_0-closure: the Λ-successor of p must lie in Σ_0, and on
I_2 membership means b = 1), and if p + (1,−1) ∈ I_2 then p + (1,−1) ∈ X
(D_1-closure via the Z-in-arc... via the Z-successor of p). (ii) endpoint
recruitment: if the NW-end successor p + (−1,1) lies in S₂¹ then b = 1
there (A_0 idles there); if the SE-end successor p + (1,−1) lies in S₂⁰
then b = 1 there (A_1 idles there). ∎ (immediate from closure)
[M] Test D5 on all 26 available completions.

So the I_2-part of any solution is a set of **anti-diagonal bridges**, each
spanning a full gap of I_2 between two points of W's curve, with forced
recruitment bits where a bridge lands on the "wrong shore" (e1-shore at the
NW end, e0-shore at the SE end). The b-bits on W's support are likewise
chained by closure along W's runs. The result is extreme rigidity:

**Census [M, D4]** — exhaustive enumeration of C(W) for the chain gadget
words (double-period insertion chain, k=1 for m ≤ 12, k=2 for m ≥ 14; the
m = 22, 24 words are new, constructed here by insertion from the m = 20
station):

| m  | |C(W)| | B_0 single | completions | time  |
|----|--------|-----------|-------------|-------|
| 6  | 4      | 3         | 1           | 0.5 s |
| 8  | 16     | 5         | 2           | 0.0 s |
| 10 | 16     | 6         | 2           | 0.0 s |
| 12 | 4      | 1         | 1           | 0.0 s |
| 14 | 64     | 19        | 3           | 0.0 s |
| 16 | 252    | 80        | 7           | 0.1 s |
| 18 | 1024   | 281       | 33          | 0.4 s |
| 20 | 256    | 47        | 6           | 0.2 s |
| 22 | 256    | 56        | 4           | 0.2 s |
| 24 | 4096   | 715       | 59          | 2.9 s |

All enumerations complete (CP-SAT `enumerate_all_solutions`, status
OPTIMAL). Every chain word is completable, and the FULL completion sets
are now known. Compare: the previous route (AddCircuit over m² nodes)
needed hours per station at m ≈ 18–20 and proved nothing about
uniqueness.

**Ground-truth agreement [M, D3].** At m = 6 all 1038 canonical
(1,2)-words were re-enumerated: 77 are simple + B_2-single; exhausting
C(W) for each and checking the criteria reproduces the SAT-derived
completable set *exactly* (the 7 words of `m6_completable_words.json`);
the completable ones have exactly 1 completion (one word: 2). Total time
0.2 s for all 77 — this validates the procedure as a sound and complete
decision method for completability of a given word.

**Toggle-box structure [M, partD6-style probe].** Fix the minimum-|b|
solution b_min of C(W). Empirically (m = 10, 14: exactly; m = 16: sub-box):

    solutions of C(W) = { b_min ⊕ ⨁_{t ∈ T'} t  :  T' ⊆ T (allowed) },

where T is a set of pairwise **disjoint** toggle sets (|T| = 4, 6, 8 at
m = 10, 14, 16; |C(W)| = 2^|T| when the box is full). Each small toggle is
a **bridge relocation**: an anti-diagonal X-segment at level u plus the
parallel segment at u ± 1 with its endpoint-recruitment bits — switching
the toggle slides the bridge to the adjacent anti-diagonal. One large
toggle (size ≈ m²/2 ± …: 71, 135, 175) rearranges many bridges at once.
At m = 16 some toggle pairs conflict (injectivity), giving 252 = a proper
sub-box of 2^8.

So the sharp characterization requested by the task is:

> **A completion of W = the minimum solution of the local closure system
> C(W), modified by an arbitrary allowed subset of the disjoint bridge
> toggles; valid iff the two dual return maps ν∘σ (translations (1,1) and
> (1,3)) are single cycles.**

The abundance of valid choices is high and stable: 25–35 % of C(W) is
B_0-single, ~1–25 % jointly single, for every station tested.

## 5. The constructor (the deliverable template)

`dense_template.py` implements:

1. `template_model(m, W)` — C(W) as a CP-SAT model (local constraints
   only);
2. `sample_template` / `census` — enumeration with on-the-fly first-return
   checks; `fields_from_bits` — the table of §3;
3. `run_chain` — chain stations m = 6..20 from the stored artifacts
   (template completions found in ≤ 0.3 s each, saved as
   `dense_template_m{m}.json`);
4. `extend_chain` — new stations: insertion children of the m = 20 word,
   template-completed at m = 22 (child 1, 92 children available) and
   m = 24 (child 0), words saved as `chain_word_m{22,24}_k2.json`,
   completions as `dense_template_m{22,24}.json`, all re-verified
   independently (Latin, bijective, three single m²-cycles: `verify_full`).

**Frontier statistics** (station census, exhaustive for every child): at
m = 22, 40 of the 92 B_2-single children are completable (43 %, 104 s
total); at m = 24, 46 of 82 (56 %, 138 s). The failures are *proofs* of
non-completability (closure space exhausted, no valid member) — e.g. the
m = 22 child 0 with |C(W)| = 128, 9 B_0-singles, 0 joint; closure spaces
across both frontiers range 64–16384. Full data in
`dense_template_station_census.json`. Compare induction3 §4, where a
single INFEASIBLE child at m = 18 cost a long SAT run: the same verdict is
now an exhaustive certificate in ~1 s.

## 6. Why this is the right inductive object

The template turns obligation 3 into a statement with the same shape as
the gadget-word induction (obligation 1):

* the dense completion is no longer a 3^{m²} search but a bounded, local,
  exhaustible structure attached to W;
* the two dense criteria are ν∘σ single-cycle conditions on sparse
  sections — the same Cohn–Lempel-type object as Lemma B for B_2 (for
  balanced dual sections, singleness IS a GF(2) interlacement-rank
  condition);
* the b-freedom is a finite explicit box, so "some completion exists" is a
  disjunction over ≤ 2^{O(m)} — empirically ≤ 4096 — explicitly listed
  candidates.

## 7. Honest gaps (exact statements of what remains)

1. **No closed-form b(p).** The template is an O(1)-described *procedure*
   (solve C(W), pick any valid element), not a pointwise formula. Given
   that the chain words are themselves only defined by iterated insertion,
   a pointwise formula is arguably the wrong target; but a formula for a
   *co-designed* explicit word family remains open (surgery_m8's
   cross-shaped word + 2m-loop D_0 is the model case; such k=1 words die
   out by m ≈ 16 — winding_law §1.2 — so a co-designed family must have
   k ~ m/4).
2. **Nonemptiness not proved uniformly in m.** Verified: every station
   m = 6..24 (chain words), 43 % of the m = 22 frontier. To prove: "along
   the insertion chain, some B_2-single child admits a valid toggle
   choice". Suggested route: (a) describe how C(W') of a child relates to
   C(W) under double-period insertion (the bridge structure is local along
   the anti-diagonals, and the insertion is local along the word — the
   toggle boxes should be stable away from the splice); (b) show the two
   single-cycle conditions restricted to the box are non-degenerate
   (Cohn–Lempel rank argument, cf. the Insertion Lemma of induction3 §2).
   This is the same class of open problem as obligation 1 — the two should
   be attacked together.
3. **Toggle theory not formalized.** Provable-looking claims, currently
   only machine-observed: (i) solutions of C(W) form a sub-box over a set
   of disjoint toggles; (ii) each minimal toggle is a bridge relocation
   u → u ± 1; (iii) |T| grows ~ linearly in m. (i) should follow from
   viewing C(W)-solution differences as disjoint alternating cycles of the
   two successor structures.
4. **Coverage/nonempty-idle are imposed, not derived**: C(W) as
   implemented contains two necessary conditions of singleness beyond
   bijectivity (coverage, I_0, I_1 ≠ ∅). Dropping them enlarges the
   enumeration but changes nothing else; kept for speed.

## 8. File map

* `dense_template.py` — everything; suites: `A` (level-data extraction),
  `D1` (dual factorization ⟺ criterion, 16 solutions × 2 cycles), `D2`
  (parametrization soundness), `D3` (m=6 exhaustive ground-truth
  agreement), `D4` (chain census m=6..24), `D5` (bridge-propagation
  lemma), `RUN` (regenerate template completions).
* `dense_template_m{6..24}.json` — verified template completions (same
  format as chain_completion files).
* `chain_word_m22_k2.json`, `chain_word_m24_k2.json` — new chain stations.
* `dense_template_station_census.json` — full m=22/24 frontier census.
