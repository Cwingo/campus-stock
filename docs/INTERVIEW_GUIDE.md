# Resume and interview guide

## Resume wording

Use after running and understanding the project. Adapt the verbs to accurately reflect your work, and follow any application rules about AI assistance.

**Campus Stock — Inventory & Sales Analytics | Python, SQL, SQLite, Tkinter**

- Developed an inventory and sales analytics prototype with a four-table relational database, parameterized SQL queries, and a desktop dashboard for product performance and reorder alerts.
- Implemented date/category filtering and CSV export; validated financial calculations and inventory reconciliation with automated tests.

Do not claim real customers, deployment, cost savings, or business improvements. The dataset is simulated. If you are presenting this unmodified scaffold, describe it as an AI-assisted project you studied, rather than implying independent authorship.

## Explain it in 30 seconds

“This project models a campus store. It stores products, suppliers, and sales in SQLite, then uses SQL to calculate revenue, gross profit, and ending stock. The Python interface lets a manager filter sales and identify products at their reorder point. I used simulated data and checked that units sold reconcile with remaining inventory.”

## Questions to prepare for

1. Why separate sales from sale_items? One transaction can contain multiple products without duplicating transaction fields.
2. Why store money as cents? Exact integer arithmetic avoids binary floating-point issues for currency totals.
3. Why capture cost on each sale line? Historical gross profit should not change when current catalog costs change.
4. Why does the inventory panel ignore the date range? It represents ending stock. Historical stock would need an explicit as-of calculation and all stock movements.
5. What does the test with a known sale prove? Three units at $4.50 with $1.80 unit cost must produce $13.50 revenue and $8.10 gross profit.
6. What is missing for a real store? Receipts, returns, transaction-safe stock checks, imports, backup, access controls, and operational validation.
7. What did YOU change? Complete a small extension and explain your own decision, code, and verification.

## Suggested personal extension

Add a stock_receipts table with product, date, quantity, and unit cost; update inventory to include receipts. Test that a receipt increases stock and does not alter historical sales revenue. This makes a useful contribution you can demonstrate yourself.
