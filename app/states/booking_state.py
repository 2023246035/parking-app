import reflex as rx
from datetime import datetime, timedelta
from typing import Optional
import random
import logging
import asyncio
import uuid
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

    @rx.var
    def estimated_price(self) -> float:
        if not self.selected_lot:
            return 0.0
        return self.selected_lot.price_per_hour * self.duration_hours

    @rx.var
    def active_bookings(self) -> list[Booking]:
        return [b for b in self.bookings if b.status == "Confirmed"]

    @rx.var
    def past_bookings(self) -> list[Booking]:
        return [b for b in self.bookings if b.status == "Completed"]

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
        """Check if user can proceed to next step"""
        if self.booking_step == 1:
            return self.selected_slot != ""
        elif self.booking_step == 2:
            return True
        elif self.booking_step == 3:
            return self.vehicle_number != "" and self.phone_number != ""
        return True

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
                        cancellation_reason=b.cancellation_reason or "",
                        cancellation_at=b.cancellation_at.isoformat()
                        if b.cancellation_at
                        else "",
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

    @rx.event
    def close_modal(self):
        self.is_modal_open = False
        self.selected_lot = None

    @rx.event
    def set_start_date(self, date: str):
        self.start_date = date

    @rx.event
    def set_start_time(self, time: str):
        self.start_time = time

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

    @rx.event
    def set_vehicle_number(self, number: str):
        """Set vehicle registration number"""
        self.vehicle_number = number.upper()

    @rx.event
    def set_phone_number(self, number: str):
        """Set contact phone number"""
        self.phone_number = number

    @rx.event
    def next_step(self):
        """Move to next step in booking wizard"""
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

    @rx.event
    def close_payment_modal(self):
        self.is_payment_modal_open = False
        self.is_processing_payment = False

    @rx.event
    async def process_payment(self):
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
                booking.payment_status = (
                    "Refunded"
                    if self.refund_amount_display > 0
                    else booking.payment_status
                )
                booking.refund_amount = self.refund_amount_display
                booking.cancellation_reason = "User requested via web"
                booking.cancellation_at = datetime.now()
                session.add(booking)
                lot = session.get(DBParkingLot, booking.lot_id)
                if lot:
                    lot.available_spots += 1
                    session.add(lot)
                if self.refund_amount_display > 0:
                    refund = DBPayment(
                        transaction_id=f"RFD_{str(uuid.uuid4())[:8].upper()}",
                        booking_id=booking.id,
                        amount=self.refund_amount_display,
                        status="Refunded",
                        timestamp=datetime.now(),
                        method="Original Payment Method",
                    )
                    session.add(refund)
                audit = DBAuditLog(
                    action="Booking Cancelled",
                    timestamp=datetime.now(),
                    details=f"Booking {booking.id} cancelled",
                    user_id=booking.user_id,
                )
                session.add(audit)
                session.commit()
                from app.states.parking_state import ParkingState

                parking_state = await self.get_state(ParkingState)
                if lot:
                    parking_state.update_spots(lot.id, 1)
                yield BookingState.load_bookings
                yield rx.toast.info("Booking cancelled successfully.")
        except Exception as e:
            logging.exception(f"Cancellation failed: {e}")
            yield rx.toast.error("Failed to cancel booking.")
        self.is_cancellation_modal_open = False
        self.booking_to_cancel = None
