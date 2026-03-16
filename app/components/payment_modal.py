import reflex as rx
from app.states.booking_state import BookingState


def trust_badge(icon: str, label: str, color: str) -> rx.Component:
    text_style = "text-xs font-bold text-gray-700"
    badge_style = "flex flex-col items-center p-3 bg-gray-50 rounded-lg shadow-sm"
    return rx.el.div(
        rx.icon(icon, class_name=f"h-6 w-6 {color} mb-2"),
        rx.el.p(label, class_name=text_style),
        class_name=badge_style
    )


def payment_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "Secure Payment",
                class_name="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2",
            ),
            rx.dialog.description(
                "You will be redirected to RinggitPay's secure hosted payment page to complete your transaction.",
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
                        
                        # Trust Badges / Info
                        rx.el.div(
                            trust_badge("shield-check", "Secure Gateway", "text-green-500"),
                            trust_badge("credit-card", "Multiple Methods", "text-sky-500"),
                            trust_badge("zap", "Instant Confirm", "text-orange-500"),
                            class_name="grid grid-cols-3 gap-3 mb-6 font-['Roboto']"
                        ),

                        rx.cond(
                            BookingState.payment_error != "",
                            rx.el.div(
                                rx.icon(
                                    "alert-circle",
                                    class_name="h-5 w-5 text-red-500 mr-2",
                                ),
                                rx.el.p(
                                    BookingState.payment_error,
                                    class_name="text-sm text-red-600 font-medium",
                                ),
                                class_name="flex items-center bg-red-50 p-4 rounded-xl mb-6 border border-red-100",
                            ),
                        ),

                        rx.el.button(
                            rx.cond(
                                BookingState.is_processing_payment,
                                rx.el.div(
                                    rx.spinner(size="2", class_name="mr-2 text-white"),
                                    "Redirecting...",
                                    class_name="flex items-center justify-center",
                                ),
                                "Proceed to RinggitPay",
                            ),
                            disabled=BookingState.is_processing_payment,
                            on_click=BookingState.process_payment,
                            class_name=rx.cond(
                                BookingState.is_processing_payment,
                                "w-full py-4 rounded-xl bg-sky-400 text-white font-bold cursor-not-allowed",
                                "w-full py-4 rounded-xl bg-sky-600 text-white font-bold hover:bg-sky-700 shadow-md hover:shadow-lg transition-all text-lg",
                            ),
                        ),
                        rx.el.div(
                            rx.icon("lock", class_name="h-3 w-3 text-gray-400 mr-1"),
                            rx.el.span(
                                "Secure SSL Encryption by RinggitPay",
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
        on_open_change=BookingState.handle_payment_modal_open_change,
    )
