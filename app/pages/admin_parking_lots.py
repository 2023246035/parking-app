"""Admin Parking Lots Management Page"""
import reflex as rx
from sqlmodel import select
from app.db.models import ParkingLot as DBParkingLot
from app.pages.admin_users import admin_navbar


class AdminParkingLotsState(rx.State):
    """State for managing parking lots"""
    parking_lots: list[dict] = []
    is_loading: bool = False
    show_add_modal: bool = False
    
    @rx.event
    async def load_parking_lots(self):
        """Load all parking lots from database"""
        self.is_loading = True
        try:
            with rx.session() as session:
                db_lots = session.exec(select(DBParkingLot)).all()
                
                self.parking_lots = [
                    {
                        "id": lot.id,
                        "name": lot.name,
                        "location": lot.location,
                        "price_per_hour": f"RM {lot.price_per_hour:.2f}",
                        "total_spots": lot.total_spots,
                        "available_spots": lot.available_spots,
                        "occupancy": int((lot.total_spots - lot.available_spots) / lot.total_spots * 100) if lot.total_spots > 0 else 0,
                        "occupancy_color": "bg-green-500" if (int((lot.total_spots - lot.available_spots) / lot.total_spots * 100) if lot.total_spots > 0 else 0) < 50 else "bg-yellow-500" if (int((lot.total_spots - lot.available_spots) / lot.total_spots * 100) if lot.total_spots > 0 else 0) < 80 else "bg-red-500",
                        "rating": f"{lot.rating:.1f}⭐",
                    }
                    for lot in db_lots
                ]
        except Exception as e:
            print(f"Error loading parking lots: {e}")
        self.is_loading = False


def occupancy_bar(occupancy, color) -> rx.Component:
    """Occupancy progress bar"""
    return rx.el.div(
        rx.el.div(
            class_name=f"h-2 {color} rounded-full",
            style={"width": f"{occupancy}%"}
        ),
        rx.el.span(
            f"{occupancy}%",
            class_name="text-xs text-gray-600 ml-2"
        ),
        class_name="flex items-center w-full"
    )


def parking_lot_row(lot: dict) -> rx.Component:
    """Parking lot table row"""
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.el.p(lot["name"], class_name="font-semibold text-gray-900"),
                rx.el.p(lot["location"], class_name="text-sm text-gray-600"),
            ),
            class_name="px-6 py-4"
        ),
        rx.el.td(lot["price_per_hour"], class_name="px-6 py-4 font-semibold"),
        rx.el.td(
            f"{lot['available_spots']}/{lot['total_spots']}",
            class_name="px-6 py-4 font-medium"
        ),
        rx.el.td(
            occupancy_bar(lot["occupancy"], lot["occupancy_color"]),
            class_name="px-6 py-4"
        ),
        rx.el.td(lot["rating"], class_name="px-6 py-4"),
        rx.el.td(
            rx.el.div(
                rx.el.button(
                    "Edit",
                    class_name="text-sm text-blue-600 hover:text-blue-800 font-medium mr-4"
                ),
                rx.el.button(
                    "Delete",
                    class_name="text-sm text-red-600 hover:text-red-800 font-medium"
                ),
                class_name="flex items-center"
            ),
            class_name="px-6 py-4"
        ),
        class_name="border-b border-gray-100 hover:bg-gray-50"
    )


def admin_parking_lots_page() -> rx.Component:
    """Admin parking lots management page"""
    return rx.el.div(
        admin_navbar(),
        
        rx.el.main(
            rx.el.div(
                # Header
                rx.el.div(
                    rx.el.div(
                        rx.el.h1(
                            "Parking Lots Management",
                            class_name="text-3xl font-bold text-gray-900"
                        ),
                        rx.el.p(
                            f"{AdminParkingLotsState.parking_lots.length()} total parking lots",
                            class_name="text-gray-600 mt-1"
                        ),
                    ),
                    rx.el.button(
                        "+ Add New Lot",
                        class_name="px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 font-semibold"
                    ),
                    class_name="flex items-center justify-between mb-6"
                ),
                
                # Parking lots table
                rx.cond(
                    AdminParkingLotsState.is_loading,
                    rx.el.div("Loading parking lots...", class_name="text-center py-12 text-gray-600"),
                    rx.cond(
                        AdminParkingLotsState.parking_lots.length() > 0,
                        rx.el.div(
                            rx.el.table(
                                rx.el.thead(
                                    rx.el.tr(
                                        rx.el.th("Parking Lot", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        rx.el.th("Price/Hour", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        rx.el.th("Spots", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        rx.el.th("Occupancy", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        rx.el.th("Rating", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        rx.el.th("Actions", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        class_name="bg-gray-50"
                                    ),
                                ),
                                rx.el.tbody(
                                    rx.foreach(AdminParkingLotsState.parking_lots, parking_lot_row)
                                ),
                                class_name="w-full"
                            ),
                            class_name="bg-white rounded-lg border border-gray-200 overflow-x-auto"
                        ),
                        rx.el.div("No parking lots found", class_name="text-center py-12 text-gray-600")
                    )
                ),
                
                class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12"
            ),
            class_name="bg-gray-50 min-h-screen"
        ),
        
        class_name="font-['Roboto']",
        on_mount=AdminParkingLotsState.load_parking_lots,
    )
