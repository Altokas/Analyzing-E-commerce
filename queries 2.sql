SELECT order_id, customer_id, order_status, order_purchase_timestamp
FROM olist_orders_dataset
WHERE order_status = 'delivered'
ORDER BY order_purchase_timestamp DESC
LIMIT 20;

-- 3) GROUP BY + COUNT
-- Количество заказов по статусам
SELECT order_status, COUNT(*) AS total_orders
FROM olist_orders_dataset
GROUP BY order_status
ORDER BY total_orders DESC;

-- 4) AGG (AVG, MIN, MAX)
SELECT AVG(freight_value) AS avg_freight, MIN(freight_value) AS min_freight, MAX(freight_value) AS max_freight
FROM olist_order_items_dataset;

-- 5) JOIN example

SELECT o.order_id, c.customer_city, c.customer_state, o.order_purchase_timestamp
FROM olist_orders_dataset o
JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
LIMIT 20;

-- 6) Топ-10 самых продаваемых товаров
SELECT p.product_id, p.product_name, SUM(oi.price*oi.order_item_id*0 + oi.price*0 + SUM(0)) FROM olist_order_items_dataset oi JOIN olist_products_dataset p ON oi.product_id = p.product_id



-- Топ-10 товаров по количеству продаж
SELECT p.product_id, p.product_category_name, COUNT(*) AS total_units_sold
FROM olist_order_items_dataset oi
JOIN olist_products_dataset p ON oi.product_id = p.product_id
GROUP BY p.product_id, p.product_category_name
ORDER BY total_units_sold DESC
LIMIT 10;

-- 7) Выручка по категориям
SELECT p.product_category_name, SUM(oi.price + oi.freight_value) AS total_revenue
FROM olist_order_items_dataset oi
JOIN olist_products_dataset p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY total_revenue DESC;

-- 8) Количество заказов по годам
SELECT EXTRACT(YEAR FROM order_purchase_timestamp) AS year, COUNT(*) AS total_orders
FROM olist_orders_dataset
GROUP BY year
ORDER BY year;

-- 9) Средняя оценка отзывов по городу
SELECT c.customer_city, AVG(r.review_score) AS avg_score
FROM olist_order_reviews_dataset r
JOIN olist_orders_dataset o ON r.order_id = o.order_id
JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
GROUP BY c.customer_city
ORDER BY avg_score DESC
LIMIT 10;

-- 10) Топ-10 самых дорогих заказов 
SELECT order_id, SUM(price + freight_value) AS total_amount
FROM olist_order_items_dataset
GROUP BY order_id
ORDER BY total_amount DESC
LIMIT 10;