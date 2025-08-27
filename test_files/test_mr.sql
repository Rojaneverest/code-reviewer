-- Test SQL file for GitLab CI integration - MODIFIED
SELECT * FROM users;

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