import logging
from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, create_engine, select
from datetime import datetime, timedelta
from app.db.models import Booking, User, ParkingLot, BookingRule
from app.services.email_service import send_booking_reminder_email
import os

# Scheduler instance
scheduler = BackgroundScheduler()

def get_database_url():
    """Get database URL from environment or use default SQLite"""
    return os.getenv("DATABASE_URL", "sqlite:///reflex.db")

def check_upcoming_bookings():
    """Check for bookings starting in the next ~1 hour and send reminders."""
    DATABASE_URL = get_database_url()
    
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with Session(engine) as session:
            now = datetime.now()
            
            # We look for bookings starting today or tomorrow (to catch midnight crossovers)
            today_str = now.strftime("%Y-%m-%d")
            tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
            
            bookings = session.exec(select(Booking).where(
                (Booking.start_date.in_([today_str, tomorrow_str])),
                Booking.status == "Confirmed",
                Booking.reminder_sent == False
            )).all()
            
            count = 0
            for booking in bookings:
                try:
                    # Construct start datetime
                    start_dt_str = f"{booking.start_date} {booking.start_time}"
                    start_dt = datetime.strptime(start_dt_str, "%Y-%m-%d %H:%M")
                    
                    # Check if start time is between 50 and 70 minutes from now
                    # This allows the 5-minute interval job to catch it reliably
                    time_diff = start_dt - now
                    minutes_diff = time_diff.total_seconds() / 60
                    
                    # Debug log
                    # logging.info(f"Checking booking {booking.id}: starts in {minutes_diff:.1f} mins")
                    
                    if 50 <= minutes_diff <= 70:
                        # Send reminder
                        user = session.get(User, booking.user_id)
                        lot = session.get(ParkingLot, booking.lot_id)
                        
                        if user and lot:
                            # Calculate end time
                            end_dt = start_dt + timedelta(hours=booking.duration_hours)
                            end_time_str = end_dt.strftime("%H:%M")
                            
                            booking_details = {
                                "user_name": user.name,
                                "lot_name": lot.name,
                                "start_time": booking.start_time,
                                "end_time": end_time_str,
                                "vehicle_number": booking.vehicle_number or "N/A",
                                "slot_id": booking.slot_id or "Unassigned"
                            }
                            
                            logging.info(f"Sending reminder for booking {booking.id} to {user.email}")
                            
                            if send_booking_reminder_email(user.email, booking_details):
                                booking.reminder_sent = True
                                session.add(booking)
                                count += 1
                
                except ValueError:
                    # Handle invalid date/time formats
                    continue
                except Exception as e:
                    logging.error(f"Error processing booking {booking.id} for reminder: {e}")
                    continue
                    
            if count > 0:
                session.commit()
                logging.info(f"🔔 Sent {count} booking reminders.")
                
    except Exception as e:
        logging.error(f"Scheduler error: {e}")


def process_auto_booking_rules():
    """Automatically process booking rules and create bookings for tomorrow."""
    DATABASE_URL = get_database_url()
    logging.info("🤖 Auto-booking scheduler running...")
    
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with Session(engine) as session:
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow_day_name = tomorrow.strftime("%a")  # Mon, Tue, etc.
            tomorrow_date_str = tomorrow.strftime("%Y-%m-%d")
            
            # Get all active rules
            rules = session.exec(
                select(BookingRule).where(BookingRule.status == "Active")
            ).all()
            
            bookings_created = 0
            
            for rule in rules:
                try:
                    # Check if rule applies to tomorrow
                    rule_days = rule.days.split(",")
                    if tomorrow_day_name not in rule_days:
                        continue
                    
                    # Parse location string "Name - Location"
                    try:
                        lot_name, lot_loc = rule.location.split(" - ", 1)
                        lot = session.exec(
                            select(ParkingLot)
                            .where(ParkingLot.name == lot_name)
                            .where(ParkingLot.location == lot_loc)
                        ).first()
                    except ValueError:
                        logging.warning(f"Invalid location format for rule {rule.id}: {rule.location}")
                        continue
                    
                    if not lot:
                        logging.warning(f"Parking lot not found for rule {rule.id}: {rule.location}")
                        continue
                    
                    # Check if booking already exists
                    existing_booking = session.exec(
                        select(Booking)
                        .where(Booking.user_id == rule.user_id)
                        .where(Booking.lot_id == lot.id)
                        .where(Booking.start_date == tomorrow_date_str)
                        .where(Booking.start_time == rule.time)
                        .where(Booking.status != "Cancelled")
                    ).first()
                    
                    if existing_booking:
                        continue  # Skip if booking already exists
                    
                    final_slot_id = rule.slot_id or "A1"
                    
                    # Check for slot conflict
                    conflict_query = select(Booking).where(
                        Booking.lot_id == lot.id,
                        Booking.start_date == tomorrow_date_str,
                        Booking.start_time == rule.time,
                        Booking.slot_id == final_slot_id,
                        Booking.status != "Cancelled"
                    )
                    slot_conflict = session.exec(conflict_query).first()
                    
                    if slot_conflict:
                        # Smart Slot Substitution
                        logging.info(f"Slot {final_slot_id} occupied for rule {rule.id}. Finding alternative...")
                        
                        # Get all occupied slots for this time block
                        occupied_query = select(Booking.slot_id).where(
                            Booking.lot_id == lot.id,
                            Booking.start_date == tomorrow_date_str,
                            Booking.start_time == rule.time,
                            Booking.status != "Cancelled"
                        )
                        occupied_slots = [s for s in session.exec(occupied_query).all()]
                        
                        # Standard slots
                        standard_slots = ["A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3", "B4", "B5"]
                        
                        alternative_found = False
                        for s in standard_slots:
                            if s not in occupied_slots:
                                final_slot_id = s
                                alternative_found = True
                                logging.info(f"Found alternative slot {s} for rule {rule.id}")
                                break
                        
                        if not alternative_found:
                            logging.warning(f"Skipped rule {rule.id} for {rule.location}: All slots full")
                            continue
                    
                    # Create Booking
                    duration = int(rule.duration.split(" ")[0])
                    total_price = lot.price_per_hour * duration
                    
                    new_booking = Booking(
                        lot_id=lot.id,
                        user_id=rule.user_id,
                        start_date=tomorrow_date_str,
                        start_time=rule.time,
                        duration_hours=duration,
                        total_price=total_price,
                        status="Confirmed",
                        payment_status="Paid (Auto)",
                        created_at=datetime.now(),
                        slot_id=final_slot_id,
                        vehicle_number=rule.vehicle_number or "",
                        phone_number=rule.phone_number or "",
                        reminder_sent=False
                    )
                    
                    session.add(new_booking)
                    bookings_created += 1
                    logging.info(f"✅ Auto-created booking for rule {rule.id}: {lot.name} on {tomorrow_date_str} at {rule.time}")
                    
                except Exception as e:
                    logging.error(f"Error processing rule {rule.id}: {e}")
                    continue
            
            if bookings_created > 0:
                session.commit()
                logging.info(f"🤖 Auto-booking: Created {bookings_created} bookings for tomorrow")
            else:
                logging.info("🤖 Auto-booking: No new bookings needed")
                
    except Exception as e:
        logging.error(f"Auto-booking scheduler error: {e}")


def start_scheduler():
    """Start the background scheduler."""
    if not scheduler.running:
        # Email reminders every 5 minutes
        scheduler.add_job(check_upcoming_bookings, 'interval', minutes=5)
        
        # Auto-booking processing every 10 minutes (more responsive than hourly)
        # This will check for rules and create bookings throughout the day
        scheduler.add_job(process_auto_booking_rules, 'interval', minutes=10)
        
        try:
            scheduler.start()
            logging.info("📅 Notification Scheduler started (every 5 minutes).")
            logging.info("🤖 Auto-booking Scheduler started (every 10 minutes).")
        except Exception as e:
            logging.error(f"Failed to start scheduler: {e}")
