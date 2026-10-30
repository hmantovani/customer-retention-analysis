from pathlib import Path
import csv, json, sqlite3
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'

def build_data():
    summary=json.loads((OUT/'summary.json').read_text(encoding='utf-8'))
    with (OUT/'monthly.csv').open(encoding='utf-8',newline='') as f:
        monthly=[{'month':r['month'],'active':int(r['active']),'orders':int(r['orders']),'gross':float(r['gross'])} for r in csv.DictReader(f)]
    with (OUT/'cohorts.csv').open(encoding='utf-8',newline='') as f:
        cohorts=[{'month':r['cohort'],'rates':[float(v) if v else None for k,v in r.items() if k!='cohort']} for r in csv.DictReader(f)]
    with sqlite3.connect(OUT/'analysis.sqlite') as db:
        sizes=dict(db.execute("SELECT substr(first_date,1,7), count(*) FROM (SELECT customer, min(date) first_date FROM orders GROUP BY customer) GROUP BY 1"))
        bins=dict(db.execute("SELECT CASE WHEN n=1 THEN '1' WHEN n=2 THEN '2' WHEN n BETWEEN 3 AND 5 THEN '3–5' WHEN n BETWEEN 6 AND 10 THEN '6–10' ELSE '11+' END, count(*) FROM (SELECT customer, count(*) n FROM orders GROUP BY customer) GROUP BY 1"))
    for c in cohorts: c['size']=sizes[c['month']]
    distribution=[{'label':k,'customers':bins.get(k,0)} for k in ['1','2','3–5','6–10','11+']]
    assert sum(sizes.values())==summary['customers']==sum(x['customers'] for x in distribution)
    assert distribution[0]['customers']==summary['one_time']
    assert sum(x['orders'] for x in monthly)==summary['orders']
    return {'summary':summary,'monthly':monthly,'cohorts':cohorts,'distribution':distribution}

def main():
    data=build_data()
    template=(ROOT/'src/demo-template.html').read_text(encoding='utf-8')
    (ROOT/'index.html').write_text(template.replace('/* DATA_PLACEHOLDER */',json.dumps(data,ensure_ascii=True)),encoding='utf-8')
    print('Built index.html with',data['summary']['customers'],'customers')
if __name__=='__main__': main()
