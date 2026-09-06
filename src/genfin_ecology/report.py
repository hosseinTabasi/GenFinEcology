"""Build reports/RESULTS.md strictly from JSON artifacts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _load(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_results(root: Path | str) -> Path:
    root = Path(root)
    art = root / "artifacts"
    summary = _load(art / "summary.json")
    layer_a = _load(art / "layer_a.json")
    belief = _load(art / "belief.json")
    contamination = _load(art / "contamination.json")
    multiround = _load(art / "multiround.json")
    amp = _load(art / "amplification.json")
    detect = _load(art / "detectability.json")
    rqs = _load(art / "rqs.json")
    bootstrap = _load(art / "bootstrap.json")

    m = summary["means"]
    lines: list[str] = []
    lines.append("# GenFinEcology Results")
    lines.append("")
    lines.append(f"**Study ID:** `{summary['study_id']}`")
    lines.append(f"**Generated (UTC):** {summary['timestamp_utc']}")
    lines.append("")
    lines.append("All numbers below are read from `artifacts/*.json`. No invented values.")
    lines.append("")
    lines.append("## Study size")
    lines.append("")
    lines.append(f"- Events: **{summary['n_events']}**")
    lines.append(f"- Variants (ablations): **{summary['n_variants']}** — `{', '.join(summary['variants'])}`")
    lines.append(f"- Personas: **{summary['n_personas']}**")
    lines.append(f"- Seeds: **{summary['n_seeds']}**")
    lines.append(f"- Design: `{summary['design_formula']}`")
    lines.append(f"- Belief cells: **{summary['n_belief_cells']}**")
    lines.append(f"- Text cells: **{summary['n_text_cells']}**")
    lines.append("")
    lines.append("## RQ falsification (pre-registered)")
    lines.append("")
    for rq_id, rq in rqs.items():
        status = "PASS" if rq["pass"] else "FAIL"
        lines.append(f"### {rq_id}: **{status}**")
        lines.append("")
        lines.append(f"- Question: {rq['question']}")
        if rq_id == "RQ1":
            lines.append(f"- m1 = {rq['m1']}")
            lines.append(f"- Mean |Δμ| anchored = {rq['abs_delta_mu_anchored']}")
            lines.append(f"- Mean |Δμ| full_persuade = {rq['abs_delta_mu_full_persuade']}")
            lines.append(f"- Measured lift = **{rq['measured_lift']}**")
            ci = rq["bootstrap_ci"]
            lines.append(
                f"- Bootstrap (B={ci['B']}): mean={ci['mean']}, "
                f"95% CI [{ci['ci_low']}, {ci['ci_high']}]"
            )
        elif rq_id == "RQ2":
            lines.append(f"- m2 = {rq['m2']}")
            lines.append(f"- |Δμ| certainty_inflate = {rq['abs_delta_mu_certainty_inflate']}")
            lines.append(f"- |Δμ| num_drift = {rq['abs_delta_mu_num_drift']}")
            lines.append(f"- Measured diff = **{rq['measured_diff']}**")
            ci = rq["bootstrap_ci"]
            lines.append(
                f"- Bootstrap (B={ci['B']}): mean={ci['mean']}, "
                f"95% CI [{ci['ci_low']}, {ci['ci_high']}]"
            )
        elif rq_id == "RQ3":
            lines.append(f"- m3 = {rq['m3']}; R = {rq['R']}; ρ = {rq.get('rho')}")
            lines.append(f"- |multiround final bias| = {rq['abs_multiround_final_bias']}")
            lines.append(f"- |single-shot bias at same ρ| = {rq['abs_single_shot_bias_at_rho']}")
            lines.append(f"- Multiround slope (bias vs round) = {rq.get('mean_multiround_slope')}")
            lines.append(f"- Single-shot slope (bias vs ρ) = {rq.get('mean_single_shot_slope')}")
            lines.append(f"- Measured diff (final |bias| MR − SS) = **{rq['measured_diff']}**")
            ci = rq["bootstrap_ci"]
            lines.append(
                f"- Bootstrap (B={ci['B']}): mean={ci['mean']}, "
                f"95% CI [{ci['ci_low']}, {ci['ci_high']}]"
            )
        elif rq_id == "RQ4":
            lines.append(f"- m4 = {rq['m4']}; chance F1 = {rq['chance_f1']}")
            lines.append(f"- Held-out F1 = {rq['f1_test']}; accuracy = {rq['accuracy_test']}")
            lines.append(f"- Measured margin (F1 − chance) = **{rq['measured_margin']}**")
            lines.append(f"- Claim type: {rq.get('claim_type', 'descriptive')}")
        lines.append("")
    rs = summary["rq_summary"]
    lines.append(
        f"**RQ pass count:** {rs['n_pass']}/4 "
        f"(RQ1={rs['RQ1']}, RQ2={rs['RQ2']}, RQ3={rs['RQ3']}, RQ4={rs['RQ4']})"
    )
    lines.append("")
    lines.append("## Layer A — text (ablation manipulation check)")
    lines.append("")
    lines.append("| Variant | Faithfulness | Fabrication | Certainty | Hedge |")
    lines.append("|---|---:|---:|---:|---:|")
    for v, faith in m["mean_faithfulness_by_variant"].items():
        lines.append(
            f"| {v} | {faith} | {m['mean_fabrication_by_variant'][v]} | "
            f"{m['mean_certainty_by_variant'][v]} | {m['mean_hedge_by_variant'][v]} |"
        )
    lines.append("")
    lines.append(
        f"- Mean frame stability (Jaccard, paraphrase vs anchored): "
        f"**{m['mean_frame_stability_anchored_vs_paraphrase']}**"
    )
    lines.append("")
    lines.append("## Layer B — belief (by ablation)")
    lines.append("")
    lines.append("| Variant | Mean |Δμ| | Disagreement | WTA rate |")
    lines.append("|---|---:|---:|---:|")
    for v, dmu in m["abs_delta_mu_by_variant"].items():
        lines.append(
            f"| {v} | {dmu} | {m['mean_disagreement_by_variant'][v]} | "
            f"{m['willingness_rate_by_variant'][v]} |"
        )
    lines.append("")
    lines.append(
        f"- Belief lift (full_persuade − anchored): "
        f"**{m['belief_lift_full_persuade_minus_anchored']}**"
    )
    lines.append("")
    lines.append("## Layer C — single-shot contamination")
    lines.append("")
    lines.append(
        f"- Mean full_persuade contamination slope (bias vs ρ): "
        f"**{m['mean_persuade_contamination_slope']}**"
    )
    lines.append(
        f"- Mean anchored contamination slope: **{m['mean_anchored_contamination_slope']}**"
    )
    lines.append("")
    lines.append("### Contamination sweep (full_persuade contaminant)")
    lines.append("")
    lines.append("| Seed | ρ | Sentiment index | Bias vs ρ=0 | Slope |")
    lines.append("|---:|---:|---:|---:|---:|")
    for row in contamination:
        if row["contaminant"] != "full_persuade":
            continue
        lines.append(
            f"| {row['seed']} | {row['rho']} | {row['sentiment_index']} | "
            f"{row['bias_vs_rho0']} | {row['slope_bias_vs_rho']} |"
        )
    lines.append("")
    lines.append("## Layer C+ — multi-round ecological contamination")
    lines.append("")
    lines.append(f"- Mean multi-round slope (bias vs round): **{m['mean_multiround_slope']}**")
    lines.append("")
    lines.append("| Seed | Round | Sentiment index | Bias vs round0 | Mean reuse wt | Slope |")
    lines.append("|---:|---:|---:|---:|---:|---:|")
    for row in multiround:
        lines.append(
            f"| {row['seed']} | {row['round']} | {row['sentiment_index']} | "
            f"{row['bias_vs_round0']} | {row['mean_reuse_weight']} | {row['multiround_slope']} |"
        )
    lines.append("")
    lines.append("### Amplification / tail language")
    lines.append("")
    lines.append("| Seed | Mean reuse | Max reuse | Herfindahl | Tail frac (all) |")
    lines.append("|---:|---:|---:|---:|---:|")
    for row in amp:
        lines.append(
            f"| {row['seed']} | {row['mean_reuse']} | {row['max_reuse']} | "
            f"{row['reuse_herfindahl']} | {row['tail_language_fraction']} |"
        )
    lines.append("")
    lines.append("Tail language fraction by variant (mean across seeds):")
    lines.append("")
    for v, t in m["mean_tail_frac_by_variant"].items():
        lines.append(f"- `{v}`: **{t}**")
    lines.append("")
    lines.append("## Layer D — detectability (descriptive)")
    lines.append("")
    lines.append(f"- Train n = {detect['n_train']}; test n = {detect['n_test']}")
    lines.append(f"- Train events: {detect['train_events']}")
    lines.append(f"- Test events: {detect['test_events']}")
    lines.append(f"- Accuracy (train) = {detect.get('accuracy_train')}; F1 (train) = {detect.get('f1_train')}")
    lines.append(f"- Accuracy (held-out) = {detect.get('accuracy_test')}; F1 (held-out) = {detect.get('f1_test')}")
    lines.append(f"- Top strategic terms: {detect.get('top_strategic_terms', [])}")
    lines.append(f"- Top benign terms: {detect.get('top_benign_terms', [])}")
    lines.append("")
    lines.append("## Bootstrap summary")
    lines.append("")
    for key in ("belief_lift", "cert_minus_drift", "mr_minus_single_shot"):
        ci = bootstrap[key]
        lines.append(
            f"- `{key}`: mean={ci['mean']}, 95% CI [{ci['ci_low']}, {ci['ci_high']}] (B={ci['B']})"
        )
    lines.append("")
    lines.append("## Artifact paths")
    lines.append("")
    for name in (
        "summary.json", "texts.json", "layer_a.json", "belief.json",
        "contamination.json", "multiround.json", "amplification.json",
        "detectability.json", "bootstrap.json", "rqs.json",
    ):
        lines.append(f"- `artifacts/{name}`")
    lines.append("")
    lines.append(f"_Belief row count check: {len(belief)}; Layer A row count: {len(layer_a)}._")
    lines.append("")

    out = root / "reports" / "RESULTS.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    return out
