"""Reproduce frozen v1 test runs; no network, API key or external libraries."""
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from contractchecker.rules import TASKS, features, analyze
from contractchecker.model import NaiveBayes
from contractchecker.metrics import binary_metrics, bootstrap, wilson

ROOT=Path(__file__).resolve().parents[1]

def write(path,obj):
    # Python 3.12 changed float summation. Serialize research metrics at a fixed
    # precision far below the sample's resolution, instead of platform noise.
    def canonical(value):
        if isinstance(value,float):return round(value,12)
        if isinstance(value,dict):return {k:canonical(v) for k,v in value.items()}
        if isinstance(value,list):return [canonical(v) for v in value]
        return value
    path.write_text(json.dumps(canonical(obj),indent=2,ensure_ascii=False,sort_keys=True)+'\n',encoding='utf-8',newline='\n')

def main():
    rows=[json.loads(x) for x in (ROOT/'data/maud_mae.jsonl').read_text(encoding='utf-8').splitlines()]
    audit=json.loads((ROOT/'data/audit.json').read_text(encoding='utf-8'))
    assert hashlib.sha256((ROOT/'data/maud_mae.jsonl').read_bytes()).hexdigest()==audit['derived_sha256']
    split={s:[r for r in rows if r['split']==s] for s in ('train','dev','test')}
    for a,b in [('train','dev'),('train','test'),('dev','test')]:
        assert not {r['contract_id'] for r in split[a]}&{r['contract_id'] for r in split[b]}
        assert not {r['normalized_group'] for r in split[a]}&{r['normalized_group'] for r in split[b]}
    majority={t:int(sum(r['labels'][t] for r in split['train'])>=len(split['train'])/2) for t in TASKS}
    models={};tuning={}
    for task in TASKS:
        candidates=[]
        for alpha in (.1,1.0,10.0):
            model=NaiveBayes(alpha).fit([r['text'] for r in split['train']],[r['labels'][task] for r in split['train']])
            score=binary_metrics([r['labels'][task] for r in split['dev']],[model.predict(r['text']) for r in split['dev']])['macro_f1']
            candidates.append((score,alpha,model))
        # Tie resolves to the first alpha, in the documented fixed order.
        best=max(candidates,key=lambda x:x[0])
        models[task]=best[2]
        tuning[task]={'selected_alpha':best[1],'dev_candidates':[{'alpha':a,'macro_f1':s} for s,a,_ in candidates]}
    preds=[];reviews=[]
    for r in rows:
        fs=features(r['text'])
        result=analyze(r['text'])
        reviews.append({'contract_id':r['contract_id'],'split':r['split'],**result})
        for task in TASKS:
            preds.append({'contract_id':r['contract_id'],'split':r['split'],'task':task,'gold':r['labels'][task],
                          'majority':majority[task],'rules':int(fs[task]['value']),'naive_bayes':models[task].predict(r['text']),
                          'evidence':fs[task]['evidence']})
    test=[r for r in preds if r['split']=='test']
    metrics={}
    for name in ('majority','rules','naive_bayes'):
        taskmetrics={}
        for task in TASKS:
            rr=[r for r in test if r['task']==task]
            m=binary_metrics([r['gold'] for r in rr],[r[name] for r in rr])
            m['accuracy_wilson_95_ci']=wilson(m['tp']+m['tn'],m['n'])
            taskmetrics[task]=m
        contract_scores=[sum(p[name]==p['gold'] for p in test if p['contract_id']==r['contract_id'])/len(TASKS) for r in split['test']]
        metrics[name]={'per_task':taskmetrics,'mean_task_macro_f1':math.fsum(m['macro_f1'] for m in taskmetrics.values())/len(TASKS),
                       'pooled_accuracy':sum(p[name]==p['gold'] for p in test)/len(test),'accuracy_contract_bootstrap':bootstrap(contract_scores)}
    differences={}
    for other in ('majority','naive_bayes'):
        differences['rules_minus_'+other]=bootstrap([sum(int(p['rules']==p['gold'])-int(p[other]==p['gold']) for p in test if p['contract_id']==r['contract_id'])/len(TASKS) for r in split['test']])
    errors=[p for p in test if p['rules']!=p['gold']]
    prompt_counts={s:{code:sum(r['split']==s and any(p['id']==code for p in r['review_prompts']) for r in reviews) for code in ('D1','D2','D3','D4','D5','D6')} for s in split}
    results={'protocol':'Exploratory v1.1 pilot; own agreement-disjoint split, not official MAUD benchmark. Rules revised after v1 test inspection; v1.1 test metrics are post hoc. NB alpha selected on dev only. Initial v1 results preserved in initial_metrics.json.',
             'dataset_sha256':audit['derived_sha256'],'rules_sha256':hashlib.sha256((ROOT/'contractchecker/rules.py').read_bytes()).hexdigest(),
             'split_counts':{s:len(rr) for s,rr in split.items()},'test_annotations':len(test),'models':metrics,'nb_tuning':tuning,
             'paired_accuracy_differences':differences,'review_prompt_counts':prompt_counts,
             'unvalidated_outputs':'Review prompts have no independent quality or litigation labels. Counts measure cue prevalence only.',
             'synthetic_stress':stress()}
    out=ROOT/'results';out.mkdir(exist_ok=True)
    write(out/'metrics.json',results)
    write(out/'rule_errors.json',errors)
    (out/'predictions.jsonl').write_text(''.join(json.dumps(p,ensure_ascii=False,sort_keys=True)+'\n' for p in preds),encoding='utf-8',newline='\n')
    (out/'reviews.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in reviews),encoding='utf-8',newline='\n')
    with (out/'test_metrics.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['model','task','n','tp','tn','fp','fn','accuracy','precision_yes','recall_yes','macro_f1','balanced_accuracy'],lineterminator='\n')
        writer.writeheader()
        for name,mm in metrics.items():
            for task,m in mm['per_task'].items():
                writer.writerow({'model':name,'task':task,**{k:round(m[k],12) if isinstance(m[k],float) else m[k] for k in writer.fieldnames if k in m}})
    summary=['# Reproduced MAE feature results','',f"Test: {len(split['test'])} agreements, {len(test)} task annotations.",'',
             '| Model | Accuracy | Mean task macro F1 |','|---|---:|---:|']
    for n,m in metrics.items(): summary.append(f"| {n} | {m['pooled_accuracy']:.3f} | {m['mean_task_macro_f1']:.3f} |")
    summary+=['','See metrics.json for per-task confusion matrices, contract bootstrap intervals, and development-only model selection.',
              'Review prompt counts are unvalidated textual observations, not litigation estimates.','']
    (out/'summary.md').write_text('\n'.join(summary),encoding='utf-8',newline='\n')
    print('\n'.join(summary))

def stress():
    data=[json.loads(x) for x in (ROOT/'data/synthetic_stress.jsonl').read_text(encoding='utf-8').splitlines()]
    decisions=[]
    for r in data:
        predicted=features(r['text'])
        for task,y in r['expected'].items():
            decisions.append({'id':r['id'],'task':task,'expected':y,'prediction':int(predicted[task]['value']),
                              'correct':y==int(predicted[task]['value'])})
    return {'contracts':0,'clause_fragments':len(data),'task_decisions':len(decisions),'correct':sum(d['correct'] for d in decisions),
            'provenance':'AI-authored diagnostic cases with AI-assigned expectations, no independent legal validation; not an accuracy benchmark.',
            'failures':[d for d in decisions if not d['correct']]}

if __name__=='__main__':main()
