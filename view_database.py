"""Script to view the database contents"""
import reflex as rx
from sqlmodel import select
from app.db.models import User, ParkingLot, Booking, Payment, AuditLog
from datetime import datetime

def view_database():
    """View all tables in the database"""
    
    with rx.session() as session:
        print("\n" + "="*80)
        print("DATABASE CONTENTS - PARKING APP")
        print("="*80)
        
        # View Users
        print("\n📊 USERS TABLE")
        print("-" * 80)
        users = session.exec(select(User)).all()
        if users:
            for user in users:
                print(f"ID: {user.id} | Name: {user.name} | Email: {user.email}")
                print(f"   Phone: {user.phone} | Member Since: {user.member_since}")
                print(f"   Total Bookings: {len(user.bookings)}")
                print("-" * 80)
        else:
            print("No users found.")
        
        # View Parking Lots
        print("\n🅿️  PARKING LOTS TABLE")
        print("-" * 80)
        lots = session.exec(select(ParkingLot)).all()
        if lots:
            for lot in lots:
                print(f"ID: {lot.id} | Name: {lot.name}")
                print(f"   Location: {lot.location}")
                print(f"   Price: RM {lot.price_per_hour}/hr | Rating: {lot.rating}⭐")
                print(f"   Spots: {lot.available_spots}/{lot.total_spots} available")
                print(f"   Features: {lot.features}")
                print("-" * 80)
        else:
            print("No parking lots found.")
        
        # View Bookings
        print("\n📅 BOOKINGS TABLE")
        print("-" * 80)
        bookings = session.exec(select(Booking)).all()
        if bookings:
            for booking in bookings:
                user = session.get(User, booking.user_id)
                lot = session.get(ParkingLot, booking.lot_id)
                print(f"Booking ID: {booking.id}")
                print(f"   User: {user.name if user else 'N/A'}")
                print(f"   Parking Lot: {lot.name if lot else 'N/A'}")
                print(f"   Date: {booking.start_date} at {booking.start_time}")
                print(f"   Duration: {booking.duration_hours} hours | Total: RM {booking.total_price}")
                print(f"   Status: {booking.status} | Payment: {booking.payment_status}")
                if booking.transaction_id:
                    print(f"   Transaction ID: {booking.transaction_id}")
                if booking.cancellation_reason:
                    print(f"   Cancelled: {booking.cancellation_reason}")
                    print(f"   Refund: RM {booking.refund_amount}")
                print("-" * 80)
        else:
            print("No bookings found.")
        
        # View Payments
        print("\n💳 PAYMENTS TABLE")
        print("-" * 80)
        payments = session.exec(select(Payment)).all()
        if payments:
            for payment in payments:
                print(f"Payment ID: {payment.id} | Transaction: {payment.transaction_id}")
                print(f"   Amount: RM {payment.amount} | Status: {payment.status}")
                print(f"   Method: {payment.method} | Time: {payment.timestamp}")
                print(f"   Booking ID: {payment.booking_id}")
                print("-" * 80)
        else:
            print("No payments found.")
        
        # View Audit Logs
        print("\n📝 AUDIT LOGS TABLE")
        print("-" * 80)
        logs = session.exec(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10)).all()
        if logs:
            print("Showing last 10 entries:")
            for log in logs:
                user = session.get(User, log.user_id) if log.user_id else None
                print(f"[{log.timestamp}] {log.action}")
                print(f"   User: {user.name if user else 'System'} | Details: {log.details}")
                print("-" * 80)
        else:
            print("No audit logs found.")
        
        # Summary
        print("\n📈 DATABASE SUMMARY")
        print("-" * 80)
        print(f"Total Users: {len(users)}")
        print(f"Total Parking Lots: {len(lots)}")
        print(f"Total Bookings: {len(bookings)}")
        print(f"Total Payments: {len(payments)}")
        print(f"Total Audit Logs: {session.exec(select(AuditLog)).all().__len__()}")
        print("="*80)
        print()

if __name__ == "__main__":
    view_database()
