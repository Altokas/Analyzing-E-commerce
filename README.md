# Olist E-commerce Analytics  

## Company  
I am working as a **Data Analyst** at **Olist**, a Brazilian e-commerce company that connects small businesses to major online marketplaces. Olist provides a platform for sellers to manage their products, payments, and deliveries while ensuring customers receive their orders efficiently.  

---

## Project Description  
This project focuses on analyzing Olist’s e-commerce dataset.  
The dataset contains multiple tables (orders, customers, products, payments, reviews, etc.) with ~100,000 rows.  
The main goal is to explore customer behavior, order patterns, payment methods, and product performance.  
The analysis helps the company answer business questions such as:  
- Which cities generate the most orders?  
- What is the average payment value by payment type?  
- Which orders are the most expensive?  
- How do delivery times vary by region?


---

## Tools and Resources  
- **PostgreSQL** – database for storing and querying data  
- **Python** – data analysis and automation  
- **psycopg2** – Python library for PostgreSQL connection  
- **pandas** – handling tabular data and exporting results  
- **GitHub** – project hosting and version control  

---

## Database Schema (ER Diagram)  
The dataset consists of several related tables:  
- **olist_orders_dataset** – orders (order_id, customer_id, timestamps)  
- **olist_customers_dataset** – customers (customer_id, city, state)  
- **olist_order_items_dataset** – items per order (order_id, product_id, price, freight)  
- **olist_order_payments_dataset** – payment information (order_id, payment_type, payment_value)  
- **olist_products_dataset** – product details (product_id, category, dimensions)  

Relationships:  
- `customer_id` links **orders** with **customers**  
- `order_id` links **orders** with **order_items** and **payments**  
- `product_id` links **order_items** with **products**  

*ER diagram image <img width="1920" height="956" alt="2025-09-26_15-53-14" src="https://github.com/user-attachments/assets/cb0ca8a5-ced9-4a45-9340-1d6144252fec" />
 

---

## How to Run the Project  

### 1. Clone the repository  
```bash
git clone [https://github.com/your-username/olist-analytics.git
cd olist-analytics](https://github.com/Altokas/Analyzing-E-commerce)
```
2. Install dependencies
```bash
pip install psycopg2 pandas
```
3. Configure the database connection
Update connection settings in main.py:

