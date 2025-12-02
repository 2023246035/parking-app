import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "reflex.db")

def analyze_last_cancellation():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get the most recently cancelled booking
    cursor.execute("""
        SELECT id, start_date, start_time, total_price, refund_amount, cancellation_at, status
        FROM booking 
        WHERE status = 'Cancelled'
        ORDER BY cancellation_at DESC
        LIMIT 1
    """)
    
    booking = cursor.fetchone()
    
    if booking:
        id, start_date, start_time, price, refund, cancelled_at, status = booking
        print(f"Latest Cancelled Booking: BK-{id}")
        print(f"Booking Time: {start_date} {start_time}")
        print(f"Cancelled At: {cancelled_at}")
        print(f"Total Price: {price}")
        print(f"Refund Amount Calculated: {refund}")
        
        if refund == 0:
            print("\n⚠️ REASON: Refund amount is 0.0")
            print("   -> System auto-cancelled without Admin Approval (Correct Behavior)")
        else:
            print("\n✅ Refund amount is > 0")
            print("   -> Should be in Admin Portal")
            
    else:
        print("No cancelled bookings found.")
    
    conn.close()

if __name__ == "__main__":
    analyze_last_cancellation()
