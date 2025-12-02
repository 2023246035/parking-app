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
    async def reject_refund(self, booking_id: int):
        """Reject a refund request"""
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
                booking.refund_status = "Rejected"
                booking.payment_status = "Cancelled (Refund Rejected)"
                session.add(booking)
                
                # Create audit log
                audit = DBAuditLog(
                    action="Refund Rejected",
                    timestamp=datetime.now(),
                    details=f"Admin rejected refund for booking {booking.id}",
                    user_id=booking.user_id,
                )
                session.add(audit)
                
                session.commit()
                
                logging.info(f"Refund rejected for booking {booking.id}")
                yield AdminRefundsState.load_pending_refunds
                yield rx.toast.info("Refund request rejected")
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
                on_click=lambda: AdminRefundsState.approve_refund(refund["id"], refund["refund_amount"]),
                class_name="flex items-center px-4 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
            ),
            rx.el.button(
                rx.icon("x", class_name="h-4 w-4 mr-2"),
                "Reject",
                on_click=lambda: AdminRefundsState.reject_refund(refund["id"]),
                class_name="flex items-center px-4 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition-colors"
            ),
            class_name="flex gap-3"
        ),
        
        class_name="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow"
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
        
        class_name="min-h-screen bg-gray-50",
        on_mount=AdminRefundsState.load_pending_refunds,
    )
