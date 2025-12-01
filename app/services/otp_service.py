"""OTP Service for generating and managing OTP codes."""
import random
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlmodel import select
import reflex as rx
from app.db.models import OTPVerification, User


def generate_otp() -> str:
    """Generate a 6-digit OTP code."""
    return str(random.randint(100000, 999999))


def create_otp_record(email: str, purpose: str = "password_reset") -> Optional[str]:
    """
    Create an OTP record for the given email.
    Returns the generated OTP code or None if user doesn't exist (for password reset).
    """
    try:
        with rx.session() as session:
            # For password reset, verify user exists
            if purpose == "password_reset":
                user = session.exec(select(User).where(User.email == email)).first()
                if not user:
                    logging.warning(f"OTP request for non-existent email: {email}")
                    return None

            # Clean up old OTPs for this email
            old_otps = session.exec(
                select(OTPVerification).where(
                    OTPVerification.email == email,
                    OTPVerification.purpose == purpose,
                )
            ).all()
            for old_otp in old_otps:
                session.delete(old_otp)

            # Generate new OTP
            otp_code = generate_otp()
            expires_at = datetime.utcnow() + timedelta(minutes=2)  # 2 minutes expiration

            new_otp = OTPVerification(
                email=email,
                otp_code=otp_code,
                purpose=purpose,
                expires_at=expires_at,
            )

            session.add(new_otp)
            session.commit()

            logging.info(f"OTP generated for {email}: {otp_code} (expires at {expires_at})")
            return otp_code

    except Exception as e:
        logging.exception(f"Error creating OTP record: {e}")
        return None


def verify_otp_code(email: str, code: str, purpose: str = "password_reset") -> tuple[bool, str]:
    """
    Verify the OTP code for the given email.
    Returns (success: bool, message: str)
    """
    try:
        with rx.session() as session:
            otp_record = session.exec(
                select(OTPVerification).where(
                    OTPVerification.email == email,
                    OTPVerification.purpose == purpose,
                    OTPVerification.is_used == False,
                )
            ).first()

            if not otp_record:
                return False, "No valid OTP found. Please request a new one."

            # Check if OTP is expired
            if datetime.utcnow() > otp_record.expires_at:
                return False, "OTP has expired. Please request a new one."

            # Check attempt count
            if otp_record.attempts >= 3:
                return False, "Maximum verification attempts exceeded. Please request a new OTP."

            # Increment attempts
            otp_record.attempts += 1

            # Verify code
            if otp_record.otp_code != code:
                session.commit()
                remaining = 3 - otp_record.attempts
                return False, f"Invalid OTP. {remaining} attempt(s) remaining."

            # Mark as used
            otp_record.is_used = True
            session.commit()

            logging.info(f"OTP verified successfully for {email}")
            return True, "OTP verified successfully"

    except Exception as e:
        logging.exception(f"Error verifying OTP: {e}")
        return False, "An error occurred during verification."


def cleanup_expired_otps():
    """Remove expired OTP records from the database."""
    try:
        with rx.session() as session:
            expired_otps = session.exec(
                select(OTPVerification).where(
                    OTPVerification.expires_at < datetime.utcnow()
                )
            ).all()

            for otp in expired_otps:
                session.delete(otp)

            session.commit()
            logging.info(f"Cleaned up {len(expired_otps)} expired OTP records")

    except Exception as e:
        logging.exception(f"Error cleaning up expired OTPs: {e}")
