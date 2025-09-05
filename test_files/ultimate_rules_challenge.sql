-- Ultimate SQL Rules Challenge
-- This file contains comprehensive examples to test all 36 rules across all categories
-- Categories: Performance, Security, Data Integrity, Clarity, Maintainability

-- ========================================
-- PERFORMANCE RULES CHALLENGES (Rules 1, 2, 8-10, 21-26)
-- ========================================

-- Rule 1: Avoid SELECT * (Major - Performance)
SELECT * FROM massive_transactions_table WHERE date_created > '2024-01-01';

-- Rule 2: Avoid Leading Wildcards in LIKE (Major - Performance) 
SELECT customer_id, email FROM users WHERE email LIKE '%@gmail.com%';

-- Rule 8: Avoid functions on indexed columns (Major - Performance)
SELECT order_id, total FROM orders WHERE YEAR(order_date) = 2024 AND MONTH(order_date) = 12;

-- Rule 9: Use COUNT(1) or COUNT(column) instead of COUNT(*) (Minor - Performance)
SELECT department_name, COUNT(*) as total_employees, AVG(salary) 
FROM employees 
GROUP BY department_name 
HAVING COUNT(*) > 50;

-- Rule 10: Avoid HAVING for WHERE conditions (Minor - Performance)
SELECT product_category, AVG(price) as avg_price
FROM products 
GROUP BY product_category
HAVING product_category IN ('Electronics', 'Books', 'Clothing');

-- Rule 21: Avoid Correlated Subqueries (Major - Performance)
SELECT e.employee_id, e.first_name, e.last_name, e.salary
FROM employees e
WHERE e.salary > (
    SELECT AVG(e2.salary) 
    FROM employees e2 
    WHERE e2.department_id = e.department_id
    AND e2.hire_date < e.hire_date
);

-- Rule 22: Use EXISTS instead of IN for Subqueries (Minor - Performance) - BAD EXAMPLE
SELECT order_id, customer_id, total_amount
FROM orders
WHERE customer_id IN (
    SELECT customer_id 
    FROM customers 
    WHERE registration_date > '2023-01-01' 
    AND status = 'premium'
    AND country = 'USA'
);

-- Rule 22: GOOD EXAMPLE - Using EXISTS
SELECT order_id, customer_id, total_amount
FROM orders o
WHERE EXISTS (
    SELECT 1 
    FROM customers c 
    WHERE c.customer_id = o.customer_id
    AND c.registration_date > '2023-01-01' 
    AND c.status = 'premium'
    AND c.country = 'USA'
);

-- Rule 23: Avoid OR in WHERE Clauses (Minor - Performance)
SELECT product_id, product_name, price
FROM products 
WHERE category = 'electronics' 
   OR category = 'computers' 
   OR category = 'phones' 
   OR category = 'tablets'
   OR price BETWEEN 100 AND 500;

-- Rule 24: Use LIMIT for Large Result Sets (Minor - Performance) - GOOD EXAMPLE
SELECT customer_name, email, phone, address
FROM customers 
WHERE registration_date >= '2024-01-01'
ORDER BY registration_date DESC
LIMIT 1000;

-- Rule 25: Avoid SELECT DISTINCT with Large Tables (Minor - Performance)
SELECT DISTINCT customer_id, product_category, brand_name, supplier_country
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN suppliers s ON p.supplier_id = s.supplier_id
WHERE oi.order_date >= '2023-01-01';

-- Rule 26: Use Covering Indexes (Major - Performance) - GOOD EXAMPLE
CREATE INDEX IX_Orders_CustomerDate_Covering
ON orders (customer_id, order_date)
INCLUDE (total_amount, shipping_cost, tax_amount, order_status);

-- ========================================
-- SECURITY RULES CHALLENGES (Rules 17-20)
-- ========================================

-- Rule 17: Avoid Dynamic SQL Construction (Critical - Security)
DECLARE @userInput NVARCHAR(100) = 'admin''; DROP TABLE users; --';
DECLARE @dynamicSQL NVARCHAR(500);
SET @dynamicSQL = 'SELECT * FROM users WHERE username = ''' + @userInput + ''' AND status = ''active''';
EXECUTE(@dynamicSQL);

-- Another dangerous dynamic SQL example
DECLARE @tableName NVARCHAR(50) = 'products';
DECLARE @condition NVARCHAR(100) = 'price > 100 OR 1=1';
DECLARE @sql NVARCHAR(MAX) = 'DELETE FROM ' + @tableName + ' WHERE ' + @condition;
EXEC sp_executesql @sql;

-- Rule 18: Use Parameterized Queries (Major - Security) - GOOD EXAMPLE
DECLARE @safeUserInput NVARCHAR(100) = 'admin';
DECLARE @safeStatus NVARCHAR(20) = 'active';
SELECT user_id, username, email, last_login
FROM users 
WHERE username = @safeUserInput 
AND status = @safeStatus;

-- Rule 19: Avoid GRANT ALL Privileges (Critical - Security)
GRANT ALL PRIVILEGES ON sales_database.* TO 'web_app'@'%';
GRANT ALL ON customer_data.* TO 'reporting_user'@'localhost';
GRANT ALL PRIVILEGES ON financial_records TO 'temp_contractor'@'192.168.1.%';

-- Rule 20: Use Specific Column Permissions (Major - Security) - GOOD EXAMPLE
GRANT SELECT (customer_id, first_name, last_name, email) ON customers TO 'customer_service'@'%';
GRANT UPDATE (last_login, login_count) ON users TO 'auth_service'@'localhost';
GRANT INSERT (product_name, description, price, category_id) ON products TO 'inventory_manager'@'%';

-- ========================================
-- DATA INTEGRITY RULES CHALLENGES (Rules 27-30)
-- ========================================

-- Rule 27: Always Use Transactions for Multi-Statement Operations (Major - Data Integrity) - BAD EXAMPLE
UPDATE inventory SET quantity = quantity - 5 WHERE product_id = 101;
INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (1001, 101, 5, 29.99);
UPDATE orders SET total_amount = total_amount + 149.95 WHERE order_id = 1001;

-- Rule 27: GOOD EXAMPLE - With Transaction
BEGIN TRANSACTION;
    UPDATE inventory SET quantity = quantity - 3 WHERE product_id = 205;
    INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (1002, 205, 3, 89.99);
    UPDATE orders SET total_amount = total_amount + 269.97 WHERE order_id = 1002;
    INSERT INTO audit_log (table_name, action, timestamp, user_id) VALUES ('inventory', 'UPDATE', NOW(), 1);
COMMIT;

-- Rule 28: Avoid Implicit Data Type Conversions (Minor - Data Integrity)
SELECT order_id, customer_id, total_amount
FROM orders 
WHERE order_id = '12345'  -- String to integer conversion
AND customer_id = '67890'  -- Another implicit conversion
AND created_date = '2024-01-15'  -- String to date conversion
AND total_amount = '299.99';  -- String to decimal conversion

-- Rule 29: Use CHECK Constraints (Major - Data Integrity) - GOOD EXAMPLE
ALTER TABLE employees
ADD CONSTRAINT CK_Employee_Salary CHECK (salary > 0 AND salary <= 1000000);

ALTER TABLE products
ADD CONSTRAINT CK_Product_Price CHECK (price > 0 AND discount_percentage BETWEEN 0 AND 100);

ALTER TABLE orders
ADD CONSTRAINT CK_Order_Status CHECK (order_status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled'));

-- Rule 30: Always Use Foreign Key Constraints (Major - Data Integrity) - GOOD EXAMPLE
ALTER TABLE order_items
ADD CONSTRAINT FK_OrderItems_Products
FOREIGN KEY (product_id) REFERENCES products(product_id)
ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE employees
ADD CONSTRAINT FK_Employees_Departments
FOREIGN KEY (department_id) REFERENCES departments(department_id)
ON DELETE SET NULL ON UPDATE CASCADE;

-- ========================================
-- CLARITY RULES CHALLENGES (Rules 4-6, 11, 14, 16)
-- ========================================

-- Rule 4: Avoid Implicit Joins (Minor - Clarity)
SELECT c.customer_name, o.order_date, p.product_name, oi.quantity
FROM customers c, orders o, order_items oi, products p
WHERE c.customer_id = o.customer_id
AND o.order_id = oi.order_id
AND oi.product_id = p.product_id
AND c.country = 'USA';

-- Rule 5: Use Explicit Column Names (Minor - Clarity) - GOOD EXAMPLE
SELECT customer_id, first_name, last_name, email, phone, registration_date
FROM customers 
WHERE status = 'active' 
AND registration_date >= '2024-01-01';

-- Rule 6: Use Explicit JOINs (Minor - Clarity) - GOOD EXAMPLE
SELECT c.customer_name, o.order_date, o.total_amount, p.product_name
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id
WHERE c.registration_date >= '2024-01-01';

-- Rule 11: Use table aliases in JOINs (Minor - Clarity) - BAD EXAMPLE
SELECT customers.customer_name, orders.order_date, products.product_name
FROM customers
JOIN orders ON customers.customer_id = orders.customer_id
JOIN order_items ON orders.order_id = order_items.order_id
JOIN products ON order_items.product_id = products.product_id;

-- Rule 14: Use table aliases (Minor - Clarity) - GOOD EXAMPLE
SELECT c.customer_name AS customer, o.order_date AS ordered_on, p.product_name AS product
FROM customers AS c
JOIN orders AS o ON c.customer_id = o.customer_id
JOIN order_items AS oi ON o.order_id = oi.order_id
JOIN products AS p ON oi.product_id = p.product_id;

-- Rule 16: Comment complex queries (Minor - Clarity) - GOOD EXAMPLE
-- Complex analytical query to calculate customer lifetime value
-- with monthly cohort analysis and retention metrics
WITH customer_cohorts AS (
    -- Group customers by their first purchase month
    SELECT 
        customer_id,
        DATE_TRUNC('month', MIN(order_date)) as cohort_month
    FROM orders 
    GROUP BY customer_id
),
monthly_activity AS (
    -- Track customer activity by month
    SELECT 
        cc.cohort_month,
        cc.customer_id,
        DATE_TRUNC('month', o.order_date) as activity_month,
        SUM(o.total_amount) as monthly_spend
    FROM customer_cohorts cc
    JOIN orders o ON cc.customer_id = o.customer_id
    GROUP BY cc.cohort_month, cc.customer_id, DATE_TRUNC('month', o.order_date)
)
-- Calculate retention and revenue metrics
SELECT 
    cohort_month,
    COUNT(DISTINCT customer_id) as customers_in_cohort,
    AVG(monthly_spend) as avg_monthly_spend,
    SUM(monthly_spend) as total_cohort_revenue
FROM monthly_activity
GROUP BY cohort_month
ORDER BY cohort_month;

-- ========================================
-- MAINTAINABILITY RULES CHALLENGES (Rules 32-36)
-- ========================================

-- Rule 32: Avoid Hard-coded Values (Minor - Maintainability)
SELECT product_id, product_name, price
FROM products 
WHERE category_id = 5 
AND supplier_id = 12
AND status = 'active'
AND price_range = 'premium'
AND availability = 'in_stock';

-- Rule 33: Use Consistent Naming Conventions (Minor - Maintainability) - GOOD EXAMPLE
CREATE TABLE customer_preferences (
    preference_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    email_notifications BOOLEAN DEFAULT true,
    sms_notifications BOOLEAN DEFAULT false,
    marketing_emails BOOLEAN DEFAULT false,
    preferred_language VARCHAR(10) DEFAULT 'en_US',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rule 34: Avoid Magic Numbers (Minor - Maintainability)
SELECT TOP 2500 customer_id, total_purchases, last_purchase_date
FROM customer_analytics 
WHERE total_purchases > 10000
AND days_since_last_purchase < 365
ORDER BY total_purchases DESC;

-- Another example with LIMIT
SELECT order_id, total_amount 
FROM orders 
WHERE total_amount > 5000
ORDER BY order_date DESC 
LIMIT 1000;

-- Rule 35: Use Descriptive Variable Names (Minor - Maintainability) - BAD EXAMPLE
DECLARE @x INT = 30;
DECLARE @y VARCHAR(10) = 'active';
DECLARE @z DECIMAL(10,2) = 1000.00;

SELECT customer_id, first_name, last_name
FROM customers 
WHERE status = @y 
AND days_since_registration > @x
AND lifetime_value > @z;

-- Rule 35: GOOD EXAMPLE - Descriptive Variables
DECLARE @minimum_days_since_registration INT = 30;
DECLARE @active_customer_status VARCHAR(10) = 'active';
DECLARE @minimum_lifetime_value DECIMAL(10,2) = 1000.00;

SELECT customer_id, first_name, last_name, email
FROM customers 
WHERE status = @active_customer_status 
AND days_since_registration > @minimum_days_since_registration
AND lifetime_value > @minimum_lifetime_value;

-- Rule 36: Avoid Nested Subqueries (Minor - Maintainability)
SELECT order_id, customer_id, total_amount
FROM orders
WHERE customer_id IN (
    SELECT customer_id 
    FROM customers 
    WHERE city IN (
        SELECT city_name 
        FROM cities 
        WHERE region IN (
            SELECT region_name 
            FROM regions 
            WHERE country_code IN (
                SELECT country_code 
                FROM countries 
                WHERE continent = 'North America'
            )
        )
    )
);

-- ========================================
-- MIXED COMPLEXITY CHALLENGES
-- ========================================

-- Challenge: Multiple violations in one query
SELECT DISTINCT *
FROM orders o, customers c, products p, order_items oi
WHERE o.customer_id = c.customer_id
AND o.order_id = oi.order_id
AND oi.product_id = p.product_id
AND (c.country = 'USA' OR c.country = 'Canada' OR c.country = 'Mexico')
AND YEAR(o.order_date) = 2024
AND o.total_amount > 500
AND c.customer_id IN (
    SELECT customer_id 
    FROM customer_preferences 
    WHERE email_notifications = 1
    AND customer_id IN (
        SELECT customer_id 
        FROM loyalty_members 
        WHERE tier = 'gold'
    )
);

-- Challenge: Dynamic SQL with multiple security issues
DECLARE @userRole VARCHAR(20) = 'admin';
DECLARE @dateRange VARCHAR(50) = '2024-01-01 AND 2024-12-31';
DECLARE @complexQuery NVARCHAR(MAX);

SET @complexQuery = 'SELECT * FROM financial_data WHERE access_level <= ''' + @userRole + ''' AND date_created BETWEEN ''' + @dateRange + '''';

IF @userRole = 'superuser'
    SET @complexQuery = @complexQuery + ' UNION ALL SELECT * FROM sensitive_audit_logs';

EXECUTE(@complexQuery);

-- Challenge: Performance nightmare query
SELECT COUNT(*) as total_combinations
FROM (
    SELECT DISTINCT c1.customer_id, c2.product_category, c3.order_status
    FROM customers c1, products c2, orders c3
    WHERE c1.registration_date > '2020-01-01'
    AND (c2.price > 100 OR c2.price < 10 OR c2.category = 'special')
    AND UPPER(c1.email) LIKE '%@GMAIL.COM%'
    AND c3.order_date IN (
        SELECT order_date 
        FROM orders 
        WHERE total_amount > (
            SELECT AVG(total_amount) * 1.5 
            FROM orders o2 
            WHERE YEAR(o2.order_date) = YEAR(c3.order_date)
        )
    )
) subquery;

-- Challenge: Good practices showcase
-- Well-designed query with proper structure, comments, and practices
-- Purpose: Generate monthly sales report with customer segmentation
-- Author: Data Analytics Team
-- Last Modified: 2024-01-15

WITH customer_segments AS (
    -- Categorize customers based on purchase behavior
    SELECT 
        c.customer_id,
        c.first_name,
        c.last_name,
        c.email,
        CASE 
            WHEN c.lifetime_value >= @high_value_threshold THEN 'High Value'
            WHEN c.lifetime_value >= @medium_value_threshold THEN 'Medium Value'
            ELSE 'Standard Value'
        END as customer_segment
    FROM customers c
    WHERE c.status = @active_status
    AND c.registration_date >= @analysis_start_date
),
monthly_sales AS (
    -- Aggregate sales data by month and customer segment
    SELECT 
        DATE_TRUNC('month', o.order_date) as sales_month,
        cs.customer_segment,
        COUNT(DISTINCT o.order_id) as order_count,
        COUNT(DISTINCT o.customer_id) as unique_customers,
        SUM(o.total_amount) as total_revenue,
        AVG(o.total_amount) as avg_order_value
    FROM orders o
    INNER JOIN customer_segments cs ON o.customer_id = cs.customer_id
    WHERE o.order_date >= @analysis_start_date
    AND o.order_status IN ('completed', 'shipped')
    GROUP BY DATE_TRUNC('month', o.order_date), cs.customer_segment
)
-- Final result set with growth calculations
SELECT 
    ms.sales_month,
    ms.customer_segment,
    ms.order_count,
    ms.unique_customers,
    ms.total_revenue,
    ms.avg_order_value,
    LAG(ms.total_revenue) OVER (
        PARTITION BY ms.customer_segment 
        ORDER BY ms.sales_month
    ) as previous_month_revenue,
    CASE 
        WHEN LAG(ms.total_revenue) OVER (
            PARTITION BY ms.customer_segment 
            ORDER BY ms.sales_month
        ) IS NOT NULL THEN
            ROUND(
                ((ms.total_revenue - LAG(ms.total_revenue) OVER (
                    PARTITION BY ms.customer_segment 
                    ORDER BY ms.sales_month
                )) / LAG(ms.total_revenue) OVER (
                    PARTITION BY ms.customer_segment 
                    ORDER BY ms.sales_month
                )) * 100, 2
            )
        ELSE NULL
    END as revenue_growth_percentage
FROM monthly_sales ms
ORDER BY ms.sales_month DESC, ms.customer_segment
LIMIT @result_limit;
