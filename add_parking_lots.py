"""Script to add more parking lots to the database"""
import reflex as rx
from sqlmodel import select
from app.db.models import ParkingLot


def add_more_parking_lots():
    """Add additional parking lots to the database"""
    with rx.session() as session:
        # Check how many lots exist
        existing_count = len(session.exec(select(ParkingLot)).all())
        print(f"Current parking lots: {existing_count}")
        
        # New parking lots to add
        new_lots = [
            # Suria KLCC
            ParkingLot(
                name="Suria KLCC Basement",
                location="Kuala Lumpur City Centre",
                price_per_hour=5.5,
                total_spots=250,
                available_spots=200,
                image_url="/placeholder.svg",
                features="Covered,Direct Mall Access,EV Charging",
                rating=4.7,
            ),
            # More Bukit Bintang
            ParkingLot(
                name="Lot 10 Shopping Centre",
                location="Bukit Bintang",
                price_per_hour=4.0,
                total_spots=180,
                available_spots=150,
                image_url="/placeholder.svg",
                features="Covered,Wheelchair Access,Near MRT",
                rating=4.3,
            ),
            ParkingLot(
                name="Berjaya Times Square",
                location="Bukit Bintang",
                price_per_hour=3.5,
                total_spots=450,
                available_spots=400,
                image_url="/placeholder.svg",
                features="Covered,Theme Park Access,24/7",
                rating=4.0,
            ),
            # Mid Valley
            ParkingLot(
                name="Mid Valley North Wing",
                location="Mid Valley",
                price_per_hour=3.0,
                total_spots=400,
                available_spots=350,
                image_url="/placeholder.svg",
                features="Covered,Direct To Cinema,Family Parking",
                rating=4.4,
            ),
            ParkingLot(
                name="The Gardens Mall Premium",
                location="Mid Valley",
                price_per_hour=5.0,
                total_spots=300,
                available_spots=250,
                image_url="/placeholder.svg",
                features="Premium,Valet,Wide Bays,EV Charging",
                rating=4.8,
            ),
            # Bangsar
            ParkingLot(
                name="Bangsar Shopping Complex",
                location="Bangsar",
                price_per_hour=3.5,
                total_spots=120,
                available_spots=100,
                image_url="/placeholder.svg",
                features="Covered,Near LRT,Wheelchair Access",
                rating=4.1,
            ),
            # Sunway/PJ
            ParkingLot(
                name="Sunway Pyramid Zone A",
                location="Subang Jaya",
                price_per_hour=3.0,
                total_spots=350,
                available_spots=300,
                image_url="/placeholder.svg",
                features="Covered,Near Ice Rink,Family Parking",
                rating=4.5,
            ),
            ParkingLot(
                name="Paradigm Mall PJ",
                location="Petaling Jaya",
                price_per_hour=2.5,
                total_spots=400,
                available_spots=380,
                image_url="/placeholder.svg",
                features="Covered,Affordable,Smart Parking",
                rating=4.3,
            ),
            ParkingLot(
                name="1 Utama Orange Zone",
                location="Petaling Jaya",
                price_per_hour=3.0,
                total_spots=600,
                available_spots=500,
                image_url="/placeholder.svg",
                features="Covered,Multiple Entries,CCTV",
                rating=4.4,
            ),
            ParkingLot(
                name="1 Utama Blue Zone",
                location="Petaling Jaya",
                price_per_hour=3.0,
                total_spots=550,
                available_spots=480,
                image_url="/placeholder.svg",
                features="Covered,Near Cinema,EV Charging",
                rating=4.5,
            ),
            # Mont Kiara
            ParkingLot(
                name="Mont Kiara Plaza",
                location="Mont Kiara",
                price_per_hour=4.0,
                total_spots=200,
                available_spots=180,
                image_url="/placeholder.svg",
                features="Covered,Expat Area,Clean",
                rating=4.6,
            ),
            ParkingLot(
                name="Publika Shopping Gallery",
                location="Mont Kiara",
                price_per_hour=4.5,
                total_spots=250,
                available_spots=220,
                image_url="/placeholder.svg",
                features="Covered,Modern,Art Gallery Access",
                rating=4.7,
            ),
            # KL Sentral
            ParkingLot(
                name="NU Sentral Station",
                location="KL Sentral",
                price_per_hour=4.0,
                total_spots=300,
                available_spots=250,
                image_url="/placeholder.svg",
                features="Train Station,24/7,CCTV",
                rating=4.2,
            ),
            ParkingLot(
                name="KL Gateway Mall",
                location="KL Sentral",
                price_per_hour=3.5,
                total_spots=200,
                available_spots=170,
                image_url="/placeholder.svg",
                features="Covered,Near Office Towers",
                rating=4.3,
            ),
        ]
        
        # Check if any of these already exist
        existing_names = {lot.name for lot in session.exec(select(ParkingLot)).all()}
        lots_to_add = [lot for lot in new_lots if lot.name not in existing_names]
        
        if lots_to_add:
            session.add_all(lots_to_add)
            session.commit()
            print(f"✅ Successfully added {len(lots_to_add)} new parking lots!")
            print("\nNew lots added:")
            for lot in lots_to_add:
                print(f"  - {lot.name} ({lot.location})")
        else:
            print("ℹ️ All parking lots already exist in the database.")
        
        # Show final count
        final_count = len(session.exec(select(ParkingLot)).all())
        print(f"\nTotal parking lots now: {final_count}")


if __name__ == "__main__":
    add_more_parking_lots()
