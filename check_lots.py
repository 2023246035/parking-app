import os
import sys

# Add the project root to sys.path
sys.path.append(r"m:\Repository_code\ParkingApp\parking-app")

from sqlmodel import Session, create_engine, select
from app.db.models import ParkingLot, ParkingSlot, Booking

# Get DATABASE_URL from .env if needed
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./parking.db")
print(f"Connecting to: {DATABASE_URL}")
engine = create_engine(DATABASE_URL)

def check_data():
    with Session(engine) as session:
        try:
            print("--- Checking Parking Lots ---")
            lots = session.exec(select(ParkingLot)).all()
            print(f"Found {len(lots)} parking lots.")
            for lot in lots:
                print(f"Lot ID: {lot.id}, Name: {lot.name}, Available Spots: {lot.available_spots}")
            
            print("\n--- Checking Parking Slots (First 10) ---")
            slots = session.exec(select(ParkingSlot)).all()
            print(f"Found {len(slots)} parking slots total.")
            for slot in slots[:10]:
                print(f"Slot ID: {slot.id}, Lot ID: {slot.lot_id}, Number: {slot.slot_number}, Occupied: {slot.is_occupied}")
            
            print("\n--- Checking Active Bookings ---")
            bookings = session.exec(select(Booking).where(Booking.status == "Confirmed")).all()
            print(f"Found {len(bookings)} active bookings.")
            
        except Exception as e:
            print(f"\n❌ Error encountered: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_data()
