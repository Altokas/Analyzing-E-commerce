import psycopg2
from datetime import datetime, timedelta
import time

# === PostgreSQL connection ===
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="123456",
    host="localhost",
    port="5433"
)
cur = conn.cursor()

# === Configuration ===
BASE_STRING = "ddddddddddddddddddddd"
START_NUMBER = 1
DELAY_SECONDS = 5  # how often to insert new rows (you can change this)
price = 50000
start_date = datetime.now() - timedelta(days=365)

# === Function to generate IDs ===
def make_id(base, num):
    return f"{base}{num:07d}"

# === Infinite insertion loop ===
i = START_NUMBER
print("🚀 Auto-insertion started. Press Ctrl + C to stop.\n")

try:
    while True:
        order_id = make_id(BASE_STRING, i + 50000)
        product_id = make_id(BASE_STRING, i + 10000)
        seller_id = make_id(BASE_STRING, i + 20000)
        order_item_id = i
        shipping_limit_date = start_date + timedelta(days=i)

        query = """
            INSERT INTO olist_order_items_dataset
            (order_id, order_item_id, product_id, seller_id, shipping_limit_date, price)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        cur.execute(query, (order_id, order_item_id, product_id, seller_id, shipping_limit_date, price))
        conn.commit()

        print(f"✅ Inserted: {order_id} | Date: {shipping_limit_date.strftime('%Y-%m-%d')}")

        i += 1
        time.sleep(DELAY_SECONDS)  # wait before inserting the next row

except KeyboardInterrupt:
    print("\n🛑 Stopped manually by user.")
finally:
    cur.close()
    conn.close()
    print("🔒 PostgreSQL connection closed.")
