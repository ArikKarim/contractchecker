# MAUD MAE pilot dataset

## Identity and use

Source: [The Atticus Project, MAUD v1](https://www.atticusprojectai.org/maud/); [research paper](https://arxiv.org/abs/2301.00876); [official release repository](https://github.com/The-Atticus-Project/maud). Accessed November 2, 2026. The publisher states [CC BY 4.0](https://www.atticusprojectai.org/legal/).

Wang, Steven H., Antoine Scardigli, Leonard Tang, Wei Chen, Dimitry Levkin, Anya Chen, Spencer Ball, Thomas Woodside, Oliver Zhang, and Dan Hendrycks. 2023. *MAUD: An Expert-Annotated Legal NLP Dataset for Merger Agreement Understanding*. EMNLP. arXiv:2301.00876.

This project retains 152 expert-extracted MAE definitions from the original `main` data and four binary task labels per agreement, totaling 608 annotations. The 152 rows are real source agreement excerpts, not AI-generated contracts. Full agreement texts can be fetched to ignored local storage with `scripts/prepare_data.py --download`. They are not required for the evaluated clause-reading task.

## Inclusion and transformations

Read all three official CSVs; retain `data_type == main` and the four exact question strings recorded in `audit.json`. Exclude the separately labeled `abridged` and `rare_answers` datasets. Preserve original excerpt text, Yes/No labels (mapped to 1/0), source row IDs and upstream split names. No legal label corrections or silent text repairs are applied. Five `main` records already include `<omitted>`; this quality issue is retained and flagged rather than reclassifying those records.

All four chosen tasks have exactly one label per contract and exactly the same source excerpt within a contract. The validator rejects missing labels, duplicate contract-task pairs, conflicting excerpt texts, empty text and unexpected answers. It verifies the archive hash and the expected contract count. It records all transformations and output hashes.

## Fields in maud_mae.jsonl

| Field | Meaning |
|---|---|
| `contract_id` | Publisher's anonymized contract ID, not a named deal identifier |
| `text` | Unmodified source MAE excerpt, including source page references |
| `labels` | Four expert-derived binary labels, keyed by project task |
| `source_rows` | Original CSV split and row ID for every task |
| `text_sha256` | SHA-256 of the original excerpt's UTF-8 bytes |
| `normalized_group` | Hash of case-folded, whitespace-collapsed text; grouping only |
| `split` | This pilot's agreement-disjoint partition |
| `contains_source_omission` | Whether the original main excerpt contains `<omitted>` |
| `source`, `license` | Attribution and stated publisher license |

The four tasks are `forward_looking`, `consummation`, `shareholder_litigation`, and `buyer_actions`. Exact question strings and class counts are in `audit.json`. A gold 1 identifies an annotated legal feature; it does not mean a defect, unenforceability, or elevated litigation risk.

Canonical derived files use LF line endings for cross-platform reproducibility. The archived initial run used CRLF record separators and records that serialization's hash. `scripts/evaluate_initial.py` reconstructs those bytes and verifies the initial hash as well as the unchanged numerical results.

## Split and quality findings

The upstream CSVs overlap by contract across different questions. For these four selected tasks, 76 contract IDs occur in both upstream train and dev, 86 in train and test, and 40 in dev and test. This is a finding about this task combination, not an assertion that MAUD's published task-specific evaluation is invalid.

This pilot sorts normalized exact-text groups by SHA-256 of a fixed seed plus group hash, then assigns the first 60% of groups to train, the next 20% to dev and the remainder to test. All questions for one agreement stay together. Counts: 91/30/31. The split is deterministic and not stratified. All 152 excerpts are distinct even after case/whitespace normalization. Near-duplicate agreement templates and drafting-firm families were not identified. Do not interpret this as a clean split by template, deal year, law firm or issuer.

## Licensing and limitations

MAUD is publicly available and usable for attributed research under the publisher's stated CC BY 4.0 license. Retain the citation, source link, license link, transformations and no-endorsement notice when redistributing this subset. Underlying SEC-filed agreement text can involve third-party rights; public availability alone is not a claim that every underlying instrument is public domain. No endorsement by The Atticus Project, ABA or Stanford is implied.

The source is a small, selected public-company M&A corpus. It is not representative of private deals, small transactions, non-US practice, all deal years, or all governing laws. The pilot does not verify Delaware governing law. It contains no litigation outcomes and no labels for drafting quality. Its selection of MAE excerpts gives the analyzer an extraction advantage compared with full-document use.

`synthetic_stress.jsonl` is a separate set of 16 AI-authored fragments with 18 diagnostic expectations. Its expectations were assigned by the same AI-assisted workflow as the implementation, not independent lawyers. It is useful for exposing negation, actor and scope failures; it is not an external accuracy benchmark or a set of execution-ready contracts.
