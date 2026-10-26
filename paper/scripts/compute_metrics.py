#!/usr/bin/env python3
"""Compute every numeric table input from the common-530 paper snapshot."""

from __future__ import annotations

import bisect
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

PAPER_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = PAPER_ROOT / "data" / "snapshots" / "predictions_common530.jsonl"
DERIVED = PAPER_ROOT / "data" / "derived"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return float(statistics.mean(values)) if values else 0.0


def rmsce(rows: list[dict[str, Any]], bins: int) -> float:
    boundaries = [i / bins for i in range(bins + 1)]
    grouped: dict[int, list[tuple[float, float]]] = defaultdict(list)
    for row in rows:
        confidence = min(1.0, max(0.0, float(row.get("confidence") or 0.0)))
        similarity = float(row.get("similarity") or 0.0) if row.get("valid") else 0.0
        # Equal-width bins follow ((m - 1) / M, m / M], with confidence 0
        # included in the first bin rather than forming an extra group.
        bin_index = max(1, bisect.bisect_left(boundaries, confidence))
        grouped[bin_index].append((confidence, similarity))
    total = len(rows)
    error = 0.0
    for pairs in grouped.values():
        avg_confidence = mean(pair[0] for pair in pairs)
        avg_similarity = mean(pair[1] for pair in pairs)
        error += len(pairs) / total * (avg_similarity - avg_confidence) ** 2
    return math.sqrt(error)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    protocol = load_json(PAPER_ROOT / "config" / "metric_protocol.json")
    models = load_json(PAPER_ROOT / "config" / "models.json")
    expected = int(protocol["expected_samples_per_configuration"])
    with SNAPSHOT.open(encoding="utf-8") as handle:
        snapshot = [json.loads(line) for line in handle if line.strip()]

    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in snapshot:
        groups[(row["model"], row["mode"])].append(row)

    main_rows: list[dict[str, Any]] = []
    stereo_rows: list[dict[str, Any]] = []
    run_rows: list[dict[str, Any]] = []
    for model in models:
        model_id = model["id"]
        for mode in ("agent", "baseline"):
            rows = groups[(model_id, mode)]
            uuids = {row["uuid"] for row in rows}
            if len(rows) != expected or len(uuids) != expected:
                raise RuntimeError(f"{mode}/{model_id}: expected {expected} unique rows, found {len(rows)}/{len(uuids)}")
            valid_rows = [row for row in rows if row["valid"]]
            correct = sum(bool(row["match"]) for row in rows)
            valid = len(valid_rows)
            formula_matches = sum(bool(row["formula_match"]) for row in valid_rows)
            stereo_correct = sum(bool(row["stereo_agnostic_match"]) for row in rows)
            main_rows.append(
                {
                    "model": model_id,
                    "mode": mode,
                    "samples": len(rows),
                    "correct": correct,
                    "valid": valid,
                    "formula_matches": formula_matches,
                    "accuracy": round(correct / len(rows) * 100, 4),
                    "validity": round(valid / len(rows) * 100, 4),
                    "similarity": round(mean(float(row["similarity"]) for row in valid_rows) * 100, 4),
                    "rmsce": round(rmsce(rows, int(protocol["rmsce"]["bins"])) * 100, 4),
                    "formula_conservation": round(formula_matches / valid * 100 if valid else 0.0, 4),
                }
            )
            stereo_rows.append(
                {
                    "model": model_id,
                    "mode": mode,
                    "samples": len(rows),
                    "strict_correct": correct,
                    "strict_accuracy": round(correct / len(rows) * 100, 4),
                    "stereo_agnostic_correct": stereo_correct,
                    "stereo_agnostic_accuracy": round(stereo_correct / len(rows) * 100, 4),
                    "stereo_rescued": stereo_correct - correct,
                }
            )
            if mode == "agent":
                correct_rows = [row for row in rows if row["match"]]
                wrong_rows = [row for row in rows if not row["match"]]
                run_rows.append(
                    {
                        "model": model_id,
                        "samples": len(rows),
                        "correct": correct,
                        "accuracy": round(correct / len(rows) * 100, 4),
                        "avg_llm_calls": round(mean(row["llm_calls"] for row in rows), 4),
                        "avg_planner_calls": round(mean(row["planner_calls"] for row in rows), 4),
                        "avg_final_calls": round(mean(row["final_calls"] for row in rows), 4),
                        "avg_llm_calls_correct": round(mean(row["llm_calls"] for row in correct_rows), 4),
                        "avg_llm_calls_wrong": round(mean(row["llm_calls"] for row in wrong_rows), 4),
                        "avg_total_tokens": round(mean(row["total_tokens"] for row in rows), 4),
                        "avg_prompt_tokens": round(mean(row["prompt_tokens"] for row in rows), 4),
                        "avg_completion_tokens": round(mean(row["completion_tokens"] for row in rows), 4),
                        "avg_duration_ms": round(mean(row["duration_ms"] for row in rows), 4),
                    }
                )

    write_csv(
        DERIVED / "main_results.csv", main_rows,
        ["model", "mode", "samples", "correct", "valid", "formula_matches", "accuracy", "validity", "similarity", "rmsce", "formula_conservation"],
    )
    write_csv(
        DERIVED / "stereo_results.csv", stereo_rows,
        ["model", "mode", "samples", "strict_correct", "strict_accuracy", "stereo_agnostic_correct", "stereo_agnostic_accuracy", "stereo_rescued"],
    )
    write_csv(
        DERIVED / "run_metrics.csv", run_rows,
        ["model", "samples", "correct", "accuracy", "avg_llm_calls", "avg_planner_calls", "avg_final_calls", "avg_llm_calls_correct", "avg_llm_calls_wrong", "avg_total_tokens", "avg_prompt_tokens", "avg_completion_tokens", "avg_duration_ms"],
    )

    trace_source = PAPER_ROOT / "data" / "snapshots" / "trace_process_metrics_common530.csv"
    with trace_source.open(encoding="utf-8", newline="") as handle:
        trace_rows = list(csv.DictReader(handle))
    configured = {model["id"] for model in models}
    trace_rows = [row for row in trace_rows if row["model"] in configured]
    write_csv(DERIVED / "trace_metrics.csv", trace_rows, list(trace_rows[0]))

    molecules = load_json(PAPER_ROOT / "data" / "snapshots" / "molecules_530.json")
    total_molecules = len(molecules)

    def has_raw_field(row: dict[str, Any], field: str) -> bool:
        return bool((row.get("raw_data") or {}).get(field))

    def has_raw_prefix(row: dict[str, Any], prefix: str) -> bool:
        return any(key.startswith(prefix) and bool(value) for key, value in (row.get("raw_data") or {}).items())

    dataset_rows = [
        {"key": "compounds", "label": "Compounds", "count": total_molecules, "total": total_molecules, "show_denominator": "false"},
        {"key": "humanreviewed", "label": "Human-reviewed cases", "count": total_molecules, "total": total_molecules, "show_denominator": "true"},
        {
            "key": "formulaweight",
            "label": "Molecular formula / weight",
            "count": sum(bool(row.get("molecular_formula")) and row.get("molecular_weight") is not None for row in molecules),
            "total": total_molecules,
            "show_denominator": "true",
        },
        {"key": "honenmr", "label": "${}^1$H NMR", "count": sum(has_raw_field(row, "1H_NMR") for row in molecules), "total": total_molecules, "show_denominator": "true"},
        {"key": "cthirteennmr", "label": "${}^{13}$C NMR", "count": sum(has_raw_field(row, "13C_NMR") for row in molecules), "total": total_molecules, "show_denominator": "true"},
        {"key": "hrms", "label": "HRMS", "count": sum(has_raw_prefix(row, "HRMS") for row in molecules), "total": total_molecules, "show_denominator": "true"},
        {"key": "ir", "label": "IR", "count": sum(has_raw_prefix(row, "IR") for row in molecules), "total": total_molecules, "show_denominator": "true"},
    ]
    write_csv(
        DERIVED / "dataset_audit.csv",
        dataset_rows,
        ["key", "label", "count", "total", "show_denominator"],
    )
    print(f"Wrote five derived CSV files under {DERIVED.relative_to(PAPER_ROOT)}")


if __name__ == "__main__":
    main()
