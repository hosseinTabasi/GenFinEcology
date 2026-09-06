"""CLI: python -m genfin_ecology run | report | demo"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def cmd_run(args: argparse.Namespace) -> int:
    from genfin_ecology.run_study import run_study

    root = Path(args.root) if args.root else _repo_root()
    summary = run_study(root)
    print(json.dumps({
        "n_belief_cells": summary["n_belief_cells"],
        "design_formula": summary["design_formula"],
        "rq_summary": summary["rq_summary"],
        "belief_lift": summary["rqs"]["RQ1"]["measured_lift"],
        "f1_test": summary["detectability"].get("f1_test"),
    }, indent=2))
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    from genfin_ecology.report import write_results

    root = Path(args.root) if args.root else _repo_root()
    out = write_results(root)
    print(f"Wrote {out}")
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    from genfin_ecology.factcard import load_all_events
    from genfin_ecology.generate import ABLATION_VARIANTS, generate_variant
    from genfin_ecology.metrics_text import layer_a_metrics

    root = Path(args.root) if args.root else _repo_root()
    events = load_all_events(root / "data" / "events")
    card = events[0]
    for v in ABLATION_VARIANTS:
        text = generate_variant(card, v, seed=20260311)
        a = layer_a_metrics(text, card, root / "data" / "lexicons", paraphrase_text=None)
        print(f"=== {card['event_id']} / {v} ===")
        print(text[:420] + ("..." if len(text) > 420 else ""))
        print({
            k: a[k]
            for k in (
                "numerical_faithfulness",
                "source_fabrication_count",
                "certainty_score",
                "hedge_ratio",
            )
        })
        print()
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="genfin_ecology", description="GenFinEcology CLI")
    p.add_argument("--root", default=None, help="Repository root (default: auto)")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="Run full study → artifacts/")
    r.set_defaults(func=cmd_run)

    rep = sub.add_parser("report", help="Write reports/RESULTS.md from artifacts")
    rep.set_defaults(func=cmd_report)

    d = sub.add_parser("demo", help="Print one-event ablation texts and Layer A scores")
    d.set_defaults(func=cmd_demo)

    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
