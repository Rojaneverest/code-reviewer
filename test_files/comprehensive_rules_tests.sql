-- Comprehensive SQL Test File for New Rules
-- This file contains examples that should trigger the 20 new rules we added

-- Security Issues
-- 1. Dynamic SQL Construction (Critical)
DECLARE @query NVARCHAR(500);
SET @query = 'SELECT * FROM users WHERE name = ''' + @userName + '''';
EXECUTE(@query);

-- 2. Non-parameterized query (should be flagged as missing parameterization)
SELECT * FROM orders WHERE user_id = 12345 AND status = 'pending';

-- 3. Excessive privileges (Critical)
GRANT ALL PRIVILEGES ON sales_database.* TO 'app_user'@'localhost';

-- 4. Good: Specific column permissions (should be recognized as good practice)
GRANT SELECT (id, name, email) ON users TO 'readonly_user'@'%';

-- Performance Issues
-- 5. Correlated subquery (Major performance issue)
SELECT o.order_id, o.total_amount
FROM orders o
WHERE o.user_id IN (
    SELECT u.id 
    FROM users u 
    WHERE u.status = 'active' 
    AND u.registration_date > '2023-01-01'
    AND u.id = o.user_id  -- This makes it correlated
);

-- 6. Good: Using EXISTS instead of IN (should be recognized as good practice)
SELECT o.order_id, o.total_amount
FROM orders o
WHERE EXISTS (
    SELECT 1 
    FROM users u 
    WHERE u.id = o.user_id 
    AND u.status = 'active'
);

-- 7. OR condition that prevents index usage
SELECT * FROM products 
WHERE category = 'electronics' 
   OR category = 'books' 
   OR category = 'music';

-- 8. Good: Using LIMIT for large results (should be recognized)
SELECT product_name, price, description
FROM products 
ORDER BY created_date DESC 
LIMIT 50;

-- 9. Expensive DISTINCT on large table
SELECT DISTINCT category, brand, supplier_id
FROM products 
WHERE price BETWEEN 10 AND 1000
AND created_date > '2023-01-01';

-- 10. Good: Covering index creation (should be recognized)
CREATE INDEX IX_Orders_UserStatus_Covering 
ON orders (user_id, status) 
INCLUDE (order_date, total_amount, shipping_address);

-- Data Integrity Issues
-- 11. Good: Transaction usage (should be recognized)
BEGIN TRANSACTION;
    UPDATE account_balances SET balance = balance - 500 WHERE account_id = 101;
    UPDATE account_balances SET balance = balance + 500 WHERE account_id = 102;
    INSERT INTO transaction_log (from_account, to_account, amount) VALUES (101, 102, 500);
COMMIT;

-- 12. Implicit data type conversion
SELECT order_id, customer_name, total_amount
FROM orders 
WHERE order_id = '12345'  -- String compared to numeric ID
AND created_date = '2023-12-01';

-- 13. Good: CHECK constraint (should be recognized)
ALTER TABLE products 
ADD CONSTRAINT CK_Products_PositivePrice 
CHECK (price > 0 AND discount_percentage BETWEEN 0 AND 100);

-- 14. Good: Foreign key constraint (should be recognized)
ALTER TABLE order_items 
ADD CONSTRAINT FK_OrderItems_Orders 
FOREIGN KEY (order_id) REFERENCES orders(order_id)
ON DELETE CASCADE;

-- Maintainability Issues
-- 15. Poor table aliases (single letters)
SELECT o.id, u.name, p.price
FROM orders AS o
JOIN users AS u ON o.user_id = u.id
JOIN order_items AS oi ON o.id = oi.order_id
JOIN products AS p ON oi.product_id = p.id;

-- 16. Hard-coded values scattered throughout
SELECT customer_id, order_total
FROM orders 
WHERE order_status = 'shipped' 
AND shipping_method = 'express'
AND payment_status = 'completed'
AND order_date >= '2024-01-01';

-- 17. Good: Consistent naming convention (should be recognized)
CREATE TABLE user_login_history (
    login_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    login_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- 18. Magic numbers in queries
SELECT TOP 2500 customer_id, total_purchases
FROM customer_analytics
WHERE last_purchase_date >= DATEADD(day, -365, GETDATE())
ORDER BY total_purchases DESC;

-- 19. Good: CTE usage for complex query (should be recognized)
WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', order_date) as sales_month,
        SUM(total_amount) as monthly_total,
        COUNT(*) as order_count
    FROM orders 
    WHERE order_date >= '2023-01-01'
    GROUP BY DATE_TRUNC('month', order_date)
),
sales_trends AS (
    SELECT 
        sales_month,
        monthly_total,
        LAG(monthly_total) OVER (ORDER BY sales_month) as previous_month_total
    FROM monthly_sales
)
SELECT 
    sales_month,
    monthly_total,
    CASE 
        WHEN previous_month_total IS NULL THEN 0
        ELSE ((monthly_total - previous_month_total) / previous_month_total) * 100
    END as growth_percentage
FROM sales_trends
ORDER BY sales_month;

-- 20. Good: Documentation for schema changes (should be recognized)
-- Migration v2.1.0: Add customer preferences and notification settings
-- This migration adds support for personalized user experience
CREATE TABLE customer_preferences (
    preference_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    notification_email BOOLEAN DEFAULT true,
    newsletter_subscription BOOLEAN DEFAULT false,
    preferred_language VARCHAR(5) DEFAULT 'en_US',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Additional edge cases that might be interesting
-- Complex query combining multiple issues
SELECT DISTINCT *
FROM orders o, customers c, products p
WHERE o.customer_id = c.customer_id
AND UPPER(c.email) = 'TEST@EXAMPLE.COM'
AND p.category = 'electronics' OR p.category = 'books'
AND o.total_amount > 100;

-- Dynamic SQL with potential injection
DECLARE @searchTerm VARCHAR(100) = 'electronics';
DECLARE @sql NVARCHAR(MAX) = 'SELECT * FROM products WHERE category = ''' + @searchTerm + ''' ORDER BY price';
EXEC sp_executesql @sql;
