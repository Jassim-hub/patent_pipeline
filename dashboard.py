import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as st_plt
import seaborn as sns

st.set_page_config(page_title="Global Patent Intelligence", layout="wide")

st.title("Global Patent Intelligence Dashboard")

DB_NAME = "patents.db"

@st.cache_data
def load_data(query):
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except sqlite3.Error:
        return pd.DataFrame()

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Inventors")
    inventor_query = """
    SELECT i.name, COUNT(r.patent_id) as patents
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    GROUP BY i.inventor_id
    ORDER BY patents DESC LIMIT 10
    """
    df_inv = load_data(inventor_query)
    if not df_inv.empty:
        st.bar_chart(df_inv.set_index('name'))
    else:
        st.warning("No data found or database not initialized.")

with col2:
    st.subheader("Top 10 Companies")
    company_query = """
    SELECT c.name, COUNT(r.patent_id) as patents
    FROM companies c
    JOIN relationships r ON c.company_id = r.company_id
    GROUP BY c.company_id
    ORDER BY patents DESC LIMIT 10
    """
    df_comp = load_data(company_query)
    if not df_comp.empty:
        st.bar_chart(df_comp.set_index('name'))

st.subheader("Patent Trends Over Time")
trends_query = """
SELECT year, COUNT(patent_id) as patents
FROM patents
WHERE year > 1900 AND year <= strftime('%Y', 'now')
GROUP BY year
ORDER BY year
"""
df_trends = load_data(trends_query)
if not df_trends.empty:
    st.line_chart(df_trends.set_index('year'))

st.markdown("---")
st.markdown("*Built for the Global Patent Intelligence Data Pipeline Project.*")
