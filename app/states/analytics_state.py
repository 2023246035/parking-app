import reflex as rx
from sqlmodel import select, func, desc
from app.db.models import Booking, ParkingLot, User
from datetime import datetime, timedelta
import logging

class AnalyticsState(rx.State):
    """State for Admin Analytics Dashboard"""
    bookings_data: list[dict] = []
    revenue_data: list[dict] = []
    lot_stats: list[dict] = []
    refund_stats: dict = {
        "total_refunds": 0,
        "refund_amount": 0.0,
        "refund_rate": 0.0
    }
    
    @rx.event
    async def load_analytics(self):
        """Load all analytics data"""
        logging.info("Loading analytics data...")
        try:
            with rx.session() as session:
                self.load_bookings_chart(session)
                self.load_revenue_chart(session)
                self.load_lot_stats(session)
                self.load_refund_stats(session)
        except Exception as e:
            logging.exception(f"Error loading analytics: {e}")
            
    def load_bookings_chart(self, session):
        """Load bookings per day for the last 7 days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        data = []
        for i in range(7):
            day = start_date + timedelta(days=i)
            next_day = day + timedelta(days=1)
            
            # Count bookings for this day
            count = len(session.exec(
                select(Booking).where(
                    Booking.created_at >= day,
                    Booking.created_at < next_day
                )
            ).all())
            
            data.append({
                "date": day.strftime("%a"),  # Mon, Tue, etc.
                "bookings": count
            })
        self.bookings_data = data

    def load_revenue_chart(self, session):
        """Load revenue per day for the last 7 days"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        data = []
        for i in range(7):
            day = start_date + timedelta(days=i)
            next_day = day + timedelta(days=1)
            
            # Sum revenue for this day
            bookings = session.exec(
                select(Booking).where(
                    Booking.created_at >= day,
                    Booking.created_at < next_day,
                    Booking.payment_status == "Paid"
                )
            ).all()
            
            revenue = sum(b.total_price for b in bookings)
            
            data.append({
                "date": day.strftime("%a"),
                "revenue": revenue
            })
        self.revenue_data = data

    def load_lot_stats(self, session):
        """Load stats per parking lot"""
        lots = session.exec(select(ParkingLot)).all()
        stats = []
        
        for lot in lots:
            # Calculate occupancy rate
            occupancy = 0
            if lot.total_spots > 0:
                occupancy = ((lot.total_spots - lot.available_spots) / lot.total_spots) * 100
            
            # Find most used time slot (simplified: just count total bookings for now)
            total_bookings = len(session.exec(
                select(Booking).where(Booking.lot_id == lot.id)
            ).all())
            
            stats.append({
                "name": lot.name,
                "occupancy": round(occupancy, 1),
                "total_bookings": total_bookings,
                "revenue": sum(b.total_price for b in lot.bookings if b.payment_status == "Paid")
            })
        
        # Sort by occupancy descending
        self.lot_stats = sorted(stats, key=lambda x: x["occupancy"], reverse=True)

    def load_refund_stats(self, session):
        """Load refund metrics"""
        all_bookings = session.exec(select(Booking)).all()
        total_bookings = len(all_bookings)
        
        refunded_bookings = [b for b in all_bookings if b.status == "Cancelled" and b.payment_status == "Refunded"]
        total_refunds = len(refunded_bookings)
        refund_amount = sum(b.total_price for b in refunded_bookings) # Assuming full refund for simplicity or store refund amount
        
        refund_rate = 0
        if total_bookings > 0:
            refund_rate = (total_refunds / total_bookings) * 100
            
        self.refund_stats = {
            "total_refunds": total_refunds,
            "refund_amount": refund_amount,
            "refund_rate": round(refund_rate, 1)
        }
