-- Bad Practices
SELECT * FROM employees;

DELETE FROM logs;

SELECT * FROM products WHERE product_name LIKE '%chair%';

-- Good Practices
SELECT user_id, user_name FROM users WHERE is_active = true;

SELECT p.product_name, c.category_name
FROM products p
JOIN categories c ON p.category_id = c.category_id;
