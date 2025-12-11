-- 示例SQL查询文件，包含各种SQL语句类型

-- 简单SELECT查询
SELECT * FROM users;

-- 带WHERE条件的查询
SELECT id, name, email FROM customers WHERE status = 'active';

-- JOIN查询
SELECT u.id, u.name, o.order_id, o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- 多表JOIN
SELECT 
    c.customer_name,
    o.order_date,
    p.product_name,
    od.quantity
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
INNER JOIN order_details od ON o.order_id = od.order_id
RIGHT JOIN products p ON od.product_id = p.product_id;

-- 子查询
SELECT * FROM employees 
WHERE department_id IN (SELECT id FROM departments WHERE location = 'Beijing');

-- INSERT语句
INSERT INTO users (name, email, created_at) 
VALUES ('张三', 'zhangsan@example.com', NOW());

-- UPDATE语句
UPDATE products SET price = price * 1.1 WHERE category = 'electronics';

-- DELETE语句
DELETE FROM temp_data WHERE created_at < '2023-01-01';

-- CREATE TABLE
CREATE TABLE IF NOT EXISTS user_logs (
    id INT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100),
    created_at TIMESTAMP
);

-- WITH CTE (Common Table Expression)
WITH sales_summary AS (
    SELECT 
        product_id,
        SUM(quantity) as total_quantity
    FROM sales_records
    GROUP BY product_id
)
SELECT p.product_name, ss.total_quantity
FROM products p
JOIN sales_summary ss ON p.id = ss.product_id;

-- 复杂嵌套查询
SELECT t1.id, t1.name
FROM (
    SELECT id, name FROM employees WHERE salary > 50000
) t1
WHERE t1.id IN (
    SELECT employee_id FROM performance_reviews WHERE rating > 4
);

-- UNION查询
SELECT customer_id, name FROM customers_2023
UNION
SELECT customer_id, name FROM customers_2024;

-- 带schema的表名
SELECT * FROM db_schema.table_name;
SELECT * FROM `database`.`users`;

-- 多个INSERT
INSERT INTO logs (message) SELECT error_message FROM error_table;

-- TRUNCATE
TRUNCATE TABLE temporary_cache;

-- DROP TABLE
DROP TABLE IF EXISTS old_backup_table;

-- ALTER TABLE
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- FROM子句中的子查询
SELECT * FROM (SELECT * FROM raw_data WHERE valid = 1) AS filtered_data;
