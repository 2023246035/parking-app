"""Multi-step booking modal with slot selection"""
import reflex as rx
from app.states.booking_state import BookingState


def progress_indicator(current_step: int) -> rx.Component:
    """Step progress indicator"""
    return rx.el.div(
        rx.foreach(
            rx.Var.range(1, 5),
            lambda step: rx.el.div(
                rx.el.div(
                    step.to_string(),
                    class_name=rx.cond(
                        step <= current_step,
                        "w-8 h-8 rounded-full bg-sky-500 text-white flex items-center justify-center text-sm font-bold",
                        "w-8 h-8 rounded-full bg-gray-200 text-gray-500 flex items-center justify-center text-sm font-bold"
                    )
                ),
                class_name="flex-1 flex items-center justify-center"
            )
        ),
        class_name="flex items-center gap-2 mb-8"
    )


def slot_button(slot: str, is_selected: bool) -> rx.Component:
    """Individual slot button"""
    return rx.el.button(
        slot,
        on_click=BookingState.select_slot(slot),
        class_name=rx.cond(
            is_selected,
            "px-4 py-3 rounded-lg bg-sky-500 text-white font-bold border-2 border-sky-600 shadow-lg",
            "px-4 py-3 rounded-lg bg-white text-gray-700 font-semibold border-2 border-gray-200 hover:border-sky-400 hover:bg-sky-50 transition-all"
        )
    )


def step1_slot_selection() -> rx.Component:
    """Step 1: Select parking slot"""
    return rx.el.div(
        rx.el.h3(
            "Select Your Parking Slot",
            class_name="text-xl font-bold text-gray-900 mb-4"
        ),
        rx.el.p(
            "Choose an available parking space",
            class_name="text-gray-600 mb-6"
        ),
        
        # Zone A
        rx.el.div(
            rx.el.h4("Zone A", class_name="text-sm font-bold text-gray-700 mb-3"),
            rx.el.div(
                rx.foreach(
                    BookingState.zone_a_slots,
                    lambda slot: slot_button(slot, BookingState.selected_slot == slot)
                ),
                class_name="grid grid-cols-5 gap-3"
            ),
            class_name="mb-6"
        ),
        
        # Zone B
        rx.el.div(
            rx.el.h4("Zone B", class_name="text-sm font-bold text-gray-700 mb-3"),
            rx.el.div(
                rx.foreach(
                    BookingState.zone_b_slots,
                    lambda slot: slot_button(slot, BookingState.selected_slot == slot)
                ),
                class_name="grid grid-cols-5 gap-3"
            ),
            class_name="mb-6"
        ),
        
        # Selected slot display
        rx.cond(
            BookingState.selected_slot != "",
            rx.el.div(
                rx.icon("check", class_name="h-5 w-5 text-green-500 mr-2"),
                "Selected: ",
                rx.el.span(
                    BookingState.selected_slot,
                    class_name="font-bold text-sky-600"
                ),
                class_name="flex items-center bg-green-50 border border-green-200 px-4 py-3 rounded-lg mt-4"
            ),
            rx.fragment()
        )
    )


def step2_datetime_selection() -> rx.Component:
    """Step 2: Select date and time"""
    return rx.el.div(
        rx.el.h3(
            "Select Date & Time",
            class_name="text-xl font-bold text-gray-900 mb-4"
        ),
        
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Date",
                    class_name="block text-sm font-medium text-gray-700 mb-2"
                ),
                rx.el.input(
                    type="date",
                    min=BookingState.start_date,
                    default_value=BookingState.start_date,
                    on_change=BookingState.set_start_date,
                    class_name="w-full rounded-lg border-gray-300 border px-4 py-3 focus:ring-2 focus:ring-sky-200 focus:border-sky-500 outline-none"
                ),
            ),
            rx.el.div(
                rx.el.label(
                    "Start Time",
                    class_name="block text-sm font-medium text-gray-700 mb-2"
                ),
                rx.el.input(
                    type="time",
                    default_value=BookingState.start_time,
                    on_change=BookingState.set_start_time,
                    class_name="w-full rounded-lg border-gray-300 border px-4 py-3 focus:ring-2 focus:ring-sky-200 focus:border-sky-500 outline-none"
                ),
            ),
            class_name="grid grid-cols-2 gap-4 mb-4"
        ),
        
        rx.el.div(
            rx.el.label(
                "Duration (Hours)",
                class_name="block text-sm font-medium text-gray-700 mb-2"
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
                class_name="w-full rounded-lg border-gray-300 border px-4 py-3 focus:ring-2 focus:ring-sky-200 focus:border-sky-500 outline-none bg-white"
            ),
        )
    )


def step3_vehicle_details() -> rx.Component:
    """Step 3: Enter vehicle and contact details"""
    return rx.el.div(
        rx.el.h3(
            "Vehicle & Contact Information",
            class_name="text-xl font-bold text-gray-900 mb-4"
        ),
        
        rx.el.div(
            rx.el.label(
                "Vehicle Number",
                class_name="block text-sm font-medium text-gray-700 mb-2"
            ),
            rx.el.input(
                type="text",
                placeholder="e.g., ABC 1234",
                value=BookingState.vehicle_number,
                on_change=BookingState.set_vehicle_number,
                class_name="w-full rounded-lg border-gray-300 border px-4 py-3 focus:ring-2 focus:ring-sky-200 focus:border-sky-500 outline-none"
            ),
            class_name="mb-4"
        ),
        
        rx.el.div(
            rx.el.label(
                "Phone Number",
                class_name="block text-sm font-medium text-gray-700 mb-2"
            ),
            rx.el.input(
                type="tel",
                placeholder="e.g., +60123456789",
                value=BookingState.phone_number,
                on_change=BookingState.set_phone_number,
                class_name="w-full rounded-lg border-gray-300 border px-4 py-3 focus:ring-2 focus:ring-sky-200 focus:border-sky-500 outline-none"
            ),
        )
    )


def step4_confirmation() -> rx.Component:
    """Step 4: Confirmation summary"""
    return rx.el.div(
        rx.el.h3(
            "Confirm Your Booking",
            class_name="text-xl font-bold text-gray-900 mb-6"
        ),
        
        rx.el.div(
            # Parking lot info
            rx.el.div(
                rx.el.div(
                    rx.icon("map-pin", class_name="h-5 w-5 text-sky-500 mr-2"),
                    BookingState.selected_lot.name,
                    class_name="flex items-center font-bold text-gray-900"
                ),
                rx.el.p(
                    BookingState.selected_lot.location,
                    class_name="text-sm text-gray-600 ml-7"
                ),
                class_name="mb-4 pb-4 border-b border-gray-200"
            ),
            
            # Booking details
            rx.el.div(
                rx.el.div(
                    rx.el.span("Slot:", class_name="text-gray-600"),
                    rx.el.span(
                        BookingState.selected_slot,
                        class_name="font-bold text-sky-600 ml-2"
                    ),
                    class_name="flex justify-between mb-2"
                ),
                rx.el.div(
                    rx.el.span("Date:", class_name="text-gray-600"),
                    rx.el.span(
                        BookingState.start_date,
                        class_name="font-semibold text-gray-900 ml-2"
                    ),
                    class_name="flex justify-between mb-2"
                ),
                rx.el.div(
                    rx.el.span("Time:", class_name="text-gray-600"),
                    rx.el.span(
                        BookingState.start_time,
                        class_name="font-semibold text-gray-900 ml-2"
                    ),
                    class_name="flex justify-between mb-2"
                ),
                rx.el.div(
                    rx.el.span("Duration:", class_name="text-gray-600"),
                    rx.el.span(
                        f"{BookingState.duration_hours} hours",
                        class_name="font-semibold text-gray-900 ml-2"
                    ),
                    class_name="flex justify-between mb-2"
                ),
                rx.el.div(
                    rx.el.span("Vehicle:", class_name="text-gray-600"),
                    rx.el.span(
                        BookingState.vehicle_number,
                        class_name="font-semibold text-gray-900 ml-2"
                    ),
                    class_name="flex justify-between mb-2"
                ),
                rx.el.div(
                    rx.el.span("Phone:", class_name="text-gray-600"),
                    rx.el.span(
                        BookingState.phone_number,
                        class_name="font-semibold text-gray-900 ml-2"
                    ),
                    class_name="flex justify-between"
                ),
                class_name="mb-4 pb-4 border-b border-gray-200"
            ),
            
            # Price summary
            rx.el.div(
                rx.el.div(
                    rx.el.span("Rate per hour:", class_name="text-gray-600"),
                    rx.el.span(
                        f"RM {BookingState.selected_lot.price_per_hour:.2f}",
                        class_name="font-semibold text-gray-900"
                    ),
                    class_name="flex justify-between mb-2"
                ),
                rx.el.div(
                    rx.el.span("Total Amount:", class_name="font-bold text-gray-900"),
                    rx.el.span(
                        f"RM {BookingState.estimated_price:.2f}",
                        class_name="font-bold text-sky-600 text-xl"
                    ),
                    class_name="flex justify-between pt-3 border-t border-gray-200"
                ),
            ),
            
            class_name="bg-gray-50 rounded-xl p-6"
        )
    )


def slot_booking_modal() -> rx.Component:
    """Multi-step booking modal with slot selection"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "Book Parking Spot",
                class_name="text-2xl font-bold text-gray-900 mb-6"
            ),
            
            rx.cond(
                BookingState.selected_lot,
                rx.el.div(
                    # Progress indicator
                    progress_indicator(BookingState.booking_step),
                    
                    # Step content
                    rx.match(
                        BookingState.booking_step,
                        (1, step1_slot_selection()),
                        (2, step2_datetime_selection()),
                        (3, step3_vehicle_details()),
                        (4, step4_confirmation()),
                        step1_slot_selection()
                    ),
                    
                    # Navigation buttons
                    rx.el.div(
                        # Back button
                        rx.cond(
                            BookingState.booking_step > 1,
                            rx.el.button(
                                rx.icon("chevron-left", class_name="h-5 w-5 mr-1"),
                                "Back",
                                on_click=BookingState.previous_step,
                                class_name="px-5 py-2.5 rounded-lg text-gray-700 hover:bg-gray-100 font-medium transition-colors flex items-center"
                            ),
                            rx.dialog.close(
                                rx.el.button(
                                    "Cancel",
                                    on_click=BookingState.close_modal,
                                    class_name="px-5 py-2.5 rounded-lg text-gray-600 hover:bg-gray-100 font-medium transition-colors"
                                )
                            )
                        ),
                        
                        # Next/Proceed button
                        rx.cond(
                            BookingState.booking_step < 4,
                            rx.el.button(
                                "Next",
                                rx.icon("chevron-right", class_name="h-5 w-5 ml-1"),
                                on_click=BookingState.next_step,
                                disabled=~BookingState.can_proceed_to_next_step,
                                class_name=rx.cond(
                                    BookingState.can_proceed_to_next_step,
                                    "px-6 py-2.5 rounded-lg bg-sky-500 text-white hover:bg-sky-600 font-medium shadow-sm hover:shadow-md transition-all flex items-center",
                                    "px-6 py-2.5 rounded-lg bg-gray-300 text-gray-500 font-medium cursor-not-allowed flex items-center"
                                )
                            ),
                            rx.el.button(
                                "Proceed to Payment",
                                rx.icon("credit-card", class_name="h-5 w-5 ml-2"),
                                on_click=BookingState.proceed_to_payment,
                                class_name="px-6 py-2.5 rounded-lg bg-green-500 text-white hover:bg-green-600 font-bold shadow-sm hover:shadow-md transition-all flex items-center"
                            )
                        ),
                        
                        class_name="flex justify-between gap-3 mt-8 pt-6 border-t border-gray-200"
                    ),
                ),
                rx.el.div("Loading...", class_name="p-4 text-center text-gray-500")
            ),
            
            class_name="bg-white rounded-2xl p-8 shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        ),
        open=BookingState.is_modal_open,
        on_open_change=lambda open: rx.cond(
            open, rx.noop(), BookingState.close_modal()
        ),
    )
