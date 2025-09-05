-- Additional 20 SQL Rules for Code Review
-- These rules cover performance, security, maintainability, and best practices

INSERT INTO rules (title, description, code_pattern, severity, language, category, practice_type, example_snippet)
VALUES
    -- Security Rules
    ('Avoid Dynamic SQL Construction', 'Building SQL strings through concatenation can lead to SQL injection vulnerabilities. Use parameterized queries instead.', 'execute\s*\(\s*[''"].*\+.*[''"]', 'Critical', 'SQL', 'Security', 'bad', 'EXECUTE(''SELECT * FROM users WHERE id = '' + @userId);'),
    ('Use Parameterized Queries', 'Always use parameterized queries to prevent SQL injection attacks.', '@\w+|:\w+|\$\d+|\?', 'Major', 'SQL', 'Security', 'good', 'SELECT * FROM users WHERE id = @userId;'),
    ('Avoid GRANT ALL Privileges', 'Granting ALL privileges violates the principle of least privilege. Grant only necessary permissions.', 'grant\s+all', 'Critical', 'SQL', 'Security', 'bad', 'GRANT ALL ON database.* TO user@host;'),
    ('Use Specific Column Permissions', 'Grant permissions on specific columns rather than entire tables when possible.', 'grant\s+select\s*\([^)]+\)', 'Major', 'SQL', 'Security', 'good', 'GRANT SELECT (id, name) ON users TO app_user;'),

    -- Performance Rules
    ('Avoid Correlated Subqueries', 'Correlated subqueries execute once for each row and can be very slow. Consider using JOINs or window functions instead.', 'where\s+\w+\s+in\s*\(\s*select.*where.*\.\w+\s*=\s*\w+\.\w+', 'Major', 'SQL', 'Performance', 'bad', 'SELECT * FROM orders o WHERE o.user_id IN (SELECT u.id FROM users u WHERE u.status = ''active'' AND u.id = o.user_id);'),
    ('Use EXISTS instead of IN for Subqueries', 'EXISTS can be more efficient than IN for subqueries, especially with large datasets.', 'exists\s*\(\s*select', 'Minor', 'SQL', 'Performance', 'good', 'SELECT * FROM orders o WHERE EXISTS (SELECT 1 FROM users u WHERE u.id = o.user_id AND u.status = ''active'');'),
    ('Avoid OR in WHERE Clauses', 'OR conditions can prevent index usage. Consider using UNION or restructuring the query.', 'where.*or.*=', 'Minor', 'SQL', 'Performance', 'bad', 'SELECT * FROM products WHERE category = ''electronics'' OR category = ''books'';'),
    ('Use LIMIT for Large Result Sets', 'Always use LIMIT or TOP to restrict result sets when not all rows are needed.', 'limit\s+\d+|top\s+\d+', 'Minor', 'SQL', 'Performance', 'good', 'SELECT * FROM products ORDER BY created_date DESC LIMIT 100;'),
    ('Avoid SELECT DISTINCT with Large Tables', 'DISTINCT requires sorting/grouping operations which can be expensive. Consider if DISTINCT is really necessary.', 'select\s+distinct.*from\s+\w+\s+where', 'Minor', 'SQL', 'Performance', 'bad', 'SELECT DISTINCT category FROM products WHERE price > 100;'),
    ('Use Covering Indexes', 'Include frequently queried columns in index definitions to avoid key lookups.', 'create.*index.*include\s*\(', 'Major', 'SQL', 'Performance', 'good', 'CREATE INDEX IX_Orders_UserDate INCLUDE (total_amount, status) ON orders (user_id, order_date);'),

    -- Data Integrity Rules
    ('Always Use Transactions for Multi-Statement Operations', 'Wrap multiple related statements in transactions to ensure data consistency.', 'begin\s+transaction|start\s+transaction', 'Major', 'SQL', 'Data Integrity', 'good', 'BEGIN TRANSACTION; UPDATE accounts SET balance = balance - 100 WHERE id = 1; UPDATE accounts SET balance = balance + 100 WHERE id = 2; COMMIT;'),
    ('Avoid Implicit Data Type Conversions', 'Implicit conversions can lead to performance issues and unexpected results. Be explicit with data types.', 'where\s+\w+\s*=\s*[''"][0-9]+[''"]', 'Minor', 'SQL', 'Data Integrity', 'bad', 'SELECT * FROM orders WHERE order_id = ''123'';'),
    ('Use CHECK Constraints', 'CHECK constraints help maintain data integrity at the database level.', 'check\s*\(.*\)', 'Major', 'SQL', 'Data Integrity', 'good', 'ALTER TABLE products ADD CONSTRAINT CK_Price CHECK (price > 0);'),
    ('Always Use Foreign Key Constraints', 'Foreign key constraints ensure referential integrity between related tables.', 'foreign\s+key.*references', 'Major', 'SQL', 'Data Integrity', 'good', 'ALTER TABLE orders ADD CONSTRAINT FK_Orders_Users FOREIGN KEY (user_id) REFERENCES users(id);'),

    -- Maintainability Rules
    ('Use Meaningful Table Aliases', 'Use descriptive aliases that make the query more readable rather than single letters.', 'from\s+\w+\s+as\s+[a-z]\s', 'Minor', 'SQL', 'Clarity', 'bad', 'SELECT o.id FROM orders AS o JOIN users AS u ON o.user_id = u.id;'),
    ('Avoid Hard-coded Values', 'Use variables or constants instead of hard-coded values for better maintainability.', 'where.*=\s*[''"][^''\"]*[''"]', 'Minor', 'SQL', 'Maintainability', 'bad', 'SELECT * FROM products WHERE status = ''active'' AND category = ''electronics'';'),
    ('Use Consistent Naming Conventions', 'Follow consistent naming conventions for tables, columns, and other database objects.', 'create\s+table\s+[A-Z]', 'Minor', 'SQL', 'Maintainability', 'good', 'CREATE TABLE user_profiles (user_id INT, profile_data JSON);'),
    ('Avoid Magic Numbers', 'Replace magic numbers with named constants or variables for better code readability.', 'limit\s+[0-9]{2,}|top\s+[0-9]{2,}', 'Minor', 'SQL', 'Maintainability', 'bad', 'SELECT * FROM products ORDER BY price DESC LIMIT 1000;'),
    ('Use CTEs for Complex Queries', 'Common Table Expressions (CTEs) make complex queries more readable and maintainable.', 'with\s+\w+\s+as\s*\(', 'Major', 'SQL', 'Clarity', 'good', 'WITH active_users AS (SELECT id FROM users WHERE status = ''active'') SELECT * FROM orders WHERE user_id IN (SELECT id FROM active_users);'),
    ('Document Schema Changes', 'Always document significant schema changes with comments in migration scripts.', '--.*alter|--.*create|--.*drop', 'Major', 'SQL', 'Maintainability', 'good', '-- Migration: Add user preferences table for personalization feature\nCRETE TABLE user_preferences (id SERIAL PRIMARY KEY, user_id INT, preferences JSON);');
