"""
Enhanced AI Chatbot Assistant for Parking Bookings
High-performance with caching and better intent detection
"""

import reflex as rx
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlmodel import select
from app.db.models import ParkingLot, Booking, User
import logging


class ChatbotCache:
    """Simple cache for frequently accessed data"""
    _cache = {}
    _cache_time = {}
    CACHE_DURATION = 60  # seconds
    
    @classmethod
    def get(cls, key: str):
        """Get from cache if not expired"""
        if key in cls._cache:
            if (datetime.now() - cls._cache_time[key]).seconds < cls.CACHE_DURATION:
                return cls._cache[key]
        return None
    
    @classmethod
    def set(cls, key: str, value):
        """Set cache with timestamp"""
        cls._cache[key] = value
        cls._cache_time[key] = datetime.now()


class ParkingChatbot:
    """Enhanced AI-powered chatbot for parking assistance"""

    # Enhanced intent detection with better keywords
    INTENTS = {
        "book": ["book", "reserve", "parking", "spot", "need", "want", "find", "search", "looking for"],
        "check_availability": ["available", "free", "spots", "spaces", "check", "vacancy", "open", "empty"],
        "get_info": ["info", "information", "details", "about", "price", "location", "tell me", "what is", "how much"],
        "my_bookings": ["my booking", "my reservation", "show booking", "view booking", "my spots"],
        "cancel": ["cancel", "remove", "delete", "refund"],
        "pricing": ["price", "cost", "cheap", "expensive", "rate", "fee"],
        "help": ["help", "what can you do", "how", "assist", "commands"],
        "greeting": ["hi", "hello", "hey", "good morning", "good afternoon", "sup", "yo"]
    }

    @staticmethod
    def detect_intent(user_message: str) -> str:
        """Enhanced intent detection with priority"""
        message_lower = user_message.lower()

        # Priority order - more specific intents first
        intent_priority = ["pricing", "book", "check_availability", "my_bookings", "cancel", "get_info", "help", "greeting"]
        
        for intent in intent_priority:
            keywords = ParkingChatbot.INTENTS.get(intent, [])
            if any(keyword in message_lower for keyword in keywords):
                return intent

        return "unknown"

    @staticmethod
    def extract_location(user_message: str) -> Optional[str]:
        """Enhanced location extraction"""
        message_lower = user_message.lower()
        
        exclude_words = {
            "parking", "lot", "lots", "spot", "spots", "space", "spaces",
            "book", "reserve", "find", "show", "check", "available",
            "need", "want", "looking", "search", "where", "can", "i", "the", "a", "an"
        }
        
        location_indicators = ["near", "at", "in", "around", "by", "close to"]
        
        for indicator in location_indicators:
            if indicator in message_lower:
                parts = message_lower.split(indicator)
                if len(parts) > 1:
                    potential_location = parts[1].strip().strip("?.,!")
                    words = potential_location.split()
                    
                    # Take up to 5 words for full location names
                    location_words = []
                    for word in words[:5]:
                        if word not in exclude_words:
                            location_words.append(word)
                        else:
                            break  # Stop at first generic word
                    
                    if location_words:
                        return " ".join(location_words)

        return None

    @staticmethod
    async def generate_response(
        user_message: str,
        user_id: Optional[int] = None,
        conversation_id: Optional[str] = None
    ) -> Dict:
        """
        Generate enhanced chatbot response
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
                    "👋 **Hello! Welcome to ParkMyCar's AI Assistant**\n\n"
                    "I'm here to make parking effortless! I can help you:\n\n"
                    "• 🅿️ **Find & book** parking spots instantly\n"
                    "• 📊 **Check live availability** across all locations\n"
                    "• 💰 **Compare prices** and find the best deals\n"
                    "• ℹ️ **Get detailed info** about parking lots\n"
                    "• 📋 **Manage your bookings** (view, track, cancel)\n\n"
                    "**Just tell me what you need!** 🚗"
                )
                response_data["suggestions"] = [
                    "Find parking near KLCC",
                    "Show cheapest spots",
                    "Check availability"
                ]

            elif intent == "pricing":
                # Check cache first
                cache_key = "all_lots_pricing"
                lots = ChatbotCache.get(cache_key)
                
                if not lots:
                    with rx.session() as session:
                        lots = session.exec(
                            select(ParkingLot)
                            .where(ParkingLot.available_spots > 0)
                            .order_by(ParkingLot.price_per_hour)
                            .limit(5)
                        ).all()
                        ChatbotCache.set(cache_key, lots)

                if lots:
                    cheapest = lots[0]
                    response_data["response"] = "💰 **Parking Pricing Overview:**\n\n"
                    
                    for i, lot in enumerate(lots, 1):
                        emoji = "🏆" if i == 1 else "⭐" if i == 2 else "📍"
                        response_data["response"] += (
                            f"{emoji} **{lot.name}**\n"
                            f"💵 **RM {lot.price_per_hour}/hour**\n"
                            f"📍 {lot.location}\n"
                            f"🅿️ {lot.available_spots} spots available\n\n"
                        )
                    
                    response_data["response"] += (
                        f"\n🎯 **Best Deal:** {cheapest.name} at **RM {cheapest.price_per_hour}/hr**\n\n"
                        f"📌 [View all listings](/listings) to book!"
                    )
                else:
                    response_data["response"] = "😔 No parking available at the moment. Please check back later!"

            elif intent == "book":
                location = ParkingChatbot.extract_location(user_message)
                
                if location:
                    cache_key = f"location_{location}"
                    lots = ChatbotCache.get(cache_key)
                    
                    if not lots:
                        with rx.session() as session:
                            lots = session.exec(
                                select(ParkingLot)
                                .where(
                                    (ParkingLot.location.contains(location)) | 
                                    (ParkingLot.name.contains(location))
                                )
                                .where(ParkingLot.available_spots > 0)
                                .order_by(ParkingLot.rating.desc())
                                .limit(4)
                            ).all()
                            ChatbotCache.set(cache_key, lots)

                    if lots:
                        response_data["response"] = f"🎯 **Found {len(lots)} available spot(s) matching '{location}':**\n\n"
                        
                        for i, lot in enumerate(lots, 1):
                            occupancy = int((lot.total_spots - lot.available_spots) / lot.total_spots * 100) if lot.total_spots > 0 else 0
                            
                            if occupancy < 30:
                                status = "🟢 **Low**"
                            elif occupancy < 70:
                                status = "🟡 **Medium**"
                            else:
                                status = "🔴 **High**"
                            
                            response_data["response"] += (
                                f"**{i}. {lot.name}**\n"
                                f"📍 {lot.location}\n"
                                f"💰 RM {lot.price_per_hour}/hr · "
                                f"🅿️ {lot.available_spots}/{lot.total_spots} free\n"
                                f"📊 Occupancy: {status} ({occupancy}%)\n"
                                f"⭐ Rating: {lot.rating}/5.0\n\n"
                            )

                        response_data["response"] += "✅ **Ready to book?** Visit the [Listings Page](/listings)!"
                    else:
                        response_data["response"] = (
                            f"😕 **No available parking found near '{location}'**\n\n"
                            "**Suggestions:**\n"
                            "• Try a different area (e.g., 'near Sunway', 'at KLCC')\n"
                            "• Check [all available lots](/listings)\n"
                            "• Be more specific with location"
                        )
                else:
                    # No location - show top available
                    cache_key = "top_available"
                    lots = ChatbotCache.get(cache_key)
                    
                    if not lots:
                        with rx.session() as session:
                            lots = session.exec(
                                select(ParkingLot)
                                .where(ParkingLot.available_spots > 0)
                                .order_by(ParkingLot.rating.desc())
                                .limit(5)
                            ).all()
                            ChatbotCache.set(cache_key, lots)

                    if lots:
                        response_data["response"] = "🌟 **Top Available Parking Lots:**\n\n"
                        
                        for i, lot in enumerate(lots, 1):
                            response_data["response"] += (
                                f"**{i}. {lot.name}** ⭐{lot.rating}\n"
                                f"📍 {lot.location}\n"
                                f"💰 RM {lot.price_per_hour}/hr | "
                                f"🅿️ {lot.available_spots} spots\n\n"
                            )
                        
                        response_data["response"] += (
                            "\n💡 **Pro Tip:** Specify location for better results!\n"
                            "_Example: 'Find parking near Sunway'_\n\n"
                            "📌 [Browse all lots](/listings)"
                        )

            elif intent == "check_availability":
                cache_key = "availability_check"
                lots = ChatbotCache.get(cache_key)
                
                if not lots:
                    with rx.session() as session:
                        all_lots = session.exec(select(ParkingLot)).all()
                        available_lots = [l for l in all_lots if l.available_spots > 0]
                        total_available = sum(l.available_spots for l in available_lots)
                        
                        lots = {
                            "all": all_lots,
                            "available": available_lots,
                            "total_available": total_available
                        }
                        ChatbotCache.set(cache_key, lots)

                response_data["response"] = (
                    "📊 **Real-Time Parking Availability:**\n\n"
                    f"🅿️ **{lots['total_available']} spots** available across **{len(lots['available'])} locations**\n\n"
                    "**Top Locations:**\n\n"
                )

                for lot in sorted(lots['available'], key=lambda x: x.available_spots, reverse=True)[:5]:
                    avail_percent = (lot.available_spots / lot.total_spots * 100) if lot.total_spots > 0 else 0
                    emoji = "🟢" if avail_percent > 50 else "🟡" if avail_percent > 20 else "🔴"
                    
                    response_data["response"] += (
                        f"{emoji} **{lot.name}**\n"
                        f"   📍 {lot.location}\n"
                        f"   🅿️ {lot.available_spots}/{lot.total_spots} spots free\n"
                        f"   💰 RM {lot.price_per_hour}/hr\n\n"
                    )

                response_data["response"] += "\n📌 [View full listings](/listings)"

            elif intent == "help":
                response_data["response"] = (
                    "🤖 **AI Parking Assistant - Quick Guide**\n\n"
                    "**🅿️ Find Parking:**\n"
                    "_'Find parking near KLCC'_\n"
                    "_'Show spots in Sunway'_\n\n"
                    "**📊 Check Availability:**\n"
                    "_'What's available?'_\n"
                    "_'Show availability'_\n\n"
                    "**💰 Compare Prices:**\n"
                    "_'Show prices'_\n"
                    "_'Cheapest parking'_\n\n"
                    "**ℹ️ Get Details:**\n"
                    "_'Tell me about [lot name]'_\n\n"
                    "**📋 Your Bookings:**\n"
                    "_'Show my bookings'_ (login required)\n\n"
                    "**Just type naturally - I'll understand!** 😊"
                )
                response_data["suggestions"] = [
                    "Find parking near me",
                    "Show cheapest spots",
                    "Check availability"
                ]

            else:
                response_data["response"] = (
                    "🤔 **Hmm, I didn't quite understand that.**\n\n"
                    "**Try asking me to:**\n"
                    "• 🅿️ Find parking (e.g., 'near KLCC')\n"
                    "• 📊 Check availability\n"
                    "• 💰 Compare prices\n"
                    "• ℹ️ Get lot information\n"
                    "• ❓ Type 'help' for more examples\n\n"
                    "**Or just describe what you need!**"
                )
                response_data["suggestions"] = [
                    "Find parking",
                    "Check availability",
                    "Help"
                ]

        except Exception as e:
            logging.exception(f"Chatbot error: {e}")
            response_data["response"] = (
                "⚠️ **Oops! I encountered an error.**\n\n"
                "Please try rephrasing your question or refresh the page.\n\n"
                f"_Error: {str(e)}_"
            )

        return response_data
