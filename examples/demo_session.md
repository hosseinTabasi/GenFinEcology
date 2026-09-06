# Demo session

```bash
pip install -e ".[dev]"
python -m genfin_ecology demo
```

Expected: eight ablation blocks for E01 with Layer A scores (faithfulness, fabrication, certainty, hedge).

```bash
python -m genfin_ecology run
python -m genfin_ecology report
```

Inspect `artifacts/summary.json` and `reports/RESULTS.md` for RQ pass/fail and exact belief-cell N.
