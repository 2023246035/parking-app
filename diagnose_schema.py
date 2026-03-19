import os
import sys
from sqlmodel import Session, create_engine, select, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def diagnose():
    with Session(engine) as session:
        print("--- Table Existence ---")
        tables_query = text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        tables = session.exec(tables_query).all()
        table_list = [t[0] for t in tables]
        print(f"Tables: {', '.join(table_list)}")
        
        has_slot_table = "parkingslot" in table_list
        print(f"parkingslot table exists: {has_slot_table}")
        
        print("\n--- Booking Columns ---")
        cols_query = text("SELECT column_name FROM information_schema.columns WHERE table_name='booking'")
        cols = session.exec(cols_query).all()
        col_list = [c[0] for c in cols]
        print(f"Booking Columns: {', '.join(col_list)}")
        
        has_slot_db_id = "slot_db_id" in col_list
        print(f"booking.slot_db_id exists: {has_slot_db_id}")

        print("\n--- Model Check ---")
        try:
            from app.db.models import ParkingLot
            lot_stmt = select(ParkingLot)
            lots = session.exec(lot_stmt).first()
            print("Successfully queried ParkingLot model.")
        except Exception as e:
            print(f"Error querying ParkingLot: {e}")

if __name__ == "__main__":
    diagnose()
