# Paper result reproduction bundle

This bundle supports **MolQuest: A Benchmark for Agentic Evaluation of Abductive
Reasoning in Chemical Structure Elucidation**. It imports the reconciled
common-530 artifacts from Overleaf commit
`c99d3f0939ef16ae987a20bb709edb3f1a75433f`. The manuscript is maintained in Overleaf;
this directory publishes the numerical and visual artifacts used for the GitHub
presentation.

## What is fixed

- 530 reference molecules, identical to `../data/molecules_final.json`.
- 16 model variants in Agent and Baseline settings: 32 configurations and 16,960
  per-case prediction records.
- A fixed metric protocol in `config/metric_protocol.json`.
- Derived CSVs, generated LaTeX tables/macros, and four vector PDF figures.
- Run/trace diagnostic snapshots and source-result hashes.

`data/snapshots/source_manifest.json` retains the original result-source commit
and file hashes. `IMPORT_MANIFEST.json` identifies this Overleaf import and its
original bytes. `generated/artifact_manifest.json` verifies derived outputs.
[DATA_AUDIT.md](DATA_AUDIT.md) explains the reconciliation of historical results.

## Verify and regenerate

From the repository root:

```bash
uv sync
uv run python paper/scripts/verify_artifacts.py
uv run python paper/scripts/compute_metrics.py
uv run python paper/scripts/generate_tables.py
uv run python paper/scripts/verify_artifacts.py
uv run python paper/scripts/sync_github_results.py --check
```

These commands do not call a model API. They recompute aggregate metrics from
saved per-case fields (including stored canonicalization and similarity), rather
than rerunning models or recanonicalizing predictions under a new RDKit version.
The metrics and table scripts require only Python's standard library. The original
source exporter verified agreement between evaluated and merged-run predictions;
its provenance is preserved in the source manifest.

For deliberate result updates, rerun `sync_github_results.py` without `--check`
to update the README summary and `docs/results.md`. Verify and review the output
before replacing a published snapshot or its hashes.

## Figures

```bash
uv run python paper/scripts/generate_figures.py
```

Figure regeneration requires the project scientific dependencies. The imported
PDFs are preserved for the pinned paper version; a different plotting/library
version can change bytes even when the plotted data agree. Regenerated artifacts
will fail the original hash check until explicitly reviewed and versioned.

The GitHub PNG previews in `../docs/assets/` were rendered from the imported PDFs.
Static framework, curation, and case-study illustrations were copied from the same
Overleaf commit. Numerical claims in README and `docs/results.md` are generated
from `data/derived/main_results.csv`, rather than transcribed from older figures.

## Scope

The compact snapshot is sufficient to reproduce reported aggregate outcomes,
run diagnostics, trace-summary metrics, tables, and plots. It does not include
all original tool-call transcripts or the original document extraction/review UI.
Existing `../results/` artifacts can represent earlier collections; the fixed
snapshot and source manifest define the figures reported here.
