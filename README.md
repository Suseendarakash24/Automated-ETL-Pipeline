#  DataFlow ETL Engine

An automated, configuration-driven ETL (Extract, Transform, Load) pipeline built with Python. It monitors directories for incoming CSV files, processes them in memory-efficient chunks, validates data against a JSON schema, and loads clean data into a SQLite database with real-time Discord alerts.

## ✨ Key Features
- **Memory-Efficient Chunking:** Processes large datasets (GBs in size) in 10,000-row batches, keeping RAM usage under 100MB.
- **Configuration-Driven:** Uses a `schema_config.json` file to dynamically define columns, data types, and validation rules without changing Python code.
- **Automated Data Quality:** Automatically detects and quarantines duplicates, null values, and invalid formats (e.g., regex email checks).
- **Real-Time Observability:** Integrated Discord webhooks for instant pipeline success/failure notifications.
- **Interactive Dashboard:** A Streamlit UI for live data exploration, business analytics, and pipeline health monitoring.

## 🛠️ Tech Stack
- **Backend:** Python, Pandas, Watchdog (File System Events)
- **Database:** SQLite
- **Frontend/Analytics:** Streamlit
- **DevOps/Alerting:** Discord Webhooks, JSON Configuration

## 📂 Project Structure
```text
etl_pipeline/
├── main.py                 # File watcher entry point
├── processor.py            # Chunked ETL logic & cleaning rules
├── database.py             # SQLite dynamic table creation & logging
├── dashboard.py            # Streamlit analytics UI
├── schema_config.json      # Configuration rules for the pipeline
├── requirements.txt        # Python dependencies
└── README.md