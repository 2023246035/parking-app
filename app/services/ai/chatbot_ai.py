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

    # MASSIVELY EXPANDED INTENT KEYWORDS - COMPREHENSIVE COVERAGE
    INTENTS = {
        # 1. BOOKING INTENT - Super Expanded
        "book": [
            # Original
            "book", "reserve", "parking", "spot", "need", "want", "find", "search", "looking for",
            "near me", "nearby", "location", "give", "show me", "list", "get", "where",
            # NEW - Availability variations
            "available", "availability", "free slots", "open spots", "find parking",
            # NEW - Proximity
            "closest", "nearest", "around me", "close to me", "near my place", "near my location",
            # NEW - Suggestions
            "any parking", "suggest", "recommend", "best spot", "find lot", "look for parking",
            # NEW - Actions
            "park", "parking place", "search parking", "any slots", "give options",
            # NEW - Current status
            "latest availability", "current availability"
        ],
        
        # 2. CHECK AVAILABILITY INTENT - Enhanced
        "check_availability": [
            "available", "free", "spots", "spaces", "check", "vacancy", "open", "empty", "any",
            # NEW
            "available now", "availability", "any empty", "any free", "is parking free",
            "is slot free", "show free spots", "free now", "any space", "any vacancy"
        ],
        
        # 3. PRICING INTENT - Comprehensive
        "pricing": [
            "price", "cost", "cheap", "expensive", "rate", "fee", "cheapest", "affordable",
            # NEW
            "pricing", "charges", "how much", "per hour", "price list", "low price",
            "budget", "cheap parking", "compare prices", "best price"
        ],
        
        # 4. LOCATION INTENT - NEW!
        "location": [
            "address", "where is", "location list", "map", "directions", "how to reach",
            "show map", "display locations", "lot locations", "parking locations",
            "route to parking", "navigate", "gps", "coordinates"
        ],
        
        # 5. MY BOOKINGS INTENT
        "my_bookings": [
            "my booking", "my reservation", "show booking", "view booking", "my spots",
            "my history", "past bookings", "upcoming bookings", "booking history"
        ],
        
        # 6. CANCEL INTENT - Enhanced
        "cancel": [
            "cancel", "remove", "delete",
            # NEW
            "cancel booking", "stop booking", "undo booking", "remove booking",
            "delete booking", "close booking", "cancel my slot", "cancel reservation"
        ],
        
        # 7. REFUND INTENT - NEW!
        "refund": [
            "refund", "money back", "refund status", "how much refund", "refund amount",
            "refund policy", "eligible for refund", "cancel refund", "my refund",
            "why refund", "when refund", "get money back", "return money"
        ],
        
        # 8. HELP INTENT - Comprehensive
        "help": [
            "help", "what can you do", "how", "assist", "commands", "guide", "options",
            # NEW
            "how it works", "instructions", "explain", "features", "support",
            "show menu", "what options", "tell me options", "what services",
            "how to book", "help me", "tutorial", "faq"
        ],
        
        # 9. GET INFO INTENT
        "get_info": [
            "info", "information", "details", "about", "tell me", "what is", "how much",
            "description", "overview", "specifics"
        ],
        
        # 10. ADMIN INTENT - NEW!
        "admin": [
            "admin login", "dashboard", "manage users", "view bookings", "update price",
            "add lot", "delete lot", "admin help", "analytics", "reports",
            "admin panel", "management", "admin access"
        ],
        
        # 11. GREETING Intent - Expanded
        "greeting": [
            "hi", "hello", "hey", "good morning", "good afternoon", "sup", "yo", "howdy",
            # NEW
            "good evening", "how are you", "greetings", "hi there", "hello there"
        ],
        
        # 12. ACKNOWLEDGMENT Intent
        "acknowledgment": [
            "ok", "okay", "thanks", "thank you", "alright", "got it", "noted", "fine", "cool",
            # NEW
            "thank you very much", "appreciate it", "understood"
        ],
        
        # 13. FAREWELL Intent - NEW!
        "farewell": [
            "bye", "goodbye", "see you", "later", "exit", "quit", "done", "that's all",
            "thank you bye", "thanks bye"
        ],
        
        # 14. ABOUT APP Intent
        "about_app": [
            "about", "what is this", "tell me about", "app info", "how does this work",
            "explain", "what app", "app details"
        ],
        
        # 15. POSITIVE Intent
        "positive": [
            "yes", "yep", "yeah", "sure", "confirm", "correct", "right", "absolutely",
            "definitely", "agreed", "proceed"
        ],
        
        # 16. NEGATIVE SENTIMENT Intent - NEW!
        "negative_sentiment": [
            "bad", "not working", "issue", "problem", "error", "angry", "upset",
            "why not", "complaint", "fix this", "useless", "hate", "terrible",
            "disappointed", "frustrating", "broken"
        ],
        
        # 17. NEGATIVE Response Intent (regular no)
        "negative": [
            "no", "nope", "nah", "stop", "nevermind", "not interested", "decline"
        ]
    }

    @staticmethod
    def detect_intent(user_message: str) -> str:
        """Enhanced intent detection with priority"""
        message_lower = user_message.lower().strip()
        
        # Handle very short messages
        if len(message_lower) <= 2:
            if message_lower in ["hi", "yo"]:
                return "greeting"
            elif message_lower in ["ok", "k"]:
                return "acknowledgment"
            return "unknown"

        # Priority order - more specific intents first
        intent_priority = [
            "greeting", "acknowledgment", "positive", "negative",
            "about_app", "pricing", "book", "check_availability", 
            "my_bookings", "cancel", "get_info", "help"
        ]
        
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

            elif intent == "acknowledgment":
                response_data["response"] = (
                    "👍 **Great!**\n\n"
                    "Is there anything else I can help you with?\n\n"
                    "You can:\n"
                    "• Find parking spots\n"
                    "• Check availability\n"
                    "• Compare prices\n"
                    "• View your bookings"
                )
                response_data["suggestions"] = [
                    "Find parking",
                    "Check availability",
                    "Show my bookings"
                ]

            elif intent == "about_app":
                response_data["response"] = (
                   "🚗 **About ParkMyCar**\n\n"
                    "ParkMyCar is your smart parking assistant that makes finding and booking parking spots effortless!\n\n"
                    "**🎯 Key Features:**\n"
                    "• **Smart Search** - Find parking by location, price, or rating\n"
                    "• **Real-time Availability** - See live spots across all locations\n"
                    "• **Multi-Slot Booking** - Book multiple slots at once\n"
                    "• **QR Codes** - Easy check-in with QR codes\n"
                    "• **Auto-Booking** - Set up recurring bookings\n"
                    "• **Price Comparison** - Find the best deals\n"
                    "• **Email Reminders** - Never miss your booking\n\n"
                    "**💡 How it works:**\n"
                    "1. Browse available parking lots\n"
                    "2. Select date, time & slot\n"
                    "3. Enter vehicle details\n"
                    "4. Pay securely\n"
                    "5. Get confirmation & QR code!\n\n"
                    "**Ready to find parking?** 🅿️"
                )
                response_data["suggestions"] = [
                    "Find parking",
                    "Check availability",
                    "Show prices"
                ]

            elif intent == "positive":
                response_data["response"] = (
                    "✅ **Perfect!**\n\n"
                    "How can I assist you further?\n\n"
                    "Try asking:\n"
                    "• 'Find parking near [location]'\n"
                    "• 'Show available spots'\n"
                    "• 'Compare prices'"
                )
                response_data["suggestions"] = [
                    "Find parking",
                    "Check availability"
                ]

            elif intent == "negative":
                response_data["response"] = (
                    "👌 **No problem!**\n\n"
                    "Let me know if you change your mind or need anything else.\n\n"
                    "I'm here to help! 😊"
                )
                response_data["suggestions"] = [
                    "Find parking",
                    "Help"
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
