"""Script to update parking lot images in the database"""
import reflex as rx
from sqlmodel import select
from app.db.models import ParkingLot


def update_parking_images():
    """Update all parking lot images to use new realistic images"""
    with rx.session() as session:
        # Get all parking lots
        lots = session.exec(select(ParkingLot)).all()
        
        # Map of image variations
        images = [
            "/parking/covered_mall.png",
            "/parking/premium.png",
            "/parking/city_center.png",
            "/parking/basement.png",
        ]
        
        # Update each lot with an image (cycle through the images)
        for i, lot in enumerate(lots):
            # Assign images in rotation
            lot.image_url = images[i % len(images)]
        
        session.commit()
        print(f"✅ Updated {len(lots)} parking lots with new images!")
        
        # Show what was updated
        print("\nUpdated parking lots:")
        for lot in lots:
            print(f"  - {lot.name}: {lot.image_url}")


if __name__ == "__main__":
    update_parking_images()
