import sqlite3
import os

def ensure_slot_id_column():
    db_path = 'reflex.db'
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(booking)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'slot_id' not in columns:
            print("Adding slot_id column to booking table...")
            cursor.execute("ALTER TABLE booking ADD COLUMN slot_id TEXT")
            conn.commit()
            print("Column added successfully.")
        else:
            print("slot_id column already exists.")
            
    except Exception as e:
        print(f"Error updating database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    ensure_slot_id_column()
