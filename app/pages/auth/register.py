import reflex as rx
from app.states.auth_state import AuthState


def register_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    rx.el.div(
                        rx.icon("car-front", class_name="h-8 w-8 text-sky-500"),
                        rx.el.span(
                            "ParkMyCar",
                            class_name="text-2xl font-bold text-gray-900 tracking-tight",
                        ),
                        class_name="flex items-center gap-2 justify-center mb-8",
                    ),
                    href="/",
                ),
                rx.el.div(
                    rx.el.h2(
                        "Create Account",
                        class_name="text-2xl font-bold text-gray-900 text-center mb-2",
                    ),
                    rx.el.p(
                        "Join thousands of happy drivers",
                        class_name="text-gray-500 text-center mb-8",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Full Name",
                            class_name="block text-sm font-medium text-gray-700 mb-1.5",
                        ),
                        rx.el.div(
                            rx.icon(
                                "user",
                                class_name="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400",
                            ),
                            rx.el.input(
                                placeholder="John Doe",
                                on_change=AuthState.set_full_name,
                                class_name="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 outline-none transition-all bg-gray-50/50 focus:bg-white",
                            ),
                            class_name="relative",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Email Address",
                            class_name="block text-sm font-medium text-gray-700 mb-1.5",
                        ),
                        rx.el.div(
                            rx.icon(
                                "mail",
                                class_name="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400",
                            ),
                            rx.el.input(
                                placeholder="you@example.com",
                                type="email",
                                on_change=AuthState.set_email,
                                class_name="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 outline-none transition-all bg-gray-50/50 focus:bg-white",
                            ),
                            class_name="relative",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Phone Number",
                            class_name="block text-sm font-medium text-gray-700 mb-1.5",
                        ),
                        rx.el.div(
                            rx.icon(
                                "phone",
                                class_name="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400",
                            ),
                            rx.el.input(
                                placeholder="+60 12-345 6789",
                                type="tel",
                                on_change=AuthState.set_phone,
                                class_name="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 outline-none transition-all bg-gray-50/50 focus:bg-white",
                            ),
                            class_name="relative",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Password",
                            class_name="block text-sm font-medium text-gray-700 mb-1.5",
                        ),
                        rx.el.div(
                            rx.icon(
                                "lock",
                                class_name="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400",
                            ),
                            rx.el.input(
                                placeholder="••••••••",
                                type="password",
                                on_change=AuthState.set_password,
                                class_name="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 outline-none transition-all bg-gray-50/50 focus:bg-white",
                            ),
                            class_name="relative",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Confirm Password",
                            class_name="block text-sm font-medium text-gray-700 mb-1.5",
                        ),
                        rx.el.div(
                            rx.icon(
                                "lock-keyhole",
                                class_name="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400",
                            ),
                            rx.el.input(
                                placeholder="••••••••",
                                type="password",
                                on_change=AuthState.set_confirm_password,
                                class_name="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 outline-none transition-all bg-gray-50/50 focus:bg-white",
                            ),
                            class_name="relative",
                        ),
                        class_name="mb-6",
                    ),
                    rx.cond(
                        AuthState.error_message != "",
                        rx.el.div(
                            rx.icon("circle-alert", class_name="h-4 w-4 mr-2"),
                            rx.el.p(AuthState.error_message),
                            class_name="flex items-center p-3 mb-4 text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg",
                        ),
                    ),
                    rx.el.button(
                        rx.cond(
                            AuthState.is_loading,
                            rx.el.div(
                                rx.spinner(size="2", class_name="mr-2 text-white"),
                                "Creating account...",
                                class_name="flex items-center justify-center",
                            ),
                            "Create Account",
                        ),
                        disabled=AuthState.is_loading,
                        on_click=AuthState.register,
                        class_name="w-full py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-semibold shadow-lg shadow-sky-500/30 hover:shadow-sky-500/50 hover:scale-[1.01] active:scale-[0.99] transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed",
                    ),
                    rx.el.p(
                        "By creating an account, you agree to our ",
                        rx.el.a(
                            "Terms of Service",
                            href="#",
                            class_name="text-sky-600 hover:underline",
                        ),
                        " and ",
                        rx.el.a(
                            "Privacy Policy",
                            href="#",
                            class_name="text-sky-600 hover:underline",
                        ),
                        ".",
                        class_name="text-xs text-gray-500 text-center mt-4",
                    ),
                    rx.el.div(class_name="h-px bg-gray-200 my-6"),
                    rx.el.p(
                        "Already have an account? ",
                        rx.el.a(
                            "Sign in",
                            href="/login",
                            class_name="font-semibold text-sky-600 hover:text-sky-700 hover:underline decoration-2 underline-offset-2 transition-all",
                        ),
                        class_name="text-center text-sm text-gray-600",
                    ),
                    class_name="p-8 bg-white/80 backdrop-blur-xl rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white/20",
                ),
                class_name="w-full max-w-md",
            ),
            class_name="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-sky-50 via-white to-indigo-50",
        ),
        class_name="font-['Roboto']",
    )