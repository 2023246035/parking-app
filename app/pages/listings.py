import reflex as rx
from app.components.navbar import navbar
from app.components.footer import footer
from app.components.parking_card import parking_card, loading_card
from app.components.slot_booking_modal import slot_booking_modal
from app.components.payment_modal import payment_modal
from app.states.parking_state import ParkingState


def compact_header() -> rx.Component:
    """Compact header section"""
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "Discover ",
                rx.el.span(
                    "Premium Parking",
                    class_name="text-transparent bg-clip-text bg-gradient-to-r from-sky-500 to-blue-600"
                ),
                class_name="text-3xl md:text-4xl font-black text-gray-900 mb-2"
            ),
            rx.el.p(
                "Real-time availability • Secure booking",
                class_name="text-sm text-gray-600"
            ),
            class_name="text-center max-w-7xl mx-auto px-6 py-6"
        ),
        class_name="bg-gradient-to-br from-sky-50 to-white border-b border-gray-100"
    )


def search_bar() -> rx.Component:
    """Search bar with filter toggle"""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(
                    "search",
                    class_name="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-sky-500"
                ),
                rx.el.input(
                    placeholder="Search parking...",
                    value=ParkingState.search_query,
                    class_name="w-full pl-12 pr-4 py-3.5 rounded-xl ring-2 ring-gray-200 focus:ring-sky-500 outline-none bg-white",
                    on_change=ParkingState.set_search_query,
                ),
                class_name="relative flex-1"
            ),
            rx.el.button(
                rx.icon(
                    rx.cond(ParkingState.show_filters, "x", "sliders-horizontal"),
                    class_name="h-5 w-5"
                ),
                on_click=ParkingState.toggle_filters,
                class_name=rx.cond(
                    ParkingState.show_filters,
                    "px-4 py-3.5 rounded-xl bg-sky-500 text-white hover:bg-sky-600 transition-all",
                    "px-4 py-3.5 rounded-xl bg-white ring-2 ring-gray-200 hover:ring-sky-500 transition-all"
                )
            ),
            class_name="flex gap-3 max-w-4xl mx-auto"
        ),
        
        # Collapsible filters
        rx.cond(
            ParkingState.show_filters,
            rx.el.div(
                rx.el.div(
                    # Location
                    rx.el.div(
                        rx.el.label("Location", class_name="text-xs font-bold text-gray-700 mb-2 block"),
                        rx.el.select(
                            rx.el.option("All", value="All"),
                            rx.el.option("KL City", value="Kuala Lumpur"),
                            rx.el.option("Bukit Bintang", value="Bukit Bintang"),
                            rx.el.option("Bangsar", value="Bangsar"),
                            rx.el.option("Mid Valley", value="Mid Valley"),
                            value=ParkingState.location_filter,
                            class_name="w-full px-3 py-2 rounded-lg ring-1 ring-gray-200 focus:ring-sky-500 outline-none bg-white cursor-pointer",
                            on_change=ParkingState.set_location_filter,
                        ),
                        class_name="bg-gray-50 p-4 rounded-xl"
                    ),
                    
                    # Price
                    rx.el.div(
                        rx.el.label("Price (RM/hr)", class_name="text-xs font-bold text-gray-700 mb-2 block"),
                        rx.el.div(
                            rx.el.input(
                                type="number",
                                placeholder="Min",
                                value=ParkingState.min_price,
                                class_name="w-full px-3 py-2 rounded-lg ring-1 ring-gray-200 focus:ring-sky-500 outline-none bg-white",
                                on_change=ParkingState.set_min_price,
                            ),
                            rx.el.input(
                                type="number",
                                placeholder="Max",
                                value=ParkingState.max_price,
                                class_name="w-full px-3 py-2 rounded-lg ring-1 ring-gray-200 focus:ring-sky-500 outline-none bg-white",
                                on_change=ParkingState.set_max_price,
                            ),
                            class_name="flex gap-2"
                        ),
                        class_name="bg-gray-50 p-4 rounded-xl"
                    ),
                    
                    # Sort
                    rx.el.div(
                        rx.el.label("Sort By", class_name="text-xs font-bold text-gray-700 mb-2 block"),
                        rx.el.select(
                            rx.el.option("Default", value="default"),
                            rx.el.option("Price: Low-High", value="price_low"),
                            rx.el.option("Price: High-Low", value="price_high"),
                            rx.el.option("Rating", value="rating"),
                            rx.el.option("Availability", value="availability"),
                            value=ParkingState.sort_by,
                            class_name="w-full px-3 py-2 rounded-lg ring-1 ring-gray-200 focus:ring-sky-500 outline-none bg-white cursor-pointer",
                            on_change=ParkingState.set_sort_by,
                        ),
                        class_name="bg-gray-50 p-4 rounded-xl"
                    ),
                    
                    # Actions
                    rx.el.div(
                        rx.el.button(
                            rx.icon(
                                rx.cond(ParkingState.show_available_only, "check-circle", "circle"),
                                class_name="h-4 w-4 mr-1.5"
                            ),
                            "Available",
                            on_click=ParkingState.toggle_available_only,
                            class_name=rx.cond(
                                ParkingState.show_available_only,
                                "px-3 py-2 rounded-lg bg-green-500 text-white text-sm font-semibold",
                                "px-3 py-2 rounded-lg bg-white ring-1 ring-gray-200 text-sm font-semibold"
                            )
                        ),
                        rx.el.button(
                            rx.icon("rotate-ccw", class_name="h-4 w-4 mr-1.5"),
                            "Reset",
                            on_click=ParkingState.reset_filters,
                            class_name="px-3 py-2 rounded-lg bg-white ring-1 ring-gray-200 hover:ring-sky-500 text-sm font-semibold"
                        ),
                        class_name="flex gap-2 bg-gray-50 p-4 rounded-xl"
                    ),
                    
                    class_name="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4 max-w-4xl mx-auto"
                ),
                class_name="animate-in fade-in slide-in-from-top-2 duration-300"
            ),
            rx.fragment()
        ),
        
        class_name="bg-white border-b border-gray-100 px-6 py-5 sticky top-16 z-40 shadow-sm"
    )


def results_grid() -> rx.Component:
    """Parking results grid"""
    return rx.el.div(
        # Count
        rx.el.p(
            rx.el.span(
                ParkingState.filtered_lots.length(),
                class_name="font-bold text-sky-600 text-xl"
            ),
            " parking spots found",
            class_name="text-gray-600 mb-6"
        ),
        
        # Grid
        rx.cond(
            ParkingState.is_loading,
            rx.el.div(
                rx.foreach(rx.Var.range(6), lambda i: loading_card()),
                class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            ),
            rx.cond(
                ParkingState.filtered_lots.length() > 0,
                rx.el.div(
                    rx.foreach(ParkingState.filtered_lots, parking_card),
                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                ),
                rx.el.div(
                    rx.icon("search-x", class_name="h-16 w-16 text-gray-300 mb-4"),
                    rx.el.h3("No results", class_name="text-xl font-bold text-gray-900 mb-2"),
                    rx.el.p("Try different filters", class_name="text-gray-500 mb-4"),
                    rx.el.button(
                        "Reset Filters",
                        on_click=ParkingState.reset_filters,
                        class_name="px-6 py-3 bg-sky-500 text-white rounded-xl hover:bg-sky-600 font-semibold"
                    ),
                    class_name="flex flex-col items-center justify-center py-20 text-center"
                )
            )
        ),
        
        class_name="max-w-7xl mx-auto px-6 py-8"
    )


def listings_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        compact_header(),
        search_bar(),
        
        rx.el.main(
            results_grid(),
            class_name="bg-gray-50 min-h-screen"
        ),
        
        slot_booking_modal(),
        payment_modal(),
        footer(),
        
        class_name="font-['Roboto'] min-h-screen flex flex-col",
        on_mount=ParkingState.on_load,
    )
