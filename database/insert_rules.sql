-- SQL Rules: Performance
INSERT INTO rules (code_pattern, language, category, severity, title, description)
VALUES
    ('SELECT *', 'SQL', 'Performance', 'Major', 'Avoid SELECT *', 'Explicitly list the columns you need instead of using `SELECT *`. This reduces data transfer and improves query readability.'),
    ('LIKE ''%...', 'SQL', 'Performance', 'Major', 'Avoid leading wildcards in LIKE', 'Using a wildcard at the beginning of a LIKE pattern (e.g., `%value`) prevents the database from using an index, leading to a full table scan.'),
    ('IN (SELECT ...)', 'SQL', 'Performance', 'Minor', 'Prefer EXISTS over IN for subqueries', 'For large subqueries, `EXISTS` is often more performant than `IN` because it can stop as soon as it finds a match.'),
    ('DELETE FROM', 'SQL', 'Performance', 'Major', 'Use TRUNCATE for clearing entire tables', '`TRUNCATE TABLE` is faster than `DELETE FROM table` for deleting all rows, as it deallocates data pages with minimal logging.');

-- SQL Rules: Readability & Maintainability
INSERT INTO rules (code_pattern, language, category, severity, title, description)
VALUES
    ('JOIN', 'SQL', 'Readability', 'Minor', 'Use explicit JOIN syntax', 'Use `JOIN` syntax instead of comma-separated tables in the `FROM` clause. It makes the relationships between tables clearer and is the ANSI standard.'),
    ('NOLOCK', 'SQL', 'Best Practice', 'Critical', 'Avoid using NOLOCK hint', 'The `NOLOCK` hint can lead to reading uncommitted data (dirty reads), which can cause data inconsistency and incorrect results.');

-- PySpark Rules: Performance
INSERT INTO rules (code_pattern, language, category, severity, title, description)
VALUES
    ('.collect()', 'PySpark', 'Performance', 'Critical', 'Avoid .collect() on large DataFrames', 'Calling `.collect()` on a large DataFrame can cause an OutOfMemoryError on the driver node. Use `.take()`, `.show()`, or write to a file instead.'),
    ('udf(', 'PySpark', 'Performance', 'Major', 'Prefer built-in functions over UDFs', 'User-Defined Functions (UDFs) in PySpark are a black box to the Catalyst optimizer. Whenever possible, use built-in Spark SQL functions for better performance.'),
    ('.withColumn(', 'PySpark', 'Performance', 'Minor', 'Avoid using .withColumn in a loop', 'Adding columns one by one in a loop can be inefficient. It is better to use `select()` with all new columns defined at once.'),
    ('df.write.format("csv")', 'PySpark', 'Performance', 'Major', 'Use Parquet or ORC for storage', 'Parquet and ORC are columnar storage formats that offer better compression and query performance compared to row-based formats like CSV or JSON.');

-- PySpark Rules: Best Practice
INSERT INTO rules (code_pattern, language, category, severity, title, description)
VALUES
    ('.cache()', 'PySpark', 'Best Practice', 'Major', 'Use .cache() or .persist() wisely', 'Cache DataFrames that are used multiple times in an iterative algorithm. Un-persisting them after use is also important to free up memory.'),
    ('spark.read.csv', 'PySpark', 'Best Practice', 'Minor', 'Define schema when reading data', 'When reading data from sources like CSV or JSON, explicitly defining a schema avoids an extra pass over the data to infer types and prevents potential type mismatches.');
