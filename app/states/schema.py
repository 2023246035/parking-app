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
    cancellation_reason: str = ""
    cancellation_at: str = ""
    slot_id: str = ""
    vehicle_number: str = ""
    phone_number: str = ""