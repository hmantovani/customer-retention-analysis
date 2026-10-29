from pathlib import Path
import sqlite3, hashlib, html, json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'Online Retail.xlsx'
OUT = ROOT / 'output'
END = pd.Timestamp('2011-12-01') # exclusive: last complete calendar month

def prepare(df):
    d = df.rename(columns={'InvoiceNo':'invoice','InvoiceDate':'date','CustomerID':'customer','UnitPrice':'price','Quantity':'quantity'}).copy()
    d['date'] = pd.to_datetime(d['date'])
    d['invoice'] = d['invoice'].astype(str)
    d['customer'] = d['customer'].astype('Int64').astype('string')
    d['value'] = d['quantity'] * d['price']
    d = d[d.date < END].copy()
    # Positive, non-cancellation lines define an order; refunds remain signed cash-flow adjustments.
    d['purchase'] = (~d.invoice.str.startswith('C')) & (d.quantity > 0) & (d.price > 0)
    d['refund'] = d.invoice.str.startswith('C') & (d.quantity < 0) & (d.price > 0)
    return d

def analyze(df):
    d=prepare(df)
    identified=d[d.customer.notna()]
    purchase=identified[identified.purchase]
    orders=(purchase.groupby(['customer','invoice'],as_index=False).agg(date=('date','min'),gross=('value','sum')).sort_values(['customer','date','invoice']))
    customers=orders.groupby('customer').agg(first=('date','min'),last=('date','max'),orders=('invoice','size'),gross=('gross','sum'))
    second=orders.groupby('customer').nth(1).set_index('customer')['date']
    customers['second']=second
    customers['days_second']=(customers['second']-customers['first']).dt.total_seconds()/86400
    mature=customers[customers['first'] <= END-pd.Timedelta(days=90)]
    repeat90=(mature.days_second <= 90).sum()
    monthly=orders.assign(month=orders.date.dt.to_period('M').astype(str)).groupby('month').agg(active=('customer','nunique'),orders=('invoice','size'),gross=('gross','sum'))
    first_month=customers['first'].dt.to_period('M')
    order_month=orders.date.dt.to_period('M')
    offsets=(order_month.astype('int64').to_numpy()-first_month.loc[orders.customer].astype('int64').to_numpy())
    cohort=orders.assign(cohort=first_month.loc[orders.customer].astype(str).to_numpy(),age=offsets).groupby(['cohort','age']).customer.nunique().unstack(fill_value=0)
    cohort=cohort.reindex(columns=range((END.to_period('M')-first_month.min()).n),fill_value=0)
    sizes=first_month.astype(str).value_counts().sort_index()
    # Full month observation only; mask future or partial cohort ages.
    for c in cohort.index:
        for age in cohort.columns:
            if pd.Period(c, freq='M')+int(age) >= END.to_period('M'): cohort.loc[c,age]=float('nan')
    rates=cohort.div(sizes,axis=0)*100
    refunds=identified[identified.refund].groupby('customer').value.sum()
    net=customers.gross.add(refunds,fill_value=0).sort_values(ascending=False)
    # Include refund-only identified customers in cash-flow reconciliation, but not purchaser concentration.
    net_purchase=customers.gross.add(refunds.reindex(customers.index,fill_value=0),fill_value=0).sort_values(ascending=False)
    k=max(1, __import__('math').ceil(len(net_purchase)*.1))
    return d,orders,customers,monthly,rates,{'customers':len(customers),'orders':len(orders),'one_time':int((customers.orders==1).sum()),'mature':len(mature),'repeat90':int(repeat90),'median_days':float(customers.days_second.median()),'gross':float(customers.gross.sum()),'refunds':float(identified[identified.refund].value.sum()),'top10':float(net_purchase.iloc[:k].sum()/net_purchase.sum()),'missing_lines':int(d.customer.isna().sum()),'lines':len(d),'refund_only':float(net.sum()-net_purchase.sum()),'source_sha256':hashlib.sha256(DATA.read_bytes()).hexdigest()}

def table(df): return df.to_html(classes='data',border=0,na_rep='—',escape=True)
def build():
    OUT.mkdir(exist_ok=True)
    raw=pd.read_excel(DATA,engine='openpyxl')
    d,o,c,m,co,s=analyze(raw)
    with sqlite3.connect(OUT/'analysis.sqlite') as db:
        o.assign(date=o.date.astype(str)).to_sql('orders',db,if_exists='replace',index=False)
        d.assign(date=d.date.astype(str),customer=d.customer.astype(object)).to_sql('lines',db,if_exists='replace',index=False)
    m.to_csv(OUT/'monthly.csv'); co.to_csv(OUT/'cohorts.csv',float_format='%.2f'); (OUT/'summary.json').write_text(json.dumps(s,indent=2),encoding='utf-8')
    cohort_view=co.loc[:,co.columns<=6].round(1).rename_axis('First observed month'); cohort_view.columns=[f'M{n}' for n in cohort_view.columns]
    mv=m.copy(); mv['gross']=mv.gross.map(lambda x:f'£{x:,.0f}'); mv.index.name='Month'
    bars=''.join(f'<div class="barrow"><span>{idx}</span><div class="track"><i style="width:{row.active/m.active.max()*100:.1f}%"></i></div><b>{int(row.active):,}</b></div>' for idx,row in m.iterrows())
    report=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Customer retention | Online Retail</title><style>body{{margin:0;background:#f5f3ed;color:#1d2b29;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1050px;margin:auto;padding:48px 24px}}h1{{font-size:clamp(2.5rem,6vw,4.5rem);line-height:1.03;max-width:800px;margin:.3em 0}}h2{{margin-top:2em}}.eyebrow{{text-transform:uppercase;letter-spacing:.16em;color:#17705b;font-weight:700;font-size:.75rem}}.lead{{max-width:760px;font-size:1.2rem;color:#52615b}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:32px 0}}.card{{background:#173f36;color:white;padding:20px;border-radius:10px}}.card strong{{display:block;font-size:2rem}}.card small{{color:#c7ded4}}section{{background:white;border:1px solid #e1e5df;border-radius:12px;padding:24px;margin:18px 0}}.scroll{{overflow:auto}}table{{border-collapse:collapse;font-size:.85rem;width:100%;white-space:nowrap}}th,td{{padding:8px;border-bottom:1px solid #e7ece8;text-align:right}}th:first-child,td:first-child{{text-align:left}}.barrow{{display:flex;align-items:center;gap:12px;margin:7px 0;font-size:.85rem}}.barrow span{{width:70px}}.track{{background:#eef2ed;flex:1;height:12px;border-radius:8px}}i{{display:block;background:#329579;height:100%;border-radius:8px}}.barrow b{{width:50px;text-align:right}}.note{{color:#596963;font-size:.9rem}}a{{color:#126b57}}@media print{{body{{background:white}}section{{break-inside:avoid}}}}</style></head><body><main><div class="eyebrow">Portfolio case study · observed transactions · 2010–2011</div><h1>Retention starts with the second order.</h1><p class="lead">A decision brief for sales and finance using UCI Online Retail. Purchases through November 2011 are analyzed; December is excluded because it is incomplete.</p><div class="cards"><div class="card"><strong>{s['customers']:,}</strong><small>identified customers with a purchase</small></div><div class="card"><strong>{s['repeat90']/s['mature']:.1%}</strong><small>repeat within 90 days among {s['mature']:,} eligible customers</small></div><div class="card"><strong>{s['one_time']/s['customers']:.1%}</strong><small>one observed order during the window</small></div><div class="card"><strong>{s['top10']:.1%}</strong><small>net revenue from top 10% of purchasers</small></div></div><section><h2>What to do next</h2><ol><li><b>Investigate the second-order journey.</b> Only {s['repeat90']/s['mature']:.1%} of customers with a full 90-day observation window placed a second order in that time. Test an onboarding offer against a randomized holdout; measure incremental 90-day repeat and margin, not just coupon use.</li><li><b>Review account concentration.</b> The top 10% of observed purchasers account for {s['top10']:.1%} of identified purchaser net revenue. Examine large wholesale accounts and account-level refund exposure before setting targets.</li><li><b>Check seasonality and acquisition mix.</b> Monthly active purchasers range from {m.active.min():,} to {m.active.max():,}. Compare like-for-like seasons and new versus existing accounts before interpreting changes as churn.</li></ol><p class="note">These are descriptive associations, not causal effects. The data contain no campaign exposure, acquisition cost, margin, or reason for inactivity.</p></section><section><h2>Repeat purchasing</h2><p>{s['one_time']:,} of {s['customers']:,} purchasers have only one observed order. Among customers with a second observed order, the median time to it is {s['median_days']:.0f} days; this conditional median excludes one-time customers and is not a population time-to-event estimate. Customers without a second order may return after the data end.</p></section><section><h2>Active customers by month</h2><p class="note">Distinct identified customers with at least one qualifying purchase. The first and last bars cover complete calendar months, but activity is not evidence of permanent churn.</p>{bars}<details><summary>Show monthly figures</summary><div class="scroll">{table(mv)}</div></details></section><section><h2>Cohort purchase activity</h2><p class="note">Percent of each first-observed-month cohort making at least one purchase in the indicated calendar month after that first month. M0 is 100%; activity is not necessarily consecutive. Em dash means the month has not fully elapsed. The first cohort is left-censored and may contain existing customers.</p><div class="scroll">{table(cohort_view)}</div></section><section><h2>Interpretation and boundaries</h2><p>Transactions are invoice lines for a UK-based online retailer, including wholesale customers, from 1 December 2010 to 9 December 2011. This analysis stops before 1 December 2011. Customer IDs are missing on {s['missing_lines']:,} of {s['lines']:,} lines in the analysis window; those lines cannot be linked to a customer and are excluded from customer metrics. First observed purchase is not necessarily acquisition. The source is historical and cannot establish current performance or represent all retailers.</p><p>Orders are distinct customer/invoice combinations with positive quantity and price, excluding cancellation invoices. Revenue concentration uses positive purchase value plus signed cancellation lines for the same identified purchasing customers, recognized on the transaction date. Refunds are not matched to original invoices; refunds after cutoff and nonstandard adjustments are missed. Identified cancellation lines total £{s['refunds']:,.0f}; refund-only customers contribute £{s['refund_only']:,.0f} and are excluded from purchaser concentration. This is net transaction value, not profit or accounting revenue.</p><p class="note">Source: Chen, D. (2015), <a href="https://doi.org/10.24432/C5BW33">Online Retail</a>, UCI Machine Learning Repository, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>. See README for definitions, exclusions, reproducibility, and data quality checks.</p></section></main></body></html>'''
    (ROOT/'report.html').write_text(report,encoding='utf-8')
    print(json.dumps(s,indent=2)); print(m.to_string())
if __name__=='__main__': build()


