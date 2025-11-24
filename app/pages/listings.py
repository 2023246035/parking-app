import reflex as rx
from app.components.navbar import navbar
from app.components.footer import footer
from app.components.parking_card import parking_card, loading_card
from app.components.booking_modal import booking_modal
from app.components.payment_modal import payment_modal
from app.states.parking_state import ParkingState


def search_filter_bar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(
                    "search",
                    class_name="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400",
                ),
                rx.el.input(
                    placeholder="Search by location or name...",
                    class_name="w-full pl-12 pr-4 py-4 rounded-2xl border-0 ring-1 ring-gray-200 focus:ring-2 focus:ring-sky-500 shadow-sm transition-all outline-none text-gray-900 bg-white/80 backdrop-blur-sm",
                    on_change=ParkingState.set_search_query,
                ),
                class_name="relative flex-1",
            ),
            rx.el.div(
                rx.el.select(
                    rx.el.option("All Locations", value="All"),
                    rx.el.option("KL City Centre", value="Kuala Lumpur"),
                    rx.el.option("Bukit Bintang", value="Bukit Bintang"),
                    rx.el.option("Bangsar", value="Bangsar"),
                    rx.el.option("Mid Valley", value="Mid Valley"),
                    class_name="w-full md:w-48 px-4 py-4 rounded-2xl border-0 ring-1 ring-gray-200 focus:ring-2 focus:ring-sky-500 shadow-sm transition-all outline-none bg-white/80 backdrop-blur-sm text-gray-900 cursor-pointer",
                    on_change=ParkingState.set_location_filter,
                )
            ),
            class_name="flex flex-col md:flex-row gap-4 max-w-5xl mx-auto",
        ),
        class_name="bg-white/50 backdrop-blur-lg border-b border-white/20 py-8 px-4 sm:px-6 lg:px-8 sticky top-20 z-40",
    )


def listings_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        search_filter_bar(),
        rx.el.main(
            rx.el.div(
                rx.cond(
                    ParkingState.is_loading,
                    rx.el.div(
                        rx.foreach(rx.Var.range(6), lambda i: loading_card()),
                        class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8",
                    ),
                    rx.el.div(
                        rx.cond(
                            ParkingState.filtered_lots.length() > 0,
                            rx.el.div(
                                rx.foreach(ParkingState.filtered_lots, parking_card),
                                class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8",
                            ),
                            rx.el.div(
                                rx.icon(
                                    "search-x",
                                    class_name="h-24 w-24 text-gray-200 mb-6",
                                ),
                                rx.el.h3(
                                    "No parking lots found",
                                    class_name="text-2xl font-bold text-gray-900 mb-3",
                                ),
                                rx.el.p(
                                    "Try adjusting your search or filters to find what you're looking for.",
                                    class_name="text-gray-500 max-w-md mx-auto mb-6",
                                ),
                                rx.el.button(
                                    "Reload Parking Lots",
                                    on_click=ParkingState.load_data,
                                    class_name="px-6 py-2 bg-sky-500 text-white rounded-lg hover:bg-sky-600 transition-colors font-medium",
                                ),
                                class_name="col-span-full flex flex-col items-center justify-center py-32 text-center",
                            ),
                        )
                    ),
                ),
                class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12",
            ),
            class_name="bg-gradient-to-br from-sky-50 via-white to-indigo-50 flex-1 min-h-screen",
        ),
        booking_modal(),
        payment_modal(),
        footer(),
        class_name="font-['Roboto'] min-h-screen flex flex-col",
        on_mount=ParkingState.on_load,
    )