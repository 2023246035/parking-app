import os
import sys
from sqlmodel import Session, create_engine, select
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def check_logs():
    from app.db.models import AuditLog
    with Session(engine) as session:
        try:
            logs = session.exec(select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(10)).all()
            print("--- Recent Audit Logs ---")
            for l in logs:
                print(f"{l.timestamp}: {l.action} - {l.details}")
        except Exception as e:
            print(f"Error checking logs: {e}")

if __name__ == "__main__":
    check_logs()
