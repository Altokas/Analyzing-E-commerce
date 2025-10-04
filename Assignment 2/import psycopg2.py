import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import os

# ==============================
# Database connection
# ==============================
conn = psycopg2.connect(
    host="localhost",
    database="postgres",   
    password="123456",     
    port="5433"            
)

os.makedirs("charts", exist_ok=True)

# Helper function
def run_query(sql):
    df = pd.read_sql(sql, conn)
    print(f"{sql.split()[0]} → {len(df)} rows")
    return df


# ==============================
# 1. PIE CHART — Payment method distribution
# ==============================
query_pie = """
SELECT payment_type, COUNT(*) AS total
FROM olist_order_payments_dataset
GROUP BY payment_type;
"""
df_pie = run_query(query_pie)

plt.figure(figsize=(6,6))
plt.pie(df_pie['total'], labels=df_pie['payment_type'], autopct='%1.1f%%', startangle=90)
plt.title("Payment Method Distribution")
plt.savefig("charts/pie_payment_methods.png")
plt.close()


# ==============================
# 2. BAR CHART — Average payment per city (2 JOINs)
# ==============================
query_bar = """
SELECT c.customer_city AS city, ROUND(AVG(p.payment_value), 2) AS avg_payment
FROM olist_order_payments_dataset p
JOIN olist_orders_dataset o ON p.order_id = o.order_id
JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
GROUP BY city
ORDER BY avg_payment DESC
LIMIT 10;
"""
df_bar = run_query(query_bar)

plt.figure(figsize=(8,5))
plt.bar(df_bar['city'], df_bar['avg_payment'], color='skyblue')
plt.title("Top 10 Cities by Average Payment Value")
plt.xlabel("City")
plt.ylabel("Average Payment (R$)")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig("charts/bar_avg_payment_city.png")
plt.close()


# ==============================
# 3. HORIZONTAL BAR — Revenue by state (2 JOINs)
# ==============================
query_barh = """
SELECT c.customer_state AS state, SUM(p.payment_value) AS total_revenue
FROM olist_order_payments_dataset p
JOIN olist_orders_dataset o ON p.order_id = o.order_id
JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
GROUP BY state
ORDER BY total_revenue DESC
LIMIT 10;
"""
df_barh = run_query(query_barh)

plt.figure(figsize=(8,5))
plt.barh(df_barh['state'], df_barh['total_revenue'], color='lightgreen')
plt.title("Top 10 States by Total Revenue")
plt.xlabel("Total Revenue (R$)")
plt.ylabel("State")
plt.tight_layout()
plt.savefig("charts/barh_revenue_state.png")
plt.close()


# ==============================
# 4. LINE CHART — Monthly orders over time (2 JOINs)
# ==============================
query_line = """
SELECT DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
       COUNT(DISTINCT o.order_id) AS total_orders
FROM olist_orders_dataset o
JOIN olist_order_items_dataset i ON o.order_id = i.order_id
GROUP BY month
ORDER BY month;
"""
df_line = run_query(query_line)

plt.figure(figsize=(8,5))
plt.plot(df_line['month'], df_line['total_orders'], marker='o', color='coral')
plt.title("Monthly Number of Orders Over Time")
plt.xlabel("Month")
plt.ylabel("Number of Orders")
plt.grid(True)
plt.tight_layout()
plt.savefig("charts/line_monthly_orders.png")
plt.close()


# ==============================
# 5. HISTOGRAM — Payment value distribution
# ==============================
query_hist = """
SELECT payment_value
FROM olist_order_payments_dataset;
"""
df_hist = run_query(query_hist)

plt.figure(figsize=(8,5))
plt.hist(df_hist['payment_value'], bins=30, color='orange', edgecolor='black')
plt.title("Distribution of Payment Values")
plt.xlabel("Payment Value (R$)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("charts/hist_payment_values.png")
plt.close()


# ==============================
# 6. SCATTER PLOT — Payment vs installments (2 JOINs)
# ==============================
query_scatter = """
SELECT p.payment_value, p.payment_installments
FROM olist_order_payments_dataset p
JOIN olist_orders_dataset o ON p.order_id = o.order_id
JOIN olist_customers_dataset c ON o.customer_id = c.customer_id;
"""
df_scatter = run_query(query_scatter)

plt.figure(figsize=(8,5))
plt.scatter(df_scatter['payment_installments'], df_scatter['payment_value'], alpha=0.5, color='purple')
plt.title("Payment Value vs Number of Installments")
plt.xlabel("Number of Installments")
plt.ylabel("Payment Value (R$)")
plt.tight_layout()
plt.savefig("charts/scatter_payment_vs_installments.png")
plt.close()


# ==============================
# Report
# ==============================
print("\n✅ All 6 charts created successfully in /charts/ directory!")

conn.close()
