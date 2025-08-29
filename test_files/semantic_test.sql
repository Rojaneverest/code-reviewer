-- This file tests semantic search capabilities by using variations of common SQL patterns

-- Test 1: Semantically similar to "Avoid SELECT *" but written differently
-- This query retrieves every column without explicitly using SELECT *
SELECT u.*, o.*, a.*
FROM users u 
CROSS APPLY orders o
CROSS APPLY addresses a;

-- Test 2: Semantically similar to "Use Explicit Column Names" but with aliases
-- Good practice with clear column selection
SELECT 
    u.user_id AS customer_number,
    u.first_name || ' ' || u.last_name AS full_name,
    o.order_reference AS invoice_number
FROM users u
JOIN orders o ON u.user_id = o.user_id;

-- Test 3: Similar to "Avoid Leading Wildcards" but using different pattern
-- This should trigger the performance warning for leading wildcards
SELECT product_name 
FROM products 
WHERE description SIMILAR TO '%organic%food%';

-- Test 4: Testing JOIN patterns without explicit table aliases
-- Should match with "Use table aliases" rule semantically
SELECT 
    orders.order_date,
    order_items.quantity,
    products.name,
    categories.category_name
FROM orders
INNER JOIN order_items ON orders.order_id = order_items.order_id
INNER JOIN products ON order_items.product_id = products.product_id
INNER JOIN categories ON products.category_id = categories.category_id;

-- Test 5: Complex conditional logic without CASE
-- Semantically similar to "Use CASE for conditional logic"
SELECT 
    product_name,
    IIF(stock_quantity > 100, 'Overstocked',
        IIF(stock_quantity > 50, 'Well Stocked',
            IIF(stock_quantity > 20, 'Low Stock', 'Critical'))) as stock_status
FROM products;

-- Test 6: Implicit cross join variation
-- Semantically similar to "Avoid Implicit Joins"
SELECT customer_name, order_date
FROM customers c, orders o, order_items i
WHERE c.customer_id = o.customer_id
AND o.order_id = i.order_id;

-- Test 7: Function on indexed column variation
-- Similar to "Avoid functions on indexed columns"
SELECT user_id, email
FROM users
WHERE TRIM(LOWER(email)) = 'test@example.com';

-- Test 8: COUNT variation
-- Semantically similar to "Use COUNT(1) or COUNT(column)"
SELECT 
    department,
    COUNT(*) as total_employees,
    COUNT(1) as employee_count,
    COUNT(employee_id) as valid_employees
FROM employees
GROUP BY department;

-- Test 9: HAVING misuse variation
-- Similar to "Avoid HAVING for WHERE conditions"
SELECT product_category, AVG(price)
FROM products
GROUP BY product_category
HAVING product_category NOT IN ('Discontinued', 'Archived');

-- Test 10: Uncommented complex query
-- Should be flagged for missing comments (opposite of "Comment complex queries")
SELECT DISTINCT 
    u.user_id,
    u.email,
    COUNT(o.order_id) order_count,
    SUM(oi.quantity * p.price) total_spent,
    FIRST_VALUE(o.order_date) OVER (PARTITION BY u.user_id ORDER BY o.order_date DESC) last_order_date
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN products p ON oi.product_id = p.product_id
WHERE o.order_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY u.user_id, u.email
HAVING COUNT(o.order_id) > 0;
