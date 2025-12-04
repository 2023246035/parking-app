"""
Migration script to add vehicle_number and phone_number to bookingrule table.
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "app", "reflex.db")
if not os.path.exists(db_path):
    # Try alternate path if running from root
    db_path = os.path.join(os.path.dirname(__file__), "reflex.db")

def migrate_booking_rule():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if columns exist
        cursor.execute("PRAGMA table_info(bookingrule)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "vehicle_number" not in columns:
            print("Adding vehicle_number column...")
            cursor.execute("ALTER TABLE bookingrule ADD COLUMN vehicle_number TEXT")
        else:
            print("vehicle_number column already exists.")
            
        if "phone_number" not in columns:
            print("Adding phone_number column...")
            cursor.execute("ALTER TABLE bookingrule ADD COLUMN phone_number TEXT")
        else:
            print("phone_number column already exists.")
            
        conn.commit()
        print("✅ Migration completed successfully.")
        
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_booking_rule()
