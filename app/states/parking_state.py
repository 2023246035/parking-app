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

    @rx.event
    def on_load(self):
        """Load data when the page loads."""
        self.is_loading = True
        yield ParkingState.load_data

    @rx.event
    async def load_data(self):
        """Fetch parking lots from the database."""
        try:
            with rx.session() as session:
                stmt = select(DBParkingLot)
                db_lots = session.exec(stmt).all()
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
        """Filter parking lots based on search query and location."""
        query = self.search_query.lower()
        filtered = self.parking_lots
        if query:
            filtered = [
                lot
                for lot in filtered
                if query in lot.name.lower() or query in lot.location.lower()
            ]
        if self.location_filter != "All":
            filtered = [
                lot
                for lot in filtered
                if self.location_filter.lower() in lot.location.lower()
            ]
        self.filtered_lots = filtered

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query
        self.filter_lots()

    @rx.event
    def set_location_filter(self, location: str):
        self.location_filter = location
        self.filter_lots()