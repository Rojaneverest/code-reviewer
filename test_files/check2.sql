-- Test SQL file for GitLab CI integration - MODIFIED
SELECT * FROM products;

DELETE FROM logs;

SELECT * FROM products WHERE product_name LIKE '%chair%';

SELECT user_id, user_name FROM users WHERE is_active = true;

-- New problematic query added
SELECT * FROM sales WITH (NOLOCK);

SELECT * FROM employees;

DELETE FROM logs;

SELECT * FROM products WHERE product_name LIKE '%chair%';

-- Good Practices
SELECT user_id, user_name FROM users WHERE is_active = true;

SELECT p.product_name, c.category_name
FROM products p
JOIN categories c ON p.category_id = c.category_id;

TRUNCATE TABLE temp_data;

SELECT id FROM table1 UNION ALL SELECT id FROM table2;

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

SELECT products.product_name, categories.category_name FROM products JOIN categories ON products.category_id = categories.category_id;

SELECT * FROM products WHERE product_name LIKE '%chair%';