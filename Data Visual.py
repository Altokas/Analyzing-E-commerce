import psycopg2
import pandas as pd

conn = psycopg2.connect(
    dbname="postgres",      
    user="postgres",        
    password="123456",  
    host="localhost",
    port="5433"           
)


cur = conn.cursor()


queries = {
    "orders_per_city": """
        SELECT c.customer_city, COUNT(*) AS total_orders
        FROM olist_orders_dataset o
        JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
        GROUP BY c.customer_city
        ORDER BY total_orders DESC
        LIMIT 10;
    """,
    "avg_payment_type": """
        SELECT payment_type, AVG(payment_value) AS avg_payment
        FROM olist_order_payments_dataset
        GROUP BY payment_type
        ORDER BY avg_payment DESC;
    """,
    "top_expensive_orders": """
        SELECT order_id, SUM(price + freight_value) AS total_amount
        FROM olist_order_items_dataset
        GROUP BY order_id
        ORDER BY total_amount DESC
        LIMIT 10;
    """
}


for name, query in queries.items():
    print(f"\n=== {name} ===")
    df = pd.read_sql_query(query, conn)
    print(df.head(10)) 
    df.to_csv(f"{name}.csv", index=False, encoding="utf-8") 


cur.close()
conn.close()
