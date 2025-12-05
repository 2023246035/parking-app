import reflex as rx
from sqlmodel import Session, create_engine, select
from app.db.models import Booking, User, ParkingLot
from datetime import datetime, timedelta
import random

def seed_bookings():
    DATABASE_URL = "sqlite:///reflex.db"
    engine = create_engine(DATABASE_URL)
    
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        lots = session.exec(select(ParkingLot)).all()
        
        if not users or not lots:
            print("❌ Need users and parking lots to seed bookings.")
            return

        print(f"Found {len(users)} users and {len(lots)} lots.")
        
        bookings = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Generate 50 random bookings
        for _ in range(50):
            user = random.choice(users)
            lot = random.choice(lots)
            
            # Random time in last 7 days
            days_offset = random.randint(0, 7)
            hour_offset = random.randint(8, 20) # 8 AM to 8 PM
            booking_time = start_date + timedelta(days=days_offset)
            booking_time = booking_time.replace(hour=hour_offset, minute=0, second=0, microsecond=0)
            
            duration = random.randint(1, 4)
            total_price = lot.price_per_hour * duration
            
            status = random.choice(["Confirmed", "Completed", "Cancelled"])
            payment_status = "Paid" if status != "Cancelled" else "Refunded"
            
            booking = Booking(
                user_id=user.id,
                lot_id=lot.id,
                start_date=booking_time.date().isoformat(), # String
                start_time=booking_time.time().strftime("%H:%M"),
                duration_hours=duration,
                total_price=total_price,
                status=status,
                payment_status=payment_status,
                created_at=booking_time, # Datetime
                is_refundable=True,
                vehicle_number="ABC 1234",
                phone_number=user.phone
            )
            bookings.append(booking)
            
        session.add_all(bookings)
        session.commit()
        print(f"✅ seeded {len(bookings)} bookings!")

if __name__ == "__main__":
    seed_bookings()
