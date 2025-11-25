"""
Rewards Program Migration Script
Adds reward_points field to User table and initializes all users with 0 points
"""
import reflex as rx
from sqlmodel import select
from app.db.models import User

def add_rewards_to_database():
    """Add rewards points to all users"""
    print("🎁 Starting Rewards Program Migration...")
    
    try:
        with rx.session() as session:
            # Check if the column already exists by trying to query it
            try:
                users = session.exec(select(User)).all()
                # Test if reward_points exists
                if hasattr(User, 'reward_points'):
                    print("✅ reward_points field already exists!")
                else:
                    print("❌ reward_points field needs to be added to models.py manually")
                    print("\nPlease add this line to the User class in app/db/models.py:")
                    print("    reward_points: int = Field(default=0)")
                    return False
                    
                print(f"Found {len(users)} users in database")
                
                # Initialize points for users who don't have any
                for user in users:
                    if not hasattr(user, 'reward_points') or user.reward_points is None:
                        user.reward_points = 0
                
                session.commit()
                print(f"✅ Successfully initialized rewards for {len(users)} users!")
                return True
                
            except Exception as e:
                print(f"⚠️ Error: {e}")
                print("\nThe reward_points field doesn't exist yet.")
                print("Please add this line to the User class in app/db/models.py (after line 16):")
                print("    reward_points: int = Field(default=0)")
                return False
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    add_rewards_to_database()
