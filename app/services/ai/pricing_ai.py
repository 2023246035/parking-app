"""
Dynamic Pricing Engine for Parking Lots
Automatically adjusts parking prices based on demand, occupancy, time, and events
"""

import reflex as rx
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import json
from sqlmodel import select
from app.db.models import ParkingLot, Booking
from app.db.ai_models import PricingHistory


class DynamicPricingEngine:
    """AI-powered dynamic pricing engine for parking lots"""

    # Pricing multiplier configurations
    PEAK_HOURS = [(7, 10), (17, 20)]  # Morning and evening rush hours
    WEEKEND_MULTIPLIER = 1.1
    PEAK_HOUR_MULTIPLIER = 1.3
    HIGH_DEMAND_MULTIPLIER = 1.5
    LOW_DEMAND_MULTIPLIER = 0.8

    @staticmethod
    def calculate_time_multiplier(current_time: datetime = None) -> float:
        """Calculate price multiplier based on time of day and day of week"""
        if current_time is None:
            current_time = datetime.now()

        multiplier = 1.0
        hour = current_time.hour
        is_weekend = current_time.weekday() >= 5

        # Weekend premium
        if is_weekend:
            multiplier *= DynamicPricingEngine.WEEKEND_MULTIPLIER

        # Peak hour premium
        for start_hour, end_hour in DynamicPricingEngine.PEAK_HOURS:
            if start_hour <= hour < end_hour:
                multiplier *= DynamicPricingEngine.PEAK_HOUR_MULTIPLIER
                break

        return multiplier

    @staticmethod
    def calculate_occupancy_multiplier(occupancy_rate: float) -> float:
        """Calculate price multiplier based on current occupancy rate"""
        if occupancy_rate >= 0.9:  # 90%+ occupied
            return DynamicPricingEngine.HIGH_DEMAND_MULTIPLIER
        elif occupancy_rate >= 0.75:  # 75-89% occupied
            return 1.2
        elif occupancy_rate >= 0.5:  # 50-74% occupied
            return 1.0
        elif occupancy_rate >= 0.25:  # 25-49% occupied
            return 0.95
        else:  # Less than 25% occupied
            return DynamicPricingEngine.LOW_DEMAND_MULTIPLIER

    @staticmethod
    def calculate_demand_multiplier(booking_velocity: int) -> float:
        """
        Calculate multiplier based on booking velocity
        booking_velocity: number of bookings in the last hour
        """
        if booking_velocity >= 10:
            return 1.4
        elif booking_velocity >= 5:
            return 1.2
        elif booking_velocity >= 2:
            return 1.0
        else:
            return 0.9

    @staticmethod
    async def get_booking_velocity(lot_id: int, hours_back: int = 1) -> int:
        """Get number of bookings made in the last N hours"""
        with rx.session() as session:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            bookings = session.exec(
                select(Booking).where(
                    Booking.lot_id == lot_id,
                    Booking.created_at >= cutoff_time
                )
            ).all()
            return len(bookings)

    @staticmethod
    async def calculate_dynamic_price(
        lot_id: int,
       base_price: float,
        current_time: datetime = None
    ) -> Dict:
        """
        Calculate dynamic price for a parking lot
        Returns dict with price and breakdown of factors
        """
        if current_time is None:
            current_time = datetime.now()

        result = {
            "base_price": base_price,
            "dynamic_price": base_price,
            "multipliers": {},
            "factors": []
        }

        try:
            with rx.session() as session:
                # Get parking lot
                lot = session.get(ParkingLot, lot_id)
                if not lot:
                    return result

                # Calculate occupancy rate
                occupancy_rate = (lot.total_spots - lot.available_spots) / lot.total_spots if lot.total_spots > 0 else 0

                # Get booking velocity
                booking_velocity = await DynamicPricingEngine.get_booking_velocity(lot_id)

                # Calculate multipliers
                time_mult = DynamicPricingEngine.calculate_time_multiplier(current_time)
                occupancy_mult = DynamicPricingEngine.calculate_occupancy_multiplier(occupancy_rate)
                demand_mult = DynamicPricingEngine.calculate_demand_multiplier(booking_velocity)

                # Combine multipliers
                total_multiplier = time_mult * occupancy_mult * demand_mult

                # Calculate final price
                dynamic_price = round(base_price * total_multiplier, 2)

                # Build result
                result.update({
                    "dynamic_price": dynamic_price,
                    "multipliers": {
                        "time": round(time_mult, 2),
                        "occupancy": round(occupancy_mult, 2),
                        "demand": round(demand_mult, 2),
                        "total": round(total_multiplier, 2)
                    },
                    "factors": []
                })

                # Add explanatory factors
                if time_mult > 1.0:
                    if current_time.weekday() >= 5:
                        result["factors"].append("Weekend premium")
                    result["factors"].append("Peak hour pricing")
                
                if occupancy_rate >= 0.75:
                    result["factors"].append(f"High occupancy ({int(occupancy_rate * 100)}%)")
                elif occupancy_rate < 0.25:
                    result["factors"].append("Low occupancy discount")

                if booking_velocity >= 5:
                    result["factors"].append("High demand period")

                # Save to pricing history
                pricing_record = PricingHistory(
                    parking_lot_id=lot_id,
                    base_price=base_price,
                    dynamic_price=dynamic_price,
                    occupancy_rate=occupancy_rate,
                    demand_multiplier=demand_mult,
                    time_multiplier=time_mult,
                    factors=json.dumps(result["factors"])
                )
                session.add(pricing_record)
                session.commit()

        except Exception as e:
            print(f"Error calculating dynamic price: {e}")

        return result


    @staticmethod
    async def update_all_parking_prices():
        """Update dynamic prices for all parking lots"""
        updated_lots = []
        
        with rx.session() as session:
            lots = session.exec(select(ParkingLot)).all()
            
            for lot in lots:
                pricing_info = await DynamicPricingEngine.calculate_dynamic_price(
                    lot.id,
                    lot.price_per_hour
                )
                updated_lots.append({
                    "lot_id": lot.id,
                    "name": lot.name,
                    "base_price": lot.price_per_hour,
                    "dynamic_price": pricing_info["dynamic_price"],
                    "multiplier": pricing_info["multipliers"]["total"],
                    "factors": pricing_info["factors"]
                })

        return updated_lots


    @staticmethod
    async def get_price_history(lot_id: int, days: int = 7) -> List[Dict]:
        """Get pricing history for a parking lot"""
        with rx.session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            history = session.exec(
                select(PricingHistory)
                .where(
                    PricingHistory.parking_lot_id == lot_id,
                    PricingHistory.timestamp >= cutoff_date
                )
                .order_by(PricingHistory.timestamp.desc())
            ).all()

            return [record.to_dict() for record in history]

    @staticmethod
    def get_price_trend(lot_id: int) -> str:
        """Get price trend: 'rising', 'falling', or 'stable'"""
        try:
            with rx.session() as session:
                # Get last 10 price records
                records = session.exec(
                    select(PricingHistory)
                    .where(PricingHistory.parking_lot_id == lot_id)
                    .order_by(PricingHistory.timestamp.desc())
                    .limit(10)
                ).all()

                if len(records) < 2:
                    return "stable"

                # Compare recent average with older average
                recent_avg = sum(r.dynamic_price for r in records[:3]) / 3
                older_avg = sum(r.dynamic_price for r in records[3:]) / max(1, len(records) - 3)

                if recent_avg > older_avg * 1.05:
                    return "rising"
                elif recent_avg < older_avg * 0.95:
                    return "falling"
                else:
                    return "stable"

        except Exception as e:
            print(f"Error getting price trend: {e}")
            return "stable"
