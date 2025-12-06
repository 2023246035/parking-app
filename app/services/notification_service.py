import logging
from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, create_engine, select
from datetime import datetime, timedelta
from app.db.models import Booking, User, ParkingLot
from app.services.email_service import send_booking_reminder_email
import os

# Scheduler instance
scheduler = BackgroundScheduler()

def check_upcoming_bookings():
    """Check for bookings starting in the next ~1 hour and send reminders."""
    # Use generic generic URL or env var if available
    DATABASE_URL = "sqlite:///reflex.db"
    
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

def start_scheduler():
    """Start the background scheduler."""
    if not scheduler.running:
        scheduler.add_job(check_upcoming_bookings, 'interval', minutes=5)
        try:
            scheduler.start()
            logging.info("📅 Notification Scheduler started.")
        except Exception as e:
            logging.error(f"Failed to start scheduler: {e}")
