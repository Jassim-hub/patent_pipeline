import sqlite3
import pandas as pd
import os
import gc

DB_NAME = "patents.db"
SCHEMA_FILE = "schema.sql"
DATA_DIR = "data"
# Significantly reduced chunk size to prevent Silent RAM crashes on massive abstract strings
CHUNK_SIZE = 50000 

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
    try:
        for chunk in pd.read_csv(file_path, chunksize=CHUNK_SIZE):
            chunk.to_sql(table_name, conn, if_exists="append", index=False)
            chunk_count += 1
            if chunk_count % 5 == 0:
                print(f"  ...inserted {chunk_count * CHUNK_SIZE} rows")
            
            # Force garbage collection to free RAM
            del chunk
            gc.collect()
            
        print(f"Finished loading {file_name}. Deleting CSV to free up disk space...")
        # Free up disk space progressively by deleting the CSV file once it's safely in the database!
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Warning: Could not delete {file_path} - {e}")

    except Exception as e:
        print(f"Error loading {file_name}: {e}")

def transform_data(conn):
    print("\nExecuting SQL Transformations to build final tables...")
    cursor = conn.cursor()

    print("1. Building 'patents' table (this may take a few minutes)...")
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
    # Execute a VACUUM to reclaim disk space from dropped tables
    print("Vacuuming database to reclaim disk space...")
    cursor.execute("VACUUM")
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
