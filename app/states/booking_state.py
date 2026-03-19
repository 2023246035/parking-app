import reflex as rx
from datetime import datetime, timedelta
from typing import Optional
import random
import logging
import asyncio
import uuid
import qrcode
import io
import base64
from sqlmodel import select
from app.states.schema import Booking, ParkingLot, Payment, AuditLog
from app.db.models import (
    Booking as DBBooking,
    ParkingLot as DBParkingLot,
    Payment as DBPayment,
    AuditLog as DBAuditLog,
    User as DBUser,
    ParkingSlot as DBParkingSlot,
)
from app.states.user_state import UserState



class BookingState(rx.State):
    session_email: str = rx.Cookie("", name="session_email")
    bookings: list[Booking] = []
    payments: list[Payment] = []
    audit_logs: list[AuditLog] = []
    is_modal_open: bool = False
    is_payment_modal_open: bool = False
    is_cancellation_modal_open: bool = False
    selected_lot: Optional[ParkingLot] = None
    booking_to_cancel: Optional[Booking] = None
    start_date: str = datetime.now().strftime("%Y-%m-%d")
    start_time: str = (datetime.now() + timedelta(hours=1)).strftime("%H:00")
    duration_hours: int = 2
    is_processing_payment: bool = False
    payment_error: str = ""
    refund_amount_display: float = 0.0
    refund_percentage: int = 0
    cancellation_message: str = ""
    user_cancellation_reason: str = ""  # User's reason for cancelling
    # Reschedule variables
    is_reschedule_modal_open: bool = False
    booking_to_reschedule: Optional[Booking] = None
    new_start_date: str = ""
    new_start_time: str = ""
    # New slot booking variables
    booking_step: int = 1
    selected_slots: list[str] = []  # Changed from single slot to multiple
    vehicle_details: dict[str, dict[str, str]] = {}  # {slot_id: {vehicle_number: str, driver_name: str}}
    phone_number: str = ""  # Single phone for all bookings
    is_loading_slots: bool = False
    occupied_slots: list[str] = []
    qr_codes: dict[str, str] = {}  # Store QR codes by booking ID
    is_generating_qr: bool = False  # Loading state for QR generation
    expanded_refund_details: dict[str, bool] = {}  # Track which booking's refund details are expanded
    expanded_qr_codes: dict[str, bool] = {}  # Track which QR codes are expanded
    is_refreshing: bool = False
    
    @rx.var
    def reschedulable_booking_ids(self) -> list[str]:
        """Return list of booking IDs that can be rescheduled (>24 hours away)"""
        from datetime import datetime
        import logging
        
        reschedulable_ids = []
        
        for booking in self.active_bookings:
            try:
                # Parse booking start time
                booking_start = datetime.strptime(
                    f"{booking.start_date} {booking.start_time}",
                    "%Y-%m-%d %H:%M"
                )
                
                # Calculate hours until booking
                time_until = booking_start - datetime.now()
                hours_until = time_until.total_seconds() / 3600
                
                # Must be MORE than 24 hours
                if hours_until > 24.0:
                    reschedulable_ids.append(booking.id)
                    logging.info(f"✅ Booking {booking.id} ({booking.start_date} {booking.start_time}) is reschedulable: {hours_until:.2f} hours")
                else:
                    logging.info(f"❌ Booking {booking.id} ({booking.start_date} {booking.start_time}) NOT reschedulable: {hours_until:.2f} hours")
                    
            except Exception as e:
                logging.error(f"Error checking booking {booking.id}: {e}")
                continue
        
        return reschedulable_ids

    @rx.var
    def cancellable_booking_ids(self) -> list[str]:
        """Return list of booking IDs that can be cancelled (before start time)"""
        from datetime import datetime
        import logging
        
        cancellable_ids = []
        
        for booking in self.active_bookings:
            try:
                # Parse booking start time
                booking_start = datetime.strptime(
                    f"{booking.start_date} {booking.start_time}",
                    "%Y-%m-%d %H:%M"
                )
                
                # Check if booking hasn't started yet
                if datetime.now() < booking_start:
                    cancellable_ids.append(booking.id)
                    logging.info(f"✅ Booking {booking.id} can be cancelled (starts at {booking.start_date} {booking.start_time})")
                else:
                    logging.info(f"❌ Booking {booking.id} cannot be cancelled (already started)")
                    
            except Exception as e:
                logging.error(f"Error checking booking {booking.id}: {e}")
                continue
        
        return cancellable_ids
    
    # Payment form fields
    card_number: str = ""
    card_expiry: str = ""
    card_cvc: str = ""
    card_name: str = ""
    
    # Validation error messages
    error_slot: str = ""
    error_date: str = ""
    error_time: str = ""
    error_duration: str = ""
    error_vehicle: str = ""
    error_phone: str = ""
    error_payment_card: str = ""
    error_payment_expiry: str = ""
    error_payment_cvc: str = ""
    error_payment_name: str = ""
    
    # Validation methods
    def validate_date(self) -> bool:
        """Validate start date"""
        self.error_date = ""
        
        if not self.start_date or self.start_date.strip() == "":
            self.error_date = "Date is required"
            return False
        
        try:
            from datetime import datetime
            selected_date = datetime.strptime(self.start_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            
            if selected_date < today:
                self.error_date = "Cannot book a past date"
                return False
            
            # Check if date is too far in the future (e.g., max 30 days)
            max_days_ahead = (selected_date - today).days
            if max_days_ahead > 90:
                self.error_date = "Cannot book more than 90 days in advance"
                return False
                
        except ValueError:
            self.error_date = "Invalid date format. Use YYYY-MM-DD"
            return False
        
        return True
    
    def validate_time(self) -> bool:
        """Validate start time"""
        self.error_time = ""
        
        if not self.start_time or self.start_time.strip() == "":
            self.error_time = "Time is required"
            return False
        
        try:
            from datetime import datetime
            selected_date = datetime.strptime(self.start_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            
            # If booking is for today, check time is in future
            if selected_date == today:
                selected_time = datetime.strptime(self.start_time, "%H:%M").time()
                current_time = datetime.now().time()
                
                if selected_time <= current_time:
                    self.error_time = "Please select a future time for today"
                    return False
        except ValueError:
            self.error_time = "Invalid time format. Use HH:MM"
            return False
        
        return True
    
    def validate_duration(self) -> bool:
        """Validate booking duration"""
        self.error_duration = ""
        
        if self.duration_hours <= 0:
            self.error_duration = "Duration must be at least 1 hour"
            return False
        
        if self.duration_hours > 24:
            self.error_duration = "Duration cannot exceed 24 hours"
            return False
        
        return True
    
    def validate_slots(self) -> bool:
        """Validate parking slots selection"""
        self.error_slot = ""
        
        if not self.selected_slots or len(self.selected_slots) == 0:
            self.error_slot = "Please select at least one parking slot"
            return False
        
        # Check if any selected slot is occupied
        for slot in self.selected_slots:
            if slot in self.occupied_slots:
                self.error_slot = f"Slot {slot} is already occupied. Please deselect it."
                return False
        
        return True
    
    def validate_vehicle_number(self) -> bool:
        """Validate vehicle registration number"""
        self.error_vehicle = ""
        
        if not self.vehicle_number or self.vehicle_number.strip() == "":
            self.error_vehicle = "Vehicle number is required"
            return False
        
        # Remove spaces for validation
        clean_vehicle = self.vehicle_number.replace(" ", "").replace("-", "")
        
        if len(clean_vehicle) < 3:
            self.error_vehicle = "Vehicle number must be at least 3 characters"
            return False
        
        if len(clean_vehicle) > 15:
            self.error_vehicle = "Vehicle number cannot exceed 15 characters"
            return False
        
        # Check if contains at least one alphanumeric character
        if not any(c.isalnum() for c in clean_vehicle):
            self.error_vehicle = "Vehicle number must contain alphanumeric characters"
            return False
        
        return True
    
    def validate_phone_number(self) -> bool:
        """Validate contact phone number"""
        self.error_phone = ""
        
        if not self.phone_number or self.phone_number.strip() == "":
            self.error_phone = "Phone number is required"
            return False
        
        # Remove common separators
        clean_phone = self.phone_number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "")
        
        # Check if only digits
        if not clean_phone.isdigit():
            self.error_phone = "Phone number must contain only digits"
            return False
        
        # Check exact length of 10 digits
        if len(clean_phone) != 10:
            self.error_phone = "Phone number must be exactly 10 digits"
            return False
        
        return True
    
    def validate_all_booking_fields(self) -> bool:
        """Validate all booking fields together"""
        is_valid = True
        
        # Validate each field
        if not self.validate_date():
            is_valid = False
        
        if not self.validate_time():
            is_valid = False
        
        if not self.validate_duration():
            is_valid = False
        
        if not self.validate_slots():
            is_valid = False
        
        # Validate that all selected slots have vehicle numbers
        for slot_id in self.selected_slots:
            vehicle_number = self.vehicle_details.get(slot_id, {}).get("vehicle_number", "").strip()
            if not vehicle_number or len(vehicle_number) < 3:
                is_valid = False
                break
        
        if not self.validate_phone_number():
            is_valid = False
        
        return is_valid

    @rx.var
    def estimated_price(self) -> float:
        if not self.selected_lot:
            return 0.0
        return self.selected_lot.price_per_hour * self.duration_hours

    @rx.var
    def active_bookings(self) -> list[Booking]:
        now = datetime.now()
        active = []
        for b in self.bookings:
            if b.status == "Confirmed":
                try:
                    # Calculate end time
                    start = datetime.strptime(f"{b.start_date} {b.start_time}", "%Y-%m-%d %H:%M")
                    end = start + timedelta(hours=b.duration_hours)
                    # Only include if end time is in the future
                    if end > now:
                        active.append(b)
                except Exception as e:
                    logging.error(f"Error parsing booking date for active check: {e}")
                    # If error, keep in active to be safe
                    active.append(b)
        return active

    @rx.var
    def past_bookings(self) -> list[Booking]:
        now = datetime.now()
        past = []
        for b in self.bookings:
            if b.status == "Completed":
                past.append(b)
            elif b.status == "Confirmed":
                try:
                    # Check if expired
                    start = datetime.strptime(f"{b.start_date} {b.start_time}", "%Y-%m-%d %H:%M")
                    end = start + timedelta(hours=b.duration_hours)
                    if end <= now:
                        past.append(b)
                except Exception:
                    pass
        return past

    @rx.var
    def cancelled_bookings(self) -> list[Booking]:
        return [b for b in self.bookings if b.status == "Cancelled"]

    @rx.var
    def total_spent(self) -> float:
        return sum(
            [
                b.total_price
                for b in self.bookings
                if b.status in ["Completed", "Confirmed"]
            ]
        )

    @rx.var
    def zone_a_slots(self) -> list[str]:
        """Generate Zone A slots (A1-A10)"""
        return [f"A{i}" for i in range(1, 11)]

    @rx.var
    def zone_b_slots(self) -> list[str]:
        """Generate Zone B slots (B1-B10)"""
        return [f"B{i}" for i in range(1, 11)]

    @rx.var
    def total_slots_selected(self) -> int:
        """Return number of slots selected"""
        return len(self.selected_slots)
    
    @rx.var
    def total_price_all_slots(self) -> float:
        """Calculate total price for all selected slots"""
        if not self.selected_lot or self.total_slots_selected == 0:
            return 0.0
        return self.selected_lot.price_per_hour * self.duration_hours * self.total_slots_selected
    
    @rx.var
    def estimated_price(self) -> float:
        """Alias for total_price_all_slots for compatibility"""
        return self.total_price_all_slots

    @rx.var
    def can_proceed_to_next_step(self) -> bool:
        """Check if user can proceed to next step with proper validation"""
        if self.booking_step == 1:
            # Step 1: Must have date, time, and valid duration
            return (
                self.start_date != "" and 
                self.start_time != "" and 
                self.duration_hours > 0 and
                self.error_date == "" and
                self.error_time == "" and
                self.error_duration == ""
            )
        elif self.booking_step == 2:
            # Step 2: Must have selected at least one slot
            return len(self.selected_slots) > 0 and self.error_slot == ""
        elif self.booking_step == 3:
            # Step 3: Must have vehicle details for each slot and phone
            # Check if all selected slots have vehicle numbers
            all_slots_have_vehicle = all(
                self.vehicle_details.get(slot, {}).get("vehicle_number", "").strip() != ""
                for slot in self.selected_slots
            )
            return (
                all_slots_have_vehicle and
                self.phone_number.strip() != "" and
                self.error_phone == ""
            )
        elif self.booking_step == 4:
            # Step 4: All validations must pass
            return (
                self.start_date != "" and
                self.start_time != "" and
                len(self.selected_slots) > 0 and
                self.phone_number.strip() != "" and
                self.error_date == "" and
                self.error_time == "" and
                self.error_duration == "" and
                self.error_slot == "" and
                self.error_phone == ""
            )
        return True

    @rx.var
    def zone_a_slots_with_status(self) -> list[dict]:
        """Generate Zone A slots with availability status"""
        return [
            {"slot": f"A{i}", "available": f"A{i}" not in self.occupied_slots}
            for i in range(1, 11)
        ]

    @rx.var
    def zone_b_slots_with_status(self) -> list[dict]:
        """Generate Zone B slots with availability status"""
        return [
            {"slot": f"B{i}", "available": f"B{i}" not in self.occupied_slots}
            for i in range(1, 11)
        ]

    @rx.var
    def available_slots_zone_a(self) -> list[str]:
        """Get available slots in Zone A"""
        return [f"A{i}" for i in range(1, 11) if f"A{i}" not in self.occupied_slots]

    @rx.var
    def available_slots_zone_b(self) -> list[str]:
        """Get available slots in Zone B"""
        return [f"B{i}" for i in range(1, 11) if f"B{i}" not in self.occupied_slots]

    @rx.event
    async def load_bookings(self):
        """Fetch user's bookings from the database."""
        user_email = self.session_email
        logging.info(
            f"BookingState.load_bookings: Checking bookings for user: '{user_email}'"
        )
        if not user_email:
            logging.warning("BookingState: No session email found. Skipping load.")
            return
        try:
            with rx.session() as session:
                user = session.exec(
                    select(DBUser).where(DBUser.email == user_email)
                ).first()
                if not user:
                    logging.warning(
                        f"BookingState: User email '{user_email}' found in state/cookie but NOT in DB."
                    )
                    return
                stmt = (
                    select(DBBooking)
                    .where(DBBooking.user_id == user.id)
                    .order_by(DBBooking.created_at.desc())
                )
                db_bookings = session.exec(stmt).all()
                logging.info(
                    f"BookingState: Found {len(db_bookings)} bookings for user ID {user.id}"
                )
                self.bookings = []
                for b in db_bookings:
                    lot = b.parking_lot
                    booking_obj = Booking(
                        id=f"BK-{b.id}",
                        lot_id=str(b.lot_id),
                        lot_name=lot.name if lot else "Unknown",
                        lot_location=lot.location if lot else "Unknown",
                        lot_image=lot.image_url if lot else "/placeholder.svg",
                        start_date=b.start_date,
                        start_time=b.start_time,
                        duration_hours=b.duration_hours,
                        total_price=b.total_price,
                        status=b.status,
                        created_at=b.created_at.isoformat(),
                        payment_status=b.payment_status,
                        transaction_id=b.transaction_id or "",
                        refund_amount=b.refund_amount,
                        refund_status=b.refund_status or "",
                        refund_approved_at=b.refund_approved_at.isoformat() if b.refund_approved_at else "",
                        cancellation_reason=b.cancellation_reason or "",
                        cancellation_at=b.cancellation_at.strftime("%d-%b-%Y %I:%M:%S %p")
                        if b.cancellation_at
                        else "",
                        slot_id=b.slot_id or "",
                        vehicle_number=b.vehicle_number or "",
                        phone_number=b.phone_number or "",
                    )
                    self.bookings.append(booking_obj)
        except Exception as e:
            logging.exception(f"Error loading bookings: {e}")
            yield rx.toast.error("Failed to load bookings.")

    @rx.event
    def open_modal(self, lot: ParkingLot):
        self.selected_lot = lot
        self.is_modal_open = True
        self.start_date = datetime.now().strftime("%Y-%m-%d")
        self.start_time = (datetime.now() + timedelta(hours=1)).strftime("%H:00")
        self.duration_hours = 2
        self.reset_booking_wizard()
        # Clear all validation errors
        self.error_slot = ""
        self.error_date = ""
        self.error_time = ""
        self.error_vehicle = ""
        self.error_phone = ""
        self.occupied_slots = []
        self.booking_step = 1
        self.selected_slots = []
        return BookingState.start_realtime_sync

    @rx.event
    def close_modal(self):
        self.is_modal_open = False
        self.selected_lot = None
        self.booking_step = 1
        self.selected_slots = []
        return BookingState.stop_realtime_sync

    @rx.event
    def handle_modal_open_change(self, open: bool):
        self.is_modal_open = open
        if not open:
            self.selected_lot = None
            return BookingState.stop_realtime_sync
        else:
            return BookingState.start_realtime_sync

    @rx.event
    def set_start_date(self, date: str):
        self.start_date = date
        # Run validation on change
        self.validate_date()

    @rx.event
    def set_start_time(self, time: str):
        self.start_time = time
        # Run validation on change
        self.validate_time()

    @rx.event
    def set_duration(self, hours: str):
        try:
            self.duration_hours = int(hours)
        except ValueError as e:
            logging.exception(f"Error: {e}")

    @rx.event
    def toggle_slot_selection(self, slot: str):
        """Toggle slot selection - add or remove from selected slots"""
        if slot in self.selected_slots:
            # Deselect: remove from list
            self.selected_slots.remove(slot)
            # Remove vehicle details for this slot
            if slot in self.vehicle_details:
                del self.vehicle_details[slot]
        else:
            # Select: add to list
            self.selected_slots.append(slot)
            # Initialize vehicle details for this slot
            self.vehicle_details[slot] = {
                "vehicle_number": "",
                "driver_name": ""
            }
        
        # Run validation
        self.validate_slots()

    @rx.event
    async def load_occupied_slots(self):
        """Load occupied slots for selected date/time from database"""
        self.is_loading_slots = True
        self.occupied_slots = []
        
        try:
            with rx.session() as session:
                # Query bookings for the selected date/time and parking lot
                from datetime import datetime, timedelta
                
                # Parse the selected datetime
                booking_start = datetime.strptime(f"{self.start_date} {self.start_time}", "%Y-%m-%d %H:%M")
                booking_end = booking_start + timedelta(hours=self.duration_hours)
                
                # Find all bookings that overlap with the selected time period
                # A booking overlaps if:
                # - It starts before our booking ends, AND
                # - It ends after our booking starts
                stmt = select(DBBooking).where(
                    DBBooking.lot_id == int(self.selected_lot.id),
                    DBBooking.status.in_(["Confirmed", "Pending"])
                )
                
                all_bookings = session.exec(stmt).all()
                
                for booking in all_bookings:
                    try:
                        # Parse existing booking datetime
                        existing_start = datetime.strptime(
                            f"{booking.start_date} {booking.start_time}",
                            "%Y-%m-%d %H:%M"
                        )
                        existing_end = existing_start + timedelta(hours=booking.duration_hours)
                        
                        # Check if bookings overlap
                        if existing_start < booking_end and existing_end > booking_start:
                            # Extract slot ID from transaction ID or use a default pattern
                            # Assuming transaction_id might contain slot info like "TXN_123_A5"
                            # For now, we'll use a simple random assignment for demo
                            # In production, you'd store the slot_id in the booking table
                            # In the new system, we query the ParkingSlot table or the linked slot_db_id
                            slot_id = getattr(booking, 'slot_id', None)
                            if slot_id:
                                self.occupied_slots.append(slot_id)
                    except Exception as e:
                        logging.warning(f"Error parsing booking datetime: {e}")
                        continue
                
                # Also include slots currently marked as occupied in the database
                # (This handles the real-time status from the reset task)
                active_slots = session.exec(
                    select(DBParkingSlot).where(
                        DBParkingSlot.lot_id == int(self.selected_lot.id),
                        DBParkingSlot.is_occupied == True
                    )
                ).all()
                for slot in active_slots:
                    if slot.slot_number not in self.occupied_slots:
                        self.occupied_slots.append(slot.slot_number)
                        
        except Exception as e:
            logging.exception(f"Error loading occupied slots: {e}")
            logging.error("Failed to load slot availability")
        finally:
            self.is_loading_slots = False
    
    @rx.event
    async def start_realtime_sync(self):
        """Start periodic background task to sync slot availability"""
        if self.is_refreshing:
            return
        
        self.is_refreshing = True
        logging.info("🔄 Starting real-time sync for booking modal")
        
        # Keep syncing while the modal is open or is_refreshing is True
        while self.is_refreshing and (self.is_modal_open or self.is_payment_modal_open):
            try:
                # 1. Update occupied slots based on specific slot logic
                if self.selected_lot:
                    await self.load_occupied_slots()
                
                # 2. Update parking lots availability stats
                from app.states.parking_state import ParkingState
                parking_state = await self.get_state(ParkingState)
                await parking_state.load_data()
                
                # Yield to update UI
                yield
            except Exception as e:
                logging.error(f"Error in real-time sync loop: {e}")
            
            # Wait 5 seconds before next sync
            await asyncio.sleep(5)
        
        logging.info("🛑 Real-time sync stopped")
        self.is_refreshing = False

    @rx.event
    def stop_realtime_sync(self):
        """Stop the background sync task"""
        self.is_refreshing = False

    @rx.event
    async def proceed_to_slot_selection(self):
        """Validate datetime and duration, then proceed to slot selection"""
        # Use comprehensive validators
        date_valid = self.validate_date()
        time_valid = self.validate_time()
        duration_valid = self.validate_duration()
        
        # Only proceed if all validations pass
        if not (date_valid and time_valid and duration_valid):
            return
        
        # Load occupied slots
        await self.load_occupied_slots()
        
        # Move to step 2
        self.booking_step = 2

    @rx.event
    def go_back_to_datetime(self):
        """Go back to datetime selection"""
        self.booking_step = 1
        self.selected_slots = []
        self.error_slot = ""

    @rx.event
    def go_back_to_step_1(self):
        """Go back to step 1"""
        self.booking_step = 1
        self.selected_slots = []
        self.error_slot = ""

    @rx.event
    def go_back_to_step_2(self):
        """Go back to step 2"""
        self.booking_step = 2

    @rx.event
    def go_back_to_step_3(self):
        """Go back to step 3"""
        self.booking_step = 3

    @rx.event
    def proceed_to_details(self):
        """Step 2 -> Step 3: Validate slots selection"""
        if not self.validate_slots():
            return
        self.booking_step = 3

    @rx.event
    def proceed_to_review(self):
        """Step 3 -> Step 4: Validate vehicle details for all slots and phone"""
        # Validate phone number
        phone_valid = self.validate_phone_number()
        
        # Validate that all selected slots have vehicle numbers
        all_vehicles_valid = True
        vehicle_numbers = []
        
        for slot_id in self.selected_slots:
            vehicle_number = self.vehicle_details.get(slot_id, {}).get("vehicle_number", "").strip().upper()
            
            # Check if vehicle number is valid
            if not vehicle_number or len(vehicle_number) < 3:
                all_vehicles_valid = False
                yield rx.toast.error(f"Please enter a valid vehicle number for Slot {slot_id}")
                return
            
            # Check for duplicate vehicle numbers
            if vehicle_number in vehicle_numbers:
                yield rx.toast.error(f"Vehicle number '{vehicle_number}' is used for multiple slots. Each slot must have a different vehicle.")
                return
            
            vehicle_numbers.append(vehicle_number)
        
        # Only proceed if all validations pass
        if not (all_vehicles_valid and phone_valid):
            return
            
        self.booking_step = 4

    @rx.event
    def set_vehicle_number(self, number: str):
        """Set vehicle registration number"""
        self.vehicle_number = number.upper()
        # Run validation on change
        self.validate_vehicle_number()

    @rx.event
    def set_phone_number(self, number: str):
        """Set contact phone number"""
        self.phone_number = number
        # Run validation on change
        self.validate_phone_number()
    
    @rx.event
    def set_slot_vehicle_number(self, slot_id: str, vehicle_number: str):
        """Set vehicle number for a specific slot"""
        if slot_id in self.vehicle_details:
            self.vehicle_details[slot_id]["vehicle_number"] = vehicle_number.upper()
    
    @rx.event
    def set_slot_driver_name(self, slot_id: str, driver_name: str):
        """Set driver name for a specific slot"""
        if slot_id in self.vehicle_details:
            self.vehicle_details[slot_id]["driver_name"] = driver_name

    @rx.event
    def set_card_number(self, value: str):
        """Set credit card number"""
        self.card_number = value
        self.error_payment_card = ""

    @rx.event
    def set_card_expiry(self, value: str):
        """Set card expiry date"""
        self.card_expiry = value
        self.error_payment_expiry = ""

    @rx.event
    def set_card_cvc(self, value: str):
        """Set card CVC"""
        self.card_cvc = value
        self.error_payment_cvc = ""

    @rx.event
    def set_card_name(self, value: str):
        """Set cardholder name"""
        self.card_name = value
        self.error_payment_name = ""

    def validate_step(self) -> bool:
        """Validate current step before proceeding - shows errors on Next button click"""
        
        if self.booking_step == 1:
            # Step 1: Validate Date, Time, and Duration
            date_valid = self.validate_date()
            time_valid = self.validate_time()
            duration_valid = self.validate_duration()
            
            # Return False if ANY validation fails (errors are already set)
            return date_valid and time_valid and duration_valid
                
        elif self.booking_step == 2:
            # Step 2: Validate Slot Selection
            return self.validate_slots()
                
        elif self.booking_step == 3:
            # Step 3: Validate Vehicle and Phone
            vehicle_valid = self.validate_vehicle_number()
            phone_valid = self.validate_phone_number()
            
            # Return False if ANY validation fails
            return vehicle_valid and phone_valid
        
        # Step 4 or other steps - no validation needed
        return True

    @rx.event
    def next_step(self):
        """Move to next step in booking wizard"""
        # Validate current step first
        if not self.validate_step():
            return  # Stop if validation fails
            
        if self.can_proceed_to_next_step and self.booking_step < 4:
            self.booking_step += 1

    @rx.event
    def previous_step(self):
        """Move to previous step in booking wizard"""
        if self.booking_step > 1:
            self.booking_step -= 1

    @rx.event
    def reset_booking_wizard(self):
        """Reset booking wizard to step 1"""
        self.booking_step = 1
        self.selected_slots = []
        self.vehicle_details = {}
        self.phone_number = ""

    @rx.event
    def proceed_to_payment(self):
        if not self.selected_lot:
            return
        self.is_modal_open = False
        self.is_payment_modal_open = True
        self.payment_error = ""
        # Clear validation errors
        self.error_payment_card = ""
        self.error_payment_expiry = ""
        self.error_payment_cvc = ""
        self.error_payment_name = ""

    @rx.event
    def close_payment_modal(self):
        self.is_payment_modal_open = False
        self.is_processing_payment = False

    @rx.event
    def handle_payment_modal_open_change(self, open: bool):
        self.is_payment_modal_open = open
        if not open:
            self.is_processing_payment = False

    def validate_payment(self) -> bool:
        """Validate payment form fields"""
        is_valid = True
        
        # Reset errors
        self.error_payment_card = ""
        self.error_payment_expiry = ""
        self.error_payment_cvc = ""
        self.error_payment_name = ""
        self.payment_error = ""

        # Validate Card Number
        clean_card = self.card_number.replace(" ", "")
        if not clean_card.isdigit():
            self.error_payment_card = "Card number must contain only digits."
            is_valid = False
        elif len(clean_card) != 16:
            self.error_payment_card = "Card number must be 16 digits."
            is_valid = False

        # Validate Expiry - Must be MM/YY format
        if not self.card_expiry:
            self.error_payment_expiry = "Expiry date is required."
            is_valid = False
        else:
            try:
                if "/" not in self.card_expiry:
                    raise ValueError
                    
                parts = self.card_expiry.split("/")
                if len(parts) != 2:
                    raise ValueError
                    
                month_str, year_str = parts
                
                # Check MM format (2 digits)
                if len(month_str) != 2 or not month_str.isdigit():
                    self.error_payment_expiry = "Month must be 2 digits (MM)."
                    is_valid = False
                    raise ValueError
                
                # Check YY format (2 digits)
                if len(year_str) != 2 or not year_str.isdigit():
                    self.error_payment_expiry = "Year must be 2 digits (YY)."
                    is_valid = False
                    raise ValueError
                
                month = int(month_str)
                year = int(year_str) + 2000  # Convert YY to YYYY
                
                now = datetime.now()
                current_year = now.year
                current_month = now.month
                
                if not (1 <= month <= 12):
                    self.error_payment_expiry = "Invalid month (01-12)."
                    is_valid = False
                elif year < current_year or (year == current_year and month < current_month):
                    self.error_payment_expiry = "Card has expired."
                    is_valid = False
            except ValueError:
                if not self.error_payment_expiry:  # Only set if not already set
                    self.error_payment_expiry = "Invalid format. Use MM/YY (e.g., 12/25)."
                is_valid = False

        # Validate CVC - Must be exactly 3 digits
        if not self.card_cvc:
            self.error_payment_cvc = "CVC is required."
            is_valid = False
        elif not self.card_cvc.isdigit():
            self.error_payment_cvc = "CVC must be numeric."
            is_valid = False
        elif len(self.card_cvc) != 3:
            self.error_payment_cvc = "CVC must be exactly 3 digits."
            is_valid = False

        # Validate Name
        if not self.card_name.strip():
            self.error_payment_name = "Cardholder name is required."
            is_valid = False

        return is_valid

    @rx.event
    async def process_payment(self):
        # STEP 1: Validate ALL booking fields first  
        if not self.validate_all_booking_fields():
            # Collect specific errors to show the user
            error_details = []
            if self.error_date: error_details.append(f"Date: {self.error_date}")
            if self.error_time: error_details.append(f"Time: {self.error_time}")
            if self.error_duration: error_details.append(f"Duration: {self.error_duration}")
            if self.error_slot: error_details.append(f"Slot: {self.error_slot}")
            if self.error_phone: error_details.append(f"Phone: {self.error_phone}")
            
            error_msg = " • ".join(error_details) if error_details else "Please check your inputs."
            yield rx.toast.error(f"Correction Needed: {error_msg}")
            return
        
        # STEP 2: Validate payment fields
        if not self.validate_payment():
            yield rx.toast.error("Please enter valid payment details")
            return

        self.is_processing_payment = True
        await asyncio.sleep(1.0)
        from app.states.auth_state import AuthState

        auth_state = await self.get_state(AuthState)
        user_email = auth_state.email or auth_state.session_email
        if not user_email:
            self.is_processing_payment = False
            yield rx.toast.error("User not identified.")
            return
        try:
            with rx.session() as session:
                user = session.exec(
                    select(DBUser).where(DBUser.email == user_email)
                ).first()
                if not user:
                    raise ValueError("User not found")
                lot = session.get(DBParkingLot, int(self.selected_lot.id))
                if not lot:
                    raise ValueError("Parking lot not found")
                
                # Check if lot has enough spots for all selected slots
                if lot.available_spots < len(self.selected_slots):
                    self.payment_error = f"Not enough spots available. Only {lot.available_spots} left."
                    self.is_processing_payment = False
                    yield rx.toast.error("Booking Failed: Not enough spots available.")
                    return
                
                # Simulate payment failure
                if random.random() > 0.98:
                    self.payment_error = "Payment declined by bank."
                    self.is_processing_payment = False
                    yield rx.toast.error("Payment Failed")
                    return
                
                # Create transaction ID for this payment
                transaction_id = f"TXN_{str(uuid.uuid4())[:8].upper()}"
                timestamp = datetime.now()
                created_booking_ids = []
                
                # Create one booking for EACH selected slot
                for slot_id in self.selected_slots:
                    vehicle_info = self.vehicle_details.get(slot_id, {})
                    vehicle_number = vehicle_info.get("vehicle_number", "UNKNOWN")
                    
                    # Find the slot in DB to link it and mark as occupied
                    db_slot = session.exec(
                        select(DBParkingSlot).where(
                            DBParkingSlot.lot_id == lot.id,
                            DBParkingSlot.slot_number == slot_id
                        )
                    ).first()
                    
                    if db_slot:
                        db_slot.is_occupied = True
                        db_slot.last_occupied_at = timestamp
                        session.add(db_slot)

                    new_booking = DBBooking(
                        user_id=user.id,
                        lot_id=lot.id,
                        start_date=self.start_date,
                        start_time=self.start_time,
                        duration_hours=self.duration_hours,
                        total_price=self.selected_lot.price_per_hour * self.duration_hours,  # Price per individual slot
                        status="Confirmed",
                        payment_status="Paid",
                        transaction_id=transaction_id,  # Same transaction for all
                        slot_id=slot_id,
                        slot_db_id=db_slot.id if db_slot else None,
                        vehicle_number=vehicle_number,
                        phone_number=self.phone_number,
                        created_at=timestamp,
                    )
                    session.add(new_booking)
                    session.flush()
                    created_booking_ids.append(new_booking.id)
                
                # Create single payment for total amount
                new_payment = DBPayment(
                    transaction_id=transaction_id,
                    booking_id=created_booking_ids[0] if created_booking_ids else None,  # Link to first booking
                    amount=self.total_price_all_slots,  # Total for all slots
                    status="Success",
                    timestamp=timestamp,
                    method="Credit Card",
                )
                session.add(new_payment)
                
                # Update available spots (reduce by number of slots booked)
                lot.available_spots -= len(self.selected_slots)
                session.add(lot)
                
                # Create audit log
                slot_list = ", ".join(self.selected_slots)
                new_audit = DBAuditLog(
                    action="Multi-Slot Booking Created",
                    timestamp=timestamp,
                    details=f"Created {len(self.selected_slots)} bookings ({slot_list}) for {lot.name}. Total: RM {self.total_price_all_slots:.2f}",
                    user_id=user.id,
                )
                session.add(new_audit)
                session.commit()

                # Send Confirmation Email
                try:
                    from app.services.email_service import send_booking_confirmation_email, send_payment_success_email
                    
                    logging.info(f"🔔 Attempting to send booking confirmation email to {user.email}")
                    
                    # Send confirmation for the first booking (or could send one email with all details)
                    booking_details = {
                        "user_name": user.full_name or "User",
                        "lot_name": lot.name,
                        "start_date": self.start_date,
                        "start_time": self.start_time,
                        "duration": self.duration_hours,
                        "slot_id": slot_list,  # All slots
                        "vehicle_number": ", ".join([self.vehicle_details.get(s, {}).get("vehicle_number", "N/A") for s in self.selected_slots]),
                        "total_price": self.total_price_all_slots,
                        "payment_status": "Paid"
                    }
                    
                    confirmation_sent = send_booking_confirmation_email(user.email, booking_details)
                    if confirmation_sent:
                        logging.info(f"✅ Booking confirmation email sent successfully to {user.email}")
                    else:
                        logging.warning(f"⚠️ Booking confirmation email FAILED to send to {user.email}")
                    
                    # Send Payment Receipt
                    payment_details = {
                        "user_name": user.full_name or "User",
                        "amount": self.total_price_all_slots,
                        "transaction_id": transaction_id,
                        "payment_date": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "payment_method": "Credit Card",
                        "booking_id": f"BK-{', '.join(map(str, created_booking_ids))}"
                    }
                    
                    payment_sent = send_payment_success_email(user.email, payment_details)
                    if payment_sent:
                        logging.info(f"✅ Payment receipt email sent successfully to {user.email}")
                    else:
                        logging.warning(f"⚠️ Payment receipt email FAILED to send to {user.email}")
                        
                except Exception as e:
                    logging.exception(f"❌ Failed to send confirmation/receipt emails: {e}")


                from app.states.parking_state import ParkingState

                parking_state = await self.get_state(ParkingState)
                parking_state.update_spots(lot.id, -len(self.selected_slots))  # Decrease by number of slots
                self.is_payment_modal_open = False
                self.is_processing_payment = False
                self.selected_lot = None
                
                # Clear selected slots and vehicle details
                self.selected_slots = []
                self.vehicle_details = {}
                
                yield rx.toast.success(f"Payment Successful! {len(created_booking_ids)} booking(s) confirmed.")
                yield BookingState.load_bookings
                yield rx.redirect("/bookings")
        except Exception as e:
            logging.exception(f"Transaction failed: {e}")
            self.is_processing_payment = False
            yield rx.toast.error(f"Error processing booking: {str(e)}")

    @rx.event
    def initiate_cancellation(self, booking: Booking):
        self.booking_to_cancel = booking
        self.is_cancellation_modal_open = True
        try:
            booking_start = datetime.strptime(
                f"{booking.start_date} {booking.start_time}", "%Y-%m-%d %H:%M"
            )
            now = datetime.now()
            diff = booking_start - now
            hours_diff = diff.total_seconds() / 3600
            if hours_diff >= 24:
                self.refund_percentage = 100
                self.refund_amount_display = booking.total_price
                self.cancellation_message = (
                    "Full refund available (more than 24h before booking)."
                )
            elif hours_diff > 0:
                self.refund_percentage = 50
                self.refund_amount_display = booking.total_price * 0.5
                self.cancellation_message = (
                    "50% refund available (less than 24h before booking)."
                )
            else:
                self.refund_percentage = 0
                self.refund_amount_display = 0.0
                self.cancellation_message = (
                    "No refund available (booking has already started)."
                )
        except Exception as e:
            logging.exception(f"Error calculating refund: {e}")
            self.refund_percentage = 0
            self.refund_amount_display = 0.0
            self.cancellation_message = "Error calculating refund eligibility."

    @rx.event
    def close_cancellation_modal(self):
        self.is_cancellation_modal_open = False
        self.booking_to_cancel = None
        self.user_cancellation_reason = ""  # Reset reason

    @rx.event
    def handle_cancellation_modal_open_change(self, open: bool):
        self.is_cancellation_modal_open = open
        if not open:
            self.booking_to_cancel = None

    @rx.event
    async def confirm_cancellation(self):
        if not self.booking_to_cancel:
            return
        try:
            db_id = int(self.booking_to_cancel.id.replace("BK-", ""))
        except ValueError as e:
            logging.exception(f"Invalid booking ID format: {e}")
            yield rx.toast.error("Invalid booking ID format.")
            return
        try:
            with rx.session() as session:
                booking = session.get(DBBooking, db_id)
                if not booking:
                    raise ValueError("Booking not found in database")
                if booking.status == "Cancelled":
                    yield rx.toast.error("Booking already cancelled.")
                    return
                booking.status = "Cancelled"
                
                # Set refund status to Pending instead of processing immediately
                if self.refund_amount_display > 0:
                    booking.refund_status = "Pending"
                    booking.refund_amount = self.refund_amount_display
                    booking.payment_status = "Pending Refund"
                else:
                    booking.payment_status = "Cancelled (No Refund)"
                
                booking.cancellation_reason = self.user_cancellation_reason.strip() or "User requested cancellation"
                booking.cancellation_at = datetime.now()
                session.add(booking)
                
                # Free up the parking spot
                lot = session.get(DBParkingLot, booking.lot_id)
                if lot:
                    lot.available_spots = min(lot.total_spots, lot.available_spots + 1)
                    session.add(lot)
                
                # Free the specific slot in DB
                if booking.slot_db_id:
                    db_slot = session.get(DBParkingSlot, booking.slot_db_id)
                    if db_slot:
                        db_slot.is_occupied = False
                        session.add(db_slot)
                
                # Audit log
                audit = DBAuditLog(
                    action="Booking Cancelled",
                    timestamp=datetime.now(),
                    details=f"Booking {booking.id} cancelled. Refund pending admin approval: RM {self.refund_amount_display:.2f}",
                    user_id=booking.user_id,
                )
                session.add(audit)
                session.commit()
                
                from app.states.parking_state import ParkingState

                parking_state = await self.get_state(ParkingState)
                if lot:
                    parking_state.update_spots(lot.id, 1)
                yield BookingState.load_bookings
                yield rx.toast.info("Booking cancelled. Refund request sent to admin for approval.")
        except Exception as e:
            logging.exception(f"Cancellation failed: {e}")
            yield rx.toast.error("Failed to cancel booking.")
        self.is_cancellation_modal_open = False
        self.booking_to_cancel = None
        self.user_cancellation_reason = ""  # Reset reason

    @rx.event
    def print_ticket(self, booking_id: str):
        """Find booking and trigger client-side print"""
        # Find the booking in the list
        booking = next((b for b in self.bookings if b.id == booking_id), None)
        if booking:
            # Construct the JS call with concrete values
            js_call = (
                f"window.printTicket({{"
                f"id: '{booking.id}', "
                f"lot_name: '{booking.lot_name}', "
                f"start_date: '{booking.start_date}', "
                f"start_time: '{booking.start_time}', "
                f"duration_hours: '{booking.duration_hours}', "
                f"slot_id: '{booking.slot_id}', "
                f"vehicle_number: '{booking.vehicle_number}', "
                f"phone_number: '{booking.phone_number}', "
                f"status: '{booking.status}', "
                f"total_price: '{booking.total_price}'"
                f"}})"
            )
            return rx.call_script(js_call)
        else:
            return rx.toast.error("Booking not found for printing.")

    @rx.event
    def share_ticket(self, booking_id: str):
        """Copy booking details to clipboard for sharing"""
        booking = next((b for b in self.bookings if b.id == booking_id), None)
        if booking:
            share_text = (
                f"🚗 *Parking Ticket - {booking.lot_name}*\\n"
                f"📍 {booking.lot_location}\\n\\n"
                f"📅 Date: {booking.start_date}\\n"
                f"⏰ Time: {booking.start_time}\\n"
                f"⏳ Duration: {booking.duration_hours} Hours\\n"
                f"🅿️ Slot: {booking.slot_id}\\n"
                f"🚘 Vehicle: {booking.vehicle_number}\\n"
                f"🆔 Booking ID: {booking.id}\\n\\n"
                f"💰 Total Paid: RM {booking.total_price}\\n"
                f"✅ Status: {booking.status}"
            )
            return [
                rx.set_clipboard(share_text),
                rx.toast.success("Ticket details copied to clipboard!")
            ]
        else:
            return rx.toast.error("Booking not found for sharing.")
    
    
    @rx.event
    async def generate_qr_codes(self):
        """Generate QR codes for all bookings"""
        self.is_generating_qr = True
        yield
        
        for booking in self.bookings:
            if booking.id not in self.qr_codes:
                # Create QR code data
                qr_data = (
                    f"PARKING TICKET\n"
                    f"ID: {booking.id}\n"
                    f"Location: {booking.lot_name}\n"
                    f"Slot: {booking.slot_id}\n"
                    f"Date: {booking.start_date}\n"
                    f"Time: {booking.start_time}\n"
                    f"Duration: {booking.duration_hours}h\n"
                    f"Vehicle: {booking.vehicle_number}\n"
                    f"Status: {booking.status}"
                )
                
                # Generate QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(qr_data)
                qr.make(fit=True)
                
                # Create image
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                # Store in state
                self.qr_codes[booking.id] = f"data:image/png;base64,{img_base64}"
        
        self.is_generating_qr = False
    
    
    def get_qr_code(self, booking_id: str) -> str:
        """Get QR code from cache"""
        return self.qr_codes.get(booking_id, "")
    
    def toggle_refund_details(self, booking_id: str):
        """Toggle refund details visibility for a booking"""
        current_state = self.expanded_refund_details.get(booking_id, False)
        self.expanded_refund_details[booking_id] = not current_state
    
    def toggle_qr_code(self, booking_id: str):
        """Toggle QR code visibility for a booking"""
        current_state = self.expanded_qr_codes.get(booking_id, False)
        self.expanded_qr_codes[booking_id] = not current_state
    
    def set_card_expiry(self, value: str):
        """Format expiry date as MM/YY - auto-insert / after 2 digits"""
        # Remove any existing slashes
        cleaned = value.replace("/", "")
        
        # Only allow digits
        cleaned = ''.join(c for c in cleaned if c.isdigit())
        
        # Limit to 4 digits max (MMYY)
        cleaned = cleaned[:4]
        
        # Auto-insert / after 2 digits
        if len(cleaned) >= 2:
            formatted = cleaned[:2] + "/" + cleaned[2:]
        else:
            formatted = cleaned
        
        # Store the formatted value
        self.card_expiry = formatted
    
    def set_card_cvc(self, value: str):
        """Limit CVC to exactly 3 digits"""
        # Only allow digits
        cleaned = ''.join(c for c in value if c.isdigit())
        
        # Limit to 3 digits
        self.card_cvc = cleaned[:3]
    
    def can_reschedule_booking(self, booking: Booking) -> bool:
        """Check if a booking can be rescheduled (MORE than 24 hours before start)"""
        try:
            from datetime import datetime
            
            # Parse booking start datetime
            booking_start = datetime.strptime(
                f"{booking.start_date} {booking.start_time}",
                "%Y-%m-%d %H:%M"
            )
            
            # Get current time
            current_time = datetime.now()
            
            # Calculate time difference
            time_until = booking_start - current_time
            hours_until = time_until.total_seconds() / 3600
            
            # Must be MORE than 24 hours (not equal to)
            return hours_until > 24.0
            
        except Exception as e:
            # If any error, don't allow rescheduling
            return False
    
    def initiate_reschedule(self, booking: Booking):
        """Open reschedule modal with current booking details"""
        self.booking_to_reschedule = booking
        self.new_start_date = booking.start_date
        self.new_start_time = booking.start_time
        self.is_reschedule_modal_open = True
    
    def close_reschedule_modal(self):
        """Close reschedule modal and reset"""
        self.is_reschedule_modal_open = False
        self.booking_to_reschedule = None
        self.new_start_date = ""
        self.new_start_time = ""
    
    @rx.event
    async def confirm_reschedule(self):
        """Confirm booking time change"""
        if not self.booking_to_reschedule:
            return
        
        try:
            # Validate new time is at least 24 hours away
            from datetime import datetime, timedelta
            new_booking_time = datetime.strptime(
                f"{self.new_start_date} {self.new_start_time}",
                "%Y-%m-%d %H:%M"
            )
            time_until = new_booking_time - datetime.now()
            
            if time_until.total_seconds() < 24 * 3600:
                yield rx.toast.error("New booking time must be at least 24 hours from now.")
                return
            
            db_id = int(self.booking_to_reschedule.id.replace("BK-", ""))
            
            with rx.session() as session:
                from app.db.models import Booking as DBBooking
                booking = session.get(DBBooking, db_id)
                
                if not booking:
                    yield rx.toast.error("Booking not found.")
                    return
                
                # Update booking time
                old_date = booking.start_date
                old_time = booking.start_time
                booking.start_date = self.new_start_date
                booking.start_time = self.new_start_time
                
                session.add(booking)
                session.commit()
                
                yield rx.toast.success(f"Booking rescheduled from {old_date} {old_time} to {self.new_start_date} {self.new_start_time}")
                yield BookingState.load_bookings
                
        except Exception as e:
            logging.exception(f"Reschedule failed: {e}")
            yield rx.toast.error("Failed to reschedule booking.")
        
        self.close_reschedule_modal()

