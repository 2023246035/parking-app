import reflex as rx
import asyncio
import logging
from sqlmodel import select
from app.states.user_state import UserState
from app.db.models import User as DBUser


class AuthState(rx.State):
    is_authenticated: bool = False
    session_email: str = rx.Cookie("", name="session_email")
    email: str = ""
    password: str = ""
    confirm_password: str = ""
    full_name: str = ""
    phone: str = ""
    is_loading: bool = False
    error_message: str = ""
    success_message: str = ""

    @rx.event
    def set_email(self, value: str):
        self.email = value
        self.error_message = ""

    @rx.event
    def set_password(self, value: str):
        self.password = value
        self.error_message = ""

    @rx.event
    def set_confirm_password(self, value: str):
        self.confirm_password = value
        self.error_message = ""

    @rx.event
    def set_full_name(self, value: str):
        self.full_name = value

    @rx.event
    def set_phone(self, value: str):
        self.phone = value

    @rx.event
    async def login(self):
        self.is_loading = True
        self.error_message = ""
        await asyncio.sleep(1.0)
        if not self.email or not self.password:
            self.error_message = "Please enter both email and password."
            self.is_loading = False
            return
        try:
            with rx.session() as session:
                user = session.exec(
                    select(DBUser).where(DBUser.email == self.email)
                ).first()
                if user and user.password_hash == self.password:
                    self.is_authenticated = True
                    self.session_email = self.email
                    self.is_loading = False
                    from app.states.booking_state import BookingState

                    yield UserState.load_profile
                    yield BookingState.load_bookings
                    yield rx.redirect("/")
                    return
                else:
                    self.error_message = "Invalid email or password."
                    self.is_loading = False
        except Exception as e:
            logging.exception(f"Login error: {e}")
            self.error_message = "An error occurred during login."
            self.is_loading = False

    @rx.event
    async def register(self):
        self.is_loading = True
        self.error_message = ""
        await asyncio.sleep(1.0)
        if not self.email or not self.password or (not self.full_name):
            self.error_message = "Please fill in all required fields."
            self.is_loading = False
            return
        if self.password != self.confirm_password:
            self.error_message = "Passwords do not match."
            self.is_loading = False
            return
        try:
            with rx.session() as session:
                existing_user = session.exec(
                    select(DBUser).where(DBUser.email == self.email)
                ).first()
                if existing_user:
                    self.error_message = "Email already registered."
                    self.is_loading = False
                    return
                new_user = DBUser(
                    name=self.full_name,
                    email=self.email,
                    password_hash=self.password,
                    phone=self.phone or "",
                    avatar_url=f"https://api.dicebear.com/9.x/notionists/svg?seed={self.email}",
                )
                session.add(new_user)
                session.commit()
                self.is_authenticated = True
                self.session_email = self.email
                self.is_loading = False
                from app.states.booking_state import BookingState

                yield UserState.load_profile
                yield BookingState.load_bookings
                yield rx.redirect("/")
                return
        except Exception as e:
            logging.exception(f"Registration error: {e}")
            self.error_message = "An error occurred during registration."
            self.is_loading = False

    @rx.event
    def logout(self):
        self.is_authenticated = False
        self.session_email = ""
        self.email = ""
        self.password = ""
        return rx.redirect("/")

    @rx.event
    async def check_login(self):
        from app.states.booking_state import BookingState

        logging.info(
            f"Checking login. Auth: {self.is_authenticated}, SessionCookie: {self.session_email}"
        )
        if self.is_authenticated:
            if not self.email and self.session_email:
                self.email = self.session_email
            yield UserState.load_profile
            yield BookingState.load_bookings
            return
        if self.session_email:
            try:
                with rx.session() as session:
                    user = session.exec(
                        select(DBUser).where(DBUser.email == self.session_email)
                    ).first()
                    if user:
                        logging.info(f"Restoring session for {self.session_email}")
                        self.is_authenticated = True
                        self.email = self.session_email
                        yield UserState.load_profile
                        yield BookingState.load_bookings
                        return
                    else:
                        logging.warning(
                            f"Session email {self.session_email} not found in DB"
                        )
            except Exception as e:
                logging.exception(f"Error checking login: {e}")
        logging.warning("Check login failed or no session. Redirecting to login.")
        yield rx.redirect("/login")
        return

    @rx.event
    async def request_password_reset(self):
        self.is_loading = True
        self.error_message = ""
        self.success_message = ""
        await asyncio.sleep(1.0)
        if not self.email:
            self.error_message = "Please enter your email address."
            self.is_loading = False
            return
        self.success_message = "If an account exists for this email, you will receive a reset link shortly."
        self.is_loading = False