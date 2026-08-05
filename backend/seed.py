"""
seed.py
Creates tables (if missing) and seeds demo rooms, the restaurant menu
(loaded from data/menu.json), and facility info. Safe to re-run — every
step checks "if empty" first. Run with: python -m backend.seed
"""

import json
from pathlib import Path

from backend import models
from backend.database import Base, SessionLocal, engine

MENU_PATH = Path(__file__).parent.parent / "data" / "menu.json"


def seed_rooms(db):
    if db.query(models.Room).count() > 0:
        return
    demo_rooms = [
        ("101", "Standard", True, 3500),
        ("102", "Standard", True, 3500),
        ("103", "Standard", False, 3500),
        ("104", "Standard", True, 3500),
        ("201", "Deluxe", True, 5500),
        ("202", "Deluxe", True, 5500),
        ("203", "Deluxe", False, 5500),
        ("301", "Suite", True, 9000),
        ("302", "Suite", True, 9000),
        ("303", "Suite", False, 9000),
        ("401", "Presidential Suite", True, 18000),
    ]
    for number, rtype, available, price in demo_rooms:
        db.add(
            models.Room(
                room_number=number,
                room_type=rtype,
                is_available=available,
                price_per_night=price,
            )
        )
    db.commit()


def seed_menu(db):
    if db.query(models.MenuItem).count() > 0:
        return
    with open(MENU_PATH, "r", encoding="utf-8") as f:
        menu = json.load(f)
    count = 0
    for category, items in menu.items():
        for item in items:
            db.add(
                models.MenuItem(
                    category=category,
                    name=item["name"],
                    description=item.get("description", ""),
                    price=item["price"],
                    is_available=True,
                )
            )
            count += 1
    db.commit()


def seed_facilities(db):
    if db.query(models.FacilityInfo).count() > 0:
        return
    facilities = [
        ("check_in_time", "Check-in Time", "2:00 PM"),
        ("check_out_time", "Check-out Time", "11:00 AM"),
        (
            "gym",
            "Gym",
            "Open 24/7 on the 2nd floor. Free for all in-house guests, no booking required.",
        ),
        (
            "spa",
            "Spa",
            "Open 9:00 AM - 9:00 PM near the pool deck. Advance booking recommended, call extension 105.",
        ),
        (
            "swimming_pool",
            "Swimming Pool",
            "Open 6:00 AM - 8:00 PM, temperature controlled, ground floor near the garden.",
        ),
    ]
    for key, label, info in facilities:
        db.add(models.FacilityInfo(key=key, label=label, info=info))
    db.commit()


def seed_demo_orders(db):
    """A few demo orders/requests so the dashboard isn't empty on first run."""
    if db.query(models.FoodOrder).count() > 0:
        return
    demo_orders = [
        ("101", [{"name": "Masala Dosa", "quantity": 2, "price": 120}], "Delivered"),
        ("104", [{"name": "Omelette", "quantity": 1, "price": 90}], "Pending"),
        ("202", [{"name": "Puri Bhaji", "quantity": 2, "price": 140}], "Preparing"),
        ("304", [{"name": "Paneer Paratha", "quantity": 2, "price": 150}], "Delivered"),
        ("309", [{"name": "Boiled Eggs", "quantity": 1, "price": 70}], "Delivered"),
        ("405", [{"name": "Green Salad", "quantity": 2, "price": 80}], "Preparing"),
        ("502", [{"name": "Plain Curd", "quantity": 2, "price": 60}], "Preparing"),
        (
            "409",
            [{"name": "Fresh Fruit Platter", "quantity": 2, "price": 140}],
            "Pending",
        ),
    ]
    for room, items, status in demo_orders:
        total = sum(i["price"] * i["quantity"] for i in items)
        db.add(
            models.FoodOrder(
                room_number=room,
                items=json.dumps(items),
                total_amount=total,
                status=status,
            )
        )
    db.commit()


def seed_demo_requests(db):
    if db.query(models.RoomServiceRequest).count() > 0:
        return
    demo_requests = [
        ("101", "Room Cleaning", "", "Completed"),
        ("104", "Extra Pillow", "2 pillows", "Pending"),
        ("202", "Laundry", "3 shirts, 1 trouser", "In Progress"),
        ("301", "Extra Toiletries", "shampoo, toothpaste", "Pending"),
        ("303", "Room Cleaning", "", "In Progress"),
        ("401", "Extra Blanket", "1 blanket", "Completed"),
        ("104", "Toothpaste", "", "Pending"),
    ]
    for room, rtype, details, status in demo_requests:
        db.add(
            models.RoomServiceRequest(
                room_number=room, request_type=rtype, details=details, status=status
            )
        )
    db.commit()


def run():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        seed_rooms(db)
        seed_menu(db)
        seed_facilities(db)
        seed_demo_orders(db)
        seed_demo_requests(db)
    finally:
        db.close()
    print("Seeding complete.")


if __name__ == "__main__":
    run()
