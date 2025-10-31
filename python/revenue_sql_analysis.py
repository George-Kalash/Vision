import sqlite3
import pandas as pd

def analyze_revenue_sql():
    # Read the CSV file
    df = pd.read_csv('final_output.csv')
    
    # Create in-memory SQLite database
    conn = sqlite3.connect(':memory:')
    
    # Load CSV data into SQLite
    df.to_sql('financial_data', conn, index=False, if_exists='replace')
    
    # SQL query to calculate revenue changes
    query = """
    WITH revenue_data AS (
      SELECT 
        rowid as row_number,
        Revenue,
        LAG(Revenue) OVER (ORDER BY rowid) AS previous_revenue
      FROM financial_data
      WHERE Revenue IS NOT NULL AND Revenue != ''
      ORDER BY rowid DESC
    )
    SELECT 
      row_number,
      Revenue,
      previous_revenue,
      CASE 
        WHEN previous_revenue IS NOT NULL AND previous_revenue != 0
        THEN ROUND(((Revenue - previous_revenue) / previous_revenue * 100.0), 2)
        ELSE NULL 
      END AS revenue_change_percent
    FROM revenue_data
    ORDER BY row_number DESC;
    """
    
    # Execute query and get results
    result = pd.read_sql_query(query, conn)
    
    # Close connection
    conn.close()
    
    return result

# Run the analysis
if __name__ == "__main__":
    try:
        revenue_analysis = analyze_revenue_sql()
        print("Revenue Analysis:")
        print("=" * 50)
        print(revenue_analysis.to_string(index=False))
        
        # Save results
        revenue_analysis.to_csv('revenue_analysis_results.csv', index=False)
        print(f"\nResults saved to revenue_analysis_results.csv")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure 'final_output.csv' exists and has a 'Revenue' column")