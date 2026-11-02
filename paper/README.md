# Paper source and build

The paper is available as PDF and editable, browser-readable HTML. Both use `content.json` and the measured result files. Rebuild after any substantive results change:

```sh
python -m pip install reportlab==4.4.9
python scripts/build_paper.py
```

Paper creation is optional and separate from the standard-library-only analyzer and evaluation. The PDF must be rendered and visually reviewed after editing. The original PDF was rendered and inspected in the task workspace. No credentials or independent lawyer review are claimed. A Word version was not delivered because the required Word rendering dependency was unavailable.
