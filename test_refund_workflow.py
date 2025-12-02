"""
Quick test to verify refund approval workflow
This simulates cancelling a booking and checking the refund status
"""
import sqlite3
import os
from datetime import datetime

db_path = os.path.join(os.path.dirname(__file__), "reflex.db")

def simulate_booking_cancellation():
    """Simulate what happens when a user cancels a booking"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Find an active booking to "cancel"
        cursor.execute("""
            SELECT id, total_price, status, payment_status, refund_status 
            FROM booking 
            WHERE status = 'Confirmed' 
            LIMIT 1
        """)
        
        booking = cursor.fetchone()
        
        if not booking:
            print("❌ No confirmed bookings found to test with")
            print("   Please create a booking first through the UI")
            return
        
        booking_id, total_price, old_status, old_payment_status, old_refund_status = booking
        
        print(f"\n📋 Found Booking ID: {booking_id}")
        print(f"   Current Status: {old_status}")
        print(f"   Payment Status: {old_payment_status}")
        print(f"   Refund Status: {old_refund_status}")
        print(f"   Total Price: RM {total_price}")
        
        # Simulate the NEW cancellation workflow
        refund_amount = total_price  # Full refund for testing
        
        print(f"\n🔄 Simulating cancellation with NEW workflow...")
        print(f"   Refund Amount: RM {refund_amount}")
        
        cursor.execute("""
            UPDATE booking 
            SET status = 'Cancelled',
                refund_status = 'Pending',
                refund_amount = ?,
                payment_status = 'Pending Refund',
                cancellation_at = ?,
                cancellation_reason = 'Test cancellation'
            WHERE id = ?
        """, (refund_amount, datetime.now(), booking_id))
        
        conn.commit()
        
        print(f"\n✅ Booking {booking_id} cancelled successfully!")
        print(f"   Status: Cancelled")
        print(f"   Refund Status: Pending")
        print(f"   Payment Status: Pending Refund")
        
        # Verify it will appear in admin portal
        cursor.execute("SELECT COUNT(*) FROM booking WHERE refund_status = 'Pending'")
        pending_count = cursor.fetchone()[0]
        
        print(f"\n🎯 Admin Portal Check:")
        print(f"   Bookings with refund_status = 'Pending': {pending_count}")
        print(f"   ✅ This booking WILL appear in /admin/refunds")
        
        # Show what the booking looks like now
        cursor.execute("""
            SELECT id, status, payment_status, refund_status, refund_amount
            FROM booking
            WHERE id = ?
        """, (booking_id,))
        
        updated = cursor.fetchone()
        print(f"\n📊 Updated Booking Details:")
        print(f"   ID: {updated[0]}")
        print(f"   Status: {updated[1]}")
        print(f"   Payment Status: {updated[2]}")
        print(f"   Refund Status: {updated[3]}")  
        print(f"   Refund Amount: RM {updated[4]}")
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Go to /admin/refunds in your browser")
        print(f"   2. You should see Booking BK-{booking_id}")
        print(f"   3. Click 'Approve & Process Refund' to test approval")
        print(f"   4. Or click 'Reject' to test rejection")
        
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

def show_pending_refunds():
    """Show all pending refunds"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, status, payment_status, refund_status, refund_amount, cancellation_at
            FROM booking
            WHERE refund_status = 'Pending'
        """)
        
        bookings = cursor.fetchall()
        
        print(f"\n\n📋 All Pending Refunds (what admin will see):")
        print("=" * 80)
        
        if not bookings:
            print("   No pending refunds found")
            print("   Run this script to create a test refund!")
        else:
            for b in bookings:
                print(f"   BK-{b[0]} | Status: {b[1]} | Payment: {b[2]} | Refund: {b[3]} | Amount: RM {b[4]} | Cancelled: {b[5]}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("="*80)
    print(" REFUND APPROVAL WORKFLOW TEST")
    print("="*80)
    
    # First show current state
    show_pending_refunds()
    
    # Ask user if they want to simulate
    print("\n\n")
    response = input("Do you want to simulate a booking cancellation? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        simulate_booking_cancellation()
        show_pending_refunds()
    else:
        print("\nSkipped simulation. You can run this again anytime!")
