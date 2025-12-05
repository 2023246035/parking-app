"""Admin Refund Management Page"""
import reflex as rx
from sqlmodel import select
from app.db.models import Booking as DBBooking, User as DBUser, Payment as DBPayment, AuditLog as DBAuditLog
from app.pages.admin_users import admin_navbar
from datetime import datetime
import uuid
import logging


class AdminRefundsState(rx.State):
    """State for managing refund approvals"""
    pending_refunds: list[dict] = []
    is_loading: bool = False
    
    # Rejection modal state
    is_rejection_modal_open: bool = False
    rejection_booking_id: int = 0
    rejection_reason: str = ""
    rejection_booking_display_id: str = ""
    rejection_user_email: str = ""
    rejection_user_name: str = ""
    
    @rx.event
    async def load_pending_refunds(self):
        """Load all bookings with pending refund status"""
        self.is_loading = True
        try:
            with rx.session() as session:
                # Get all bookings with refund_status = "Pending"
                stmt = select(DBBooking).where(DBBooking.refund_status == "Pending")
                db_bookings = session.exec(stmt).all()
                
                self.pending_refunds = []
                for booking in db_bookings:
                    user = booking.user
                    lot = booking.parking_lot
                    
                    self.pending_refunds.append({
                        "id": booking.id,
                        "booking_id": f"BK-{booking.id}",
                        "user_name": user.name if user else "Unknown",
                        "user_email": user.email if user else "Unknown",
                        "lot_name": lot.name if lot else "Unknown",
                        "lot_location": lot.location if lot else "Unknown",
                        "start_date": booking.start_date,
                        "start_time": booking.start_time,
                        "duration": f"{booking.duration_hours} Hours",
                        "total_price": f"RM {booking.total_price:.2f}",
                        "refund_amount": booking.refund_amount,
                        "refund_amount_display": f"RM {booking.refund_amount:.2f}",
                        "cancellation_reason": booking.cancellation_reason or "Not provided",
                        "cancelled_at": booking.cancellation_at.strftime("%Y-%m-%d %H:%M") if booking.cancellation_at else "N/A",
                    })
                
                logging.info(f"Loaded {len(self.pending_refunds)} pending refunds")
        except Exception as e:
            logging.exception(f"Error loading pending refunds: {e}")
            yield rx.toast.error("Failed to load pending refunds")
        finally:
            self.is_loading = False
    
    @rx.event
    async def approve_refund(self, booking_id: int, refund_amount: float):
        """Approve a refund request"""
        try:
            with rx.session() as session:
                booking = session.get(DBBooking, booking_id)
                if not booking:
                    yield rx.toast.error("Booking not found")
                    return
                
                if booking.refund_status != "Pending":
                    yield rx.toast.error("Refund already processed")
                    return
                
                # Update booking status
                booking.refund_status = "Approved"
                booking.refund_approved_at = datetime.now()
                booking.payment_status = "Refunded"
                session.add(booking)
                
                # Create refund payment record
                refund = DBPayment(
                    transaction_id=f"RFD_{str(uuid.uuid4())[:8].upper()}",
                    booking_id=booking.id,
                    amount=refund_amount,
                    status="Refunded",
                    timestamp=datetime.now(),
                    method="Admin Approved Refund",
                )
                session.add(refund)
                
                # Create audit log
                audit = DBAuditLog(
                    action="Refund Approved",
                    timestamp=datetime.now(),
                    details=f"Admin approved refund of RM {refund_amount:.2f} for booking {booking.id}",
                    user_id=booking.user_id,
                )
                session.add(audit)
                
                session.commit()
                
                logging.info(f"Refund approved for booking {booking.id}: RM {refund_amount:.2f}")
                yield AdminRefundsState.load_pending_refunds
                yield rx.toast.success(f"Refund of RM {refund_amount:.2f} approved successfully")
        except Exception as e:
            logging.exception(f"Error approving refund: {e}")
            yield rx.toast.error("Failed to approve refund")
    
    @rx.event
    def open_rejection_modal(self, refund: dict):
        """Open modal to get rejection reason"""
        self.rejection_booking_id = refund["id"]
        self.rejection_booking_display_id = refund["booking_id"]
        self.rejection_user_email = refund["user_email"]
        self.rejection_user_name = refund["user_name"]
        self.rejection_reason = ""
        self.is_rejection_modal_open = True
    
    @rx.event
    def close_rejection_modal(self):
        """Close rejection modal"""
        self.is_rejection_modal_open = False
        self.rejection_reason = ""
    
    @rx.event
    async def confirm_rejection(self):
        """Confirm and process refund rejection with email notification"""
        if not self.rejection_reason or self.rejection_reason.strip() == "":
            yield rx.toast.error("Please provide a reason for rejection")
            return
        
        try:
            with rx.session() as session:
                booking = session.get(DBBooking, self.rejection_booking_id)
                if not booking:
                    yield rx.toast.error("Booking not found")
                    return
                
                if booking.refund_status != "Pending":
                    yield rx.toast.error("Refund already processed")
                    return
                
                # Update booking status
                booking.refund_status = "Rejected"
                booking.payment_status = "Cancelled (Refund Rejected)"
                # Note: rejection_reason field needs to be added to DB schema
                # For now, we'llstore it in cancellation_reason or add a comment in audit log
                session.add(booking)
                
                # Create audit log with rejection reason
                audit = DBAuditLog(
                    action="Refund Rejected",
                    timestamp=datetime.now(),
                    details=f"Admin rejected refund for booking {booking.id}. Reason: {self.rejection_reason}",
                    user_id=booking.user_id,
                )
                session.add(audit)
                
                session.commit()
                
                logging.info(f"Refund rejected for booking {booking.id}: {self.rejection_reason}")
            
            # Send email notification to user
            from app.services.email_service import send_refund_rejection_email
            email_sent = send_refund_rejection_email(
                email=self.rejection_user_email,
                booking_id=self.rejection_booking_display_id,
                reason=self.rejection_reason,
                user_name=self.rejection_user_name
            )
            
            if email_sent:
                yield rx.toast.success(f"Refund rejected and user notified via email")
            else:
                yield rx.toast.warning("Refund rejected but email notification failed")
            
            # Close modal and reload
            self.is_rejection_modal_open = False
            self.rejection_reason = ""
            yield AdminRefundsState.load_pending_refunds
            
        except Exception as e:
            logging.exception(f"Error rejecting refund: {e}")
            yield rx.toast.error("Failed to reject refund")


def refund_card(refund: dict) -> rx.Component:
    """Refund request card"""
    return rx.el.div(
        # Header
        rx.el.div(
            rx.el.div(
                rx.el.h3(refund["booking_id"], class_name="text-lg font-bold text-gray-900"),
                rx.el.p(refund["lot_name"], class_name="text-sm text-gray-600"),
            ),
            rx.el.span(
                "Pending Approval",
                class_name="px-3 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800"
            ),
            class_name="flex justify-between items-start mb-4 pb-4 border-b border-gray-200"
        ),
        
        # Details Grid
        rx.el.div(
            rx.el.div(
                rx.el.p("User", class_name="text-xs text-gray-500 mb-1"),
                rx.el.p(refund["user_name"], class_name="text-sm font-medium text-gray-900"),
                rx.el.p(refund["user_email"], class_name="text-xs text-gray-600"),
            ),
            rx.el.div(
                rx.el.p("Booking Date", class_name="text-xs text-gray-500 mb-1"),
                rx.el.p(refund["start_date"], class_name="text-sm font-medium text-gray-900"),
                rx.el.p(refund["start_time"], class_name="text-xs text-gray-600"),
            ),
            rx.el.div(
                rx.el.p("Cancelled", class_name="text-xs text-gray-500 mb-1"),
                rx.el.p(refund["cancelled_at"], class_name="text-sm font-medium text-gray-900"),
            ),
            rx.el.div(
                rx.el.p("Refund Amount", class_name="text-xs text-gray-500 mb-1"),
                rx.el.p(refund["refund_amount_display"], class_name="text-lg font-bold text-green-600"),
            ),
            class_name="grid grid-cols-4 gap-4 mb-4"
        ),
        
        # Action Buttons
        rx.el.div(
            rx.el.button(
                rx.icon("check", class_name="h-4 w-4 mr-2"),
                "Approve & Process Refund",
                on_click=AdminRefundsState.approve_refund(refund["id"], refund["refund_amount"]),
                class_name="flex items-center px-4 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
            ),
            rx.el.button(
                rx.icon("x", class_name="h-4 w-4 mr-2"),
                "Reject",
                on_click=AdminRefundsState.open_rejection_modal(refund),
                class_name="flex items-center px-4 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition-colors"
            ),
            class_name="flex gap-3"
        ),
        
        class_name="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow"
    )


def rejection_modal() -> rx.Component:
    """Modal to collect rejection reason"""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "Reject Refund Request",
                class_name="text-xl font-bold text-gray-900 mb-4"
            ),
            rx.dialog.description(
                f"You are rejecting refund for booking: {AdminRefundsState.rejection_booking_display_id}",
                class_name="text-sm text-gray-600 mb-4"
            ),
            
            # Rejection reason input
            rx.el.div(
                rx.el.label(
                    "Reason for Rejection *",
                    class_name="block text-sm font-medium text-gray-700 mb-2"
                ),
                rx.text_area(
                    placeholder="Please provide a detailed reason for rejecting this refund request. This will be sent to the user via email.",
                    value=AdminRefundsState.rejection_reason,
                    on_change=AdminRefundsState.set_rejection_reason,
                    rows="4",
                    class_name="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                ),
                class_name="mb-6"
            ),
            
            # Action buttons
            rx.el.div(
                rx.dialog.close(
                    rx.el.button(
                        "Cancel",
                        on_click=AdminRefundsState.close_rejection_modal,
                        class_name="px-4 py-2 bg-gray-200 text-gray-700 font-medium rounded-lg hover:bg-gray-300 transition-colors"
                    ),
                ),
                rx.el.button(
                    rx.icon("x-circle", class_name="h-4 w-4 mr-2"),
                    "Confirm Rejection",
                    on_click=AdminRefundsState.confirm_rejection,
                    class_name="flex items-center px-4 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition-colors"
                ),
                class_name="flex justify-end gap-3"
            ),
            
            class_name="max-w-2xl"
        ),
        open=AdminRefundsState.is_rejection_modal_open,
        on_open_change=AdminRefundsState.set_is_rejection_modal_open,
    )


def admin_refunds_page() -> rx.Component:
    return rx.el.div(
        admin_navbar(),
        
        rx.el.div(
            # Header
            rx.el.div(
                rx.el.h1(
                    "Refund Management",
                    class_name="text-3xl font-bold text-gray-900 mb-2"
                ),
                rx.el.p(
                    "Review and approve pending refund requests from users",
                    class_name="text-gray-600"
                ),
                class_name="mb-8"
            ),
            
            # Stats
            rx.el.div(
                rx.el.div(
                    rx.el.p("Pending Refunds", class_name="text-sm text-gray-600 mb-1"),
                    rx.el.p(
                        rx.cond(
                            AdminRefundsState.pending_refunds.length() > 0,
                            AdminRefundsState.pending_refunds.length().to_string(),
                            "0"
                        ),
                        class_name="text-3xl font-bold text-yellow-600"
                    ),
                ),
                class_name="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-8"
            ),
            
            # Refund List
            rx.cond(
                AdminRefundsState.is_loading,
                rx.el.div(
                    rx.spinner(size="3"),
                    rx.el.p("Loading refund requests...", class_name="mt-4 text-gray-600"),
                    class_name="flex flex-col items-center justify-center py-12"
                ),
                rx.cond(
                    AdminRefundsState.pending_refunds.length() > 0,
                    rx.el.div(
                        rx.foreach(AdminRefundsState.pending_refunds, refund_card),
                        class_name="grid grid-cols-1 gap-6"
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.icon("check-circle", class_name="h-16 w-16 text-gray-400 mb-4"),
                            rx.el.h3("No Pending Refunds", class_name="text-xl font-bold text-gray-900 mb-2"),
                            rx.el.p("All refund requests have been processed", class_name="text-gray-600"),
                            class_name="flex flex-col items-center justify-center py-16"
                        ),
                        class_name="bg-white rounded-lg border border-gray-200"
                    )
                )
            ),
            
            class_name="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
        ),
        
        # Rejection Modal
        rejection_modal(),
        
        class_name="min-h-screen bg-gray-50",
        on_mount=AdminRefundsState.load_pending_refunds,
    )
