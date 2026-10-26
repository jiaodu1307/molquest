# MolQuest datasets

## Published snapshots

| File | Records | Purpose |
| --- | ---: | --- |
| `molecules_final.json` | 530 | Default dataset for execution and evaluation |
| `examples.json` | 6 | Small schema / usage examples |
| `versions/molecules_v3_535.json` | 535 | Historical v3 experiment ground truth |
| `versions/v3_to_final.json` | 5 exclusions | Exact UUID membership differences between v3 and final |

Every final record occurs in v3 with identical values after removing the
`properties` field. Five v3 records are absent from final. Their historical
exclusion reasons were not documented in the available files; the difference
manifest records this uncertainty rather than assigning a new reason.
Do not mix metrics from these two versions. To evaluate historical v3 runs:

```bash
uv run python scripts/analyze/evaluate_predictions.py --help
# Supply --ground_truth data/versions/molecules_v3_535.json when evaluating v3.
```

The agent reads `config/settings.yaml` (`data_path`) or `MOLECULE_DATA_PATH`.
Batch execution and evaluation default to `data/molecules_final.json`.
Example UUIDs belong to the separate example dataset; use its path explicitly.
Records contain UUIDs, reference SMILES, formula / molecular weight, optional
InChI identifiers, and spectral descriptions in `raw_data`. Reference structures
are evaluation labels. Null values indicate missing measurements.

## Original source files

These files were copied byte-for-byte from the local legacy `nmr-agent/data/raw/`
archive. They are preserved as received, including any existing data errors.

| File | Records | Description |
| --- | ---: | --- |
| `raw/nmr_data.csv` | 512 | Spectral text, IUPAC names, and SMILES |
| `raw/molecules.json` | 342 | Earlier structured molecular dataset |
| `raw/NMRdata-2-260112.json` | 393 | Literature-labelled molecular records |
| `raw/sorted_isomers_merged.json` | 194 groups | Grouped isomer source; count is groups, not molecules |

`raw/literature_sources.csv` lists the literature titles and counts present in
`NMRdata-2-260112.json`. Titles do not establish redistribution permission.
Original download URLs, DOI mapping, and redistribution licenses were not present
in the inspected archive. No data license is asserted here; the repository's
software license does not automatically apply to third-party source data.

`manifest.json` records byte sizes and SHA-256 checksums for the published JSON
and CSV snapshots (excluding the manifest itself and generated outputs).

## Paper result snapshot

The [`paper/`](../paper/README.md) bundle imports the manuscript's reconciled
common-530 prediction snapshot and fixed metric protocol. Its molecular dataset
is byte-for-byte identical to `molecules_final.json`. Use this bundle to reproduce
the paper tables; legacy evaluation scripts and older saved results may use
different metric denominators or prediction collections. See the
[reconciliation audit](../paper/DATA_AUDIT.md).

## Preparation utilities

Install the locked project dependencies with `uv sync`. Run from the repository
root; each utility also resolves its default paths relative to the repository
when invoked elsewhere. Outputs go to ignored `data/generated/` and never
replace the published snapshots.

```bash
uv run python scripts/data/process_isomers.py
uv run python scripts/data/merge_molecule_data.py
uv run python scripts/data/check_duplicates.py
uv run python scripts/data/validate_molecules.py
uv run python scripts/data/analyze_dataset_stats.py
uv run python scripts/data/analyze_smiles_diversity.py
```

Use `--help` for input/output overrides. The first four commands normalize the
literature-labelled source, merge it with the earlier structured dataset,
deduplicate canonical isomeric SMILES, and validate molecular structures and
formula / weight. Despite its legacy filename, `process_isomers.py` processes
the literature-labelled list, not `sorted_isomers_merged.json`.

These utilities recover the available preparation steps; they do not reconstruct
the final snapshot byte-for-byte. Historical UUID generation uses UUID4, additional
manual selection steps are undocumented, and the CSV extraction utility in
`src/utils/csv_to_molecule_json.py` uses an LLM. Validation retains the historical
average molecular weight calculation (`RDKit MolWt`); the CSV extraction utility
uses monoisotopic mass (`ExactMolWt`). Generated values must not be substituted
into published labels without an explicit dataset version change.

The two analysis commands default to the 530-record final dataset. To reproduce
statistics on the historical dataset, pass
`--input data/versions/molecules_v3_535.json`.

## Storage policy

The nested legacy checkout, environments, secrets, logs, raw run traces and
intermediate outputs are excluded through `.gitignore`. Existing published
results and figures remain available. Full experiment archives should be
published separately with an explicit dataset version, model configuration,
sample UUID list, and checksum rather than duplicated across export folders.
