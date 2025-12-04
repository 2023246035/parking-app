import reflex as rx
from app.states.booking_state import BookingState


def cancellation_modal() -> rx.Component:
    """Clean, minimal cancellation modal"""
    return rx.dialog.root(
        rx.dialog.content(
            # Header
            rx.el.div(
                rx.el.h2(
                    "Cancel Booking?",
                    class_name="text-xl font-bold text-gray-900"
                ),
                rx.el.p(
                    "This action cannot be undone",
                    class_name="text-sm text-gray-500 mt-1"
                ),
                class_name="mb-6"
            ),
            
            rx.cond(
                BookingState.booking_to_cancel,
                rx.el.div(
                    # Refund info banner
                    rx.el.div(
                        rx.el.div(
                            "ℹ️",
                            class_name="text-2xl mr-3"
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Refund Policy",
                                class_name="text-xs font-semibold text-gray-700 mb-0.5"
                            ),
                            rx.el.p(
                                BookingState.cancellation_message,
                                class_name="text-sm text-gray-600"
                            ),
                        ),
                        class_name="flex items-start p-4 bg-blue-50 rounded-lg mb-6 border border-blue-100"
                    ),
                    
                    # Payment summary
                    rx.el.div(
                        rx.el.div(
                            rx.el.span("Original Payment", class_name="text-sm text-gray-600"),
                            rx.el.span(
                                f"RM {BookingState.booking_to_cancel.total_price:.2f}",
                                class_name="text-sm font-semibold text-gray-900"
                            ),
                            class_name="flex justify-between mb-2"
                        ),
                        
                        rx.el.div(
                            rx.el.span("Refund Percentage", class_name="text-sm text-gray-600"),
                            rx.el.span(
                                f"{BookingState.refund_percentage}%",
                                class_name="text-sm font-semibold text-gray-900"
                            ),
                            class_name="flex justify-between mb-3"
                        ),
                        
                        rx.el.div(class_name="border-t border-gray-200 my-3"),
                        
                        rx.el.div(
                            rx.el.span("Refund Amount", class_name="text-sm font-semibold text-gray-900"),
                            rx.el.span(
                                f"RM {BookingState.refund_amount_display:.2f}",
                                class_name="text-lg font-bold text-green-600"
                            ),
                            class_name="flex justify-between"
                        ),
                        
                        class_name="bg-gray-50 p-4 rounded-lg mb-6"
                    ),
                    
                    # Action buttons
                    rx.el.div(
                        rx.dialog.close(
                            rx.el.button(
                                "Keep Booking",
                                on_click=BookingState.close_cancellation_modal,
                                class_name="flex-1 px-4 py-2.5 rounded-lg text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 font-medium transition-colors"
                            )
                        ),
                        rx.el.button(
                            "Confirm Cancellation",
                            on_click=BookingState.confirm_cancellation,
                            class_name="flex-1 px-4 py-2.5 rounded-lg bg-red-600 text-white hover:bg-red-700 font-medium transition-colors"
                        ),
                        class_name="flex gap-3"
                    ),
                ),
            ),
            
            class_name="bg-white rounded-xl p-6 shadow-xl max-w-md w-full"
        ),
        open=BookingState.is_cancellation_modal_open,
        on_open_change=BookingState.handle_cancellation_modal_open_change,
    )