"""
Setup a test Auto-Booking Rule for TOMORROW to verify the Smart Dashboard logic.
"""
import sqlite3
import os
from datetime import datetime, timedelta

db_path = os.path.join(os.path.dirname(__file__), "reflex.db")

def setup_test_rule():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Get a user
        cursor.execute("SELECT id, email FROM user LIMIT 1")
        user = cursor.fetchone()
        if not user:
            print("❌ No users found.")
            return

        # 2. Get a parking lot
        cursor.execute("SELECT name, location FROM parkinglot LIMIT 1")
        lot = cursor.fetchone()
        if not lot:
            print("❌ No parking lots found.")
            return
            
        lot_str = f"{lot[0]} - {lot[1]}"
        
        # 3. Determine Tomorrow's Day
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow_day = tomorrow.strftime("%a") # e.g., "Wed"
        
        print(f"Setting up rule for User: {user[1]}")
        print(f"Location: {lot_str}")
        print(f"Day: {tomorrow_day}")
        
        # 4. Create or Update Rule
        # Check if rule exists
        cursor.execute("""
            SELECT id FROM bookingrule 
            WHERE user_id = ? AND location = ?
        """, (user[0], lot_str))
        
        existing_rule = cursor.fetchone()
        
        if existing_rule:
            print("Updating existing rule...")
            cursor.execute("""
                UPDATE bookingrule 
                SET days = ?, status = 'Active', time = '08:00', duration = '2 hours'
                WHERE id = ?
            """, (tomorrow_day, existing_rule[0]))
        else:
            print("Creating new rule...")
            cursor.execute("""
                INSERT INTO bookingrule (location, days, time, duration, status, next_run, user_id, created_at)
                VALUES (?, ?, '08:00', '2 hours', 'Active', 'Tomorrow', ?, ?)
            """, (lot_str, tomorrow_day, user[0], datetime.now()))
            
        conn.commit()
        print("✅ Auto-Booking Rule Set Up Successfully!")
        print(f"   Rule: Book {lot_str} every {tomorrow_day} at 08:00 for 2 hours")
        print("\n👉 INSTRUCTIONS:")
        print("1. Go to 'Smart Dashboard' page.")
        print("2. The page load should trigger the auto-booking.")
        print("3. You should see a toast message: 'Auto-booked 1 spots for tomorrow!'")
        print("4. Check 'My Bookings' to confirm.")
        
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    setup_test_rule()
