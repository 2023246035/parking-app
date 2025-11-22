import reflex as rx
from app.states.auth_state import AuthState


def forgot_password_page() -> rx.Component:
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
                        "Reset Password",
                        class_name="text-2xl font-bold text-gray-900 text-center mb-2",
                    ),
                    rx.el.p(
                        "Enter your email to receive reset instructions",
                        class_name="text-gray-500 text-center mb-8",
                    ),
                    rx.cond(
                        AuthState.success_message != "",
                        rx.el.div(
                            rx.icon(
                                "check_check",
                                class_name="h-12 w-12 text-green-500 mb-4",
                            ),
                            rx.el.p(
                                "Check your email",
                                class_name="text-lg font-semibold text-gray-900 mb-2",
                            ),
                            rx.el.p(
                                AuthState.success_message,
                                class_name="text-center text-gray-600 mb-6",
                            ),
                            rx.el.a(
                                rx.el.button(
                                    "Back to Login",
                                    class_name="w-full py-2.5 rounded-xl bg-gray-100 text-gray-700 font-semibold hover:bg-gray-200 transition-colors",
                                ),
                                href="/login",
                                class_name="w-full",
                            ),
                            class_name="flex flex-col items-center",
                        ),
                        rx.el.div(
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
                                        rx.spinner(
                                            size="2", class_name="mr-2 text-white"
                                        ),
                                        "Sending link...",
                                        class_name="flex items-center justify-center",
                                    ),
                                    "Send Reset Link",
                                ),
                                disabled=AuthState.is_loading,
                                on_click=AuthState.request_password_reset,
                                class_name="w-full py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-semibold shadow-lg shadow-sky-500/30 hover:shadow-sky-500/50 hover:scale-[1.01] active:scale-[0.99] transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed",
                            ),
                            rx.el.div(
                                rx.el.a(
                                    rx.el.span("← Back to Login"),
                                    href="/login",
                                    class_name="text-sm font-medium text-gray-500 hover:text-gray-800 transition-colors",
                                ),
                                class_name="mt-6 text-center",
                            ),
                        ),
                    ),
                    class_name="p-8 bg-white/80 backdrop-blur-xl rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white/20",
                ),
                class_name="w-full max-w-md",
            ),
            class_name="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-sky-50 via-white to-indigo-50",
        ),
        class_name="font-['Roboto']",
    )