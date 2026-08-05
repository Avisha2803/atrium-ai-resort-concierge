"""
tools.py
All @tool-decorated functions the LangGraph agents can call. Guardrails
(quantity caps, item-count caps, menu validation) are enforced here in
plain Python — not left to the LLM — so they can't be bypassed by prompting.
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from langchain_core.tools import tool

from backend.config import settings
from backend.database import SessionLocal
from backend.models import (FacilityInfo, FoodOrder, MenuItem, Room,
                            RoomServiceRequest)

ALLOWED_REQUEST_TYPES = {
    "Room Cleaning",
    "Laundry",
    "Extra Toiletries",
    "Extra Pillow",
    "Extra Blanket",
    "Toothpaste",
    "Other",
}


# --------------------------------------------------------------------------
# Receptionist tools
# --------------------------------------------------------------------------
@tool
def get_checkin_checkout_time() -> str:
    """Get the resort's standard check-in and check-out times."""
    db = SessionLocal()
    try:
        checkin = (
            db.query(FacilityInfo).filter(FacilityInfo.key == "check_in_time").first()
        )
        checkout = (
            db.query(FacilityInfo).filter(FacilityInfo.key == "check_out_time").first()
        )
        return (
            f"Check-in time: {checkin.info if checkin else '2:00 PM'}. "
            f"Check-out time: {checkout.info if checkout else '11:00 AM'}."
        )
    finally:
        db.close()


@tool
def get_facility_info(facility_name: str) -> str:
    """Get information (hours, location, booking) about a resort facility.

    Args:
        facility_name: name of the facility, e.g. 'gym', 'spa', or 'swimming pool'.
    """
    db = SessionLocal()
    try:
        key = facility_name.strip().lower().replace(" ", "_")
        fac = db.query(FacilityInfo).filter(FacilityInfo.key.ilike(f"%{key}%")).first()
        if fac:
            return fac.info
        return f"Sorry, I don't have information about '{facility_name}'. Available facilities: gym, spa, swimming pool."
    finally:
        db.close()


@tool
def check_room_availability(room_type: str = "any") -> str:
    """Check currently available rooms at the resort, optionally filtered by type.

    Args:
        room_type: 'Standard', 'Deluxe', 'Suite', 'Presidential Suite', or 'any'.
    """
    db = SessionLocal()
    try:
        query = db.query(Room).filter(Room.is_available == True)  # noqa: E712
        if room_type and room_type.lower() != "any":
            query = query.filter(Room.room_type.ilike(f"%{room_type}%"))
        rooms = query.all()
        if not rooms:
            return f"No available rooms found for type '{room_type}'."
        lines = [
            f"Room {r.room_number} ({r.room_type}) - Rs.{r.price_per_night:.0f}/night"
            for r in rooms
        ]
        return "Available rooms:\n" + "\n".join(lines)
    finally:
        db.close()


# --------------------------------------------------------------------------
# Restaurant tools
# --------------------------------------------------------------------------
@tool
def get_menu(category: str = "all") -> str:
    """Get the restaurant menu."""

    db = SessionLocal()

    import os

    from backend.database import engine

    try:
        total = db.query(MenuItem).count()

        items = db.query(MenuItem).all()

        for item in items[:5]:
            if total == 0:
                return "DATABASE IS EMPTY"

        base = db.query(MenuItem).filter(MenuItem.is_available == True)

        if category.lower() != "all":
            items = base.filter(MenuItem.category.ilike(f"%{category}%")).all()
        else:
            items = base.all()

        output = ""

        current = ""

        for item in items:

            if current != item.category:
                current = item.category
                output += f"\n## {current}\n"

            output += f"- {item.name} - Rs.{item.price}\n"

        return output

    finally:
        db.close()


@tool
def place_order(room_number: str, items: List[Dict[str, Any]]) -> str:
    """Place a food order and store it in the database.

    Args:
        room_number: the guest's room number.
        items: list of objects like {"name": "Butter Chicken", "quantity": 2}.
               Names must match menu items (case-insensitive).
    """
    if not items:
        return "No items were provided — please tell me what you'd like to order."
    if len(items) > settings.MAX_ITEMS_PER_ORDER:
        return (
            f"That's too many distinct items in one order "
            f"(max {settings.MAX_ITEMS_PER_ORDER}). Please split it into multiple orders."
        )

    db = SessionLocal()
    try:
        total = 0.0
        order_lines = []
        resolved_items = []

        for entry in items:
            name = str(entry.get("name", "")).strip()
            try:
                qty = int(entry.get("quantity", 1))
            except (TypeError, ValueError):
                return f"Invalid quantity for '{name}'."
            if qty <= 0:
                return f"Quantity for '{name}' must be at least 1."
            if qty > settings.MAX_QTY_PER_ITEM:
                return f"Quantity for '{name}' exceeds the max of {settings.MAX_QTY_PER_ITEM} per order."

            menu_item = (
                db.query(MenuItem)
                .filter(
                    MenuItem.name.ilike(name), MenuItem.is_available == True
                )  # noqa: E712
                .first()
            )
            if not menu_item:
                return (
                    f"Item '{name}' was not found on the menu, so the order was not placed. "
                    f"Please check the menu with get_menu and try again."
                )

            subtotal = menu_item.price * qty
            total += subtotal
            order_lines.append(f"{qty} x {menu_item.name} = Rs.{subtotal:.0f}")
            resolved_items.append(
                {"name": menu_item.name, "quantity": qty, "price": menu_item.price}
            )

        order = FoodOrder(
            room_number=str(room_number),
            items=json.dumps(resolved_items),
            total_amount=total,
            status="Pending",
            created_at=datetime.now(timezone.utc),
        )
        db.add(order)
        db.commit()
        db.refresh(order)

        return (
            f"Order #{order.id} placed for Room {room_number}.\n"
            + "\n".join(order_lines)
            + f"\nTotal: Rs.{total:.0f}\nStatus: Pending"
        )
    finally:
        db.close()


@tool
def get_order_status(order_id: int) -> str:
    """Get the status of a previously placed food order.

    Args:
        order_id: the numeric ID of the order.
    """
    db = SessionLocal()
    try:
        order = db.query(FoodOrder).filter(FoodOrder.id == order_id).first()
        if not order:
            return f"No order found with ID {order_id}."
        return f"Order #{order.id} - Status: {order.status} - Total: Rs.{order.total_amount:.0f}"
    finally:
        db.close()


# --------------------------------------------------------------------------
# Room Service tools
# --------------------------------------------------------------------------
@tool
def create_room_service_request(
    room_number: str, request_type: str, details: str = ""
) -> str:
    """Log a room service request (cleaning, laundry, or extra amenities).

    Args:
        room_number: the guest's room number.
        request_type: 'Room Cleaning', 'Laundry', 'Extra Toiletries',
                       'Extra Pillow', 'Extra Blanket', 'Toothpaste', or 'Other'.
        details: any extra notes from the guest (optional, max 500 chars).
    """
    normalized = request_type.strip() if request_type else "Other"
    if normalized not in ALLOWED_REQUEST_TYPES:
        details = f"(requested as: {normalized}) {details}".strip()
        normalized = "Other"

    db = SessionLocal()
    try:
        req = RoomServiceRequest(
            room_number=str(room_number),
            request_type=normalized,
            details=(details or "")[:500],
            status="Pending",
            created_at=datetime.now(timezone.utc),
        )
        db.add(req)
        db.commit()
        db.refresh(req)
        return f"Request #{req.id} ({normalized}) for Room {room_number} logged. Status: Pending."
    finally:
        db.close()


@tool
def get_service_request_status(request_id: int) -> str:
    """Get the status of a previously created room service request.

    Args:
        request_id: the numeric ID of the request.
    """
    db = SessionLocal()
    try:
        req = (
            db.query(RoomServiceRequest)
            .filter(RoomServiceRequest.id == request_id)
            .first()
        )
        if not req:
            return f"No request found with ID {request_id}."
        return f"Request #{req.id} ({req.request_type}) - Status: {req.status}"
    finally:
        db.close()
