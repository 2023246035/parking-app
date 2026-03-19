import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add the project root to sys.path
sys.path.append(r"m:\Repository_code\ParkingApp\parking-app")

from app.db.init_db import init_db

if __name__ == "__main__":
    print("🚀 Manually triggering init_db...")
    try:
        init_db()
        print("✅ init_db completed successfully!")
    except Exception as e:
        print(f"❌ init_db failed: {e}")
        import traceback
        traceback.print_exc()
