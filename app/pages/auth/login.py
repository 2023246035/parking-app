import reflex as rx
from app.states.auth_state import AuthState


def login_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.a(
                        rx.el.div(
                            rx.icon("car-front", class_name="h-10 w-10 text-white"),
                            rx.el.span(
                                "ParkMyCar",
                                class_name="text-3xl font-bold text-white tracking-tight",
                            ),
                            class_name="flex items-center gap-3 mb-12",
                        ),
                        href="/",
                    ),
                    rx.el.div(
                        rx.el.h2(
                            "Smart Parking Simplified.",
                            class_name="text-4xl font-bold text-white mb-6 leading-tight",
                        ),
                        rx.el.p(
                            "Join thousands of drivers who save time and money by booking parking spots in advance.",
                            class_name="text-lg text-sky-100 leading-relaxed mb-8",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    rx.image(
                                        src="https://api.dicebear.com/9.x/notionists/svg?seed=Sarah",
                                        class_name="h-12 w-12 rounded-full border-2 border-white/30",
                                    ),
                                    rx.el.div(
                                        rx.el.p(
                                            "Best parking app I've used! Saved me so much hassle in KL.",
                                            class_name="text-white font-medium italic mb-2",
                                        ),
                                        rx.el.p(
                                            "- Sarah L., Verified User",
                                            class_name="text-sm text-sky-200 font-semibold",
                                        ),
                                        class_name="bg-white/10 backdrop-blur-md p-4 rounded-xl border border-white/10",
                                    ),
                                    class_name="flex flex-col gap-4",
                                )
                            ),
                            class_name="mt-auto",
                        ),
                        class_name="flex flex-col h-full justify-center max-w-lg mx-auto lg:mx-0",
                    ),
                    class_name="relative z-10 h-full flex flex-col justify-between p-12",
                ),
                rx.el.div(
                    rx.el.div(
                        class_name="absolute top-[-10%] left-[-10%] w-96 h-96 bg-sky-400/30 rounded-full blur-3xl"
                    ),
                    rx.el.div(
                        class_name="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-indigo-500/30 rounded-full blur-3xl"
                    ),
                    class_name="absolute top-0 left-0 w-full h-full overflow-hidden z-0",
                ),
                class_name="hidden lg:flex flex-col relative bg-gradient-to-br from-sky-600 to-indigo-800 w-full lg:w-1/2 h-full",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Welcome Back",
                            class_name="text-3xl font-bold text-gray-900 mb-2",
                        ),
                        rx.el.p(
                            "Please enter your details to sign in.",
                            class_name="text-gray-500 mb-8",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Email Address",
                                class_name="block text-sm font-semibold text-gray-700 mb-2",
                            ),
                            rx.el.input(
                                placeholder="you@example.com",
                                type="email",
                                on_change=AuthState.set_email,
                                class_name="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-sky-500 focus:ring-4 focus:ring-sky-500/10 outline-none transition-all bg-gray-50 focus:bg-white text-gray-900",
                            ),
                            class_name="mb-5",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.label(
                                    "Password",
                                    class_name="block text-sm font-semibold text-gray-700",
                                ),
                                rx.el.a(
                                    "Forgot Password?",
                                    href="/forgot-password",
                                    class_name="text-sm font-medium text-sky-600 hover:text-sky-700 transition-colors",
                                ),
                                class_name="flex justify-between items-center mb-2",
                            ),
                            rx.el.input(
                                placeholder="••••••••",
                                type="password",
                                on_change=AuthState.set_password,
                                class_name="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-sky-500 focus:ring-4 focus:ring-sky-500/10 outline-none transition-all bg-gray-50 focus:bg-white text-gray-900",
                            ),
                            class_name="mb-6",
                        ),
                        rx.cond(
                            AuthState.error_message != "",
                            rx.el.div(
                                rx.icon(
                                    "circle-alert",
                                    class_name="h-5 w-5 text-red-500 mr-2 flex-shrink-0",
                                ),
                                rx.el.p(
                                    AuthState.error_message,
                                    class_name="text-sm text-red-600 font-medium",
                                ),
                                class_name="flex items-center p-4 mb-6 bg-red-50 border border-red-100 rounded-xl animate-fadeIn",
                            ),
                        ),
                        rx.el.button(
                            rx.cond(
                                AuthState.is_loading,
                                rx.el.div(
                                    rx.spinner(size="2", class_name="mr-2 text-white"),
                                    "Signing in...",
                                    class_name="flex items-center justify-center",
                                ),
                                "Sign In",
                            ),
                            disabled=AuthState.is_loading,
                            on_click=AuthState.login,
                            class_name="w-full py-3.5 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 text-white font-bold text-lg shadow-lg shadow-sky-500/20 hover:shadow-sky-500/40 hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none",
                        ),
                        rx.el.div(
                            rx.el.div(class_name="h-px bg-gray-200 flex-1"),
                            rx.el.span(
                                "or",
                                class_name="text-xs text-gray-400 font-medium px-4 uppercase",
                            ),
                            rx.el.div(class_name="h-px bg-gray-200 flex-1"),
                            class_name="flex items-center my-8",
                        ),
                        rx.el.div(
                            rx.el.button(
                                rx.icon(
                                    "chrome", class_name="h-5 w-5 mr-2 text-gray-900"
                                ),
                                "Google",
                                class_name="flex-1 flex items-center justify-center py-3 border border-gray-200 rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-all font-semibold text-gray-700",
                            ),
                            rx.el.button(
                                rx.icon(
                                    "facebook", class_name="h-5 w-5 mr-2 text-blue-600"
                                ),
                                "Facebook",
                                class_name="flex-1 flex items-center justify-center py-3 border border-gray-200 rounded-xl hover:bg-gray-50 hover:border-gray-300 transition-all font-semibold text-gray-700",
                            ),
                            class_name="flex gap-4 mb-8",
                        ),
                        rx.el.p(
                            "Don't have an account? ",
                            rx.el.a(
                                "Create free account",
                                href="/register",
                                class_name="font-bold text-sky-600 hover:text-sky-700 hover:underline decoration-2 underline-offset-4 transition-all",
                            ),
                            class_name="text-center text-sm text-gray-500",
                        ),
                        class_name="w-full max-w-md mx-auto",
                    ),
                    class_name="flex items-center justify-center h-full p-8 lg:p-12",
                ),
                class_name="w-full lg:w-1/2 h-full bg-white",
            ),
            class_name="flex flex-col lg:flex-row h-screen w-full overflow-hidden bg-white",
        ),
        class_name="font-['Roboto']",
    )