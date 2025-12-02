import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "reflex.db")

def check_latest_booking():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, start_date, status FROM booking ORDER BY id DESC LIMIT 1")
    booking = cursor.fetchone()
    if booking:
        print(f"Latest Booking: BK-{booking[0]} | Date: {booking[1]} | Status: {booking[2]}")
    else:
        print("No bookings found.")
    conn.close()

if __name__ == "__main__":
    check_latest_booking()
