import sqlite3
import pandas as pd

def run_analysis():
    print("Connecting to FoodTech Analytics Database...")
    # This is a simulation script showing how the SQL would be integrated into a pipeline
    try:
        conn = sqlite3.connect('foodtech_analytics.db')
        # In a real scenario, we would execute the SQL file here
        print("Successfully connected. Running Customer LTV Query...")
        
        # Example of executing one of the project's queries
        query = """
        SELECT user_id, SUM(price) as total_spent 
        FROM sales 
        JOIN product ON sales.product_id = product.product_id 
        GROUP BY user_id 
        ORDER BY total_spent DESC
        """
        df = pd.read_sql_query(query, conn)
        print(df.head())
        
        conn.close()
    except Exception as e:
        print(f"Simulation Note: This script requires the .db file to be initialized. Error: {e}")

if __name__ == '__main__':
    run_analysis()
