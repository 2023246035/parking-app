import reflex as rx
from app.states.parking_state import ParkingLot
from app.states.booking_state import BookingState
from app.states.auth_state import AuthState


def status_badge(spots: int) -> rx.Component:
    return rx.cond(
        spots > 20,
        rx.el.div(
            rx.el.span(
                rx.el.span(
                    class_name="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"
                ),
                rx.el.span(
                    class_name="relative inline-flex rounded-full h-2 w-2 bg-green-500"
                ),
                class_name="relative flex h-2 w-2 mr-2",
            ),
            "Available",
            class_name="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-50/90 backdrop-blur-md text-green-700 border border-green-200 shadow-sm",
        ),
        rx.cond(
            spots > 0,
            rx.el.div(
                rx.el.span(class_name="h-2 w-2 mr-2 rounded-full bg-yellow-400"),
                "Limited",
                class_name="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-yellow-50/90 backdrop-blur-md text-yellow-700 border border-yellow-200 shadow-sm",
            ),
            rx.el.div(
                rx.el.span(class_name="h-2 w-2 mr-2 rounded-full bg-red-400"),
                "Full",
                class_name="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-red-50/90 backdrop-blur-md text-red-700 border border-red-200 shadow-sm",
            ),
        ),
    )


def parking_card(lot: ParkingLot) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.image(
                src=lot.image_url,
                alt=lot.name,
                class_name="h-56 w-full object-cover transition-transform duration-700 group-hover:scale-105",
            ),
            rx.el.div(
                status_badge(lot.available_spots), class_name="absolute top-4 right-4"
            ),
            # Recommendation Badge
            rx.cond(
                lot.recommendation_score >= 7.0,
                rx.el.div(
                    rx.icon("star", class_name="h-3 w-3 mr-1 fill-yellow-400 text-yellow-400"),
                    "Top Pick",
                    class_name="absolute top-4 left-4 inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-gray-900/90 backdrop-blur-md text-white border border-gray-700 shadow-lg z-10",
                ),
            ),
            class_name="relative overflow-hidden",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        lot.name, class_name="text-lg font-bold text-gray-900 truncate"
                    ),
                    # High Demand Badge
                    rx.cond(
                        lot.demand_multiplier >= 1.2,
                        rx.el.div(
                            rx.icon("trending-up", class_name="h-3 w-3 mr-1"),
                            "High Demand",
                            class_name="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-orange-100 text-orange-700 border border-orange-200 uppercase tracking-wide",
                        ),
                    ),
                    class_name="flex items-center justify-between mb-1 gap-2"
                ),
                rx.el.div(
                    rx.icon(
                        "map-pin", class_name="h-4 w-4 text-gray-400 mr-1 flex-shrink-0"
                    ),
                    rx.el.span(
                        lot.location, class_name="text-sm text-gray-500 truncate"
                    ),
                    class_name="flex items-center mb-4",
                ),
                rx.el.div(
                    rx.foreach(
                        lot.features,
                        lambda f: rx.el.span(
                            f,
                            class_name="text-xs font-medium text-sky-700 bg-sky-50 px-2.5 py-1 rounded-lg border border-sky-100",
                        ),
                    ),
                    class_name="flex flex-wrap gap-2 mb-6",
                ),
                rx.el.div(
                    rx.el.div(
                        # Dynamic Price Display
                        rx.cond(
                            (lot.dynamic_price > 0) & (lot.dynamic_price != lot.base_price),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.span(
                                        "RM", class_name="text-xs font-medium text-gray-400 mr-0.5"
                                    ),
                                    rx.el.span(
                                        f"{lot.base_price:.2f}",
                                        class_name="text-sm font-medium text-gray-400 line-through",
                                    ),
                                    class_name="flex items-baseline mb-[-4px]"
                                ),
                                rx.el.div(
                                    rx.el.span(
                                        "RM", class_name="text-xs font-bold text-orange-600 mr-1"
                                    ),
                                    rx.el.span(
                                        f"{lot.dynamic_price:.2f}",
                                        class_name="text-2xl font-black text-orange-600",
                                    ),
                                    rx.el.span("/hr", class_name="text-xs text-orange-600/70 ml-1 font-medium"),
                                    class_name="flex items-baseline",
                                ),
                                class_name="flex flex-col"
                            ),
                            # Standard Price Display
                            rx.el.div(
                                rx.el.span(
                                    "RM", class_name="text-xs font-medium text-gray-500 mr-1"
                                ),
                                rx.el.span(
                                    f"{lot.price_per_hour:.2f}",
                                    class_name="text-2xl font-bold text-gray-900",
                                ),
                                rx.el.span("/hr", class_name="text-xs text-gray-500 ml-1"),
                                class_name="flex items-baseline",
                            ),
                        ),
                        class_name="flex items-baseline",
                    ),
                    rx.el.div(
                        rx.el.button(
                            rx.icon("bot", class_name="w-5 h-5"),
                            on_click=rx.redirect(f"/chatbot?query=Tell me about {lot.name}"),
                            class_name="p-2.5 rounded-xl bg-indigo-50 text-indigo-600 hover:bg-indigo-100 hover:scale-105 transition-all duration-200 mr-2",
                            title="Ask AI about this lot"
                        ),
                        rx.el.button(
                            "Book Now",
                            disabled=lot.available_spots == 0,
                            on_click=rx.cond(
                                AuthState.is_authenticated,
                                BookingState.open_modal(lot),
                                rx.redirect("/login"),
                            ),
                            class_name=rx.cond(
                                lot.available_spots > 0,
                                "bg-gradient-to-r from-sky-500 to-blue-600 text-white hover:shadow-lg hover:shadow-sky-500/30 hover:scale-105",
                                "bg-gray-100 text-gray-400 cursor-not-allowed",
                            )
                            + " px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 shadow-sm flex-1",
                        ),
                        class_name="flex items-center flex-1 justify-end"
                    ),
                    class_name="flex items-center justify-between pt-4 border-t border-gray-100 mt-auto",
                ),
                class_name="flex flex-col flex-1",
            ),
            class_name="p-6 flex flex-col flex-1",
        ),
        class_name="group flex flex-col bg-white rounded-2xl overflow-hidden border border-white/20 shadow-lg hover:shadow-2xl hover:-translate-y-1 transition-all duration-300 h-full bg-white/90 backdrop-blur-sm",
    )


def loading_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(class_name="h-56 bg-gray-200 animate-pulse"),
        rx.el.div(
            rx.el.div(class_name="h-6 w-3/4 bg-gray-200 rounded-lg animate-pulse mb-2"),
            rx.el.div(class_name="h-4 w-1/2 bg-gray-200 rounded-lg animate-pulse mb-4"),
            rx.el.div(
                rx.el.div(class_name="h-6 w-16 bg-gray-200 rounded-lg animate-pulse"),
                rx.el.div(class_name="h-6 w-16 bg-gray-200 rounded-lg animate-pulse"),
                class_name="flex gap-2 mb-6",
            ),
            rx.el.div(
                rx.el.div(class_name="h-8 w-24 bg-gray-200 rounded-lg animate-pulse"),
                rx.el.div(class_name="h-8 w-24 bg-gray-200 rounded-lg animate-pulse"),
                class_name="flex justify-between pt-4 border-t border-gray-100 mt-auto",
            ),
            class_name="p-6 flex flex-col flex-1",
        ),
        class_name="bg-white rounded-2xl overflow-hidden border border-gray-100 shadow-sm h-full",
    )