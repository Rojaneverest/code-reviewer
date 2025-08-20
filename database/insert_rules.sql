TRUNCATE TABLE rules RESTART IDENTITY;

INSERT INTO rules (title, description, code_pattern, severity, language, category, practice_type)
VALUES
    -- Bad Practices (with Regex Patterns)
    ('Avoid SELECT *', 'Using SELECT * can cause performance issues and break views or code if the schema changes.', 'select\s+\*\s+from', 'Major', 'SQL', 'Performance', 'bad'),
    ('Avoid Leading Wildcards in LIKE', 'Leading wildcards in LIKE clauses prevent the database from using an index, leading to slow queries.', 'like\s+''%[^'']*%''', 'Major', 'SQL', 'Performance', 'bad'),
    ('Avoid DELETE without WHERE', 'DELETE statements without a WHERE clause will delete all rows in a table. Use TRUNCATE for clarity if this is intended.', 'delete\s+from\s+[a-zA-Z0-9_]+\s*;', 'Major', 'SQL', 'Data Integrity', 'bad'),
    -- FIXED: Simplified the implicit joins pattern
    ('Avoid Implicit Joins', 'Use explicit JOIN syntax instead of comma-separated tables in the FROM clause for better readability and to avoid accidental cross joins.', '(?i)from\s+\w+\s*,\s*\w+', 'Minor', 'SQL', 'Clarity', 'bad'),

    -- Good Practices (with Simple Keywords)
    ('Use Explicit Column Names', 'Always specify the columns you need in a SELECT statement.', 'select', 'Minor', 'SQL', 'Clarity', 'good'),
    ('Use Explicit JOINs', 'Use explicit JOIN syntax for clarity and to prevent accidental cross joins.', 'join', 'Minor', 'SQL', 'Clarity', 'good'),

    -- More Bad Practices
    ('Avoid NOLOCK hint', 'The NOLOCK hint can lead to reading uncommitted data (dirty reads), which can cause data inconsistency.', '\(\s*NOLOCK\s*\)', 'Critical', 'SQL', 'Data Integrity', 'bad'),
    ('Avoid functions on indexed columns', 'Applying functions to indexed columns in a WHERE clause can prevent the optimizer from using the index.', 'WHERE\s+\w+\([^)]+\)\s*=', 'Major', 'SQL', 'Performance', 'bad'),
    ('Use COUNT(1) or COUNT(column) instead of COUNT(*)', 'COUNT(*) can be slower as it may check all columns. Use COUNT(1) for existence checks or COUNT(column) for non-null counts.', 'COUNT\s*\(\s*\*\s*\)', 'Minor', 'SQL', 'Performance', 'bad'),
    ('Avoid HAVING for WHERE conditions', 'HAVING should only be used to filter aggregated results. Use WHERE for row-level filtering before aggregation.', 'having\s+[^=]*$', 'Minor', 'SQL', 'Performance', 'bad'),
    -- FIXED: Simplified the table aliases pattern
    ('Use table aliases in JOINs', 'Using table aliases (e.g., `FROM products p JOIN categories c`) improves readability, especially in complex queries.', '(?i)join\s+\w+\s+on\s+', 'Minor', 'SQL', 'Clarity', 'bad'),

    -- More Good Practices
    ('Use TRUNCATE to clear tables', 'TRUNCATE is faster than DELETE for clearing all rows from a table.', 'truncate\s+table', 'Minor', 'SQL', 'Performance', 'good'),
    ('Use UNION ALL over UNION', 'Use UNION ALL if you do not need to remove duplicate rows, as it is more performant.', 'union\s+all', 'Minor', 'SQL', 'Performance', 'good'),
    ('Use table aliases', 'Using table aliases improves readability in queries with multiple tables.', 'as\s+[a-zA-Z_]', 'Minor', 'SQL', 'Clarity', 'good'),
    ('Use CASE for conditional logic', 'The CASE statement is the standard way to handle conditional logic within SQL queries.', 'case\s+when', 'Minor', 'SQL', 'Clarity', 'good'),
    ('Comment complex queries', 'Adding comments (--) to explain complex logic improves maintainability.', '--', 'Minor', 'SQL', 'Clarity', 'good');
    