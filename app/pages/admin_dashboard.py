"""Admin dashboard page with beautiful modern design"""
import reflex as rx
from app.states.admin_state import AdminState
from app.pages.admin_users import admin_navbar


def stat_card(title: str, value: rx.Var, icon: str, gradient: str = "from-blue-500 to-blue-600") -> rx.Component:
    """Beautiful gradient stat card with icon - compact version"""
    return rx.el.div(
        # Gradient background layer
        rx.el.div(
            rx.el.div(
                # Icon
                rx.icon(
                    icon,
                    class_name="w-8 h-8 text-white mb-2"
                ),
                # Title
                rx.el.p(
                    title,
                    class_name="text-xs text-white/80 font-medium mb-1"
                ),
                # Value
                rx.el.p(
                    value,
                    class_name="text-2xl font-black text-white"
                ),
                class_name="relative z-10"
            ),
            class_name=f"bg-gradient-to-br {gradient} rounded-xl p-4 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 cursor-pointer"
        ),
    )


def quick_action_card(title: str, description: str, icon: str, href: str, color: str = "indigo") -> rx.Component:
    """Modern quick action card"""
    color_classes = {
        "indigo": "bg-indigo-50 hover:bg-indigo-100 border-indigo-200 text-indigo-600",
        "purple": "bg-purple-50 hover:bg-purple-100 border-purple-200 text-purple-600",
        "blue": "bg-blue-50 hover:bg-blue-100 border-blue-200 text-blue-600",
    }
    
    return rx.el.a(
        rx.el.div(
            # Icon with background
            rx.el.div(
                rx.icon(icon, class_name="w-8 h-8"),
                class_name=f"w-16 h-16 rounded-xl {color_classes[color]} flex items-center justify-center mb-4 shadow-md"
            ),
            # Title
            rx.el.h3(
                title,
                class_name="text-xl font-bold text-gray-900 mb-2"
            ),
            # Description
            rx.el.p(
                description,
                class_name="text-gray-600 text-sm"
            ),
            # Arrow icon
            rx.el.div(
                rx.icon("arrow-right", class_name="w-5 h-5"),
                class_name="absolute top-6 right-6 text-gray-400 group-hover:text-gray-600 transition-colors"
            ),
            class_name="relative"
        ),
        href=href,
        class_name="group block bg-white rounded-2xl p-6 border-2 border-gray-100 hover:border-gray-200 hover:shadow-xl transition-all duration-300 hover:scale-105"
    )


def admin_dashboard() -> rx.Component:
    """Beautiful admin dashboard page"""
    return rx.el.div(
        # Header with navigation
        admin_navbar(),
        
        # Main content
        rx.el.main(
            # Hero Header Section
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h1(
                            "Dashboard",
                            class_name="text-5xl font-black text-white mb-3"
                        ),
                        rx.el.p(
                            "Welcome back! Here's what's happening with your parking system.",
                            class_name="text-xl text-white/80"
                        ),
                    ),
                    class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16"
                ),
                class_name="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 mb-12"
            ),
            
            rx.el.div(
                # Stats Overview Section
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "📊 Key Metrics",
                            class_name="text-3xl font-black text-gray-900 mb-2"
                        ),
                        rx.el.p(
                            "Real-time overview of your parking operations",
                            class_name="text-gray-600 mb-8"
                        ),
                    ),
                    
                    # Stats Grid
                    rx.el.div(
                        stat_card(
                            "Total Users",
                            AdminState.total_users.to_string(),
                            "users",
                            "from-blue-500 to-cyan-500"
                        ),
                        stat_card(
                            "Total Bookings",
                            AdminState.total_bookings.to_string(),
                            "calendar",
                            "from-purple-500 to-pink-500"
                        ),
                        stat_card(
                            "Active Bookings",
                            AdminState.active_bookings.to_string(),
                            "zap",
                            "from-green-500 to-emerald-500"
                        ),
                        stat_card(
                            "Total Revenue",
                            rx.cond(
                                AdminState.total_revenue > 0,
                                f"RM {AdminState.total_revenue:.0f}",
                                "RM 0"
                            ),
                            "dollar-sign",
                            "from-amber-500 to-orange-500"
                        ),
                        stat_card(
                            "Parking Lots",
                            AdminState.total_parking_lots.to_string(),
                            "map-pin",
                            "from-indigo-500 to-purple-500"
                        ),
                        stat_card(
                            "Avg per Booking",
                            rx.cond(
                                AdminState.total_bookings > 0,
                                f"RM {(AdminState.total_revenue / AdminState.total_bookings):.0f}",
                                "RM 0"
                            ),
                            "trending-up",
                            "from-rose-500 to-red-500"
                        ),
                        
                        class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16"
                    ),
                ),
                
                # Quick Actions Section
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "⚡ Quick Actions",
                            class_name="text-3xl font-black text-gray-900 mb-2"
                        ),
                        rx.el.p(
                            "Manage your parking system with ease",
                            class_name="text-gray-600 mb-8"
                        ),
                    ),
                    
                    rx.el.div(
                        quick_action_card(
                            "Manage Users",
                            "View, search, and manage all user accounts",
                            "users",
                            "/admin/users",
                            "indigo"
                        ),
                        quick_action_card(
                            "Manage Bookings",
                            "Monitor and control all parking reservations",
                            "calendar-check",
                            "/admin/bookings",
                            "purple"
                        ),
                        quick_action_card(
                            "Manage Parking Lots",
                            "Add, edit, and organize parking locations",
                            "map-pin",
                            "/admin/parking-lots",
                            "blue"
                        ),
                        
                        class_name="grid grid-cols-1 md:grid-cols-3 gap-6"
                    ),
                ),
                
                # Additional Info Section
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.icon("info", class_name="w-6 h-6 text-blue-600 mr-3"),
                            rx.el.div(
                                rx.el.p(
                                    "System Status",
                                    class_name="font-bold text-gray-900 mb-1"
                                ),
                                rx.el.p(
                                    "All systems operational. Database connected and syncing.",
                                    class_name="text-sm text-gray-600"
                                ),
                            ),
                            class_name="flex items-start"
                        ),
                        class_name="bg-blue-50 border-2 border-blue-200 rounded-2xl p-6 mt-12"
                    ),
                ),
                
                class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12"
            ),
        ),
        
        class_name="font-['Roboto'] min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50",
        on_mount=AdminState.check_admin_auth,
    )
