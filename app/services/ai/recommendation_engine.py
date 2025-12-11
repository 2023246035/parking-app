"""
AI Recommendation System for ParkMyCar
Suggests best parking lots based on user preferences, history, and context
"""

from datetime import datetime, time
from typing import List, Dict, Optional
from sqlmodel import select, Session
from app.db.models import Booking, ParkingLot, User
import reflex as rx
from collections import Counter


class ParkingRecommendationEngine:
    """Advanced AI engine for parking recommendations"""
    
    @staticmethod
    def calculate_recommendation_score(
        lot: ParkingLot,
        user_id: int,
        booking_time: Optional[str] = None,
        user_preferences: Optional[Dict] = None
    ) -> float:
        """
        Calculate recommendation score for a parking lot
        Returns: Score 0-100 (higher is better)
        """
        score = 0.0
        weights = {
            "history": 30,      # 30% - User's past bookings
            "availability": 25, # 25% - Current availability
            "price": 20,        # 20% - Price preference
            "rating": 15,       # 15% - Lot rating
            "traffic": 10       # 10% - Peak hours consideration
        }
        
        with rx.session() as session:
            # 1. HISTORY SCORE (30%) - User's past bookings
            history_score = ParkingRecommendationEngine._calculate_history_score(
                session, lot, user_id
            )
            score += history_score * weights["history"]
            
            # 2. AVAILABILITY SCORE (25%) - Current availability
            availability_score = ParkingRecommendationEngine._calculate_availability_score(lot)
            score += availability_score * weights["availability"]
            
            # 3. PRICE SCORE (20%) - Price preference
            price_score = ParkingRecommendationEngine._calculate_price_score(
                session, lot, user_id, user_preferences
            )
            score += price_score * weights["price"]
            
            # 4. RATING SCORE (15%) - Lot quality
            rating_score = lot.rating / 5.0  # Normalize to 0-1
            score += rating_score * weights["rating"]
            
            # 5. TRAFFIC SCORE (10%) - Peak hours
            traffic_score = ParkingRecommendationEngine._calculate_traffic_score(
                booking_time
            )
            score += traffic_score * weights["traffic"]
        
        return round(score, 2)
    
    @staticmethod
    def _calculate_history_score(session: Session, lot: ParkingLot, user_id: int) -> float:
        """
        Calculate score based on user's booking history
        Returns: 0-1 (1 = frequently booked here)
        """
        # Get user's past bookings
        user_bookings = session.exec(
            select(Booking)
            .where(Booking.user_id == user_id)
            .where(Booking.status.in_(["Confirmed", "Completed"]))
        ).all()
        
        if not user_bookings:
            return 0.5  # Neutral score for new users
        
        # Count bookings at this lot
        lot_bookings = sum(1 for b in user_bookings if b.lot_id == lot.id)
        total_bookings = len(user_bookings)
        
        # Frequency score
        frequency = lot_bookings / total_bookings if total_bookings > 0 else 0
        
        # Boost score if user has booked here before
        if lot_bookings > 0:
            return min(0.7 + (frequency * 0.3), 1.0)  # 0.7-1.0 range
        
        return 0.3  # Lower score for lots never visited
    
    @staticmethod
    def _calculate_availability_score(lot: ParkingLot) -> float:
        """
        Calculate score based on current availability
        Returns: 0-1 (1 = plenty available)
        """
        if lot.total_spots == 0:
            return 0.0
        
        availability_ratio = lot.available_spots / lot.total_spots
        
        # Score curve: more available = higher score
        if availability_ratio >= 0.5:
            return 1.0  # Plenty of spots
        elif availability_ratio >= 0.3:
            return 0.8  # Good availability
        elif availability_ratio >= 0.1:
            return 0.5  # Some spots
        elif availability_ratio > 0:
            return 0.3  # Few spots
        else:
            return 0.0  # Full
    
    @staticmethod
    def _calculate_price_score(
        session: Session,
        lot: ParkingLot,
        user_id: int,
        user_preferences: Optional[Dict]
    ) -> float:
        """
        Calculate score based on price preference
        Returns: 0-1 (1 = matches user's typical spending)
        """
        # Get user's average spending
        user_bookings = session.exec(
            select(Booking)
            .where(Booking.user_id == user_id)
            .where(Booking.status.in_(["Confirmed", "Completed"]))
        ).all()
        
        if user_bookings:
            avg_price = sum(b.total_price for b in user_bookings) / len(user_bookings)
        else:
            # Use preferences or system average
            if user_preferences and "max_price" in user_preferences:
                avg_price = user_preferences["max_price"]
            else:
                all_lots = session.exec(select(ParkingLot)).all()
                avg_price = sum(l.price_per_hour for l in all_lots) / len(all_lots) if all_lots else 5.0
        
        # Calculate price per hour for typical booking (assume 2 hours)
        typical_price = lot.price_per_hour * 2
        
        # Score based on how close to user's average
        price_diff = abs(typical_price - avg_price)
        max_diff = avg_price * 0.5  # 50% tolerance
        
        if price_diff == 0:
            return 1.0
        elif price_diff <= max_diff:
            return 1.0 - (price_diff / max_diff) * 0.5  # 0.5-1.0 range
        else:
            return max(0.3, 1.0 - (price_diff / (avg_price * 2)))  # Lower scores
    
    @staticmethod
    def _calculate_traffic_score(booking_time: Optional[str]) -> float:
        """
        Calculate score based on peak hours
        Returns: 0-1 (1 = off-peak, easier booking)
        """
        if not booking_time:
            return 0.5  # Neutral if no time specified
        
        try:
            hour = int(booking_time.split(":")[0])
        except:
            return 0.5
        
        # Peak hours: 7-9 AM, 5-7 PM (lower score)
        # Off-peak: other times (higher score)
        if hour in [7, 8, 17, 18]:  # Peak morning/evening
            return 0.3  # Lower score (harder to find parking)
        elif hour in [9, 10, 16]:  # Near-peak
            return 0.6
        else:  # Off-peak
            return 1.0  # Higher score (easier parking)
    
    @staticmethod
    async def get_recommendations(
        user_id: int,
        booking_time: Optional[str] = None,
        location_filter: Optional[str] = None,
        price_range: Optional[tuple] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Get top N recommended parking lots for user
        
        Returns: List of dicts with lot info + recommendation score
        """
        with rx.session() as session:
            # Build query
            query = select(ParkingLot).where(ParkingLot.available_spots > 0)
            
            # Apply filters
            if location_filter:
                query = query.where(
                    (ParkingLot.location.contains(location_filter)) |
                    (ParkingLot.name.contains(location_filter))
                )
            
            if price_range:
                min_price, max_price = price_range
                query = query.where(
                    ParkingLot.price_per_hour >= min_price,
                    ParkingLot.price_per_hour <= max_price
                )
            
            lots = session.exec(query).all()
            
            # Calculate scores for each lot
            recommendations = []
            for lot in lots:
                score = ParkingRecommendationEngine.calculate_recommendation_score(
                    lot, user_id, booking_time
                )
                
                recommendations.append({
                    "lot": lot,
                    "score": score,
                    "reason": ParkingRecommendationEngine._generate_reason(
                        lot, user_id, score, session
                    )
                })
            
            # Sort by score (highest first)
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            
            return recommendations[:limit]
    
    @staticmethod
    def _generate_reason(lot: ParkingLot, user_id: int, score: float, session: Session) -> str:
        """Generate human-readable reason for recommendation"""
        reasons = []
        
        # Check booking history
        past_bookings = session.exec(
            select(Booking)
            .where(Booking.user_id == user_id)
            .where(Booking.lot_id == lot.id)
            .where(Booking.status.in_(["Confirmed", "Completed"]))
        ).all()
        
        if past_bookings:
            reasons.append(f"You've booked here {len(past_bookings)} time(s) before")
        
        # Check availability
        avail_ratio = lot.available_spots / lot.total_spots if lot.total_spots > 0 else 0
        if avail_ratio >= 0.5:
            reasons.append("Plenty of spots available")
        elif avail_ratio >= 0.3:
            reasons.append("Good availability")
        
        # Check rating
        if lot.rating >= 4.5:
            reasons.append(f"Highly rated ({lot.rating}⭐)")
        elif lot.rating >= 4.0:
            reasons.append("Well-rated location")
        
        # Check price
        all_lots = session.exec(select(ParkingLot)).all()
        avg_price = sum(l.price_per_hour for l in all_lots) / len(all_lots) if all_lots else lot.price_per_hour
        
        if lot.price_per_hour < avg_price * 0.8:
            reasons.append("Great price")
        elif lot.price_per_hour < avg_price:
            reasons.append("Affordable")
        
        if not reasons:
            reasons.append("Matches your preferences")
        
        return " • ".join(reasons[:3])  # Max 3 reasons
    
    @staticmethod
    async def get_user_preferences(user_id: int) -> Dict:
        """
        Analyze user's booking history to determine preferences
        """
        with rx.session() as session:
            bookings = session.exec(
                select(Booking)
                .where(Booking.user_id == user_id)
                .where(Booking.status.in_(["Confirmed", "Completed"]))
            ).all()
            
            if not bookings:
                return {
                    "favorite_locations": [],
                    "avg_price": 5.0,
                    "preferred_duration": 2,
                    "peak_booking_time": "09:00",
                    "total_bookings": 0
                }
            
            # Analyze locations
            locations = [session.get(ParkingLot, b.lot_id).location for b in bookings if session.get(ParkingLot, b.lot_id)]
            location_counts = Counter(locations)
            favorite_locations = [loc for loc, count in location_counts.most_common(3)]
            
            # Calculate averages
            avg_price = sum(b.total_price for b in bookings) / len(bookings)
            avg_duration = sum(b.duration_hours for b in bookings) / len(bookings)
            
            # Find peak booking time
            times = [b.start_time for b in bookings]
            time_counts = Counter(times)
            peak_time = time_counts.most_common(1)[0][0] if times else "09:00"
            
            return {
                "favorite_locations": favorite_locations,
                "avg_price": round(avg_price, 2),
                "preferred_duration": round(avg_duration, 1),
                "peak_booking_time": peak_time,
                "total_bookings": len(bookings),
                "avg_spending_per_booking": round(avg_price, 2)
            }
