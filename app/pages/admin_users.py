"""Admin Users Management Page"""
import reflex as rx
from app.states.admin_state import AdminState
from sqlmodel import select
from app.db.models import User as DBUser, Booking as DBBooking, ParkingLot as DBParkingLot


class AdminUsersState(rx.State):
    """State for managing users"""
    users: list[dict] = []
    search_query: str = ""
    is_loading: bool = False
    
    # Modal State
    show_modal: bool = False
    selected_user: dict = {}
    user_bookings: list[dict] = []
    
    # Delete Confirmation State
    show_delete_confirm: bool = False
    user_to_delete: dict = {}
    
    @rx.event
    async def load_users(self):
        """Load all users from database"""
        self.is_loading = True
        try:
            with rx.session() as session:
                db_users = session.exec(select(DBUser)).all()
                self.users = [
                    {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "phone": user.phone or "N/A",
                        "member_since": user.member_since.strftime("%Y-%m-%d"),
                        "total_bookings": len(user.bookings),
                    }
                    for user in db_users
                ]
        except Exception as e:
            print(f"Error loading users: {e}")
        self.is_loading = False
    
    @rx.var
    def filtered_users(self) -> list[dict]:
        """Filter users by search query"""
        if not self.search_query:
            return self.users
        
        query = self.search_query.lower()
        return [
            user for user in self.users
            if query in user["name"].lower() 
            or query in user["email"].lower()
            or query in str(user["phone"]).lower()
        ]

    @rx.event
    def set_search_query(self, value: str):
        self.search_query = value

    @rx.event
    async def view_user(self, user: dict):
        """View user details"""
        self.selected_user = user
        self.show_modal = True
        
        # Load user bookings
        try:
            with rx.session() as session:
                bookings = session.exec(
                    select(DBBooking)
                    .where(DBBooking.user_id == user["id"])
                    .order_by(DBBooking.created_at.desc())
                    .limit(10)
                ).all()
                
                self.user_bookings = []
                for b in bookings:
                    lot = session.get(DBParkingLot, b.lot_id)
                    lot_name = lot.name if lot else "Unknown Lot"
                    self.user_bookings.append({
                        "lot_name": lot_name,
                        "date": b.start_date,
                        "time": b.start_time,
                        "price": f"RM {b.total_price:.2f}",
                        "status": b.status
                    })
                    
        except Exception as e:
            print(f"Error loading user bookings: {e}")

    @rx.event
    def close_modal(self):
        self.show_modal = False
    
    @rx.event
    def confirm_delete_user(self, user: dict):
        """Show delete confirmation dialog"""
        self.user_to_delete = user
        self.show_delete_confirm = True
    
    @rx.event
    def cancel_delete(self):
        """Cancel delete operation"""
        self.show_delete_confirm = False
        self.user_to_delete = {}
    
    @rx.event
    async def delete_user(self):
        """Delete user from database"""
        try:
            user_id = self.user_to_delete.get("id")
            if not user_id:
                return
            
            with rx.session() as session:
                user = session.get(DBUser, user_id)
                if user:
                    user_email = user.email
                    session.delete(user)
                    session.commit()
                    print(f"✅ User {user_email} (ID: {user_id}) deleted successfully")
                    
                    # Close dialog and reload users
                    self.show_delete_confirm = False
                    self.user_to_delete = {}
                    await self.load_users()
                else:
                    print(f"❌ User with ID {user_id} not found")
                    
        except Exception as e:
            print(f"❌ Error deleting user: {e}")
            import traceback
            traceback.print_exc()


def admin_navbar() -> rx.Component:
    """Admin navigation bar"""
    return rx.el.header(
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    "🔐 Admin Portal",
                    href="/admin/dashboard",
                    class_name="text-xl font-bold text-gray-900"
                ),
                rx.el.div(
                    rx.el.a(
                        "Dashboard",
                        href="/admin/dashboard",
                        class_name="text-sm font-medium text-gray-600 hover:text-gray-900 px-3 py-2"
                    ),
                    rx.el.a(
                        "Analytics",
                        href="/admin/analytics",
                        class_name="text-sm font-medium text-gray-600 hover:text-gray-900 px-3 py-2"
                    ),
                    rx.el.a(
                        "Users",
                        href="/admin/users",
                        class_name="text-sm font-medium text-gray-600 hover:text-gray-900 px-3 py-2"
                    ),
                    rx.el.a(
                        "Bookings",
                        href="/admin/bookings",
                        class_name="text-sm font-medium text-gray-600 hover:text-gray-900 px-3 py-2"
                    ),
                    rx.el.a(
                        "Parking Lots",
                        href="/admin/parking-lots",
                        class_name="text-sm font-medium text-gray-600 hover:text-gray-900 px-3 py-2"
                    ),
                    rx.el.a(
                        "Refunds",
                        href="/admin/refunds",
                        class_name="text-sm font-medium text-gray-600 hover:text-gray-900 px-3 py-2"
                    ),
                    class_name="flex items-center gap-2"
                ),
                class_name="flex items-center gap-8"
            ),
            rx.el.button(
                "Logout",
                on_click=AdminState.admin_logout,
                class_name="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 font-medium text-sm"
            ),
            class_name="flex items-center justify-between max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4"
        ),
        class_name="bg-white border-b border-gray-200 sticky top-0 z-50"
    )


def user_row(user: dict) -> rx.Component:
    """User table row"""
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.el.p(user["name"], class_name="font-semibold text-gray-900"),
                rx.el.p(user["email"], class_name="text-sm text-gray-600"),
            ),
            class_name="px-6 py-4"
        ),
        rx.el.td(
            user["phone"],
            class_name="px-6 py-4 text-gray-900"
        ),
        rx.el.td(
            user["member_since"],
            class_name="px-6 py-4 text-gray-600"
        ),
        rx.el.td(
            rx.el.span(
                f"{user['total_bookings']} bookings",
                class_name="text-sm font-medium text-blue-600"
            ),
            class_name="px-6 py-4"
        ),
        rx.el.td(
            rx.el.div(
                rx.el.button(
                    "View",
                    on_click=AdminUsersState.view_user(user),
                    class_name="text-sm text-blue-600 hover:text-blue-800 font-medium mr-3"
                ),
                rx.el.button(
                    "Delete",
                    on_click=AdminUsersState.confirm_delete_user(user),
                    class_name="text-sm text-red-600 hover:text-red-800 font-medium"
                ),
                class_name="flex items-center gap-2"
            ),
            class_name="px-6 py-4"
        ),
        class_name="border-b border-gray-100 hover:bg-gray-50"
    )


def booking_row(booking: dict) -> rx.Component:
    """Booking history row in user details modal"""
    return rx.el.div(
        rx.el.div(
            rx.el.p(booking["lot_name"], class_name="font-semibold text-gray-900"),
            rx.el.p(
                f"{booking['date']} at {booking['time']}", 
                class_name="text-sm text-gray-500"
            ),
        ),
        rx.el.div(
            rx.el.p(booking["price"], class_name="font-medium text-gray-900"),
            rx.el.span(
                booking["status"],
                class_name=rx.cond(
                    booking["status"] == "Confirmed",
                    "text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full",
                    "text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded-full"
                )
            ),
            class_name="text-right"
        ),
        class_name="flex justify-between items-center py-3  border-b border-gray-100 last:border-0"
    )


def user_details_modal() -> rx.Component:
    """Modal for viewing user details"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "User Details",
                class_name="text-2xl font-bold text-gray-900 mb-4"
            ),
            
            rx.el.div(
                # User Info
                rx.el.div(
                    rx.el.div(
                        rx.el.p("Name", class_name="text-sm text-gray-500"),
                        rx.el.p(AdminUsersState.selected_user["name"], class_name="font-medium text-gray-900"),
                        class_name="mb-3"
                    ),
                    rx.el.div(
                        rx.el.p("Email", class_name="text-sm text-gray-500"),
                        rx.el.p(AdminUsersState.selected_user["email"], class_name="font-medium text-gray-900"),
                        class_name="mb-3"
                    ),
                    rx.el.div(
                        rx.el.p("Phone", class_name="text-sm text-gray-500"),
                        rx.el.p(AdminUsersState.selected_user["phone"], class_name="font-medium text-gray-900"),
                        class_name="mb-3"
                    ),
                    rx.el.div(
                        rx.el.p("Member Since", class_name="text-sm text-gray-500"),
                        rx.el.p(AdminUsersState.selected_user["member_since"], class_name="font-medium text-gray-900"),
                    ),
                    class_name="grid grid-cols-2 gap-4 mb-6 p-4 bg-gray-50 rounded-lg"
                ),
                
                # Recent Bookings
                rx.el.h3("Recent Bookings", class_name="text-lg font-bold text-gray-900 mb-3"),
                rx.cond(
                    AdminUsersState.user_bookings.length() > 0,
                    rx.el.div(
                        rx.foreach(
                            AdminUsersState.user_bookings,
                            booking_row
                        ),
                        class_name="border border-gray-200 rounded-lg px-4"
                    ),
                    rx.el.p("No bookings found.", class_name="text-gray-500 italic")
                ),
                
                rx.el.div(
                    rx.el.button(
                        "Close",
                        on_click=AdminUsersState.close_modal,
                        class_name="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 mt-6 w-full"
                    ),
                )
            ),
            class_name="max-w-lg"
        ),
        open=AdminUsersState.show_modal,
        on_open_change=AdminUsersState.close_modal,
    )


def delete_confirmation_dialog() -> rx.Component:
    """Confirmation dialog for deleting users"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "⚠️ Delete User",
                class_name="text-2xl font-bold text-red-600 mb-4"
            ),
            
            rx.el.div(
                # Warning message
                rx.el.div(
                    rx.icon("alert-triangle", class_name="w-12 h-12 text-red-500 mx-auto mb-4"),
                    rx.el.p(
                        "Are you sure you want to delete this user?",
                        class_name="text-lg font-semibold text-gray-900 text-center mb-2"
                    ),
                    rx.el.p(
                        f"User: {AdminUsersState.user_to_delete['name']}",
                        class_name="text-gray-700 text-center mb-1"
                    ),
                    rx.el.p(
                        f"Email: {AdminUsersState.user_to_delete['email']}",
                        class_name="text-gray-600 text-center mb-4"
                    ),
                    rx.el.div(
                        rx.el.p(
                            "⚠️ This action cannot be undone!",
                            class_name="text-red-600 font-semibold text-center"
                        ),
                        rx.el.p(
                            "All user data and bookings will be permanently deleted.",
                            class_name="text-sm text-gray-600 text-center mt-1"
                        ),
                        class_name="bg-red-50 border border-red-200 rounded-lg p-3 mt-4"
                    ),
                ),
                
                # Action buttons
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        on_click=AdminUsersState.cancel_delete,
                        class_name="flex-1 px-4 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 font-semibold"
                    ),
                    rx.el.button(
                        "Delete User",
                        on_click=AdminUsersState.delete_user,
                        class_name="flex-1 px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-semibold"
                    ),
                    class_name="flex gap-3 mt-6"
                ),
            ),
            class_name="max-w-md"
        ),
        open=AdminUsersState.show_delete_confirm,
        on_open_change=AdminUsersState.cancel_delete,
    )


def admin_users_page() -> rx.Component:
    """Admin users management page"""
    return rx.el.div(
        admin_navbar(),
        
        rx.el.main(
            rx.el.div(
                # Header
                rx.el.div(
                    rx.el.h1(
                        "User Management",
                        class_name="text-3xl font-bold text-gray-900"
                    ),
                    rx.el.p(
                        f"{AdminUsersState.filtered_users.length()} total users",
                        class_name="text-gray-600 mt-1"
                    ),
                    class_name="mb-6"
                ),
                
                # Search bar
                rx.el.div(
                    rx.el.input(
                        placeholder="Search by name, email, or phone...",
                        value=AdminUsersState.search_query,
                        on_change=AdminUsersState.set_search_query,
                        class_name="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-gray-900 focus:border-transparent outline-none"
                    ),
                    class_name="mb-6"
                ),
                
                # Users table
                rx.cond(
                    AdminUsersState.is_loading,
                    rx.el.div(
                        "Loading users...",
                        class_name="text-center py-12 text-gray-600"
                    ),
                    rx.cond(
                        AdminUsersState.filtered_users.length() > 0,
                        rx.el.div(
                            rx.el.table(
                                rx.el.thead(
                                    rx.el.tr(
                                        rx.el.th("User", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        rx.el.th("Phone", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        rx.el.th("Member Since", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        rx.el.th("Bookings", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        rx.el.th("Actions", class_name="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase"),
                                        class_name="bg-gray-50"
                                    ),
                                ),
                                rx.el.tbody(
                                    rx.foreach(AdminUsersState.filtered_users, user_row)
                                ),
                                class_name="w-full"
                            ),
                            class_name="bg-white rounded-lg border border-gray-200 overflow-hidden"
                        ),
                        rx.el.div(
                            "No users found",
                            class_name="text-center py-12 text-gray-600"
                        )
                    )
                ),
                
                class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12"
            ),
            class_name="bg-gray-50 min-h-screen"
        ),
        
        user_details_modal(),
        delete_confirmation_dialog(),
        
        class_name="font-['Roboto']",
        on_mount=AdminUsersState.load_users,
    )
