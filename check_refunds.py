import sqlite3
import os

# Path to the database
db_path = os.path.join(os.path.dirname(__file__), "reflex.db")

def check_pending_refunds():
    """Check for bookings with pending refund status"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check all cancelled bookings
        cursor.execute("""
            SELECT id, status, payment_status, refund_status, refund_amount, cancellation_at 
            FROM booking 
            WHERE status = 'Cancelled'
            ORDER BY id DESC
            LIMIT 10
        """)
        
        bookings = cursor.fetchall()
        
        print(f"\n📋 Found {len(bookings)} cancelled bookings:")
        print("-" * 100)
        
        for booking in bookings:
            booking_id, status, payment_status, refund_status, refund_amount, cancelled_at = booking
            print(f"ID: {booking_id} | Status: {status} | Payment: {payment_status} | Refund Status: {refund_status} | Amount: RM {refund_amount} | Cancelled: {cancelled_at}")
        
        # Count pending refunds
        cursor.execute("SELECT COUNT(*) FROM booking WHERE refund_status = 'Pending'")
        pending_count = cursor.fetchone()[0]
        
        print(f"\n✅ Total bookings with refund_status = 'Pending': {pending_count}")
        
        # Show bookings with NULL refund_status that have refund_amount > 0
        cursor.execute("""
            SELECT id, status, payment_status, refund_status, refund_amount 
            FROM booking 
            WHERE status = 'Cancelled' AND refund_amount > 0 AND (refund_status IS NULL OR refund_status = '')
            LIMIT 5
        """)
        
        null_status = cursor.fetchall()
        if null_status:
            print(f"\n⚠️ Found {len(null_status)} cancelled bookings with refund amount but NULL/empty refund_status:")
            for b in null_status:
                print(f"   ID: {b[0]} | Status: {b[1]} | Payment: {b[2]} | Refund Status: '{b[3]}' | Amount: RM {b[4]}")
        
    except sqlite3.Error as e:
        print(f"✗ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Checking database for pending refunds...")
    check_pending_refunds()
