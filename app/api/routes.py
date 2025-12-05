from fastapi import APIRouter, HTTPException, status
from sqlmodel import select
from typing import Optional
from datetime import datetime
import logging
import reflex as rx
from app.db.models import ParkingLot, Booking, User, AuditLog

router = APIRouter(tags=["Parking API"])


@router.get("/api/parking-lots", summary="Get all parking lots")
async def get_parking_lots(
    location: Optional[str] = None, search: Optional[str] = None
):
    """Retrieve all parking lots with optional filtering by location and search term."""
    with rx.session() as session:
        query = select(ParkingLot)
        if location and location != "All":
            query = query.where(ParkingLot.location.contains(location))
        if search:
            query = query.where(ParkingLot.name.contains(search))
        lots = session.exec(query).all()
        return [lot.to_dict() for lot in lots]


@router.get("/api/parking-lots/{lot_id}", summary="Get parking lot by ID")
async def get_parking_lot(lot_id: int):
    """Retrieve a specific parking lot by its ID."""
    with rx.session() as session:
        lot = session.get(ParkingLot, lot_id)
        if not lot:
            raise HTTPException(status_code=404, detail="Parking lot not found")
        return lot.to_dict()


@router.put("/api/parking-lots/{lot_id}/availability", summary="Update availability")
async def update_availability(lot_id: int, available_spots: int):
    """Update the available spots for a parking lot."""
    with rx.session() as session:
        lot = session.get(ParkingLot, lot_id)
        if not lot:
            raise HTTPException(status_code=404, detail="Parking lot not found")
        lot.available_spots = available_spots
        session.add(lot)
        session.commit()
        session.refresh(lot)
        return lot.to_dict()


@router.get("/api/bookings", summary="Get user bookings")
async def get_bookings(user_email: str, status_filter: Optional[str] = None):
    """Retrieve bookings for a specific user with optional status filter."""
    with rx.session() as session:
        user = session.exec(select(User).where(User.email == user_email)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        query = select(Booking).where(Booking.user_id == user.id)
        if status_filter:
            query = query.where(Booking.status == status_filter)
        bookings = session.exec(query.order_by(Booking.created_at.desc())).all()
        return [b.to_dict() for b in bookings]


@router.post("/api/bookings", summary="Create a new booking")
async def create_booking(data: dict):
    """Create a new parking booking."""
    with rx.session() as session:
        required_fields = [
            "user_email",
            "lot_id",
            "start_date",
            "start_time",
            "duration_hours",
            "total_price",
        ]
        if not all((k in data for k in required_fields)):
            raise HTTPException(status_code=400, detail="Missing required fields")
        user = session.exec(
            select(User).where(User.email == data["user_email"])
        ).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        lot = session.get(ParkingLot, data["lot_id"])
        if not lot:
            raise HTTPException(status_code=404, detail="Parking lot not found")
        if lot.available_spots <= 0:
            raise HTTPException(status_code=400, detail="Parking lot is full")
        booking = Booking(
            user_id=user.id,
            lot_id=lot.id,
            start_date=data["start_date"],
            start_time=data["start_time"],
            duration_hours=data["duration_hours"],
            total_price=data["total_price"],
            status="Confirmed",
            payment_status="Paid",
            transaction_id=f"TXN_{int(datetime.now().timestamp())}",
        )
        session.add(booking)
        lot.available_spots -= 1
        session.add(lot)
        audit = AuditLog(
            action="Booking Created",
            details=f"Booking for {lot.name} by {user.email}",
            user_id=user.id,
        )
        session.add(audit)
        try:
            session.commit()
            session.refresh(booking)
            return booking.to_dict()
        except Exception as e:
            logging.exception(f"Error creating booking: {e}")
            session.rollback()
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/bookings/{booking_id}/cancel", summary="Cancel a booking")
async def cancel_booking(booking_id: int):
    """Cancel an existing booking and process refund."""
    with rx.session() as session:
        booking = session.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        if booking.status == "Cancelled":
            raise HTTPException(status_code=400, detail="Booking already cancelled")
        refund_amount = booking.total_price * 0.5
        booking.status = "Cancelled"
        booking.payment_status = "Refunded"
        booking.refund_amount = refund_amount
        booking.cancellation_at = datetime.utcnow()
        booking.cancellation_reason = "User requested via API"
        session.add(booking)
        lot = session.get(ParkingLot, booking.lot_id)
        if lot:
            lot.available_spots += 1
            session.add(lot)
        try:
            session.commit()
            return {"message": "Booking cancelled", "refund_amount": refund_amount}
        except Exception as e:
            logging.exception(f"Error cancelling booking: {e}")
            session.rollback()
            raise HTTPException(status_code=500, detail=str(e))