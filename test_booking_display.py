"""Test script to verify booking loading logic"""
import sqlite3

print("\n" + "="*80)
print("BOOKING DISPLAY TEST - User: rvijay1702@gmail.com")
print("="*80)

conn = sqlite3.connect('reflex.db')
cursor = conn.cursor()

# Get user ID
cursor.execute("SELECT id, name FROM user WHERE email = 'rvijay1702@gmail.com'")
user = cursor.fetchone()

if user:
    user_id = user[0]
    user_name = user[1]
    print(f"\n✓ User Found: {user_name} (ID: {user_id})")
    
    # Get bookings for this user
    cursor.execute("""
        SELECT b.id, b.start_date, b.start_time, b.duration_hours, 
               b.total_price, b.status, b.payment_status,
               p.name, p.location
        FROM booking b
        JOIN parkinglot p ON b.lot_id = p.id
        WHERE b.user_id = ?
        ORDER BY b.created_at DESC
    """, (user_id,))
    
    bookings = cursor.fetchall()
    
    print(f"\n📅 BOOKINGS FOR THIS USER: {len(bookings)} found")
    print("-" * 80)
    
    if bookings:
        for booking in bookings:
            print(f"\nBooking ID: BK-{booking[0]}")
            print(f"  Parking Lot: {booking[7]} ({booking[8]})")
            print(f"  Date & Time: {booking[1]} at {booking[2]}")
            print(f"  Duration: {booking[3]} hours")
            print(f"  Total Price: RM {booking[4]}")
            print(f"  Status: {booking[5]} | Payment: {booking[6]}")
            
            # Determine which tab this should appear in
            if booking[5] == "Confirmed":
                print(f"  📍 Should appear in: ACTIVE tab")
            elif booking[5] == "Completed":
                print(f"  📍 Should appear in: PAST tab")
            elif booking[5] == "Cancelled":
                print(f"  📍 Should appear in: CANCELLED tab")
    else:
        print("  ⚠️  No bookings found for this user!")
        print("  This explains why the bookings page is empty.")
else:
    print("\n❌ User not found in database!")

print("\n" + "="*80)
print("RECOMMENDATION:")
print("-" * 80)
if user and bookings:
    print("1. Make sure you're logged in as: rvijay1702@gmail.com")
    print("2. The booking should appear in the 'Active' tab")
    print("3. Check browser console for any JavaScript errors")
    print("4. Try refreshing the page or logging out and back in")
else:
    print("1. Log in with: rvijay1702@gmail.com")
    print("2. Go to 'Available Lots' and create a new booking")
    print("3. Then check 'My Bookings' page")
print("="*80 + "\n")

conn.close()
