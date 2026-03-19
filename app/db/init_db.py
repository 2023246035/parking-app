import reflex as rx
from sqlmodel import select, SQLModel, text
from sqlalchemy import inspect
from app.db.models import ParkingLot, User, Booking, Payment, AuditLog, CancellationPolicy, BookingRule, ParkingSlot
from app.db.ai_models import UserPreference, PricingHistory, AutoBookingSetting, ChatbotConversation, RecommendationScore
import logging


def init_db():
    """Initialize the database with seed data if empty."""
    logging.info("Checking database initialization...")
    with rx.session() as session:
        try:
            engine = session.get_bind()
            
            # --- BEGIN SAFE MIGRATION ---
            # SQLModel.metadata.create_all only creates MISSING tables.
            # It DOES NOT add missing columns to existing tables.
            try:
                # 1. Ensure all tables exist (especially new ones like parkingslot)
                SQLModel.metadata.create_all(engine)
                logging.info("Core tables verified.")

                # 2. Check for missing columns in 'booking' table (Database Agnostic)
                inspector = inspect(engine)
                columns = [c['name'] for c in inspector.get_columns('booking')]
                
                if 'slot_db_id' not in columns:
                    logging.info("Adding missing column 'slot_db_id' to 'booking' table...")
                    with engine.connect() as conn:
                        # SQLite doesn't support complex ALTER TABLE but ADD COLUMN is fine
                        # PostgreSQL dialect detection if needed, but simple ALTER works for both
                        conn.execute(text("ALTER TABLE booking ADD COLUMN slot_db_id INTEGER REFERENCES parkingslot(id)"))
                        conn.commit()
                    logging.info("Added 'slot_db_id' to 'booking' table successfully.")
                else:
                    logging.info("'slot_db_id' column already exists in 'booking' table.")
                    
            except Exception as migrate_err:
                logging.warning(f"Migration warning: {migrate_err}")
            # --- END SAFE MIGRATION ---

            logging.info("Database tables verified/created.")
            
            # Initialize default cancellation policy
            existing_policy = session.exec(select(CancellationPolicy)).first()
            if not existing_policy:
                logging.info("Creating default cancellation policy...")
                default_policy = CancellationPolicy(
                    full_refund_hours=24,
                    partial_refund_hours=0,
                    partial_refund_percentage=50,
                    non_cancellable_hours=0,
                    allow_cancellation_after_start=False,
                    is_active=True
                )
                session.add(default_policy)
                session.commit()
                logging.info("Default cancellation policy created.")
            
            existing_lots = session.exec(select(ParkingLot)).first()
            if not existing_lots:
                logging.info("Seeding parking lots...")
                lots = [
                    ParkingLot(
                        name="KLCC Tower Parking",
                        location="Kuala Lumpur City Centre",
                        price_per_hour=5.0,
                        total_spots=150,
                        available_spots=120,
                        image_url="/placeholder.svg",
                        features="Covered,CCTV,24/7",
                        rating=4.8,
                    ),
                    ParkingLot(
                        name="Bukit Bintang Central",
                        location="Bukit Bintang",
                        price_per_hour=4.5,
                        total_spots=200,
                        available_spots=180,
                        image_url="/placeholder.svg",
                        features="Valet,EV Charging",
                        rating=4.5,
                    ),
                    ParkingLot(
                        name="Mid Valley South Key",
                        location="Mid Valley",
                        price_per_hour=3.0,
                        total_spots=500,
                        available_spots=450,
                        image_url="/placeholder.svg",
                        features="Covered,Multiple Entries",
                        rating=4.2,
                    ),
                    ParkingLot(
                        name="Bangsar Village Open Lot",
                        location="Bangsar",
                        price_per_hour=2.0,
                        total_spots=50,
                        available_spots=45,
                        image_url="/placeholder.svg",
                        features="Open Air,Cheap Rates",
                        rating=3.9,
                    ),
                    ParkingLot(
                        name="Sunway Pyramid Zone B",
                        location="Subang Jaya",
                        price_per_hour=3.5,
                        total_spots=300,
                        available_spots=280,
                        image_url="/placeholder.svg",
                        features="Smart Parking,Wide Bays",
                        rating=4.6,
                    ),
                    ParkingLot(
                        name="Pavilion Elite",
                        location="Bukit Bintang",
                        price_per_hour=6.0,
                        total_spots=100,
                        available_spots=95,
                        image_url="/placeholder.svg",
                        features="Premium,Valet,Car Wash",
                        rating=4.9,
                    ),
                ]
                session.add_all(lots)
                session.commit() # Commit lots first so we can link slots
                
                # Seed slots for each lot
                all_lots = session.exec(select(ParkingLot)).all()
                for lot in all_lots:
                    logging.info(f"Seeding slots for {lot.name}...")
                    slots = []
                    # Zone A: A1-A10
                    for i in range(1, 11):
                        slots.append(ParkingSlot(slot_number=f"A{i}", lot_id=lot.id))
                    # Zone B: B1-B10
                    for i in range(1, 11):
                        slots.append(ParkingSlot(slot_number=f"B{i}", lot_id=lot.id))
                    session.add_all(slots)
                
                existing_user = session.exec(
                    select(User).where(User.email == "alex.tan@example.com")
                ).first()
                if not existing_user:
                    demo_user = User(
                        name="Alex Tan",
                        email="alex.tan@example.com",
                        password_hash="password123",
                        phone="+60 12-345 6789",
                        avatar_url="https://api.dicebear.com/9.x/notionists/svg?seed=Alex",
                    )
                    session.add(demo_user)
                session.commit()
                logging.info("Database seeded successfully with Slots, Lots, and Users.")
            else:
                # If lots exist, check if slots need seeding
                existing_slots = session.exec(select(ParkingSlot)).first()
                if not existing_slots:
                    logging.info("Parking lots exist but no slots found. Seeding slots...")
                    all_lots = session.exec(select(ParkingLot)).all()
                    for lot in all_lots:
                        slots = []
                        for i in range(1, 11):
                            slots.append(ParkingSlot(slot_number=f"A{i}", lot_id=lot.id))
                        for i in range(1, 11):
                            slots.append(ParkingSlot(slot_number=f"B{i}", lot_id=lot.id))
                        session.add_all(slots)
                    session.commit()
                    logging.info("Slots seeded for existing lots.")
                logging.info("Database already seeded.")
        except Exception as e:
            logging.exception(f"Error initializing database: {e}")
            raise e