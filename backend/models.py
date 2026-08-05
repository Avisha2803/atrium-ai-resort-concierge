"""
models.py
Five tables: rooms (inventory), menu items, facility info, food orders, and
room service requests. No login/auth tables in this build — the guest chat
widget just asks for a room number, matching the lightweight concierge
widget in the reference design. (A JWT-based login layer, like in the
previous version of this project, can be dropped in later without touching
this schema.)
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from backend.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True)
    room_number = Column(String, unique=True, nullable=False)
    room_type = Column(String, nullable=False)
    is_available = Column(Boolean, default=True)
    price_per_night = Column(Float, nullable=False)


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True)
    category = Column(String, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    description = Column(String, default="")
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)


class FacilityInfo(Base):
    __tablename__ = "facility_info"

    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    label = Column(String, nullable=False)
    info = Column(Text, nullable=False)


class FoodOrder(Base):
    __tablename__ = "food_orders"

    id = Column(Integer, primary_key=True)
    room_number = Column(String, nullable=False)
    items = Column(Text, nullable=False)  # JSON string
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="Pending")  # Pending / Preparing / Delivered
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class RoomServiceRequest(Base):
    __tablename__ = "room_service_requests"

    id = Column(Integer, primary_key=True)
    room_number = Column(String, nullable=False)
    request_type = Column(String, nullable=False)
    details = Column(Text, default="")
    status = Column(String, default="Pending")  # Pending / In Progress / Completed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
