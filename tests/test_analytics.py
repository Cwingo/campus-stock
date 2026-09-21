import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import analyze, connect, seed

class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/'test.db'
        seed(self.path)
        self.db=connect(self.path)
    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()
    def test_inventory_reconciles(self):
        self.assertEqual(self.db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
        self.assertFalse(self.db.execute('PRAGMA foreign_key_check').fetchall())
        self.assertGreaterEqual(self.db.execute('SELECT MIN(on_hand) FROM inventory').fetchone()[0],0)
        initial=self.db.execute('SELECT SUM(opening_stock) FROM products').fetchone()[0]
        remaining=self.db.execute('SELECT SUM(on_hand) FROM inventory').fetchone()[0]
        self.assertEqual(initial-remaining,analyze(self.db)['units'])
    def test_category_totals_partition_revenue(self):
        total=analyze(self.db)['revenue']
        self.assertEqual(total,sum(analyze(self.db,category=c)['revenue'] for c in ['Stationery','Technology','Essentials']))
    def test_date_filters_and_empty_period(self):
        whole=analyze(self.db)
        first=analyze(self.db,end='2026-03-31')
        second=analyze(self.db,start='2026-04-01')
        self.assertEqual(whole['revenue'],first['revenue']+second['revenue'])
        empty=analyze(self.db,start='2027-01-01',end='2027-12-31')
        self.assertEqual(empty['revenue'],0)
        self.assertEqual(empty['products'],[])
        self.assertEqual(empty['inventory'],whole['inventory'])
        with self.assertRaises(ValueError):
            analyze(self.db,start='2026-07-01',end='2026-01-01')
    def test_known_transaction_math(self):
        self.db.execute('DELETE FROM sale_items')
        self.db.execute('DELETE FROM sales')
        self.db.execute("INSERT INTO sales VALUES (1,'2026-01-01')")
        self.db.execute('INSERT INTO sale_items VALUES (1,1,3,450,180)')
        result=analyze(self.db,start='2026-01-01',end='2026-01-01')
        self.assertEqual((result['revenue'],result['profit'],result['units']),(1350,810,3))
    def test_seed_preserves_existing_database(self):
        self.assertFalse(seed(self.path))

if __name__=='__main__':
    unittest.main()
