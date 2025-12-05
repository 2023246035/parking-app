"""
Database Update Script - Add rejection_reason field to Booking table
Run this script to add the rejection_reason column to your existing database
"""
import sqlite3
import os

DB_PATH = "parking_app.db"

def update_database():
    """Add rejection_reason column to booking table"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        print("   Run 'reflex db init' first to create the database")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(booking)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'rejection_reason' in columns:
            print("✅ rejection_reason column already exists!")
            print("   No changes needed.")
            return True
        
        # Add the column
        print("📝 Adding rejection_reason column to booking table...")
        cursor.execute("""
            ALTER TABLE booking 
            ADD COLUMN rejection_reason TEXT
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Successfully added rejection_reason column!")
        print("\nNext steps:")
        print("1. Update app/db/models.py to include:")
        print("   rejection_reason: Optional[str] = Field(default=None)")
        print("\n2. Update app/pages/admin_refunds.py line ~128 to:")
        print("   booking.rejection_reason = self.rejection_reason")
        print("\n3. Restart your Reflex application")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("DATABASE UPDATE: Add rejection_reason Field")
    print("="*60 + "\n")
    
    print(f"Database: {DB_PATH}\n")
    
    response = input("Do you want to proceed? (y/n): ").strip().lower()
    
    if response == 'y':
        print()
        if update_database():
            print("\n✅ Database update completed successfully!")
        else:
            print("\n❌ Database update failed!")
    else:
        print("\n❌ Operation cancelled by user")
    
    print("\n" + "="*60 + "\n")
