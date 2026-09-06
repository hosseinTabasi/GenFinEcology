# GenFinEcology

**Author:** Hossein Tabasi (`hosseinTabasi`)  
**License:** MIT  
**Python:** 3.11+

Feature-ablation ecology for generative financial text: construct-isolated rewrites, computational belief updates, multi-round corpus contamination, surface detectability, and bootstrap CIs — offline and deterministic after install.

Fact cards cover **USDT / USDC** events (sourced, verified). No module places live posts or executes trades. Outputs are **not investment advice**.

## Standalone install and run

```bash
cd GenFinEcology
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
python -m genfin_ecology run
python -m genfin_ecology report
python -m genfin_ecology demo
```

Optional UI:

```bash
pip install -e ".[app]"
streamlit run app/streamlit_app.py
```

## What is new vs GenFinTextEval

This project **installs and runs standalone**. GenFinTextEval (same author) is an optional prior **A/B/C baseline** with blob persuade variants. GenFinEcology adds substantial science:

| Addition | Role |
|----------|------|
| Feature ablations | Isolate `num_drift`, `authority_cues`, `certainty_inflate`, `omission`, plus combined `full_persuade_*` and `paraphrase` |
| Layer D | TF-IDF + logistic regression detectability; held-out event transfer |
| Layer C+ | R=3 multi-round preferential reuse contamination |
| Bootstrap | B≥200 event resamples; 95% percentile CIs from actual draws |
| Multiple RQs | Pre-registered falsification thresholds in `PROTOCOL.md` / `config/study.yaml` |
| Scale | 10×8×4×3 = **960** belief cells |

## Layers

- **A Text** — faithfulness, fabrication, hedge/certainty, frame stability  
- **B Belief** — computational personas, Δμ, disagreement, willingness-to-act  
- **C System** — single-shot contamination vs ρ  
- **C+ Ecology** — multi-round sentiment path and slope  
- **D Detectability** — descriptive surface classifier (not causal)

## Study design (locked)

- Events: E01–E10 (`data/events/`)  
- Variants: 8 ablations (`config/study.yaml`)  
- Personas: 4 (`data/personas.yaml`)  
- Seeds: 3  
- Layer D split: train E01–E08 / test E09–E10  

See **`PROTOCOL.md`** for the eight-section supervisor contract, ablation table, and RQ falsification table.

## Repository layout

```
GenFinEcology/
  PROTOCOL.md README.md LICENSE
  config/study.yaml
  data/events/ data/personas.yaml data/lexicons/
  src/genfin_ecology/
  tests/ artifacts/ reports/
  docs/ examples/ app/
```

## Claim discipline

Every claim is labeled **definitional / descriptive / causal / speculative**. Identification threats (event confounding, template sensitivity, treatment–outcome contamination; judge circularity N/A) are named in the protocol.

## Ethics

See `docs/SECURITY_ETHICS.md`. Persuasion and fabricated-authority strings are experimental treatments, not content to publish as news.
