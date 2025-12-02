import sqlite3
import os

# Path to the database
db_path = os.path.join(os.path.dirname(__file__), "reflex.db")

def migrate_refund_fields():
    """Add refund_status and refund_approved_at fields to booking table"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if refund_status column exists
        cursor.execute("PRAGMA table_info(booking)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add refund_status if it doesn't exist
        if "refund_status" not in columns:
            print("Adding refund_status column...")
            cursor.execute("ALTER TABLE booking ADD COLUMN refund_status TEXT")
            print("✓ Added refund_status column")
        else:
            print("✓ refund_status column already exists")
        
        # Add refund_approved_at if it doesn't exist
        if "refund_approved_at" not in columns:
            print("Adding refund_approved_at column...")
            cursor.execute("ALTER TABLE booking ADD COLUMN refund_approved_at TIMESTAMP")
            print("✓ Added refund_approved_at column")
        else:
            print("✓ refund_approved_at column already exists")
        
        conn.commit()
        print("\n✓ Migration completed successfully!")
        
    except sqlite3.Error as e:
        print(f"✗ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("Starting migration for refund approval fields...")
    migrate_refund_fields()
