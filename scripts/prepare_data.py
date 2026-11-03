"""Fetch pinned MAUD release and derive four original-text tasks.

Run from repository root. The full contracts stay in ignored data/raw/.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import urllib.request
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from contractchecker.rules import TASKS

URL='https://raw.githubusercontent.com/The-Atticus-Project/maud/main/data.zip'
SHA256='75af5a33d038e9254864f043da38072490ffe11e8488d58d0a2dd39c8f554519'
SEED='contractchecker-maud-v1-2026-11-02'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')

def prepare(archive, output=Path('data')):
    raw=archive.read_bytes()
    if digest(raw)!=SHA256:
        raise ValueError('Archive SHA-256 mismatch. Refusing unreviewed source revision.')
    csv.field_size_limit(10_000_000)
    lookup={q:task for task,q in TASKS.items()}
    records={}
    upstream={}
    all_rows=0
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        for split in ('train','dev','test'):
            rows=list(csv.DictReader(io.StringIO(z.read(f'data/MAUD_{split}.csv').decode('utf-8-sig'))))
            upstream[split]=set()
            for r in rows:
                all_rows+=1
                if r['data_type']!='main' or r['question'] not in lookup:
                    continue
                task=lookup[r['question']]
                cid=r['contract_name']
                upstream[split].add(cid)
                if r['answer'] not in ('Yes','No'):
                    raise ValueError(f'Unexpected answer {cid} {task}')
                rec=records.setdefault(cid,{'contract_id':cid,'text':r['text'],'labels':{},'source_rows':{},
                                           'source':'MAUD v1 / The Atticus Project','license':'CC-BY-4.0'})
                if rec['text']!=r['text'] or task in rec['labels']:
                    raise ValueError(f'Conflicting text or duplicate task: {cid} {task}')
                rec['labels'][task]=int(r['answer']=='Yes')
                rec['source_rows'][task]={'upstream_split':split,'id':r['id']}
        if len(records)!=152:
            raise ValueError(f'Expected 152 source contracts; found {len(records)}')
        # Do not extract arbitrary archive paths. Only known contract IDs are written.
        rawdir=output/'raw/contracts'
        rawdir.mkdir(parents=True,exist_ok=True)
        for cid in records:
            if not __import__('re').fullmatch(r'contract_\d+',cid):
                raise ValueError('Unsafe source ID')
            (rawdir/f'{cid}.txt').write_bytes(z.read(f'data/contracts/{cid}.txt'))
    groups={}
    for r in records.values():
        if set(r['labels'])!=set(TASKS) or not r['text'].strip():
            raise ValueError('Missing task or empty text')
        r['contains_source_omission']='<omitted>' in r['text']
        r['text_sha256']=digest(r['text'].encode('utf-8'))
        groups.setdefault(r['text_sha256'],[]).append(r)
    # Identical normalized texts are also kept together, not just identical bytes.
    normalized={}
    for r in records.values():
        h=digest(' '.join(r['text'].casefold().split()).encode('utf-8'))
        normalized.setdefault(h,[]).append(r)
    keys=sorted(normalized,key=lambda h:digest((SEED+h).encode()))
    ntrain,ndev=int(len(keys)*.6),int(len(keys)*.2)
    for i,h in enumerate(keys):
        split='train' if i<ntrain else 'dev' if i<ntrain+ndev else 'test'
        for r in normalized[h]:
            r['split']=split
            r['normalized_group']=h
    ordered=sorted(records.values(),key=lambda r:int(r['contract_id'].split('_')[1]))
    path=output/'maud_mae.jsonl'
    path.write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in ordered),encoding='utf-8',newline='\n')
    counts={s:sum(r['split']==s for r in ordered) for s in ('train','dev','test')}
    classes={s:{t:{str(y):sum(r['split']==s and r['labels'][t]==y for r in ordered) for y in (0,1)} for t in TASKS} for s in counts}
    audit={'source_archive_sha256':SHA256,'derived_sha256':digest(path.read_bytes()),'archive_csv_rows':all_rows,
           'contracts':len(ordered),'task_annotations':len(ordered)*len(TASKS),'tasks':TASKS,'split_seed':SEED,
           'split_unit':'normalized exact text group; all tasks from one contract stay together',
           'split_contract_counts':counts,'class_counts':classes,'exact_text_groups':len(groups),'normalized_text_groups':len(normalized),
           'replacement_characters':sum(r['text'].count('\ufffd') for r in ordered),
           'main_records_with_source_omission':sum(r['contains_source_omission'] for r in ordered),
           'upstream_contract_overlap':{a+'_'+b:len(upstream[a]&upstream[b]) for a,b in [('train','dev'),('train','test'),('dev','test')]},
           'empty_texts':0,'duplicate_contract_task_pairs':0,'missing_labels':0,'cross_split_contract_overlap':0,'cross_split_normalized_text_overlap':0,
           'near_duplicate_templates':'Not deduplicated; this remains a generalization limitation.'}
    write_json(output/'audit.json',audit)
    write_json(output/'source_manifest.json',{'dataset':'MAUD v1','publisher':'The Atticus Project','source_url':URL,
        'source_sha256':SHA256,'accessed':'2026-11-02','license':'CC BY 4.0',
        'license_url':'https://www.atticusprojectai.org/legal/','homepage':'https://www.atticusprojectai.org/maud/',
        'paper':'https://arxiv.org/abs/2301.00876','citation':'Wang et al. (2023). MAUD: An Expert-Annotated Legal NLP Dataset for Merger Agreement Understanding.',
        'transformations':'Retain main original MAE text and four binary tasks; preserve labels and upstream IDs; regroup by agreement/normalized exact text; no abridged or rare-answer examples.',
        'data_notices':'MAUD terms do not establish litigation outcomes or remove any third-party rights in underlying SEC exhibits.'})
    print(json.dumps({'contracts':len(ordered),'splits':counts,'class_counts':classes},indent=2))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--archive',type=Path,default=Path('data/raw/maud-data.zip'))
    p.add_argument('--download',action='store_true')
    args=p.parse_args()
    if args.download:
        args.archive.parent.mkdir(parents=True,exist_ok=True)
        with urllib.request.urlopen(URL,timeout=120) as response:
            payload=response.read()
        if digest(payload)!=SHA256:
            raise ValueError('Downloaded archive differs from the pinned release')
        args.archive.write_bytes(payload)
    if not args.archive.exists():
        p.error('Archive not found. Use --download or --archive PATH.')
    prepare(args.archive)

if __name__=='__main__':
    main()
