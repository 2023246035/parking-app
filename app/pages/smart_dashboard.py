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
    
    # Form Fields
    form_location: str = ""
    form_days: List[str] = []
    form_time: str = "09:00"
    form_duration: str = "1"
    
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
                            slot_id="AUTO-A1", # Placeholder
                            vehicle_number="AUTO-CAR", # Placeholder
                            phone_number=user.phone or "N/A"
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
                    next_run=r.next_run
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
        self.show_rule_modal = True
        
    @rx.event
    def open_edit_modal(self, rule: Rule):
        self.is_editing = True
        self.editing_rule_id = rule.id
        self.form_location = rule.location
        self.form_days = rule.days
        self.form_time = rule.time
        self.form_duration = rule.duration.replace(" hours", "").replace(" hour", "")
        self.show_rule_modal = True
        
    @rx.event
    def close_rule_modal(self):
        self.show_rule_modal = False
        
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
    def toggle_day(self, day: str):
        if day in self.form_days:
            self.form_days.remove(day)
        else:
            self.form_days.append(day)

    @rx.event
    async def save_rule(self):
        """Save new or updated rule to DB"""
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
                    session.add(rule)
            else:
                new_rule = DBBookingRule(
                    location=self.form_location,
                    days=days_str,
                    time=self.form_time,
                    duration=duration_str,
                    status="Active",
                    next_run="Tomorrow",  # Simplified logic
                    user_id=user.id
                )
                session.add(new_rule)
            
            session.commit()
            
        self.show_rule_modal = False
        return SmartDashboardState.load_rules


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


def rule_modal() -> rx.Component:
    """Modal for adding/editing rules"""
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    return rx.el.div(
        rx.el.div(
            # Gradient header
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
                class_name="mb-6 pb-4 border-b border-gray-100"
            ),
            
            # Form
            rx.el.div(
                # Location
                rx.el.div(
                    rx.el.label(
                        rx.icon("map-pin", class_name="w-4 h-4 inline mr-1.5"),
                        "Location",
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
                    class_name="mb-5"
                ),
                
                # Days
                rx.el.div(
                    rx.el.label(
                        rx.icon("calendar", class_name="w-4 h-4 inline mr-1.5"),
                        "Days",
                        class_name="flex items-center text-sm font-semibold text-gray-700 mb-2"
                    ),
                    rx.el.div(
                        rx.foreach(
                            days,
                            lambda day: rx.el.button(
                                day,
                                on_click=lambda: SmartDashboardState.toggle_day(day),
                                class_name=rx.cond(
                                    SmartDashboardState.form_days.contains(day),
                                    "bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-md hover:shadow-lg",
                                    "bg-gray-100 text-gray-600 hover:bg-gray-200"
                                ) + " px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200"
                            )
                        ),
                        class_name="flex flex-wrap gap-2"
                    ),
                    class_name="mb-5"
                ),
                
                # Time & Duration Row
                rx.el.div(
                    # Time
                    rx.el.div(
                        rx.el.label(
                            rx.icon("clock", class_name="w-4 h-4 inline mr-1.5"),
                            "Time",
                            class_name="flex items-center text-sm font-semibold text-gray-700 mb-2"
                        ),
                        rx.el.div(
                            rx.el.input(
                                type="time",
                                value=SmartDashboardState.form_time,
                                on_change=SmartDashboardState.set_form_time,
                                class_name="w-full px-4 py-2.5 rounded-lg border-2 border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 transition-all"
                            ),
                            class_name="relative"
                        ),
                        class_name="flex-1"
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
                            class_name="w-full px-4 py-2.5 rounded-lg border-2 border-gray-200 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
                        ),
                        class_name="flex-1"
                    ),
                    class_name="grid grid-cols-2 gap-4 mb-6"
                ),
            ),
            
            # Actions
            rx.el.div(
                rx.el.button(
                    rx.icon("x", class_name="w-4 h-4 mr-1.5"),
                    "Cancel",
                    on_click=SmartDashboardState.close_rule_modal,
                    class_name="flex items-center px-5 py-2.5 text-sm font-semibold text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-all"
                ),
                rx.el.button(
                    rx.icon("check", class_name="w-4 h-4 mr-1.5"),
                    "Save Rule",
                    on_click=SmartDashboardState.save_rule,
                    class_name="flex items-center px-6 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg hover:from-indigo-600 hover:to-purple-700 shadow-md hover:shadow-lg transition-all"
                ),
                class_name="flex justify-end gap-3"
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
                class_name="grid grid-cols-2 gap-3 mb-5"
            ),
            
            # Action buttons
            rx.el.div(
                rx.el.button(
                    rx.icon(
                        rx.cond(rule.status == "Active", "pause", "play"),
                        class_name="w-4 h-4 mr-1.5"
                    ),
                    rx.cond(rule.status == "Active", "Pause", "Resume"),
                    on_click=lambda: SmartDashboardState.toggle_rule(rule.id),
                    class_name="flex items-center text-sm font-semibold text-white bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 px-4 py-2 rounded-lg shadow-md hover:shadow-lg transition-all"
                ),
                rx.el.button(
                    rx.icon("edit", class_name="w-4 h-4 mr-1.5"),
                    "Edit",
                    on_click=lambda: SmartDashboardState.open_edit_modal(rule),
                    class_name="flex items-center text-sm font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-lg transition-all"
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="w-4 h-4 mr-1.5"),
                    "Delete",
                    on_click=lambda: SmartDashboardState.prompt_delete_rule(rule.id),
                    class_name="flex items-center text-sm font-semibold text-red-600 hover:text-white bg-red-50 hover:bg-red-600 px-4 py-2 rounded-lg transition-all"
                ),
                class_name="flex items-center gap-2 pt-5 border-t border-gray-100"
            ),
            class_name="bg-white p-6 rounded-2xl"
        ),
        class_name="relative bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-50 p-[2px] rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02]"
    )


def smart_dashboard_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        
        rx.el.main(
            rx.el.div(
                # Header
                rx.el.div(
                    rx.el.h1("Smart Dashboard", class_name="text-3xl font-bold text-gray-900"),
                    rx.el.p("Manage your AI preferences and auto-booking rules", class_name="text-gray-600 mt-1"),
                    class_name="mb-8"
                ),
                
                # Stats Row
                rx.el.div(
                    stat_card("Total Savings", "RM " + SmartDashboardState.savings.to_string(), "wallet", "from-green-500 to-emerald-600"),
                    stat_card("Hours Saved", SmartDashboardState.hours_saved.to_string() + " hrs", "clock", "from-blue-500 to-indigo-600"),
                    stat_card("Active Rules", SmartDashboardState.rules.length().to_string() + " Rules", "zap", "from-purple-500 to-violet-600"),
                    class_name="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12"
                ),
                
                # Content Grid
                rx.el.div(
                    # Left Column: Rules
                    rx.el.div(
                        rx.el.div(
                            rx.el.h2("Auto-Booking Rules", class_name="text-xl font-bold text-gray-900"),
                            rx.el.button(
                                "+ New Rule",
                                on_click=SmartDashboardState.open_add_modal,
                                class_name="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-800"
                            ),
                            class_name="flex justify-between items-center mb-6"
                        ),
                        
                        rx.el.div(
                            rx.foreach(SmartDashboardState.rules, rule_card),
                            class_name="space-y-4"
                        ),
                        class_name="col-span-2"
                    ),
                    
                    # Right Column: AI Insights
                    rx.el.div(
                        rx.el.div(
                            rx.el.h2("AI Insights", class_name="text-xl font-bold text-gray-900 mb-6"),
                            
                            rx.el.div(
                                rx.el.div(
                                    rx.icon("trending-down", class_name="w-5 h-5 text-green-600 mt-1 mr-3"),
                                    rx.el.div(
                                        rx.el.h4("Price Drop Alert", class_name="font-bold text-gray-900 text-sm"),
                                        rx.el.p("Sunway Pyramid prices are 20% lower on Tuesdays.", class_name="text-sm text-gray-600 mt-1"),
                                    ),
                                    class_name="flex items-start p-4 bg-green-50 rounded-xl mb-4"
                                ),
                                rx.el.div(
                                    rx.icon("alert-circle", class_name="w-5 h-5 text-orange-600 mt-1 mr-3"),
                                    rx.el.div(
                                        rx.el.h4("High Demand Warning", class_name="font-bold text-gray-900 text-sm"),
                                        rx.el.p("KLCC is expected to be full by 10 AM tomorrow.", class_name="text-sm text-gray-600 mt-1"),
                                    ),
                                    class_name="flex items-start p-4 bg-orange-50 rounded-xl"
                                ),
                            ),
                        ),
                        class_name="col-span-1"
                    ),
                    class_name="grid grid-cols-1 lg:grid-cols-3 gap-12"
                ),
                
                class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12"
            ),
            
            # Modals
            delete_confirmation_modal(),
            rule_modal(),
            
            class_name="bg-gray-50 min-h-screen"
        ),
        
        class_name="font-['Roboto']",
        on_mount=[AuthState.check_login, SmartDashboardState.on_load]
    )
