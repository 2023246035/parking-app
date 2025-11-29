"""
Script to create an admin user account
Run this once to create your first admin account
"""
import bcrypt
from sqlmodel import Session, select, create_engine
from app.db.models import User
from datetime import datetime

def create_admin_user():
    """Create an admin user account"""
    print("🔧 Creating Admin User...")
    
    # Admin details
    admin_email = "admin@parkmycar.com"
    admin_password = "admin123"  # Change this to a secure password!
    admin_name = "System Administrator"
    admin_phone = "+60123456789"
    
    # Hash the password
    password_hash = bcrypt.hashpw(
        admin_password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    # Database connection
    DATABASE_URL = "sqlite:///reflex.db"
    engine = create_engine(DATABASE_URL)
    
    try:
        with Session(engine) as session:
            # Check if admin already exists
            existing_admin = session.exec(
                select(User).where(User.email == admin_email)
            ).first()
            
            if existing_admin:
                print(f"⚠️  Admin user already exists: {admin_email}")
                print("Admin credentials:")
                print(f"   Email: {admin_email}")
                print(f"   Password: (use your existing password)")
                return
            
            # Create new admin user
            admin_user = User(
                email=admin_email,
                password_hash=password_hash,
                name=admin_name,
                phone=admin_phone,
                member_since=datetime.utcnow(),
                avatar_url="https://api.dicebear.com/9.x/notionists/svg?seed=admin",
                reward_points=0
            )
            
            session.add(admin_user)
            session.commit()
            
            print("✅ Admin user created successfully!")
            print("\nAdmin credentials:")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
            print("\n🔐 Access admin portal at: http://localhost:3000/admin/login")
            print("\n⚠️  IMPORTANT: Change the password after first login!")
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

if __name__ == "__main__":
    create_admin_user()
