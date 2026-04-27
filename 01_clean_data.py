import pandas as pd
import os
import argparse

def clean_data(data_dir):
    print(f"Reading raw PatentsView files from directory: {data_dir}...")
    
    # Expected file names based on the data dictionary
    file_patent = os.path.join(data_dir, "g_patent.tsv")
    file_abstract = os.path.join(data_dir, "g_patent_abstract.tsv")
    file_application = os.path.join(data_dir, "g_application.tsv")
    file_inventor = os.path.join(data_dir, "g_inventor_disambiguated.tsv")
    file_assignee = os.path.join(data_dir, "g_assignee_disambiguated.tsv")
    file_location = os.path.join(data_dir, "g_location_disambiguated.tsv")

    # Read the data - specifying low_memory=False and sep='\t' for PV TSV files
    try:
        print("Loading g_patent.tsv...")
        df_patent = pd.read_csv(file_patent, sep='\t', low_memory=False, usecols=['patent_id', 'patent_title'])
        print("Loading g_patent_abstract.tsv...")
        df_abstract = pd.read_csv(file_abstract, sep='\t', low_memory=False, usecols=['patent_id', 'patent_abstract'])
        print("Loading g_application.tsv...")
        df_application = pd.read_csv(file_application, sep='\t', low_memory=False, usecols=['patent_id', 'filing_date'])
        
        print("Loading g_inventor_disambiguated.tsv...")
        df_inventor = pd.read_csv(file_inventor, sep='\t', low_memory=False, usecols=['patent_id', 'inventor_id', 'disambig_inventor_name_first', 'disambig_inventor_name_last', 'location_id'])
        
        print("Loading g_assignee_disambiguated.tsv...")
        df_assignee = pd.read_csv(file_assignee, sep='\t', low_memory=False, usecols=['patent_id', 'assignee_id', 'disambig_assignee_organization'])
        
        print("Loading g_location_disambiguated.tsv...")
        df_location = pd.read_csv(file_location, sep='\t', low_memory=False, usecols=['location_id', 'disambig_country'])
        
    except FileNotFoundError as e:
        print(f"Error: Could not find required file. {e}")
        print("Please ensure all required PatentsView TSV files are in the specified directory.")
        return

    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n--- Processing Table 1: PATENTS ---")
    # Merge patent, abstract, and application
    df_patents_clean = pd.merge(df_patent, df_abstract, on='patent_id', how='left')
    df_patents_clean = pd.merge(df_patents_clean, df_application, on='patent_id', how='left')
    
    # Rename columns to match our target schema
    df_patents_clean = df_patents_clean.rename(columns={
        'patent_title': 'title',
        'patent_abstract': 'abstract'
    })
    
    # Clean missing values
    df_patents_clean['title'] = df_patents_clean['title'].fillna('Unknown Title')
    df_patents_clean['abstract'] = df_patents_clean['abstract'].fillna('No abstract available')
    
    # Fix dates
    df_patents_clean['filing_date'] = pd.to_datetime(df_patents_clean['filing_date'], errors='coerce')
    df_patents_clean['year'] = df_patents_clean['filing_date'].dt.year.fillna(0).astype(int)
    df_patents_clean['filing_date'] = df_patents_clean['filing_date'].dt.strftime('%Y-%m-%d').fillna('1970-01-01')
    
    # Drop duplicates just in case
    df_patents_clean = df_patents_clean.drop_duplicates(subset=['patent_id'])
    
    df_patents_clean.to_csv(os.path.join(output_dir, 'clean_patents.csv'), index=False)
    print(f"Saved {len(df_patents_clean)} records to clean_patents.csv")


    print("\n--- Processing Table 2: INVENTORS ---")
    # Combine first and last name
    df_inventor['name'] = df_inventor['disambig_inventor_name_first'].fillna('') + ' ' + df_inventor['disambig_inventor_name_last'].fillna('')
    df_inventor['name'] = df_inventor['name'].str.strip().replace('', 'Unknown Inventor')
    
    # Merge with location to get country
    df_inv_loc = pd.merge(df_inventor, df_location, on='location_id', how='left')
    df_inv_loc = df_inv_loc.rename(columns={'disambig_country': 'country'})
    df_inv_loc['country'] = df_inv_loc['country'].fillna('Unknown')
    
    # Select distinct inventors
    df_inventors_clean = df_inv_loc[['inventor_id', 'name', 'country']].drop_duplicates(subset=['inventor_id'])
    # Filter out records where inventor_id is null
    df_inventors_clean = df_inventors_clean.dropna(subset=['inventor_id'])
    
    df_inventors_clean.to_csv(os.path.join(output_dir, 'clean_inventors.csv'), index=False)
    print(f"Saved {len(df_inventors_clean)} records to clean_inventors.csv")


    print("\n--- Processing Table 3: COMPANIES (ASSIGNEES) ---")
    df_assignee_clean = df_assignee[['assignee_id', 'disambig_assignee_organization']].copy()
    df_assignee_clean = df_assignee_clean.rename(columns={'disambig_assignee_organization': 'name'})
    df_assignee_clean['name'] = df_assignee_clean['name'].fillna('Unknown Company')
    
    # Select distinct assignees
    df_companies_clean = df_assignee_clean.drop_duplicates(subset=['assignee_id'])
    # Filter out null IDs
    df_companies_clean = df_companies_clean.dropna(subset=['assignee_id'])
    
    df_companies_clean.to_csv(os.path.join(output_dir, 'clean_companies.csv'), index=False)
    print(f"Saved {len(df_companies_clean)} records to clean_companies.csv")


    print("\n--- Processing Table 4: RELATIONSHIPS ---")
    # We need a table that maps patent_id -> inventor_id -> company_id
    # PatentsView defines relationships at the patent level.
    # An assignee owns a patent, and an inventor invented a patent.
    # We will join them on patent_id.
    
    rel_inv = df_inventor[['patent_id', 'inventor_id']].dropna()
    rel_ass = df_assignee[['patent_id', 'assignee_id']].dropna().rename(columns={'assignee_id': 'company_id'})
    
    # To map patent -> inventor -> company, we merge them on patent_id
    # This creates a row for every combination of inventor and company for a given patent.
    df_relationships = pd.merge(rel_inv, rel_ass, on='patent_id', how='inner')
    df_relationships = df_relationships.drop_duplicates()
    
    df_relationships.to_csv(os.path.join(output_dir, 'clean_relationships.csv'), index=False)
    print(f"Saved {len(df_relationships)} records to clean_relationships.csv")

    print("\nData cleaning process completed successfully! All tables adhere to the strict PatentsView Dictionary.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean raw PatentsView data from TSV files.")
    parser.add_argument('data_dir', type=str, help="Directory containing the extracted PatentsView TSV files (g_patent.tsv, g_application.tsv, etc).")
    args = parser.parse_args()
    
    clean_data(args.data_dir)
