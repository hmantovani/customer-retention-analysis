import sys
from pathlib import Path
import unittest
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analyze import prepare, analyze

class AnalysisTests(unittest.TestCase):
 def test_refunds_cutoff_and_one_time(self):
  data=pd.DataFrame([
   ['1','2011-01-01',1,10,1], ['2','2011-02-01',1,20,1],
   ['C2','2011-02-01',1,20,-1], ['3','2011-11-01',2,5,1],
   ['4','2011-12-01',2,5,1], ['5','2011-01-02',None,5,1]],
   columns=['InvoiceNo','InvoiceDate','CustomerID','UnitPrice','Quantity'])
  d=prepare(data)
  self.assertEqual(len(d),5)
  self.assertEqual(int(d.purchase.sum()),3+1) # includes anonymous line
  self.assertEqual(d.loc[d.refund,'value'].sum(),-20)
  # analyze computes a source hash as well; source workbook is required by the production pipeline.
  _,orders,c,monthly,co,s=analyze(data)
  self.assertEqual(len(orders),3)
  self.assertEqual(s['one_time'],1)
  self.assertEqual(s['mature'],1)
  self.assertEqual(s['repeat90'],1)
  self.assertEqual(c.loc['1','days_second'],31)
  self.assertEqual(co.loc['2011-01',1],100)
  self.assertTrue(pd.isna(co.loc['2011-11',1]))
if __name__=='__main__': unittest.main()

