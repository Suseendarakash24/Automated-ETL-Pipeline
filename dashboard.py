import streamlit as st
import sqlite3
import pandas as pd
import json

st.set_page_config(page_title="Config-Driven ETL Dashboard", layout="wide", page_icon="⚙️")
st.title("⚙️ Configuration-Driven ETL Dashboard")

DB_NAME = "pipeline.db"
CONFIG_FILE = "schema_config.json"

def get_db():
    return sqlite3.connect(DB_NAME)

conn = get_db()

with open(CONFIG_FILE, 'r') as f:
    config = json.load(f)
table_name = config['table_name']
display_cols = config['required_columns']

total_files = int(pd.read_sql_query("SELECT COUNT(*) as c FROM processing_log", conn).iloc[0]['c'])

if total_files == 0:
    st.info("👋 No files processed yet. Drop a CSV into the `incoming_files` folder!")
    st.stop()

total_initial = int(pd.read_sql_query("SELECT COALESCE(SUM(initial_rows), 0) FROM processing_log", conn).iloc[0, 0])
total_final = int(pd.read_sql_query("SELECT COALESCE(SUM(final_rows), 0) FROM processing_log WHERE status='SUCCESS'", conn).iloc[0, 0])
quality_score = (total_final / total_initial * 100) if total_initial > 0 else 100.0

col1, col2, col3 = st.columns(3)
col1.metric("📁 Files Processed", total_files)
col2.metric("📊 Total Records Loaded", f"{total_final:,}")
col3.metric("✨ Data Quality Score", f"{quality_score:.1f}%")

st.markdown("---")

st.subheader("📜 Recent Processing Logs")
log_df = pd.read_sql_query('''
    SELECT filename, status, initial_rows, final_rows, timestamp 
    FROM processing_log ORDER BY timestamp DESC LIMIT 5
''', conn)

def color_status(val):
    return 'color: green' if val == 'SUCCESS' else 'color: red'
st.dataframe(log_df.style.applymap(color_status, subset=['status']), use_container_width=True, hide_index=True)

st.markdown("---")

st.subheader(f" Live Data: `{table_name}`")
search = st.text_input("🔎 Search:", placeholder=f"Search in {', '.join(display_cols)}...")

query = f"SELECT {', '.join(display_cols)} FROM \"{table_name}\""
if search:
    conditions = [f"{col} LIKE '%{search}%'" for col in display_cols]
    query += f" WHERE {' OR '.join(conditions)}"
query += " LIMIT 100"

live_df = pd.read_sql_query(query, conn)
st.dataframe(live_df, use_container_width=True, height=400)

conn.close()