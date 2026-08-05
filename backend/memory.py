from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ConversationMemory:

    room_number: str

    current_order: List[Dict] = field(default_factory=list)

    awaiting_confirmation: bool = False

    pending_room_service: Optional[Dict] = None

    booking: Optional[Dict] = None

    conversation_stage: str = "idle"


# ------------------------------------------------------------------
# In-memory session store
# ------------------------------------------------------------------

conversation_store = {}


def get_memory(room_number: str) -> ConversationMemory:

    if room_number not in conversation_store:

        conversation_store[room_number] = ConversationMemory(room_number=room_number)

    return conversation_store[room_number]


def clear_order(room_number: str):

    memory = get_memory(room_number)

    memory.current_order = []

    memory.awaiting_confirmation = False


def add_items(room_number: str, items):

    memory = get_memory(room_number)

    for new_item in items:

        found = False

        for existing in memory.current_order:

            if existing["name"] == new_item["name"]:

                existing["quantity"] += new_item["quantity"]

                found = True

                break

        if not found:

            memory.current_order.append(new_item)

    memory.awaiting_confirmation = True

    memory.conversation_stage = "restaurant"


def get_order_total(items):

    from backend.database import SessionLocal
    from backend.models import MenuItem

    db = SessionLocal()

    try:

        total = 0

        for order_item in items:

            menu = (
                db.query(MenuItem).filter(MenuItem.name == order_item["name"]).first()
            )

            if menu:
                total += menu.price * order_item["quantity"]

        return total

    finally:
        db.close()
