"""Admin login page"""
import reflex as rx
from app.states.admin_state import AdminState


def admin_login_page() -> rx.Component:
    """Clean admin login page"""
    return rx.el.div(
        # Background gradient
        rx.el.div(
            class_name="absolute inset-0 bg-gradient-to-br from-gray-900 via-gray-800 to-black"
        ),
        
        # Login card
        rx.el.div(
            rx.el.div(
                # Logo/Icon
                rx.el.div(
                    "🔐",
                    class_name="text-6xl mb-4"
                ),
                
                # Title
                rx.el.h1(
                    "Admin Portal",
                    class_name="text-3xl font-bold text-gray-900 mb-2"
                ),
                rx.el.p(
                    "Sign in to access the admin dashboard",
                    class_name="text-gray-600 mb-8"
                ),
                
                # Error message
                rx.cond(
                    AdminState.login_error != "",
                    rx.el.div(
                        AdminState.login_error,
                        class_name="bg-red-50 text-red-600 px-4 py-3 rounded-lg mb-4 text-sm"
                    ),
                ),
                
                # Login form
                rx.form(
                    rx.el.div(
                        # Email
                        rx.el.div(
                            rx.el.label(
                                "Admin Email",
                                class_name="block text-sm font-semibold text-gray-700 mb-2"
                            ),
                            rx.el.input(
                                type="email",
                                name="email",
                                placeholder="admin@parkmycar.com",
                                required=True,
                                class_name="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-gray-900 focus:border-transparent outline-none"
                            ),
                            class_name="mb-4"
                        ),
                        
                        # Password
                        rx.el.div(
                            rx.el.label(
                                "Password",
                                class_name="block text-sm font-semibold text-gray-700 mb-2"
                            ),
                            rx.el.input(
                                type="password",
                                name="password",
                                placeholder="Enter your password",
                                required=True,
                                class_name="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-gray-900 focus:border-transparent outline-none"
                            ),
                            class_name="mb-6"
                        ),
                        
                        # Submit button
                        rx.el.button(
                            "Sign In",
                            type="submit",
                            class_name="w-full px-6 py-3 bg-gray-900 text-white font-semibold rounded-lg hover:bg-gray-800 transition-colors"
                        ),
                    ),
                    on_submit=AdminState.admin_login,
                ),
                
                # Back to main site
                rx.el.div(
                    rx.el.a(
                        "← Back to main site",
                        href="/",
                        class_name="text-sm text-gray-600 hover:text-gray-900"
                    ),
                    class_name="mt-6 text-center"
                ),
                
                class_name="bg-white rounded-2xl p-8 shadow-2xl w-full max-w-md"
            ),
            class_name="relative z-10 flex items-center justify-center min-h-screen px-4"
        ),
        
        class_name="relative min-h-screen font-['Roboto']"
    )
