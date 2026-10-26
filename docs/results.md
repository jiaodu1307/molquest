# Paper outcome metrics

[Repository overview](../README.md) · [Metric definitions](benchmark.md) · [Reproduce these results](../paper/README.md)

Generated from [`main_results.csv`](../paper/data/derived/main_results.csv). Every configuration uses the same 530 cases. Values are percentages (0–100); accuracy is stereochemistry-aware. Similarity and formula conservation use valid predictions as their denominator. RMSCE uses all predictions and is lower when confidence better tracks structural similarity.

## Agent

| Model variant | Correct / 530 | Accuracy ↑ | Validity ↑ | Similarity ↑ | RMSCE ↓ | Formula conservation ↑ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Gemini 3 Flash | 273 / 530 | 51.51 | 94.72 | 77.69 | 23.89 | 90.84 |
| Gemini 3 Pro Thinking | 256 / 530 | 48.30 | 96.79 | 74.43 | 24.85 | 93.57 |
| GPT-5.5 High | 226 / 530 | 42.64 | 95.66 | 73.53 | 14.67 | 95.86 |
| Claude Opus 4.5 Thinking | 135 / 530 | 25.47 | 97.74 | 58.84 | 24.30 | 69.11 |
| Doubao-2.0 Pro | 132 / 530 | 24.91 | 92.45 | 57.44 | 36.94 | 70.20 |
| Qwen3.5 Plus Thinking | 102 / 530 | 19.25 | 91.32 | 52.36 | 34.64 | 63.02 |
| Claude Sonnet 4.5 | 96 / 530 | 18.11 | 96.60 | 50.04 | 40.47 | 49.02 |
| Qwen3 Max Thinking | 93 / 530 | 17.55 | 81.51 | 49.90 | 44.99 | 59.49 |
| Doubao-1.8 | 91 / 530 | 17.17 | 73.77 | 53.76 | 48.03 | 64.71 |
| DeepSeek V3.2 Thinking | 88 / 530 | 16.60 | 71.13 | 53.55 | 27.21 | 64.46 |
| Qwen3 Max | 81 / 530 | 15.28 | 83.02 | 45.96 | 48.08 | 47.95 |
| Claude Haiku 4.5 | 61 / 530 | 11.51 | 88.68 | 41.30 | 43.19 | 29.15 |
| DeepSeek V3.2 | 60 / 530 | 11.32 | 85.28 | 41.56 | 47.68 | 29.87 |
| Kimi K2 Thinking | 60 / 530 | 11.32 | 73.02 | 47.17 | 38.16 | 49.10 |
| GLM-4.7 Thinking | 42 / 530 | 7.92 | 65.47 | 39.82 | 48.40 | 25.36 |
| DeepSeek V3.1 | 39 / 530 | 7.36 | 84.34 | 37.31 | 51.97 | 23.71 |

## Baseline

| Model variant | Correct / 530 | Accuracy ↑ | Validity ↑ | Similarity ↑ | RMSCE ↓ | Formula conservation ↑ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-5.5 High | 279 / 530 | 52.64 | 96.23 | 78.54 | 9.98 | 97.65 |
| Gemini 3 Pro Thinking | 276 / 530 | 52.08 | 96.04 | 77.39 | 23.69 | 90.57 |
| Gemini 3 Flash | 271 / 530 | 51.13 | 95.09 | 78.06 | 21.94 | 85.52 |
| Claude Opus 4.5 Thinking | 151 / 530 | 28.49 | 97.17 | 62.05 | 15.43 | 56.31 |
| Qwen3.5 Plus Thinking | 151 / 530 | 28.49 | 91.13 | 60.56 | 35.36 | 72.88 |
| Doubao-2.0 Pro | 131 / 530 | 24.72 | 87.92 | 58.06 | 36.52 | 71.89 |
| Kimi K2 Thinking | 109 / 530 | 20.57 | 71.89 | 60.20 | 30.08 | 75.07 |
| DeepSeek V3.2 Thinking | 108 / 530 | 20.38 | 56.79 | 64.12 | 23.07 | 81.73 |
| Qwen3 Max Thinking | 97 / 530 | 18.30 | 72.08 | 54.06 | 37.69 | 66.49 |
| Claude Sonnet 4.5 | 93 / 530 | 17.55 | 95.09 | 51.98 | 34.94 | 42.26 |
| Doubao-1.8 | 88 / 530 | 16.60 | 70.75 | 53.91 | 47.87 | 60.27 |
| GLM-4.7 Thinking | 85 / 530 | 16.04 | 68.87 | 50.72 | 43.90 | 50.14 |
| Claude Haiku 4.5 | 51 / 530 | 9.62 | 86.04 | 40.70 | 36.41 | 23.03 |
| DeepSeek V3.1 | 36 / 530 | 6.79 | 86.23 | 35.42 | 55.58 | 16.41 |
| DeepSeek V3.2 | 30 / 530 | 5.66 | 86.04 | 31.65 | 52.48 | 16.01 |
| Qwen3 Max | 25 / 530 | 4.72 | 89.62 | 31.15 | 57.75 | 13.68 |

## Additional diagnostics

- [Stereochemistry-agnostic accuracy](../paper/data/derived/stereo_results.csv)
- [Run-level metrics](../paper/data/derived/run_metrics.csv)
- [Trace-level metrics](../paper/data/derived/trace_metrics.csv)
- [Dataset coverage](../paper/data/derived/dataset_audit.csv)
- [Reconciliation audit](../paper/DATA_AUDIT.md)

The paper snapshot is pinned to Overleaf commit `c99d3f0939ef16ae987a20bb709edb3f1a75433f`. These are recomputed outcomes from saved predictions; no model was rerun during reconciliation.
