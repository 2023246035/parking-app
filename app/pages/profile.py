import reflex as rx
from app.components.navbar import navbar
from app.components.footer import footer
from app.states.user_state import UserState
from app.states.booking_state import BookingState
from app.states.auth_state import AuthState


def stat_card(label: str, value: str, icon: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-6 w-6 text-white"),
            class_name="h-12 w-12 rounded-xl bg-gradient-to-br from-sky-500 to-blue-600 flex items-center justify-center mb-3 shadow-lg shadow-sky-500/20",
        ),
        rx.el.p(label, class_name="text-sm text-gray-500 font-medium"),
        rx.el.p(value, class_name="text-2xl font-bold text-gray-900"),
        class_name="bg-white/80 backdrop-blur-sm p-6 rounded-2xl border border-white/20 shadow-lg hover:shadow-xl transition-shadow",
    )


def profile_field(
    label: str, default_value: str, on_change: rx.event.EventHandler, type: str = "text"
) -> rx.Component:
    return rx.el.div(
        rx.el.label(label, class_name="block text-sm font-medium text-gray-700 mb-1.5"),
        rx.el.input(
            type=type,
            default_value=default_value,
            on_change=on_change,
            class_name="w-full rounded-xl border border-gray-200 px-4 py-2.5 focus:ring-2 focus:ring-sky-200 focus:border-sky-500 outline-none text-gray-900 bg-gray-50/50 focus:bg-white transition-all",
        ),
        class_name="mb-5",
    )


def profile_page() -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.main(
            rx.el.div(
                rx.el.div(
                    rx.el.h1(
                        "My Profile", class_name="text-3xl font-bold text-gray-900 mb-8"
                    ),
                    class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-12",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.image(
                                    src=UserState.user.avatar_url,
                                    class_name="w-24 h-24 rounded-full border-4 border-white shadow-xl",
                                ),
                                rx.el.div(
                                    rx.el.h2(
                                        UserState.user.name,
                                        class_name="text-2xl font-bold text-gray-900",
                                    ),
                                    rx.el.p(
                                        f"Member since {UserState.user.member_since}",
                                        class_name="text-sm text-gray-500",
                                    ),
                                    class_name="ml-6",
                                ),
                                class_name="flex items-center mb-10",
                            ),
                            rx.el.form(
                                profile_field(
                                    "Full Name",
                                    UserState.user.name,
                                    UserState.update_name,
                                ),
                                profile_field(
                                    "Email Address",
                                    UserState.user.email,
                                    UserState.update_email,
                                    type="email",
                                ),
                                profile_field(
                                    "Phone Number",
                                    UserState.user.phone,
                                    UserState.update_phone,
                                    type="tel",
                                ),
                                rx.el.div(
                                    rx.el.button(
                                        "Save Changes",
                                        type="button",
                                        on_click=UserState.save_profile,
                                        class_name="bg-gradient-to-r from-sky-500 to-blue-600 text-white px-8 py-3 rounded-xl font-semibold hover:shadow-lg hover:shadow-sky-500/30 hover:scale-105 active:scale-95 transition-all",
                                    ),
                                    class_name="flex justify-end pt-6 border-t border-gray-100",
                                ),
                            ),
                            class_name="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl border border-white/20 p-10",
                        ),
                        class_name="col-span-1 lg:col-span-2",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3(
                                "Overview",
                                class_name="text-lg font-bold text-gray-900 mb-6",
                            ),
                            rx.el.div(
                                stat_card(
                                    "Active Bookings",
                                    BookingState.active_bookings.length().to_string(),
                                    "car-front",
                                ),
                                stat_card(
                                    "Total Bookings",
                                    BookingState.bookings.length().to_string(),
                                    "ticket",
                                ),
                                stat_card(
                                    "Total Spent",
                                    f"RM {BookingState.total_spent:.2f}",
                                    "wallet",
                                ),
                                class_name="space-y-6",
                            ),
                            class_name="bg-white/40 backdrop-blur-sm rounded-3xl p-8 border border-white/20",
                        ),
                        class_name="col-span-1",
                    ),
                    class_name="grid grid-cols-1 lg:grid-cols-3 gap-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-24",
                ),
            ),
            class_name="flex-1 bg-gradient-to-br from-sky-50 via-white to-indigo-50",
        ),
        footer(),
        class_name="font-['Roboto'] min-h-screen flex flex-col",
    )