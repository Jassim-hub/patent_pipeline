import pandas as pd
import os
import argparse

def clean_data(input_file):
    print(f"Reading raw data from {input_file}...")
    
    # Determine separator based on file extension
    sep = '\t' if input_file.endswith('.tsv') else ','
    
    # Read the data - specifying low_memory=False for large files
    try:
        df = pd.read_csv(input_file, sep=sep, low_memory=False)
    except FileNotFoundError:
        print(f"Error: Could not find '{input_file}'. Please ensure you have downloaded the data and placed it at the correct path.")
        return
    
    print(f"Successfully loaded {len(df)} rows.")

    # Convert all column names to lowercase and strip spaces for easier access
    df.columns = df.columns.str.lower().str.strip()

    # Standardize expected column names. 
    # Adjust the dictionary below if your PatentsView data file has different column names.
    column_mapping = {
        'patent_id': 'patent_id',
        'id': 'patent_id', # Alternative
        'title': 'title',
        'patent_title': 'title',
        'abstract': 'abstract',
        'patent_abstract': 'abstract',
        'date': 'filing_date',
        'filing_date': 'filing_date',
        'grant_date': 'filing_date',
        'inventor_id': 'inventor_id',
        'inventor_name': 'inventor_name',
        'inventor_first_name': 'inventor_first',
        'inventor_last_name': 'inventor_last',
        'country': 'country',
        'inventor_country': 'country',
        'assignee_id': 'company_id',
        'organization': 'company_name',
        'assignee_organization': 'company_name',
        'company_name': 'company_name'
    }
    
    # Rename columns to standard names if they match our mapping
    df = df.rename(columns={col: column_mapping[col] for col in df.columns if col in column_mapping})
    
    print("Cleaning messy data and fixing missing values...")
    
    # 1. Fill missing values
    if 'title' in df.columns:
        df['title'] = df['title'].fillna('Unknown Title')
    if 'abstract' in df.columns:
        df['abstract'] = df['abstract'].fillna('No abstract available')
        
    # Combine first and last name if inventor_name is split
    if 'inventor_name' not in df.columns and 'inventor_first' in df.columns and 'inventor_last' in df.columns:
        df['inventor_name'] = df['inventor_first'].fillna('') + ' ' + df['inventor_last'].fillna('')
        df['inventor_name'] = df['inventor_name'].str.strip()
        
    if 'inventor_name' in df.columns:
        df['inventor_name'] = df['inventor_name'].fillna('Unknown Inventor')
        
    if 'company_name' in df.columns:
        df['company_name'] = df['company_name'].fillna('Unknown Company')
        
    if 'country' in df.columns:
        df['country'] = df['country'].fillna('Unknown')
        
    # Generate IDs if they don't exist in the flat file
    if 'inventor_id' not in df.columns and 'inventor_name' in df.columns:
        df['inventor_id'] = df.groupby('inventor_name').ngroup()
        
    if 'company_id' not in df.columns and 'company_name' in df.columns:
        df['company_id'] = df.groupby('company_name').ngroup()

    # 2. Fix and extract Date/Year
    if 'filing_date' in df.columns:
        # Convert to datetime, coercing errors to NaT
        df['filing_date'] = pd.to_datetime(df['filing_date'], errors='coerce')
        # Extract year, filling missing with 0 and converting to int
        df['year'] = df['filing_date'].dt.year.fillna(0).astype(int)
        # Convert back to string format YYYY-MM-DD
        df['filing_date'] = df['filing_date'].dt.strftime('%Y-%m-%d').fillna('1970-01-01')

    print("Organizing into relational tables...")
    
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)
    
    # --- TABLE 1: PATENTS ---
    patents_cols = ['patent_id', 'title', 'abstract', 'filing_date', 'year']
    existing_patents_cols = [c for c in patents_cols if c in df.columns]
    
    if 'patent_id' in df.columns:
        patents_df = df[existing_patents_cols].drop_duplicates(subset=['patent_id'])
        patents_df.to_csv(os.path.join(output_dir, 'clean_patents.csv'), index=False)
        print(f"Saved {len(patents_df)} records to clean_patents.csv")
    else:
        print("Warning: 'patent_id' not found. Could not generate clean_patents.csv")

    # --- TABLE 2: INVENTORS ---
    inventors_cols = ['inventor_id', 'inventor_name', 'country']
    existing_inv_cols = [c for c in inventors_cols if c in df.columns]
    
    if 'inventor_id' in df.columns:
        inventors_df = df[existing_inv_cols].drop_duplicates(subset=['inventor_id'])
        inventors_df = inventors_df.rename(columns={'inventor_name': 'name'})
        inventors_df.to_csv(os.path.join(output_dir, 'clean_inventors.csv'), index=False)
        print(f"Saved {len(inventors_df)} records to clean_inventors.csv")
    else:
         print("Warning: 'inventor_id' not found. Could not generate clean_inventors.csv")

    # --- TABLE 3: COMPANIES ---
    companies_cols = ['company_id', 'company_name']
    existing_comp_cols = [c for c in companies_cols if c in df.columns]
    
    if 'company_id' in df.columns:
        companies_df = df[existing_comp_cols].drop_duplicates(subset=['company_id'])
        companies_df = companies_df.rename(columns={'company_name': 'name'})
        companies_df.to_csv(os.path.join(output_dir, 'clean_companies.csv'), index=False)
        print(f"Saved {len(companies_df)} records to clean_companies.csv")
    else:
         print("Warning: 'company_id' not found. Could not generate clean_companies.csv")

    # --- TABLE 4: RELATIONSHIPS ---
    rel_cols = ['patent_id', 'inventor_id', 'company_id']
    existing_rel_cols = [c for c in rel_cols if c in df.columns]
    
    if all(c in df.columns for c in ['patent_id', 'inventor_id', 'company_id']):
        relationships_df = df[existing_rel_cols].drop_duplicates()
        relationships_df.to_csv(os.path.join(output_dir, 'clean_relationships.csv'), index=False)
        print(f"Saved {len(relationships_df)} records to clean_relationships.csv")
    else:
         print("Warning: Missing IDs for relationship table. Could not generate clean_relationships.csv")

    print("Data cleaning process completed successfully!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean raw PatentsView data.")
    parser.add_argument('input_file', type=str, help="Path to the raw CSV or TSV data file.")
    args = parser.parse_args()
    
    clean_data(args.input_file)
