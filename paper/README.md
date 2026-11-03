# Paper source and build

The paper is available as PDF and editable, browser-readable HTML. Both use `content.json` and the measured result files. Rebuild after any substantive results change:

```sh
python -m pip install reportlab==4.4.9
python scripts/paper_statistics.py --output paper/descriptive_results.json
python scripts/build_paper.py
```

Paper creation is optional and separate from the standard-library-only analyzer and evaluation. The PDF uses a single-column scientific manuscript layout, numbered sections, equations, tables, a vector accuracy plot and numbered references. Times New Roman is embedded when available; Linux builds can use Liberation Serif, with standard PDF Times as a fallback. The PDF must be rendered and visually reviewed after editing. No credentials or independent lawyer review are claimed.

The expanded manuscript retains the original experiment and its post hoc revision disclosure. New descriptive summaries are computed from existing data and predictions without retuning models. The paper source is `content.json`; the statistical supplement is `descriptive_results.json`. Source quotations are checked against the original excerpt using recorded Unicode character offsets.
