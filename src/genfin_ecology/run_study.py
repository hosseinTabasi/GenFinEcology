"""Full factorial study runner → JSON artifacts (A/B/C+/D + bootstrap + RQs)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from genfin_ecology.bootstrap import bootstrap_over_events
from genfin_ecology.extract import load_lexicon
from genfin_ecology.factcard import load_all_events
from genfin_ecology.generate import generate_variant
from genfin_ecology.metrics_belief import (
    authority_cue,
    disagreement,
    load_personas,
    text_polarity,
    update_belief,
    willingness_to_act,
)
from genfin_ecology.metrics_detect import run_detectability
from genfin_ecology.metrics_system import (
    amplification_proxy,
    build_baseline_corpus,
    contamination_slope,
    contamination_sweep,
    multiround_contamination,
    multiround_slope,
    tail_language_fraction,
)
from genfin_ecology.metrics_text import layer_a_metrics


def load_config(path: Path | str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def run_study(root: Path | str, config_path: Path | str | None = None) -> dict[str, Any]:
    root = Path(root)
    cfg = load_config(config_path or root / "config" / "study.yaml")
    events = load_all_events(root / cfg["paths"]["events_dir"])
    personas = load_personas(root / cfg["paths"]["personas"])
    lex_dir = root / cfg["paths"]["lexicons_dir"]
    seeds = list(cfg["seeds"])
    variants = list(cfg["variants"])
    eps = float(cfg["num_epsilon"])
    tau = float(cfg["willingness_tau"])
    kappa = float(cfg["willingness_kappa"])
    rho_grid = list(cfg["contamination_rho"])
    art_dir = root / cfg["paths"]["artifacts_dir"]
    art_dir.mkdir(parents=True, exist_ok=True)

    texts_rows: list[dict[str, Any]] = []
    belief_rows: list[dict[str, Any]] = []
    layer_a_rows: list[dict[str, Any]] = []
    text_store: dict[tuple[str, str, int], str] = {}

    for seed in seeds:
        for card in events:
            eid = card["event_id"]
            local: dict[str, str] = {}
            for v in variants:
                local[v] = generate_variant(card, v, seed)
                text_store[(eid, v, seed)] = local[v]
                texts_rows.append({
                    "event_id": eid,
                    "variant": v,
                    "seed": seed,
                    "text": local[v],
                })
            for v in variants:
                para = None
                if v == "paraphrase":
                    para = local.get("anchored")
                elif v == "anchored":
                    para = local.get("paraphrase")
                a = layer_a_metrics(local[v], card, lex_dir, eps=eps, paraphrase_text=para)
                layer_a_rows.append({"event_id": eid, "variant": v, "seed": seed, **a})

                pol = text_polarity(local[v], lex_dir)
                auth = authority_cue(local[v], lex_dir, int(a["source_fabrication_count"]))
                mu_after: list[float] = []
                for persona in personas:
                    b = update_belief(persona, a, pol, auth)
                    wta = willingness_to_act(float(b["delta_mu"]), float(b["c1"]), tau, kappa)
                    belief_rows.append({
                        "event_id": eid,
                        "variant": v,
                        "seed": seed,
                        **b,
                        "willingness_to_act": wta,
                        "unit": f"{persona['id']}×{eid}×{v}",
                    })
                    mu_after.append(float(b["mu1"]))
                d = disagreement(mu_after)
                for row_b in belief_rows[-len(personas):]:
                    row_b["cross_persona_disagreement"] = round(d, 6)

    # Layer C: single-shot contamination + C+ multi-round
    bull = load_lexicon(lex_dir / "polarity_bull.txt")
    bear = load_lexicon(lex_dir / "polarity_bear.txt")
    crash = load_lexicon(lex_dir / "crash.txt")
    mr_cfg = cfg["multiround"]
    R = int(mr_cfg["R"])
    mr_rho = float(mr_cfg["rho"])
    pref_boost = float(mr_cfg.get("preferential_boost", 1.5))

    contamination_rows: list[dict[str, Any]] = []
    multiround_rows: list[dict[str, Any]] = []
    amp_rows: list[dict[str, Any]] = []

    combined_persuade = ("full_persuade_bull", "full_persuade_bear")

    for seed in seeds:
        baseline = build_baseline_corpus(seed, int(cfg["baseline_corpus_size"]), bull, bear)
        synth = [
            text_store[(c["event_id"], v, seed)]
            for c in events for v in combined_persuade
        ]
        anchored_texts = [text_store[(c["event_id"], "anchored", seed)] for c in events]
        for label, bag in (("full_persuade", synth), ("anchored", anchored_texts)):
            sweep = contamination_sweep(baseline, bag, rho_grid, bull, bear, seed)
            slope = contamination_slope(sweep)
            for srow in sweep:
                contamination_rows.append({
                    "seed": seed,
                    "contaminant": label,
                    **srow,
                    "slope_bias_vs_rho": round(slope, 6),
                })

        # Multi-round C+ for full_persuade synthetics
        path = multiround_contamination(
            baseline, synth, R, mr_rho, bull, bear, seed, preferential_boost=pref_boost
        )
        mr_slope = multiround_slope(path)
        for prow in path:
            multiround_rows.append({
                "seed": seed,
                "contaminant": "full_persuade",
                **prow,
                "multiround_slope": round(mr_slope, 6),
                "fixed_rho": mr_rho,
                "R": R,
            })

        all_texts = [text_store[(c["event_id"], v, seed)] for c in events for v in variants]
        amp = amplification_proxy(all_texts, seed)
        amp["seed"] = seed
        amp["tail_language_fraction"] = round(tail_language_fraction(all_texts, crash), 6)
        for v in variants:
            vt = [text_store[(c["event_id"], v, seed)] for c in events]
            amp[f"tail_frac_{v}"] = round(tail_language_fraction(vt, crash), 6)
        amp_rows.append(amp)

    # Layer D: detectability
    det_cfg = cfg["detectability"]
    detect = run_detectability(
        texts_rows,
        train_events=list(det_cfg["train_events"]),
        test_events=list(det_cfg["test_events"]),
        benign_variants=list(det_cfg["benign_variants"]),
        strategic_variants=list(det_cfg["strategic_variants"]),
        seed=int(cfg["bootstrap"]["seed"]),
    )

    # Aggregates by variant
    def mean_abs_dmu(variant: str, event_filter: list[str] | None = None) -> float:
        xs = []
        for r in belief_rows:
            if r["variant"] != variant:
                continue
            if event_filter is not None and r["event_id"] not in event_filter:
                continue
            xs.append(abs(float(r["delta_mu"])))
        return _mean(xs)

    def mean_abs_dmu_pool(vs: tuple[str, ...], event_filter: list[str] | None = None) -> float:
        xs = []
        for r in belief_rows:
            if r["variant"] not in vs:
                continue
            if event_filter is not None and r["event_id"] not in event_filter:
                continue
            xs.append(abs(float(r["delta_mu"])))
        return _mean(xs)

    event_ids = [c["event_id"] for c in events]
    abs_by_variant = {v: mean_abs_dmu(v) for v in variants}
    anchored_abs = abs_by_variant["anchored"]
    full_persuade_abs = mean_abs_dmu_pool(combined_persuade)
    cert_abs = abs_by_variant.get("certainty_inflate", 0.0)
    drift_abs = abs_by_variant.get("num_drift", 0.0)

    # Single-shot slopes
    slope_by_seed_persuade: dict[int, float] = {}
    slope_by_seed_anchored: dict[int, float] = {}
    for r in contamination_rows:
        if r["contaminant"] == "full_persuade":
            slope_by_seed_persuade[r["seed"]] = float(r["slope_bias_vs_rho"])
        elif r["contaminant"] == "anchored":
            slope_by_seed_anchored[r["seed"]] = float(r["slope_bias_vs_rho"])
    mean_persuade_slope = _mean(list(slope_by_seed_persuade.values()))
    mean_anchored_slope = _mean(list(slope_by_seed_anchored.values()))

    # Multi-round slopes
    mr_slope_by_seed: dict[int, float] = {}
    for r in multiround_rows:
        mr_slope_by_seed[r["seed"]] = float(r["multiround_slope"])
    mean_mr_slope = _mean(list(mr_slope_by_seed.values()))

    # --- Bootstrap CIs ---
    boot_cfg = cfg["bootstrap"]
    B = int(boot_cfg["B"])
    boot_seed = int(boot_cfg["seed"])

    def _belief_lift_for_events(eids: list[str]) -> float:
        pers = mean_abs_dmu_pool(combined_persuade, eids)
        anc = mean_abs_dmu("anchored", eids)
        return pers - anc

    def _cert_minus_drift_for_events(eids: list[str]) -> float:
        return mean_abs_dmu("certainty_inflate", eids) - mean_abs_dmu("num_drift", eids)

    def _mr_minus_single_for_events(eids: list[str]) -> float:
        # Compare |final multiround bias| vs |single-shot bias at same ρ|.
        mr_biases = []
        ss_biases = []
        for seed in seeds:
            baseline = build_baseline_corpus(seed, int(cfg["baseline_corpus_size"]), bull, bear)
            synth = [
                text_store[(eid, v, seed)]
                for eid in eids for v in combined_persuade
                if (eid, v, seed) in text_store
            ]
            if not synth:
                continue
            path = multiround_contamination(
                baseline, synth, R, mr_rho, bull, bear, seed, preferential_boost=pref_boost
            )
            mr_biases.append(abs(float(path[-1]["bias_vs_round0"])))
            sweep = contamination_sweep(baseline, synth, [0.0, mr_rho], bull, bear, seed)
            # bias at mr_rho (second row)
            ss_row = next(r for r in sweep if abs(float(r["rho"]) - mr_rho) < 1e-12)
            ss_biases.append(abs(float(ss_row["bias_vs_rho0"])))
        return _mean(mr_biases) - _mean(ss_biases)

    boot_belief_lift = bootstrap_over_events(
        event_ids, _belief_lift_for_events, B=B, seed=boot_seed, tag="belief_lift"
    )
    boot_cert_vs_drift = bootstrap_over_events(
        event_ids, _cert_minus_drift_for_events, B=B, seed=boot_seed, tag="cert_vs_drift"
    )
    boot_mr_vs_ss = bootstrap_over_events(
        event_ids, _mr_minus_single_for_events, B=B, seed=boot_seed, tag="mr_vs_ss"
    )

    # --- RQ falsification ---
    fals = cfg["falsification"]
    m1 = float(fals["m1"])
    m2 = float(fals["m2"])
    m3 = float(fals["m3"])
    m4 = float(fals["m4"])
    chance_f1 = float(fals["chance_f1"])

    belief_lift = full_persuade_abs - anchored_abs
    cert_minus_drift = cert_abs - drift_abs
    # RQ3 operationalization: |bias after R rounds at ρ| vs |single-shot bias at same ρ|
    mr_final_biases = []
    ss_same_rho_biases = []
    for seed in seeds:
        finals = [float(r["bias_vs_round0"]) for r in multiround_rows
                  if r["seed"] == seed and r["round"] == R]
        if finals:
            mr_final_biases.append(abs(finals[0]))
        ss_rows = [float(r["bias_vs_rho0"]) for r in contamination_rows
                   if r["seed"] == seed and r["contaminant"] == "full_persuade"
                   and abs(float(r["rho"]) - mr_rho) < 1e-12]
        if ss_rows:
            ss_same_rho_biases.append(abs(ss_rows[0]))
    mean_mr_final_bias = _mean(mr_final_biases)
    mean_ss_same_rho_bias = _mean(ss_same_rho_biases)
    abs_mr = mean_mr_final_bias
    abs_ss = mean_ss_same_rho_bias
    mr_minus_ss = abs_mr - abs_ss
    f1_test = detect.get("f1_test")
    f1_test_val = float(f1_test) if f1_test is not None else 0.0
    f1_margin = f1_test_val - chance_f1

    rq1_pass = belief_lift >= m1
    rq2_pass = cert_minus_drift > m2
    rq3_pass = mr_minus_ss > m3
    rq4_pass = f1_margin >= m4

    rqs = {
        "RQ1": {
            "question": "Do combined persuade variants increase mean |Δμ| vs anchored by margin m1?",
            "m1": m1,
            "measured_lift": round(belief_lift, 6),
            "abs_delta_mu_anchored": round(anchored_abs, 6),
            "abs_delta_mu_full_persuade": round(full_persuade_abs, 6),
            "pass": rq1_pass,
            "bootstrap_ci": boot_belief_lift,
        },
        "RQ2": {
            "question": "Does certainty_inflate alone move |Δμ| more than num_drift alone?",
            "m2": m2,
            "abs_delta_mu_certainty_inflate": round(cert_abs, 6),
            "abs_delta_mu_num_drift": round(drift_abs, 6),
            "measured_diff": round(cert_minus_drift, 6),
            "pass": rq2_pass,
            "bootstrap_ci": boot_cert_vs_drift,
        },
        "RQ3": {
            "question": (
                "Is |bias| after R multi-round preferential-reuse steps steeper "
                "(larger) than single-shot mix at the same ρ?"
            ),
            "m3": m3,
            "R": R,
            "rho": mr_rho,
            "abs_multiround_final_bias": round(abs_mr, 6),
            "abs_single_shot_bias_at_rho": round(abs_ss, 6),
            "mean_multiround_slope": round(mean_mr_slope, 6),
            "mean_single_shot_slope": round(mean_persuade_slope, 6),
            "measured_diff": round(mr_minus_ss, 6),
            "pass": rq3_pass,
            "bootstrap_ci": boot_mr_vs_ss,
        },
        "RQ4": {
            "question": "Does detectability F1 on held-out events exceed chance by margin m4?",
            "m4": m4,
            "chance_f1": chance_f1,
            "f1_test": detect.get("f1_test"),
            "accuracy_test": detect.get("accuracy_test"),
            "measured_margin": round(f1_margin, 6),
            "pass": rq4_pass,
            "claim_type": "descriptive",
        },
    }

    summary = {
        "study_id": cfg["study_id"],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "n_events": len(events),
        "n_variants": len(variants),
        "n_personas": len(personas),
        "n_seeds": len(seeds),
        "n_belief_cells": len(belief_rows),
        "n_text_cells": len(texts_rows),
        "design_formula": (
            f"{len(events)} events × {len(variants)} variants × "
            f"{len(personas)} personas × {len(seeds)} seeds = {len(belief_rows)}"
        ),
        "variants": variants,
        "means": {
            "abs_delta_mu_by_variant": {v: round(abs_by_variant[v], 6) for v in variants},
            "abs_delta_mu_anchored": round(anchored_abs, 6),
            "abs_delta_mu_full_persuade": round(full_persuade_abs, 6),
            "belief_lift_full_persuade_minus_anchored": round(belief_lift, 6),
            "mean_persuade_contamination_slope": round(mean_persuade_slope, 6),
            "mean_anchored_contamination_slope": round(mean_anchored_slope, 6),
            "mean_multiround_slope": round(mean_mr_slope, 6),
            "mean_multiround_final_abs_bias": round(mean_mr_final_bias, 6),
            "mean_single_shot_abs_bias_at_mr_rho": round(mean_ss_same_rho_bias, 6),
            "mean_faithfulness_by_variant": {
                v: round(_mean([float(r["numerical_faithfulness"]) for r in layer_a_rows if r["variant"] == v]), 6)
                for v in variants
            },
            "mean_fabrication_by_variant": {
                v: round(_mean([float(r["source_fabrication_count"]) for r in layer_a_rows if r["variant"] == v]), 6)
                for v in variants
            },
            "mean_certainty_by_variant": {
                v: round(_mean([float(r["certainty_score"]) for r in layer_a_rows if r["variant"] == v]), 6)
                for v in variants
            },
            "mean_hedge_by_variant": {
                v: round(_mean([float(r["hedge_ratio"]) for r in layer_a_rows if r["variant"] == v]), 6)
                for v in variants
            },
            "mean_frame_stability_anchored_vs_paraphrase": round(
                _mean([
                    float(r["frame_stability_jaccard"])
                    for r in layer_a_rows
                    if r["variant"] == "paraphrase" and "frame_stability_jaccard" in r
                ]),
                6,
            ),
            "mean_disagreement_by_variant": {
                v: round(_mean([float(r["cross_persona_disagreement"]) for r in belief_rows if r["variant"] == v]), 6)
                for v in variants
            },
            "willingness_rate_by_variant": {
                v: round(_mean([1.0 if r["willingness_to_act"] else 0.0 for r in belief_rows if r["variant"] == v]), 6)
                for v in variants
            },
            "mean_tail_frac_by_variant": {
                v: round(_mean([float(r.get(f"tail_frac_{v}", 0.0)) for r in amp_rows]), 6)
                for v in variants
            },
        },
        "detectability": detect,
        "bootstrap": {
            "B": B,
            "belief_lift": boot_belief_lift,
            "cert_minus_drift": boot_cert_vs_drift,
            "mr_minus_single_shot": boot_mr_vs_ss,
        },
        "rqs": rqs,
        "rq_summary": {
            "RQ1": rq1_pass,
            "RQ2": rq2_pass,
            "RQ3": rq3_pass,
            "RQ4": rq4_pass,
            "n_pass": int(rq1_pass) + int(rq2_pass) + int(rq3_pass) + int(rq4_pass),
        },
    }

    artifacts = {
        "summary.json": summary,
        "texts.json": texts_rows,
        "layer_a.json": layer_a_rows,
        "belief.json": belief_rows,
        "contamination.json": contamination_rows,
        "multiround.json": multiround_rows,
        "amplification.json": amp_rows,
        "detectability.json": detect,
        "bootstrap.json": summary["bootstrap"],
        "rqs.json": rqs,
    }
    for name, obj in artifacts.items():
        (art_dir / name).write_text(json.dumps(obj, indent=2), encoding="utf-8")

    return summary
