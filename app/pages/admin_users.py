"""Admin Users Management Page"""
import reflex as rx
from app.states.admin_state import AdminState
from sqlmodel import select
from app.db.models import User as DBUser
from datetime import datetime


class AdminUsersState(rx.State):
    """State for managing users"""
    users: list[dict] = []
    search_query: str = ""
    is_loading: bool = False
    
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
                        "phone": user.phone,
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
            or query in user["phone"].lower()
        ]


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
            rx.el.button(
                "View",
                class_name="text-sm text-blue-600 hover:text-blue-800 font-medium"
            ),
            class_name="px-6 py-4"
        ),
        class_name="border-b border-gray-100 hover:bg-gray-50"
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
        
        class_name="font-['Roboto']",
        on_mount=AdminUsersState.load_users,
    )
