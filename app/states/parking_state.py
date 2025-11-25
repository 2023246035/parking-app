import reflex as rx
import asyncio
import logging
from sqlmodel import select
from app.states.schema import ParkingLot
from app.db.models import ParkingLot as DBParkingLot


class ParkingState(rx.State):
    parking_lots: list[ParkingLot] = []
    filtered_lots: list[ParkingLot] = []
    search_query: str = ""
    location_filter: str = "All"
    is_loading: bool = False
    
    # Advanced filters
    min_price: float = 0.0
    max_price: float = 100.0
    sort_by: str = "default"  # Options: default, price_low, price_high, rating, availability
    show_available_only: bool = False
    show_filters: bool = False  # Toggle for filter panel visibility

    @rx.event
    def on_load(self):
        """Load data when the page loads."""
        self.is_loading = True
        yield ParkingState.load_data

    @rx.event
    async def load_data(self):
        """Fetch parking lots from the database."""
        logging.info("ParkingState: Starting load_data...")
        try:
            with rx.session() as session:
                stmt = select(DBParkingLot)
                db_lots = session.exec(stmt).all()
                logging.info(f"ParkingState: Found {len(db_lots)} lots in DB")
                
                self.parking_lots = [
                    ParkingLot(
                        id=str(lot.id),
                        name=lot.name,
                        location=lot.location,
                        price_per_hour=lot.price_per_hour,
                        total_spots=lot.total_spots,
                        available_spots=lot.available_spots,
                        image_url=lot.image_url,
                        features=lot.features.split(",") if lot.features else [],
                        rating=lot.rating,
                    )
                    for lot in db_lots
                ]
                logging.info(f"ParkingState: Populated {len(self.parking_lots)} state objects")
                self.filter_lots()
        except Exception as e:
            logging.exception(f"Error loading parking data: {e}")
            yield rx.toast.error("Failed to load parking lots.")
        finally:
            self.is_loading = False

    @rx.event
    def update_spots(self, lot_id: str, change: int):
        """
        Update available spots for a lot locally.
        Note: The actual DB update happens in BookingState during transaction.
        This method keeps the UI in sync.
        """
        new_lots = []
        for lot in self.parking_lots:
            if lot.id == lot_id:
                lot.available_spots += change
                if lot.available_spots < 0:
                    lot.available_spots = 0
                if lot.available_spots > lot.total_spots:
                    lot.available_spots = lot.total_spots
            new_lots.append(lot)
        self.parking_lots = new_lots
        self.filter_lots()

    @rx.event
    def filter_lots(self):
        """Filter parking lots based on all active filters."""
        logging.info(f"ParkingState: Filtering lots. Query='{self.search_query}', Location='{self.location_filter}'")
        query = self.search_query.lower()
        filtered = self.parking_lots
        
        # Search query filter
        if query:
            filtered = [
                lot
                for lot in filtered
                if query in lot.name.lower() or query in lot.location.lower()
            ]
        
        # Location filter
        if self.location_filter != "All":
            filtered = [
                lot
                for lot in filtered
                if self.location_filter.lower() in lot.location.lower()
            ]
        
        # Price range filter
        if self.min_price > 0.0 or self.max_price < 100.0:
            filtered = [
                lot
                for lot in filtered
                if self.min_price <= lot.price_per_hour <= self.max_price
            ]
        
        # Availability filter
        if self.show_available_only:
            filtered = [
                lot
                for lot in filtered
                if lot.available_spots > 0
            ]
        
        # Sorting
        if self.sort_by == "price_low":
            filtered = sorted(filtered, key=lambda x: x.price_per_hour)
        elif self.sort_by == "price_high":
            filtered = sorted(filtered, key=lambda x: x.price_per_hour, reverse=True)
        elif self.sort_by == "rating":
            filtered = sorted(filtered, key=lambda x: x.rating if x.rating else 0, reverse=True)
        elif self.sort_by == "availability":
            filtered = sorted(filtered, key=lambda x: x.available_spots, reverse=True)
        
        self.filtered_lots = filtered
        logging.info(f"ParkingState: Filtered down to {len(self.filtered_lots)} lots")

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query
        self.filter_lots()

    @rx.event
    def set_location_filter(self, location: str):
        self.location_filter = location
        self.filter_lots()
    
    @rx.event
    def set_min_price(self, price: str):
        try:
            self.min_price = float(price) if price else 0.0
            self.filter_lots()
        except ValueError:
            pass
    
    @rx.event
    def set_max_price(self, price: str):
        try:
            self.max_price = float(price) if price else 100.0
            self.filter_lots()
        except ValueError:
            pass
    
    @rx.event
    def set_sort_by(self, sort_option: str):
        self.sort_by = sort_option
        self.filter_lots()
    
    @rx.event
    def toggle_available_only(self):
        self.show_available_only = not self.show_available_only
        self.filter_lots()
    
    @rx.event
    def toggle_filters(self):
        """Toggle filter panel visibility."""
        self.show_filters = not self.show_filters
    
    @rx.event
    def reset_filters(self):
        """Reset all filters to default values."""
        self.search_query = ""
        self.location_filter = "All"
        self.min_price = 0.0
        self.max_price = 100.0
        self.sort_by = "default"
        self.show_available_only = False
        self.filter_lots()