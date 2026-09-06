# Architecture: how GenFinEcology extends GenFinTextEval

**Author:** Hossein Tabasi

## Shared substrate

Both projects use:

- Verified USDT/USDC fact cards (`data/events/`)
- Lexicon-based Layer A features and computational persona Layer B update rule
- Deterministic template generation (no paid decoder required)
- Offline JSON artifacts → `RESULTS.md` only from JSON

GenFinEcology **copies** verified fact cards and lexicon files from the GenFinTextEval lineage; it does **not** invent new market statistics.

## New modules

| Module | Responsibility |
|--------|----------------|
| `generate.py` | Eight ablation generators (isolates + combined + paraphrase) |
| `metrics_detect.py` | Layer D: TF-IDF + logistic regression; event-held-out F1 |
| `metrics_system.py` | Adds `multiround_contamination` / `multiround_slope` (C+) |
| `bootstrap.py` | Event-level bootstrap percentile CIs |
| `run_study.py` | Factorial A/B/C+/D + RQ evaluation |
| `report.py` | RESULTS.md including ablation and RQ tables |

## Data flow

```
fact cards → ablation texts → Layer A features
                           → Layer B persona updates (960 cells)
                           → Layer C ρ sweep + Layer C+ R rounds
                           → Layer D classifier (8/2 event split)
                           → bootstrap over events
                           → RQ pass/fail → artifacts/*.json → RESULTS.md
```

## Design N

`10 events × 8 variants × 4 personas × 3 seeds = 960` belief cells.

## Non-goals relative to GenFinTextEval

GenFinEcology does not deprecate GenFinTextEval. The earlier repo remains the smaller A/B/C blob-persuade baseline. Cross-repo claim conflation is prohibited.
