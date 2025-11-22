import reflex as rx
from app.states.booking_state import BookingState


def cancellation_summary_row(
    label: str, value: str, color: str = "text-gray-900"
) -> rx.Component:
    return rx.el.div(
        rx.el.span(label, class_name="text-gray-600"),
        rx.el.span(value, class_name=f"font-medium {color}"),
        class_name="flex justify-between items-center mb-2",
    )


def cancellation_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "Cancel Booking", class_name="text-xl font-bold text-gray-900 mb-2"
            ),
            rx.dialog.description(
                "Are you sure you want to cancel this booking?",
                class_name="text-sm text-gray-500 mb-6",
            ),
            rx.cond(
                BookingState.booking_to_cancel,
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "flag_triangle_right",
                            class_name="h-12 w-12 text-yellow-500 mb-2",
                        ),
                        rx.el.p(
                            BookingState.cancellation_message,
                            class_name="text-center text-gray-700 font-medium mb-4",
                        ),
                        class_name="flex flex-col items-center p-4 bg-yellow-50 rounded-xl mb-6 border border-yellow-100",
                    ),
                    rx.el.div(
                        cancellation_summary_row(
                            "Original Payment",
                            f"RM {BookingState.booking_to_cancel.total_price:.2f}",
                        ),
                        cancellation_summary_row(
                            "Refund Percentage", f"{BookingState.refund_percentage}%"
                        ),
                        rx.el.div(class_name="border-t border-gray-100 my-2"),
                        cancellation_summary_row(
                            "Refund Amount",
                            f"RM {BookingState.refund_amount_display:.2f}",
                            "text-green-600 font-bold",
                        ),
                        class_name="bg-gray-50 p-4 rounded-xl mb-6",
                    ),
                    rx.el.div(
                        rx.dialog.close(
                            rx.el.button(
                                "Keep Booking",
                                class_name="px-4 py-2 rounded-lg text-gray-600 hover:bg-gray-100 font-medium transition-colors",
                                on_click=BookingState.close_cancellation_modal,
                            )
                        ),
                        rx.el.button(
                            "Confirm Cancellation",
                            class_name="px-6 py-2 rounded-lg bg-red-500 text-white hover:bg-red-600 font-medium shadow-sm hover:shadow-md transition-all",
                            on_click=BookingState.confirm_cancellation,
                        ),
                        class_name="flex justify-end gap-3",
                    ),
                ),
            ),
            class_name="bg-white rounded-2xl p-6 shadow-2xl max-w-md w-full",
        ),
        open=BookingState.is_cancellation_modal_open,
        on_open_change=lambda open: rx.cond(
            open, rx.noop(), BookingState.close_cancellation_modal()
        ),
    )