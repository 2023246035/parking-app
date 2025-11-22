import reflex as rx
from sqlmodel import select
import logging
from app.states.schema import User
from app.db.models import User as DBUser


class UserState(rx.State):
    user: User = User(
        name="Guest",
        email="",
        phone="",
        member_since="",
        avatar_url="https://api.dicebear.com/9.x/notionists/svg?seed=Guest",
    )

    @rx.event
    async def load_profile(self):
        """Fetch user profile from DB based on email in AuthState."""
        from app.states.auth_state import AuthState

        auth_state = await self.get_state(AuthState)
        target_email = auth_state.email or auth_state.session_email
        logging.info(
            f"Loading profile. Auth: {auth_state.is_authenticated}, Email: {target_email}"
        )
        if not target_email:
            logging.warning("Cannot load profile: missing email")
            return
        try:
            with rx.session() as session:
                db_user = session.exec(
                    select(DBUser).where(DBUser.email == target_email)
                ).first()
                if db_user:
                    logging.info(f"Profile loaded for {db_user.email}")
                    self.user = User(
                        name=db_user.name,
                        email=db_user.email,
                        phone=db_user.phone,
                        member_since=db_user.member_since.strftime("%b %Y"),
                        avatar_url=db_user.avatar_url,
                    )
                else:
                    logging.warning(
                        f"User {auth_state.email} authenticated but not found in DB."
                    )
        except Exception as e:
            logging.exception(f"Error loading profile: {e}")
            yield rx.toast.error("Failed to load profile.")

    @rx.event
    def update_name(self, value: str):
        self.user.name = value

    @rx.event
    def update_email(self, value: str):
        self.user.email = value

    @rx.event
    def update_phone(self, value: str):
        self.user.phone = value

    @rx.event
    async def save_profile(self):
        """Persist profile changes to database."""
        try:
            with rx.session() as session:
                from app.states.auth_state import AuthState

                auth_state = await self.get_state(AuthState)
                db_user = session.exec(
                    select(DBUser).where(DBUser.email == auth_state.email)
                ).first()
                if db_user:
                    db_user.name = self.user.name
                    db_user.phone = self.user.phone
                    session.add(db_user)
                    session.commit()
                    yield rx.toast.success("Profile saved successfully!")
                else:
                    yield rx.toast.error("User record not found.")
        except Exception as e:
            logging.exception(f"Error saving profile: {e}")
            yield rx.toast.error("Failed to save profile.")