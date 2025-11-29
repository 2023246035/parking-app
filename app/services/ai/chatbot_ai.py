"""
AI Chatbot Assistant for Parking Bookings
Uses OpenAI/Anthropic for natural language understanding and booking assistance
"""

import reflex as rx
from datetime import datetime
from typing import List, Dict, Optional
import json
import uuid
from sqlmodel import select
from app.db.models import ParkingLot, Booking, User
from app.db.ai_models import ChatbotConversation


class ParkingChatbot:
    """AI-powered chatbot for parking assistance"""

    # For now, we'll use rule-based NLU
    # In production, integrate with OpenAI/Claude API

    INTENTS = {
        "book": ["book", "reserve", "parking", "spot", "need"],
        "check_availability": ["available", "free", "spots", "spaces", "check"],
        "get_info": ["info", "information", "details", "about", "price", "location"],
        "cancel": ["cancel", "remove", "delete"],
        "help": ["help", "what can you do", "how"],
        "greeting": ["hi", "hello", "hey"]
    }

    @staticmethod
    def detect_intent(user_message: str) -> str:
        """Simple intent detection (replace with AI model in production)"""
        message_lower = user_message.lower()

        # Check for each intent
        for intent, keywords in ParkingChatbot.INTENTS.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent

        return "unknown"

    @staticmethod
    def extract_location(user_message: str) -> Optional[str]:
        """Extract location from user message"""
        # Simple extraction - look for common location keywords
        message_lower = user_message.lower()
        
        # Common location patterns
        location_indicators = ["in", "at", "near", "around"]
        
        for indicator in location_indicators:
            if indicator in message_lower:
                parts = message_lower.split(indicator)
                if len(parts) > 1:
                    # Get the part after the indicator
                    potential_location = parts[1].strip().split()[0:3]  # Take up to 3 words
                    return " ".join(potential_location).strip(".,!?")

        return None

    @staticmethod
    async def generate_response(
        user_message: str,
        user_id: Optional[int] = None,
        conversation_id: Optional[str] = None
    ) -> Dict:
        """
        Generate chatbot response to user message
        Returns: {response, intent, suggestions, actions}
        """
        intent = ParkingChatbot.detect_intent(user_message)
        response_data = {
            "response": "",
            "intent": intent,
            "suggestions": [],
            "actions": []
        }

        try:
            if intent == "greeting":
                response_data["response"] = (
                    "👋 Hello! I'm your parking assistant. "
                    "I can help you:\n"
                    "• Book parking spots\n"
                    "• Check availability\n"
                    "• Get parking lot information\n"
                    "• Manage your bookings\n\n"
                    "What would you like to do today?"
                )
                response_data["suggestions"] = [
                    "Find parking near downtown",
                    "Check my bookings",
                    "Show available spots"
                ]

            elif intent == "book":
                location = ParkingChatbot.extract_location(user_message)
                
                if location:
                    # Search for parking lots
                    with rx.session() as session:
                        lots = session.exec(
                            select(ParkingLot)
                            .where(ParkingLot.location.contains(location))
                            .where(ParkingLot.available_spots > 0)
                            .limit(3)
                        ).all()

                        if lots:
                            response_data["response"] = f"🅿️ I found  {len(lots)} available parking lot(s) near {location}:\n\n"
                            
                            for i, lot in enumerate(lots, 1):
                                response_data["response"] += (
                                    f"{i}. **{lot.name}**\n"
                                    f"   📍 {lot.location}\n"
                                    f"   💰 RM {lot.price_per_hour}/hour\n"
                                    f"   🅿️ {lot.available_spots}/{lot.total_spots} spots available\n"
                                    f"   ⭐ {lot.rating}/5.0\n\n"
                                )
                                
                                response_data["actions"].append({
                                    "type": "book",
                                    "lot_id": lot.id,
                                    "lot_name": lot.name
                                })

                            response_data["response"] += "Which one would you like to book?"
                            response_data["suggestions"] = [f"Book {lot.name}" for lot in lots]
                        else:
                            response_data["response"] = (
                                f"😔 Sorry, I couldn't find any available parking near {location}. "
                                "Would you like to search in a different area?"
                            )
                else:
                    response_data["response"] = (
                        "I'd be happy to help you book parking! "
                        "Could you tell me where you need parking? "
                        "For example: 'I need parking near downtown' or 'Find parking at Central Plaza'"
                    )

            elif intent == "check_availability":
                with rx.session() as session:
                    lots = session.exec(
                        select(ParkingLot)
                        .where(ParkingLot.available_spots > 0)
                        .order_by(ParkingLot.rating.desc())
                        .limit(5)
                    ).all()

                    if lots:
                        response_data["response"] = "🅿️ Here are the parking lots with availability:\n\n"
                        
                        for lot in lots:
                            availability_percent = (lot.available_spots / lot.total_spots * 100) if lot.total_spots > 0 else 0
                            status_emoji = "🟢" if availability_percent > 50 else "🟡" if availability_percent > 20 else "🔴"
                            
                            response_data["response"] += (
                                f"{status_emoji} **{lot.name}** - {lot.location}\n"
                                f"   {lot.available_spots}/{lot.total_spots} spots | RM {lot.price_per_hour}/hr | {lot.rating}⭐\n\n"
                            )
                    else:
                        response_data["response"] = "😔 Sorry, all parking lots are currently full. Please check back later!"

            elif intent == "get_info":
                if user_id:
                    with rx.session() as session:
                        # Get user's recent bookings
                        bookings = session.exec(
                            select(Booking)
                            .where(Booking.user_id == user_id)
                            .order_by(Booking.created_at.desc())
                            .limit(3)
                        ).all()

                        if bookings:
                            response_data["response"] = "📋 Your recent bookings:\n\n"
                            
                            for booking in bookings:
                                lot = session.get(ParkingLot, booking.lot_id)
                                status_emoji = "✅" if booking.status == "Confirmed" else "⏳" if booking.status == "Pending" else "❌"
                                
                                response_data["response"] += (
                                    f"{status_emoji} **{lot.name if lot else 'Unknown'}**\n"
                                    f"   📅 {booking.start_date} at {booking.start_time}\n"
                                    f"   ⏱️ {booking.duration_hours} hours\n"
                                    f"   💰 RM {booking.total_price}\n"
                                    f"   Status: {booking.status}\n\n"
                                )
                        else:
                            response_data["response"] = "You don't have any bookings yet. Would you like to book a parking spot?"
                            response_data["suggestions"] = ["Find parking near me"]
                else:
                    response_data["response"] = "Please log in to view your booking information."

            elif intent == "help":
                response_data["response"] = (
                    "🤖 **I can help you with:**\n\n"
                    "🅿️ **Finding Parking**\n"
                    "   Say: 'Find parking near downtown' or 'I need parking at Central Mall'\n\n"
                    "📋 **Check Availability**\n"
                    "   Say: 'Show available spots' or 'What's available?'\n\n"
                    "ℹ️ **Get Information**\n"
                    "   Say: 'Show my bookings' or 'Tell me about lot prices'\n\n"
                    "Just type your question naturally, and I'll do my best to help!"
                )

            else:
                response_data["response"] = (
                    "I'm not sure I understood that. Could you rephrase? "
                    "You can ask me to:\n"
                    "• Find parking spots\n"
                    "• Check availability\n"
                    "• View your bookings\n"
                    "• Get information about parking lots"
                )

        except Exception as e:
            print(f"Error generating chatbot response: {e}")
            response_data["response"] = "Sorry, I encountered an error. Please try again."

        # Save conversation
        if conversation_id:
            await ParkingChatbot.save_conversation(
                conversation_id, user_id, user_message, response_data["response"], intent
            )

        return response_data

    @staticmethod
    async def save_conversation(
        conversation_id: str,
        user_id: Optional[int],
        user_message: str,
        bot_response: str,
        intent: str
    ):
        """Save conversation to database"""
        try:
            with rx.session() as session:
                # Check if conversation exists
                conversation = session.exec(
                    select(ChatbotConversation)
                    .where(ChatbotConversation.conversation_id == conversation_id)
                ).first()

                message_obj = {
                    "user": user_message,
                    "bot": bot_response,
                    "timestamp": datetime.utcnow().isoformat()
                }

                if conversation:
                    # Update existing conversation
                    messages = json.loads(conversation.messages) if conversation.messages else []
                    messages.append(message_obj)
                    conversation.messages = json.dumps(messages)
                    conversation.intent = intent
                    conversation.updated_at = datetime.utcnow()
                else:
                    # Create new conversation
                    new_conversation = ChatbotConversation(
                        conversation_id=conversation_id,
                        user_id=user_id,
                        messages=json.dumps([message_obj]),
                        intent=intent
                    )
                    session.add(new_conversation)

                session.commit()

        except Exception as e:
            print(f"Error saving conversation: {e}")

    @staticmethod
    def create_conversation_id() -> str:
        """Generate a unique conversation ID"""
        return str(uuid.uuid4())

    @staticmethod
    async def get_conversation_history(conversation_id: str) -> List[Dict]:
        """Get conversation history"""
        try:
            with rx.session() as session:
                conversation = session.exec(
                    select(ChatbotConversation)
                    .where(ChatbotConversation.conversation_id == conversation_id)
                ).first()

                if conversation and conversation.messages:
                    return json.loads(conversation.messages)

        except Exception as e:
            print(f"Error getting conversation history: {e}")

        return []

    @staticmethod
    async def rate_conversation(conversation_id: str, rating: int):
        """Allow user to rate the chatbot conversation"""
        try:
            with rx.session() as session:
                conversation = session.exec(
                    select(ChatbotConversation)
                    .where(ChatbotConversation.conversation_id == conversation_id)
                ).first()

                if conversation:
                    conversation.rating = rating
                    conversation.resolved = True
                    session.commit()
                    return True

        except Exception as e:
            print(f"Error rating conversation: {e}")

        return False
