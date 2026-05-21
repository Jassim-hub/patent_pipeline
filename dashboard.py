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
    SELECT inventor_name as name, total_patents as patents
    FROM top_inventors
    ORDER BY total_patents DESC
    LIMIT 10
    """
    df_inv = load_data(inventor_query)
    if not df_inv.empty:
        st.bar_chart(df_inv.set_index('name'))
    else:
        st.warning("No data found or database not initialized.")

with col2:
    st.subheader("Top 10 Companies")
    company_query = """
    SELECT company_name as name, total_patents as patents
    FROM top_companies
    ORDER BY total_patents DESC
    LIMIT 10
    """
    df_comp = load_data(company_query)
    if not df_comp.empty:
        st.bar_chart(df_comp.set_index('name'))

st.subheader("Top Countries")
country_query = """
SELECT country as name, total_patents as patents
FROM country_trends
ORDER BY total_patents DESC
"""
df_trends = load_data(country_query)
if not df_trends.empty:
    st.bar_chart(df_trends.set_index('name'))

st.markdown("---")
st.markdown("*Built for the Global Patent Intelligence Data Pipeline Project.*")
