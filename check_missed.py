import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "reflex.db")

def check_missed_refunds():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, status, payment_status, refund_status, refund_amount, cancellation_at 
        FROM booking 
        WHERE status = 'Cancelled' AND refund_amount > 0
    """)
    bookings = cursor.fetchall()
    
    print(f"Found {len(bookings)} cancelled bookings with refund > 0:")
    for b in bookings:
        print(f"ID: {b[0]} | Refund Status: '{b[3]}' | Amount: {b[4]}")

    conn.close()

if __name__ == "__main__":
    check_missed_refunds()
