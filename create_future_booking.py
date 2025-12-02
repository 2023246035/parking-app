"""
Create a FUTURE booking (Next Week) to guarantee 100% refund eligibility.
"""
import sqlite3
import os
from datetime import datetime, timedelta

db_path = os.path.join(os.path.dirname(__file__), "reflex.db")

def create_guaranteed_refund_booking():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Get a user
        cursor.execute("SELECT id, email FROM user LIMIT 1")
        user = cursor.fetchone()
        
        # 2. Get a parking lot
        cursor.execute("SELECT id, price_per_hour FROM parkinglot LIMIT 1")
        lot = cursor.fetchone()

        # 3. Create a booking for 7 DAYS FROM NOW
        future_date = datetime.now() + timedelta(days=7)
        start_date = future_date.strftime("%Y-%m-%d")
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
            0.0, True, "TEST-FUTURE", "TEST-CAR", "0123456789"
        ))
        
        booking_id = cursor.lastrowid
        conn.commit()
        
        print(f"\n✅ Created Booking BK-{booking_id} for {start_date}")
        print(f"   This booking is 7 days in the future.")
        print(f"   Cancelling it will give 100% refund.")
        print(f"   It WILL appear in Admin Portal.")
        
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_guaranteed_refund_booking()
