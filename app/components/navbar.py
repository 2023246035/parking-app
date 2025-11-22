import reflex as rx
from app.states.auth_state import AuthState
from app.states.user_state import UserState


def navbar_link(text: str, url: str) -> rx.Component:
    return rx.el.a(
        text,
        href=url,
        class_name="text-sm font-medium text-gray-600 hover:text-sky-600 transition-all duration-200 hover:bg-sky-50 px-3 py-2 rounded-lg",
    )


def navbar() -> rx.Component:
    return rx.el.nav(
        rx.el.div(
            rx.el.a(
                rx.el.div(
                    rx.el.div(
                        rx.icon("car-front", class_name="h-6 w-6 text-white"),
                        class_name="bg-gradient-to-br from-sky-500 to-blue-600 p-1.5 rounded-lg shadow-lg shadow-sky-500/20",
                    ),
                    rx.el.span(
                        "ParkMyCar",
                        class_name="text-xl font-bold text-gray-900 tracking-tight",
                    ),
                    class_name="flex items-center gap-3",
                ),
                href="/",
            ),
            rx.el.div(
                navbar_link("Home", "/"),
                navbar_link("Find Parking", "/listings"),
                rx.cond(
                    AuthState.is_authenticated,
                    rx.fragment(
                        navbar_link("My Bookings", "/bookings"),
                        navbar_link("Profile", "/profile"),
                    ),
                ),
                class_name="hidden md:flex items-center gap-2",
            ),
            rx.el.div(
                rx.cond(
                    AuthState.is_authenticated,
                    rx.el.div(
                        rx.el.span(
                            f"Hi, {UserState.user.name.split(' ')[0]}",
                            class_name="text-sm font-medium text-gray-600 mr-4",
                        ),
                        rx.el.button(
                            "Log Out",
                            on_click=AuthState.logout,
                            class_name="text-sm font-medium text-red-500 hover:text-red-600 hover:bg-red-50 px-4 py-2 rounded-lg transition-colors",
                        ),
                        class_name="flex items-center",
                    ),
                    rx.el.div(
                        rx.el.a(
                            rx.el.button(
                                "Sign In",
                                class_name="text-sm font-medium text-gray-600 hover:text-gray-900 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors",
                            ),
                            href="/login",
                        ),
                        rx.el.a(
                            rx.el.button(
                                "Get Started",
                                class_name="text-sm font-medium bg-gradient-to-r from-sky-500 to-blue-600 text-white px-5 py-2 rounded-lg hover:shadow-lg hover:shadow-sky-500/30 hover:scale-105 active:scale-95 transition-all duration-200",
                            ),
                            href="/register",
                        ),
                        class_name="flex items-center gap-2",
                    ),
                ),
                class_name="hidden md:flex items-center",
            ),
            rx.el.button(
                rx.icon("menu", class_name="h-6 w-6 text-gray-600"),
                class_name="md:hidden p-2 rounded-lg hover:bg-gray-100",
            ),
            class_name="flex items-center justify-between h-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8",
        ),
        class_name="sticky top-0 z-50 w-full bg-white/70 backdrop-blur-lg border-b border-white/20 shadow-[0_4px_30px_rgb(0,0,0,0.03)]",
    )