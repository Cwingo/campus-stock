-- Revenue, gross profit, and units by product in an inclusive date window.
-- Store money as integer cents; costs/prices are captured at time of sale.
SELECT p.name, p.category, SUM(i.quantity) AS units,
 SUM(i.quantity*i.unit_price_cents) AS revenue_cents,
 SUM(i.quantity*(i.unit_price_cents-i.unit_cost_cents)) AS profit_cents
FROM sale_items i JOIN sales s ON s.id=i.sale_id
JOIN products p ON p.id=i.product_id
WHERE s.sold_on BETWEEN :start AND :end
AND (:category='All categories' OR p.category=:category)
GROUP BY p.id ORDER BY revenue_cents DESC, p.name;
