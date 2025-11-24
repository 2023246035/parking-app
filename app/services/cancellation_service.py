"""Cancellation service with BRD-aligned logic"""
import reflex as rx
import logging
from datetime import datetime
from sqlmodel import select
from app.db.models import CancellationPolicy, Booking as DBBooking


def get_active_cancellation_policy():
    """Get the active cancellation policy from database"""
    try:
        with rx.session() as session:
            policy = session.exec(
                select(CancellationPolicy).where(CancellationPolicy.is_active == True)
            ).first()
            
            if not policy:
                # Fallback to default if none exists
                logging.warning("No active cancellation policy found, using defaults")
                return CancellationPolicy(
                    full_refund_hours=24,
                    partial_refund_hours=0,
                    partial_refund_percentage=50,
                    non_cancellable_hours=0,
                    allow_cancellation_after_start=False
                )
            return policy
    except Exception as e:
        logging.exception(f"Error fetching cancellation policy: {e}")
        # Return default policy on error
        return CancellationPolicy(
            full_refund_hours=24,
            partial_refund_hours=0,
            partial_refund_percentage=50,
            non_cancellable_hours=0,
            allow_cancellation_after_start=False
        )


def validate_cancellation_eligibility(booking: DBBooking) -> dict:
    """
    Validate if booking can be cancelled based on BRD rules
    
    Returns:
        dict with keys:
            - can_cancel: bool
            - refund_amount: float
            - refund_percentage: int
            - message: str
            - reason: str
    """
    policy = get_active_cancellation_policy()
    
    try:
        booking_start = datetime.strptime(
            f"{booking.start_date} {booking.start_time}", 
            "%Y-%m-%d %H:%M"
        )
    except:
        # Fallback for different time formats
        booking_start = datetime.strptime(
            f"{booking.start_date} {booking.start_time}", 
            "%Y-%m-%d %H:%M"
        )
    
    now = datetime.now()
    hours_until_start = (booking_start - now).total_seconds() / 3600
    
    # Check 1: Already started?
    if hours_until_start <= 0 and not policy.allow_cancellation_after_start:
        return {
            "can_cancel": False,
            "refund_amount": 0.0,
            "refund_percentage": 0,
            "message": "Cannot cancel - booking has already started",
            "reason": "BOOKING_STARTED"
        }
    
    # Check 2: Non-cancellable block window
    if hours_until_start < policy.non_cancellable_hours:
        return {
            "can_cancel": False,
            "refund_amount": 0.0,
            "refund_percentage": 0,
            "message": f"Cannot cancel within {policy.non_cancellable_hours} hours of booking start",
            "reason": "WITHIN_BLOCK_WINDOW"
        }
    
    # Check 3: Non-refundable booking
    if not booking.is_refundable:
        return {
            "can_cancel": True,
            "refund_amount": 0.0,
            "refund_percentage": 0,
            "message": "This booking is non-refundable",
            "reason": "NON_REFUNDABLE"
        }
    
    # Check 4: Calculate refund based on policy
    if hours_until_start >= policy.full_refund_hours:
        return {
            "can_cancel": True,
            "refund_amount": booking.total_price,
            "refund_percentage": 100,
            "message": f"Full refund available (more than {policy.full_refund_hours}h before booking)",
            "reason": "FULL_REFUND"
        }
    elif hours_until_start >= policy.partial_refund_hours:
        refund = booking.total_price * (policy.partial_refund_percentage / 100)
        return {
            "can_cancel": True,
            "refund_amount": refund,
            "refund_percentage": policy.partial_refund_percentage,
            "message": f"{policy.partial_refund_percentage}% refund available",
            "reason": "PARTIAL_REFUND"
        }
    else:
        return {
            "can_cancel": True,
            "refund_amount": 0.0,
            "refund_percentage": 0,
            "message": "No refund available",
            "reason": "NO_REFUND"
        }


def send_cancellation_email_to_user(user_email: str, user_name: str, booking_details: dict, refund_amount: float):
    """
    Send cancellation confirmation email to user
    (Simulated for now - logs instead of sending actual email)
    """
    email_body = f"""
    ===== CANCELLATION CONFIRMATION EMAIL =====
    To: {user_email}
    Subject: Booking Cancelled - {booking_details['booking_id']}
    
    Dear {user_name},
    
    Your parking booking has been successfully cancelled.
    
    Booking Details:
    - Booking ID: {booking_details['booking_id']}
    - Parking Lot: {booking_details['lot_name']}
    - Location: {booking_details['lot_location']}
    - Date: {booking_details['start_date']} at {booking_details['start_time']}
    - Duration: {booking_details['duration_hours']} hours
    - Original Amount: RM {booking_details['total_price']:.2f}
    - Refund Amount: RM {refund_amount:.2f}
    
    {f"The refund of RM {refund_amount:.2f} will be processed to your original payment method within 5-7 business days." if refund_amount > 0 else "No refund applicable for this cancellation."}
    
    Thank you for using ParkMyCar.
    
    Best regards,
    ParkMyCar Team
    ==========================================
    """
    logging.info(email_body)
    print(email_body)


def send_cancellation_email_to_admin(booking_details: dict, user_details: dict, refund_amount: float):
    """
    Send cancellation notification to admin
    (Simulated for now - logs instead of sending actual email)
    """
    email_body = f"""
    ===== ADMIN CANCELLATION ALERT =====
    To: admin@parkmycar.com
    Subject: Booking Cancellation Alert - {booking_details['booking_id']}
    
    A booking has been cancelled:
    
    User Information:
    - Name: {user_details['name']}
    - Email: {user_details['email']}
    - Phone: {user_details['phone']}
    
    Booking Details:
    - Booking ID: {booking_details['booking_id']}
    - Parking Lot: {booking_details['lot_name']} ({booking_details['lot_location']})
    - Date: {booking_details['start_date']} at {booking_details['start_time']}
    - Duration: {booking_details['duration_hours']} hours
    - Original Amount: RM {booking_details['total_price']:.2f}
    - Refund Amount: RM {refund_amount:.2f}
    - Cancellation Reason: {booking_details.get('cancellation_reason', 'Not specified')}
    - Cancelled At: {booking_details.get('cancelled_at', 'Now')}
    
    Action Required: Review and process refund if necessary.
    =====================================
    """
    logging.info(email_body)
    print(email_body)


def simulate_refund_api(transaction_id: str, amount: float, reason: str) -> dict:
    """
    Simulate RinggitPay refund API call
    (Replace with actual API call when integrating)
    
    Returns:
        dict with keys:
            - success: bool
            - refund_id: str
            - status: str
            - message: str
    """
    import uuid
    
    logging.info(f"[SIMULATED] Processing refund via RinggitPay:")
    logging.info(f"  Original Transaction: {transaction_id}")
    logging.info(f"  Refund Amount: RM {amount:.2f}")
    logging.info(f"  Reason: {reason}")
    
    # Simulate 98% success rate
    import random
    if random.random() > 0.02:
        refund_id = f"RFD_{str(uuid.uuid4())[:8].upper()}"
        logging.info(f"  ✅ Refund Successful - ID: {refund_id}")
        return {
            "success": True,
            "refund_id": refund_id,
            "status": "Completed",
            "message": "Refund processed successfully"
        }
    else:
        logging.error("  ❌ Refund Failed - Payment gateway error")
        return {
            "success": False,
            "refund_id": None,
            "status": "Failed",
            "message": "Payment gateway error - please try again"
        }
