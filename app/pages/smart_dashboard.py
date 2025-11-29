import reflex as rx
import json
from typing import Dict, List
from app.components.navbar import navbar
from app.components.footer import footer
from app.services.ai.auto_booking_ai import AutoBookingAgent
from app.db.models import User
from sqlmodel import select
from app.db.ai_models import AutoBookingSetting


class BookingPattern(rx.Base):
    """Model for a detected booking pattern"""
    day: str
    time: str
    duration: int
    lot_id: int
    frequency: int


class AutoBookingState(rx.State):
    """State for the Auto-Booking Smart Dashboard"""
    
    # User Settings
    enabled: bool = False
    auto_confirm: bool = False
    max_price: float = 15.0
    
    # AI Insights
    patterns: List[BookingPattern] = []
    confidence_score: float = 0.0
    
    # UI State
    is_loading: bool = False
    session_email: str = rx.Cookie("session_email")
    
    @rx.event
    def on_load(self):
        """Load data when page opens"""
        self.is_loading = True
        yield AutoBookingState.fetch_data

    @rx.event
    async def fetch_data(self):
        """Fetch user settings and AI patterns"""
        if not self.session_email:
            self.is_loading = False
            return

        try:
            with rx.session() as session:
                user = session.exec(select(User).where(User.email == self.session_email)).first()
                if not user:
                    return

                user_id = user.id
                
                # 1. Get Settings
                settings = session.exec(
                    select(AutoBookingSetting).where(AutoBookingSetting.user_id == user_id)
                ).first()
                
                if settings:
                    self.enabled = settings.enabled
                    self.auto_confirm = settings.auto_confirm
                    self.max_price = settings.max_price_threshold or 15.0
                
                # 2. Get AI Patterns
                detected_patterns = AutoBookingAgent.detect_booking_patterns(user_id)
                raw_patterns = detected_patterns.get("weekly_patterns", {})
                
                # Convert dict to list of BookingPattern objects
                self.patterns = [
                    BookingPattern(
                        day=day,
                        time=data["time"],
                        duration=data["duration"],
                        lot_id=data["lot_id"],
                        frequency=data["frequency"]
                    )
                    for day, data in raw_patterns.items()
                ]
                
                self.confidence_score = detected_patterns.get("confidence", 0.0)
                
        except Exception as e:
            print(f"Error fetching auto-booking data: {e}")
            yield rx.toast.error("Failed to load AI insights")
        finally:
            self.is_loading = False

    @rx.event
    async def save_settings(self):
        """Save user preferences"""
        if not self.session_email:
            return

        try:
            with rx.session() as session:
                user = session.exec(select(User).where(User.email == self.session_email)).first()
                if not user:
                    return

                success = await AutoBookingAgent.save_auto_booking_settings(
                    user_id=user.id,
                    enabled=self.enabled,
                    auto_confirm=self.auto_confirm,
                    max_price_threshold=self.max_price
                )
                
                if success:
                    yield rx.toast.success("Settings updated!")
                else:
                    yield rx.toast.error("Failed to save settings")
                    
        except Exception as e:
            print(f"Error saving settings: {e}")

    @rx.event
    def toggle_enabled(self, checked: bool):
        self.enabled = checked
        yield AutoBookingState.save_settings

    @rx.event
    def toggle_auto_confirm(self, checked: bool):
        self.auto_confirm = checked
        yield AutoBookingState.save_settings

    @rx.event
    def set_max_price(self, value: list[int]):
        self.max_price = float(value[0])
        yield AutoBookingState.save_settings


def pattern_card(pattern: BookingPattern) -> rx.Component:
    """Card showing a detected pattern with premium styling"""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    pattern.day.capitalize(),
                    class_name="text-xs font-bold text-indigo-500 uppercase tracking-wider"
                ),
                rx.el.span(
                    f"{pattern.frequency}x Found",
                    class_name="text-[10px] font-bold bg-indigo-50 text-indigo-600 px-2 py-1 rounded-full border border-indigo-100"
                ),
                class_name="flex justify-between items-center mb-3"
            ),
            rx.el.div(
                rx.icon("clock", class_name="w-5 h-5 text-gray-400 mr-2"),
                rx.el.span(
                    pattern.time,
                    class_name="text-2xl font-black text-gray-900 tracking-tight"
                ),
                class_name="flex items-center mb-2"
            ),
            rx.el.div(
                rx.icon("map-pin", class_name="w-4 h-4 text-gray-400 mr-2"),
                rx.el.span(
                    f"Lot ID: {pattern.lot_id}",
                    class_name="text-sm font-medium text-gray-500"
                ),
                class_name="flex items-center"
            ),
            class_name="p-5 bg-white rounded-2xl border border-gray-100 shadow-sm hover:shadow-md hover:border-indigo-200 transition-all duration-300 group"
        ),
        class_name="col-span-1"
    )


def smart_dashboard_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        
        rx.el.div(
            # Header
            rx.el.div(
                rx.el.h1(
                    "Smart Dashboard",
                    class_name="text-4xl font-black text-gray-900 mb-2 tracking-tight"
                ),
                rx.el.p(
                    "Manage your AI Auto-Booking preferences and view insights.",
                    class_name="text-lg text-gray-500"
                ),
                class_name="mb-12"
            ),
            
            rx.el.div(
                # Left Column: Settings
                rx.el.div(
                    # Main Toggle Card
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.h3("AI Agent Status", class_name="text-lg font-bold text-gray-900"),
                                rx.el.p("Allow AI to book spots automatically", class_name="text-sm text-gray-500"),
                            ),
                            rx.switch(
                                checked=AutoBookingState.enabled,
                                on_change=AutoBookingState.toggle_enabled,
                                color_scheme="indigo",
                                size="3",
                                class_name="cursor-pointer"
                            ),
                            class_name="flex justify-between items-center mb-6"
                        ),
                        rx.el.div(
                            rx.cond(
                                AutoBookingState.enabled,
                                rx.el.div(
                                    rx.icon("sparkles", class_name="w-5 h-5 text-indigo-600 mr-2"),
                                    rx.el.span("AI Active", class_name="font-bold text-indigo-700"),
                                    class_name="flex items-center"
                                ),
                                rx.el.div(
                                    rx.icon("pause-circle", class_name="w-5 h-5 text-gray-400 mr-2"),
                                    rx.el.span("AI Paused", class_name="font-bold text-gray-500"),
                                    class_name="flex items-center"
                                )
                            ),
                            class_name=rx.cond(
                                AutoBookingState.enabled,
                                "bg-indigo-50 border border-indigo-100 p-3 rounded-xl transition-colors duration-300",
                                "bg-gray-50 border border-gray-200 p-3 rounded-xl transition-colors duration-300"
                            )
                        ),
                        class_name="p-6 bg-white rounded-3xl shadow-lg shadow-gray-200/50 border border-gray-100 mb-6"
                    ),
                    
                    # Configuration Card
                    rx.el.div(
                        rx.el.h3("Configuration", class_name="text-sm font-bold text-gray-400 uppercase tracking-wider mb-6"),
                        
                        # Auto-Confirm
                        rx.el.div(
                            rx.el.div(
                                rx.el.span("Auto-Confirm", class_name="font-bold text-gray-900 block"),
                                rx.el.span("Skip manual approval", class_name="text-xs text-gray-500"),
                            ),
                            rx.switch(
                                checked=AutoBookingState.auto_confirm,
                                on_change=AutoBookingState.toggle_auto_confirm,
                                color_scheme="gray",
                            ),
                            class_name="flex justify-between items-center mb-8"
                        ),
                        
                        # Price Limit
                        rx.el.div(
                            rx.el.div(
                                rx.el.span("Max Price Limit", class_name="font-bold text-gray-900"),
                                rx.el.span(f"RM {AutoBookingState.max_price:.0f}", class_name="font-bold text-indigo-600 bg-indigo-50 px-2 py-1 rounded-lg text-sm"),
                                class_name="flex justify-between items-center mb-4"
                            ),
                            rx.slider(
                                default_value=[15],
                                value=[AutoBookingState.max_price],
                                on_change=AutoBookingState.set_max_price,
                                min=5,
                                max=50,
                                step=1,
                                class_name="w-full"
                            ),
                            rx.el.p("Don't book if price exceeds this limit", class_name="text-xs text-gray-400 mt-2"),
                        ),
                        
                        class_name="p-8 bg-white rounded-3xl shadow-lg shadow-gray-200/50 border border-gray-100"
                    ),
                    class_name="col-span-1"
                ),
                
                # Right Column: Insights
                rx.el.div(
                    # Confidence Score Card
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3("Pattern Confidence", class_name="text-sm font-bold text-white/80 uppercase tracking-wider mb-1"),
                            rx.el.p("How well we know your routine", class_name="text-xs text-white/60"),
                        ),
                        rx.el.div(
                            rx.el.span(
                                f"{AutoBookingState.confidence_score * 100:.0f}%",
                                class_name="text-5xl font-black text-white tracking-tighter"
                            ),
                            rx.icon("activity", class_name="w-12 h-12 text-white/20 absolute right-6 top-6"),
                            class_name="mt-4 relative"
                        ),
                        # Progress Bar
                        rx.el.div(
                            rx.el.div(
                                class_name="h-full bg-white/30 rounded-full",
                                style={"width": f"{AutoBookingState.confidence_score * 100}%"}
                            ),
                            class_name="h-2 w-full bg-black/20 rounded-full mt-6 overflow-hidden"
                        ),
                        class_name="p-8 bg-gradient-to-br from-indigo-600 to-purple-700 rounded-3xl shadow-xl shadow-indigo-500/30 text-white mb-8 relative overflow-hidden"
                    ),
                    
                    # Patterns Grid
                    rx.el.div(
                        rx.el.h3("Detected Routine", class_name="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2"),
                        rx.cond(
                            AutoBookingState.patterns,
                            rx.el.div(
                                rx.foreach(
                                    AutoBookingState.patterns,
                                    pattern_card
                                ),
                                class_name="grid grid-cols-1 sm:grid-cols-2 gap-4"
                            ),
                            rx.el.div(
                                rx.icon("search", class_name="w-10 h-10 text-gray-300 mb-3"),
                                rx.el.p("No patterns detected yet", class_name="font-bold text-gray-900"),
                                rx.el.p("Keep booking to train the AI", class_name="text-sm text-gray-500"),
                                class_name="p-10 bg-gray-50 rounded-3xl border-2 border-dashed border-gray-200 flex flex-col items-center justify-center text-center"
                            )
                        ),
                    ),
                    
                    class_name="col-span-1 md:col-span-2"
                ),
                
                class_name="grid grid-cols-1 md:grid-cols-3 gap-8"
            ),
            
            class_name="max-w-7xl mx-auto px-6 py-12"
        ),
        
        footer(),
        class_name="min-h-screen bg-gray-50 font-['Inter',sans-serif]",
        on_mount=AutoBookingState.on_load
    )
