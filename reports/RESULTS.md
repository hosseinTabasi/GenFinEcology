# GenFinEcology Results

**Study ID:** `genfin_ecology_v1`
**Generated (UTC):** 2026-09-06T17:00:07.104379+00:00

All numbers below are read from `artifacts/*.json`. No invented values.

## Study size

- Events: **10**
- Variants (ablations): **8** — `anchored, num_drift, authority_cues, certainty_inflate, omission, full_persuade_bull, full_persuade_bear, paraphrase`
- Personas: **4**
- Seeds: **3**
- Design: `10 events × 8 variants × 4 personas × 3 seeds = 960`
- Belief cells: **960**
- Text cells: **240**

## RQ falsification (pre-registered)

### RQ1: **PASS**

- Question: Do combined persuade variants increase mean |Δμ| vs anchored by margin m1?
- m1 = 0.03
- Mean |Δμ| anchored = 0.111919
- Mean |Δμ| full_persuade = 0.204659
- Measured lift = **0.09274**
- Bootstrap (B=200): mean=0.092552, 95% CI [0.075344, 0.106918]

### RQ2: **PASS**

- Question: Does certainty_inflate alone move |Δμ| more than num_drift alone?
- m2 = 0.0
- |Δμ| certainty_inflate = 0.114285
- |Δμ| num_drift = 0.108198
- Measured diff = **0.006087**
- Bootstrap (B=200): mean=0.006338, 95% CI [-0.007969, 0.017843]

### RQ3: **PASS**

- Question: Is |bias| after R multi-round preferential-reuse steps steeper (larger) than single-shot mix at the same ρ?
- m3 = 0.0; R = 3; ρ = 0.25
- |multiround final bias| = 0.327889
- |single-shot bias at same ρ| = 0.035972
- Multiround slope (bias vs round) = -0.111961
- Single-shot slope (bias vs ρ) = -0.174141
- Measured diff (final |bias| MR − SS) = **0.291917**
- Bootstrap (B=200): mean=0.298236, 95% CI [0.264861, 0.318333]

### RQ4: **PASS**

- Question: Does detectability F1 on held-out events exceed chance by margin m4?
- m4 = 0.15; chance F1 = 0.5
- Held-out F1 = 0.857143; accuracy = 0.75
- Measured margin (F1 − chance) = **0.357143**
- Claim type: descriptive

**RQ pass count:** 4/4 (RQ1=True, RQ2=True, RQ3=True, RQ4=True)

## Layer A — text (ablation manipulation check)

| Variant | Faithfulness | Fabrication | Certainty | Hedge |
|---|---:|---:|---:|---:|
| anchored | 0.975 | 0.0 | 0.014286 | 0.077638 |
| num_drift | 0.941667 | 0.0 | 0.011111 | 0.065589 |
| authority_cues | 0.975 | 2.0 | 0.011111 | 0.063367 |
| certainty_inflate | 0.975 | 0.0 | 0.348253 | 0.058203 |
| omission | 0.770079 | 0.0 | 0.005556 | 0.058365 |
| full_persuade_bull | 0.739127 | 1.0 | 0.485761 | 0.041353 |
| full_persuade_bear | 0.81123 | 1.0 | 0.189837 | 0.132059 |
| paraphrase | 0.975 | 0.0 | 0.014286 | 0.077638 |

- Mean frame stability (Jaccard, paraphrase vs anchored): **0.991575**

## Layer B — belief (by ablation)

| Variant | Mean |Δμ| | Disagreement | WTA rate |
|---|---:|---:|---:|
| anchored | 0.111919 | 0.102403 | 0.566667 |
| num_drift | 0.108198 | 0.099938 | 0.55 |
| authority_cues | 0.201158 | 0.069177 | 0.658333 |
| certainty_inflate | 0.114285 | 0.085085 | 0.566667 |
| omission | 0.093209 | 0.088217 | 0.441667 |
| full_persuade_bull | 0.265283 | 0.079371 | 0.708333 |
| full_persuade_bear | 0.144035 | 0.121615 | 0.433333 |
| paraphrase | 0.111919 | 0.102403 | 0.566667 |

- Belief lift (full_persuade − anchored): **0.09274**

## Layer C — single-shot contamination

- Mean full_persuade contamination slope (bias vs ρ): **-0.174141**
- Mean anchored contamination slope: **-0.047965**

### Contamination sweep (full_persuade contaminant)

| Seed | ρ | Sentiment index | Bias vs ρ=0 | Slope |
|---:|---:|---:|---:|---:|
| 20260311 | 0.0 | 0.125 | 0.0 | -0.189254 |
| 20260311 | 0.1 | 0.0825 | -0.0425 | -0.189254 |
| 20260311 | 0.25 | 0.09625 | -0.02875 | -0.189254 |
| 20260311 | 0.5 | -0.000833 | -0.125833 | -0.189254 |
| 20260311 | 0.75 | -0.012917 | -0.137917 | -0.189254 |
| 20260813 | 0.0 | 0.203333 | 0.0 | -0.161966 |
| 20260813 | 0.1 | 0.188667 | -0.014667 | -0.161966 |
| 20260813 | 0.25 | 0.127667 | -0.075667 | -0.161966 |
| 20260813 | 0.5 | 0.096667 | -0.106667 | -0.161966 |
| 20260813 | 0.75 | 0.087667 | -0.115667 | -0.161966 |
| 20260101 | 0.0 | 0.145 | 0.0 | -0.171204 |
| 20260101 | 0.1 | 0.154917 | 0.009917 | -0.171204 |
| 20260101 | 0.25 | 0.1485 | 0.0035 | -0.171204 |
| 20260101 | 0.5 | 0.102917 | -0.042083 | -0.171204 |
| 20260101 | 0.75 | 0.01975 | -0.12525 | -0.171204 |

## Layer C+ — multi-round ecological contamination

- Mean multi-round slope (bias vs round): **-0.111961**

| Seed | Round | Sentiment index | Bias vs round0 | Mean reuse wt | Slope |
|---:|---:|---:|---:|---:|---:|
| 20260311 | 0 | 0.125 | 0.0 | 1.0 | -0.105792 |
| 20260311 | 1 | 0.024583 | -0.100417 | 3.5 | -0.105792 |
| 20260311 | 2 | -0.100833 | -0.225833 | 6.0 | -0.105792 |
| 20260311 | 3 | -0.185833 | -0.310833 | 8.5 | -0.105792 |
| 20260813 | 0 | 0.203333 | 0.0 | 1.0 | -0.158167 |
| 20260813 | 1 | 0.064667 | -0.138667 | 3.5 | -0.158167 |
| 20260813 | 2 | -0.093 | -0.296333 | 6.0 | -0.158167 |
| 20260813 | 3 | -0.271333 | -0.474667 | 8.5 | -0.158167 |
| 20260101 | 0 | 0.145 | 0.0 | 1.0 | -0.071925 |
| 20260101 | 1 | 0.111083 | -0.033917 | 3.5 | -0.071925 |
| 20260101 | 2 | -0.013667 | -0.158667 | 6.0 | -0.071925 |
| 20260101 | 3 | -0.053167 | -0.198167 | 8.5 | -0.071925 |

### Amplification / tail language

| Seed | Mean reuse | Max reuse | Herfindahl | Tail frac (all) |
|---:|---:|---:|---:|---:|
| 20260311 | 0.1 | 2.0 | 0.15625 | 0.2625 |
| 20260813 | 0.1 | 2.0 | 0.15625 | 0.2625 |
| 20260101 | 0.1 | 2.0 | 0.15625 | 0.2625 |

Tail language fraction by variant (mean across seeds):

- `anchored`: **0.2**
- `num_drift`: **0.2**
- `authority_cues`: **0.2**
- `certainty_inflate`: **0.2**
- `omission`: **0.1**
- `full_persuade_bull`: **0.0**
- `full_persuade_bear`: **1.0**
- `paraphrase`: **0.2**

## Layer D — detectability (descriptive)

- Train n = 192; test n = 48
- Train events: ['E01', 'E02', 'E03', 'E04', 'E05', 'E06', 'E07', 'E08']
- Test events: ['E09', 'E10']
- Accuracy (train) = 0.75; F1 (train) = 0.857143
- Accuracy (held-out) = 0.75; F1 (held-out) = 0.857143
- Top strategic terms: ['figures include', 'reported figures', 'highlighted', 'selective', 'selected facts', 'selected', 'highlighted figures', 'selective summary']
- Top benign terms: ['card constrained', 'is fact', 'this summary', 'constrained and', 'constrained', 'and not', 'fact card', 'fact']

## Bootstrap summary

- `belief_lift`: mean=0.092552, 95% CI [0.075344, 0.106918] (B=200)
- `cert_minus_drift`: mean=0.006338, 95% CI [-0.007969, 0.017843] (B=200)
- `mr_minus_single_shot`: mean=0.298236, 95% CI [0.264861, 0.318333] (B=200)

## Artifact paths

- `artifacts/summary.json`
- `artifacts/texts.json`
- `artifacts/layer_a.json`
- `artifacts/belief.json`
- `artifacts/contamination.json`
- `artifacts/multiround.json`
- `artifacts/amplification.json`
- `artifacts/detectability.json`
- `artifacts/bootstrap.json`
- `artifacts/rqs.json`

_Belief row count check: 960; Layer A row count: 240._
