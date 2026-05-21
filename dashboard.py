import streamlit as st
import pandas as pd
import sqlite3
import os

try:
    import psycopg2
except ImportError:
    psycopg2 = None

st.set_page_config(page_title="Global Patent Intelligence", layout="wide")

st.title("Global Patent Intelligence Dashboard")

DB_NAME = "patents.db"
DATABASE_URL = os.getenv("DATABASE_URL") or st.secrets.get("DATABASE_URL", "")


def get_connection():
    if DATABASE_URL:
        if psycopg2 is None:
            raise RuntimeError("psycopg2 is required for DATABASE_URL connections")
        return psycopg2.connect(DATABASE_URL)

    if not os.path.exists(DB_NAME):
        return None

    return sqlite3.connect(DB_NAME)

@st.cache_data
def load_data(query):
    try:
        conn = get_connection()
        if conn is None:
            return pd.DataFrame()
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


if not DATABASE_URL and not os.path.exists(DB_NAME):
    st.error(
        "No database is available in this deployment. Add a Supabase/Postgres DATABASE_URL secret or include a usable patents.db file."
    )
    st.stop()

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
if DATABASE_URL:
    trends_query = """
    SELECT year, COUNT(patent_id) as patents
    FROM patents
    WHERE year > 1900 AND year <= EXTRACT(YEAR FROM CURRENT_DATE)
    GROUP BY year
    ORDER BY year
    """
else:
    trends_query = """
    SELECT year, COUNT(patent_id) as patents
    FROM patents
    WHERE year > 1900 AND year <= CAST(strftime('%Y', 'now') AS INTEGER)
    GROUP BY year
    ORDER BY year
    """
df_trends = load_data(trends_query)
if not df_trends.empty:
    st.line_chart(df_trends.set_index('year'))

st.markdown("---")
st.markdown("*Built for the Global Patent Intelligence Data Pipeline Project.*")
