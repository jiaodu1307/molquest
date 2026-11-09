# MolQuest Agent traces: common-530

Version 1.0, generated from molquest commit `846efdc9fdbfea0dcd9928cf13f4329fced57a2b`.

## Contents

- 16 Agent model configurations.
- 8,480 runs: 530 molecules per model.
- One structured JSON trace and one readable Markdown trace per run (16,960 trace files).
- `manifest.json`: dataset/source hashes, model mapping, selected paths, and per-file SHA-256 hashes.

Traces are under `traces/agent/<model>/`. JSON traces contain `uuid`, `final_answer`, and `steps`; Markdown files are readable renderings of the same runs.

## Selection and validation

Each trace is the exact file referenced by `trace_json_path` in the corresponding current `results/agent/` merged-runs file. Unreferenced reruns and records outside common-530 are excluded. Trace UUIDs and final answers were checked against the merged-run records. One qwen3-max error trace retains a public Alibaba Cloud help URL that is redacted in the published merged run; this is documented in `manifest.json` and does not change its prediction.

These are original model outputs and may contain incorrect reasoning or predictions. They are preserved for research reproducibility, not treated as ground truth. Baseline runs do not have separate tool-call traces; their predictions are already published under `results/baseline/`.
