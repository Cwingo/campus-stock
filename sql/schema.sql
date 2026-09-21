PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS suppliers (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, lead_days INTEGER NOT NULL CHECK(lead_days >= 0)
);
CREATE TABLE IF NOT EXISTS products (
 id INTEGER PRIMARY KEY, supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
 name TEXT NOT NULL UNIQUE, category TEXT NOT NULL,
 cost_cents INTEGER NOT NULL CHECK(cost_cents >= 0),
 price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
 opening_stock INTEGER NOT NULL CHECK(opening_stock >= 0),
 reorder_point INTEGER NOT NULL CHECK(reorder_point >= 0)
);
CREATE TABLE IF NOT EXISTS sales (
 id INTEGER PRIMARY KEY, sold_on TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sale_items (
 sale_id INTEGER NOT NULL REFERENCES sales(id),
 product_id INTEGER NOT NULL REFERENCES products(id),
 quantity INTEGER NOT NULL CHECK(quantity > 0),
 unit_price_cents INTEGER NOT NULL CHECK(unit_price_cents >= 0),
 unit_cost_cents INTEGER NOT NULL CHECK(unit_cost_cents >= 0),
 PRIMARY KEY(sale_id, product_id)
);
CREATE INDEX IF NOT EXISTS sales_date_idx ON sales(sold_on);
CREATE VIEW IF NOT EXISTS inventory AS
 SELECT p.id, p.name, p.category, s.name AS supplier, s.lead_days,
 p.opening_stock - COALESCE(SUM(i.quantity),0) AS on_hand,
 p.reorder_point, p.cost_cents
 FROM products p JOIN suppliers s ON s.id=p.supplier_id
 LEFT JOIN sale_items i ON i.product_id=p.id GROUP BY p.id;
