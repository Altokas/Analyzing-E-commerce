import psycopg2
import pandas as pd

# Подключение к базе PostgreSQL
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="123456",
    host="localhost",
    port="5433"
)

# Проверим, какие таблицы есть в базе
tables_query = """
SELECT table_name
FROM information_schema.tables
WHERE table_schema='public';
"""
tables = pd.read_sql_query(tables_query, conn)
print("Таблицы в базе:\n", tables)

# Словарь с запросами (с проверенными названиями таблиц)
queries = {
    "last_20_delivered_orders": """
        SELECT order_id, customer_id, order_status, order_purchase_timestamp
        FROM olist_orders_dataset
        WHERE order_status = 'delivered'
        ORDER BY order_purchase_timestamp DESC
        LIMIT 20;
    """,
    "orders_by_status": """
        SELECT order_status, COUNT(*) AS total_orders
        FROM olist_orders_dataset
        GROUP BY order_status
        ORDER BY total_orders DESC;
    """,
    "freight_stats": """
        SELECT 
            AVG(freight_value) AS avg_freight, 
            MIN(freight_value) AS min_freight, 
            MAX(freight_value) AS max_freight
        FROM olist_order_items_dataset;
    """,
    "orders_with_city_state": """
        SELECT o.order_id, c.customer_city, c.customer_state, o.order_purchase_timestamp
        FROM olist_orders_dataset o
        JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
        LIMIT 20;
    """,
    "top_10_selling_products": """
        SELECT p.product_id, p.product_name, COUNT(*) AS total_units_sold
        FROM olist_order_items_dataset oi
        JOIN olist_products p ON oi.product_id = p.product_id
        GROUP BY p.product_id, p.product_name
        ORDER BY total_units_sold DESC
        LIMIT 10;
    """,
    "revenue_by_category": """
        SELECT p.product_category_name, SUM(oi.price + oi.freight_value) AS total_revenue
        FROM olist_order_items_dataset oi
        JOIN olist_products p ON oi.product_id = p.product_id
        GROUP BY p.product_category_name
        ORDER BY total_revenue DESC;
    """,
    "orders_by_year": """
        SELECT EXTRACT(YEAR FROM order_purchase_timestamp) AS year, COUNT(*) AS total_orders
        FROM olist_orders_dataset
        GROUP BY year
        ORDER BY year;
    """,
    "avg_review_score_by_city": """
        SELECT c.customer_city, AVG(r.review_score) AS avg_score
        FROM olist_order_reviews_dataset r
        JOIN olist_orders_dataset o ON r.order_id = o.order_id
        JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
        GROUP BY c.customer_city
        ORDER BY avg_score DESC
        LIMIT 10;
    """,
    "top_10_expensive_orders": """
        SELECT order_id, SUM(price + freight_value) AS total_amount
        FROM olist_order_items_dataset
        GROUP BY order_id
        ORDER BY total_amount DESC
        LIMIT 10;
    """,
    "avg_order_amount_by_customer": """
        SELECT o.customer_id, AVG(oi.price + oi.freight_value) AS avg_order_amount
        FROM olist_orders_dataset o
        JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
        GROUP BY o.customer_id
        ORDER BY avg_order_amount DESC
        LIMIT 10;
    """
}

# Сохраняем все результаты в один Excel-файл с листами
with pd.ExcelWriter("olist_analysis.xlsx", engine='xlsxwriter') as writer:
    for name, query in queries.items():
        try:
            df = pd.read_sql_query(query, conn)
            print(f"\n=== {name} ===")
            print(df.head(10))
            df.to_excel(writer, sheet_name=name[:31], index=False)  # Лист Excel: max 31 символ
        except Exception as e:
            print(f"Ошибка при выполнении запроса {name}: {e}")

conn.close()
