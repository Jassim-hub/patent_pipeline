import pandas as pd
import os
import argparse

CHUNK_SIZE = 250000

def process_file_in_chunks(input_file, output_file, usecols, transform_func=None):
    if not os.path.exists(input_file):
        print(f"Warning: {input_file} not found. Skipping.")
        return False
        
    print(f"Processing {os.path.basename(input_file)} in chunks of {CHUNK_SIZE}...")
    
    # Remove existing output file to start fresh
    if os.path.exists(output_file):
        os.remove(output_file)
        
    chunk_count = 0
    
    for chunk in pd.read_csv(input_file, sep='\t', low_memory=False, usecols=usecols, chunksize=CHUNK_SIZE):
        if transform_func:
            chunk = transform_func(chunk)
            
        # Append to CSV
        mode = 'w' if chunk_count == 0 else 'a'
        header = True if chunk_count == 0 else False
        chunk.to_csv(output_file, mode=mode, header=header, index=False)
        chunk_count += 1
        print(f"  ...processed {chunk_count * CHUNK_SIZE} rows")
        
    print(f"Completed {os.path.basename(output_file)}.")
    return True

def clean_data(data_dir):
    print(f"Starting chunk-based cleaning pipeline from {data_dir}...")
    
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)

    # 1. Patent Base
    def transform_patent(df):
        df = df.rename(columns={'patent_title': 'title'})
        df['title'] = df['title'].fillna('Unknown Title')
        return df
        
    process_file_in_chunks(
        os.path.join(data_dir, "g_patent.tsv"),
        os.path.join(output_dir, "stg_patent.csv"),
        usecols=['patent_id', 'patent_title'],
        transform_func=transform_patent
    )

    # 2. Patent Abstract
    def transform_abstract(df):
        df = df.rename(columns={'patent_abstract': 'abstract'})
        df['abstract'] = df['abstract'].fillna('No abstract available')
        return df
        
    process_file_in_chunks(
        os.path.join(data_dir, "g_patent_abstract.tsv"),
        os.path.join(output_dir, "stg_abstract.csv"),
        usecols=['patent_id', 'patent_abstract'],
        transform_func=transform_abstract
    )

    # 3. Application (Dates)
    def transform_application(df):
        df['filing_date'] = pd.to_datetime(df['filing_date'], errors='coerce')
        df['year'] = df['filing_date'].dt.year.fillna(0).astype(int)
        df['filing_date'] = df['filing_date'].dt.strftime('%Y-%m-%d').fillna('1970-01-01')
        return df

    process_file_in_chunks(
        os.path.join(data_dir, "g_application.tsv"),
        os.path.join(output_dir, "stg_application.csv"),
        usecols=['patent_id', 'filing_date'],
        transform_func=transform_application
    )

    # 4. Inventors
    def transform_inventor(df):
        df['name'] = df['disambig_inventor_name_first'].fillna('') + ' ' + df['disambig_inventor_name_last'].fillna('')
        df['name'] = df['name'].str.strip().replace('', 'Unknown Inventor')
        return df[['patent_id', 'inventor_id', 'name', 'location_id']].dropna(subset=['inventor_id'])

    process_file_in_chunks(
        os.path.join(data_dir, "g_inventor_disambiguated.tsv"),
        os.path.join(output_dir, "stg_inventor.csv"),
        usecols=['patent_id', 'inventor_id', 'disambig_inventor_name_first', 'disambig_inventor_name_last', 'location_id'],
        transform_func=transform_inventor
    )

    # 5. Assignees (Companies)
    def transform_assignee(df):
        df = df.rename(columns={'disambig_assignee_organization': 'company_name'})
        df['company_name'] = df['company_name'].fillna('Unknown Company')
        return df.dropna(subset=['assignee_id'])

    process_file_in_chunks(
        os.path.join(data_dir, "g_assignee_disambiguated.tsv"),
        os.path.join(output_dir, "stg_assignee.csv"),
        usecols=['patent_id', 'assignee_id', 'disambig_assignee_organization'],
        transform_func=transform_assignee
    )

    # 6. Locations
    def transform_location(df):
        df = df.rename(columns={'disambig_country': 'country'})
        df['country'] = df['country'].fillna('Unknown')
        return df.drop_duplicates()

    process_file_in_chunks(
        os.path.join(data_dir, "g_location_disambiguated.tsv"),
        os.path.join(output_dir, "stg_location.csv"),
        usecols=['location_id', 'disambig_country'],
        transform_func=transform_location
    )

    print("\nData chunking and cleaning completed successfully! Run 02_load_data.py to merge them into the database.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean raw PatentsView TSV files using chunking.")
    parser.add_argument('data_dir', type=str, help="Directory containing the extracted PatentsView TSV files.")
    args = parser.parse_args()
    clean_data(args.data_dir)
