"""Admin Parking Lots Management Page"""
import reflex as rx
from sqlmodel import select
from app.db.models import ParkingLot as DBParkingLot
from app.pages.admin_users import admin_navbar


class AdminParkingLotsState(rx.State):
    """State for managing parking lots"""
    parking_lots: list[dict] = []
    is_loading: bool = False
    
    # Modal State
    show_modal: bool = False
    modal_mode: str = "add"  # "add" or "edit"
    editing_lot_id: int = 0
    
    # Form Fields
    form_name: str = ""
    form_location: str = ""
    form_price: str = ""
    form_total_spots: str = ""
    form_rating: str = "5.0"
    
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
                        "occupancy_percent": int((lot.total_spots - lot.available_spots) / lot.total_spots * 100) if lot.total_spots > 0 else 0,
                        "rating": f"{lot.rating:.1f}⭐",
                    }
                    for lot in db_lots
                ]
        except Exception as e:
            print(f"Error loading parking lots: {e}")
        self.is_loading = False

    @rx.event
    def open_add_modal(self):
        """Open modal for adding a new lot"""
        self.modal_mode = "add"
        self.form_name = ""
        self.form_location = ""
        self.form_price = ""
        self.form_total_spots = ""
        self.form_rating = "5.0"
        self.show_modal = True

    @rx.event
    def open_edit_modal(self, lot: dict):
        """Open modal for editing an existing lot"""
        self.modal_mode = "edit"
        self.editing_lot_id = lot["id"]
        self.form_name = lot["name"]
        self.form_location = lot["location"]
        # Extract numeric value from "RM X.XX" format
        self.form_price = lot["price_per_hour"].replace("RM ", "")
        self.form_total_spots = str(lot["total_spots"])
        # Extract numeric rating from "X.X⭐" format
        self.form_rating = lot["rating"].replace("⭐", "")
        self.show_modal = True

    @rx.event
    def close_modal(self):
        self.show_modal = False

    @rx.event
    def set_form_name(self, value: str):
        self.form_name = value

    @rx.event
    def set_form_location(self, value: str):
        self.form_location = value

    @rx.event
    def set_form_price(self, value):
        self.form_price = str(value)

    @rx.event
    def set_form_total_spots(self, value):
        self.form_total_spots = str(value)

    @rx.event
    async def save_parking_lot(self):
        """Save (create or update) parking lot"""
        try:
            price = float(self.form_price) if self.form_price else 0.0
            spots = int(self.form_total_spots) if self.form_total_spots else 0
            rating = float(self.form_rating) if self.form_rating else 5.0
            
            with rx.session() as session:
                if self.modal_mode == "add":
                    new_lot = DBParkingLot(
                        name=self.form_name,
                        location=self.form_location,
                        price_per_hour=price,
                        total_spots=spots,
                        available_spots=spots,  # Default to full availability
                        rating=rating,
                        image_url="https://images.unsplash.com/photo-1506521781263-d8422e82f27a?auto=format&fit=crop&w=800&q=80",
                        features="24/7 Security,Covered Parking,EV Charging"  # Default features
                    )
                    session.add(new_lot)
                    session.commit()
                    yield rx.toast.success("Parking lot created successfully!")
                
                else:
                    lot = session.get(DBParkingLot, self.editing_lot_id)
                    if lot:
                        lot.name = self.form_name
                        lot.location = self.form_location
                        lot.price_per_hour = price
                        
                        # Adjust available spots if total spots changed
                        diff = spots - lot.total_spots
                        lot.total_spots = spots
                        lot.available_spots = max(0, lot.available_spots + diff)
                        lot.rating = rating
                        
                        session.add(lot)
                        session.commit()
                        yield rx.toast.success("Parking lot updated successfully!")
            
            self.show_modal = False
            yield AdminParkingLotsState.load_parking_lots
            
        except Exception as e:
            print(f"Error saving parking lot: {e}")
            yield rx.toast.error(f"Failed to save parking lot: {str(e)}")

    @rx.event
    async def delete_parking_lot(self, lot_id: int):
        """Delete a parking lot"""
        try:
            with rx.session() as session:
                lot = session.get(DBParkingLot, lot_id)
                if lot:
                    # Check if there are any bookings associated with this lot
                    from app.db.models import Booking as DBBooking
                    bookings_count = session.exec(
                        select(DBBooking).where(DBBooking.lot_id == lot_id)
                    ).all()
                    
                    if len(bookings_count) > 0:
                        yield rx.toast.error(
                            f"Cannot delete {lot.name}. It has {len(bookings_count)} associated booking(s). "
                            "Please cancel or complete all bookings first."
                        )
                        return
                    
                    session.delete(lot)
                    session.commit()
                    yield rx.toast.success(f"{lot.name} deleted successfully.")
                    yield AdminParkingLotsState.load_parking_lots
                else:
                    yield rx.toast.error("Parking lot not found.")
        except Exception as e:
            print(f"Error deleting parking lot: {e}")
            yield rx.toast.error(f"Failed to delete parking lot: {str(e)}")


def parking_lot_row(lot: dict) -> rx.Component:
    """Parking lot table row - simplified without dynamic color bar"""
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.el.p(lot["name"], class_name="font-semibold text-gray-900"),
                rx.el.p(lot["location"], class_name="text-sm text-gray-600"),
            ),
            class_name="px-6 py-4"
        ),
        rx.el.td(
            lot["price_per_hour"], 
            class_name="px-6 py-4 font-semibold"
        ),
        rx.el.td(
            f"{lot['available_spots']}/{lot['total_spots']}",
            class_name="px-6 py-4 font-medium"
        ),
        rx.el.td(
            f"{lot['occupancy_percent']}%",
            class_name="px-6 py-4"
        ),
        rx.el.td(
            lot["rating"], 
            class_name="px-6 py-4"
        ),
        rx.el.td(
            rx.el.div(
                rx.el.button(
                    "Edit",
                    on_click=AdminParkingLotsState.open_edit_modal(lot),
                    class_name="text-sm text-blue-600 hover:text-blue-800 font-medium mr-4"
                ),
                rx.el.button(
                    "Delete",
                    on_click=AdminParkingLotsState.delete_parking_lot(lot["id"]),
                    class_name="text-sm text-red-600 hover:text-red-800 font-medium"
                ),
                class_name="flex items-center"
            ),
            class_name="px-6 py-4"
        ),
        class_name="border-b border-gray-100 hover:bg-gray-50"
    )


def parking_lot_modal() -> rx.Component:
    """Modal for adding/editing parking lots"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                rx.cond(
                    AdminParkingLotsState.modal_mode == "add",
                    "Add New Parking Lot",
                    "Edit Parking Lot"
                ),
                class_name="text-2xl font-bold text-gray-900 mb-4"
            ),
            
            rx.el.div(
                rx.el.div(
                    rx.el.label("Name", class_name="block text-sm font-medium text-gray-700 mb-1"),
                    rx.el.input(
                        value=AdminParkingLotsState.form_name,
                        on_change=AdminParkingLotsState.set_form_name,
                        placeholder="e.g. Sunway Pyramid Zone A",
                        class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    ),
                    class_name="mb-4"
                ),
                rx.el.div(
                    rx.el.label("Location", class_name="block text-sm font-medium text-gray-700 mb-1"),
                    rx.el.input(
                        value=AdminParkingLotsState.form_location,
                        on_change=AdminParkingLotsState.set_form_location,
                        placeholder="e.g. Bandar Sunway, Petaling Jaya",
                        class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    ),
                    class_name="mb-4"
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label("Price per Hour (RM)", class_name="block text-sm font-medium text-gray-700 mb-1"),
                        rx.el.input(
                            value=AdminParkingLotsState.form_price,
                            on_change=AdminParkingLotsState.set_form_price,
                            type="number",
                            step="0.50",
                            placeholder="e.g. 5.00",
                            class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                        ),
                    ),
                    rx.el.div(
                        rx.el.label("Total Spots", class_name="block text-sm font-medium text-gray-700 mb-1"),
                        rx.el.input(
                            value=AdminParkingLotsState.form_total_spots,
                            on_change=AdminParkingLotsState.set_form_total_spots,
                            type="number",
                            placeholder="e.g. 100",
                            class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                        ),
                    ),
                    class_name="grid grid-cols-2 gap-4 mb-6"
                ),
                
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        on_click=AdminParkingLotsState.close_modal,
                        class_name="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 mr-2"
                    ),
                    rx.el.button(
                        "Save",
                        on_click=AdminParkingLotsState.save_parking_lot,
                        class_name="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700"
                    ),
                    class_name="flex justify-end"
                )
            ),
        ),
        open=AdminParkingLotsState.show_modal,
        on_open_change=AdminParkingLotsState.close_modal,
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
                        on_click=AdminParkingLotsState.open_add_modal,
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
        
        parking_lot_modal(),
        
        class_name="font-['Roboto']",
        on_mount=AdminParkingLotsState.load_parking_lots,
    )
