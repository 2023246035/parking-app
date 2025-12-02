import reflex as rx
from app.states.booking_state import BookingState


def payment_field(label: str, placeholder: str, icon: str, value_var: rx.Var, on_change: rx.EventHandler, error_var: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.label(label, class_name="block text-sm font-medium text-gray-700 mb-1"),
        rx.el.div(
            rx.el.input(
                placeholder=placeholder,
                value=value_var,
                on_change=on_change,
                class_name=rx.cond(
                    error_var != "",
                    "w-full pl-10 pr-4 py-2.5 rounded-lg border border-red-300 focus:ring-2 focus:ring-red-200 focus:border-red-500 outline-none transition-all bg-red-50",
                    "w-full pl-10 pr-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-sky-200 focus:border-sky-500 outline-none transition-all"
                ),
            ),
            rx.icon(
                icon,
                class_name="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400",
            ),
            class_name="relative",
        ),
        rx.cond(
            error_var != "",
            rx.el.p(error_var, class_name="text-xs text-red-600 mt-1"),
        ),
        class_name="mb-4",
    )


def payment_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "Secure Payment",
                class_name="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2",
            ),
            rx.dialog.description(
                "Complete your booking securely with RinggitPay.",
                class_name="text-sm text-gray-500 mb-6",
            ),
            rx.cond(
                BookingState.selected_lot,
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(
                                "Total Amount", class_name="text-sm text-gray-500"
                            ),
                            rx.el.span(
                                f"RM {BookingState.estimated_price:.2f}",
                                class_name="text-2xl font-bold text-gray-900",
                            ),
                            class_name="flex justify-between items-center mb-6 p-4 bg-gray-50 rounded-xl border border-gray-100",
                        ),
                        payment_field(
                            "Card Number", "0000 0000 0000 0000", "credit-card",
                            BookingState.card_number, BookingState.set_card_number, BookingState.error_payment_card
                        ),
                        rx.el.div(
                            payment_field(
                                "Expiry Date", "MM/YY", "calendar",
                                BookingState.card_expiry, BookingState.set_card_expiry, BookingState.error_payment_expiry
                            ),
                            payment_field(
                                "CVC", "123", "lock",
                                BookingState.card_cvc, BookingState.set_card_cvc, BookingState.error_payment_cvc
                            ),
                            class_name="grid grid-cols-2 gap-4",
                        ),
                        payment_field(
                            "Cardholder Name", "Full Name on Card", "user",
                            BookingState.card_name, BookingState.set_card_name, BookingState.error_payment_name
                        ),
                        rx.cond(
                            BookingState.payment_error != "",
                            rx.el.div(
                                rx.icon(
                                    "badge_alert",
                                    class_name="h-5 w-5 text-red-500 mr-2",
                                ),
                                rx.el.p(
                                    BookingState.payment_error,
                                    class_name="text-sm text-red-600",
                                ),
                                class_name="flex items-center bg-red-50 p-3 rounded-lg mb-4 border border-red-100",
                            ),
                        ),
                        rx.el.button(
                            rx.cond(
                                BookingState.is_processing_payment,
                                rx.el.div(
                                    rx.spinner(size="2", class_name="mr-2 text-white"),
                                    "Processing...",
                                    class_name="flex items-center justify-center",
                                ),
                                f"Pay RM {BookingState.estimated_price:.2f}",
                            ),
                            disabled=BookingState.is_processing_payment,
                            on_click=BookingState.process_payment,
                            class_name=rx.cond(
                                BookingState.is_processing_payment,
                                "w-full py-3 rounded-xl bg-sky-400 text-white font-semibold cursor-not-allowed",
                                "w-full py-3 rounded-xl bg-sky-600 text-white font-semibold hover:bg-sky-700 shadow-md hover:shadow-lg transition-all",
                            ),
                        ),
                        rx.el.div(
                            rx.icon("lock", class_name="h-3 w-3 text-gray-400 mr-1"),
                            rx.el.span(
                                "Payments are secure and encrypted",
                                class_name="text-xs text-gray-400",
                            ),
                            class_name="flex items-center justify-center mt-4",
                        ),
                    )
                ),
            ),
            class_name="bg-white rounded-2xl p-6 shadow-2xl max-w-md w-full",
        ),
        open=BookingState.is_payment_modal_open,
        on_open_change=lambda open: rx.cond(
            open, rx.noop(), BookingState.close_payment_modal()
        ),
    )
