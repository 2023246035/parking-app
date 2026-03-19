import os
import sys
import reflex as rx
from sqlmodel import select

# Add the project root to sys.path
sys.path.append(r"m:\Repository_code\ParkingApp\parking-app")

from app.db.models import ParkingLot, ParkingSlot

def verify_data():
    print("🔍 Verifying data using rx.session()...")
    with rx.session() as session:
        try:
            # Check lots
            lots = session.exec(select(ParkingLot)).all()
            print(f"✅ Found {len(lots)} parking lots.")
            
            # Check slots
            slots = session.exec(select(ParkingSlot)).all()
            print(f"✅ Found {len(slots)} parking slots.")
            
            # Check columns in Booking (indirectly via a query)
            from app.db.models import Booking
            booking = session.exec(select(Booking)).first()
            if booking:
                print(f"✅ Found a booking. slot_db_id: {getattr(booking, 'slot_db_id', 'N/A')}")
            else:
                print("ℹ️ No bookings found, but query succeeded.")
                
            print("🚀 ALL SYSTEMS NOMINAL!")
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    verify_data()
