# ContractChecker

A small, reproducible research prototype for **material adverse effect (MAE) definitions in M&A merger agreements**, with drafting questions informed by Delaware decisions. It runs offline, uses Python's standard library, and requires no API key.

**Current status:** exploratory research, not a legal screening product. The interactive tool reads an **extracted target MAE definition**, including exclusions and provisos. It does not extract clauses from a PDF or full agreement. It reports literal textual cues and review questions; it does not estimate litigation probability or decide enforceability.

## Start the tool

Use Python 3.10 or newer from the repository root:

```sh
python -m contractchecker --serve
```

Open http://127.0.0.1:8765 in a browser. Paste an MAE definition, load the clearly marked illustrative clause, or open a UTF-8 `.txt` file. Download the review as JSON. Text stays on your computer; uploads are not saved or logged.

For CLI output:

```sh
python -m contractchecker examples/illustrative_mae.txt
```

The evidence offsets are zero-based Unicode character offsets, with an exclusive end. The evidence quote is an exact slice of the input. A missing cue is **not a finding that the legal feature is absent**.

## Read the research

- [Short paper PDF](paper/mae_drafting_paper.pdf) and [editable HTML version](paper/mae_drafting_paper.html).
- [Dataset card and attribution](data/DATASET_CARD.md), [audit](data/audit.json), and [source manifest](data/source_manifest.json).
- [Methods and iteration record](research/PROTOCOL.md), [error analysis](research/ERROR_ANALYSIS.md), and [fellowship alignment](research/FELLOWSHIP_ALIGNMENT.md).
- [Machine-readable results](results/metrics.json), [per-task results](results/test_metrics.csv), [all predictions](results/predictions.jsonl), and [test rule errors](results/rule_errors.json).

The main sample comprises 152 real merger agreements from **MAUD v1**, with 608 retained expert task labels. The agreement-disjoint split contains 91 training, 30 development, and 31 test agreements. This is a custom pilot, not a reproduction of the published MAUD benchmark.

| Method | Accuracy across 124 test decisions | Mean task macro F1 |
|---|---:|---:|
| Training-majority baseline | 64.5% | 0.389 |
| Initial rules v1 | 63.7% | 0.568 |
| Statistical naive Bayes baseline | 74.2% | 0.657 |
| Revised rules v1.1 **after test inspection** | 79.0% | 0.690 |

The v1.1 result is **post hoc**, not an independent estimate of generalization. The rules miss all five positive buyer-action labels in the test sample. They also fail several negation and scope diagnostics. Feature accuracy does not validate the drafting questions or show that editing language reduces litigation.

## Reproduce the experiments

No installation is needed for the CLI, local interface, tests, or experiments:

```sh
python -m unittest discover -s tests -v
python scripts/evaluate.py
```

The checked-in derived dataset permits offline reproduction. Results use deterministic seeds and recorded hashes. To re-create the subset from the original release and obtain full contract texts locally:

```sh
python scripts/prepare_data.py --download
python scripts/evaluate.py
```

The downloader checks the pinned archive SHA-256 before processing. Full contract texts are written only to ignored `data/raw/contracts/`. The source URL can change, in which case the script deliberately refuses different bytes. A local copy of the same archive can be supplied with `--archive PATH`.

To reproduce the initial implementation's numerical results:

```sh
python scripts/evaluate_initial.py
```

The statistical baseline is a class-balanced multinomial naive Bayes text classifier. Smoothing is selected per task on the development set only. It is an experiment, not an API-based LLM. [AI assistance is disclosed here](research/AI_ASSISTANCE.md).

## What the checks cover

Four cue checks concern forward-looking wording, an ability-to-consummate prong, stockholder litigation exclusions, and buyer-action exclusions. Six review prompts ask about comparator groups, causal connectors, underlying causes of missed forecasts, emergency responses and ordinary-course covenants, clause cross references, and separate closing-ability prongs.

These prompts identify things to read and negotiate. Common, deliberate provisions can trigger them. They are not defect labels, risk rankings, or recommended one-size-fits-all provisions.

## Responsible research scope

The data contain no litigation, settlement, negotiation cost, or causal outcome labels. Governing law is not verified for the sample. Boilerplate relatives may span the split despite exact-text deduplication. Five original MAUD `main` records contain omission markers. The analysis depends on an already extracted definition and does not test OCR or extraction. See the paper for the proposed independent lawyer evaluation and causal research design.

## Licenses

Original software is MIT licensed. MAUD-derived text and annotations are attributed to The Atticus Project and provided under its stated CC BY 4.0 terms; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The code license does not relicense MAUD or other third-party material. Synthetic diagnostic clauses are AI-generated research examples, not execution-ready agreements.
