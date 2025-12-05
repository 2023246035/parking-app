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
    # New slot booking variables
    booking_step: int = 1
    selected_slot: str = ""
    vehicle_number: str = ""
    phone_number: str = ""
    is_loading_slots: bool = False
    occupied_slots: list[str] = []
    qr_codes: dict[str, str] = {}  # Store QR codes by booking ID
    is_generating_qr: bool = False  # Loading state for QR generation
    
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
    
    def validate_slot(self) -> bool:
        """Validate parking slot selection"""
        self.error_slot = ""
        
        if not self.selected_slot or self.selected_slot.strip() == "":
            self.error_slot = "Please select a parking slot"
            return False
        
        # Check if slot is occupied
        if self.selected_slot in self.occupied_slots:
            self.error_slot = f"Slot {self.selected_slot} is already occupied"
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
        
        # Check minimum length (international standard)
        if len(clean_phone) < 10:
            self.error_phone = "Phone number must be at least 10 digits"
            return False
        
        # Check maximum length
        if len(clean_phone) > 15:
            self.error_phone = "Phone number cannot exceed 15 digits"
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
        
        if not self.validate_slot():
            is_valid = False
        
        if not self.validate_vehicle_number():
            is_valid = False
        
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
            # Step 2: Must have selected a slot
            return self.selected_slot != "" and self.error_slot == ""
        elif self.booking_step == 3:
            # Step 3: Must have vehicle and phone
            return (
                self.vehicle_number.strip() != "" and 
                self.phone_number.strip() != "" and
                self.error_vehicle == "" and
                self.error_phone == ""
            )
        elif self.booking_step == 4:
            # Step 4: All validations must pass
            return (
                self.start_date != "" and
                self.start_time != "" and
                self.selected_slot != "" and
                self.vehicle_number.strip() != "" and
                self.phone_number.strip() != "" and
                self.error_date == "" and
                self.error_time == "" and
                self.error_duration == "" and
                self.error_slot == "" and
                self.error_vehicle == "" and
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
                        cancellation_at=b.cancellation_at.isoformat()
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

    @rx.event
    def close_modal(self):
        self.is_modal_open = False
        self.selected_lot = None

    @rx.event
    def handle_modal_open_change(self, open: bool):
        self.is_modal_open = open
        if not open:
            self.selected_lot = None

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
    def select_slot(self, slot: str):
        """Select a parking slot"""
        self.selected_slot = slot
        # Run validation on change
        self.validate_slot()

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
                            slot_id = getattr(booking, 'slot_id', None)
                            if slot_id:
                                self.occupied_slots.append(slot_id)
                    except Exception as e:
                        logging.warning(f"Error parsing booking datetime: {e}")
                        continue
                        
        except Exception as e:
            logging.exception(f"Error loading occupied slots: {e}")
            logging.error("Failed to load slot availability")
        finally:
            self.is_loading_slots = False

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
        self.selected_slot = ""
        self.error_slot = ""

    @rx.event
    def go_back_to_step_1(self):
        """Go back to step 1"""
        self.booking_step = 1
        self.selected_slot = ""
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
        """Step 2 -> Step 3: Validate slot selection"""
        if not self.validate_slot():
            return
        self.booking_step = 3

    @rx.event
    def proceed_to_review(self):
        """Step 3 -> Step 4: Validate vehicle and contact info"""
        # Use comprehensive validators
        vehicle_valid = self.validate_vehicle_number()
        phone_valid = self.validate_phone_number()
        
        # Only proceed if both validations pass
        if not (vehicle_valid and phone_valid):
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
            return self.validate_slot()
                
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
        self.selected_slot = ""
        self.vehicle_number = ""
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

        # Validate Expiry
        if not self.card_expiry:
            self.error_payment_expiry = "Expiry date is required."
            is_valid = False
        else:
            try:
                if "/" not in self.card_expiry:
                    raise ValueError
                month, year = self.card_expiry.split("/")
                month = int(month)
                year = int(year) + 2000  # Assume YY format
                
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
                self.error_payment_expiry = "Invalid format (MM/YY)."
                is_valid = False

        # Validate CVC
        if not self.card_cvc.isdigit():
            self.error_payment_cvc = "CVC must be numeric."
            is_valid = False
        elif not (3 <= len(self.card_cvc) <= 4):
            self.error_payment_cvc = "CVC must be 3 or 4 digits."
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
            yield rx.toast.error("Please fill in all required fields correctly")
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
                if lot.available_spots <= 0:
                    self.payment_error = "This parking lot is now full."
                    self.is_processing_payment = False
                    yield rx.toast.error("Booking Failed: Lot is full.")
                    return
                if random.random() > 0.98:
                    self.payment_error = "Payment declined by bank."
                    self.is_processing_payment = False
                    yield rx.toast.error("Payment Failed")
                    return
                transaction_id = f"TXN_{str(uuid.uuid4())[:8].upper()}"
                timestamp = datetime.now()
                new_booking = DBBooking(
                    user_id=user.id,
                    lot_id=lot.id,
                    start_date=self.start_date,
                    start_time=self.start_time,
                    duration_hours=self.duration_hours,
                    total_price=self.estimated_price,
                    status="Confirmed",
                    payment_status="Paid",
                    transaction_id=transaction_id,
                    slot_id=self.selected_slot,
                    vehicle_number=self.vehicle_number,
                    phone_number=self.phone_number,
                    created_at=timestamp,
                )
                session.add(new_booking)
                session.flush()
                new_payment = DBPayment(
                    transaction_id=transaction_id,
                    booking_id=new_booking.id,
                    amount=self.estimated_price,
                    status="Success",
                    timestamp=timestamp,
                    method="Credit Card",
                )
                session.add(new_payment)
                lot.available_spots -= 1
                session.add(lot)
                new_audit = DBAuditLog(
                    action="Booking Created",
                    timestamp=timestamp,
                    details=f"Booking {new_booking.id} for {lot.name}, Slot: {self.selected_slot}, Vehicle: {self.vehicle_number}",
                    user_id=user.id,
                )
                session.add(new_audit)
                session.commit()
                from app.states.parking_state import ParkingState

                parking_state = await self.get_state(ParkingState)
                parking_state.update_spots(lot.id, -1)
                self.is_payment_modal_open = False
                self.is_processing_payment = False
                self.selected_lot = None
                yield rx.toast.success("Payment Successful! Booking Confirmed.")
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
                
                booking.cancellation_reason = "User requested via web"
                booking.cancellation_at = datetime.now()
                session.add(booking)
                
                # Free up the parking spot
                lot = session.get(DBParkingLot, booking.lot_id)
                if lot:
                    lot.available_spots += 1
                    session.add(lot)
                
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
