from sqlmodel import create_engine, text
from sqlalchemy.orm import Session

def add_column():
    DATABASE_URL = "sqlite:///reflex.db"
    engine = create_engine(DATABASE_URL)
    
    with Session(engine) as session:
        try:
            session.execute(text("ALTER TABLE booking ADD COLUMN reminder_sent BOOLEAN DEFAULT 0"))
            session.commit()
            print("✅ Added 'reminder_sent' column to 'booking' table.")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("⚠️ Column 'reminder_sent' already exists.")
            else:
                print(f"❌ Error adding column: {e}")

if __name__ == "__main__":
    add_column()
