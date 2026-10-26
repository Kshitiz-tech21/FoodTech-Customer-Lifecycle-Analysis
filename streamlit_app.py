import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Page Config
st.set_page_config(page_title="FoodTech Customer Lifecycle Analysis", layout="wide")

# --- DATABASE INITIALIZATION ---
@st.cache_data
def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()
    
    # Schema
    cursor.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, signup_date DATE)")
    cursor.execute("CREATE TABLE membership_enrollments (user_id INTEGER, enrollment_date DATE)")
    cursor.execute("CREATE TABLE product (product_id INTEGER PRIMARY KEY, product_name TEXT, price NUMERIC)")
    cursor.execute("CREATE TABLE sales (sale_id INTEGER PRIMARY KEY, user_id INTEGER, order_date DATE, product_id INTEGER)")
    
    # Data
    cursor.executemany("INSERT INTO users VALUES (?, ?)", [
        (1, '2014-09-02'), (2, '2015-01-15'), (3, '2014-04-11'), (4, '2016-05-20'), (5, '2017-08-10')
    ])
    cursor.executemany("INSERT INTO membership_enrollments VALUES (?, ?)", [
        (1, '2017-09-22'), (3, '2017-04-21'), (4, '2018-01-15'), (5, '2019-03-10')
    ])
    cursor.executemany("INSERT INTO product VALUES (?, ?, ?)", [
        (1, 'Premium Meal Box', 980), (2, 'Standard Combo', 870), (3, 'Quick Bite', 330)
    ])
    cursor.executemany("INSERT INTO sales (user_id, order_date, product_id) VALUES (?, ?, ?)", [
        (1, '2017-04-19', 2), (3, '2019-12-18', 1), (2, '2020-07-20', 3), 
        (1, '2019-10-23', 2), (1, '2018-03-19', 3), (3, '2016-12-20', 2),
        (1, '2016-11-09', 1), (1, '2016-05-20', 3), (2, '2017-09-24', 1),
        (1, '2017-03-11', 2), (1, '2016-03-11', 1), (3, '2016-11-10', 1),
        (3, '2017-12-07', 2), (3, '2016-12-15', 2), (2, '2017-11-08', 2),
        (2, '2018-09-10', 3), (4, '2018-02-01', 1), (4, '2018-03-15', 2),
        (5, '2019-04-01', 3), (5, '2019-05-10', 1)
    ])
    conn.commit()
    return conn

conn = init_db()

# --- UI ---
st.title("🍔 FoodTech Customer Lifecycle Analysis")
st.markdown("### Executive Dashboard: Loyalty Program Impact on LTV & Retention")
st.write("This dashboard analyzes how the 'Gold Membership' affects spending and user behavior using a SQL-backed pipeline.")

# Sidebar for Navigation
menu = st.sidebar.selectbox("Choose Analysis", ["Overview", "Loyalty Impact", "User Behavior", "SQL Explorer"])

if menu == "Overview":
    st.subheader("Key Business Metrics")
    
    # Metric 1: Total Revenue
    rev_df = pd.read_sql_query("SELECT SUM(p.price) as total FROM sales s JOIN product p ON s.product_id = p.product_id", conn)
    total_rev = rev_df['total'][0]
    
    # Metric 2: Avg Order Value
    aov_df = pd.read_sql_query("SELECT AVG(p.price) as aov FROM sales s JOIN product p ON s.product_id = p.product_id", conn)
    aov = aov_df['aov'][0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"₹{total_rev:,.2f}")
    col2.metric("Average Order Value", f"₹{aov:,.2f}")
    col3.metric("Total Customers", "5")
    
    # Chart: LTV per User
    st.markdown("#### Customer Lifetime Value (LTV)")
    ltv_query = """
    SELECT s.user_id, SUM(p.price) as total_spent
    FROM sales s
    JOIN product p ON s.product_id = p.product_id
    GROUP BY s.user_id
    ORDER BY total_spent DESC
    """
    ltv_df = pd.read_sql_query(ltv_query, conn)
    fig = px.bar(ltv_df, x='user_id', y='total_spent', labels={'user_id': 'User ID', 'total_spent': 'Total Spend (₹)'}, 
                 title="Total Spend by User", color='total_spent')
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Loyalty Impact":
    st.subheader("Gold Membership Analysis")
    
    # Pre-Membership vs Post-Membership Spend
    # We use the project's SQL logic here
    pre_query = """
    SELECT s.user_id, SUM(p.price) as pre_spend
    FROM sales s
    JOIN membership_enrollments m ON s.user_id = m.user_id
    JOIN product p ON s.product_id = p.product_id
    WHERE s.order_date <= m.enrollment_date
    GROUP BY s.user_id
    """
    post_query = """
    SELECT s.user_id, SUM(p.price) as post_spend
    FROM sales s
    JOIN membership_enrollments m ON s.user_id = m.user_id
    JOIN product p ON s.product_id = p.product_id
    WHERE s.order_date > m.enrollment_date
    GROUP BY s.user_id
    """
    
    pre_df = pd.read_sql_query(pre_query, conn)
    post_df = pd.read_sql_query(post_query, conn)
    
    merged = pd.merge(pre_df, post_df, on='user_id', how='outer').fillna(0)
    merged = merged.rename(columns={'pre_spend': 'Spend Before Gold', 'post_spend': 'Spend After Gold'})
    
    st.write("Comparing spending before and after joining the loyalty program:")
    st.dataframe(merged, use_container_width=True)
    
    # Plot
    fig2 = px.bar(merged, x='user_id', y=['Spend Before Gold', 'Spend After Gold'], 
                  barmode='group', title="Spending Shift: Pre vs Post Gold")
    st.plotly_chart(fig2, use_container_width=True)

elif menu == "User Behavior":
    st.subheader("User Engagement Metrics")
    
    # Retention: Distinct days visited
    retention_query = "SELECT user_id, COUNT(DISTINCT order_date) as active_days FROM sales GROUP BY user_id"
    ret_df = pd.read_sql_query(retention_query, conn)
    
    st.markdown("#### Order Frequency (Active Days)")
    st.bar_chart(ret_df.set_index('user_id'))
    
    # First Product Purchased
    first_prod_query = """
    SELECT s.user_id, p.product_name, s.order_date
    FROM (SELECT *, RANK() OVER (PARTITION BY user_id ORDER BY order_date ASC) as rnk FROM sales) s
    JOIN product p ON s.product_id = p.product_id
    WHERE s.purchase_rank = 1
    """
    # Fixed query for SQLite (SQLite doesn't support 'purchase_rank' in outer unless specified)
    first_prod_query = """
    SELECT user_id, product_name, order_date
    FROM (SELECT s.user_id, p.product_name, s.order_date, RANK() OVER (PARTITION BY s.user_id ORDER BY s.order_date ASC) as rnk 
          FROM sales s JOIN product p ON s.product_id = p.product_id)
    WHERE rnk = 1
    """
    fp_df = pd.read_sql_query(first_prod_query, conn)
    st.markdown("#### First Purchase Preferences")
    st.table(fp_df)

elif menu == "SQL Explorer":
    st.subheader("Engineering Behind the Dashboard")
    st.markdown("This section shows the raw SQL logic used to drive the insights.")
    
    with st.expander("View LTV Query"):
        st.code("SELECT s.user_id, SUM(p.price) as total_spent FROM sales s JOIN product p ON s.product_id = p.product_id GROUP BY s.user_id", language="sql")
        
    with st.expander("View Loyalty Impact Query"):
        st.code("SELECT s.user_id, SUM(p.price) FROM sales s JOIN membership_enrollments m ON s.user_id = m.user_id WHERE s.order_date > m.enrollment_date GROUP BY s.user_id", language="sql")
    
    st.info("The app uses an in-memory SQLite database for demonstration purposes.")
