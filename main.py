import time
import os
import shutil
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import processor
import database

WATCH_FOLDER = os.path.join(os.getcwd(), "incoming_files")
PROCESSED_FOLDER = os.path.join(os.getcwd(), "processed_files")
FAILED_FOLDER = os.path.join(os.getcwd(), "failed_files")

os.makedirs(WATCH_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(FAILED_FOLDER, exist_ok=True)

# Thread-safe set to keep track of files currently being processed
processing_files = set()
lock = threading.Lock()

class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".csv"):
            filepath = event.src_path
            filename = os.path.basename(filepath)
            
            with lock:
                if filename in processing_files:
                    return
                processing_files.add(filename)
            
            print(f"👀 Detected new file: {filename}")
            time.sleep(2) 
            
            try:
                if not os.path.exists(filepath):
                    return

                # 1. Process the file and capture the True/False result
                success = processor.process_file(filepath, filename)
                
                # 2. Move to the CORRECT folder based on the result
                if os.path.exists(filepath):
                    if success:
                        shutil.move(filepath, os.path.join(PROCESSED_FOLDER, filename))
                        print(f"Moved '{filename}' to PROCESSED folder.\n")
                    else:
                        shutil.move(filepath, os.path.join(FAILED_FOLDER, filename))
                        print(f"️ Moved '{filename}' to FAILED folder.\n")
                        
            except Exception as e:
                print(f"❌ Unexpected error handling '{filename}': {e}\n")
            finally:
                with lock:
                    processing_files.discard(filename)

if __name__ == "__main__":
    print("🚀 Starting ETL Pipeline...")
    database.setup_database()
    
    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    observer.start()
    
    print(f"Watching folder: {WATCH_FOLDER}")
    print("Press Ctrl+C to stop.\n")
    
    try:
        while True:
            time.sleep(1) # Keep the script running
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Pipeline stopped.")
    observer.join()