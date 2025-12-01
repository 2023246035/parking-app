"""Manually initialize the database"""
import sys
sys.path.insert(0, '.')

import reflex as rx
from app.db.init_db import init_db

print("Initializing database...")
try:
    init_db()
    print("✅ Database initialized successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
