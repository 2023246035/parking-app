import reflex as rx
from datetime import datetime, timedelta
from typing import Optional
import sqlmodel
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    """User model for authentication and profile management."""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    name: str
    phone: str
    member_since: datetime = Field(default_factory=datetime.utcnow)
    avatar_url: str = "https://api.dicebear.com/9.x/notionists/svg?seed=default"
    bookings: list["Booking"] = Relationship(back_populates="user")
    booking_rules: list["BookingRule"] = Relationship(back_populates="user")
    audit_logs: list["AuditLog"] = Relationship(back_populates="user")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "phone": self.phone,
            "member_since": self.member_since.isoformat(),
            "avatar_url": self.avatar_url,
        }


class ParkingLot(SQLModel, table=True):
    """Parking Lot model containing lot details and availability."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    location: str = Field(index=True)
    price_per_hour: float
    total_spots: int
    available_spots: int
    image_url: str
    features: str
    rating: float
    bookings: list["Booking"] = Relationship(back_populates="parking_lot")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "price_per_hour": self.price_per_hour,
            "total_spots": self.total_spots,
            "available_spots": self.available_spots,
            "image_url": self.image_url,
            "features": self.features.split(",") if self.features else [],
            "rating": self.rating,
        }


class CancellationPolicy(SQLModel, table=True):
    """Configurable cancellation and refund policy (BRD-aligned)"""

    id: Optional[int] = Field(default=None, primary_key=True)
    full_refund_hours: int = Field(default=24)  # Hours before start for 100% refund
    partial_refund_hours: int = Field(default=0)  # Hours before start for partial refund
    partial_refund_percentage: int = Field(default=50)  # Percentage for partial refund
    non_cancellable_hours: int = Field(default=0)  # Block cancellation within X hours
    allow_cancellation_after_start: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Booking(SQLModel, table=True):
    """Booking model tracking reservations."""

    id: Optional[int] = Field(default=None, primary_key=True)
    start_date: str
    start_time: str
    duration_hours: int
    total_price: float
    status: str = Field(default="Pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    payment_status: str = Field(default="Pending")
    transaction_id: Optional[str] = None
    refund_amount: float = Field(default=0.0)
    refund_status: Optional[str] = Field(default=None)  # None, "Pending", "Approved", "Rejected"
    refund_approved_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    cancellation_at: Optional[datetime] = None
    is_refundable: bool = Field(default=True)  # BRD: Support non-refundable bookings
    slot_id: Optional[str] = Field(default=None)
    vehicle_number: Optional[str] = Field(default=None)
    phone_number: Optional[str] = Field(default=None)
    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="bookings")
    lot_id: int = Field(foreign_key="parkinglot.id")
    parking_lot: Optional[ParkingLot] = Relationship(back_populates="bookings")
    payment: Optional["Payment"] = Relationship(back_populates="booking")

    def to_dict(self):
        return {
            "id": self.id,
            "lot_id": self.lot_id,
            "user_id": self.user_id,
            "start_date": self.start_date,
            "start_time": self.start_time,
            "duration_hours": self.duration_hours,
            "total_price": self.total_price,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "payment_status": self.payment_status,
            "transaction_id": self.transaction_id,
        }


class Payment(SQLModel, table=True):
    """Payment model for transaction records."""

    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: str = Field(unique=True, index=True)
    amount: float
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    method: str
    booking_id: int = Field(foreign_key="booking.id")
    booking: Optional[Booking] = Relationship(back_populates="payment")

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "booking_id": self.booking_id,
            "amount": self.amount,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "method": self.method,
        }


class OTPVerification(SQLModel, table=True):
    """OTP verification model for secure password reset and email verification."""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    otp_code: str
    purpose: str = Field(default="password_reset")  # password_reset, email_verification
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    is_used: bool = Field(default=False)
    attempts: int = Field(default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "purpose": self.purpose,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_used": self.is_used,
            "attempts": self.attempts,
        }


class AuditLog(SQLModel, table=True):
    """Audit log for tracking system actions."""

    id: Optional[int] = Field(default=None, primary_key=True)
    action: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: str
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="audit_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "user_id": self.user_id,
        }


class BookingRule(SQLModel, table=True):
    """Auto-booking rule for Smart Dashboard."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    location: str
    days: str  # Comma-separated days: "Mon,Tue"
    time: str
    duration: str
    status: str = Field(default="Active")
    next_run: str
    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="booking_rules")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "location": self.location,
            "days": self.days.split(","),
            "time": self.time,
            "duration": self.duration,
            "status": self.status,
            "next_run": self.next_run,
            "user_id": self.user_id
        }