"""
Create a FUTURE booking that is eligible for a refund.
"""
import sqlite3
import os
from datetime import datetime, timedelta

db_path = os.path.join(os.path.dirname(__file__), "reflex.db")

def create_refundable_booking():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Get a user
        cursor.execute("SELECT id, email FROM user LIMIT 1")
        user = cursor.fetchone()
        if not user:
            print("❌ No users found. Please register a user first.")
            return

        # 2. Get a parking lot
        cursor.execute("SELECT id, price_per_hour FROM parkinglot LIMIT 1")
        lot = cursor.fetchone()
        if not lot:
            print("❌ No parking lots found.")
            return

        # 3. Create a booking for TOMORROW (eligible for refund)
        tomorrow = datetime.now() + timedelta(days=1)
        start_date = tomorrow.strftime("%Y-%m-%d")
        start_time = "10:00"
        
        cursor.execute("""
            INSERT INTO booking (
                lot_id, user_id, start_date, start_time, duration_hours, 
                total_price, status, created_at, payment_status, 
                refund_amount, is_refundable, slot_id, vehicle_number, phone_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lot[0], user[0], start_date, start_time, 2, 
            lot[1] * 2, "Confirmed", datetime.now(), "Paid", 
            0.0, True, "TEST-A1", "TEST-CAR", "0123456789"
        ))
        
        booking_id = cursor.lastrowid
        conn.commit()
        
        print(f"\n✅ Created Refundable Booking!")
        print(f"   Booking ID: BK-{booking_id}")
        print(f"   Date: {start_date} at {start_time}")
        print(f"   User: {user[1]}")
        print(f"\n👉 INSTRUCTIONS:")
        print(f"1. Login as {user[1]}")
        print(f"2. Go to 'My Bookings'")
        print(f"3. You will see this new booking for TOMORROW")
        print(f"4. Click 'Cancel'")
        print(f"5. You should see a refund amount (50% or 100%)")
        print(f"6. Confirm cancellation")
        print(f"7. THEN check the Admin Portal > Refunds")
        
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_refundable_booking()
