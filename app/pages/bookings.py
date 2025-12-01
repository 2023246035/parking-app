import reflex as rx
from app.components.navbar import navbar
from app.components.footer import footer
from app.components.cancellation_modal import cancellation_modal
from app.states.booking_state import BookingState, Booking
from app.states.auth_state import AuthState


def booking_status_badge(status: str) -> rx.Component:
    """Minimalist status badges"""
    return rx.match(
        status,
        (
            "Confirmed",
            rx.el.span(
                "● Confirmed",
                class_name="text-xs font-semibold text-green-600"
            ),
        ),
        (
            "Pending",
            rx.el.span(
                "● Pending",
                class_name="text-xs font-semibold text-yellow-600"
            ),
        ),
        (
            "Cancelled",
            rx.el.span(
                "● Cancelled",
                class_name="text-xs font-semibold text-red-600"
            ),
        ),
        (
            "Completed",
            rx.el.span(
                "● Completed",
                class_name="text-xs font-semibold text-gray-600"
            ),
        ),
        rx.el.span(
            f"● {status}",
            class_name="text-xs font-semibold text-gray-600"
        ),
    )


def payment_status_badge(status: str) -> rx.Component:
    """Minimal payment badges"""
    return rx.match(
        status,
        (
            "Paid",
            rx.el.span(
                "✓ Paid",
                class_name="text-xs font-medium text-green-700 bg-green-50 px-2.5 py-1 rounded-md"
            ),
        ),
        (
            "Refunded",
            rx.el.span(
                "↺ Refunded",
                class_name="text-xs font-medium text-blue-700 bg-blue-50 px-2.5 py-1 rounded-md"
            ),
        ),
        (
            "Pending",
            rx.el.span(
                "○ Pending",
                class_name="text-xs font-medium text-yellow-700 bg-yellow-50 px-2.5 py-1 rounded-md"
            ),
        ),
        rx.el.span(status, class_name="text-xs text-gray-600"),
    )


def booking_card(booking: Booking) -> rx.Component:
    """Clean, minimal booking card"""
    return rx.el.div(
        # Card content
        rx.el.div(
            # Top section - Status
            rx.el.div(
                booking_status_badge(booking.status),
                payment_status_badge(booking.payment_status),
                class_name="flex items-center justify-between mb-4"
            ),
            
            # Main info
            rx.el.div(
                rx.el.h3(
                    booking.lot_name,
                    class_name="text-lg font-bold text-gray-900 mb-1"
                ),
                rx.el.p(
                    booking.lot_location,
                    class_name="text-sm text-gray-500 mb-4"
                ),
            ),
            
            # Details grid
            rx.el.div(
                # Date & Time
                rx.el.div(
                    rx.el.p("Date & Time", class_name="text-xs text-gray-500 mb-1"),
                    rx.el.p(
                        booking.start_date,
                        class_name="text-sm font-semibold text-gray-900"
                    ),
                    rx.el.p(
                        f"at {booking.start_time}",
                        class_name="text-xs text-gray-600"
                    ),
                ),
                
                # Duration
                rx.el.div(
                    rx.el.p("Duration", class_name="text-xs text-gray-500 mb-1"),
                    rx.el.p(
                        f"{booking.duration_hours} Hours",
                        class_name="text-sm font-semibold text-gray-900"
                    ),
                ),
                
                # Booking ID
                rx.el.div(
                    rx.el.p("Booking ID", class_name="text-xs text-gray-500 mb-1"),
                    rx.el.p(
                        booking.id,
                        class_name="text-xs font-mono font-semibold text-gray-700"
                    ),
                ),
                
                class_name="grid grid-cols-3 gap-4 mb-4 pb-4 border-b border-gray-100"
            ),
            
            # Footer - Price & Action
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        rx.cond(
                            booking.status == "Cancelled",
                            "Refund Amount",
                            "Total Paid"
                        ),
                        class_name="text-xs text-gray-500 mb-1"
                    ),
                    rx.el.p(
                        rx.cond(
                            booking.status == "Cancelled",
                            f"RM {booking.refund_amount:.2f}",
                            f"RM {booking.total_price:.2f}",
                        ),
                        class_name="text-xl font-bold text-gray-900"
                    ),
                ),
                
                rx.cond(
                    booking.status == "Confirmed",
                    rx.el.button(
                        "Cancel",
                        on_click=lambda: BookingState.initiate_cancellation(booking),
                        class_name="text-sm font-medium text-red-600 hover:bg-red-50 px-4 py-2 rounded-lg transition-colors"
                    ),
                ),
                
                class_name="flex items-end justify-between"
            ),
        ),
        
        class_name="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-lg hover:border-gray-300 transition-all duration-300",
        key=booking.id,
    )


def empty_state(title: str, message: str) -> rx.Component:
    """Clean empty state"""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                "📋",
                class_name="text-6xl mb-4"
            ),
            rx.el.h3(
                title,
                class_name="text-xl font-bold text-gray-900 mb-2"
            ),
            rx.el.p(
                message,
                class_name="text-gray-600 mb-6"
            ),
            rx.el.a(
                "Find Parking →",
                href="/listings",
                class_name="inline-block px-6 py-3 bg-gray-900 text-white font-medium rounded-lg hover:bg-gray-800 transition-colors"
            ),
            class_name="flex flex-col items-center justify-center py-16 text-center"
        ),
    )


def bookings_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        
        rx.el.main(
            # Simple Header
            rx.el.div(
                rx.el.div(
                    rx.el.h1(
                        "My Bookings",
                        class_name="text-3xl font-bold text-gray-900 mb-2"
                    ),
                    rx.el.p(
                        "Manage your parking reservations",
                        class_name="text-gray-600"
                    ),
                    class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
                ),
                class_name="bg-white border-b border-gray-200"
            ),
            
            # Tabs
            rx.el.div(
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger(
                            "Active",
                            value="active",
                            class_name="px-4 py-2 text-sm font-medium text-gray-600 data-[state=active]:text-gray-900 data-[state=active]:border-b-2 data-[state=active]:border-gray-900"
                        ),
                        rx.tabs.trigger(
                            "Past",
                            value="past",
                            class_name="px-4 py-2 text-sm font-medium text-gray-600 data-[state=active]:text-gray-900 data-[state=active]:border-b-2 data-[state=active]:border-gray-900"
                        ),
                        rx.tabs.trigger(
                            "Cancelled",
                            value="cancelled",
                            class_name="px-4 py-2 text-sm font-medium text-gray-600 data-[state=active]:text-gray-900 data-[state=active]:border-b-2 data-[state=active]:border-gray-900"
                        ),
                        class_name="flex gap-6 border-b border-gray-200 mb-8"
                    ),
                    
                    rx.tabs.content(
                        rx.cond(
                            BookingState.active_bookings.length() > 0,
                            rx.el.div(
                                rx.foreach(BookingState.active_bookings, booking_card),
                                class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                            ),
                            empty_state(
                                "No Active Bookings",
                                "You don't have any active parking reservations"
                            ),
                        ),
                        value="active",
                    ),
                    
                    rx.tabs.content(
                        rx.cond(
                            BookingState.past_bookings.length() > 0,
                            rx.el.div(
                                rx.foreach(BookingState.past_bookings, booking_card),
                                class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                            ),
                            empty_state(
                                "No Past Bookings",
                                "You haven't completed any parking reservations yet"
                            ),
                        ),
                        value="past",
                    ),
                    
                    rx.tabs.content(
                        rx.cond(
                            BookingState.cancelled_bookings.length() > 0,
                            rx.el.div(
                                rx.foreach(BookingState.cancelled_bookings, booking_card),
                                class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                            ),
                            empty_state(
                                "No Cancelled Bookings",
                                "You haven't cancelled any reservations"
                            ),
                        ),
                        value="cancelled",
                    ),
                    
                    default_value="active",
                ),
                class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pb-24"
            ),
            
            class_name="flex-1 bg-gray-50"
        ),
        
        cancellation_modal(),
        footer(),
        
        class_name="font-['Roboto'] min-h-screen flex flex-col",
        on_mount=AuthState.check_login,
    )