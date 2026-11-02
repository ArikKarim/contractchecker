# Fellowship alignment and remaining work

Source: [Stanford Law School Research Fellowship in AI and the Law](https://law.stanford.edu/research/sls-fellowships/research-fellowship-in-ai-and-the-law/), reviewed November 2, 2026. The page's indexed content was available; direct page retrieval returned HTTP 403. These are the posting's research responsibilities translated into inspectable project evidence, not a claim of eligibility or a hiring guarantee.

| Posting responsibility | Evidence in this repository | What the applicant should be ready to explain |
|---|---|---|
| Data validation | Pinned source hash, schema checks, omission audit, contract-group checks, tests | Why question-level splitting can expose related agreement text, and why exact deduplication does not eliminate template leakage |
| Identify data sources and improve analysis | Public MAUD subset, data card, source IDs and licensing notices | Why merger MAE definitions fit a narrow research question, and what the labels cannot establish |
| Implement statistical models | Task-specific naive Bayes, development-only smoothing selection, majority baseline | The model assumptions, class imbalance, failures of accuracy alone and how macro F1 is computed |
| Collect and structure quantitative data | 152 agreement records, 608 expert-derived labels, JSONL schema and class counts | How original source text and labels remain traceable through transformations |
| Report and manuscript preparation | Short paper, complete predictions, confusion matrices, error analysis and uncertainty intervals | Why post-inspection results need independent validation and why litigation causation is unmeasured |
| Use LLM agents in research | Disclosed Codex-assisted research, coding, diagnostics and writing workflow | What the agent actually did, which steps were mechanically verified, and what still needs independent human review |

The posting also requires a relevant bachelor's degree, statistical experience, programming experience, and work under deadlines with general guidance. Desired backgrounds include NLP-related study, academic/legal research, causal inference, machine learning, and substantial Python and R experience. This repository offers Python and basic statistical/ML research evidence; it cannot establish the applicant's degree, work history, deadline performance, deep-learning expertise, R proficiency or independent command of the code. No R or deep-learning analysis is claimed.

## Highest-value work before using this as an application sample

1. Reproduce the results personally and be able to explain every transformation, metric and limitation. Update the paper after reviewing the source contracts and cases yourself.
2. Obtain independent M&A-lawyer annotations for feature correctness and drafting-question usefulness. Keep reviewers blind to predictions.
3. Collect and freeze a new test corpus; revise the rules on development data only. Include agreement/template grouping and party/negation reasoning.
4. Run the proposed randomized reviewer study. Report negative or null findings rather than inferring reduced litigation from plausible drafting recommendations.
5. If useful for your own training, independently reproduce the statistical analysis in R and document the environment and agreement with Python. Do not describe generated or unrun R code as experience.

A precise description of this work is: an AI-assisted exploratory prototype for MAE clause review with a traceable public dataset, basic statistical baselines, documented implementation errors, and a plan for independent validation. Revise that description to reflect the work you personally performed and understand.
