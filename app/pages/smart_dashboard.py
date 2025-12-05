"""Smart Dashboard for Auto-Booking and AI Features"""
import reflex as rx
from typing import List, Optional
from datetime import datetime, timedelta
import calendar
from sqlmodel import select
from app.components.navbar import navbar
from app.states.auth_state import AuthState
from app.db.models import BookingRule, User, ParkingLot, Booking
from app.db.models import BookingRule as DBBookingRule, Booking as DBBooking  # Alias for clarity

# Pydantic model for UI
class Rule(rx.Base):
    id: int
    location: str
    days: List[str]
    time: str
    duration: str
    status: str
    next_run: str
    vehicle_number: str
    phone_number: str
    slot_id: str

class SmartDashboardState(rx.State):
    """State for Smart Dashboard"""
    active_tab: str = "overview"
    rules: List[Rule] = []
    available_locations: List[str] = []
    
    # AI Insights
    savings: float = 145.50
    hours_saved: int = 12
    
    # Delete Confirmation
    show_confirm_delete: bool = False
    rule_to_delete_id: int = 0
    
    # Add/Edit Modal
    show_rule_modal: bool = False
    is_editing: bool = False
    editing_rule_id: int = 0
    rule_wizard_step: int = 1  # Track current step in add/edit wizard (1-4)
    
    # Form Fields
    form_location: str = ""
    form_days: List[str] = []
    form_time: str = "09:00"
    form_duration: str = "1"
    form_vehicle: str = ""
    form_phone: str = ""
    form_slot: str = ""
    available_slots: List[str] = ["A1", "A2", "A3", "A4", "A5", "B1", "B2", "B3", "B4", "B5"] # Simplified slots
    
    # Validation error messages
    error_location: str = ""
    error_days: str = ""
    error_time: str = ""
    error_duration: str = ""
    error_vehicle: str = ""
    error_phone: str = ""
    error_slot: str = ""
    
    # Validation methods
    def validate_location_and_days(self) -> bool:
        """Validate location and days selection"""
        is_valid = True
        
        # Validate location
        if not self.form_location or self.form_location.strip() == "":
            self.error_location = "Please select a parking location"
            is_valid = False
        else:
            self.error_location = ""
        
        # Validate days
        if not self.form_days or len(self.form_days) == 0:
            self.error_days = "Please select at least one day"
            is_valid = False
        else:
            self.error_days = ""
        
        return is_valid
    
    def validate_time_and_duration(self) -> bool:
        """Validate time and duration"""
        is_valid = True
        
        # Validate time
        if not self.form_time or self.form_time.strip() == "":
            self.error_time = "Please select a time"
            is_valid = False
        else:
            self.error_time = ""
        
        # Validate duration
        try:
            duration = int(self.form_duration)
            if duration <= 0:
                self.error_duration = "Duration must be at least 1 hour"
                is_valid = False
            elif duration > 24:
                self.error_duration = "Duration cannot exceed 24 hours"
                is_valid = False
            else:
                self.error_duration = ""
        except (ValueError, TypeError):
            self.error_duration = "Please enter a valid duration"
            is_valid = False
        
        return is_valid
    
    def validate_vehicle_and_phone(self) -> bool:
        """Validate vehicle and phone"""
        is_valid = True
        
        # Validate vehicle
        if not self.form_vehicle or self.form_vehicle.strip() == "":
            self.error_vehicle = "Vehicle number is required"
            is_valid = False
        elif len(self.form_vehicle.replace(" ", "").replace("-", "")) < 3:
            self.error_vehicle = "Vehicle number must be at least 3 characters"
            is_valid = False
        else:
            self.error_vehicle = ""
        
        # Validate phone
        if not self.form_phone or self.form_phone.strip() == "":
            self.error_phone = "Phone number is required"
            is_valid = False
        else:
            clean_phone = self.form_phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("+", "")
            if not clean_phone.isdigit():
                self.error_phone = "Phone number must contain only digits"
                is_valid = False
            elif len(clean_phone) < 10:
                self.error_phone = "Phone number must be at least 10 digits"
                is_valid = False
            else:
                self.error_phone = ""
        
        return is_valid
    
    def validate_slot(self) -> bool:
        """Validate slot selection"""
        if not self.form_slot or self.form_slot.strip() == "":
            self.error_slot = "Please select a parking slot"
            return False
        else:
            self.error_slot = ""
            return True
    

    @rx.event
    def on_load(self):
        """Load rules from database on page load and process them"""
        return [SmartDashboardState.load_rules, SmartDashboardState.load_locations, SmartDashboardState.process_rules]

    @rx.event
    async def process_rules(self):
        """Process active rules and create bookings if needed"""
        auth_state = await self.get_state(AuthState)
        user_email = auth_state.email
        if not user_email:
            return

        with rx.session() as session:
            user = session.exec(select(User).where(User.email == user_email)).first()
            if not user:
                return

            # Get active rules
            rules = session.exec(
                select(DBBookingRule)
                .where(DBBookingRule.user_id == user.id)
                .where(DBBookingRule.status == "Active")
            ).all()

            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow_day_name = tomorrow.strftime("%a")  # Mon, Tue, etc.
            tomorrow_date_str = tomorrow.strftime("%Y-%m-%d")

            bookings_created = 0

            for rule in rules:
                # Check if rule applies to tomorrow
                rule_days = rule.days.split(",")
                if tomorrow_day_name in rule_days:
                    # Parse location string "Name - Location"
                    try:
                        lot_name, lot_loc = rule.location.split(" - ", 1)
                        lot = session.exec(
                            select(ParkingLot)
                            .where(ParkingLot.name == lot_name)
                            .where(ParkingLot.location == lot_loc)
                        ).first()
                    except ValueError:
                        continue # Skip if format is wrong

                    if not lot:
                        continue

                    # Check if booking already exists
                    existing_booking = session.exec(
                        select(DBBooking)
                        .where(DBBooking.user_id == user.id)
                        .where(DBBooking.lot_id == lot.id)
                        .where(DBBooking.start_date == tomorrow_date_str)
                        .where(DBBooking.start_time == rule.time)
                        .where(DBBooking.status != "Cancelled")
                    ).first()

                    if not existing_booking:
                        # Check for slot conflict
                        if rule.slot_id:
                            slot_conflict = session.exec(
                                select(DBBooking)
                                .where(DBBooking.lot_id == lot.id)
                                .where(DBBooking.start_date == tomorrow_date_str)
                                .where(DBBooking.start_time == rule.time)
                                .where(DBBooking.slot_id == rule.slot_id)
                                .where(DBBooking.status != "Cancelled")
                            ).first()
                            
                            if slot_conflict:
                                yield rx.toast.warning(f"Skipped {rule.location}: Slot {rule.slot_id} unavailable.")
                                continue

                        # Create Booking
                        duration = int(rule.duration.split(" ")[0])
                        total_price = lot.price_per_hour * duration
                        
                        new_booking = DBBooking(
                            lot_id=lot.id,
                            user_id=user.id,
                            start_date=tomorrow_date_str,
                            start_time=rule.time,
                            duration_hours=duration,
                            total_price=total_price,
                            status="Confirmed",
                            payment_status="Paid (Auto)",
                            created_at=datetime.now(),
                            slot_id=rule.slot_id or "AUTO-A1",
                            vehicle_number=rule.vehicle_number or "AUTO-CAR",
                            phone_number=rule.phone_number or user.phone or "N/A"
                        )
                        session.add(new_booking)
                        
                        # Update rule next run
                        rule.next_run = (tomorrow + timedelta(days=1)).strftime("%Y-%m-%d")
                        session.add(rule)
                        
                        bookings_created += 1
            
            if bookings_created > 0:
                session.commit()
                yield rx.toast.success(f"Auto-booked {bookings_created} spots for tomorrow!")

    
    @rx.event
    async def load_locations(self):
        """Fetch available parking locations from DB"""
        with rx.session() as session:
            lots = session.exec(select(ParkingLot)).all()
            self.available_locations = [f"{lot.name} - {lot.location}" for lot in lots]
        
    @rx.event
    async def load_rules(self):
        """Fetch rules from DB for current user"""
        auth_state = await self.get_state(AuthState)
        user_email = auth_state.email
        if not user_email:
            return
            
        with rx.session() as session:
            user = session.exec(select(User).where(User.email == user_email)).first()
            if not user:
                return
                
            db_rules = session.exec(
                select(DBBookingRule).where(DBBookingRule.user_id == user.id)
            ).all()
            
            self.rules = [
                Rule(
                    id=r.id,
                    location=r.location,
                    days=r.days.split(","),
                    time=r.time,
                    duration=r.duration,
                    status=r.status,
                    next_run=r.next_run,
                    vehicle_number=r.vehicle_number or "",
                    phone_number=r.phone_number or "",
                    slot_id=r.slot_id or ""
                )
                for r in db_rules
            ]

    @rx.event
    def set_tab(self, tab: str):
        self.active_tab = tab
        
    @rx.event
    async def toggle_rule(self, rule_id: int):
        """Toggle a rule on/off in DB"""
        with rx.session() as session:
            rule = session.get(DBBookingRule, rule_id)
            if rule:
                rule.status = "Active" if rule.status == "Paused" else "Paused"
                session.add(rule)
                session.commit()
                session.refresh(rule)
        return SmartDashboardState.load_rules

    @rx.event
    def prompt_delete_rule(self, rule_id: int):
        self.rule_to_delete_id = rule_id
        self.show_confirm_delete = True

    @rx.event
    def cancel_delete(self):
        self.show_confirm_delete = False
        self.rule_to_delete_id = 0
                
    @rx.event
    async def confirm_delete_rule(self):
        """Delete rule from DB"""
        if self.rule_to_delete_id:
            with rx.session() as session:
                rule = session.get(DBBookingRule, self.rule_to_delete_id)
                if rule:
                    session.delete(rule)
                    session.commit()
        
        self.show_confirm_delete = False
        self.rule_to_delete_id = 0
        return SmartDashboardState.load_rules

    # Modal & Form Handling
    @rx.event
    def open_add_modal(self):
        self.is_editing = False
        self.form_location = ""
        self.form_days = []
        self.form_time = "09:00"
        self.form_duration = "1"
        self.form_vehicle = ""
        self.form_phone = ""
        self.form_slot = ""
        self.rule_wizard_step = 1
        self.show_rule_modal = True
        
    @rx.event
    def open_edit_modal(self, rule: Rule):
        self.is_editing = True
        self.editing_rule_id = rule.id
        self.form_location = rule.location
        self.form_days = rule.days
        self.form_time = rule.time
        self.form_duration = rule.duration.replace(" hours", "").replace(" hour", "")
        self.form_vehicle = rule.vehicle_number
        self.form_phone = rule.phone_number
        self.form_slot = rule.slot_id
        self.rule_wizard_step = 1
        self.show_rule_modal = True
        
    @rx.event
    def close_rule_modal(self):
        self.show_rule_modal = False
        self.rule_wizard_step = 1
    
    # Wizard Step Navigation
    @rx.event
    def next_rule_step(self):
        """Move to next step in the wizard - validates current step first"""
        # Validate current step before proceeding
        if self.rule_wizard_step == 1:
            # Step 1: Validate location and days
            if not self.validate_location_and_days():
                return  # Stay on step 1 if validation fails
        
        elif self.rule_wizard_step == 2:
            # Step 2: Validate time and duration
            if not self.validate_time_and_duration():
                return  # Stay on step 2 if validation fails
        
        elif self.rule_wizard_step == 3:
            # Step 3: Validate vehicle and phone
            if not self.validate_vehicle_and_phone():
                return  # Stay on step 3 if validation fails
        
        # If validation passed, move to next step
        if self.rule_wizard_step < 4:
            self.rule_wizard_step += 1
    
    @rx.event
    def prev_rule_step(self):
        """Move to previous step in the wizard"""
        if self.rule_wizard_step > 1:
            self.rule_wizard_step -= 1
        
    @rx.event
    def set_form_location(self, val: str):
        self.form_location = val
        
    @rx.event
    def set_form_time(self, val: str):
        self.form_time = val
        
    @rx.event
    def set_form_duration(self, val):
        self.form_duration = str(val)

    @rx.event
    def set_form_vehicle(self, val: str):
        self.form_vehicle = val

    @rx.event
    def set_form_phone(self, val: str):
        self.form_phone = val

    @rx.event
    def set_form_slot(self, val: str):
        self.form_slot = val

    @rx.event
    def toggle_day(self, day: str):
        if day in self.form_days:
            self.form_days.remove(day)
        else:
            self.form_days.append(day)

    @rx.event
    async def save_rule(self):
        """Save new or updated rule to DB"""
        # Validation
        if not self.form_location:
            yield rx.toast.error("Please select a location.")
            return
        if not self.form_days:
            yield rx.toast.error("Please select at least one day.")
            return
        if not self.form_time:
            yield rx.toast.error("Please select a time.")
            return
        if not self.form_duration or int(self.form_duration) < 1:
            yield rx.toast.error("Please enter a valid duration.")
            return
        if not self.form_vehicle.strip():
            yield rx.toast.error("Vehicle number is required.")
            return
        if not self.form_phone.strip():
            yield rx.toast.error("Phone number is required.")
            return
        if not self.form_slot:
            yield rx.toast.error("Please select a preferred slot.")
            return

        auth_state = await self.get_state(AuthState)
        user_email = auth_state.email
        if not user_email:
            return
            
        with rx.session() as session:
            user = session.exec(select(User).where(User.email == user_email)).first()
            if not user:
                return

            days_str = ",".join(self.form_days)
            duration_str = f"{self.form_duration} hour{'s' if int(self.form_duration) > 1 else ''}"
            
            if self.is_editing:
                rule = session.get(DBBookingRule, self.editing_rule_id)
                if rule:
                    rule.location = self.form_location
                    rule.days = days_str
                    rule.time = self.form_time
                    rule.duration = duration_str
                    rule.vehicle_number = self.form_vehicle
                    rule.phone_number = self.form_phone
                    rule.slot_id = self.form_slot
                    session.add(rule)
            else:
                new_rule = DBBookingRule(
                    location=self.form_location,
                    days=days_str,
                    time=self.form_time,
                    duration=duration_str,
                    vehicle_number=self.form_vehicle,
                    phone_number=self.form_phone,
                    slot_id=self.form_slot,
                    status="Active",
                    next_run="Tomorrow",  # Simplified logic
                    user_id=user.id
                )
                session.add(new_rule)
            
            session.commit()
            
        self.show_rule_modal = False
        yield SmartDashboardState.load_rules


def stat_card(title: str, value: str, icon: str, color: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="w-6 h-6 text-white"),
            class_name=f"w-12 h-12 rounded-xl bg-gradient-to-br {color} flex items-center justify-center mb-4 shadow-lg"
        ),
        rx.el.p(title, class_name="text-sm text-gray-500 font-medium"),
        rx.el.p(value, class_name="text-2xl font-bold text-gray-900"),
        class_name="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm"
    )


def delete_confirmation_modal() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("alert-triangle", class_name="h-6 w-6 text-red-600"),
                    class_name="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10"
                ),
                rx.el.div(
                    rx.el.h3("Delete Auto-Booking Rule", class_name="text-base font-semibold leading-6 text-gray-900"),
                    rx.el.div(
                        rx.el.p("Are you sure you want to delete this rule? This action cannot be undone.", class_name="text-sm text-gray-500"),
                        class_name="mt-2"
                    ),
                    class_name="mt-3 text-center sm:ml-4 sm:mt-0 sm:text-left"
                ),
                class_name="sm:flex sm:items-start"
            ),
            rx.el.div(
                rx.el.button(
                    "Delete",
                    on_click=SmartDashboardState.confirm_delete_rule,
                    class_name="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:ml-3 sm:w-auto"
                ),
                rx.el.button(
                    "Cancel",
                    on_click=SmartDashboardState.cancel_delete,
                    class_name="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
                ),
                class_name="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse"
            ),
            class_name="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6"
        ),
        class_name=rx.cond(
            SmartDashboardState.show_confirm_delete,
            "fixed inset-0 z-50 flex items-center justify-center bg-gray-500 bg-opacity-75 transition-opacity",
            "hidden"
        )
    )


# Wizard Step Components
def wizard_step_indicator(step_number: int, step_name: str, is_active: bool, is_completed: bool) -> rx.Component:
    """Step indicator for the wizard"""
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
                "w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-sm font-semibold transition-all duration-300 shadow-lg",
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
                "text-xs font-medium text-indigo-600 mt-1",
                "text-xs text-gray-500 mt-1"
            ),
        ),
        class_name="flex flex-col items-center z-10 bg-white px-2",
    )


def wizard_progress_bar() -> rx.Component:
    """Progress bar connecting the steps"""
    return rx.el.div(
        rx.el.div(
            class_name=rx.cond(
                SmartDashboardState.rule_wizard_step == 1, "w-[0%] h-full bg-green-500 transition-all duration-500",
                rx.cond(
                    SmartDashboardState.rule_wizard_step == 2, "w-[33%] h-full bg-green-500 transition-all duration-500",
                    rx.cond(
                        SmartDashboardState.rule_wizard_step == 3, "w-[66%] h-full bg-green-500 transition-all duration-500",
                        "w-[100%] h-full bg-green-500 transition-all duration-500"
                    )
                )
            ),
        ),
        class_name="absolute top-4 left-0 w-full h-0.5 bg-gray-200 -z-0",
    )


def rule_step_1_location_days() -> rx.Component:
    """Step 1: Location & Days Selection"""
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    return rx.el.div(
        rx.el.h3("Location & Days", class_name="text-lg font-bold text-gray-900 mb-1"),
        rx.el.p("Choose parking location and days", class_name="text-sm text-gray-500 mb-6"),
        
        # Location
        rx.el.div(
            rx.el.label(
                rx.icon("map-pin", class_name="w-4 h-4 inline mr-1.5"),
                "Parking Location",
                class_name="flex items-center text-sm font-semibold text-gray-700 mb-2"
            ),
            rx.select(
                SmartDashboardState.available_locations,
                value=SmartDashboardState.form_location,
                on_change=SmartDashboardState.set_form_location,
                placeholder="Select a parking location",
                size="3",
                class_name="w-full"
            ),
            # Error message for location
            rx.cond(
                SmartDashboardState.error_location != "",
                rx.el.p(
                    SmartDashboardState.error_location,
                    class_name="text-sm text-red-600 mt-1"
                ),
            ),
            class_name="mb-6"
        ),
        
        # Days
        rx.el.div(
            rx.el.label(
                rx.icon("calendar", class_name="w-4 h-4 inline mr-1.5"),
                "Select Days",
                class_name="flex items-center text-sm font-semibold text-gray-700 mb-3"
            ),
            rx.el.div(
                rx.foreach(
                    days,
                    lambda day: rx.el.button(
                        day,
                        on_click=SmartDashboardState.toggle_day(day),
                        type="button",
                        class_name=rx.cond(
                            SmartDashboardState.form_days.contains(day),
                            "bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-md hover:shadow-lg",
                            "bg-gray-100 text-gray-600 hover:bg-gray-200"
                        ) + " px-4 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200"
                    )
                ),
                class_name="grid grid-cols-4 gap-2"
            ),
            # Error message for days
            rx.cond(
                SmartDashboardState.error_days != "",
                rx.el.p(
                    SmartDashboardState.error_days,
                    class_name="text-sm text-red-600 mt-2"
                ),
            ),
            class_name="mb-8"
        ),
        
        # Navigation Buttons
        rx.el.div(
            rx.el.button(
                rx.icon("x", class_name="w-4 h-4 mr-2"),
                "Cancel",
                on_click=SmartDashboardState.close_rule_modal,
                type="button",
                class_name="flex items-center px-5 py-2.5 text-gray-700 bg-white border-2 border-gray-300 rounded-lg hover:bg-gray-50 font-semibold transition-all"
            ),
            rx.el.button(
                "Next Step",
                rx.icon("arrow-right", class_name="w-4 h-4 ml-2"),
                on_click=SmartDashboardState.next_rule_step,
                type="button",
                class_name="flex items-center px-6 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 font-semibold shadow-md hover:shadow-lg transition-all"
            ),
            class_name="flex justify-between items-center gap-3"
        ),
    )


def rule_step_2_time_duration() -> rx.Component:
    """Step 2: Time & Duration Selection"""
    return rx.el.div(
        rx.el.h3("Time & Duration", class_name="text-lg font-bold text-gray-900 mb-1"),
        rx.el.p("Set parking time and duration", class_name="text-sm text-gray-500 mb-6"),
        
        # Time
        rx.el.div(
            rx.el.label(
                rx.icon("clock", class_name="w-4 h-4 inline mr-1.5"),
                "Start Time",
                class_name="flex items-center text-sm font-semibold text-gray-700 mb-2"
            ),
            rx.el.input(
                type="time",
                value=SmartDashboardState.form_time,
                on_change=SmartDashboardState.set_form_time,
                class_name="w-full px-4 py-2.5 rounded-lg border-2 border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all"
            ),
            class_name="mb-5"
        ),
        
        # Duration
        rx.el.div(
            rx.el.label(
                rx.icon("timer", class_name="w-4 h-4 inline mr-1.5"),
                "Duration (Hours)",
                class_name="flex items-center text-sm font-semibold text-gray-700 mb-2"
            ),
            rx.el.input(
                type="number",
                min="1",
                max="24",
                value=SmartDashboardState.form_duration,
                on_change=SmartDashboardState.set_form_duration,
                placeholder="1",
                class_name="w-full px-4 py-2.5 rounded-lg border-2 border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all"
            ),
            class_name="mb-8"
        ),
        
        # Navigation Buttons
        rx.el.div(
            rx.el.button(
                rx.icon("arrow-left", class_name="w-4 h-4 mr-2"),
                "Back",
                on_click=SmartDashboardState.prev_rule_step,
                type="button",
                class_name="flex items-center px-5 py-2.5 text-gray-700 bg-white border-2 border-gray-300 rounded-lg hover:bg-gray-50 font-semibold transition-all"
            ),
            rx.el.button(
                "Next Step",
                rx.icon("arrow-right", class_name="w-4 h-4 ml-2"),
                on_click=SmartDashboardState.next_rule_step,
                type="button",
                class_name="flex items-center px-6 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 font-semibold shadow-md hover:shadow-lg transition-all"
            ),
            class_name="flex justify-between items-center gap-3"
        ),
    )


def rule_step_3_vehicle_phone() -> rx.Component:
    """Step 3: Vehicle & Contact Info"""
    return rx.el.div(
        rx.el.h3("Vehicle & Contact", class_name="text-lg font-bold text-gray-900 mb-1"),
        rx.el.p("Enter your details", class_name="text-sm text-gray-500 mb-6"),
        
        # Vehicle Number
        rx.el.div(
            rx.el.label(
                rx.icon("car", class_name="w-4 h-4 inline mr-1.5"),
                "Vehicle Number",
                class_name="flex items-center text-sm font-semibold text-gray-700 mb-2"
            ),
            rx.el.input(
                type="text",
                value=SmartDashboardState.form_vehicle,
                on_change=SmartDashboardState.set_form_vehicle,
                placeholder="e.g. ABC 1234",
                class_name="w-full px-4 py-2.5 rounded-lg border-2 border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all uppercase"
            ),
            class_name="mb-5"
        ),
        
        # Phone Number
        rx.el.div(
            rx.el.label(
                rx.icon("phone", class_name="w-4 h-4 inline mr-1.5"),
                "Phone Number",
                class_name="flex items-center text-sm font-semibold text-gray-700 mb-2"
            ),
            rx.el.input(
                type="tel",
                value=SmartDashboardState.form_phone,
                on_change=SmartDashboardState.set_form_phone,
                placeholder="e.g. 0123456789",
                class_name="w-full px-4 py-2.5 rounded-lg border-2 border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all"
            ),
            class_name="mb-8"
        ),
        
        # Navigation Buttons
        rx.el.div(
            rx.el.button(
                rx.icon("arrow-left", class_name="w-4 h-4 mr-2"),
                "Back",
                on_click=SmartDashboardState.prev_rule_step,
                type="button",
                class_name="flex items-center px-5 py-2.5 text-gray-700 bg-white border-2 border-gray-300 rounded-lg hover:bg-gray-50 font-semibold transition-all"
            ),
            rx.el.button(
                "Next Step",
                rx.icon("arrow-right", class_name="w-4 h-4 ml-2"),
                on_click=SmartDashboardState.next_rule_step,
                type="button",
                class_name="flex items-center px-6 py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:from-indigo-600 hover:to-purple-700 font-semibold shadow-md hover:shadow-lg transition-all"
            ),
            class_name="flex justify-between items-center gap-3"
        ),
    )


def rule_step_4_slot_selection() -> rx.Component:
    """Step 4: Slot Selection"""
    return rx.el.div(
        rx.el.h3("Select Slot", class_name="text-lg font-bold text-gray-900 mb-1"),
        rx.el.p("Choose your preferred parking slot", class_name="text-sm text-gray-500 mb-4"),
        
        # Zones Container - Grid Layout
        rx.el.div(
            # Zone A Slots
            rx.el.div(
                rx.el.div(
                    rx.icon("circle", class_name="w-2 h-2 bg-orange-500 rounded-full inline-block mr-2"),
                    rx.el.span("Zone A", class_name="text-xs font-bold text-orange-600 uppercase tracking-wider"),
                    class_name="flex items-center mb-2"
                ),
                rx.el.div(
                    rx.foreach(
                        ["A1", "A2", "A3", "A4", "A5"],
                        lambda slot: rx.el.button(
                            rx.el.div(
                                rx.icon("car", class_name="w-4 h-4 mb-0.5"),
                                rx.el.div(slot, class_name="text-xs font-bold"),
                                class_name="flex flex-col items-center justify-center"
                            ),
                            on_click=SmartDashboardState.set_form_slot(slot),
                            type="button",
                            class_name=rx.cond(
                                SmartDashboardState.form_slot == slot,
                                "w-14 h-14 rounded-lg bg-gradient-to-br from-orange-500 via-orange-400 to-yellow-400 text-white font-bold shadow-md border-2 border-orange-600 transform scale-105 transition-all duration-200",
                                "w-14 h-14 rounded-lg bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-300 text-gray-700 font-semibold hover:border-orange-400 hover:shadow-sm hover:scale-105 transition-all duration-200"
                            )
                        )
                    ),
                    class_name="flex gap-2 flex-wrap justify-center"
                ),
                class_name="p-3 bg-orange-50/50 rounded-xl border border-orange-100"
            ),
            
            # Zone B Slots
            rx.el.div(
                rx.el.div(
                    rx.icon("circle", class_name="w-2 h-2 bg-blue-500 rounded-full inline-block mr-2"),
                    rx.el.span("Zone B", class_name="text-xs font-bold text-blue-600 uppercase tracking-wider"),
                    class_name="flex items-center mb-2"
                ),
                rx.el.div(
                    rx.foreach(
                        ["B1", "B2", "B3", "B4", "B5"],
                        lambda slot: rx.el.button(
                            rx.el.div(
                                rx.icon("car", class_name="w-4 h-4 mb-0.5"),
                                rx.el.div(slot, class_name="text-xs font-bold"),
                                class_name="flex flex-col items-center justify-center"
                            ),
                            on_click=SmartDashboardState.set_form_slot(slot),
                            type="button",
                            class_name=rx.cond(
                                SmartDashboardState.form_slot == slot,
                                "w-14 h-14 rounded-lg bg-gradient-to-br from-blue-500 via-blue-400 to-indigo-400 text-white font-bold shadow-md border-2 border-blue-600 transform scale-105 transition-all duration-200",
                                "w-14 h-14 rounded-lg bg-gradient-to-br from-gray-50 to-gray-100 border border-gray-300 text-gray-700 font-semibold hover:border-blue-400 hover:shadow-sm hover:scale-105 transition-all duration-200"
                            )
                        )
                    ),
                    class_name="flex gap-2 flex-wrap justify-center"
                ),
                class_name="p-3 bg-blue-50/50 rounded-xl border border-blue-100"
            ),
            class_name="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6"
        ),
        
        # Selected Slot Indicator - Compact
        rx.cond(
            SmartDashboardState.form_slot != "",
            rx.el.div(
                rx.el.div(
                    rx.icon("check-circle-2", class_name="w-4 h-4 text-green-600 mr-2"),
                    rx.el.span("Selected:", class_name="text-sm font-medium text-gray-600 mr-2"),
                    rx.el.span(SmartDashboardState.form_slot, class_name="text-base font-bold text-gray-900"),
                    class_name="flex items-center"
                ),
                class_name="flex items-center justify-center p-3 bg-green-50 border border-green-200 rounded-lg mb-6"
            ),
            # Placeholder to keep layout stable if nothing selected
            rx.el.div(class_name="h-[50px] mb-6") 
        ),
        
        # Navigation Buttons
        rx.el.div(
            rx.el.button(
                rx.icon("arrow-left", class_name="w-4 h-4 mr-2"),
                "Back",
                on_click=SmartDashboardState.prev_rule_step,
                type="button",
                class_name="flex items-center px-5 py-2.5 text-gray-700 bg-white border-2 border-gray-300 rounded-lg hover:bg-gray-50 font-semibold transition-all"
            ),
            rx.el.button(
                rx.icon("check", class_name="w-4 h-4 mr-2"),
                "Save Rule",
                on_click=SmartDashboardState.save_rule,
                type="button",
                class_name="flex items-center px-6 py-2.5 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:from-green-600 hover:to-emerald-700 font-semibold shadow-md hover:shadow-lg transition-all"
            ),
            class_name="flex justify-between items-center gap-3"
        ),
    )


def rule_modal() -> rx.Component:
    """Multi-step wizard modal for adding/editing rules"""
    return rx.el.div(
        rx.el.div(
            # Header
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            rx.cond(SmartDashboardState.is_editing, "edit", "plus-circle"),
                            class_name="w-6 h-6 text-white"
                        ),
                        class_name="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg"
                    ),
                    rx.el.div(
                        rx.el.h3(
                            rx.cond(SmartDashboardState.is_editing, "Edit Auto-Booking Rule", "Add New Rule"),
                            class_name="text-xl font-bold text-gray-900"
                        ),
                        rx.el.p(
                            "Schedule your parking automatically",
                            class_name="text-sm text-gray-500 mt-0.5"
                        ),
                        class_name="ml-3"
                    ),
                    class_name="flex items-start"
                ),
                rx.el.button(
                    rx.icon("x", class_name="h-5 w-5 text-gray-400 hover:text-gray-600"),
                    on_click=SmartDashboardState.close_rule_modal,
                    class_name="p-2 hover:bg-gray-100 rounded-full transition-colors"
                ),
                class_name="flex justify-between items-start mb-6 pb-4 border-b border-gray-100"
            ),
            
            # Progress Steps
            rx.el.div(
                wizard_progress_bar(),
                rx.el.div(
                    wizard_step_indicator("1", "Location", SmartDashboardState.rule_wizard_step == 1, SmartDashboardState.rule_wizard_step > 1),
                    wizard_step_indicator("2", "Time", SmartDashboardState.rule_wizard_step == 2, SmartDashboardState.rule_wizard_step > 2),
                    wizard_step_indicator("3", "Details", SmartDashboardState.rule_wizard_step == 3, SmartDashboardState.rule_wizard_step > 3),
                    wizard_step_indicator("4", "Slot", SmartDashboardState.rule_wizard_step == 4, False),
                    class_name="flex justify-between relative z-10"
                ),
                class_name="relative mb-8 mx-2"
            ),
            
            # Step Content
            rx.cond(
                SmartDashboardState.rule_wizard_step == 1, rule_step_1_location_days(),
                rx.cond(
                    SmartDashboardState.rule_wizard_step == 2, rule_step_2_time_duration(),
                    rx.cond(
                        SmartDashboardState.rule_wizard_step == 3, rule_step_3_vehicle_phone(),
                        rule_step_4_slot_selection()
                    )
                )
            ),
            
            class_name="bg-white rounded-2xl shadow-2xl p-7 w-full max-w-lg relative border border-gray-100"
        ),
        class_name=rx.cond(
            SmartDashboardState.show_rule_modal,
            "fixed inset-0 z-50 flex items-center justify-center bg-gray-900/60 backdrop-blur-md transition-opacity animate-in fade-in duration-200",
            "hidden"
        )
    )


def rule_card(rule: Rule) -> rx.Component:
    return rx.el.div(
        # Gradient border effect
        rx.el.div(
            # Header section with location and status
            rx.el.div(
                # Left side - Location icon and text
                rx.el.div(
                    rx.el.div(
                        rx.icon("map-pin", class_name="w-5 h-5 text-white"),
                        class_name="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg"
                    ),
                    rx.el.div(
                        rx.el.h3(rule.location, class_name="font-bold text-gray-900 text-base"),
                        rx.el.div(
                            rx.foreach(
                                rule.days,
                                lambda d: rx.el.span(
                                    d, 
                                    class_name="text-xs bg-gradient-to-r from-indigo-50 to-purple-50 text-indigo-700 px-2.5 py-1 rounded-full mr-1 font-medium border border-indigo-100"
                                )
                            ),
                            class_name="flex flex-wrap gap-1 mt-2"
                        ),
                        class_name="ml-3"
                    ),
                    class_name="flex items-start"
                ),
                # Right side - Status badge
                rx.el.div(
                    rx.el.span(
                        rule.status,
                        class_name=rx.cond(
                            rule.status == "Active",
                            "bg-gradient-to-r from-green-500 to-emerald-600 text-white px-4 py-1.5 rounded-full text-xs font-bold shadow-md",
                            "bg-gradient-to-r from-yellow-400 to-orange-500 text-white px-4 py-1.5 rounded-full text-xs font-bold shadow-md"
                        )
                    ),
                ),
                class_name="flex justify-between items-start mb-5"
            ),
            
            # Details section
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("clock", class_name="w-4 h-4 text-indigo-500 mr-2"),
                        rx.el.span(rule.time + " (" + rule.duration + ")", class_name="text-sm text-gray-700 font-medium"),
                        class_name="flex items-center bg-indigo-50 rounded-lg px-3 py-2"
                    ),
                    class_name="flex-1"
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon("calendar", class_name="w-4 h-4 text-purple-500 mr-2"),
                        rx.el.span("Next: " + rule.next_run, class_name="text-sm text-gray-700 font-medium"),
                        class_name="flex items-center bg-purple-50 rounded-lg px-3 py-2"
                    ),
                    class_name="flex-1"
                ),
                class_name="grid grid-cols-2 gap-3 mb-3"
            ),

            # Vehicle & Phone Details
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("car", class_name="w-4 h-4 text-blue-500 mr-2"),
                        rx.el.span(rule.vehicle_number, class_name="text-sm text-gray-700 font-medium uppercase"),
                        class_name="flex items-center bg-blue-50 rounded-lg px-3 py-2"
                    ),
                    class_name="flex-1"
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon("phone", class_name="w-4 h-4 text-green-500 mr-2"),
                        rx.el.span(rule.phone_number, class_name="text-sm text-gray-700 font-medium"),
                        class_name="flex items-center bg-green-50 rounded-lg px-3 py-2"
                    ),
                    class_name="flex-1"
                ),
                class_name="grid grid-cols-2 gap-3 mb-3"
            ),
            
            # Slot Display
            rx.el.div(
                rx.el.div(
                    rx.icon("parking-square", class_name="w-4 h-4 text-orange-500 mr-2"),
                    rx.el.span("Slot: " + rule.slot_id, class_name="text-sm text-gray-700 font-medium"),
                    class_name="flex items-center bg-orange-50 rounded-lg px-3 py-2 w-full"
                ),
                class_name="mb-5"
            ),
            
            # Action buttons
            rx.el.div(
                rx.el.button(
                    rx.icon(
                        rx.cond(rule.status == "Active", "pause", "play"),
                        class_name="w-4 h-4 mr-1.5"
                    ),
                    rx.cond(rule.status == "Active", "Pause", "Resume"),
                    on_click=SmartDashboardState.toggle_rule(rule.id),
                    class_name="flex items-center text-sm font-semibold text-white bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 px-4 py-2 rounded-lg shadow-md hover:shadow-lg transition-all"
                ),
                rx.el.button(
                    rx.icon("edit", class_name="w-4 h-4 mr-1.5"),
                    "Edit",
                    on_click=SmartDashboardState.open_edit_modal(rule),
                    class_name="flex items-center text-sm font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-lg transition-all"
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="w-4 h-4 mr-1.5"),
                    "Delete",
                    on_click=SmartDashboardState.prompt_delete_rule(rule.id),
                    class_name="flex items-center text-sm font-semibold text-red-600 hover:text-white bg-red-50 hover:bg-red-600 px-4 py-2 rounded-lg transition-all"
                ),
                class_name="flex items-center gap-2 pt-5 border-t border-gray-100"
            ),
            class_name="p-5"
        ),
        class_name="bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-lg transition-all duration-300"
    )


def smart_dashboard_page() -> rx.Component:
    """Smart Dashboard page with Auto-Booking capabilities"""
    return rx.box(
        navbar(),
        
        # Modals
        delete_confirmation_modal(),
        rule_modal(),
        
        # Main Content
        rx.el.div(
            # Hero Section
            rx.el.div(
                rx.el.div(
                    rx.el.h1("Smart Auto-Booking Dashboard", class_name="text-4xl font-bold text-gray-900 mb-3"),
                    rx.el.p("Automate your parking bookings and save time", class_name="text-lg text-gray-600 mb-6"),
                    rx.el.button(
                        rx.icon("plus-circle", class_name="w-5 h-5 mr-2"),
                        "Create New Rule",
                        on_click=SmartDashboardState.open_add_modal,
                        class_name="flex items-center px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all hover:scale-105"
                    ),
                    class_name="max-w-7xl mx-auto px-6 py-8"
                ),
                class_name="bg-gradient-to-br from-indigo-50 via-purple-50 to-white border-b border-gray-100"
            ),
            
            # Stats Cards
            rx.el.div(
                rx.el.div(
                    stat_card("Active Rules", SmartDashboardState.rules.length(), "zap", "from-indigo-500 to-purple-600"),
                    stat_card("Money Saved", f"RM {SmartDashboardState.savings:.2f}", "piggy-bank", "from-green-500 to-emerald-600"),
                    stat_card("Hours Saved", f"{SmartDashboardState.hours_saved}h", "clock", "from-orange-500 to-amber-600"),
                    class_name="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
                ),
                class_name="max-w-7xl mx-auto px-6 py-8"
            ),
            
            # Rules List
            rx.el.div(
                rx.el.div(
                    rx.el.h2("Your Auto-Booking Rules", class_name="text-2xl font-bold text-gray-900 mb-6"),
                    rx.cond(
                        SmartDashboardState.rules.length() > 0,
                        rx.el.div(
                            rx.foreach(
                                SmartDashboardState.rules,
                                rule_card
                            ),
                            class_name="grid grid-cols-1 md:grid-cols-2 gap-6"
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.icon("calendar-x", class_name="w-16 h-16 text-gray-300 mb-4"),
                                rx.el.h3("No Auto-Booking Rules Yet", class_name="text-xl font-semibold text-gray-700 mb-2"),
                                rx.el.p("Create your first rule to start automating your parking bookings", class_name="text-gray-500 mb-6"),
                                rx.el.button(
                                    rx.icon("plus-circle", class_name="w-5 h-5 mr-2"),
                                    "Create Your First Rule",
                                    on_click=SmartDashboardState.open_add_modal,
                                    class_name="flex items-center px-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all"
                                ),
                                class_name="flex flex-col items-center justify-center py-16"
                            ),
                            class_name="bg-white rounded-2xl border-2 border-dashed border-gray-200"
                        )
                    ),
                    class_name="max-w-7xl mx-auto px-6 py-8"
                ),
            ),
            
            class_name="min-h-screen bg-gray-50"
        ),
        
        on_mount=[AuthState.check_login, SmartDashboardState.on_load]
    )
