#!/usr/bin/env python3
"""Generate GitHub result tables from the pinned paper CSV."""

import argparse
import csv
import json
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
ROOT = PAPER.parent
START = "<!-- paper-results:start -->"
END = "<!-- paper-results:end -->"


def render():
    models = json.loads((PAPER / "config/models.json").read_text())
    names = {model["id"]: model["name"] for model in models}
    with (PAPER / "data/derived/main_results.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    by_key = {(row["model"], row["mode"]): row for row in rows}
    order = sorted(names, key=lambda model: -float(by_key[model, "agent"]["accuracy"]))
    summary = ["| Model variant | Agent accuracy ↑ | Baseline accuracy ↑ | Δ (pp) |",
               "| --- | ---: | ---: | ---: |"]
    for model in order:
        agent = float(by_key[model, "agent"]["accuracy"])
        baseline = float(by_key[model, "baseline"]["accuracy"])
        summary.append(f"| {names[model]} | {agent:.2f} | {baseline:.2f} | {agent-baseline:+.2f} |")
    readme = (ROOT / "README.md").read_text()
    before, rest = readme.split(START, 1)
    _, after = rest.split(END, 1)
    readme = before + START + "\n" + "\n".join(summary) + "\n" + END + after
    details = ["# Paper outcome metrics", "",
               "[Repository overview](../README.md) · [Metric definitions](benchmark.md) · [Reproduce these results](../paper/README.md)", "",
               "Generated from [`main_results.csv`](../paper/data/derived/main_results.csv). "
               "Every configuration uses the same 530 cases. Values are percentages (0–100); "
               "accuracy is stereochemistry-aware. Similarity and formula conservation use valid "
               "predictions as their denominator. RMSCE uses all predictions and is lower when "
               "confidence better tracks structural similarity.", ""]
    for mode in ("agent", "baseline"):
        details += [f"## {mode.title()}", "",
                    "| Model variant | Correct / 530 | Accuracy ↑ | Validity ↑ | Similarity ↑ | RMSCE ↓ | Formula conservation ↑ |",
                    "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for model in sorted(names, key=lambda key: -float(by_key[key, mode]["accuracy"])):
            row = by_key[model, mode]
            values = " | ".join(f"{float(row[field]):.2f}" for field in
                                ("accuracy", "validity", "similarity", "rmsce", "formula_conservation"))
            details.append(f"| {names[model]} | {row['correct']} / 530 | {values} |")
        details.append("")
    details += ["## Additional diagnostics", "",
                "- [Stereochemistry-agnostic accuracy](../paper/data/derived/stereo_results.csv)",
                "- [Run-level metrics](../paper/data/derived/run_metrics.csv)",
                "- [Trace-level metrics](../paper/data/derived/trace_metrics.csv)",
                "- [Dataset coverage](../paper/data/derived/dataset_audit.csv)",
                "- [Reconciliation audit](../paper/DATA_AUDIT.md)", "",
                "The paper snapshot is pinned to Overleaf commit `c99d3f0939ef16ae987a20bb709edb3f1a75433f`. "
                "These are recomputed outcomes from saved predictions; no model was rerun during reconciliation.", ""]
    return {ROOT / "README.md": readme, ROOT / "docs/results.md": "\n".join(details)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, content in render().items():
        if args.check:
            if not path.exists() or path.read_text() != content:
                raise SystemExit(f"Stale result table: {path.relative_to(ROOT)}")
        else:
            path.write_text(content)
    print("GitHub result tables agree with the paper CSV")


if __name__ == "__main__":
    main()
