# Main-result data audit

This camera-ready source uses one fixed evaluation universe and one prediction
source for every reported configuration:

- 530 UUIDs from `data/snapshots/molecules_530.json`;
- 16 model configurations in Agent and Baseline modes (32 result rows);
- predictions verified against each model's `*_merged_runs.json` record;
- no model was rerun during this reconciliation.

## Metric protocol

The executable definition is `config/metric_protocol.json`.

- Accuracy and validity use all 530 cases.
- Similarity averages all valid predictions, including exact matches.
- RMSCE uses 10 equal-width confidence bins over all 530 outputs, includes
  confidence zero in the first bin, and assigns similarity zero to invalid
  SMILES.
- Formula conservation is conditioned on valid predictions because validity is
  already reported as a separate end-to-end failure measure.

## Material changes from the previous manuscript table

The previous table mixed a 535-case snapshot with common-530 results and, for
Claude Opus Agent, mixed two different prediction collections. The reconciled
table therefore makes the following material corrections:

| Configuration | Previous | Reconciled | Reason |
|---|---:|---:|---|
| GLM-4.7 Agent accuracy | 4.49 | 7.92 | Existing merged runs contain 42 correct predictions among the common 530; the old 4.49 value cannot be reproduced from retained predictions. |
| GLM-4.7 Agent validity | 78.69 | 65.47 | Same source reconciliation as above. |
| GLM-4.7 Agent similarity | 34.73 | 39.82 | Same source reconciliation as above. |
| GLM-4.7 Agent RMSCE | 56.01 | 48.40 | Same source reconciliation as above. |
| GLM-4.7 Agent formula conservation | 14.96 | 25.36 | Same source reconciliation and valid-prediction denominator. |
| Claude Opus Agent accuracy | 25.66 | 25.47 | The main merged-run source has 135 correct cases; the collected-trace copy has 136 and is not used for outcome metrics. |
| Claude Opus Agent formula conservation | 61.58 | 69.11 | Recomputed from the same merged-run source used for the other outcome metrics. |
| GPT-5.5 Agent accuracy | 42.24 | 42.64 | Same 226 correct predictions, with denominator corrected from 535 to 530. |
| GPT-5.5 Baseline accuracy | 52.15 | 52.64 | Same 279 correct predictions, with denominator corrected from 535 to 530. |
| Qwen3 Max Thinking Agent accuracy | 17.38 | 17.55 | Same 93 correct predictions, with denominator corrected from 535 to 530. |

Smaller changes in Doubao, Qwen3.5 Plus, validity, similarity, calibration, and
formula conservation follow from the same common-530 filtering and source
normalization. The complete reconciled values and integer counts are stored in
`data/derived/main_results.csv`.

## Integrity controls

`data/snapshots/source_manifest.json` stores SHA-256 hashes of every imported
evaluated and merged file. `generated/artifact_manifest.json` hashes all
derived CSV, generated table, macro, and figure artifacts. Run `make verify`
to detect missing or stale outputs.
