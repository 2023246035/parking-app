import sqlite3
import os

def ensure_booking_columns():
    db_path = 'reflex.db'
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(booking)")
        columns = [info[1] for info in cursor.fetchall()]
        
        # Add vehicle_number if missing
        if 'vehicle_number' not in columns:
            print("Adding vehicle_number column...")
            cursor.execute("ALTER TABLE booking ADD COLUMN vehicle_number TEXT")
            print("vehicle_number added.")
            
        # Add phone_number if missing
        if 'phone_number' not in columns:
            print("Adding phone_number column...")
            cursor.execute("ALTER TABLE booking ADD COLUMN phone_number TEXT")
            print("phone_number added.")
            
        conn.commit()
        print("Database schema updated successfully.")
            
    except Exception as e:
        print(f"Error updating database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    ensure_booking_columns()
