# Business requirements and data dictionary

## Scenario

A fictional campus shop has sales records but needs a repeatable way to review performance and prioritize restocking. The store manager is the intended user. The dataset covers January 1–June 30, 2026; the year is a fixed demo period, unrelated to a student's graduation date.

## Acceptance criteria

| Requirement | Expected behavior |
|---|---|
| Summarize sales | Display revenue, gross profit, and units for selected dates/category |
| Filter dates | Include both boundary dates; reject invalid/reversed dates |
| Compare products | Sort products by revenue descending |
| Identify stock risk | Flag on-hand quantity at or below the reorder point |
| Export analysis | Export the displayed product rows with stable CSV headers |
| Handle no sales | Show zero sales metrics, empty product rows, and an explicit chart message |
| Reproduce results | Generate the same dataset from seed 2027 |

## Metrics

- Revenue = sum(quantity × unit price).
- Gross profit = sum(quantity × (unit price − unit cost)).
- Units = sum(quantity).
- On hand = opening stock − all units sold, through the dataset's end.
- Reorder alert = on hand ≤ reorder point; zero stock is labeled separately.

## Tables

| Table | Grain | Key and fields |
|---|---|---|
| suppliers | One supplier | id; unique name; lead_days |
| products | One product | id; supplier_id; name; category; cost_cents; price_cents; opening_stock; reorder_point |
| sales | One transaction | id; sold_on (ISO date) |
| sale_items | One product per transaction | (sale_id, product_id); quantity; unit_price_cents; unit_cost_cents |

Supplier lead time is retained for a possible future replenishment model; it is not used to calculate current fixed reorder points. No personal or real business data is included.

## Verification

Automated tests cover database integrity, stock reconciliation, nonnegative generated stock, known transaction arithmetic, category/date partitions, inclusive date boundaries, empty sales ranges, invalid date ordering, and preservation of an existing database.
