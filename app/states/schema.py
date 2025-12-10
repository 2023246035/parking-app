import reflex as rx


class User(rx.Base):
    name: str
    email: str
    phone: str
    member_since: str
    avatar_url: str


class ParkingLot(rx.Base):
    id: str
    name: str
    location: str
    price_per_hour: float
    total_spots: int
    available_spots: int
    image_url: str
    features: list[str]
    rating: float
    # AI Features
    base_price: float = 0.0
    dynamic_price: float = 0.0
    demand_multiplier: float = 1.0
    recommendation_score: float = 0.0
    recommendation_reasons: list[str] = []


class Payment(rx.Base):
    transaction_id: str
    booking_id: str
    amount: float
    status: str
    timestamp: str
    method: str


class AuditLog(rx.Base):
    id: str
    action: str
    timestamp: str
    details: str
    user_email: str


class Booking(rx.Base):
    id: str
    lot_id: str
    lot_name: str
    lot_location: str
    lot_image: str
    start_date: str
    start_time: str
    duration_hours: int
    total_price: float
    status: str
    created_at: str
    payment_status: str = "Pending"
    transaction_id: str = ""
    refund_amount: float = 0.0
    refund_status: str = ""  # "", "Pending", "Approved", "Rejected"
    refund_approved_at: str = ""
    cancellation_reason: str = ""
    cancellation_at: str = ""
    slot_id: str = ""
    vehicle_number: str = ""
    phone_number: str = ""
    
    @property
    def is_future(self) -> bool:
        """Check if booking end time is in the future"""
        try:
            from datetime import datetime, timedelta
            # Parse booking start time
            booking_start = datetime.strptime(
                f"{self.start_date} {self.start_time}", 
                "%Y-%m-%d %H:%M"
            )
            # Calculate end time
            booking_end = booking_start + timedelta(hours=self.duration_hours)
            # Check if end time is in the future
            return booking_end > datetime.now()
        except Exception:
            # If parsing fails, consider it not future
            return False
    
    @property
    def formatted_cancellation_at(self) -> str:
        """Format cancellation timestamp as dd-mmm-yyyy hh:mm:ss AM/PM"""
        if not self.cancellation_at or self.cancellation_at == "":
            return ""
        
        try:
            from datetime import datetime
            # Try parsing ISO format
            if "T" in self.cancellation_at:
                dt = datetime.fromisoformat(self.cancellation_at.replace("Z", "+00:00"))
            else:
                # Try standard format
                dt = datetime.strptime(self.cancellation_at, "%Y-%m-%d %H:%M:%S")
            
            # Format as dd-mmm-yyyy hh:mm:ss AM/PM
            return dt.strftime("%d-%b-%Y %I:%M:%S %p")
        except Exception:
            # If parsing fails, return original
            return self.cancellation_at
    
    @property
    def is_reschedulable(self) -> bool:
        """Check if booking can be rescheduled (MORE than 24 hours before start time)"""
        try:
            from datetime import datetime
            import logging
            
            # Parse booking start time
            booking_start = datetime.strptime(
                f"{self.start_date} {self.start_time}", 
                "%Y-%m-%d %H:%M"
            )
            # Check if booking is MORE than 24 hours away (not equal to)
            current_time = datetime.now()
            time_until_booking = booking_start - current_time
            hours_until = time_until_booking.total_seconds() / 3600
            
            result = hours_until > 24.0
            
            # Debug logging
            logging.info(f"Booking {self.id}: {self.start_date} {self.start_time} | Hours until: {hours_until:.2f} | Reschedulable: {result}")
            
            return result  # Strict > instead of >=
        except Exception as e:
            import logging
            logging.error(f"Error checking is_reschedulable for booking {self.id}: {e}")
            # If parsing fails, don't allow rescheduling
            return False