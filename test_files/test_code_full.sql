-- Bad Practices
SELECT * FROM employees;

DELETE FROM logs;

SELECT * FROM products WHERE product_name LIKE '%chair%';

-- Good Practices
SELECT user_id, user_name FROM users WHERE is_active = true;

SELECT p.product_name, c.category_name
FROM products p
JOIN categories c ON p.category_id = c.category_id;

-- New Bad Practices to test
SELECT * FROM sales WITH (NOLOCK);

SELECT * FROM users WHERE YEAR(creation_date) = 2023;

SELECT COUNT(*) FROM orders;

SELECT customer_id, SUM(total_amount) FROM orders GROUP BY customer_id HAVING total_amount > 100;

SELECT products.product_name, categories.category_name FROM products JOIN categories ON products.category_id = categories.category_id;

-- New Good Practices to test
TRUNCATE TABLE temp_data;

SELECT id FROM table1 UNION ALL SELECT id FROM table2;

SELECT o.order_id, c.customer_name FROM orders AS o JOIN customers AS c ON o.customer_id = c.customer_id;

SELECT order_id, CASE WHEN status = 1 THEN 'Active' ELSE 'Inactive' END AS order_status FROM orders;

-- This query calculates the total sales per region
SELECT region, SUM(sales) FROM sales_data GROUP BY region;
