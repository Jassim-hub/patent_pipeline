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
Run the cleaning script and point it to the downloaded file:
```bash
python 01_clean_data.py "path/to/your/downloaded_data.csv"
```
*This will parse the data, handle missing values, and output normalized tables to the `data/` folder.*

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
