"""Reproducible sample data and SQL analytics. Python standard library only."""
import csv
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'data' / 'campus_stock.db'
START, END = '2026-01-01', '2026-06-30'


def connect(path=DB):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    return db


def seed(path=DB):
    """Create the demo once; refuse to overwrite an existing database."""
    path = Path(path)
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    rng = random.Random(2027)
    with connect(path) as db:
        db.executescript((ROOT / 'sql/schema.sql').read_text())
        db.executemany('INSERT INTO suppliers VALUES (?,?,?)', [
            (1,'Campus Supply Co.',5),(2,'Northside Tech',10),(3,'Everyday Goods',3)])
        catalog = [
            ('Spiral notebook','Stationery',1,180,450,240,60),
            ('Gel pen pack','Stationery',1,220,550,230,55),
            ('Highlighter set','Stationery',1,160,425,220,45),
            ('Index cards','Stationery',1,90,250,250,50),
            ('USB-C cable','Technology',2,350,999,210,65),
            ('Wireless mouse','Technology',2,800,1999,200,50),
            ('Laptop sleeve','Technology',2,650,1699,230,45),
            ('USB flash drive','Technology',2,400,1199,190,55),
            ('Water bottle','Essentials',3,500,1499,260,50),
            ('Canvas tote','Essentials',3,350,999,240,45),
            ('Coffee tumbler','Essentials',3,600,1799,230,40),
            ('Snack pack','Essentials',3,150,399,280,60)]
        for pid, (name,cat,supplier,cost,price,stock,point) in enumerate(catalog,1):
            db.execute('INSERT INTO products VALUES (?,?,?,?,?,?,?,?)',
                       (pid,supplier,name,cat,cost,price,stock,point))
        remaining = {i+1:p[5] for i,p in enumerate(catalog)}
        sale_id = 0
        for day in range(181):
            for _ in range(rng.randint(3,7)):
                chosen = rng.sample(range(1,13),rng.randint(1,3))
                items = []
                for pid in chosen:
                    qty = min(rng.randint(1,2),remaining[pid])
                    if qty:
                        remaining[pid] -= qty
                        p = catalog[pid-1]
                        items.append((pid,qty,p[4],p[3]))
                if items:
                    sale_id += 1
                    db.execute('INSERT INTO sales VALUES (?,?)',
                               (sale_id,(date(2026,1,1)+timedelta(days=day)).isoformat()))
                    db.executemany('INSERT INTO sale_items VALUES (?,?,?,?,?)',
                                   [(sale_id,*item) for item in items])
    return True


def analyze(db, start=START, end=END, category='All categories'):
    date.fromisoformat(start)
    date.fromisoformat(end)
    if start > end:
        raise ValueError('Start date must be on or before end date.')
    params = dict(start=start,end=end,category=category)
    products = [dict(r) for r in db.execute((ROOT/'sql/analysis.sql').read_text(),params)]
    trend = [dict(r) for r in db.execute('''
        SELECT substr(s.sold_on,1,7) AS month,
        SUM(i.quantity*i.unit_price_cents) AS revenue_cents
        FROM sales s JOIN sale_items i ON s.id=i.sale_id
        JOIN products p ON p.id=i.product_id
        WHERE s.sold_on BETWEEN :start AND :end
        AND (:category='All categories' OR p.category=:category)
        GROUP BY month ORDER BY month''',params)]
    inventory = [dict(r) for r in db.execute('''SELECT * FROM inventory
        WHERE (:category='All categories' OR category=:category)
        ORDER BY on_hand-reorder_point, name''',params)]
    return dict(products=products,trend=trend,inventory=inventory,
                revenue=sum(p['revenue_cents'] for p in products),
                profit=sum(p['profit_cents'] for p in products),
                units=sum(p['units'] for p in products))


def money(cents):
    return '${:,.2f}'.format(cents/100)


def export_csv(rows,path):
    with open(path,'w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['name','category','units','revenue_cents','profit_cents'])
        writer.writeheader()
        writer.writerows(rows)
