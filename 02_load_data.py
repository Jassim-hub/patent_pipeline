import sqlite3
import pandas as pd
import os

DB_NAME = "patents.db"
SCHEMA_FILE = "schema.sql"
DATA_DIR = "data"
CHUNK_SIZE = 250000

def init_db():
    print(f"Initializing database from {SCHEMA_FILE}...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    with open(SCHEMA_FILE, "r") as f:
        cursor.executescript(f.read())
    conn.commit()
    return conn

def load_staging_file(conn, file_name, table_name):
    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found. Skipping staging load for {table_name}.")
        return

    print(f"Loading {file_name} into staging table '{table_name}'...")
    chunk_count = 0
    for chunk in pd.read_csv(file_path, chunksize=CHUNK_SIZE):
        chunk.to_sql(table_name, conn, if_exists="append", index=False)
        chunk_count += 1
        print(f"  ...inserted {chunk_count * CHUNK_SIZE} rows")

def transform_data(conn):
    print("\nExecuting SQL Transformations to build final tables...")
    cursor = conn.cursor()

    print("1. Building 'patents' table...")
    cursor.execute("""
        INSERT INTO patents (patent_id, title, abstract, filing_date, year)
        SELECT 
            p.patent_id, 
            p.title, 
            a.abstract, 
            app.filing_date, 
            app.year
        FROM stg_patent p
        LEFT JOIN stg_abstract a ON p.patent_id = a.patent_id
        LEFT JOIN stg_application app ON p.patent_id = app.patent_id
        GROUP BY p.patent_id; -- Ensure uniqueness
    """)
    conn.commit()

    print("2. Building 'inventors' table...")
    cursor.execute("""
        INSERT INTO inventors (inventor_id, name, country)
        SELECT 
            i.inventor_id, 
            MAX(i.name), 
            MAX(l.country)
        FROM stg_inventor i
        LEFT JOIN stg_location l ON i.location_id = l.location_id
        GROUP BY i.inventor_id;
    """)
    conn.commit()

    print("3. Building 'companies' table...")
    cursor.execute("""
        INSERT INTO companies (company_id, name)
        SELECT 
            assignee_id, 
            MAX(company_name)
        FROM stg_assignee
        GROUP BY assignee_id;
    """)
    conn.commit()

    print("4. Building 'relationships' table...")
    # Relationship maps patent to inventor to company
    cursor.execute("""
        INSERT INTO relationships (patent_id, inventor_id, company_id)
        SELECT DISTINCT
            i.patent_id,
            i.inventor_id,
            a.assignee_id
        FROM stg_inventor i
        INNER JOIN stg_assignee a ON i.patent_id = a.patent_id;
    """)
    conn.commit()
    
    print("\nData Transformation Complete! Final tables are populated.")
    
    print("Cleaning up staging tables to save space...")
    staging_tables = ['stg_patent', 'stg_abstract', 'stg_application', 'stg_inventor', 'stg_assignee', 'stg_location']
    for t in staging_tables:
        cursor.execute(f"DROP TABLE IF EXISTS {t}")
    conn.commit()
    print("Database is ready for analysis!")

if __name__ == "__main__":
    if not os.path.exists(SCHEMA_FILE):
        print(f"Error: Schema file {SCHEMA_FILE} not found.")
    else:
        conn = init_db()
        
        # Load all chunked CSVs into staging
        load_staging_file(conn, "stg_patent.csv", "stg_patent")
        load_staging_file(conn, "stg_abstract.csv", "stg_abstract")
        load_staging_file(conn, "stg_application.csv", "stg_application")
        load_staging_file(conn, "stg_inventor.csv", "stg_inventor")
        load_staging_file(conn, "stg_assignee.csv", "stg_assignee")
        load_staging_file(conn, "stg_location.csv", "stg_location")
        
        # Build the final tables
        transform_data(conn)
        
        conn.close()
