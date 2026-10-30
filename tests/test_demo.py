import json, sqlite3, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from build_demo import build_data

class DemoTests(unittest.TestCase):
 def test_aggregates_against_orders(self):
  d=build_data()
  with sqlite3.connect(ROOT/'output/analysis.sqlite') as db:
   orders=db.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
   counts=dict(db.execute('SELECT substr(date,1,7), COUNT(DISTINCT customer) FROM orders GROUP BY 1'))
   first=dict(db.execute('SELECT substr(first_date,1,7), COUNT(*) FROM (SELECT customer, MIN(date) first_date FROM orders GROUP BY customer) GROUP BY 1'))
  self.assertEqual(sum(x['orders'] for x in d['monthly']),orders)
  self.assertEqual({x['month']:x['active'] for x in d['monthly']},counts)
  self.assertEqual({x['month']:x['size'] for x in d['cohorts']},first)
  self.assertEqual(sum(x['customers'] for x in d['distribution']),d['summary']['customers'])
  self.assertEqual(d['distribution'][0]['customers'],d['summary']['one_time'])
  self.assertEqual(d['cohorts'][-1]['rates'][1],None)
 def test_page_contains_current_data(self):
  html=(ROOT/'index.html').read_text(encoding='utf-8')
  self.assertIn('const data='+json.dumps(build_data(),ensure_ascii=True)+';',html)
  self.assertIn('href="report.html"',html)
  self.assertIn('href="index.html"',(ROOT/'report.html').read_text(encoding='utf-8'))
if __name__=='__main__': unittest.main()
