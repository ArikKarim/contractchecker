# AI assistance and provenance

Codex assisted with source discovery, scope selection (revised to M&A at the user's direction), code generation, data preparation, rule design, evaluation scripts, synthetic diagnostics, manuscript drafting, and implementation fixes. The scripts were executed against the downloaded source release; the reported metrics were computed, not invented. The code, tests and artifact inspection do not substitute for independent legal review.

No LLM API calls, model fine-tuning, or autonomous legal-agent inference were used to score MAUD clauses. The interactive analyzer is a deterministic rule system. The statistical comparator is a standard-library naive Bayes implementation. The 16 synthetic diagnostic fragments and their expected outcomes are AI-authored and not independent ground truth. The browser's single illustrative sample is also AI-generated.

The researcher should reproduce and inspect the work, review the legal sources, correct errors and accurately describe their own contribution before presenting the repository as a personal research sample. No education, experience, authorship credentials, lawyer review or Stanford affiliation is asserted by this project.

## Optional future LLM comparison protocol

An LLM-assisted comparator could be added only as a separately logged experiment: provide the extracted clause and exact task definitions, ask for structured labels plus literal evidence spans, validate all cited spans against input, record provider/model/version/date/prompt/settings and cost, and freeze prompts before opening a new test set. Treat text inside contracts as data, never as instructions. Score it on the same new agreement-disjoint sample as the other baselines. Use independent lawyers for prompt usefulness and scope judgments. This proposed experiment has not been run.
