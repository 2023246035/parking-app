"""Admin dashboard page"""
import reflex as rx
from app.states.admin_state import AdminState
from app.pages.admin_users import admin_navbar


def stat_card(title: str, value: str, icon: str, color: str = "gray") -> rx.Component:
    """Dashboard stat card"""
    colors = {
        "gray": "bg-gray-50 text-gray-900",
        "blue": "bg-blue-50 text-blue-900",
        "green": "bg-green-50 text-green-900",
        "purple": "bg-purple-50 text-purple-900",
    }
    
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                icon,
                class_name="text-3xl mb-2"
            ),
            rx.el.p(
                title,
                class_name="text-sm text-gray-600 mb-1"
            ),
            rx.el.p(
                value,
                class_name="text-3xl font-bold text-gray-900"
            ),
        ),
        class_name=f"{colors.get(color, colors['gray'])} rounded-xl p-6 border border-gray-200"
    )


def admin_dashboard() -> rx.Component:
    """Admin dashboard page"""
    return rx.el.div(
        # Header with navigation
        admin_navbar(),
        
        # Main content
        rx.el.main(
            rx.el.div(
                # Stats grid
                rx.el.div(
                    rx.el.h2(
                        "Overview",
                        class_name="text-xl font-bold text-gray-900 mb-6"
                    ),
                    
                    rx.el.div(
                        stat_card(
                            "Total Users",
                            AdminState.total_users.to_string(),
                            "👥",
                            "blue"
                        ),
                        stat_card(
                            "Total Bookings",
                            AdminState.total_bookings.to_string(),
                            "📅",
                            "purple"
                        ),
                        stat_card(
                            "Active Bookings",
                            AdminState.active_bookings.to_string(),
                            "🎯",
                            "green"
                        ),
                        stat_card(
                            "Total Revenue",
                            f"RM {AdminState.total_revenue:.0f}",
                            "💰",
                            "green"
                        ),
                        stat_card(
                            "Parking Lots",
                            AdminState.total_parking_lots.to_string(),
                            "🅿️",
                            "gray"
                        ),
                        stat_card(
                            "Avg per Booking",
                            rx.cond(
                                AdminState.total_bookings > 0,
                                f"RM {(AdminState.total_revenue / AdminState.total_bookings):.0f}",
                                "RM 0"
                            ),
                            "📊",
                            "blue"
                        ),
                        
                        class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12"
                    ),
                ),
                
                # Quick actions
                rx.el.div(
                    rx.el.h2(
                        "Quick Actions",
                        class_name="text-xl font-bold text-gray-900 mb-6"
                    ),
                    
                    rx.el.div(
                        rx.el.a(
                            rx.el.div(
                                "👥",
                                class_name="text-4xl mb-2"
                            ),
                            rx.el.h3(
                                "Manage Users",
                                class_name="text-lg font-bold text-gray-900 mb-1"
                            ),
                            rx.el.p(
                                "View and manage user accounts",
                                class_name="text-sm text-gray-600"
                            ),
                            href="/admin/users",
                            class_name="block bg-white rounded-xl p-6 border border-gray-200 hover:shadow-lg hover:border-gray-300 transition-all"
                        ),
                        
                        rx.el.a(
                            rx.el.div(
                                "📅",
                                class_name="text-4xl mb-2"
                            ),
                            rx.el.h3(
                                "Manage Bookings",
                                class_name="text-lg font-bold text-gray-900 mb-1"
                            ),
                            rx.el.p(
                                "View and manage all bookings",
                                class_name="text-sm text-gray-600"
                            ),
                            href="/admin/bookings",
                            class_name="block bg-white rounded-xl p-6 border border-gray-200 hover:shadow-lg hover:border-gray-300 transition-all"
                        ),
                        
                        rx.el.a(
                            rx.el.div(
                                "🅿️",
                                class_name="text-4xl mb-2"
                            ),
                            rx.el.h3(
                                "Manage Parking Lots",
                                class_name="text-lg font-bold text-gray-900 mb-1"
                            ),
                            rx.el.p(
                                "Add, edit, and remove parking lots",
                                class_name="text-sm text-gray-600"
                            ),
                            href="/admin/parking-lots",
                            class_name="block bg-white rounded-xl p-6 border border-gray-200 hover:shadow-lg hover:border-gray-300 transition-all"
                        ),
                        
                        class_name="grid grid-cols-1 md:grid-cols-3 gap-6"
                    ),
                ),
                
                class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12"
            ),
            class_name="bg-gray-50 min-h-screen"
        ),
        
        class_name="font-['Roboto'] min-h-screen",
        on_mount=AdminState.check_admin_auth,
    )
