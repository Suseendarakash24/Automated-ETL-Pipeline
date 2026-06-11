import sqlite3
import json

DB_NAME = "pipeline.db"
CONFIG_FILE = "schema_config.json"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def setup_database():
    config = load_config()
    table_name = config['table_name']
    rules = config['rules']
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Create the target table dynamically based on JSON
    col_defs = []
    for col, props in rules.items():
        col_def = f'"{col}" {props["type"]}'
        if props.get('unique'):
            col_def += " UNIQUE"
        col_defs.append(col_def)
    
    cursor.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(col_defs)})')
    
    # 2. Create the processing log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processing_log (
            filename TEXT PRIMARY KEY,
            status TEXT,
            initial_rows INTEGER,
            rows_cleaned INTEGER,
            final_rows INTEGER,
            error_message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database setup complete for table: '{table_name}'")

def log_processing(filename, status, initial=0, cleaned=0, final=0, error=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO processing_log 
        (filename, status, initial_rows, rows_cleaned, final_rows, error_message)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (filename, status, initial, cleaned, final, error))
    conn.commit()
    conn.close()

def save_clean_data(table_name, columns, data_list):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    col_names = ", ".join([f'"{col}"' for col in columns])
    placeholders = ", ".join(["?" for _ in columns])
    
    query = f'INSERT OR IGNORE INTO "{table_name}" ({col_names}) VALUES ({placeholders})'
    cursor.executemany(query, data_list)
    
    conn.commit()
    conn.close()