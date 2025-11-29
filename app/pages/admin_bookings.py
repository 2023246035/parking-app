"""Admin Bookings Management Page"""
import reflex as rx
from sqlmodel import select
from app.db.models import Booking as DBBooking
from app.pages.admin_users import admin_navbar


class AdminBookingsState(rx.State):
    """State for managing bookings"""
    bookings: list[dict] = []
    filter_status: str = "All"
    is_loading: bool = False
    
    @rx.event
    async def load_bookings(self):
        """Load all bookings from database"""
        self.is_loading = True
        try:
            with rx.session() as session:
                db_bookings = session.exec(
                    select(DBBooking).order_by(DBBooking.created_at.desc())
                ).all()
                
                self.bookings = [
                    {
                        "id": f"BK-{booking.id}",
                        "user_name": booking.user.name if booking.user else "N/A",
                        "lot_name": booking.parking_lot.name if booking.parking_lot else "N/A",
                        "start_date": booking.start_date,
                        "start_time": booking.start_time,
                        "duration": f"{booking.duration_hours}h",
                        "total_price": f"RM {booking.total_price:.2f}",
                        "status": booking.status,
                        "payment_status": booking.payment_status,
                    }
                    for booking in db_bookings
                ]
        except Exception as e:
            print(f"Error loading bookings: {e}")
        self.is_loading = False
    
    @rx.var
    def filtered_bookings(self) -> list[dict]:
        """Filter bookings by status"""
        if self.filter_status == "All":
            return self.bookings
        return [b for b in self.bookings if b["status"] == self.filter_status]


def status_badge(status: str) -> rx.Component:
    """Status badge component"""
    colors = {
        "Confirmed": "bg-green-100 text-green-700",
        "Pending": "bg-yellow-100 text-yellow-700",
        "Cancelled": "bg-red-100 text-red-700",
        "Completed": "bg-gray-100 text-gray-700",
    }
    return rx.el.span(
        status,
        class_name=f"px-3 py-1 rounded-full text-xs font-semibold {colors.get(status, 'bg-gray-100 text-gray-700')}"
    )


def booking_row(booking: dict) -> rx.Component:
    """Booking table row"""
    return rx.el.tr(
        rx.el.td(booking["id"], class_name="px-6 py-4 font-mono text-sm"),
        rx.el.td(booking["user_name"], class_name="px-6 py-4 font-medium"),
        rx.el.td(booking["lot_name"], class_name="px-6 py-4"),
        rx.el.td(
            rx.el.div(
                rx.el.p(booking["start_date"], class_name="text-sm font-medium"),
                rx.el.p(booking["start_time"], class_name="text-xs text-gray-600"),
            ),
            class_name="px-6 py-4"
        ),
        rx.el.td(booking["duration"], class_name="px-6 py-4"),
        rx.el.td(booking["total_price"], class_name="px-6 py-4 font-semibold"),
        rx.el.td(status_badge(booking["status"]), class_name="px-6 py-4"),
        class_name="border-b border-gray-100 hover:bg-gray-50"
    )


def admin_bookings_page() -> rx.Component:
    """Admin bookings management page"""
    return rx.el.div(
        admin_navbar(),
        
        rx.el.main(
            rx.el.div(
                # Header
                rx.el.div(
                    rx.el.h1(
                        "Bookings Management",
                        class_name="text-3xl font-bold text-gray-900"
                    ),
                    rx.el.p(
                        f"{AdminBookingsState.filtered_bookings.length()} bookings",
                        class_name="text-gray-600 mt-1"
                    ),
                    class_name="mb-6"
                ),
                
                # Filters
                rx.el.div(
                    rx.el.label("Filter by status:", class_name="text-sm font-medium text-gray-700 mr-3"),
                    rx.el.select(
                        rx.el.option("All", value="All"),
                        rx.el.option("Confirmed", value="Confirmed"),
                        rx.el.option("Pending", value="Pending"),
                        rx.el.option("Completed", value="Completed"),
                        rx.el.option("Cancelled", value="Cancelled"),
                        value=AdminBookingsState.filter_status,
                        on_change=AdminBookingsState.set_filter_status,
                        class_name="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-gray-900 outline-none"
                    ),
                    class_name="flex items-center mb-6"
                ),
                
                # Bookings table
                rx.cond(
                    AdminBookingsState.is_loading,
                    rx.el.div("Loading bookings...", class_name="text-center py-12 text-gray-600"),
                    rx.cond(
                        AdminBookingsState.filtered_bookings.length() > 0,
                        rx.el.div(
                            rx.el.table(
                                rx.el.thead(
                                    rx.el.tr(
                                        rx.el.th("ID", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        rx.el.th("User", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        rx.el.th("Parking Lot", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        rx.el.th("Start", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        rx.el.th("Duration", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        rx.el.th("Price", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        rx.el.th("Status", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        class_name="bg-gray-50"
                                    ),
                                ),
                                rx.el.tbody(
                                    rx.foreach(AdminBookingsState.filtered_bookings, booking_row)
                                ),
                                class_name="w-full"
                            ),
                            class_name="bg-white rounded-lg border border-gray-200 overflow-x-auto"
                        ),
                        rx.el.div("No bookings found", class_name="text-center py-12 text-gray-600")
                    )
                ),
                
                class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12"
            ),
            class_name="bg-gray-50 min-h-screen"
        ),
        
        class_name="font-['Roboto']",
        on_mount=AdminBookingsState.load_bookings,
    )
