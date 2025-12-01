"""Quick test to check if parking lots load"""
import reflex as rx
from sqlmodel import select
from app.db.models import ParkingLot
from app.states.schema import ParkingLot as ParkingLotSchema

with rx.session() as session:
    stmt = select(ParkingLot)
    db_lots = session.exec(stmt).all()
    
    print(f"\n✅ Database has {len(db_lots)} parking lots\n")
    
    if len(db_lots) > 0:
        print("Converting to schema objects...")
        schema_lots = [
            ParkingLotSchema(
                id=str(lot.id),
                name=lot.name,
                location=lot.location,
                price_per_hour=lot.price_per_hour,
                total_spots=lot.total_spots,
                available_spots=lot.available_spots,
                image_url=lot.image_url,
                features=lot.features.split(",") if lot.features else [],
                rating=lot.rating,
            )
            for lot in db_lots
        ]
        print(f"✅ Successfully converted {len(schema_lots)} lots to schema objects\n")
        
        print("First 3 parking lots:")
        for i, lot in enumerate(schema_lots[:3], 1):
            print(f"{i}. {lot.name} - {lot.location}")
            print(f"   Price: RM{lot.price_per_hour}/hr")
            print(f"   Available: {lot.available_spots}/{lot.total_spots}")
            print(f"   Image: {lot.image_url}")
            print()
    else:
        print("❌ No parking lots found in database!")
