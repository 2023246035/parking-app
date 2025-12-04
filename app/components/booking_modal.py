import reflex as rx
from app.states.booking_state import BookingState


def booking_summary_row(label: str, value: str, is_total: bool = False) -> rx.Component:
    return rx.el.div(
        rx.el.span(
            label,
            class_name=rx.cond(
                ~is_total, "text-gray-600", "font-semibold text-gray-900"
            ),
        ),
        rx.el.span(
            value,
            class_name=rx.cond(
                ~is_total, "font-medium text-gray-900", "font-bold text-sky-600 text-lg"
            ),
        ),
        class_name=f"flex justify-between items-center {rx.cond(is_total, 'pt-3 border-t border-gray-100 mt-3', 'mb-2')}",
    )


def booking_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "Book Parking Spot", class_name="text-xl font-bold text-gray-900 mb-4"
            ),
            rx.dialog.description(
                "Select your preferred time and duration.",
                class_name="text-sm text-gray-500 mb-6",
            ),
            rx.cond(
                BookingState.selected_lot,
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.h4(
                                BookingState.selected_lot.name,
                                class_name="font-semibold text-gray-900",
                            ),
                            rx.el.p(
                                BookingState.selected_lot.location,
                                class_name="text-sm text-gray-500",
                            ),
                        ),
                        rx.el.div(
                            rx.el.span("RM ", class_name="text-xs text-gray-500"),
                            rx.el.span(
                                f"{BookingState.selected_lot.price_per_hour:.2f}",
                                class_name="font-bold text-gray-900",
                            ),
                            rx.el.span("/hr", class_name="text-xs text-gray-500"),
                            class_name="text-right",
                        ),
                        class_name="bg-gray-50 p-4 rounded-xl mb-6 flex justify-between items-center",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.label(
                                    "Date",
                                    class_name="block text-sm font-medium text-gray-700 mb-1",
                                ),
                                rx.el.input(
                                    type="date",
                                    min=BookingState.start_date,
                                    default_value=BookingState.start_date,
                                    on_change=BookingState.set_start_date,
                                    class_name="w-full rounded-lg border-gray-300 border px-3 py-2 focus:ring-2 focus:ring-sky-200 focus:border-sky-500 outline-none",
                                ),
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Start Time",
                                    class_name="block text-sm font-medium text-gray-700 mb-1",
                                ),
                                rx.el.input(
                                    type="time",
                                    default_value=BookingState.start_time,
                                    on_change=BookingState.set_start_time,
                                    class_name="w-full rounded-lg border-gray-300 border px-3 py-2 focus:ring-2 focus:ring-sky-200 focus:border-sky-500 outline-none",
                                ),
                            ),
                            class_name="grid grid-cols-2 gap-4 mb-4",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Duration (Hours)",
                                class_name="block text-sm font-medium text-gray-700 mb-1",
                            ),
                            rx.el.select(
                                rx.el.option("1 Hour", value="1"),
                                rx.el.option("2 Hours", value="2"),
                                rx.el.option("3 Hours", value="3"),
                                rx.el.option("4 Hours", value="4"),
                                rx.el.option("5 Hours", value="5"),
                                rx.el.option("8 Hours", value="8"),
                                rx.el.option("12 Hours", value="12"),
                                rx.el.option("24 Hours", value="24"),
                                default_value=BookingState.duration_hours.to_string(),
                                on_change=BookingState.set_duration,
                                class_name="w-full rounded-lg border-gray-300 border px-3 py-2 focus:ring-2 focus:ring-sky-200 focus:border-sky-500 outline-none bg-white",
                            ),
                            class_name="mb-6",
                        ),
                    ),
                    rx.el.div(
                        booking_summary_row(
                            "Rate per hour",
                            f"RM {BookingState.selected_lot.price_per_hour:.2f}",
                        ),
                        booking_summary_row(
                            "Duration", f"{BookingState.duration_hours} hours"
                        ),
                        booking_summary_row("Service Fee", "RM 0.00"),
                        booking_summary_row(
                            "Total Amount",
                            f"RM {BookingState.estimated_price:.2f}",
                            is_total=True,
                        ),
                        class_name="mb-8",
                    ),
                    rx.el.div(
                        rx.dialog.close(
                            rx.el.button(
                                "Cancel",
                                class_name="px-4 py-2 rounded-lg text-gray-600 hover:bg-gray-100 font-medium transition-colors",
                                on_click=BookingState.close_modal,
                            )
                        ),
                        rx.el.button(
                            "Proceed to Payment",
                            class_name="px-6 py-2 rounded-lg bg-sky-500 text-white hover:bg-sky-600 font-medium shadow-sm hover:shadow-md transition-all",
                            on_click=BookingState.proceed_to_payment,
                        ),
                        class_name="flex justify-end gap-3",
                    ),
                ),
                rx.el.div("Loading...", class_name="p-4 text-center text-gray-500"),
            ),
            class_name="bg-white rounded-2xl p-6 shadow-xl max-w-md w-full",
        ),
        open=BookingState.is_modal_open,
        on_open_change=BookingState.handle_modal_open_change,
    )