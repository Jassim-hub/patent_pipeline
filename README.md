# Global Patent Intelligence Data Pipeline

A data engineering pipeline built to process, clean, store, and analyze the PatentsView Granted Patent Disambiguated Data.

## Prerequisites
- Python 3.8+
- pandas
- sqlite3 (built-in)
- streamlit (optional, for dashboard)
- matplotlib, seaborn (optional, for dashboard)

## Setup and Execution

### 1. Prepare the Data
1. Download the "Granted Patent Disambiguated Data" file from the [USPTO Bulk Data portal](https://data.uspto.gov/bulkdata/datasets/pvgpatdis).
2. Save the extracted TSV or CSV file to your computer.

### 2. Clean the Data
The PatentsView data comes as multiple `.tsv` files. Place all the extracted files (`g_patent.tsv`, `g_patent_abstract.tsv`, `g_application.tsv`, `g_inventor_disambiguated.tsv`, `g_assignee_disambiguated.tsv`, `g_location_disambiguated.tsv`) into a single directory (e.g., `raw_data_dir/`).

Run the cleaning script and point it to that directory:
```bash
python 01_clean_data.py "path/to/your/raw_data_dir/"
```
*This will parse the distinct TSV files, join them via `patent_id`, handle missing values, and output normalized tables to the `data/` folder.*

### 3. Load into Database
Initialize the SQLite database (`patents.db`) and load the cleaned CSVs:
```bash
python 02_load_data.py
```

### 4. Analyze Data and Generate Reports
Execute the analytical SQL queries and generate the Console Report, CSVs, and JSON files:
```bash
python 03_analyze_data.py
```

### 5. View Dashboard (Extra Credit)
To launch the interactive data visualization dashboard:
```bash
pip install streamlit pandas matplotlib seaborn
streamlit run dashboard.py
```

## SQL Queries
The file `queries.sql` contains the requested analytical SQL answers (Q1-Q7), including JOINs, CTEs, and Window Ranking functions.

## Output Files
- `top_inventors.csv`
- `top_companies.csv`
- `country_trends.csv`
- `report.json`
- `patents.db` (SQLite Database)
