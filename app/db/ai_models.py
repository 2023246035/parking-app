"""
AI Feature Models for Parking System
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class UserPreference(SQLModel, table=True):
    """User preferences for personalized recommendations."""
    __tablename__ = "userpreference"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    preferred_locations: Optional[str] = None
    preferred_price_min: Optional[float] = None
    preferred_price_max: Optional[float] = None
    preferred_amenities: Optional[str] = None
    booking_frequency: str = Field(default="occasional")
    average_duration: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "user_id": self.user_id,
            "preferred_locations": json.loads(self.preferred_locations) if self.preferred_locations else [],
            "preferred_price_min": self.preferred_price_min,
            "preferred_price_max": self.preferred_price_max,
            "preferred_amenities": json.loads(self.preferred_amenities) if self.preferred_amenities else [],
            "booking_frequency": self.booking_frequency,
            "average_duration": self.average_duration,
        }


class PricingHistory(SQLModel, table=True):
    """Track pricing history for dynamic pricing analysis."""
    __tablename__ = "pricinghistory"

    id: Optional[int] = Field(default=None, primary_key=True)
    parking_lot_id: int = Field(foreign_key="parkinglot.id", index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
    base_price: float
    dynamic_price: float
    occupancy_rate: float
    demand_multiplier: float = Field(default=1.0)
    time_multiplier: float = Field(default=1.0)
    event_multiplier: float = Field(default=1.0)
    factors: Optional[str] = None

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "parking_lot_id": self.parking_lot_id,
            "timestamp": self.timestamp.isoformat(),
            "base_price": self.base_price,
            "dynamic_price": self.dynamic_price,
            "occupancy_rate": self.occupancy_rate,
            "factors": json.loads(self.factors) if self.factors else {},
        }


class AutoBookingSetting(SQLModel, table=True):
    """User settings for auto-booking agent."""
    __tablename__ = "autobookingsetting"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    enabled: bool = Field(default=False)
    preferred_lot_ids: Optional[str] = None
    schedule_patterns: Optional[str] = None
    max_price_threshold: Optional[float] = None
    notification_before_minutes: int = Field(default=30)
    auto_confirm: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "user_id": self.user_id,
            "enabled": self.enabled,
            "preferred_lot_ids": json.loads(self.preferred_lot_ids) if self.preferred_lot_ids else [],
            "schedule_patterns": json.loads(self.schedule_patterns) if self.schedule_patterns else {},
            "max_price_threshold": self.max_price_threshold,
            "notification_before_minutes": self.notification_before_minutes,
            "auto_confirm": self.auto_confirm,
        }


class ChatbotConversation(SQLModel, table=True):
    """Store chatbot conversations for context and training."""
    __tablename__ = "chatbotconversation"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: str = Field(unique=True, index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    messages: str
    intent: Optional[str] = None
    resolved: bool = Field(default=False)
    rating: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "messages": json.loads(self.messages) if self.messages else [],
            "intent": self.intent,
            "resolved": self.resolved,
            "rating": self.rating,
            "created_at": self.created_at.isoformat(),
        }


class RecommendationScore(SQLModel, table=True):
    """Cache recommendation scores for users."""
    __tablename__ = "recommendationscore"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    parking_lot_id: int = Field(foreign_key="parkinglot.id", index=True)
    score: float
    factors: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "user_id": self.user_id,
            "parking_lot_id": self.parking_lot_id,
            "score": self.score,
            "factors": json.loads(self.factors) if self.factors else {},
            "last_updated": self.last_updated.isoformat(),
        }
