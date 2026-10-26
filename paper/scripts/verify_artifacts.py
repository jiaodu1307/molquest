#!/usr/bin/env python3
"""Verify the imported paper snapshot and generated numerical artifacts."""

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    imported = json.loads((PAPER / "IMPORT_MANIFEST.json").read_text())
    for relative, expected in {**imported["imported_files"], **imported["rendered_previews"]}.items():
        path = PAPER / relative
        if not path.is_file() or sha256(path) != expected:
            raise SystemExit(f"Changed imported artifact: {relative}")
    artifacts = json.loads((PAPER / "generated/artifact_manifest.json").read_text())["artifacts"]
    for relative, expected in artifacts.items():
        if sha256(PAPER / relative) != expected:
            raise SystemExit(f"Stale generated artifact: {relative}")
    source = json.loads((PAPER / "data/snapshots/source_manifest.json").read_text())
    if sha256(PAPER / source["snapshot"]) != source["snapshot_sha256"]:
        raise SystemExit("Prediction snapshot does not match its source manifest")
    dataset = json.loads((PAPER / "data/snapshots/molecules_530.json").read_text())
    released = json.loads((PAPER.parent / "data/molecules_final.json").read_text())
    if dataset != released:
        raise SystemExit("Paper dataset differs from the released final dataset")
    universe = {row["uuid"] for row in dataset}
    if len(dataset) != 530 or len(universe) != 530:
        raise SystemExit("Expected 530 unique dataset UUIDs")
    models = json.loads((PAPER / "config/models.json").read_text())
    keys = {(model["id"], mode) for model in models for mode in ("agent", "baseline")}
    seen = Counter()
    with (PAPER / source["snapshot"]).open() as handle:
        for line in handle:
            row = json.loads(line)
            key = (row["model"], row["mode"], row["uuid"])
            if key[:2] not in keys or key[2] not in universe:
                raise SystemExit(f"Unexpected prediction key: {key}")
            seen[key] += 1
    if len(seen) != len(keys) * len(universe) or any(count != 1 for count in seen.values()):
        raise SystemExit("Missing or duplicate per-case predictions")
    with (PAPER / "data/derived/main_results.csv").open(newline="") as handle:
        outcomes = list(csv.DictReader(handle))
    if len(outcomes) != len(keys) or {(row['model'], row['mode']) for row in outcomes} != keys:
        raise SystemExit("Incomplete aggregate configuration coverage")
    for row in outcomes:
        total = int(row["samples"])
        if total != 530 or abs(float(row["accuracy"]) - 100 * int(row["correct"]) / total) > 0.0001:
            raise SystemExit("Aggregate sample count or accuracy disagrees with integer counts")
    print(f"Verified {len(artifacts)} generated artifacts, {len(keys)} configurations, "
          f"{len(seen)} predictions, and the released 530-case dataset")


if __name__ == "__main__":
    main()
