import sqlite3
import pandas as pd
import json

DB_NAME = "patents.db"

def run_analysis():
    print("Connecting to database for analysis...\n")
    try:
        conn = sqlite3.connect(DB_NAME)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return

    # Total Patents
    total_patents_df = pd.read_sql_query("SELECT COUNT(*) as count FROM patents", conn)
    total_patents = int(total_patents_df.iloc[0]['count'])

    # Q1: Top Inventors
    top_inventors_df = pd.read_sql_query("""
        SELECT i.name as inventor_name, COUNT(r.patent_id) as total_patents
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        GROUP BY i.inventor_id
        ORDER BY total_patents DESC
        LIMIT 10
    """, conn)
    
    # Export Top Inventors to CSV
    top_inventors_df.to_csv("top_inventors.csv", index=False)

    # Q2: Top Companies
    top_companies_df = pd.read_sql_query("""
        SELECT c.name as company_name, COUNT(r.patent_id) as total_patents
        FROM companies c
        JOIN relationships r ON c.company_id = r.company_id
        GROUP BY c.company_id
        ORDER BY total_patents DESC
        LIMIT 10
    """, conn)
    
    # Export Top Companies to CSV
    top_companies_df.to_csv("top_companies.csv", index=False)

    # Q3: Top Countries
    top_countries_df = pd.read_sql_query("""
        SELECT i.country, COUNT(DISTINCT r.patent_id) as total_patents
        FROM inventors i
        JOIN relationships r ON i.inventor_id = r.inventor_id
        GROUP BY i.country
        ORDER BY total_patents DESC
        LIMIT 10
    """, conn)
    
    # Export Countries to CSV
    top_countries_df.to_csv("country_trends.csv", index=False)

    # === 1. Console Report ===
    print("================== PATENT REPORT ===================")
    print(f"Total Patents: {total_patents:,}")
    
    print("\nTop Inventors:")
    for idx, row in top_inventors_df.head(5).iterrows():
        print(f"{idx+1}. {row['inventor_name']} - {row['total_patents']}")
        
    print("\nTop Companies:")
    for idx, row in top_companies_df.head(5).iterrows():
        print(f"{idx+1}. {row['company_name']} - {row['total_patents']}")
        
    print("\nTop Countries:")
    for idx, row in top_countries_df.head(5).iterrows():
        print(f"{idx+1}. {row['country']} - {row['total_patents']}")
    print("====================================================\n")

    # === 2. JSON Report ===
    # Calculate share for countries
    if total_patents > 0:
        top_countries_list = []
        for _, row in top_countries_df.head(5).iterrows():
            share = round(row['total_patents'] / total_patents, 4)
            top_countries_list.append({"country": row['country'], "share": share})
    else:
        top_countries_list = []

    report_dict = {
        "total_patents": total_patents,
        "top_inventors": [
            {"name": row['inventor_name'], "patents": int(row['total_patents'])} 
            for _, row in top_inventors_df.head(5).iterrows()
        ],
        "top_companies": [
            {"name": row['company_name'], "patents": int(row['total_patents'])} 
            for _, row in top_companies_df.head(5).iterrows()
        ],
        "top_countries": top_countries_list
    }

    with open("report.json", "w") as f:
        json.dump(report_dict, f, indent=4)
        
    print("Reports successfully generated:")
    print("- top_inventors.csv")
    print("- top_companies.csv")
    print("- country_trends.csv")
    print("- report.json")

    conn.close()

if __name__ == "__main__":
    run_analysis()
