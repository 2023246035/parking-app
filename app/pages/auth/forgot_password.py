import reflex as rx
from app.states.auth_state import AuthState


def email_step() -> rx.Component:
    """Step 1: Email entry"""
    return rx.el.div(
        rx.el.h2(
            "Reset Password",
            class_name="text-2xl font-bold text-gray-900 text-center mb-2",
        ),
        rx.el.p(
            "Enter your email to receive an OTP code",
            class_name="text-gray-500 text-center mb-8",
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
                    value=AuthState.email,
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
                    rx.spinner(size="2", class_name="mr-2 text-white"),
                    "Sending OTP...",
                    class_name="flex items-center justify-center",
                ),
                "Send OTP",
            ),
            disabled=AuthState.is_loading,
            on_click=AuthState.send_otp,
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
    )


def otp_step() -> rx.Component:
    """Step 2: OTP verification"""
    return rx.el.div(
        rx.el.h2(
            "Verify OTP",
            class_name="text-2xl font-bold text-gray-900 text-center mb-2",
        ),
        rx.el.p(
            f"Enter the 6-digit code sent to {AuthState.email}",
            class_name="text-gray-500 text-center mb-8",
        ),
        rx.cond(
            AuthState.success_message != "",
            rx.el.div(
                rx.icon("check", class_name="h-4 w-4 mr-2 text-green-600"),
                rx.el.p(AuthState.success_message, class_name="text-green-600"),
                class_name="flex items-center p-3 mb-4 text-sm bg-green-50 border border-green-100 rounded-lg",
            ),
        ),
        rx.el.div(
            rx.el.label(
                "OTP Code",
                class_name="block text-sm font-medium text-gray-700 mb-1.5",
            ),
            rx.el.div(
                rx.icon(
                    "shield-check",
                    class_name="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400",
                ),
                rx.el.input(
                    placeholder="000000",
                    type="text",
                    max_length=6,
                    value=AuthState.otp_code,
                    on_change=AuthState.set_otp_code,
                    class_name="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 outline-none transition-all bg-gray-50/50 focus:bg-white text-center text-2xl tracking-widest font-mono",
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
                    "Verifying...",
                    class_name="flex items-center justify-center",
                ),
                "Verify OTP",
            ),
            disabled=AuthState.is_loading,
            on_click=AuthState.verify_otp,
            class_name="w-full py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-semibold shadow-lg shadow-sky-500/30 hover:shadow-sky-500/50 hover:scale-[1.01] active:scale-[0.99] transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed",
        ),
        rx.el.div(
            rx.el.button(
                "Resend OTP",
                on_click=AuthState.resend_otp,
                class_name="text-sm font-medium text-sky-600 hover:text-sky-700 transition-colors",
            ),
            class_name="mt-4 text-center",
        ),
        rx.el.div(
            rx.el.p(
                "OTP expires in 5 minutes",
                class_name="text-xs text-gray-400 text-center",
            ),
            class_name="mt-2",
        ),
    )


def password_step() -> rx.Component:
    """Step 3: New password entry"""
    return rx.el.div(
        rx.el.h2(
            "Set New Password",
            class_name="text-2xl font-bold text-gray-900 text-center mb-2",
        ),
        rx.el.p(
            "Choose a strong password for your account",
            class_name="text-gray-500 text-center mb-8",
        ),
        rx.cond(
            AuthState.success_message != "",
            rx.el.div(
                rx.icon("check", class_name="h-4 w-4 mr-2 text-green-600"),
                rx.el.p(AuthState.success_message, class_name="text-green-600"),
                class_name="flex items-center p-3 mb-4 text-sm bg-green-50 border border-green-100 rounded-lg",
            ),
        ),
        rx.el.div(
            rx.el.label(
                "New Password",
                class_name="block text-sm font-medium text-gray-700 mb-1.5",
            ),
            rx.el.div(
                rx.icon(
                    "lock",
                    class_name="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400",
                ),
                rx.el.input(
                    placeholder="Enter new password",
                    type="password",
                    value=AuthState.new_password,
                    on_change=AuthState.set_new_password,
                    class_name="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-200 focus:border-sky-500 focus:ring-2 focus:ring-sky-500/20 outline-none transition-all bg-gray-50/50 focus:bg-white",
                ),
                class_name="relative",
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.label(
                "Confirm New Password",
                class_name="block text-sm font-medium text-gray-700 mb-1.5",
            ),
            rx.el.div(
                rx.icon(
                    "lock",
                    class_name="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400",
                ),
                rx.el.input(
                    placeholder="Confirm new password",
                    type="password",
                    value=AuthState.confirm_new_password,
                    on_change=AuthState.set_confirm_new_password,
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
                    "Resetting...",
                    class_name="flex items-center justify-center",
                ),
                "Reset Password",
            ),
            disabled=AuthState.is_loading,
            on_click=AuthState.reset_password,
            class_name="w-full py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 text-white font-semibold shadow-lg shadow-sky-500/30 hover:shadow-sky-500/50 hover:scale-[1.01] active:scale-[0.99] transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed",
        ),
    )


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
                    # Progress indicator
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.span("1", class_name="text-xs font-semibold"),
                                class_name=rx.cond(
                                    AuthState.otp_step == "email",
                                    "w-8 h-8 flex items-center justify-center rounded-full bg-sky-500 text-white border-2 border-sky-500",
                                    "w-8 h-8 flex items-center justify-center rounded-full bg-white text-gray-400 border-2 border-gray-200",
                                ),
                            ),
                            rx.el.span("Email", class_name="text-xs text-gray-600 mt-1"),
                            class_name="flex flex-col items-center",
                        ),
                        rx.el.div(
                            class_name=rx.cond(
                                AuthState.otp_step != "email",
                                "h-0.5 flex-1 bg-sky-500 self-center mx-2",
                                "h-0.5 flex-1 bg-gray-200 self-center mx-2",
                            ),
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.span("2", class_name="text-xs font-semibold"),
                                class_name=rx.cond(
                                    AuthState.otp_step == "otp",
                                    "w-8 h-8 flex items-center justify-center rounded-full bg-sky-500 text-white border-2 border-sky-500",
                                    "w-8 h-8 flex items-center justify-center rounded-full bg-white text-gray-400 border-2 border-gray-200",
                                ),
                            ),
                            rx.el.span("Verify", class_name="text-xs text-gray-600 mt-1"),
                            class_name="flex flex-col items-center",
                        ),
                        rx.el.div(
                            class_name=rx.cond(
                                AuthState.otp_step == "password",
                                "h-0.5 flex-1 bg-sky-500 self-center mx-2",
                                "h-0.5 flex-1 bg-gray-200 self-center mx-2",
                            ),
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.span("3", class_name="text-xs font-semibold"),
                                class_name=rx.cond(
                                    AuthState.otp_step == "password",
                                    "w-8 h-8 flex items-center justify-center rounded-full bg-sky-500 text-white border-2 border-sky-500",
                                    "w-8 h-8 flex items-center justify-center rounded-full bg-white text-gray-400 border-2 border-gray-200",
                                ),
                            ),
                            rx.el.span("Reset", class_name="text-xs text-gray-600 mt-1"),
                            class_name="flex flex-col items-center",
                        ),
                        class_name="flex items-start justify-between mb-8 px-4",
                    ),
                    # Dynamic content based on step
                    rx.match(
                        AuthState.otp_step,
                        ("email", email_step()),
                        ("otp", otp_step()),
                        ("password", password_step()),
                        email_step(),  # default
                    ),
                    class_name="p-8 bg-white/80 backdrop-blur-xl rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white/20",
                ),
                class_name="w-full max-w-md",
            ),
            class_name="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-sky-50 via-white to-indigo-50",
        ),
        class_name="font-['Roboto']",
        on_mount=AuthState.reset_password_state,
    )