import reflex as rx
from app.states.booking_state import BookingState


def step_indicator(step_number: int, step_name: str, is_active: bool, is_completed: bool) -> rx.Component:
    """Step indicator for the booking wizard"""
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                step_number,
                class_name=rx.cond(
                    is_active | is_completed,
                    "text-white",
                    "text-gray-400"
                ),
            ),
            class_name=rx.cond(
                is_active,
                "w-8 h-8 rounded-full bg-sky-500 flex items-center justify-center text-sm font-semibold transition-all duration-300",
                rx.cond(
                    is_completed,
                    "w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-sm font-semibold transition-all duration-300",
                    "w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-sm font-semibold transition-all duration-300"
                )
            ),
        ),
        rx.el.span(
            step_name,
            class_name=rx.cond(
                is_active,
                "text-xs font-medium text-sky-600 mt-1",
                "text-xs text-gray-500 mt-1"
            ),
        ),
        class_name="flex flex-col items-center z-10 bg-white px-2",
    )


def progress_bar() -> rx.Component:
    """Progress bar connecting the steps"""
    return rx.el.div(
        rx.el.div(
            class_name=rx.cond(
                BookingState.booking_step == 1, "w-[0%] h-full bg-green-500 transition-all duration-500",
                rx.cond(
                    BookingState.booking_step == 2, "w-[33%] h-full bg-green-500 transition-all duration-500",
                    rx.cond(
                        BookingState.booking_step == 3, "w-[66%] h-full bg-green-500 transition-all duration-500",
                        "w-[100%] h-full bg-green-500 transition-all duration-500"
                    )
                )
            ),
        ),
        class_name="absolute top-4 left-0 w-full h-0.5 bg-gray-200 -z-0",
    )


def step_1_datetime() -> rx.Component:
    """Step 1: Date, Time & Duration Selection"""
    return rx.el.div(
        rx.el.h3("Select Date & Time", class_name="text-lg font-bold text-gray-900 mb-1"),
        rx.el.p("Choose when you need the parking spot", class_name="text-sm text-gray-500 mb-6"),
        
        # Date Selection
        rx.el.div(
            rx.el.label("Parking Date", class_name="block text-sm font-semibold text-gray-700 mb-2"),
            rx.el.input(
                type="date",
                min=BookingState.start_date,
                value=BookingState.start_date,
                on_change=BookingState.set_start_date,
                class_name="w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:ring-2 focus:ring-sky-200 focus:border-sky-500 outline-none text-gray-900 transition-all",
            ),
            rx.cond(
                BookingState.error_date != "",
                rx.el.p(BookingState.error_date, class_name="text-xs text-red-600 mt-1 font-medium"),
            ),
            class_name="mb-5",
        ),
        
        # Time Selection
        rx.el.div(
            rx.el.label("Start Time", class_name="block text-sm font-semibold text-gray-700 mb-2"),
            rx.el.input(
                type="time",
                value=BookingState.start_time,
                on_change=BookingState.set_start_time,
                class_name="w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:ring-2 focus:ring-sky-200 focus:border-sky-500 outline-none text-gray-900 transition-all",
            ),
            rx.cond(
                BookingState.error_time != "",
                rx.el.p(BookingState.error_time, class_name="text-xs text-red-600 mt-1 font-medium"),
            ),
            class_name="mb-5",
        ),
        
        # Duration Selection
        rx.el.div(
            rx.el.label("Duration", class_name="block text-sm font-semibold text-gray-700 mb-2"),
            rx.el.select(
                rx.el.option("1 Hour", value="1"),
                rx.el.option("2 Hours", value="2"),
                rx.el.option("3 Hours", value="3"),
                rx.el.option("4 Hours", value="4"),
                rx.el.option("5 Hours", value="5"),
                rx.el.option("8 Hours", value="8"),
                rx.el.option("12 Hours", value="12"),
                rx.el.option("24 Hours", value="24"),
                value=BookingState.duration_hours.to_string(),
                on_change=BookingState.set_duration,
                class_name="w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:ring-2 focus:ring-sky-200 focus:border-sky-500 outline-none bg-white text-gray-900 cursor-pointer transition-all",
            ),
            class_name="mb-8",
        ),
        
        # Next Button
        rx.el.button(
            "Check Available Slots →",
            on_click=BookingState.proceed_to_slot_selection,
            class_name="w-full px-6 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all hover:scale-[1.02]",
        ),
    )


def slot_card(slot_id: str, is_available: bool) -> rx.Component:
    """Individual slot card"""
    return rx.el.button(
        rx.el.div(
            rx.icon(
                rx.cond(is_available, "check-circle", "x-circle"),
                class_name=rx.cond(is_available, "h-5 w-5 text-green-500", "h-5 w-5 text-red-400"),
            ),
            rx.el.span(
                slot_id,
                class_name=rx.cond(is_available, "text-lg font-bold text-gray-900", "text-lg font-bold text-gray-400"),
            ),
            class_name="flex flex-col items-center gap-1",
        ),
        on_click=lambda: rx.cond(is_available, BookingState.select_slot(slot_id), rx.noop()),
        disabled=~is_available,
        class_name=rx.cond(
            BookingState.selected_slot == slot_id,
            "p-3 rounded-xl border-2 border-sky-500 bg-sky-50 transition-all shadow-md cursor-pointer scale-105",
            rx.cond(
                is_available,
                "p-3 rounded-xl border-2 border-gray-200 bg-white hover:border-sky-300 hover:bg-sky-50 transition-all cursor-pointer",
                "p-3 rounded-xl border-2 border-gray-100 bg-gray-50 cursor-not-allowed opacity-50"
            )
        ),
    )


def step_2_slots() -> rx.Component:
    """Step 2: Slot Selection"""
    return rx.el.div(
        rx.el.div(
            rx.el.button(
                rx.icon("arrow-left", class_name="h-4 w-4 mr-2"),
                "Back",
                on_click=BookingState.go_back_to_step_1,
                class_name="flex items-center text-sm text-gray-600 hover:text-gray-900 font-medium mb-4 transition-colors",
            ),
            rx.el.h3("Select Parking Slot", class_name="text-lg font-bold text-gray-900 mb-1"),
            rx.el.p(
                f"For {BookingState.start_date} at {BookingState.start_time}",
                class_name="text-sm text-gray-500 mb-6",
            ),
        ),
        
        rx.cond(
            BookingState.is_loading_slots,
            rx.el.div(
                rx.spinner(size="3", class_name="text-sky-500"),
                rx.el.p("Checking availability...", class_name="text-gray-500 mt-3"),
                class_name="flex flex-col items-center justify-center py-12",
            ),
            rx.el.div(
                # Zone A
                rx.el.div(
                    rx.el.h4("Zone A", class_name="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider"),
                    rx.el.div(
                        rx.foreach(
                            BookingState.zone_a_slots,
                            lambda slot: slot_card(slot, ~BookingState.occupied_slots.contains(slot))
                        ),
                        class_name="grid grid-cols-5 gap-3 mb-6",
                    ),
                ),
                # Zone B
                rx.el.div(
                    rx.el.h4("Zone B", class_name="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider"),
                    rx.el.div(
                        rx.foreach(
                            BookingState.zone_b_slots,
                            lambda slot: slot_card(slot, ~BookingState.occupied_slots.contains(slot))
                        ),
                        class_name="grid grid-cols-5 gap-3 mb-6",
                    ),
                ),
                
                rx.cond(
                    BookingState.error_slot != "",
                    rx.el.p(BookingState.error_slot, class_name="text-sm text-red-600 mb-4 font-medium text-center"),
                ),
                
                rx.el.button(
                    "Continue to Details →",
                    on_click=BookingState.proceed_to_details,
                    disabled=BookingState.selected_slot == "",
                    class_name="w-full px-6 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100",
                ),
            ),
        ),
    )


def step_3_details() -> rx.Component:
    """Step 3: Vehicle & Contact Info"""
    return rx.el.div(
        rx.el.div(
            rx.el.button(
                rx.icon("arrow-left", class_name="h-4 w-4 mr-2"),
                "Back",
                on_click=BookingState.go_back_to_step_2,
                class_name="flex items-center text-sm text-gray-600 hover:text-gray-900 font-medium mb-4 transition-colors",
            ),
            rx.el.h3("Vehicle & Contact", class_name="text-lg font-bold text-gray-900 mb-1"),
            rx.el.p("Enter your details for verification", class_name="text-sm text-gray-500 mb-6"),
        ),
        
        # Vehicle Number
        rx.el.div(
            rx.el.label("Vehicle Number", class_name="block text-sm font-semibold text-gray-700 mb-2"),
            rx.el.input(
                placeholder="e.g. ABC 1234",
                value=BookingState.vehicle_number,
                on_change=BookingState.set_vehicle_number,
                class_name="w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:ring-2 focus:ring-sky-200 focus:border-sky-500 outline-none text-gray-900 uppercase transition-all",
            ),
            rx.cond(
                BookingState.error_vehicle != "",
                rx.el.p(BookingState.error_vehicle, class_name="text-xs text-red-600 mt-1 font-medium"),
            ),
            class_name="mb-5",
        ),
        
        # Phone Number
        rx.el.div(
            rx.el.label("Phone Number", class_name="block text-sm font-semibold text-gray-700 mb-2"),
            rx.el.input(
                placeholder="e.g. 0123456789",
                value=BookingState.phone_number,
                on_change=BookingState.set_phone_number,
                class_name="w-full rounded-xl border-2 border-gray-200 px-4 py-3 focus:ring-2 focus:ring-sky-200 focus:border-sky-500 outline-none text-gray-900 transition-all",
            ),
            rx.cond(
                BookingState.error_phone != "",
                rx.el.p(BookingState.error_phone, class_name="text-xs text-red-600 mt-1 font-medium"),
            ),
            class_name="mb-8",
        ),
        
        rx.el.button(
            "Review Booking →",
            on_click=BookingState.proceed_to_review,
            class_name="w-full px-6 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all hover:scale-[1.02]",
        ),
    )


def summary_row(label: str, value: str, is_total: bool = False) -> rx.Component:
    return rx.el.div(
        rx.el.span(label, class_name="text-gray-600"),
        rx.el.span(
            value,
            class_name=rx.cond(is_total, "font-bold text-sky-600 text-lg", "font-medium text-gray-900")
        ),
        class_name=f"flex justify-between items-center {rx.cond(is_total, 'pt-4 border-t border-gray-100 mt-2', 'mb-2')}",
    )


def step_4_review() -> rx.Component:
    """Step 4: Review & Confirm"""
    return rx.el.div(
        rx.el.div(
            rx.el.button(
                rx.icon("arrow-left", class_name="h-4 w-4 mr-2"),
                "Back",
                on_click=BookingState.go_back_to_step_3,
                class_name="flex items-center text-sm text-gray-600 hover:text-gray-900 font-medium mb-4 transition-colors",
            ),
            rx.el.h3("Review Booking", class_name="text-lg font-bold text-gray-900 mb-1"),
            rx.el.p("Please confirm your details", class_name="text-sm text-gray-500 mb-6"),
        ),
        
        rx.el.div(
            summary_row("Parking Lot", BookingState.selected_lot.name),
            summary_row("Location", BookingState.selected_lot.location),
            rx.el.div(class_name="h-px bg-gray-100 my-3"),
            summary_row("Date", BookingState.start_date),
            summary_row("Time", BookingState.start_time),
            summary_row("Duration", f"{BookingState.duration_hours} Hours"),
            summary_row("Selected Slot", BookingState.selected_slot),
            rx.el.div(class_name="h-px bg-gray-100 my-3"),
            summary_row("Vehicle", BookingState.vehicle_number),
            summary_row("Phone", BookingState.phone_number),
            summary_row("Total Amount", f"RM {BookingState.estimated_price:.2f}", is_total=True),
            class_name="bg-gray-50 p-5 rounded-xl mb-8 border border-gray-100",
        ),
        
        rx.el.button(
            "Confirm & Pay",
            on_click=BookingState.proceed_to_payment,
            class_name="w-full px-6 py-3.5 rounded-xl bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold shadow-lg hover:shadow-xl transition-all hover:scale-[1.02]",
        ),
    )


def booking_wizard_modal() -> rx.Component:
    """Main Booking Wizard Modal"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.cond(
                BookingState.selected_lot,
                rx.el.div(
                    # Header
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3(BookingState.selected_lot.name, class_name="text-xl font-bold text-gray-900"),
                            rx.el.p(BookingState.selected_lot.location, class_name="text-sm text-gray-500"),
                        ),
                        rx.dialog.close(
                            rx.el.button(
                                rx.icon("x", class_name="h-5 w-5 text-gray-400 hover:text-gray-600"),
                                class_name="p-2 hover:bg-gray-100 rounded-full transition-colors",
                                on_click=BookingState.close_modal,
                            )
                        ),
                        class_name="flex justify-between items-start mb-8",
                    ),
                    
                    # Progress Steps
                    rx.el.div(
                        progress_bar(),
                        rx.el.div(
                            step_indicator("1", "Time", BookingState.booking_step == 1, BookingState.booking_step > 1),
                            step_indicator("2", "Slot", BookingState.booking_step == 2, BookingState.booking_step > 2),
                            step_indicator("3", "Details", BookingState.booking_step == 3, BookingState.booking_step > 3),
                            step_indicator("4", "Review", BookingState.booking_step == 4, False),
                            class_name="flex justify-between relative z-10",
                        ),
                        class_name="relative mb-8 mx-2",
                    ),
                    
                    # Step Content
                    rx.cond(
                        BookingState.booking_step == 1, step_1_datetime(),
                        rx.cond(
                            BookingState.booking_step == 2, step_2_slots(),
                            rx.cond(
                                BookingState.booking_step == 3, step_3_details(),
                                step_4_review()
                            )
                        )
                    ),
                ),
                rx.el.div("Loading...", class_name="p-8 text-center text-gray-500"),
            ),
            class_name="bg-white rounded-2xl p-6 shadow-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto focus:outline-none",
        ),
        open=BookingState.is_modal_open,
        on_open_change=lambda open: rx.cond(open, rx.noop(), BookingState.close_modal()),
    )
