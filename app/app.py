import reflex as rx
import logging
from app.pages.home import home_page
from app.pages.listings import listings_page
from app.pages.bookings import bookings_page
from app.pages.profile import profile_page
from app.pages.auth.login import login_page
from app.pages.auth.register import register_page
from app.pages.auth.forgot_password import forgot_password_page
from app.db.init_db import init_db
from app.states.booking_state import BookingState
from app.states.user_state import UserState
from app.states.auth_state import AuthState


class AppState(rx.State):
    @rx.event
    def on_load(self):
        """Run tasks when the app starts."""
        try:
            init_db()
        except Exception as e:
            logging.exception(f"Error initializing DB: {e}")


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700;900&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(home_page, route="/", on_load=AppState.on_load)
app.add_page(listings_page, route="/listings")
app.add_page(bookings_page, route="/bookings", on_load=AuthState.check_login)
app.add_page(profile_page, route="/profile", on_load=AuthState.check_login)
app.add_page(login_page, route="/login")
app.add_page(register_page, route="/register")
app.add_page(forgot_password_page, route="/forgot-password")