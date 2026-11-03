"""Reproduce v1 without modifying the current rule implementation or results."""
import importlib.util
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from contractchecker.metrics import binary_metrics
from contractchecker.rules import TASKS

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('initial_rules',root/'research/initial_rules.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
records=[json.loads(x) for x in (root/'data/maud_mae.jsonl').read_text(encoding='utf-8').splitlines()]
test=[r for r in records if r['split']=='test']
metrics={}
for task in TASKS:
    metrics[task]=binary_metrics([r['labels'][task] for r in test],[int(module.features(r['text'])[task]['value']) for r in test])
old=json.loads((root/'results/initial_metrics.json').read_text(encoding='utf-8'))['models']['rules']
assert metrics=={t:{k:m[k] for k in metrics[t]} for t,m in old['per_task'].items()}
initial=json.loads((root/'results/initial_metrics.json').read_text(encoding='utf-8'))
# The initial run used Windows CRLF record separators. The current canonical
# dataset uses LF for cross-platform CI. Reconstruct and verify initial bytes.
lf=(root/'data/maud_mae.jsonl').read_bytes().replace(b'\r\n',b'\n')
assert hashlib.sha256(lf.replace(b'\n',b'\r\n')).hexdigest()==initial['dataset_sha256']
print(json.dumps({'verified_initial_v1':True,'accuracy':old['pooled_accuracy'],'mean_task_macro_f1':old['mean_task_macro_f1']},indent=2))
