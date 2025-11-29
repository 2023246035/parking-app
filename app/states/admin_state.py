"""Admin state for authentication and admin-only operations"""
import reflex as rx
import logging
from sqlmodel import select
from app.db.models import User as DBUser, Booking as DBBooking, ParkingLot as DBParkingLot
from datetime import datetime


class AdminState(rx.State):
    """Admin authentication and management state"""
    admin_email: str = rx.Cookie("", name="admin_email")
    is_admin_logged_in: bool = False
    admin_name: str = ""
    login_error: str = ""
    
    # Dashboard stats
    total_users: int = 0
    total_bookings: int = 0
    total_parking_lots: int = 0
    total_revenue: float = 0.0
    active_bookings: int = 0
    
    @rx.event
    async def admin_login(self, form_data: dict):
        """Admin login - checks for admin role"""
        email = form_data.get("email", "")
        password = form_data.get("password", "")
        
        if not email or not password:
            self.login_error = "Please enter both email and password"
            return
        
        try:
            with rx.session() as session:
                user = session.exec(
                    select(DBUser).where(DBUser.email == email)
                ).first()
                
                if not user:
                    self.login_error = "Invalid admin credentials"
                    return
                
                # Check if user is admin (you can add is_admin field to User model)
                # For now, we'll check if email contains "admin"
                if "admin" not in email.lower():
                    self.login_error = "Access denied. Admin privileges required."
                    return
                
                # Verify password (use proper password hashing in production)
                import bcrypt
                if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                    self.admin_email = email
                    self.admin_name = user.name
                    self.is_admin_logged_in = True
                    self.login_error = ""
                    
                    # Load dashboard stats
                    await self.load_dashboard_stats()
                    
                    yield rx.redirect("/admin/dashboard")
                else:
                    self.login_error = "Invalid admin credentials"
                    
        except Exception as e:
            logging.exception(f"Admin login error: {e}")
            self.login_error = "Login failed. Please try again."
    
    @rx.event
    def admin_logout(self):
        """Logout admin user"""
        self.admin_email = ""
        self.is_admin_logged_in = False
        self.admin_name = ""
        return rx.redirect("/admin/login")
    
    @rx.event
    async def load_dashboard_stats(self):
        """Load admin dashboard statistics"""
        try:
            with rx.session() as session:
                # Count users
                users = session.exec(select(DBUser)).all()
                self.total_users = len(users)
                
                # Count bookings and calculate revenue
                bookings = session.exec(select(DBBooking)).all()
                self.total_bookings = len(bookings)
                self.active_bookings = len([b for b in bookings if b.status == "Confirmed"])
                self.total_revenue = sum(
                    b.total_price for b in bookings 
                    if b.payment_status == "Paid"
                )
                
                # Count parking lots
                lots = session.exec(select(DBParkingLot)).all()
                self.total_parking_lots = len(lots)
                
        except Exception as e:
            logging.exception(f"Error loading dashboard stats: {e}")
    
    @rx.event
    async def check_admin_auth(self):
        """Check if admin is authenticated"""
        if not self.admin_email:
            return rx.redirect("/admin/login")
        
        try:
            with rx.session() as session:
                user = session.exec(
                    select(DBUser).where(DBUser.email == self.admin_email)
                ).first()
                
                if not user or "admin" not in self.admin_email.lower():
                    self.is_admin_logged_in = False
                    return rx.redirect("/admin/login")
                
                self.is_admin_logged_in = True
                self.admin_name = user.name
                await self.load_dashboard_stats()
                
        except Exception as e:
            logging.exception(f"Admin auth check error: {e}")
            return rx.redirect("/admin/login")
