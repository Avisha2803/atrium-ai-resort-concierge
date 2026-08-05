"""
main.py
FastAPI backend.

Run with:
    uvicorn backend.main:app --reload

Guest page:
    http://localhost:8000/

API docs:
    http://localhost:8000/docs
"""

import json
import traceback
from contextlib import asynccontextmanager
from backend.database import SessionLocal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.checkpointer import get_checkpointer
from backend.config import settings
from backend.database import Base, engine, get_db
from backend.graph import build_graph
from backend.models import FoodOrder, RoomServiceRequest


# ---------------------------------------------------------------------
# App Lifespan
# ---------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)

    with get_checkpointer() as checkpointer:
        app.state.resort_graph = build_graph(checkpointer)
        yield


app = FastAPI(
    title="Atrium Resort AI Concierge",
    version="1.0.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------
# Chat Models
# ---------------------------------------------------------------------
class ChatRequest(BaseModel):
    room_number: str = Field(..., min_length=1, max_length=20)
    message: str = Field(..., min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    reply: str
    department: str | None = None


# ---------------------------------------------------------------------
# Chat Endpoint
# ---------------------------------------------------------------------
@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):

    resort_graph = app.state.resort_graph

    config = {"configurable": {"thread_id": f"room-{payload.room_number}"}}

    try:
        result = resort_graph.invoke(
            {
                "messages": [HumanMessage(content=payload.message)],
                "room_number": payload.room_number,
            },
            config=config,
        )

    except Exception as e:
        import traceback
        raise

    ai_messages = [
        m for m in result["messages"] if isinstance(m, AIMessage) and m.content
    ]

    reply = "Sorry, I couldn't process your request."

    if ai_messages:
        content = ai_messages[-1].content

        if isinstance(content, str):
            reply = content

        elif isinstance(content, list):
            parts = []

            for item in content:
                if isinstance(item, str):
                    parts.append(item)

                elif isinstance(item, dict):
                    parts.append(item.get("text", ""))

                elif hasattr(item, "text"):
                    parts.append(item.text)

                else:
                    parts.append(str(item))

            reply = "".join(parts)

        else:
            reply = str(content)

    return ChatResponse(
        reply=reply,
        department=result.get("next"),
    )


# ---------------------------------------------------------------------
# Dashboard APIs
# ---------------------------------------------------------------------
@app.get("/api/dashboard/orders")
def list_orders(db: Session = Depends(get_db)):
    orders = db.query(FoodOrder).order_by(FoodOrder.id.desc()).all()

    return [
        {
            "id": o.id,
            "room_number": o.room_number,
            "items": json.loads(o.items),
            "total_amount": o.total_amount,
            "status": o.status,
            "created_at": o.created_at.isoformat(),
        }
        for o in orders
    ]


@app.get("/api/dashboard/requests")
def list_requests(db: Session = Depends(get_db)):
    requests = db.query(RoomServiceRequest).order_by(RoomServiceRequest.id.desc()).all()

    return [
        {
            "id": r.id,
            "room_number": r.room_number,
            "request_type": r.request_type,
            "details": r.details or "",
            "status": r.status,
            "created_at": r.created_at.isoformat(),
        }
        for r in requests
    ]


@app.put("/api/dashboard/order/{order_id}")
def update_order(order_id: int, status: str):
    db = SessionLocal()
    try:
        order = db.query(FoodOrder).filter(FoodOrder.id == order_id).first()

        if not order:
            return {"error": "Order not found"}

        order.status = status
        db.commit()

        return {"success": True}
    finally:
        db.close()


@app.put("/api/dashboard/request/{request_id}")
def update_request(request_id: int, status: str):
    db = SessionLocal()
    try:
        request = (
            db.query(RoomServiceRequest)
            .filter(RoomServiceRequest.id == request_id)
            .first()
        )

        if not request:
            return {"error": "Request not found"}

        request.status = status
        db.commit()

        return {"success": True}
    finally:
        db.close()


# ---------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------
@app.get("/api/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------
# Frontend
# ---------------------------------------------------------------------
app.mount(
    "/",
    StaticFiles(directory="frontend", html=True),
    name="static",
)
