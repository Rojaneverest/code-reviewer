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

SELECT * FROM employees;