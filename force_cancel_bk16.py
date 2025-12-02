"""
Force cancel BK-16 to demonstrate admin portal functionality
"""
import sqlite3
import os
from datetime import datetime

db_path = os.path.join(os.path.dirname(__file__), "reflex.db")

def cancel_bk16():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if BK-16 exists and is confirmed
    cursor.execute("SELECT total_price FROM booking WHERE id = 16 AND status = 'Confirmed'")
    row = cursor.fetchone()
    
    if not row:
        print("BK-16 is not in 'Confirmed' state (might be already cancelled or missing).")
        return

    total_price = row[0]
    refund_amount = total_price * 0.5  # 50% refund logic
    
    print(f"Cancelling BK-16...")
    print(f"Total Price: {total_price}")
    print(f"Refund Amount: {refund_amount}")
    
    cursor.execute("""
        UPDATE booking 
        SET status = 'Cancelled',
            refund_status = 'Pending',
            refund_amount = ?,
            payment_status = 'Pending Refund',
            cancellation_at = ?,
            cancellation_reason = 'Simulated User Cancellation'
        WHERE id = 16
    """, (refund_amount, datetime.now()))
    
    conn.commit()
    print("✅ BK-16 Cancelled successfully with refund_status='Pending'")
    conn.close()

if __name__ == "__main__":
    cancel_bk16()
