"""Quick database check for bookings"""
import sqlite3

# Connect to the database
conn = sqlite3.connect('reflex.db')
cursor = conn.cursor()

print("\n" + "="*80)
print("QUICK DATABASE CHECK")
print("="*80)

# Check Users
print("\n📊 USERS:")
cursor.execute("SELECT id, email, name FROM user")
users = cursor.fetchall()
for user in users:
    print(f"  ID: {user[0]} | Email: {user[1]} | Name: {user[2]}")

# Check Parking Lots
print("\n🅿️  PARKING LOTS:")
cursor.execute("SELECT id, name, location, available_spots, total_spots FROM parkinglot")
lots = cursor.fetchall()
for lot in lots:
    print(f"  ID: {lot[0]} | {lot[1]} ({lot[2]}) - {lot[3]}/{lot[4]} spots")

# Check Bookings
print("\n📅 BOOKINGS:")
cursor.execute("SELECT id, user_id, lot_id, status, start_date, total_price FROM booking")
bookings = cursor.fetchall()
if bookings:
    for booking in bookings:
        print(f"  Booking ID: {booking[0]} | User: {booking[1]} | Lot: {booking[2]} | Status: {booking[3]} | Date: {booking[4]} | Price: RM{booking[5]}")
else:
    print("  No bookings found in database!")

print("\n" + "="*80)
print(f"Total Users: {len(users)}")
print(f"Total Parking Lots: {len(lots)}")
print(f"Total Bookings: {len(bookings)}")
print("="*80 + "\n")

conn.close()
