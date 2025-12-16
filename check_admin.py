"""
Quick script to create or check admin user in the database
"""
import os
from sqlmodel import Session, select, create_engine
from dotenv import load_dotenv
import bcrypt

# Load environment
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Import models
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.db.models import User as DBUser

# Create engine
engine = create_engine(DATABASE_URL)

def check_admin_users():
    """Check existing admin users"""
    with Session(engine) as session:
        # Get all users with 'admin' in email
        admin_users = session.exec(
            select(DBUser).where(DBUser.email.contains("admin"))
        ).all()
        
        print("\n=== ADMIN USERS IN DATABASE ===\n")
        if admin_users:
            for user in admin_users:
                print(f"Email: {user.email}")
                print(f"Name: {user.name}")
                print(f"Has Password: {'Yes' if user.password_hash else 'No'}")
                print("-" * 40)
        else:
            print("❌ No admin users found!")
            print("\nTo create an admin user, use the create_admin_user() function")

def create_admin_user(email="admin@parkmycar.com", password="admin123", name="Admin"):
    """Create a new admin user"""
    with Session(engine) as session:
        # Check if user exists
        existing = session.exec(
            select(DBUser).where(DBUser.email == email)
        ).first()
        
        if existing:
            print(f"❌ User {email} already exists!")
            return
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user
        new_user = DBUser(
            email=email,
            name=name,
            password_hash=password_hash
        )
        
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        
        print(f"✅ Admin user created successfully!")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Name: {name}")

def test_admin_login(email, password):
    """Test if admin credentials work"""
    with Session(engine) as session:
        user = session.exec(
            select(DBUser).where(DBUser.email == email)
        ).first()
        
        if not user:
            print(f"❌ User {email} not found")
            return False
        
        if "admin" not in email.lower():
            print(f"❌ Email must contain 'admin'")
            return False
        
        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            print(f"✅ Login successful for {email}")
            return True
        else:
            print(f"❌ Invalid password")
            return False

if __name__ == "__main__":
    print("=" * 50)
    print("ADMIN USER MANAGEMENT")
    print("=" * 50)
    
    # Check existing admin users
    check_admin_users()
    
    print("\n" + "=" * 50)
    print("CREATE NEW ADMIN USER")
    print("=" * 50)
    print("\nUncomment the line below to create admin user:")
    print("create_admin_user('admin@parkmycar.com', 'admin123', 'Admin User')")
    
    # Uncomment to create:
    create_admin_user('admin@parkmycar.com', 'admin123', 'Admin User')
    
    print("\n" + "=" * 50)
    print("TEST LOGIN")
    print("=" * 50)
    test_admin_login('admin@parkmycar.com', 'admin123')
