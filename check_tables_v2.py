import os
import sys
import reflex as rx
from sqlmodel import text

# Add the project root to sys.path
sys.path.append(r"m:\Repository_code\ParkingApp\parking-app")

def check_tables():
    print("🔍 Checking tables using rx.session()...")
    with rx.session() as session:
        try:
            engine = session.get_bind()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
                tables = [r[0] for r in result.all()]
                print(f"✅ Tables found: {', '.join(tables)}")
                
                required_tables = ['parkinglot', 'parkingslot', 'booking', 'user', 'pricinghistory', 'userpreference']
                missing = [t for t in required_tables if t not in tables]
                
                if missing:
                    print(f"❌ Missing tables: {', '.join(missing)}")
                else:
                    print("🚀 ALL REQUIRED TABLES EXIST!")
                    
        except Exception as e:
            print(f"❌ Table check failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_tables()
