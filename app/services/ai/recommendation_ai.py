"""
Recommendation Engine for Personalized Parking Suggestions
Uses user preferences and booking history to suggest best parking lots
"""

import reflex as rx
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
from sqlmodel import select
from app.db.models import (
    User, ParkingLot, Booking
)



class RecommendationEngine:
    """AI-powered recommendation engine for personalized parking suggestions"""

    @staticmethod
    async def analyze_user_preferences(user_id: int) -> Dict:
        """Analyze user's booking history to detect preferences"""
        preferences = {
            "preferred_locations": [],
            "preferred_price_range": {"min": None, "max": None},
            "preferred_amenities": [],
            "booking_frequency": "occasional",
            "average_duration": None
        }

        try:
            with rx.session() as session:
                # Get user's booking history
                bookings = session.exec(
                    select(Booking)
                    .where(Booking.user_id == user_id)
                    .order_by(Booking.created_at.desc())
                    .limit(50)
                ).all()

                if not bookings:
                    return preferences

                # Analyze locations
                location_counts = {}
                prices = []
                durations = []
                amenities_counts = {}

                for booking in bookings:
                    lot = session.get(ParkingLot, booking.lot_id)
                    if lot:
                        # Track locations
                        location_counts[lot.location] = location_counts.get(lot.location, 0) + 1
                        
                        # Track prices
                        prices.append(lot.price_per_hour)
                        
                        # Track durations
                        durations.append(booking.duration_hours)
                        
                        # Track amenities
                        for amenity in lot.features.split(","):
                            amenity = amenity.strip()
                            amenities_counts[amenity] = amenities_counts.get(amenity, 0) + 1

                # Determine preferred locations (top 3)
                sorted_locations = sorted(location_counts.items(), key=lambda x: x[1], reverse=True)
                preferences["preferred_locations"] = [loc for loc, _ in sorted_locations[:3]]

                # Determine price range
                if prices:
                    preferences["preferred_price_range"] = {
                        "min": round(min(prices), 2),
                        "max": round(max(prices), 2)
                    }

                # Determine preferred amenities
                total_bookings = len(bookings)
                preferences["preferred_amenities"] = [
                    amenity for amenity, count in amenities_counts.items()
                    if count / total_bookings >= 0.5  # User chose this amenity in 50%+ bookings
                ]

                # Determine booking frequency
                if len(bookings) >= 20:
                    preferences["booking_frequency"] = "frequent"
                elif len(bookings) >= 5:
                    preferences["booking_frequency"] = "regular"
                
                # Average duration
                if durations:
                    preferences["average_duration"] = int(sum(durations) / len(durations))

        except Exception as e:
            print(f"Error analyzing user preferences: {e}")

        return preferences



    @staticmethod
    def calculate_recommendation_score(
        user_prefs: Dict,
        parking_lot: ParkingLot
    ) -> tuple[float, List[str]]:
        """
        Calculate recommendation score for a parking lot based on user preferences
        Returns: (score, factors)
        Score is 0.0 to 10.0
        """
        score = 5.0  # Base score
        factors = []

        try:
            # Location match (weight: 2.0)
            if user_prefs.get("preferred_locations"):
                preferred_locs = user_prefs["preferred_locations"]
                if parking_lot.location in preferred_locs:
                    score += 2.0
                    factors.append(f"Preferred location: {parking_lot.location}")

            # Price range match (weight: 1.5)
            price_range = user_prefs.get("preferred_price_range", {})
            min_price = price_range.get("min")
            max_price = price_range.get("max")
            
            if min_price is not None and max_price is not None:
                if min_price <= parking_lot.price_per_hour <= max_price:
                    score += 1.5
                    factors.append("Within your price range")
                elif parking_lot.price_per_hour < min_price:
                    score += 1.0
                    factors.append("Great price!")
                else:
                    score -= 0.5

            # Amenities match (weight: 1.5)
            if user_prefs.get("preferred_amenities"):
                preferred_amenities = user_prefs["preferred_amenities"]
                lot_amenities = [a.strip() for a in parking_lot.features.split(",")]
                matching_amenities = set(preferred_amenities) & set(lot_amenities)
                
                if matching_amenities:
                    amenity_score = len(matching_amenities) / len(preferred_amenities) * 1.5
                    score += amenity_score
                    factors.append(f"Has preferred amenities: {', '.join(matching_amenities)}")

            # Rating bonus (weight: 1.0)
            if parking_lot.rating >= 4.5:
                score += 1.0
                factors.append(f"Highly rated ({parking_lot.rating}⭐)")
            elif parking_lot.rating >= 4.0:
                score += 0.5

            # Availability bonus
            availability_rate = parking_lot.available_spots / parking_lot.total_spots if parking_lot.total_spots > 0 else 0
            if availability_rate > 0.5:
                score += 0.5
                factors.append("Good availability")

            # Cap score at 10.0
            score = min(10.0, score)

        except Exception as e:
            print(f"Error calculating recommendation score: {e}")
            score = 5.0

        return score, factors

    @staticmethod
    async def get_recommendations(
        user_id: int,
        location: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Get personalized parking lot recommendations for a user
        """
        recommendations = []

        try:
            with rx.session() as session:
                # Dynamically calculate user preferences without hitting a dedicated AI DB tracking table
                user_prefs = await RecommendationEngine.analyze_user_preferences(user_id)

                # If user has no preferences or history, return top-rated lots
                if not user_prefs or not user_prefs.get("preferred_locations"):
                    lots = session.exec(
                        select(ParkingLot).order_by(ParkingLot.rating.desc()).limit(limit)
                    ).all()
                    return [
                        {
                            "lot": lot.to_dict(),
                            "score": lot.rating * 2,
                            "factors": [f"Highly rated ({lot.rating}⭐)"]
                        }
                        for lot in lots
                    ]

                # Get all parking lots (optionally filter by location)
                query = select(ParkingLot)
                if location:
                    query = query.where(ParkingLot.location.contains(location))
                
                lots = session.exec(query).all()

                # Calculate scores for each lot
                scored_lots = []
                for lot in lots:
                    score, factors = RecommendationEngine.calculate_recommendation_score(
                        user_prefs, lot
                    )
                    
                    scored_lots.append({
                        "lot": lot.to_dict(),
                        "score": score,
                        "factors": factors
                    })

                # No longer saving recommendation scores to the database. They are purely computed on the fly.

                # Sort by score and return top recommendations
                recommendations = sorted(scored_lots, key=lambda x: x["score"], reverse=True)[:limit]

        except Exception as e:
            print(f"Error getting recommendations: {e}")

        return recommendations

    @staticmethod
    async def update_all_user_preferences():
        """Background job to update preferences for all active users"""
        try:
            with rx.session() as session:
                # Get all users who have made bookings
                users = session.exec(
                    select(User.id).join(Booking).distinct()
                ).all()

                for user_id in users:
                    await RecommendationEngine.save_user_preferences(user_id)

                return len(users)

        except Exception as e:
            print(f"Error updating all user preferences: {e}")
            return 0
