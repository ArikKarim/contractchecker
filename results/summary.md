# Reproduced MAE feature results

Test: 31 agreements, 124 task annotations.

| Model | Accuracy | Mean task macro F1 |
|---|---:|---:|
| majority | 0.645 | 0.389 |
| rules | 0.790 | 0.690 |
| naive_bayes | 0.742 | 0.657 |

See metrics.json for per-task confusion matrices, contract bootstrap intervals, and development-only model selection.
Review prompt counts are unvalidated textual observations, not litigation estimates.
