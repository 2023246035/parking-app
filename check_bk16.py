import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "reflex.db")

def check_booking_16():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, status, payment_status, refund_status, refund_amount, start_date, start_time, cancellation_at 
        FROM booking 
        WHERE id = 16
    """)
    booking = cursor.fetchone()
    
    if booking:
        print(f"Booking ID: {booking[0]}")
        print(f"Status: {booking[1]}")
        print(f"Payment Status: {booking[2]}")
        print(f"Refund Status: '{booking[3]}'")
        print(f"Refund Amount: {booking[4]}")
        print(f"Start: {booking[5]} {booking[6]}")
        print(f"Cancelled At: {booking[7]}")
    else:
        print("Booking 16 not found.")
    conn.close()

if __name__ == "__main__":
    check_booking_16()
