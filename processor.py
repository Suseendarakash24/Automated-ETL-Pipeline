import pandas as pd
import os
import requests
import database

DISCORD_WEBHOOK_URL = "DISCORD_WEBHOOK_URL_HERE" 

def send_alert(message):
    
    # If it's a real URL, send it to Discord!
    payload = {"content": f"🚨 ETL Pipeline Alert:\n{message}"}
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        # Discord returns 204 No Content on success
        if response.status_code in [200, 204]:
            print("✅ Discord alert sent successfully!")
        else:
            print(f"⚠️ Discord alert failed. Status code: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error sending Discord alert: {e}")

def process_file(filepath, filename):
    try:
        config = database.load_config()
        table_name = config['table_name']
        required_cols = config['required_columns']
        rules = config['rules']
        
        # 1. Read just the first row to check headers
        df_preview = pd.read_csv(filepath, nrows=1)
        actual_cols = df_preview.columns.tolist()
        
        # 2. Strict Schema Validation
        missing_cols = [col for col in required_cols if col not in actual_cols]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        total_initial = 0
        total_cleaned = 0
        total_final = 0
        
        # 3. Process in chunks of 10,000 (Saves RAM!)
        chunk_iterator = pd.read_csv(filepath, chunksize=10000, dtype=str)
        
        for chunk in chunk_iterator:
            total_initial += len(chunk)
            
            # Keep ONLY the columns defined in the config
            chunk = chunk[required_cols]
            rows_before = len(chunk)
            
            # Apply cleaning rules from JSON
            for col, props in rules.items():
                chunk[col] = chunk[col].astype(str).str.strip()
                if props.get('required'):
                    chunk = chunk[chunk[col].notna() & (chunk[col] != 'nan') & (chunk[col] != '')]
            
            # Remove exact duplicates based on the 'unique' column
            unique_cols = [c for c, p in rules.items() if p.get('unique')]
            rows_before_dups = len(chunk)
            chunk = chunk.drop_duplicates(subset=unique_cols)
            
            total_cleaned += (rows_before - len(chunk)) + (rows_before_dups - len(chunk))
            total_final += len(chunk)
            
            # 4. Save clean chunk to DB
            data_to_insert = [tuple(x) for x in chunk.to_numpy()]
            database.save_clean_data(table_name, required_cols, data_to_insert)
        
        # 5. Log Success
        database.log_processing(filename, "SUCCESS", total_initial, total_cleaned, total_final)
        
        alert_msg = (f"✅ Processed: '{filename}'\n"
                     f"Initial: {total_initial:,} | Final: {total_final:,}\n"
                     f"Rows Cleaned/Dropped: {total_cleaned:,}")
        send_alert(alert_msg)
        print(f"✅ Successfully processed {filename} via JSON config!")
        
        return True # TELL MAIN.PY IT WORKED
        
    except Exception as e:
        database.log_processing(filename, "FAILED", 0, 0, 0, str(e))
        send_alert(f"❌ Failed: '{filename}'\nError: {str(e)}")
        print(f" Failed: {e}")
        
        return False # TELL MAIN.PY IT FAILED