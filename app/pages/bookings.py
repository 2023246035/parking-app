import reflex as rx
from app.components.navbar import navbar
from app.components.footer import footer
from app.components.cancellation_modal import cancellation_modal
from app.states.booking_state import BookingState, Booking
from app.states.auth_state import AuthState


def booking_status_badge(status: str) -> rx.Component:
    return rx.match(
        status,
        (
            "Confirmed",
            rx.el.span(
                "Confirmed",
                class_name="bg-green-100/80 backdrop-blur-sm text-green-700 px-3 py-1 rounded-full text-xs font-medium border border-green-200 shadow-sm",
            ),
        ),
        (
            "Pending",
            rx.el.span(
                "Pending",
                class_name="bg-yellow-100/80 backdrop-blur-sm text-yellow-700 px-3 py-1 rounded-full text-xs font-medium border border-yellow-200 shadow-sm",
            ),
        ),
        (
            "Cancelled",
            rx.el.span(
                "Cancelled",
                class_name="bg-red-100/80 backdrop-blur-sm text-red-700 px-3 py-1 rounded-full text-xs font-medium border border-red-200 shadow-sm",
            ),
        ),
        (
            "Completed",
            rx.el.span(
                "Completed",
                class_name="bg-gray-100/80 backdrop-blur-sm text-gray-700 px-3 py-1 rounded-full text-xs font-medium border border-gray-200 shadow-sm",
            ),
        ),
        rx.el.span(
            status,
            class_name="bg-gray-100 text-gray-600 px-3 py-1 rounded-full text-xs font-medium",
        ),
    )


def payment_status_badge(status: str) -> rx.Component:
    return rx.match(
        status,
        (
            "Paid",
            rx.el.div(
                rx.icon("check_check", class_name="h-3 w-3 mr-1"),
                "Paid",
                class_name="flex items-center text-xs font-medium text-green-600 bg-green-50/80 px-2 py-1 rounded-md border border-green-100",
            ),
        ),
        (
            "Refunded",
            rx.el.div(
                rx.icon("arrow_left", class_name="h-3 w-3 mr-1"),
                "Refunded",
                class_name="flex items-center text-xs font-medium text-gray-600 bg-gray-50/80 px-2 py-1 rounded-md border border-gray-100",
            ),
        ),
        (
            "Pending",
            rx.el.div(
                rx.icon("clock", class_name="h-3 w-3 mr-1"),
                "Pending",
                class_name="flex items-center text-xs font-medium text-yellow-600 bg-yellow-50/80 px-2 py-1 rounded-md border border-yellow-100",
            ),
        ),
        rx.el.div(status),
    )


def booking_card(booking: Booking) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    booking.lot_name, class_name="text-lg font-bold text-gray-900"
                ),
                rx.el.div(
                    rx.el.p(
                        booking.lot_location, class_name="text-sm text-gray-500 mr-2"
                    ),
                    payment_status_badge(booking.payment_status),
                    class_name="flex items-center flex-wrap gap-2",
                ),
                class_name="mb-4",
            ),
            booking_status_badge(booking.status),
            class_name="flex justify-between items-start",
        ),
        rx.el.div(
            rx.el.div(
                rx.icon("calendar", class_name="h-4 w-4 text-gray-400 mr-2"),
                rx.el.span(
                    f"{booking.start_date} at {booking.start_time}",
                    class_name="text-sm text-gray-600",
                ),
                class_name="flex items-center mb-2",
            ),
            rx.el.div(
                rx.icon("clock", class_name="h-4 w-4 text-gray-400 mr-2"),
                rx.el.span(
                    f"{booking.duration_hours} Hours",
                    class_name="text-sm text-gray-600",
                ),
                class_name="flex items-center mb-2",
            ),
            rx.el.div(
                rx.icon("ticket", class_name="h-4 w-4 text-gray-400 mr-2"),
                rx.el.span(
                    f"ID: {booking.id}", class_name="text-sm font-mono text-gray-500"
                ),
                class_name="flex items-center",
            ),
            class_name="bg-gray-50/50 rounded-xl p-4 mb-4 border border-gray-100",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    rx.cond(
                        booking.status == "Cancelled", "Refund Amount", "Total Paid"
                    ),
                    class_name="text-sm text-gray-500",
                ),
                rx.el.span(
                    rx.cond(
                        booking.status == "Cancelled",
                        f"RM {booking.refund_amount:.2f}",
                        f"RM {booking.total_price:.2f}",
                    ),
                    class_name="text-xl font-bold text-gray-900",
                ),
                class_name="flex flex-col",
            ),
            rx.cond(
                booking.status == "Confirmed",
                rx.el.button(
                    "Cancel Booking",
                    on_click=lambda: BookingState.initiate_cancellation(booking),
                    class_name="text-sm text-red-600 hover:text-red-700 font-medium hover:bg-red-50 px-3 py-1.5 rounded-lg transition-colors",
                ),
            ),
            class_name="flex justify-between items-end",
        ),
        class_name="bg-white/80 backdrop-blur-sm rounded-2xl border border-white/20 p-6 shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300",
        key=booking.id,
    )


def empty_state(title: str, message: str) -> rx.Component:
    """Empty state component for when there are no bookings"""
    return rx.el.div(
        rx.el.div(
            rx.icon("calendar-x", class_name="h-16 w-16 text-gray-300 mb-4"),
            rx.el.h3(
                title,
                class_name="text-xl font-semibold text-gray-700 mb-2",
            ),
            rx.el.p(
                message,
                class_name="text-gray-500 mb-6",
            ),
            rx.el.a(
                "Browse Available Parking Lots",
                href="/listings",
                class_name="inline-block px-6 py-3 bg-gradient-to-r from-sky-600 to-indigo-600 text-white font-medium rounded-xl hover:shadow-lg transition-all",
            ),
            class_name="flex flex-col items-center justify-center py-16",
        ),
    )


def bookings_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.main(
            rx.el.div(
                rx.el.div(
                    rx.el.h1(
                        "My Bookings",
                        class_name="text-3xl font-bold text-gray-900 mb-2",
                    ),
                    rx.el.p(
                        "Manage your upcoming and past parking reservations.",
                        class_name="text-gray-500 mb-8",
                    ),
                    class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12",
                ),
                rx.el.div(
                    rx.tabs.root(
                        rx.tabs.list(
                            rx.tabs.trigger(
                                "Active",
                                value="active",
                                class_name="px-6 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-900 data-[state=active]:text-sky-600 data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg transition-all",
                            ),
                            rx.tabs.trigger(
                                "Past",
                                value="past",
                                class_name="px-6 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-900 data-[state=active]:text-sky-600 data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg transition-all",
                            ),
                            rx.tabs.trigger(
                                "Cancelled",
                                value="cancelled",
                                class_name="px-6 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-900 data-[state=active]:text-sky-600 data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg transition-all",
                            ),
                            class_name="flex gap-2 p-1 bg-gray-100/50 rounded-xl w-fit mb-8 border border-gray-200",
                        ),
                        rx.tabs.content(
                            rx.cond(
                                BookingState.active_bookings.length() > 0,
                                rx.el.div(
                                    rx.foreach(BookingState.active_bookings, booking_card),
                                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
                                ),
                                empty_state("No Active Bookings", "You don't have any active parking reservations."),
                            ),
                            value="active",
                        ),
                        rx.tabs.content(
                            rx.cond(
                                BookingState.past_bookings.length() > 0,
                                rx.el.div(
                                    rx.foreach(BookingState.past_bookings, booking_card),
                                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
                                ),
                                empty_state("No Past Bookings", "You haven't completed any parking reservations yet."),
                            ),
                            value="past",
                        ),
                        rx.tabs.content(
                            rx.cond(
                                BookingState.cancelled_bookings.length() > 0,
                                rx.el.div(
                                    rx.foreach(
                                        BookingState.cancelled_bookings, booking_card
                                    ),
                                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
                                ),
                                empty_state("No Cancelled Bookings", "You haven't cancelled any reservations."),
                            ),
                            value="cancelled",
                        ),
                        default_value="active",
                    ),
                    class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-24",
                ),
            ),
            class_name="flex-1 bg-gradient-to-br from-sky-50 via-white to-indigo-50",
        ),
        cancellation_modal(),
        footer(),
        class_name="font-['Roboto'] min-h-screen flex flex-col",
        on_mount=AuthState.check_login,
    )