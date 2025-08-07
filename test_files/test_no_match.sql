
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
