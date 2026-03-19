import reflex as rx
from app.states.booking_state import BookingState


def reschedule_modal() -> rx.Component:
    """Modal for rescheduling bookings"""
    return rx.dialog.root(
        rx.dialog.content(
            # Header
            rx.dialog.title(
                "Change Booking Time",
                class_name="text-xl font-bold text-gray-900 mb-1"
            ),
            rx.dialog.description(
                "Select new date and time for your booking",
                class_name="text-sm text-gray-500 mb-6"
            ),
            
            rx.cond(
                BookingState.booking_to_reschedule,
                rx.el.div(
                    # Current booking info
                    rx.el.div(
                        rx.el.p(
                            "Current Booking",
                            class_name="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2"
                        ),
                        rx.el.div(
                            rx.el.span("Date:", class_name="text-sm text-gray-600"),
                            rx.el.span(
                                BookingState.booking_to_reschedule.start_date,
                                class_name="text-sm font-semibold text-gray-900"
                            ),
                            class_name="flex justify-between mb-1"
                        ),
                        rx.el.div(
                            rx.el.span("Time:", class_name="text-sm text-gray-600"),
                            rx.el.span(
                                BookingState.booking_to_reschedule.start_time,
                                class_name="text-sm font-semibold text-gray-900"
                            ),
                            class_name="flex justify-between"
                        ),
                        class_name="bg-gray-50 p-4 rounded-lg mb-6"
                    ),
                    
                    # New date/time inputs
                    rx.el.div(
                        rx.el.p(
                            "New Booking Time",
                            class_name="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-3"
                        ),
                        
                        # Date input
                        rx.el.div(
                            rx.el.label(
                                "New Date",
                                class_name="block text-sm font-medium text-gray-700 mb-1"
                            ),
                            rx.el.input(
                                type="date",
                                value=BookingState.new_start_date,
                                on_change=BookingState.set_new_start_date,
                                class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            ),
                            class_name="mb-4"
                        ),
                        
                        # Time input
                        rx.el.div(
                            rx.el.label(
                                "New Time",
                                class_name="block text-sm font-medium text-gray-700 mb-1"
                            ),
                            rx.el.input(
                                type="time",
                                value=BookingState.new_start_time,
                                on_change=BookingState.set_new_start_time,
                                class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            ),
                            class_name="mb-4"
                        ),
                        
                        # Info message
                        rx.el.div(
                            rx.el.div(
                                "ℹ️",
                                class_name="text-xl mr-2"
                            ),
                            rx.el.p(
                                "New booking time must be at least 24 hours from now.",
                                class_name="text-xs text-gray-600"
                            ),
                            class_name="flex items-start p-3 bg-blue-50 rounded-lg border border-blue-100"
                        ),
                        
                        class_name="mb-6"
                    ),
                    
                    # Action buttons
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            on_click=BookingState.close_reschedule_modal,
                            class_name="flex-1 px-4 py-2.5 rounded-lg text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 font-medium transition-colors"
                        ),
                        rx.el.button(
                            "Confirm Change",
                            on_click=BookingState.confirm_reschedule,
                            class_name="flex-1 px-4 py-2.5 rounded-lg bg-blue-600 text-white hover:bg-blue-700 font-medium transition-colors"
                        ),
                        class_name="flex gap-3"
                    ),
                ),
            ),
            
            class_name="bg-white rounded-xl p-6 shadow-xl max-w-md w-full"
        ),
        open=BookingState.is_reschedule_modal_open,
    )
