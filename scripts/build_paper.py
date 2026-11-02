"""Build matching PDF and HTML. Optional dependency: reportlab==4.4.9."""
import html
import json
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.pagesizes import letter

ROOT=Path(__file__).resolve().parents[1]

def tables(metrics,initial):
    out={'methods':[['Method','Accuracy','95% interval','Macro F1']]}
    for key,label in [('majority','Training majority'),('initial','Initial rules v1'),('naive_bayes','Naive Bayes'),('rules','Revised rules v1.1 post hoc')]:
        m=initial['models']['rules'] if key=='initial' else metrics['models'][key]
        a,b=m['accuracy_contract_bootstrap']['percentile_95_ci']
        out['methods'].append([label,f"{m['pooled_accuracy']:.1%}",f'{a:.1%} to {b:.1%}',f"{m['mean_task_macro_f1']:.3f}"])
    out['tasks']=[['Revised rule task','TP','TN','FP','FN','Macro F1']]
    for key,label in [('forward_looking','Forward looking'),('consummation','Closing ability'),('shareholder_litigation','Stockholder litigation'),('buyer_actions','Buyer actions')]:
        m=metrics['models']['rules']['per_task'][key]
        out['tasks'].append([label]+[str(m[x]) for x in ('tp','tn','fp','fn')]+[f"{m['macro_f1']:.3f}"])
    return out

def main():
    content=json.loads((ROOT/'paper/content.json').read_text(encoding='utf-8'))
    m=json.loads((ROOT/'results/metrics.json').read_text(encoding='utf-8'))
    initial=json.loads((ROOT/'results/initial_metrics.json').read_text(encoding='utf-8'))
    ts=tables(m,initial)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyPaper',fontName='Helvetica',fontSize=9.5,leading=12.1,spaceAfter=6,textColor=colors.HexColor('#1c2b32')))
    styles.add(ParagraphStyle(name='HeadPaper',fontName='Helvetica-Bold',fontSize=12,leading=15,spaceBefore=9,spaceAfter=6,keepWithNext=True))
    styles.add(ParagraphStyle(name='TitlePaper',fontName='Helvetica-Bold',fontSize=20,leading=23,spaceAfter=8))
    styles.add(ParagraphStyle(name='ReferencePaper',fontName='Helvetica',fontSize=8,leading=10.2,spaceAfter=5))
    styles.add(ParagraphStyle(name='TablePaper',fontName='Helvetica',fontSize=8.5,leading=10.5))
    doc=SimpleDocTemplate(str(ROOT/'paper/mae_drafting_paper.pdf'),pagesize=letter,rightMargin=48,leftMargin=48,topMargin=43,bottomMargin=43,
                          title=content['title'],author='ContractChecker research project')
    story=[Paragraph(html.escape(content['title']),styles['TitlePaper']),Paragraph(html.escape(content['subtitle']),styles['BodyPaper']),Paragraph(content['date'],styles['ReferencePaper']),Spacer(1,3)]
    rendered=[]
    for i,blocks in enumerate(content['pages']):
        if i:story.append(PageBreak())
        hs=[];number=0
        for b in blocks:
            kind=b['type']
            if kind=='heading':
                story.append(Paragraph(html.escape(b['text']),styles['HeadPaper']))
                hs.append('<h2>'+html.escape(b['text'])+'</h2>')
            elif kind in ('paragraph','numbered'):
                text=html.escape(b['text'])
                if kind=='numbered':number+=1;text=f'<b>{number}.</b> '+text
                story.append(Paragraph(text,styles['BodyPaper']))
                hs.append('<p'+(' class="principle"' if kind=='numbered' else '')+'>'+text+'</p>')
            elif kind=='table':
                rows=ts[b['name']]
                data=[[Paragraph(html.escape(v),styles['TablePaper']) for v in row] for row in rows]
                widths=[209,65,125,117] if b['name']=='methods' else [226,50,50,50,50,90]
                table=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
                table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8efeb')),('VALIGN',(0,0),(-1,-1),'TOP'),
                    ('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#9fafa5')),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d5dfd8')),
                    ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
                story.extend([Spacer(1,7),table,Spacer(1,8)])
                hs.append('<table>'+''.join('<tr>'+''.join(('<th>' if j==0 else '<td>')+html.escape(x)+('</th>' if j==0 else '</td>') for x in row)+'</tr>' for j,row in enumerate(rows))+'</table>')
            elif kind=='reference':
                label='['+b['id']+'] '+html.escape(b['label'])
                story.append(Paragraph('<link href="'+html.escape(b['url'],quote=True)+'" color="#22594a">'+label+'</link>',styles['ReferencePaper']))
                hs.append('<p class="ref" id="ref'+b['id']+'"><a href="'+html.escape(b['url'],quote=True)+'">'+label+'</a></p>')
        rendered.append('<section>'+''.join(hs)+'</section>')
    def footer(canvas,doc):
        canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#687670'))
        canvas.drawRightString(564,25,str(doc.page))
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    css='body{max-width:820px;margin:50px auto;padding:0 24px;color:#172d38;font:17px/1.7 Georgia,serif}h1{font-size:36px;line-height:1.15}h2{font:600 23px/1.3 system-ui;margin-top:32px}.subtitle,.date{font-family:system-ui;color:#5a6c73}.date{font-size:14px}table{font:14px/1.5 system-ui;border-collapse:collapse;width:100%;margin:22px 0}th,td{text-align:left;padding:10px;border-bottom:1px solid #ccd8d1}th{background:#e8efeb}a{color:#22594a}.ref{font:13px/1.5 system-ui}.principle{padding-left:18px;border-left:3px solid #dae6de}section{margin-bottom:38px}@media print{body{font-size:10pt;margin:0;max-width:none}h1{font-size:21pt}h2{font-size:13pt}section{break-after:page}section:last-child{break-after:auto}}'
    source='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(content['title'])+'</title><style>'+css+'</style><article><h1>'+html.escape(content['title'])+'</h1><p class="subtitle">'+html.escape(content['subtitle'])+'</p><p class="date">'+content['date']+'</p>'+''.join(rendered)+'</article></html>'
    (ROOT/'paper/mae_drafting_paper.html').write_text(source,encoding='utf-8',newline='\n')
    print('Built paper PDF and HTML')

if __name__=='__main__':main()
