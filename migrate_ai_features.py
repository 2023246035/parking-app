"""
Database Migration Script for AI Features
Adds new tables for AI-powered features
"""

import reflex as rx
from sqlmodel import SQLModel
from app.db.models import (
    User, ParkingLot, Booking, Payment, OTPVerification, AuditLog,
    CancellationPolicy
)
from app.db.ai_models import (
    UserPreference, PricingHistory, AutoBookingSetting,
    ChatbotConversation, RecommendationScore
)


def migrate_ai_features():
    """Create AI feature tables in the database"""
    print("Starting AI Features Migration...")
    
    try:
        # Create all tables
        with rx.session() as session:
            # This will create only the new tables that don't exist yet
            SQLModel.metadata.create_all(session.connection())
            session.commit()
        
        print("AI Features Migration Completed Successfully!")
        print("\nNew tables created:")
        print("  - User Preference (for recommendations)")
        print("  - Pricing History (for dynamic pricing)")
        print("  - Auto-Booking Settings (for auto-booking agent)")
        print("  - Chatbot Conversations (for AI chatbot)")
        print("  - Recommendation Scores (for personalized suggestions)")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration Error: {e}")
        return False


if __name__ == "__main__":
    migrate_ai_features()
