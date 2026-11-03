"""Typeset the manuscript and matching HTML. Optional: reportlab==4.4.9.

Tables and figure are generated from the recorded results, not retyped scores.
The classifier experiment is not rerun by this builder.
"""
import html
import json
import re
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, Preformatted, CondPageBreak
from reportlab.graphics.shapes import Drawing, Line, Circle, String, Rect
from reportlab.graphics import renderSVG

ROOT=Path(__file__).resolve().parents[1]
WIDTH=468
TASKS=[('forward_looking','Forward-looking wording'),('consummation','Ability to consummate'),
       ('shareholder_litigation','Stockholder litigation exclusion'),('buyer_actions','Buyer-action exclusion')]

def load(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))

def fonts():
    candidates=[(Path('C:/Windows/Fonts'),['times.ttf','timesbd.ttf','timesi.ttf','timesbi.ttf']),
                (Path('/usr/share/fonts/truetype/liberation2'),['LiberationSerif-Regular.ttf','LiberationSerif-Bold.ttf','LiberationSerif-Italic.ttf','LiberationSerif-BoldItalic.ttf'])]
    for folder,names in candidates:
        if all((folder/n).exists() for n in names):
            for role,name in zip(['Paper','Paper-Bold','Paper-Italic','Paper-BoldItalic'],names):
                pdfmetrics.registerFont(TTFont(role,str(folder/name)))
            pdfmetrics.registerFontFamily('Paper',normal='Paper',bold='Paper-Bold',italic='Paper-Italic',boldItalic='Paper-BoldItalic')
            return 'Paper','Paper-Bold','Paper-Italic'
    return 'Times-Roman','Times-Bold','Times-Italic'

def table_data(m,initial,audit,stats):
    groups=[('majority','Majority'),('initial','Rules v1'),('naive_bayes','Naive Bayes'),('rules','Rules v1.1 (post hoc)')]
    model=lambda k:initial['models']['rules'] if k=='initial' else m['models'][k]
    out={}
    rows=[['Question','All (152)','Train (91)','Dev (30)','Test (31)']]
    for k,label in TASKS:
        counts=[]
        for s in ['all','train','dev','test']:
            n=stats['sample'][s]['agreements'];y=stats['sample'][s]['positive_labels'][k]
            counts.append(f'{y} / {n-y}')
        rows.append([label]+counts)
    out['classes']=(rows,[172,74,74,74,74])
    rows=[['Method','Correct','Accuracy','95% interval','Macro F1']]
    for k,label in groups:
        mm=model(k);a,z=mm['accuracy_contract_bootstrap']['percentile_95_ci']
        n=sum(t['tp']+t['tn'] for t in mm['per_task'].values())
        rows.append([label,f'{n}/124',f"{100*mm['pooled_accuracy']:.1f}%",f'{100*a:.1f}-{100*z:.1f}%',f"{mm['mean_task_macro_f1']:.3f}"])
    out['overall']=(rows,[160,58,67,105,78])
    rows=[['Question','Majority','Rules v1','Naive Bayes','Rules v1.1']]
    for k,label in TASKS:
        rows.append([label]+[f"{model(method)['per_task'][k]['macro_f1']:.3f}" for method in ['majority','initial','naive_bayes','rules']])
    out['task_scores']=(rows,[172,74,74,74,74])
    rows=[['Question','TP','TN','FP','FN','Precision','Recall','F1 Yes']]
    for k,label in TASKS:
        mm=m['models']['rules']['per_task'][k]
        rows.append([label]+[str(mm[v]) for v in ['tp','tn','fp','fn']]+[f"{mm['precision_yes']:.3f}" if mm['tp']+mm['fp'] else '-',f"{mm['recall_yes']:.3f}",f"{mm['f1_yes']:.3f}"])
    out['confusion']=(rows,[158,30,30,30,30,65,65,60])
    rows=[['Question','Initial correct','Corrections','Regressions','Revised correct']]
    for k,label in TASKS:
        cc=stats['v1_to_v11_test_transitions'][k]['counts']
        before=cc.get('correct_to_correct',0)+cc.get('correct_to_error',0)
        after=cc.get('correct_to_correct',0)+cc.get('error_to_correct',0)
        rows.append([label,str(before),str(cc.get('error_to_correct',0)),str(cc.get('correct_to_error',0)),str(after)])
    out['transitions']=(rows,[172,74,74,74,74])
    labels=['Disproportionate-effect comparison','Causal connector','Missed projections or underlying causes','Pandemic or public health','Clause or section references','Closing-ability branch']
    rows=[['Code','Prompt topic','Excerpts','Share']]
    for i,label in enumerate(labels,1):
        n=m['review_prompt_counts']['test'][f'D{i}'];rows.append([f'D{i}',label,str(n),f'{n/31:.1%}'])
    out['prompts']=(rows,[42,296,66,64])
    rows=[['Project identifier','Exact source question']]
    for k,_ in TASKS:rows.append([k,audit['tasks'][k]])
    out['questions']=(rows,[143,325])
    rows=[['Question','alpha = 0.1','alpha = 1','alpha = 10']]
    for k,label in TASKS:
        tune=m['nb_tuning'][k]
        rows.append([label]+[f"{r['macro_f1']:.3f}"+('*' if r['alpha']==tune['selected_alpha'] else '') for r in tune['dev_candidates']])
    out['tuning']=(rows,[186,94,94,94])
    return out

def accuracy_figure(m,initial,font):
    d=Drawing(WIDTH,176)
    left,right,bottom=165,440,28
    def x(v):return left+(v-.45)/.50*(right-left)
    for tick in [.5,.6,.7,.8,.9]:
        xx=x(tick);d.add(Line(xx,bottom,xx,158,strokeColor=colors.HexColor('#dddddd'),strokeWidth=.4))
        d.add(String(xx,bottom-12,f'{tick:.0%}',fontName=font,fontSize=9,textAnchor='middle'))
    for i,(label,mm,post) in enumerate([
        ('Majority',m['models']['majority'],False),('Rules v1',initial['models']['rules'],False),
        ('Naive Bayes',m['models']['naive_bayes'],False),('Rules v1.1 (post hoc)',m['models']['rules'],True)]):
        yy=145-i*31;a,z=mm['accuracy_contract_bootstrap']['percentile_95_ci'];p=mm['pooled_accuracy']
        d.add(String(left-12,yy-3,label,fontName=font,fontSize=10,textAnchor='end'))
        d.add(Line(x(a),yy,x(z),yy,strokeWidth=1.1,strokeColor=colors.black,strokeDashArray=[3,2] if post else None))
        for endpoint in [a,z]:d.add(Line(x(endpoint),yy-4,x(endpoint),yy+4,strokeWidth=.8))
        d.add(Circle(x(p),yy,3.2,fillColor=colors.white if post else colors.black,strokeWidth=1.1))
    d.add(String((left+right)/2,2,'Decision-level accuracy',fontName=font,fontSize=9,textAnchor='middle'))
    return d

def cited(text,pdf=False):
    text=html.escape(text)
    def replace(match):
        values=re.findall(r'\d+',match.group(1))
        if pdf:return '['+', '.join(f'<link href="#ref{v}" color="black">{v}</link>' for v in values)+']'
        return '['+', '.join(f'<a href="#ref{v}">{v}</a>' for v in values)+']'
    text=re.sub(r'\[(\d+(?:,\s*\d+)*)\]',replace,text)
    for plain,math in [('yhat_it','ŷ<sub>it</sub>'),('y_it','y<sub>it</sub>'),('N_yw','N<sub>yw</sub>'),('c_w(x)','c<sub>w</sub>(x)')]:
        text=text.replace(plain,math)
    return text

def main():
    c=load('paper/content.json');m=load('results/metrics.json');initial=load('results/initial_metrics.json')
    audit=load('data/audit.json');stats=load('paper/descriptive_results.json')
    data=table_data(m,initial,audit,stats)
    normal,bold,italic=fonts()
    styles={
        'body':ParagraphStyle('Body',fontName=normal,fontSize=11,leading=14,spaceAfter=5,firstLineIndent=13,allowWidows=0,allowOrphans=0),
        'abstract':ParagraphStyle('Abstract',fontName=normal,fontSize=10.5,leading=13.2,spaceAfter=8),
        'title':ParagraphStyle('Title',fontName=bold,fontSize=17,leading=20,alignment=TA_CENTER,spaceAfter=9),
        'subtitle':ParagraphStyle('Subtitle',fontName=italic,fontSize=11.5,leading=14,alignment=TA_CENTER,spaceAfter=7),
        'date':ParagraphStyle('Date',fontName=normal,fontSize=10,leading=13,alignment=TA_CENTER,spaceAfter=16),
        'heading':ParagraphStyle('H1',fontName=bold,fontSize=12.5,leading=15,spaceBefore=13,spaceAfter=7,keepWithNext=True),
        'subheading':ParagraphStyle('H2',fontName=bold,fontSize=11,leading=14,spaceBefore=9,spaceAfter=5,keepWithNext=True),
        'caption':ParagraphStyle('Caption',fontName=bold,fontSize=9.5,leading=12,spaceBefore=9,spaceAfter=5),
        'note':ParagraphStyle('Note',fontName=normal,fontSize=9,leading=11.3,spaceBefore=5,spaceAfter=9),
        'cell':ParagraphStyle('Cell',fontName=normal,fontSize=9.3,leading=11.4),
        'cellhead':ParagraphStyle('CellHead',fontName=bold,fontSize=9.1,leading=11.2),
        'reference':ParagraphStyle('Reference',fontName=normal,fontSize=10,leading=12.5,leftIndent=19,firstLineIndent=-19,spaceAfter=7,keepWithNext=True),
        'reference_last':ParagraphStyle('ReferenceLast',fontName=normal,fontSize=10,leading=12.5,leftIndent=19,firstLineIndent=-19,spaceAfter=7),
        'quote':ParagraphStyle('Quotation',fontName=italic,fontSize=10.5,leading=13,leftIndent=20,rightIndent=14,spaceBefore=4,spaceAfter=4),
        'code':ParagraphStyle('Code',fontName='Courier',fontSize=8,leading=11,leftIndent=8,spaceBefore=5,spaceAfter=8),
        'equation':ParagraphStyle('Equation',fontName=normal,fontSize=10.5,leading=14,alignment=TA_CENTER,spaceBefore=6,spaceAfter=8)
    }
    equations={
        1:'P(w | y) = (N<sub>yw</sub> + α) / (Σ<sub>v in V</sub> N<sub>yv</sub> + α |V|)',
        2:'s(x) = Σ<sub>w in V</sub> c<sub>w</sub>(x) log[P(w | 1) / P(w | 0)]<br/>ŷ = 1 if s(x) ≥ 0; otherwise ŷ = 0',
        3:'Accuracy = (1 / 4n) Σ<sub>i=1</sub><super>n</super> Σ<sub>t=1</sub><super>4</super> I(ŷ<sub>it</sub> = y<sub>it</sub>)'
    }
    doc=SimpleDocTemplate(str(ROOT/'paper/mae_drafting_paper.pdf'),pagesize=letter,leftMargin=72,rightMargin=72,topMargin=54,bottomMargin=54,
        title=c['title'],author='ContractChecker research project',subject='Exploratory classification of four MAE clause features')
    story=[Paragraph(html.escape(c['title']),styles['title']),Paragraph(html.escape(c['subtitle']),styles['subtitle']),Paragraph(c['date'],styles['date'])]
    rendered=[];abstract=False
    for block_index,block in enumerate(c['blocks']):
        kind=block['type']
        next_kind=c['blocks'][block_index+1]['type'] if block_index+1<len(c['blocks']) else None
        if kind=='heading':
            level=block.get('level',1);text=block['text'];abstract=level==0
            if next_kind=='table':story.append(CondPageBreak(245))
            story.append(Paragraph(html.escape(text),styles['subheading'] if level==2 else styles['heading']))
            rendered.append(f'<h{3 if level==2 else 2}>{html.escape(text)}</h{3 if level==2 else 2}>')
        elif kind=='paragraph':
            if next_kind=='quotation':story.append(CondPageBreak(150))
            story.append(Paragraph(cited(block['text'],True),styles['abstract'] if abstract else styles['body']))
            rendered.append('<p'+(' class="abstract"' if abstract else '')+'>'+cited(block['text'])+'</p>')
            if abstract:
                line='Keywords: '+ '; '.join(c['keywords'])
                story.append(Paragraph(html.escape(line),styles['note']));rendered.append('<p class="keywords">'+html.escape(line)+'</p>')
                abstract=False
        elif kind=='table':
            rows,widths=data[block['name']]
            cells=[[Paragraph(html.escape(v),styles['cellhead'] if j==0 else styles['cell']) for v in row] for j,row in enumerate(rows)]
            t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
                ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEABOVE',(0,0),(-1,0),.8,colors.black),
                ('LINEBELOW',(0,0),(-1,0),.5,colors.black),('LINEBELOW',(0,-1),(-1,-1),.8,colors.black)]))
            group=[Paragraph(html.escape(block['caption']),styles['caption']),t]
            if block.get('note'):group.append(Paragraph(html.escape(block['note']),styles['note']))
            story.append(KeepTogether(group))
            rendered.append('<figure class="table"><figcaption>'+html.escape(block['caption'])+'</figcaption><table>'+''.join('<tr>'+''.join(('<th>' if j==0 else '<td>')+html.escape(v)+('</th>' if j==0 else '</td>') for v in row)+'</tr>' for j,row in enumerate(rows))+'</table><p class="note">'+html.escape(block.get('note',''))+'</p></figure>')
        elif kind=='figure':
            drawing=accuracy_figure(m,initial,normal)
            story.append(KeepTogether([Spacer(1,8),drawing,Paragraph(html.escape(block['caption']),styles['note'])]))
            svg=renderSVG.drawToString(drawing).replace('font-family: Paper','font-family: Times New Roman')
            rendered.append('<figure>'+svg+'<figcaption>'+html.escape(block['caption'])+'</figcaption></figure>')
        elif kind=='equation':
            number=block['number'];expr=equations[number]
            t=Table([[Paragraph(expr,styles['equation']),Paragraph(f'({number})',styles['equation'])]],colWidths=[430,38])
            t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
            story.append(t);rendered.append('<div class="equation">'+expr+f'<span>({number})</span></div>')
        elif kind=='quotation':
            story.append(KeepTogether([Paragraph('“'+html.escape(block['text'])+'”',styles['quote']),Paragraph(html.escape(block['label']),styles['note'])]))
            rendered.append('<blockquote>'+html.escape(block['text'])+'<footer>'+html.escape(block['label'])+'</footer></blockquote>')
        elif kind=='reference':
            ident=block['id'];label=f'[{ident}] '+html.escape(block['text'])
            style=styles['reference'] if next_kind=='reference' else styles['reference_last']
            story.append(Paragraph(f'<a name="ref{ident}"/><link href="{html.escape(block["url"],quote=True)}" color="black">{label}</link>',style))
            rendered.append(f'<p class="reference" id="ref{ident}"><a href="'+html.escape(block['url'],quote=True)+'">'+label+'</a></p>')
        elif kind=='code':
            story.append(Preformatted(block['text'],styles['code']));rendered.append('<pre>'+html.escape(block['text'])+'</pre>')
    def running(canvas,doc):
        canvas.saveState()
        canvas.setFillColor(colors.black)
        if doc.page>1:
            canvas.setFont(italic,8);canvas.drawString(72,762,'Feature classification in merger agreement MAE definitions')
        canvas.setFont(normal,9);canvas.drawCentredString(306,30,str(doc.page))
        canvas.restoreState()
    doc.build(story,onFirstPage=running,onLaterPages=running)
    css='body{max-width:800px;margin:48px auto;padding:0 28px;color:#111;font:18px/1.65 "Times New Roman",Georgia,serif}h1{font-size:30px;line-height:1.2;text-align:center}h2{font-size:23px;margin-top:32px}h3{font-size:19px;margin-top:23px}.subtitle,.date{text-align:center}.subtitle{font-style:italic}.date{font-size:15px}.keywords,.note,figcaption{font-size:15px;line-height:1.45}.abstract{font-size:17px}table{width:100%;border-collapse:collapse;font-size:15px;line-height:1.4;border-top:1px solid black;border-bottom:1px solid black}th,td{text-align:left;vertical-align:top;padding:8px 5px}th{border-bottom:1px solid black}figure{margin:26px 0}figure.table figcaption{font-weight:bold;margin-bottom:9px}.equation{text-align:center;margin:22px 0}.equation span{float:right}a{color:inherit}.reference{padding-left:25px;text-indent:-25px;font-size:16px}blockquote{margin:18px 25px;font-style:italic}blockquote footer{font-size:14px;font-style:normal}pre{font:12px/1.6 monospace;white-space:pre-wrap;overflow-wrap:anywhere}svg{max-width:100%;height:auto}@media print{body{margin:0;font-size:11pt}h1{font-size:17pt}h2{font-size:12.5pt}h3{font-size:11pt}.table,figure{break-inside:avoid}h2,h3{break-after:avoid}}'
    source='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(c['title'])+'</title><style>'+css+'</style></head><body><article><h1>'+html.escape(c['title'])+'</h1><p class="subtitle">'+html.escape(c['subtitle'])+'</p><p class="date">'+c['date']+'</p>'+''.join(rendered)+'</article></body></html>'
    (ROOT/'paper/mae_drafting_paper.html').write_text(source,encoding='utf-8',newline='\n')
    print('Built scientific PDF and matching HTML')

if __name__=='__main__':main()
