import reflex as rx
from sqlmodel import Session
import logging


def get_db():
    """Provide a transactional scope around a series of operations."""
    with rx.session() as session:
        try:
            yield session
        except Exception as e:
            logging.exception(f"Database session error: {e}")
            session.rollback()
            raise
        finally:
            session.close()