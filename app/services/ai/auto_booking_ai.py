"""
Auto-Booking Agent
Detects user booking patterns and suggests/auto-books parking spots
"""

import reflex as rx
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from collections import defaultdict
from sqlmodel import select
import os
from app.db.models import Booking, User, ParkingLot

SETTINGS_FILE = "ai_settings.json"

def _load_settings() -> Dict[int, Dict]:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return {int(k): v for k, v in json.load(f).items()}
        except Exception:
            return {}
    return {}

def _save_settings(cache: Dict[int, Dict]):
    with open(SETTINGS_FILE, "w") as f:
        json.dump({str(k): v for k, v in cache.items()}, f)

_settings_cache: Dict[int, Dict] = _load_settings()

class AutoBookingAgent:
    """AI agent that learns user patterns and auto-books parking"""

    @staticmethod
    def detect_booking_patterns(user_id: int) -> Dict:
        """
        Analyze user's booking history to detect patterns
        Returns patterns by day of week and time
        """
        patterns = {
            "weekly_patterns": {},  # day_of_week -> {time, duration, lot_id}
            "recurring_locations": [],
            "typical_duration": None,
            "confidence": 0.0
        }

        try:
            with rx.session() as session:
                # Get last 3 months of bookings
                cutoff_date = datetime.utcnow() - timedelta(days=90)
                bookings = session.exec(
                    select(Booking)
                    .where(
                        Booking.user_id == user_id,
                        Booking.created_at >= cutoff_date
                    )
                    .order_by(Booking.created_at.desc())
                ).all()

                if len(bookings) < 3:
                    return patterns

                # Group bookings by day of week
                day_bookings = defaultdict(list)
                all_durations = []
                location_counts = defaultdict(int)

                for booking in bookings:
                    try:
                        # Parse booking date
                        booking_date = datetime.strptime(booking.start_date, "%Y-%m-%d")
                        day_of_week = booking_date.strftime("%A").lower()
                        
                        day_bookings[day_of_week].append({
                            "time": booking.start_time,
                            "duration": booking.duration_hours,
                            "lot_id": booking.lot_id
                        })
                        
                        all_durations.append(booking.duration_hours)
                        
                        lot = session.get(ParkingLot, booking.lot_id)
                        if lot:
                            location_counts[booking.lot_id] += 1

                    except Exception as e:
                        print(f"Error parsing booking: {e}")
                        continue

                # Detect patterns for each day
                for day, day_bookings_list in day_bookings.items():
                    if len(day_bookings_list) >= 2:  # Need at least 2 bookings to detect pattern
                        # Find most common time and duration
                        time_counts = defaultdict(int)
                        duration_counts = defaultdict(int)
                        lot_counts = defaultdict(int)

                        for booking in day_bookings_list:
                            # Group similar times (within 30 min)
                            time_hour = booking["time"].split(":")[0] if ":" in booking["time"] else booking["time"]
                            time_counts[time_hour] += 1
                            duration_counts[booking["duration"]] += 1
                            lot_counts[booking["lot_id"]] += 1

                        # Get most common values
                        most_common_time = max(time_counts.items(), key=lambda x: x[1])
                        most_common_duration = max(duration_counts.items(), key=lambda x: x[1])
                        most_common_lot = max(lot_counts.items(), key=lambda x: x[1])

                        # Only add if pattern appears at least twice
                        if most_common_time[1] >= 2:
                            patterns["weekly_patterns"][day] = {
                                "time": f"{most_common_time[0]}:00",
                                "duration": most_common_duration[0],
                                "lot_id": most_common_lot[0],
                                "frequency": most_common_time[1]
                            }

                # Calculate typical duration
                if all_durations:
                    patterns["typical_duration"] = int(sum(all_durations) / len(all_durations))

                # Get recurring locations (appears in 30%+ of bookings)
                total_bookings = len(bookings)
                patterns["recurring_locations"] = [
                    lot_id for lot_id, count in location_counts.items()
                    if count / total_bookings >= 0.3
                ]

                # Calculate confidence (0.0 to 1.0)
                pattern_count = len(patterns["weekly_patterns"])
                if pattern_count >= 3:
                    patterns["confidence"] = 0.9
                elif pattern_count >= 2:
                    patterns["confidence"] = 0.7
                elif pattern_count >= 1:
                    patterns["confidence"] = 0.5
                else:
                    patterns["confidence"] = 0.0

        except Exception as e:
            print(f"Error detecting booking patterns: {e}")

        return patterns

    @staticmethod
    async def save_auto_booking_settings(
        user_id: int,
        enabled: bool = True,
        auto_confirm: bool = False,
        max_price_threshold: Optional[float] = None
    ):
        """Save or update auto-booking settings for a user into local JSON cache"""
        try:
            # Detect patterns first
            patterns = AutoBookingAgent.detect_booking_patterns(user_id)

            schedule_patterns = json.dumps(patterns["weekly_patterns"])
            preferred_lot_ids = json.dumps(patterns["recurring_locations"])

            _settings_cache[user_id] = {
                "user_id": user_id,
                "enabled": enabled,
                "auto_confirm": auto_confirm,
                "max_price_threshold": max_price_threshold,
                "schedule_patterns": schedule_patterns,
                "preferred_lot_ids": preferred_lot_ids,
                "updated_at": datetime.now().isoformat()
            }
            _save_settings(_settings_cache)

            return True

        except Exception as e:
            print(f"Error saving auto-booking settings: {e}")
            return False

    @staticmethod
    async def get_auto_booking_suggestions(user_id: int) -> List[Dict]:
        """
        Get auto-booking suggestions for the user based on patterns
        Returns list of suggested bookings
        """
        suggestions = []

        try:
            with rx.session() as session:
                # Get user's auto-booking settings from memory
                settings = _settings_cache.get(user_id)

                if not settings or not settings["enabled"]:
                    return suggestions

                # Parse patterns
                if not settings["schedule_patterns"]:
                    return suggestions

                patterns = json.loads(settings["schedule_patterns"])
                current_date = datetime.now()

                # Check next 7 days for pattern matches
                for i in range(7):
                    check_date = current_date + timedelta(days=i)
                    day_name = check_date.strftime("%A").lower()

                    if day_name in patterns:
                        pattern = patterns[day_name]
                        
                        # Check if there's already a booking for this day
                        existing_booking = session.exec(
                            select(Booking).where(
                                Booking.user_id == user_id,
                                Booking.start_date == check_date.strftime("%Y-%m-%d"),
                                Booking.status != "Cancelled"
                            )
                        ).first()

                        if existing_booking:
                            continue  # Skip if already booked

                        # Get the parking lot
                        lot = session.get(ParkingLot, pattern["lot_id"])
                        if not lot or lot.available_spots <= 0:
                            continue

                        # Check price threshold
                        max_price = settings.get("max_price_threshold")
                        if max_price:
                            total_price = lot.price_per_hour * pattern["duration"]
                            if total_price > max_price:
                                continue

                        # Add suggestion
                        suggestions.append({
                            "date": check_date.strftime("%Y-%m-%d"),
                            "day": day_name.capitalize(),
                            "time": pattern["time"],
                            "duration": pattern["duration"],
                            "lot_id": lot.id,
                            "lot_name": lot.name,
                            "lot_location": lot.location,
                            "price_per_hour": lot.price_per_hour,
                            "total_price": lot.price_per_hour * pattern["duration"],
                            "confidence": "High" if pattern["frequency"] >= 3 else "Medium",
                            "reason": f"You usually park here on {day_name.capitalize()}s at {pattern['time']}"
                        })

        except Exception as e:
            print(f"Error getting auto-booking suggestions: {e}")

        return suggestions

    @staticmethod
    async def execute_auto_booking(suggestion: Dict, user_id: int) -> Optional[int]:
        """
        Execute an auto-booking based on a suggestion
        Returns booking_id if successful, None otherwise
        """
        try:
            with rx.session() as session:
                # Verify lot availability
                lot = session.get(ParkingLot, suggestion["lot_id"])
                if not lot or lot.available_spots <= 0:
                    return None

                # Create booking
                new_booking = Booking(
                    user_id=user_id,
                    lot_id=suggestion["lot_id"],
                    start_date=suggestion["date"],
                    start_time=suggestion["time"],
                    duration_hours=suggestion["duration"],
                    total_price=suggestion["total_price"],
                    status="Confirmed",
                    payment_status="Pending"
                )

                # Update lot availability
                lot.available_spots -= 1

                session.add(new_booking)
                session.commit()
                session.refresh(new_booking)

                return new_booking.id

        except Exception as e:
            print(f"Error executing auto-booking: {e}")
            return None

    @staticmethod
    async def check_and_execute_auto_bookings():
        """
        Background job to check and execute auto-bookings for all enabled users
        Should run daily
        """
        executed_bookings = []

        try:
            with rx.session() as session:
                # Get all users with auto-booking enabled and auto-confirm on from local memory JSON
                settings_list = [
                    s for s in _settings_cache.values()
                    if s.get("enabled") and s.get("auto_confirm")
                ]

                for settings in settings_list:
                    suggestions = await AutoBookingAgent.get_auto_booking_suggestions(settings["user_id"])
                    
                    # Auto-book suggestions for tomorrow
                    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                    for suggestion in suggestions:
                        if suggestion["date"] == tomorrow:
                            booking_id = await AutoBookingAgent.execute_auto_booking(
                                suggestion,
                                settings["user_id"]
                            )
                            
                            if booking_id:
                                executed_bookings.append({
                                    "user_id": settings["user_id"],
                                    "booking_id": booking_id,
                                    "suggestion": suggestion
                                })

        except Exception as e:
            print(f"Error in auto-booking background job: {e}")

        return executed_bookings
