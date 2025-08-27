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

-- This file contains SQL queries that should NOT trigger any existing rules.
-- It is designed to test the system's ability to handle good code and avoid false positives.

-- A standard, well-formed SELECT statement
SELECT
    customer_id,
    customer_name,
    email
FROM
    customers
WHERE
    registration_date > '2023-01-01';

-- A standard INSERT statement
INSERT INTO products (product_name, category_id, price)
VALUES ('New Awesome Gadget', 5, 99.99);

-- A standard UPDATE statement with a WHERE clause
UPDATE
    orders
SET
    status = 'shipped'
WHERE
    order_id = 1024;
    
-- A more complex query with a JOIN and aliases (good practice)
SELECT
    o.order_id,
    c.customer_name,
    p.product_name
FROM
    orders AS o
JOIN
    customers AS c ON o.customer_id = c.customer_id
JOIN
    order_items AS oi ON o.order_id = oi.order_id
JOIN
    products AS p ON oi.product_id = p.product_id
WHERE
    o.order_date BETWEEN '2023-06-01' AND '2023-06-30';

-- A query using a window function (not covered by current rules)
SELECT
    employee_name,
    department,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) as salary_rank
FROM
    employees;

-- A new bad practice (correlated subquery) not in the rules table
SELECT
    c.customer_name
FROM
    customers c
WHERE
    EXISTS (
        SELECT 1
        FROM orders o
        WHERE o.customer_id = c.customer_id AND o.order_date > '2023-11-01'
    );