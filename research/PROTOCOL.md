# Research protocol and iteration record

## Question and scope

Can transparent, lightweight text analysis identify four MAE features and support specific drafting-review questions in merger agreements? The measured endpoint is agreement with MAUD's binary feature labels. Litigation initiation, dispute resolution, enforceability and draft quality are not measured.

The legal lens is Delaware M&A decisions. Sample governing law is not verified. Human-extracted clauses are the input. No end-to-end full-contract or PDF extraction claim is made.

## Analysis design

- Use the 152 MAUD original `main` MAE excerpts and four tasks specified in `data/audit.json`.
- Preserve contract-level grouping and normalized exact-text groups. Use fixed hash order with seed `contractchecker-maud-v1-2026-11-02`; allocate 91 train, 30 dev, 31 test. Do not tune the split to label counts.
- Compare task-specific train-majority predictions, transparent matching rules, and one multinomial naive Bayes classifier per task.
- Model features are lowercase alphabetic unigrams and adjacent bigrams. Cap each token count at three; build vocabulary on train only. Use equal class priors. Evaluate smoothing alpha in `[0.1, 1, 10]` by binary macro F1 on dev only; ties select the first candidate. No retraining on train plus dev is used.
- Report every task's TP/TN/FP/FN, Yes precision and recall, both class F1s, macro F1, balanced accuracy and accuracy. Zero-denominator metrics are defined as zero.
- Summarize the unweighted mean of task macro F1 and accuracy over all 124 test decisions. Each agreement contributes four decisions. The latter are correlated and are not 124 independent contracts.
- For accuracy and paired accuracy differences, resample 31 contracts with replacement 2,000 times, seed 20261102. Each sampled contract carries all four task decisions. Report interpolated percentile 95% intervals. Per-task accuracy also has Wilson intervals. These are small-sample exploratory intervals; no multiplicity correction, causal inference or post-selection correction is applied.

## Iterations and disclosure

This is an exploratory protocol written during implementation, not an independently preregistered study. Data structure, aggregate class counts and source snippets were inspected during development. The model is evaluated on a custom agreement-disjoint split, not the official MAUD split or published MAUD metrics.

**Initial v1:** rules were implemented before the first custom-split evaluation. Test accuracy was 79/124 (63.7%); mean task macro F1 was 0.568. The initial code is retained in `research/initial_rules.py`, the numerical results in `results/initial_metrics.json`, and errors in `results/initial_rule_errors.json`. `scripts/evaluate_initial.py` reproduces those results.

**Revision v1.1:** after inspecting the v1 test errors and diagnostic failures, the closing-ability matcher was corrected to handle inflections, whitespace and the common `ability of the Company to consummate` form. The buyer-action matcher was narrowed to avoid treating a target action at Parent's request as an action performed by Parent. Two regression tests were added. This revision scores 98/124 (79.0%), with mean task macro F1 0.690, on the same test set.

**The revised rule result is post hoc.** The development choices were informed by test errors. The intervals in `metrics.json` do not adjust for this adaptation. A new independently collected test set is necessary before claiming out-of-sample rule performance. There was no API-based LLM inference or fine-tuning. The naive Bayes hyperparameter search was development-only and was not changed after test inspection.

The 16 AI-generated diagnostic fragments are adversarial probes, not statistically independent validation. Initial: 11/18 expected decisions; revised: 14/18. Preserve failing probes. No score is used to claim legal correctness.

The canonical JSONL serialization was subsequently standardized to LF line endings for cross-platform CI. The initial metrics retain the original CRLF input hash; the initial reproduction script reconstructs and verifies that representation. The parsed records, labels, split and numerical results are unchanged.

Current numeric metric outputs are serialized to 12 decimal places, and task-level means use `math.fsum`, so differences in Python's floating-point summation do not produce spurious cross-version CI diffs. This precision exceeds what the sample can substantively support. Initial archived outputs retain their original numerical representation.

## Next confirmatory study

Collect a new sample of merger agreements outside MAUD, preferably filed after the source corpus period; record deal year, governing law, industry and drafting-template families. Have two M&A lawyers independently label clause features and review-prompt usefulness while blinded to model outputs, adjudicating disagreements. Freeze the next implementation before opening the new test set. Report reviewer agreement, feature performance, prompt precision, missed issues, and review time.

For the intervention study, randomize reviewer-contract pairs to ordinary review or review with the tool, with original/revised draft order counterbalanced. Prespecify lawyer-rated clarity and issue-detection measures, review time and adverse changes to commercial risk allocation. Analyze reviewer and contract dependence. That experiment can estimate an effect on review outcomes, not on lawsuits. A litigation study would additionally need reliable deal-to-docket linkage, timing and censoring rules, confounder measurement, and a credible identification strategy; clause prevalence alone cannot supply one.
