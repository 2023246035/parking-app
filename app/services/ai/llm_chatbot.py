"""
Advanced LLM-Powered Chatbot for ParkMyCar
Uses OpenAI GPT for natural language understanding and booking creation
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
import reflex as rx
from sqlmodel import select
from app.db.models import ParkingLot, Booking, User

# Load environment variables
load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
USE_LLM = bool(OPENAI_API_KEY)  # Only use LLM if API key is set


class LLMChatbot:
    """Advanced chatbot with natural language understanding"""
    
    @staticmethod
    async def generate_response(
        user_message: str,
        user_id: Optional[int] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Generate intelligent response using LLM or fallback to rule-based
        
        Returns: {
            "response": str,
            "intent": str,
            "actions": List[Dict],
            "suggestions": List[str],
            "booking_data": Optional[Dict]  # If creating booking
        }
        """
        
        if USE_LLM and OPENAI_API_KEY:
            return await LLMChatbot._generate_llm_response(
                user_message, user_id, conversation_history
            )
        else:
            # Fallback to enhanced rule-based system
            return await LLMChatbot._generate_rule_based_response(
                user_message, user_id
            )
    
    @staticmethod
    async def _generate_llm_response(
        user_message: str,
        user_id: Optional[int],
        conversation_history: Optional[List[Dict]]
    ) -> Dict:
        """Generate response using OpenAI GPT"""
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            
            # Build context with parking data
            context = await LLMChatbot._build_context(user_id)
            
            # Build conversation for GPT
            messages = [
                {
                    "role": "system",
                    "content": f"""You are an intelligent parking assistant for ParkMyCar.

CONTEXT:
{context}

CAPABILITIES:
- Search for parking lots by location, price, rating
- Check real-time availability
- Help users book parking (collect: location, date, time, duration, vehicle)
- Answer questions about parking lots
- Provide recommendations

RESPONSE FORMAT:
Always respond in a friendly, helpful manner. If helping with booking, ask for missing details one at a time.

BOOKING STEPS:
1. Ask for location/parking lot
2. Ask for date
3. Ask for time
4. Ask for duration (hours)  
5. Ask for vehicle number
6. Confirm and create booking

Extract any booking details from user messages into JSON format.
"""
                }
            ]
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history[-5:])  # Last 5 messages
            
            # Add current message
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            
            # Parse response for booking intent
            booking_data = LLMChatbot._extract_booking_data(
                user_message, ai_response
            )
            
            # Determine intent
            intent = LLMChatbot._determine_intent_llm(user_message, ai_response)
            
            return {
                "response": ai_response,
                "intent": intent,
                "actions": [],
                "suggestions": LLMChatbot._generate_suggestions(intent),
                "booking_data": booking_data
            }
            
        except Exception as e:
            logging.exception(f"LLM error: {e}")
            # Fallback to rule-based
            return await LLMChatbot._generate_rule_based_response(user_message, user_id)
    
    @staticmethod
    async def _build_context(user_id: Optional[int]) -> str:
        """Build context about available parking for LLM"""
        context_parts = []
        
        with rx.session() as session:
            # Get available lots
            lots = session.exec(
                select(ParkingLot)
                .where(ParkingLot.available_spots > 0)
                .limit(10)
            ).all()
            
            if lots:
                context_parts.append("AVAILABLE PARKING LOTS:")
                for lot in lots:
                    context_parts.append(
                        f"- {lot.name} in {lot.location}: "
                        f"RM {lot.price_per_hour}/hr, "
                        f"{lot.available_spots} spots, "
                        f"Rating: {lot.rating}⭐"
                    )
            
            # Get user's booking history if available
            if user_id:
                recent_bookings = session.exec(
                    select(Booking)
                    .where(Booking.user_id == user_id)
                    .order_by(Booking.created_at.desc())
                    .limit(3)
                ).all()
                
                if recent_bookings:
                    context_parts.append("\nUSER'S RECENT BOOKINGS:")
                    for booking in recent_bookings:
                        lot = session.get(ParkingLot, booking.lot_id)
                        if lot:
                            context_parts.append(
                                f"- {lot.name}: {booking.start_date} at {booking.start_time}"
                            )
        
        return "\n".join(context_parts)
    
    @staticmethod
    def _extract_booking_data(user_message: str, ai_response: str) -> Optional[Dict]:
        """Extract booking details from conversation"""
        booking_data = {}
        message_lower = user_message.lower()
        
        # Extract location
        if "near" in message_lower or "at" in message_lower or "in" in message_lower:
            # Try to extract location
            words = user_message.split()
            for i, word in enumerate(words):
                if word.lower() in ["near", "at", "in"] and i + 1 < len(words):
                    booking_data["location"] = " ".join(words[i+1:i+3])
                    break
        
        # Extract date (today, tomorrow, specific date)
        if "today" in message_lower:
            booking_data["date"] = datetime.now().strftime("%Y-%m-%d")
        elif "tomorrow" in message_lower:
            from datetime import timedelta
            booking_data["date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Extract time (9am, 14:00, etc.)
        import re
        time_patterns = [
            r'\b(\d{1,2}):(\d{2})\b',  # 14:30
            r'\b(\d{1,2})\s*(am|pm)\b',  # 9am, 2pm
        ]
        for pattern in time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                booking_data["time"] = match.group(0)
                break
        
        # Extract duration
        duration_match = re.search(r'(\d+)\s*hour', message_lower)
        if duration_match:
            booking_data["duration"] = int(duration_match.group(1))
        
        # Extract vehicle number (alphanumeric)
        vehicle_match = re.search(r'\b([A-Z0-9]{3,10})\b', user_message.upper())
        if vehicle_match:
            potential_vehicle = vehicle_match.group(1)
            # Avoid common words
            if potential_vehicle not in ["PARKING", "HOURS", "TODAY", "TOMORROW"]:
                booking_data["vehicle_number"] = potential_vehicle
        
        return booking_data if booking_data else None
    
    @staticmethod
    def _determine_intent_llm(user_message: str, ai_response: str) -> str:
        """Determine user intent from LLM conversation"""
        message_lower = user_message.lower()
        response_lower = ai_response.lower()
        
        # Check for booking intent
        book_keywords = ["book", "reserve", "parking", "spot", "need parking"]
        if any(kw in message_lower for kw in book_keywords):
            return "book"
        
        # Check for availability check
        if any(kw in message_lower for kw in ["available", "free", "check"]):
            return "check_availability"
        
        # Check for pricing
        if any(kw in message_lower for kw in ["price", "cost", "cheap", "expensive"]):
            return "pricing"
        
        # Check for information
        if any(kw in message_lower for kw in ["info", "about", "tell me", "details"]):
            return "get_info"
        
        # Check for help
        if any(kw in message_lower for kw in ["help", "how", "what can"]):
            return "help"
        
        return "general"
    
    @staticmethod
    def _generate_suggestions(intent: str) -> List[str]:
        """Generate contextual suggestions"""
        suggestions_map = {
            "book": [
                "Find parking near KLCC",
                "Show cheapest options",
                "Book for tomorrow 9am"
            ],
            "check_availability": [
                "Show available spots",
                "Check availability near me"
            ],
            "pricing": [
                "Compare all prices",
                "Show cheapest parking"
            ],
            "help": [
                "How do I book?",
                "Show my bookings"
            ],
            "general": [
                "Find parking",
                "Check availability",
                "Show prices"
            ]
        }
        
        return suggestions_map.get(intent, suggestions_map["general"])
    
    @staticmethod
    async def _generate_rule_based_response(
        user_message: str,
        user_id: Optional[int]
    ) -> Dict:
        """Enhanced rule-based fallback (improved from original)"""
        from app.services.ai.chatbot_ai import ParkingChatbot
        
        # Use existing chatbot as fallback
        response_data = await ParkingChatbot.generate_response(user_message, user_id)
        
        # Add booking data extraction
        booking_data = LLMChatbot._extract_booking_data(user_message, "")
        response_data["booking_data"] = booking_data
        
        return response_data
    
    @staticmethod
    async def create_booking_from_chat(
        booking_data: Dict,
        user_id: int
    ) -> Dict:
        """
        Create a booking from chatbot conversation
        
        booking_data should contain:
        - location or lot_id
        - date
        - time
        - duration
        - vehicle_number
        """
        try:
            with rx.session() as session:
                # Find parking lot
                if "lot_id" in booking_data:
                    lot = session.get(ParkingLot, booking_data["lot_id"])
                elif "location" in booking_data:
                    lot = session.exec(
                        select(ParkingLot)
                        .where(
                            (ParkingLot.name.contains(booking_data["location"])) |
                            (ParkingLot.location.contains(booking_data["location"]))
                        )
                        .where(ParkingLot.available_spots > 0)
                        .limit(1)
                    ).first()
                else:
                    return {"success": False, "error": "No location specified"}
                
                if not lot:
                    return {"success": False, "error": "Parking lot not found or full"}
                
                # Validate required fields
                required_fields = ["date", "time", "duration", "vehicle_number"]
                missing = [f for f in required_fields if f not in booking_data]
                if missing:
                    return {
                        "success": False,
                        "error": f"Missing required fields: {', '.join(missing)}"
                    }
                
                # Get available slot
                occupied_slots = [b.slot_id for b in session.exec(
                    select(Booking)
                    .where(Booking.lot_id == lot.id)
                    .where(Booking.start_date == booking_data["date"])
                    .where(Booking.status.in_(["Confirmed", "Pending"]))
                ).all()]
                
                all_slots = [f"A{i}" for i in range(1, 11)] + [f"B{i}" for i in range(1, 11)]
                available_slots = [s for s in all_slots if s not in occupied_slots]
                
                if not available_slots:
                    return {"success": False, "error": "No slots available"}
                
                slot_id = available_slots[0]
                
                # Calculate price
                total_price = lot.price_per_hour * booking_data["duration"]
                
                # Get user
                user = session.get(User, user_id)
                if not user:
                    return {"success": False, "error": "User not found"}
                
                # Create booking
                booking = Booking(
                    user_id=user_id,
                    lot_id=lot.id,
                    start_date=booking_data["date"],
                    start_time=booking_data["time"],
                    duration_hours=booking_data["duration"],
                    slot_id=slot_id,
                    vehicle_number=booking_data["vehicle_number"],
                    phone_number=user.phone or "0000000000",
                    total_price=total_price,
                    status="Confirmed",
                    payment_status="Paid",
                    transaction_id=f"CHAT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{user_id}"
                )
                
                session.add(booking)
                
                # Update availability
                lot.available_spots -= 1
                session.add(lot)
                
                session.commit()
                session.refresh(booking)
                
                # Send confirmation email
                try:
                    from app.services.email_service import send_booking_confirmation_email
                    send_booking_confirmation_email(
                        user.email,
                        {
                            "user_name": user.full_name,
                            "lot_name": lot.name,
                            "start_date": booking.start_date,
                            "start_time": booking.start_time,
                            "duration": booking.duration_hours,
                            "slot_id": slot_id,
                            "vehicle_number": booking.vehicle_number,
                            "total_price": total_price
                        }
                    )
                except Exception as e:
                    logging.warning(f"Email send failed: {e}")
                
                return {
                    "success": True,
                    "booking_id": booking.id,
                    "slot": slot_id,
                    "price": total_price,
                    "lot_name": lot.name
                }
                
        except Exception as e:
            logging.exception(f"Booking creation error: {e}")
            return {"success": False, "error": str(e)}
