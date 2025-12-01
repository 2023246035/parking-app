"""
AI Chatbot Assistant for Parking Bookings
Uses natural language understanding for parking assistance
"""

import reflex as rx
from datetime import datetime
from typing import List, Dict, Optional
from sqlmodel import select
from app.db.models import ParkingLot, Booking, User


class ParkingChatbot:
    """AI-powered chatbot for parking assistance"""

    # Intent detection keywords
    INTENTS = {
        "book": ["book", "reserve", "parking", "spot", "need", "want"],
        "check_availability": ["available", "free", "spots", "spaces", "check", "vacancy"],
        "get_info": ["info", "information", "details", "about", "price", "location", "tell me"],
        "my_bookings": ["my booking", "my reservation", "show booking", "view booking"],
        "cancel": ["cancel", "remove", "delete"],
        "help": ["help", "what can you do", "how", "assist"],
        "greeting": ["hi", "hello", "hey", "good morning", "good afternoon"]
    }

    @staticmethod
    def detect_intent(user_message: str) -> str:
        """Simple intent detection"""
        message_lower = user_message.lower()

        # Check for each intent
        for intent, keywords in ParkingChatbot.INTENTS.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent

        return "unknown"

    @staticmethod
    def extract_location(user_message: str) -> Optional[str]:
        """Extract location from user message"""
        message_lower = user_message.lower()
        
        # Words to exclude from location (generic parking terms)
        exclude_words = {
            "parking", "lot", "lots", "spot", "spots", "space", "spaces",
            "book", "reserve", "find", "show", "check", "available",
            "need", "want", "looking", "search", "where", "can", "i"
        }
        
        # Common location patterns
        location_indicators = ["near", "at", "in", "around", "about"]
        
        for indicator in location_indicators:
            if indicator in message_lower:
                parts = message_lower.split(indicator)
                if len(parts) > 1:
                    # Get the part after the indicator
                    potential_location = parts[1].strip().strip("?.,!")
                    # Take up to 4 words to capture full names
                    words = potential_location.split()[:4]
                    
                    # Filter out generic words
                    filtered_words = [w for w in words if w not in exclude_words]
                    
                    # Only return if we have meaningful location words
                    if filtered_words and len(" ".join(filtered_words)) > 2:
                        return " ".join(filtered_words)

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
                    "👋 **Hello! I'm your Smart Parking Assistant**\n\n"
                    "I can help you with:\n"
                    "• 🅿️ Finding and booking parking spots\n"
                    "• 📊 Checking availability in real-time\n"
                    "• ℹ️ Getting parking lot information (price, location, features)\n"
                    "• 📋 Managing your bookings\n\n"
                    "**How can I assist you today?**"
                )
                response_data["suggestions"] = [
                    "Find parking near Sunway",
                    "Check availability",
                    "Show my bookings"
                ]

            elif intent == "book":
                location = ParkingChatbot.extract_location(user_message)
                
                if location:
                    # Search for parking lots matching the location
                    with rx.session() as session:
                        lots = session.exec(
                            select(ParkingLot)
                            .where(
                                (ParkingLot.location.contains(location)) | 
                                (ParkingLot.name.contains(location))
                            )
                            .where(ParkingLot.available_spots > 0)
                            .limit(3)
                        ).all()

                        if lots:
                            response_data["response"] = f"🅿️ **I found {len(lots)} available parking lot(s) matching '{location}':**\n\n"
                            
                            for i, lot in enumerate(lots, 1):
                                occupancy = int((lot.total_spots - lot.available_spots) / lot.total_spots * 100) if lot.total_spots > 0 else 0
                                status = "🟢 Low" if occupancy < 50 else "🟡 Medium" if occupancy < 80 else "🔴 High"
                                
                                response_data["response"] += (
                                    f"**{i}. {lot.name}**\n"
                                    f"📍 {lot.location}\n"
                                    f"💰 RM {lot.price_per_hour}/hour\n"
                                    f"🅿️ {lot.available_spots}/{lot.total_spots} spots available\n"
                                    f"📊 Occupancy: {status}\n"
                                    f"⭐ {lot.rating}/5.0\n\n"
                                )
                                
                                response_data["actions"].append({
                                    "type": "book",
                                    "lot_id": lot.id,
                                    "lot_name": lot.name
                                })

                            response_data["response"] += "**Ready to book?** Go to the [Listings](/listings) page to make a reservation!"
                            response_data["suggestions"] = ["Tell me more about " + lots[0].name, "Check availability"]
                        else:
                            response_data["response"] = (
                                f"😔 **Sorry, I couldn't find any available parking matching '{location}'.**\n\n"
                                "Try:\n"
                                "• Searching for a different area (e.g., 'near Sunway', 'at KLCC')\n"
                                "• Checking our [all available lots](/listings)"
                            )
                            response_data["suggestions"] = ["Show all parking lots", "Check availability"]
                else:
                    # No specific location - show top available lots
                    with rx.session() as session:
                        lots = session.exec(
                            select(ParkingLot)
                            .where(ParkingLot.available_spots > 0)
                            .order_by(ParkingLot.rating.desc())
                            .limit(5)
                        ).all()

                        if lots:
                            response_data["response"] = "🅿️ **Here are the top available parking lots:**\n\n"
                            
                            for i, lot in enumerate(lots, 1):
                                response_data["response"] += (
                                    f"**{i}. {lot.name}**\n"
                                    f"📍 {lot.location}\n"
                                    f"💰 RM {lot.price_per_hour}/hour | "
                                    f"🅿️ {lot.available_spots}/{lot.total_spots} spots\n\n"
                                )
                            
                            response_data["response"] += (
                                "\n💡 **Tip:** For location-specific results, try:\n"
                                "• 'Find parking near Sunway'\n"
                                "• 'Book parking at KLCC'\n\n"
                                "📌 Visit [Listings](/listings) to book your spot!"
                            )
                            response_data["suggestions"] = ["Tell me about " + lots[0].name]
                        else:
                            response_data["response"] = "😔 **Sorry, all parking lots are currently full.** Please check back later!"


            elif intent == "check_availability":
                with rx.session() as session:
                    lots = session.exec(
                        select(ParkingLot)
                        .where(ParkingLot.available_spots > 0)
                        .order_by(ParkingLot.rating.desc())
                        .limit(5)
                    ).all()

                    if lots:
                        response_data["response"] = "🅿️ **Here are the top parking lots with availability:**\n\n"
                        
                        for lot in lots:
                            availability_percent = (lot.available_spots / lot.total_spots * 100) if lot.total_spots > 0 else 0
                            status_emoji = "🟢" if availability_percent > 50 else "🟡" if availability_percent > 20 else "🔴"
                            
                            response_data["response"] += (
                                f"{status_emoji} **{lot.name}** - {lot.location}\n"
                                f"   💰 RM {lot.price_per_hour}/hr | "
                                f"🅿️ {lot.available_spots}/{lot.total_spots} spots | "
                                f"⭐ {lot.rating}⭐\n\n"
                            )
                        
                        response_data["response"] += "\n📌 Visit [Listings](/listings) to book your spot!"
                    else:
                        response_data["response"] = "😔 **Sorry, all parking lots are currently full.** Please check back later!"

            elif intent == "get_info":
                # Check if asking about a specific place
                location = ParkingChatbot.extract_location(user_message)
                
                if location:
                    # Search for the specific lot
                    with rx.session() as session:
                        lots = session.exec(
                            select(ParkingLot)
                            .where(
                                (ParkingLot.name.contains(location)) | 
                                (ParkingLot.location.contains(location))
                            )
                            .limit(3)
                        ).all()

                        if lots:
                            response_data["response"] = f"ℹ️ **Here's the information about '{location}':**\n\n"
                            for lot in lots:
                                features = lot.features.split(",") if lot.features else []
                                features_text = ", ".join(features[:3]) if features else "Standard features"
                                
                                response_data["response"] += (
                                    f"🏢 **{lot.name}**\n"
                                    f"📍 Location: {lot.location}\n"
                                    f"💰 Price: RM {lot.price_per_hour}/hour\n"
                                    f"🚗 Total Spots: {lot.total_spots}\n"
                                    f"✅ Available: {lot.available_spots} spots\n"
                                    f"⭐ Rating: {lot.rating}/5.0\n"
                                    f"🎯 Features: {features_text}\n\n"
                                )
                                response_data["suggestions"].append(f"Book at {lot.name}")
                            
                            response_data["response"] += "**Want to book?** Go to [Listings](/listings)!"
                        else:
                            response_data["response"] = (
                                f"😕 **Sorry, I couldn't find any information about '{location}'.**\n\n"
                                "Try checking the name or browse all lots on the [Listings](/listings) page."
                            )
                
                # Check for user bookings (if logged in)
                elif user_id:
                    with rx.session() as session:
                        bookings = session.exec(
                            select(Booking)
                            .where(Booking.user_id == user_id)
                            .order_by(Booking.created_at.desc())
                            .limit(3)
                        ).all()

                        if bookings:
                            response_data["response"] = "📋 **Your recent bookings:**\n\n"
                            
                            for booking in bookings:
                                lot = session.get(ParkingLot, booking.lot_id)
                                status_emoji = "✅" if booking.status == "Confirmed" else "⏳" if booking.status == "Pending" else "❌"
                                
                                response_data["response"] += (
                                    f"{status_emoji} **{lot.name if lot else 'Unknown'}**\n"
                                    f"   📅 {booking.start_date} at {booking.start_time}\n"
                                    f"   ⏱️ {booking.duration_hours} hours\n"
                                    f"   💰 RM {booking.total_price}\n"
                                    f"   📊 Status: {booking.status}\n\n"
                                )
                            
                            response_data["response"] += "\n📌 View all bookings on your [Bookings](/bookings) page!"
                        else:
                            response_data["response"] = (
                                "📋 **You don't have any bookings yet.**\n\n"
                                "Ready to book your first parking spot? Check out our [available lots](/listings)!"
                            )
                            response_data["suggestions"] = ["Find parking near me"]
                else:
                    response_data["response"] = (
                        "ℹ️ **I can help you with:**\n\n"
                        "• 🔍 Tell me about specific parking lots (e.g., 'Tell me about Sunway Pyramid')\n"
                        "• 📋 View your bookings (please log in first)\n"
                        "• 🅿️ Check availability across all locations\n\n"
                        "**What would you like to know?**"
                    )

            elif intent == "my_bookings":
                if user_id:
                    # Same as get_info for bookings
                    with rx.session() as session:
                        bookings = session.exec(
                            select(Booking)
                            .where(Booking.user_id == user_id)
                            .order_by(Booking.created_at.desc())
                        ).all()

                        if bookings:
                            active = [b for b in bookings if b.status == "Confirmed"]
                            past = [b for b in bookings if b.status == "Completed"]
                            
                            response_data["response"] = f"📋 **Your Booking Summary:**\n\n"
                            response_data["response"] += f"✅ Active Bookings: {len(active)}\n"
                            response_data["response"] += f"📁 Past Bookings: {len(past)}\n\n"
                            
                            if active:
                                response_data["response"] += "**Active Bookings:**\n"
                                for booking in active[:3]:
                                    lot = session.get(ParkingLot, booking.lot_id)
                                    response_data["response"] += (
                                        f"• {lot.name if lot else 'Unknown'} - "
                                        f"{booking.start_date} at {booking.start_time}\n"
                                    )
                            
                            response_data["response"] += "\n\n📌 View all details on your [Bookings](/bookings) page!"
                        else:
                            response_data["response"] = (
                                "📋 **You don't have any bookings.**\n\n"
                                "Let's find you a parking spot! [Browse available lots](/listings)."
                            )
                else:
                    response_data["response"] = (
                        "🔐 **Please log in to view your bookings.**\n\n"
                        "Visit the [Login](/login) page to access your account."
                    )

            elif intent == "help":
                response_data["response"] = (
                    "🤖 **I'm your Smart Parking Assistant!**\n\n"
                    "**Here's what I can do:**\n\n"
                    "🅿️ **Finding Parking**\n"
                    "   Say: 'Find parking near downtown' or 'I need parking at Central Mall'\n\n"
                    "📋 **Check Availability**\n"
                    "   Say: 'Show available spots' or 'What's available?'\n\n"
                    "ℹ️ **Get Information**\n"
                    "   Say: 'Tell me about Sunway Pyramid' or 'Show lot prices'\n\n"
                    "📊 **View Your Bookings**\n"
                    "   Say: 'Show my bookings' (requires login)\n\n"
                    "**Just type your question naturally, and I'll help you!** 😊"
                )
                response_data["suggestions"] = [
                    "Find parking near KLCC",
                    "Check availability",
                    "Show my bookings"
                ]

            else:
                response_data["response"] = (
                    "🤔 **I'm not sure I understood that.**\n\n"
                    "You can ask me to:\n"
                    "• 🅿️ Find parking spots\n"
                    "• 📊 Check availability\n"
                    "• ℹ️ Get information about parking lots\n"
                    "• 📋 View your bookings\n"
                    "• ❓ Type 'help' for more options\n\n"
                    "**Try asking me something!**"
                )
                response_data["suggestions"] = [
                    "Find parking",
                    "Check availability",
                    "Help"
                ]

        except Exception as e:
            print(f"Error generating chatbot response: {e}")
            response_data["response"] = (
                "😓 **Oops! I encountered an error.**\n\n"
                "Please try rephrasing your question or contact support if the issue persists."
            )

        return response_data
