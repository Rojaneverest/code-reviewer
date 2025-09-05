TRUNCATE TABLE rules RESTART IDENTITY;

INSERT INTO rules (title, description, code_pattern, severity, language, category, practice_type, example_snippet)
VALUES
    -- Bad Practices (with Regex Patterns)
    ('Avoid SELECT *', 'Using SELECT * can cause performance issues and break views or code if the schema changes.', 'select\s+\*\s+from', 'Major', 'SQL', 'Performance', 'bad', 'SELECT * FROM users;'),
    ('Avoid Leading Wildcards in LIKE', 'Leading wildcards in LIKE clauses prevent the database from using an index, leading to slow queries.', 'like\s+''%[^'']*%''', 'Major', 'SQL', 'Performance', 'bad', 'SELECT * FROM users WHERE name LIKE ''%John%'';'),
    ('Avoid DELETE without WHERE', 'DELETE statements without a WHERE clause will delete all rows in a table. Use TRUNCATE for clarity if this is intended.', 'delete\s+from\s+[a-zA-Z0-9_]+\s*;', 'Major', 'SQL', 'Data Integrity', 'bad', 'DELETE FROM users;'),
    -- FIXED: Simplified the implicit joins pattern
    ('Avoid Implicit Joins', 'Use explicit JOIN syntax instead of comma-separated tables in the FROM clause for better readability and to avoid accidental cross joins.', '(?i)from\s+\w+\s*,\s*\w+', 'Minor', 'SQL', 'Clarity', 'bad', 'SELECT * FROM users, orders WHERE users.id = orders.user_id;'),

    -- Good Practices (with Simple Keywords)
    ('Use Explicit Column Names', 'Always specify the columns you need in a SELECT statement.', 'select', 'Minor', 'SQL', 'Clarity', 'good', 'SELECT id, name, email FROM users;'),
    ('Use Explicit JOINs', 'Use explicit JOIN syntax for clarity and to prevent accidental cross joins.', 'join', 'Minor', 'SQL', 'Clarity', 'good', 'SELECT u.name, o.order_date FROM users u JOIN orders o ON u.id = o.user_id;'),

    -- More Bad Practices
    ('Avoid NOLOCK hint', 'The NOLOCK hint can lead to reading uncommitted data (dirty reads), which can cause data inconsistency.', '\(\s*NOLOCK\s*\)', 'Critical', 'SQL', 'Data Integrity', 'bad', 'SELECT * FROM users WITH (NOLOCK);'),
    ('Avoid functions on indexed columns', 'Applying functions to indexed columns in a WHERE clause can prevent the optimizer from using the index.', 'WHERE\s+\w+\([^)]+\)\s*=', 'Major', 'SQL', 'Performance', 'bad', 'SELECT * FROM users WHERE UPPER(email) = ''USER@EXAMPLE.COM'';'),
    ('Use COUNT(1) or COUNT(column) instead of COUNT(*)', 'COUNT(*) can be slower as it may check all columns. Use COUNT(1) for existence checks or COUNT(column) for non-null counts.', 'COUNT\s*\(\s*\*\s*\)', 'Minor', 'SQL', 'Performance', 'bad', 'SELECT COUNT(*) FROM users;'),
    ('Avoid HAVING for WHERE conditions', 'HAVING should only be used to filter aggregated results. Use WHERE for row-level filtering before aggregation.', 'having\s+[^=]*$', 'Minor', 'SQL', 'Performance', 'bad', 'SELECT department, COUNT(*) FROM employees HAVING department = ''Sales'';'),
    -- FIXED: Simplified the table aliases pattern
    ('Use table aliases in JOINs', 'Using table aliases (e.g., `FROM products p JOIN categories c`) improves readability, especially in complex queries.', '(?i)join\s+\w+\s+on\s+', 'Minor', 'SQL', 'Clarity', 'bad', 'SELECT orders.id FROM orders JOIN order_items ON orders.id = order_items.order_id;'),

    -- More Good Practices
    ('Use TRUNCATE to clear tables', 'TRUNCATE is faster than DELETE for clearing all rows from a table.', 'truncate\s+table', 'Minor', 'SQL', 'Performance', 'good', 'TRUNCATE TABLE temp_logs;'),
    ('Use UNION ALL over UNION', 'Use UNION ALL if you do not need to remove duplicate rows, as it is more performant.', 'union\s+all', 'Minor', 'SQL', 'Performance', 'good', 'SELECT id FROM current_users UNION ALL SELECT id FROM archived_users;'),
    ('Use table aliases', 'Using table aliases improves readability in queries with multiple tables.', 'as\s+[a-zA-Z_]', 'Minor', 'SQL', 'Clarity', 'good', 'SELECT u.name, o.order_date FROM users AS u JOIN orders AS o ON u.id = o.user_id;'),
    ('Use CASE for conditional logic', 'The CASE statement is the standard way to handle conditional logic within SQL queries.', 'case\s+when', 'Minor', 'SQL', 'Clarity', 'good', 'SELECT name, CASE WHEN age < 18 THEN ''Minor'' ELSE ''Adult'' END AS age_group FROM users;'),
    ('Comment complex queries', 'Adding comments (--) to explain complex logic improves maintainability.', '--', 'Minor', 'SQL', 'Clarity', 'good', '-- Get active users who have made purchases in last 30 days\nSELECT DISTINCT u.id FROM users u JOIN orders o ON u.id = o.user_id WHERE o.order_date >= DATEADD(day, -30, GETDATE());'),
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
    ('Document Schema Changes', 'Always document significant schema changes with comments in migration scripts.', '--.*alter|--.*create|--.*drop', 'Major', 'SQL', 'Maintainability', 'good', '-- Migration: Add user preferences table for personalization feature\nCRETE TABLE user_preferences (id SERIAL PRIMARY KEY, user_id INT, preferences JSON);'),
    ('Detect Cartesian Products', 
    'Queries with multiple tables but missing JOIN conditions create Cartesian products, exponentially increasing result sets and severely impacting performance. Each row from the first table is combined with every row from other tables.',
    '(?i)from\s+\w+(\s*,\s*\w+)+(?!.*where\s+.*=.*\..*)', 
    'Critical', 
    'SQL', 
    'Performance', 
    'bad', 
    'SELECT * FROM users, orders, products; -- Creates users×orders×products combinations'),

    ('Cartesian Product with Insufficient Conditions',
    'Multiple tables joined with insufficient WHERE conditions to prevent Cartesian products. Ensure each table relationship has proper join conditions.',
    '(?i)from\s+(\w+\s+\w+\s*,\s*)+(\w+\s+\w+)(?=.*where)(?!.*\1\.\w+\s*=\s*\2\.\w+)',
    'Major',
    'SQL',
    'Performance', 
    'bad',
    'SELECT * FROM users u, orders o WHERE u.status = ''active''; -- Missing join condition between u and o'),
    ('Avoid Mixed Join Syntax',
    'Mixing comma-separated tables with explicit JOIN syntax in the same query reduces readability and increases the risk of errors. Use consistent JOIN syntax throughout.',
    '(?i)from\s+[^;]*,\s*[^;]*\s+(inner\s+join|left\s+join|right\s+join|full\s+join|join)',
    'Minor',
    'SQL',
    'Clarity',
    'bad',
    'SELECT * FROM users u, orders o JOIN products p ON o.product_id = p.id WHERE u.id = o.user_id;'),

-- Another pattern for mixed syntax
    ('Inconsistent Join Conventions',
    'Query mixes explicit JOIN keywords with comma-separated table syntax. Choose one approach consistently for better maintainability.',
    '(?i)(join\s+\w+\s+\w+\s+on\s+[^;]*from\s+[^;]*,|from\s+[^;]*,\s*[^;]*join\s+)',
    'Minor',
    'SQL',
    'Clarity',
    'bad',
    'SELECT * FROM users u JOIN orders o ON u.id = o.user_id, products p WHERE o.product_id = p.id;'),

    ('Avoid Functions on Columns in WHERE Clauses',
    'Using functions on columns in WHERE clauses prevents index usage and forces full table scans. Consider functional indexes or rewrite the condition.',
    '(?i)where\s+[^;]*\b(upper|lower|substring|left|right|trim|ltrim|rtrim|datepart|year|month|day)\s*\(\s*\w+\.\w+\s*\)',
    'Major',
    'SQL',
    'Performance',
    'bad',
    'SELECT * FROM users WHERE UPPER(email) = ''JOHN@EXAMPLE.COM'';'),

-- Specific date function pattern
    ('Avoid Date Functions on Columns in WHERE',
    'Using date functions like YEAR(), MONTH(), DAY() on date columns prevents index usage. Use date ranges instead.',
    '(?i)where\s+[^;]*(year|month|day|datepart)\s*\(\s*\w+\.?\w*\s*\)\s*(=|<|>|<=|>=)',
    'Major',
    'SQL',
    'Performance',
    'bad',
    'SELECT * FROM orders WHERE YEAR(order_date) = 2023; -- Use order_date >= ''2023-01-01'' AND order_date < ''2024-01-01'''),

-- String function pattern
    ('Avoid String Functions on Indexed Columns',
    'Using UPPER(), LOWER(), TRIM() functions on columns prevents index usage. Consider case-insensitive indexes or store data in consistent format.',
    '(?i)where\s+[^;]*(upper|lower|trim|ltrim|rtrim)\s*\(\s*[\w.]+\s*\)\s*(=|like|in)',
    'Major',
    'SQL',
    'Performance',
    'bad',
    'SELECT * FROM products WHERE LOWER(category) = ''electronics'';'),

-- Mathematical functions
    ('Avoid Mathematical Functions on Columns in WHERE',
    'Mathematical operations on columns in WHERE clauses prevent index usage. Rearrange the equation to isolate the column.',
    '(?i)where\s+[^;]*(abs|round|ceiling|floor|sqrt)\s*\(\s*[\w.]+\s*\)\s*(=|<|>|<=|>=)',
    'Major',
    'SQL',
    'Performance',
    'bad',
    'SELECT * FROM products WHERE ABS(price - discount) > 100; -- Use price > discount + 100 OR price < discount - 100'),

    ('Cartesian Product Risk Assessment',
    'Query structure suggests potential Cartesian product. Verify that all table relationships have appropriate join conditions.',
    '(?i)(?=.*from\s+\w+(\s+\w+)?\s*(?:,\s*\w+(?:\s+\w+)?){2,})(?!.*(?:inner\s+join|left\s+join|right\s+join|full\s+join|cross\s+join))',
    'Critical',
    'SQL',
    'Performance',
    'bad',
    'FROM users u, orders o, order_items oi, products p -- Potential 4-way Cartesian product'),

    -- Nested function calls
    ('Nested Functions in WHERE Clause',
    'Nested function calls on columns severely impact performance by preventing any index usage and requiring complex calculations for each row.',
    '(?i)where\s+[^;]*\b\w+\s*\(\s*\w+\s*\(\s*[\w.]+\s*\)\s*\)',
    'Critical',
    'SQL',
    'Performance',
    'bad',
    'WHERE YEAR(DATE(created_timestamp)) = 2023'),

    -- OR conditions with functions
    ('Functions in OR Conditions',
    'Functions used in OR conditions compound performance issues by preventing index usage across multiple conditions.',
    '(?i)(where|and|or)\s+[^;]*\b\w+\s*\(\s*[\w.]+\s*\)[^;]*\s+or\s+',
    'Major',
    'SQL',
    'Performance',
    'bad',
    'WHERE UPPER(first_name) = ''JOHN'' OR UPPER(last_name) = ''DOE'''),

    ('Proper JOIN Syntax Usage',
    'Using explicit JOIN syntax with proper ON conditions prevents Cartesian products and improves query readability.',
    '(?i)(inner\s+join|left\s+join|right\s+join)\s+\w+\s+\w+\s+on\s+\w+\.\w+\s*=\s*\w+\.\w+',
    'Minor',
    'SQL',
    'Performance',
    'good',
    'FROM users u INNER JOIN orders o ON u.id = o.user_id'),

    ('Index-Friendly WHERE Conditions',
    'Using direct column comparisons or range conditions allows efficient index usage.',
    '(?i)where\s+[\w.]+\s+(=|<|>|<=|>=|between|in)\s+',
    'Minor',
    'SQL',
    'Performance',
    'good',
    'WHERE order_date >= ''2023-01-01'' AND order_date < ''2024-01-01'''),

    ('Functional Index Usage',
    'When functions on columns are necessary, consider creating functional indexes to maintain performance.',
    '(?i)create\s+index\s+\w+\s+on\s+\w+\s*\(\s*\w+\s*\(',
    'Minor',
    'SQL',
    'Performance',
    'good',
    'CREATE INDEX ix_upper_email ON users (UPPER(email))');