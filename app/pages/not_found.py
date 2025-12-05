"""Custom 404 Not Found Page"""
import reflex as rx
from app.components.navbar import navbar
from app.components.footer import footer


def not_found_page() -> rx.Component:
    """Professional 404 page with navigation"""
    return rx.box(
        navbar(),
        
        # Main content
        rx.el.div(
            rx.el.div(
                # 404 Icon
                rx.el.div(
                    "404",
                    class_name="text-9xl font-black text-indigo-600 mb-4"
                ),
                
                # Title
                rx.el.h1(
                    "Page Not Found",
                    class_name="text-4xl font-bold text-gray-900 mb-4"
                ),
                
                # Description
                rx.el.p(
                    "Oops! The page you're looking for doesn't exist.",
                    class_name="text-xl text-gray-600 mb-2"
                ),
                rx.el.p(
                    "It might have been moved or deleted.",
                    class_name="text-lg text-gray-500 mb-8"
                ),
                
                # Action buttons
                rx.el.div(
                    rx.link(
                        rx.el.button(
                            rx.icon("home", class_name="w-5 h-5 mr-2"),
                            "Go Home",
                            class_name="flex items-center px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-semibold shadow-md hover:shadow-lg transition-all text-lg"
                        ),
                        href="/"
                    ),
                    rx.link(
                        rx.el.button(
                            rx.icon("map-pin", class_name="w-5 h-5 mr-2"),
                            "Browse Parking",
                            class_name="flex items-center px-6 py-3 bg-white text-indigo-600 border-2 border-indigo-600 rounded-lg hover:bg-indigo-50 font-semibold transition-all text-lg"
                        ),
                        href="/listings"
                    ),
                    class_name="flex gap-4 justify-center"
                ),
                
                # Helpful links
                rx.el.div(
                    rx.el.p(
                        "Looking for:",
                        class_name="text-sm text-gray-500 mb-2"
                    ),
                    rx.el.div(
                        rx.link("Home", href="/", class_name="text-indigo-600 hover:underline mx-2"),
                        "•",
                        rx.link("Parking Listings", href="/listings", class_name="text-indigo-600 hover:underline mx-2"),
                        "•",
                        rx.link("My Bookings", href="/bookings", class_name="text-indigo-600 hover:underline mx-2"),
                        "•",
                        rx.link("How It Works", href="/how-it-works", class_name="text-indigo-600 hover:underline mx-2"),
                        class_name="text-sm text-gray-600"
                    ),
                    class_name="mt-8"
                ),
                
                class_name="text-center"
            ),
            class_name="min-h-screen flex items-center justify-center px-4 py-16 bg-gradient-to-b from-gray-50 to-white"
        ),
        
        footer(),
        
        class_name="font-['Roboto'] min-h-screen flex flex-col"
    )
