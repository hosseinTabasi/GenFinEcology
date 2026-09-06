# GenFinEcology Experimental Protocol

**Project:** GenFinEcology — a methods-grade **feature-ablation ecology** for generative financial text. Extends evaluation from blob “persuade” contrasts to construct-isolated rewrites, surface detectability, multi-round corpus contamination, and bootstrap CIs.

**Author:** Hossein Tabasi, M.Tech Computer Science and Engineering, Shoolini University. GitHub: `hosseinTabasi`.

**License:** MIT.

**Assets in scope:** USD Tether (USDT) and USD Coin (USDC), plus clearly labeled lab fixtures when used.

**Version:** 1.0 (deterministic template / rule generation; offline; seedable).

**Relationship to prior work by the same author.** This repository **enhances** GenFinTextEval (Layers A/B/C on anchored vs persuade vs paraphrase). GenFinTextEval remains a valid A/B/C baseline. GenFinEcology adds: (i) feature ablations, (ii) Layer D detectability, (iii) multi-round ecological contamination (C+), (iv) bootstrap CIs, (v) multiple pre-registered RQs. Related but distinct: SynthOpinion, EchoMarket. Do not conflate claims across repositories.

**Intellectual mandate.** Reject BLEU / ROUGE / perplexity as primary claims. Distinguish **surface**, **epistemic**, **strategic**, and **ecological** generation. Evaluation **must** include layers A+B+C+D.

**Generator name.** Deterministic template generator with **construct-isolated** corruptions and strategic cues. No paid external decoder is required.

No output is investment advice. No module places live posts or executes trades.

---

## Claim taxonomy (label every claim)

| Label | Meaning |
|-------|---------|
| **definitional** | How a construct is named or measured in this protocol |
| **descriptive** | What the offline study observed under locked seeds |
| **causal** | What the design would identify if confounders were bounded |
| **speculative** | Extrapolation beyond computational personas / bag-of-texts index |

Primary RQ claim type: **causal** *within the computational design*, reported with identification threats; empirical tables are **descriptive** of the seeded study. Layer D is labeled **descriptive** (surface detectability), not causal.

---

## Unit of analysis

- **Belief (Layer B):** `investor-persona × event × ablation-variant` (seed as replication).
- **System / contamination (Layer C):** bag-of-texts fixture with contamination rate ρ.
- **Multi-round ecology (Layer C+):** same fixture over rounds R with preferential reuse.
- **Detectability (Layer D):** text instance labeled benign vs strategic/corrupt; event-held-out transfer.

---

## Counterfactual

Holding the **event fact card** fixed, compare ablation variants that isolate constructs (see ablation table). Combined `full_persuade_*` recover the GenFinTextEval-style blob for contrast with isolates.

---

## Identification threats (named and bounded)

1. **Confounding by the underlying news event** — bound by within-event contrasts; mixed peg-path polarities; event-level bootstrap CIs.
2. **Template sensitivity** — bound by ≥3 seeds; paraphrase probe; documented templates in `generate.py`.
3. **Contamination of outcome by treatment** — Layer A text-intrinsic; Layer B documented formula; Layer C/C+ separate baseline corpus; Layer D labels are variant metadata (not circular belief outcomes). Judge circularity N/A (rule-based metrics; no LLM judge).
4. **Ablation leakage** — isolates may still co-vary weakly with polarity lexicon; report Layer A manipulation checks per variant.

---

## Theoretical tensions

- **Information vs persuasion** — `num_drift` (epistemic) vs `certainty_inflate` / `authority_cues` / `omission` (strategic) under fixed facts.
- **Disagreement vs consensus** — cross-persona σ(μ).
- **Authenticity vs polish** — anchored faithfulness vs certainty-inflated prose.
- **Contamination dynamics** — single-shot ρ vs multi-round preferential reuse.
- **Detectability vs effect size** — surface classifiers may separate variants that also move beliefs.
- **Digital-money specificity** — peg, reserves, regulation, venue access for USDT/USDC.

---

## Ablation table (definitional)

| Variant | Isolated construct | Corruption / cue |
|---------|-------------------|------------------|
| `anchored` | baseline | all facts; allowlisted sources; no fabricated orgs |
| `num_drift` | epistemic | number drift only |
| `authority_cues` | strategic | fabricated “according to …” only |
| `certainty_inflate` | strategic | certainty lexicon only |
| `omission` | strategic | omit seeded fact fraction only |
| `full_persuade_bull` | combined | omission + certainty + authority + mild drift (bull) |
| `full_persuade_bear` | combined | omission + certainty + authority + drift (bear) |
| `paraphrase` | frame stability | shuffle + synonyms of anchored |

---

## 1. Sharpened questions (pre-registered RQs)

| RQ | Question | Falsification |
|----|----------|---------------|
| **RQ1** | Do combined persuade variants increase mean \|Δμ\| vs anchored by margin m1? | fail if lift < m1 |
| **RQ2** | Does `certainty_inflate` alone move \|Δμ\| more than `num_drift` alone? | fail if cert − drift ≤ m2 |
| **RQ3** | Is |bias| after R preferential-reuse rounds larger than single-shot bias at the same ρ? | fail if |bias_MR| − |bias_SS(ρ)| ≤ m3 |
| **RQ4** | Does detectability F1 on held-out events exceed chance by margin m4? | fail if F1 − chance < m4 |

Thresholds locked in `config/study.yaml`: `m1=0.03`, `m2=0.0`, `m3=0.0`, `m4=0.15`, `chance_f1=0.5`, `R=3`, `B≥200`.

Claim labels: RQs posed as **causal** inside the design (RQ4 **descriptive**); offline run reports **descriptive** pass/fail.

---

## 2. Why it is not trivial

A blob “persuade” contrast cannot attribute belief or index moves to information corruption vs strategic cues. Single-shot ρ misses preferential re-entry dynamics. Surface detectability may succeed or fail independently of belief lift. The non-trivial object is the **joint** A+B+C+D profile under construct-isolated rewrites.

---

## 3. Construct and outcome

| Layer | Construct | Primary outcomes |
|-------|-----------|------------------|
| A Text | Faithfulness & rhetoric | numerical faithfulness; fabrication; hedge; certainty; frame stability |
| B Belief | Epistemic update | Δμ; Δconfidence; disagreement; willingness-to-act (same formula as GenFinTextEval) |
| C System | Ecological bias | sentiment-index bias vs ρ; contamination slope |
| C+ Ecology | Multi-round contamination | sentiment path over R rounds; slope vs round; preferential reuse |
| D Detect | Surface separability | TF-IDF + logistic regression accuracy/F1; held-out event transfer |

Personas are **computational**. No invented human subjects.

---

## 4. Design / identification

- **Events:** ten sourced USDT/USDC fact cards E01–E10 (verified cards aligned with GenFinTextEval / prior protocols). Split: E01–E08 train for Layer D; E09–E10 held-out.
- **Variants:** eight ablations (table above).
- **Personas:** ≥4 (`risk_officer`, `retail_momentum`, `skeptical_analyst`, `macro_allocator`).
- **Seeds:** `[20260311, 20260813, 20260101]`.
- **Factorial:** 10 × 8 × 4 × 3 = **960** belief cells (target ≥600).
- **Bootstrap:** B≥200 resamples over events for belief lift and contamination-slope contrasts; report mean and 95% percentile CI from actual resamples.
- **Identification:** within-event ablation contrasts hold the fact card fixed; C/C+ vary only mix / rounds.

---

## 5. Data and generation protocol

1. Load fact cards from `data/events/*.yaml`.
2. Generate texts with `src/genfin_ecology/generate.py` (RNG keyed by `seed:event:variant`).
3. Apply ablation rules per variant (Section ablation table).
4. Measure A → B → C → C+ → D; bootstrap; evaluate RQs; write `artifacts/*.json`.
5. `reports/RESULTS.md` **only** from JSON.

---

## 6. Principal confound and how you would bound it

**Principal confound:** the underlying news event can dominate Δμ regardless of framing.

**Bounds:** within-event contrasts; ablation manipulation checks (Layer A); multi-seed replication; event-level bootstrap CIs; pre-registered RQ thresholds (Section 7 / RQ table).

Residual threats (template family; lexicon polarity; preferential-weight functional form) remain as thesis limitations.

---

## 7. What result would falsify each claim

See RQ table. Pass/fail is written from `artifacts/rqs.json` / `summary.json` into `reports/RESULTS.md`. Invented CI numbers are prohibited.

---

## 8. What a Master’s / early-PhD thesis can realistically deliver vs limitations

**Deliverable:** offline evaluation framework with locked protocol, construct-isolated generators, A/B/C+/D metrics, ≥960 belief cells, multi-round ecology, bootstrap CIs, RQ falsification table, and thesis notes linking GenFinTextEval as prior A/B/C baseline.

**Not delivered:** human-subject elicitation; live market causal estimates; trained sequence generators as primary engine; publisher-scale ecology; proof that computational personas equal investors; causal claims for Layer D.

See `reports/THESIS_NOTES.md` and `docs/ARCHITECTURE.md`.

---

## Generation typology (definitional)

| Type | Question |
|------|----------|
| Surface | Fluency / diversity? (secondary); Layer D separability |
| Epistemic | Does exposure change μ, confidence, disagreement? |
| Strategic | Do isolated persuasion cues change outcomes under fixed facts? |
| Ecological | Does mixing / multi-round reuse bias an index? |
