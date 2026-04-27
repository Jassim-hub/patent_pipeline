import sqlite3
import pandas as pd
import os

DB_NAME = "patents.db"
SCHEMA_FILE = "schema.sql"
DATA_DIR = "data"

def init_db():
    print(f"Initializing database from {SCHEMA_FILE}...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    with open(SCHEMA_FILE, "r") as f:
        schema_sql = f.read()
        
    cursor.executescript(schema_sql)
    conn.commit()
    print("Database schema created.")
    return conn

def load_data(conn):
    print("Loading clean data into database...")
    
    # Load Patents
    patents_file = os.path.join(DATA_DIR, 'clean_patents.csv')
    if os.path.exists(patents_file):
        print("Loading patents...")
        df_patents = pd.read_csv(patents_file)
        df_patents.to_sql("patents", conn, if_exists="append", index=False)
        print(f"Loaded {len(df_patents)} patents.")
    else:
        print("Warning: clean_patents.csv not found.")

    # Load Inventors
    inventors_file = os.path.join(DATA_DIR, 'clean_inventors.csv')
    if os.path.exists(inventors_file):
        print("Loading inventors...")
        df_inventors = pd.read_csv(inventors_file)
        df_inventors.to_sql("inventors", conn, if_exists="append", index=False)
        print(f"Loaded {len(df_inventors)} inventors.")
    else:
        print("Warning: clean_inventors.csv not found.")

    # Load Companies
    companies_file = os.path.join(DATA_DIR, 'clean_companies.csv')
    if os.path.exists(companies_file):
        print("Loading companies...")
        df_companies = pd.read_csv(companies_file)
        df_companies.to_sql("companies", conn, if_exists="append", index=False)
        print(f"Loaded {len(df_companies)} companies.")
    else:
        print("Warning: clean_companies.csv not found.")

    # Load Relationships
    rel_file = os.path.join(DATA_DIR, 'clean_relationships.csv')
    if os.path.exists(rel_file):
        print("Loading relationships...")
        df_rel = pd.read_csv(rel_file)
        df_rel.to_sql("relationships", conn, if_exists="append", index=False)
        print(f"Loaded {len(df_rel)} relationships.")
    else:
        print("Warning: clean_relationships.csv not found.")

    print("Data loading complete.")

if __name__ == "__main__":
    if not os.path.exists(SCHEMA_FILE):
        print(f"Error: Schema file {SCHEMA_FILE} not found.")
    else:
        conn = init_db()
        load_data(conn)
        conn.close()
