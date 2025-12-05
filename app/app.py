import reflex as rx
import logging
from app.pages.home import home_page
from app.pages.listings import listings_page
from app.pages.bookings import bookings_page
from app.pages.profile import profile_page
from app.pages.auth.login import login_page
from app.pages.auth.register import register_page
from app.pages.auth.forgot_password import forgot_password_page
from app.pages.how_it_works import how_it_works_page
from app.pages.admin_login import admin_login_page
from app.pages.admin_dashboard import admin_dashboard
from app.pages.admin_users import admin_users_page
from app.pages.admin_bookings import admin_bookings_page
from app.pages.admin_parking_lots import admin_parking_lots_page
from app.pages.admin_refunds import admin_refunds_page
from app.pages.admin_analytics import admin_analytics_page
from app.pages.chatbot_page import chatbot_page
from app.pages.smart_dashboard import smart_dashboard_page
from app.pages.not_found import not_found_page
from app.db.init_db import init_db
from app.states.booking_state import BookingState
from app.states.user_state import UserState
from app.states.auth_state import AuthState
from app.states.admin_state import AdminState
from app.api.routes import router as api_router



class AppState(rx.State):
    @rx.event
    def on_load(self):
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
app.add_page(listings_page, route="/listings")  # Public page - no login required
app.add_page(bookings_page, route="/bookings", on_load=AuthState.check_login)  # Requires login
app.add_page(profile_page, route="/profile", on_load=AuthState.check_login)  # Requires login
app.add_page(login_page, route="/login")
app.add_page(register_page, route="/register")
app.add_page(forgot_password_page, route="/forgot-password")
app.add_page(how_it_works_page, route="/how-it-works")
app.add_page(admin_login_page, route="/admin/login")
app.add_page(admin_dashboard, route="/admin/dashboard")
app.add_page(admin_users_page, route="/admin/users")
app.add_page(admin_bookings_page, route="/admin/bookings")
app.add_page(admin_parking_lots_page, route="/admin/parking-lots")
app.add_page(admin_refunds_page, route="/admin/refunds")
app.add_page(admin_analytics_page, route="/admin/analytics")
app.add_page(chatbot_page, route="/chatbot", title="AI Assistant")
app.add_page(smart_dashboard_page, route="/smart-dashboard", title="Auto-Booking")

# Try to include API routes after compilation
def setup_api_routes():
    """Setup API routes on the FastAPI backend"""
    try:
        import reflex.app as rx_app
        # Try different ways to access the FastAPI app
        backend = getattr(rx_app, 'app', None)
        if backend:
            backend.include_router(api_router)
            logging.info("✅ API router included successfully!")
        else:
            logging.warning("⚠️ Could not access FastAPI backend to include API router")
    except Exception as e:
        logging.warning(f"⚠️ Could not include API router: {e}")

# Call setup after app creation
setup_api_routes()

