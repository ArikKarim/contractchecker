# Error analysis

## Measured failures

Initial rules: 45 errors across 124 custom-split test decisions. Revised rules: 26 errors. The revised numbers were obtained after inspecting the initial test results. This improvement is an implementation result, not a new external validation.

| Revised task | True positives | True negatives | False positives | False negatives |
|---|---:|---:|---:|---:|
| Forward-looking standard | 15 | 11 | 1 | 4 |
| Ability to consummate | 12 | 14 | 0 | 5 |
| Stockholder litigation exclusion | 7 | 13 | 0 | 11 |
| Buyer-action exclusion | 0 | 26 | 0 | 5 |

The high buyer-action accuracy of 83.9% conceals zero recall for the five positive labels. The majority baseline has the same accuracy on this task. It is inappropriate to call this task successfully automated.

## What went wrong

1. **Grammatical variation.** Initial closing-ability rules missed inflected verbs and `ability of the Company to consummate`; 17/17 positive test labels were missed. The v1.1 implementation correction reduces those misses to five. The remaining cases require reading a closing prong that can appear after the first exclusions marker or use different grammatical structure.
2. **Actor confusion.** Initial buyer matching treated some target actions at a buyer's request as buyer-performed actions. The narrower matcher removes nine false positives but also loses two true positives, in `contract_32` and `contract_43`. It consequently misses all five positive test labels. Party definitions and grammatical actors need contextual interpretation.
3. **Implicit scope.** An exclusion for claims by any person can encompass shareholder claims without saying `shareholder`. Literal rules miss such broader provisions, and the matching task may require interpreting the transaction context.
4. **Negation and incidental co-occurrence.** Synthetic S06, S15 and S16 still produce false positive cues when language is negated or mentions litigation near unrelated shareholder language. S12 exposes the broader any-person exclusion. These probes are AI-authored, with no independent lawyer adjudication.
5. **Label and extraction boundaries.** A matching phrase in a forecast exception need not establish a forward-looking standard in the operative MAE trigger. The first-exclusion heuristic is incomplete, and five source `main` records contain omissions. An exact quote proves that the phrase exists, not that its legal scope was understood.

## Inspectable examples

- `contract_29`, initial buyer false positive: the exact evidence spans an action taken by the Company at Parent's written request. The revised rule no longer conflates that actor relationship. See `results/initial_rule_errors.json` and the original text in `data/maud_mae.jsonl`.
- `contract_32` and `contract_43`, revised buyer false negatives: the model reports no cue despite a positive source label. Read the full source excerpts before deciding whether a feature is absent.
- `contract_8`, revised closing-ability false negative: the wording `the ability of such Person and its Subsidiaries to consummate` occurs before the recognized boundary. The limited party construction fails to match it. The earlier version of this note incorrectly described it as a boundary failure.
- `contract_146`, revised buyer-action and stockholder-litigation false negatives: the boundary function omits `provided that` and instead selects a later `provided, however`. Both matching passages precede the resulting search region. This is a boundary failure rather than an absence of explicit wording.
- `contract_14` and `contract_18`, revised closing-ability false negatives: the terminal prong occurs after exclusions and uses `such party to timely consummate`, which is also outside the current grammar. Both position and expression coverage contribute.

## Consequence for the interface

The tool says `Cue found` and `No cue found`, exposes exact evidence, and provides review questions. It never displays `safe`, `high risk`, `enforceable` or a litigation probability. Prompt prevalence is reported separately from feature accuracy. Improvements require new independent testing rather than repeatedly optimizing against these 31 agreements.
