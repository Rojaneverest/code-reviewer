-- Test SQL file for GitLab CI integration
SELECT * FROM users;

DELETE FROM logs;

SELECT * FROM products WHERE product_name LIKE '%chair%';

SELECT user_id, user_name FROM users WHERE is_active = true;
