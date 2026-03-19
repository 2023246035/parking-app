import reflex as rx
from sqlmodel import select
from app.db.models import ParkingSlot, ParkingLot
import sys

def check_counts():
    print("🔍 Checking counts in database...")
    try:
        with rx.session() as session:
            lots = session.exec(select(ParkingLot)).all()
            slots = session.exec(select(ParkingSlot)).all()
            print(f"✅ Found {len(lots)} parking lots.")
            print(f"✅ Found {len(slots)} parking slots.")
            
            if len(lots) > 0 and len(slots) == 0:
                print("❌ Slots are missing! Seeding might have failed or not reached.")
            elif len(slots) > 0:
                print(f"🚀 Data is present: {len(slots)/len(lots) if len(lots) > 0 else 0} slots per lot on average.")
    except Exception as e:
        print(f"❌ Error checking counts: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_counts()
