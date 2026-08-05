"""
graph.py

LangGraph Supervisor Architecture

Supervisor
      |
      |------ Receptionist
      |------ Restaurant
      |------ Room Service
"""

import re
from typing import Literal

from langchain_core.messages import AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, MessagesState, StateGraph

from backend.config import settings
from backend.database import SessionLocal
from backend.memory import add_items, clear_order, get_memory, get_order_total
from backend.models import MenuItem
from backend.tools import (check_room_availability,
                           create_room_service_request,
                           get_checkin_checkout_time, get_facility_info,
                           get_menu, get_order_status,
                           get_service_request_status, place_order)

# ---------------------------------------------------------------------
# Gemini LLM
# ---------------------------------------------------------------------

if not settings.GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not found in .env")

llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0,
    max_retries=settings.LLM_MAX_RETRIES,
)


# ---------------------------------------------------------------------
# Graph State
# ---------------------------------------------------------------------


class ResortState(MessagesState):
    room_number: str
    next: Literal[
        "receptionist",
        "restaurant",
        "roomservice",
    ]


# ---------------------------------------------------------------------
# Parse Food Order
# ---------------------------------------------------------------------

NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def parse_order(message: str):
    """
    Extract menu items and quantities from the user's message.

    Example:
    "2 Butter Naan and 1 Dal Makhani"

    Returns:
    [
        {"name": "Butter Naan", "quantity": 2},
        {"name": "Dal Makhani", "quantity": 1}
    ]
    """

    db = SessionLocal()

    try:
        menu_items = sorted(
            db.query(MenuItem).all(),
            key=lambda x: len(x.name),
            reverse=True,
        )

        text = message.lower()

        order = []

        for item in menu_items:

            item_name = item.name.lower()

            if item_name in text:

                quantity = 1

                match = re.search(
                    rf"(\d+)\s+{re.escape(item_name)}",
                    text,
                )

                if match:
                    quantity = int(match.group(1))

                else:
                    # Match word quantities
                    for word, value in NUMBER_WORDS.items():
                        if re.search(
                            rf"\b{word}\s+{re.escape(item_name)}",
                            text,
                        ):
                            quantity = value
                            break

                order.append(
                    {
                        "name": item.name,
                        "quantity": quantity,
                    }
                )

                text = text.replace(item_name, "")

        return order

    finally:
        db.close()


# ---------------------------------------------------------------------
# Department Classifier
# ---------------------------------------------------------------------


def classify_department(
    message: str,
    room_number: str,
) -> Literal[
    "receptionist",
    "restaurant",
    "roomservice",
]:

    msg = message.lower()
    memory = get_memory(room_number)

    # ----------------------------------------------------
    # Continue current conversation
    # ----------------------------------------------------

    if memory.conversation_stage == "restaurant":
        if msg in [
            "yes",
            "no",
            "done",
            "cancel",
            "modify",
        ]:
            return "restaurant"

    # ---------------- Restaurant ----------------

    restaurant_keywords = [
        "menu",
        "food",
        "eat",
        "order",
        "pizza",
        "burger",
        "naan",
        "roti",
        "dal",
        "rice",
        "paneer",
        "chicken",
        "coffee",
        "tea",
        "dessert",
        "drink",
        "juice",
        "raita",
        "papad",
        "salad",
        "pickle",
        "gravy",
        "butter",
        "extra rice",
        "kulcha",
        "paratha",
        "idli",
        "dosa",
    ]

    items = parse_order(msg)
    if items:
        return "restaurant"

    if any(word in msg for word in restaurant_keywords):
        return "restaurant"

    # ---------------- Room Service ----------------

    roomservice_keywords = [
        "blanket",
        "pillow",
        "towel",
        "laundry",
        "clean",
        "cleaning",
        "housekeeping",
        "toothpaste",
        "soap",
        "toiletries",
        "amenities",
    ]

    if any(word in msg for word in roomservice_keywords):
        return "roomservice"

    # ---------------- Reception ----------------

    reception_keywords = [
        "check in",
        "check out",
        "spa",
        "gym",
        "pool",
        "facility",
        "facilities",
        "availability",
        "available room",
        "room available",
    ]

    if any(word in msg for word in reception_keywords):
        return "receptionist"

    # ---------------- Gemini Fallback ----------------

    prompt = f"""
You are a routing assistant.

Return ONLY one word.

Choices:

receptionist
restaurant
roomservice

User:

{message}
"""

    response = llm.invoke(prompt)

    answer = str(response.content).strip().lower()

    if "restaurant" in answer:
        return "restaurant"

    if "roomservice" in answer:
        return "roomservice"

    return "receptionist"


def extract_room_number(message: str, default_room: str):

    match = re.search(r"\broom\s*(\d+)\b", message.lower())

    if match:
        return match.group(1)

    return default_room


# ---------------------------------------------------------------------
# Supervisor Node
# ---------------------------------------------------------------------


def supervisor_node(state: ResortState):
    """
    Decide which department should handle the user's latest message.
    """

    latest_message = str(state["messages"][-1].content)

    room_number = state.get("room_number", "unknown")

    department = classify_department(
        latest_message,
        room_number,
    )

    return {"next": department}


# ---------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------


def route(state: ResortState):

    return state["next"]


# ---------------------------------------------------------------------
# Receptionist Node
# ---------------------------------------------------------------------


def receptionist_node(state: ResortState):

    message = str(state["messages"][-1].content).lower()

    # ---------------- Check-in / Check-out ----------------

    if (
        "check in" in message
        or "check-in" in message
        or "check out" in message
        or "check-out" in message
    ):

        result = get_checkin_checkout_time.invoke({})

        return {"messages": [AIMessage(content=result)]}

    # ---------------- Facilities ----------------

    facility_map = {
        "gym": "gym",
        "spa": "spa",
        "pool": "swimming pool",
        "swimming": "swimming pool",
    }

    for keyword, facility in facility_map.items():

        if keyword in message:

            result = get_facility_info.invoke({"facility_name": facility})

            return {"messages": [AIMessage(content=result)]}

    # ---------------- Room Availability ----------------

    if "available" in message or "availability" in message:

        room_type = "any"

        if "standard" in message:
            room_type = "Standard"

        elif "deluxe" in message:
            room_type = "Deluxe"

        elif "suite" in message:
            room_type = "Suite"

        result = check_room_availability.invoke({"room_type": room_type})

        return {"messages": [AIMessage(content=result)]}

    # ---------------- Default ----------------

    return {
        "messages": [
            AIMessage(
                content=(
                    "I can help you with:\n\n"
                    "• Check-in / Check-out timings\n"
                    "• Room availability\n"
                    "• Gym\n"
                    "• Spa\n"
                    "• Swimming Pool"
                )
            )
        ]
    }


# ---------------------------------------------------------------------
# Restaurant Node
# ---------------------------------------------------------------------


def restaurant_node(state: ResortState):

    message = str(state["messages"][-1].content).lower()

    room_number = extract_room_number(message, state.get("room_number", "unknown"))

    memory = get_memory(room_number)
    memory.conversation_stage = "restaurant"

    # --------------------------------------------------
    # Guest finished adding items
    # --------------------------------------------------

    if message in ["no", "no thanks", "that's all", "thats all", "done"]:
        if not memory.current_order:
            return {"messages": [AIMessage(content="Your order is empty.")]}

        total = get_order_total(memory.current_order)

        summary = []

        for item in memory.current_order:

            summary.append(f"{item['quantity']} x {item['name']}")

        memory.awaiting_confirmation = True

        return {
            "messages": [
                AIMessage(
                    content=(
                        "Please confirm your order.\n\n"
                        + "\n".join(summary)
                        + f"\n\nTotal: ₹{total:.0f}"
                        + "\n\nReply YES to confirm, MODIFY to change it, or CANCEL."
                    )
                )
            ]
        }

    # --------------------------------------------------
    # Guest confirms
    # --------------------------------------------------

    if message == "yes":
        if not memory.awaiting_confirmation:
            return {
                "messages": [
                    AIMessage(content="There is no order awaiting confirmation.")
                ]
            }

        result = place_order.invoke(
            {
                "room_number": room_number,
                "items": memory.current_order,
            }
        )

        clear_order(room_number)
        memory = get_memory(room_number)

        memory.conversation_stage = "idle"

        return {"messages": [AIMessage(content=result)]}

    # --------------------------------------------------
    # Cancel
    # --------------------------------------------------

    if message == "cancel":
        clear_order(room_number)
        memory = get_memory(room_number)
        memory.awaiting_confirmation = False
        memory.conversation_stage = "idle"

        return {"messages": [AIMessage(content="Your order has been cancelled.")]}

    # -------------------------------------------------
    # Show Menu
    # -------------------------------------------------

    if "menu" in message:

        menu = get_menu.invoke({"category": "all"})

        return {"messages": [AIMessage(content=menu)]}

    # -------------------------------------------------
    # Order Status
    # -------------------------------------------------

    if "status" in message:

        match = re.search(r"\d+", message)

        if match:

            order_id = int(match.group())

            status = get_order_status.invoke({"order_id": order_id})

            return {"messages": [AIMessage(content=status)]}

        return {"messages": [AIMessage(content="Please provide your order ID.")]}

    # -------------------------------------------------
    # Place Order
    # -------------------------------------------------

    items = parse_order(message)

    if not items:

        return {
            "messages": [
                AIMessage(
                    content=(
                        "I couldn't identify any menu items.\n\n"
                        "Example:\n"
                        "• 2 Butter Naan\n"
                        "• 1 Dal Makhani\n"
                        "• 1 Raita"
                    )
                )
            ]
        }

    # -------------------------------
    # Store in Conversation Memory
    # -------------------------------

    add_items(room_number, items)

    memory = get_memory(room_number)

    summary = []

    for item in memory.current_order:
        summary.append(f"{item['quantity']} x {item['name']}")

    reply = (
        "Added to your order.\n\n"
        "Current Order:\n\n" + "\n".join(summary) + "\n\nAnything else?"
    )

    return {"messages": [AIMessage(content=reply)]}


# ---------------------------------------------------------------------
# Room Service Node
# ---------------------------------------------------------------------


def roomservice_node(state: ResortState):

    message = str(state["messages"][-1].content).lower()

    room_number = state.get("room_number", "unknown")

    request_type = None
    details = ""

    # ---------------- Blanket ----------------

    if "blanket" in message:
        request_type = "Extra Blanket"
        details = message

    # ---------------- Pillow ----------------

    elif "pillow" in message:
        request_type = "Extra Pillow"
        details = message

    # ---------------- Towel ----------------

    elif "towel" in message:
        request_type = "Extra Toiletries"
        details = "Extra towels requested."

    # ---------------- Laundry ----------------

    elif "laundry" in message:
        request_type = "Laundry"
        details = message

    # ---------------- Cleaning ----------------

    elif "clean" in message or "cleaning" in message:
        request_type = "Room Cleaning"
        details = message

    # ---------------- Toiletries ----------------

    elif (
        "toothpaste" in message
        or "soap" in message
        or "toiletries" in message
        or "shampoo" in message
    ):
        request_type = "Extra Toiletries"
        details = message

    # ---------------- Unknown ----------------

    else:
        return {
            "messages": [
                AIMessage(
                    content=(
                        "I can help you with:\n\n"
                        "• Room Cleaning\n"
                        "• Laundry\n"
                        "• Extra Blanket\n"
                        "• Extra Pillow\n"
                        "• Towels\n"
                        "• Toiletries"
                    )
                )
            ]
        }

    result = create_room_service_request.invoke(
        {
            "room_number": room_number,
            "request_type": request_type,
            "details": details,
        }
    )

    return {"messages": [AIMessage(content=result)]}


# ---------------------------------------------------------------------
# Build LangGraph
# ---------------------------------------------------------------------


def build_graph(checkpointer):

    graph = StateGraph(ResortState)

    # Nodes
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("receptionist", receptionist_node)
    graph.add_node("restaurant", restaurant_node)
    graph.add_node("roomservice", roomservice_node)

    # Entry
    graph.set_entry_point("supervisor")

    # Conditional routing
    graph.add_conditional_edges(
        "supervisor",
        route,
        {
            "receptionist": "receptionist",
            "restaurant": "restaurant",
            "roomservice": "roomservice",
        },
    )

    # End nodes
    graph.add_edge("receptionist", END)
    graph.add_edge("restaurant", END)
    graph.add_edge("roomservice", END)

    return graph.compile(checkpointer=checkpointer)
