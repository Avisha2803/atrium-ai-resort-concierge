"""
dashboard.py
Staff operations dashboard, built with Streamlit + Plotly. Reads and writes
the SAME resort.db SQLite file the FastAPI backend uses — this is a
separate process, not a client of the REST API.

Run with:  streamlit run dashboard.py
"""

import json

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from backend.database import Base, SessionLocal, engine
from backend.models import FoodOrder, RoomServiceRequest

st.set_page_config(
    page_title="Resort Operations Dashboard", page_icon="📋", layout="wide"
)
Base.metadata.create_all(engine)

ORDER_STATUSES = ["Pending", "Preparing", "Delivered"]
REQUEST_STATUSES = ["Pending", "In Progress", "Completed"]

STATUS_COLORS = {
    "Pending": "#f2a900",
    "Preparing": "#3355c9",
    "Delivered": "#3d0f6e",
    "In Progress": "#3355c9",
    "Completed": "#1f9d55",
}


# --------------------------------------------------------------------------
# Data access
# --------------------------------------------------------------------------
def load_orders() -> pd.DataFrame:
    db = SessionLocal()
    try:
        orders = db.query(FoodOrder).order_by(FoodOrder.id.desc()).all()
        rows = []
        for o in orders:
            items = json.loads(o.items)
            items_str = ", ".join(f"{i['quantity']}x {i['name']}" for i in items)
            rows.append(
                {
                    "Order ID": o.id,
                    "Room": o.room_number,
                    "Items": items_str,
                    "Amount (₹)": o.total_amount,
                    "Status": o.status,
                    "Created At": o.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
        return pd.DataFrame(rows)
    finally:
        db.close()


def load_requests() -> pd.DataFrame:
    db = SessionLocal()
    try:
        reqs = db.query(RoomServiceRequest).order_by(RoomServiceRequest.id.desc()).all()
        rows = []
        for r in reqs:
            rows.append(
                {
                    "Request ID": r.id,
                    "Room": r.room_number,
                    "Type": r.request_type,
                    "Details": r.details or "",
                    "Status": r.status,
                    "Created At": r.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
        return pd.DataFrame(rows)
    finally:
        db.close()


def update_order_status(order_id: int, status: str):
    db = SessionLocal()
    try:
        o = db.query(FoodOrder).filter(FoodOrder.id == order_id).first()
        if o:
            o.status = status
            db.commit()
    finally:
        db.close()


def update_request_status(request_id: int, status: str):
    db = SessionLocal()
    try:
        r = (
            db.query(RoomServiceRequest)
            .filter(RoomServiceRequest.id == request_id)
            .first()
        )
        if r:
            r.status = status
            db.commit()
    finally:
        db.close()


def apply_filters(
    df: pd.DataFrame, status_filter: str, room_filter: str
) -> pd.DataFrame:
    filtered = df.copy()
    if status_filter and status_filter != "Choose an option":
        filtered = filtered[filtered["Status"] == status_filter]
    if room_filter:
        filtered = filtered[
            filtered["Room"]
            .astype(str)
            .str.contains(room_filter.strip(), case=False, na=False)
        ]
    return filtered


# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 📋 Resort Ops")
    st.markdown("---")
    st.markdown("### 🔍 Filters")
    all_statuses = ["Choose an option"] + sorted(set(ORDER_STATUSES + REQUEST_STATUSES))
    status_filter = st.selectbox("Filter by Status", all_statuses)
    room_filter = st.text_input("Room Number", placeholder="e.g., 101")
    st.write("")
    auto_refresh = st.checkbox("Auto-refresh (30s)")
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()
    st.markdown("---")
    st.caption("Resort Operations Dashboard v2.0")

if auto_refresh:
    st_autorefresh(interval=30_000, key="dashboard_autorefresh")


# --------------------------------------------------------------------------
# Header + top metrics
# --------------------------------------------------------------------------
st.markdown("## 📋 Resort Operations Dashboard")
st.caption("Real-time monitoring and management of resort operations")

orders_all = load_orders()
requests_all = load_requests()

total_orders = len(orders_all)
revenue = orders_all["Amount (₹)"].sum() if not orders_all.empty else 0
pending_orders = (
    int((orders_all["Status"] == "Pending").sum()) if not orders_all.empty else 0
)
service_requests_count = len(requests_all)

m1, m2, m3, m4 = st.columns(4)
m1.metric("🍽️ Total Orders", total_orders)
m2.metric("💰 Revenue", f"₹{revenue:,.0f}")
m3.metric("⏳ Pending Orders", pending_orders)
m4.metric("🧹 Service Requests", service_requests_count)

tab_overview, tab_orders, tab_requests = st.tabs(
    ["📊 Overview", "🍽️ Orders", "🧹 Service Requests"]
)

# --------------------------------------------------------------------------
# Overview tab
# --------------------------------------------------------------------------
with tab_overview:
    st.markdown("### 📈 Analytics")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Order Status Distribution**")
        if not orders_all.empty:
            counts = orders_all["Status"].value_counts().reset_index()
            counts.columns = ["Status", "Count"]
            fig = px.pie(
                counts,
                names="Status",
                values="Count",
                color="Status",
                color_discrete_map=STATUS_COLORS,
                hole=0.0,
            )
            fig.update_traces(textposition="inside", textinfo="percent")
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), legend_title_text="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No orders yet.")

    with col_b:
        st.markdown("**Top 10 Rooms by Revenue**")
        if not orders_all.empty:
            by_room = (
                orders_all.groupby("Room")["Amount (₹)"]
                .sum()
                .reset_index()
                .sort_values("Amount (₹)", ascending=False)
                .head(10)
            )
            fig2 = px.bar(
                by_room,
                x="Room",
                y="Amount (₹)",
                color="Amount (₹)",
                color_continuous_scale="Purples",
            )
            fig2.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No orders yet.")

# --------------------------------------------------------------------------
# Orders tab
# --------------------------------------------------------------------------
with tab_orders:
    st.markdown("### 🍽️ Restaurant Orders")

    if orders_all.empty:
        st.info("No restaurant orders yet.")
    else:
        st.markdown("#### ⚡ Quick Actions")
        sel_id = st.selectbox(
            "Select Order ID", orders_all["Order ID"].tolist(), key="order_select"
        )
        qc1, qc2, qc3 = st.columns(3)
        if qc1.button("🕒 Mark as Pending", use_container_width=True):
            update_order_status(sel_id, "Pending")
            st.rerun()
        if qc2.button("👨‍🍳 Mark as Preparing", use_container_width=True):
            update_order_status(sel_id, "Preparing")
            st.rerun()
        if qc3.button("✅ Mark as Delivered", use_container_width=True):
            update_order_status(sel_id, "Delivered")
            st.rerun()

        st.write("")
        st.caption(
            "💡 Edit the status directly in the table below and click 'Save Changes' to update"
        )

        orders_view = apply_filters(orders_all, status_filter, room_filter)
        edited_orders = st.data_editor(
            orders_view,
            column_config={
                "Order ID": st.column_config.NumberColumn(disabled=True),
                "Room": st.column_config.TextColumn(disabled=True),
                "Items": st.column_config.TextColumn(disabled=True, width="large"),
                "Amount (₹)": st.column_config.NumberColumn(
                    disabled=True, format="₹%.2f"
                ),
                "Status": st.column_config.SelectboxColumn(
                    "Status", options=ORDER_STATUSES
                ),
                "Created At": st.column_config.TextColumn(disabled=True),
            },
            hide_index=True,
            use_container_width=True,
            key="orders_editor",
        )

        if st.button("💾 Save Changes", key="save_orders"):
            original = orders_view.set_index("Order ID")["Status"].to_dict()
            changed = 0
            for _, row in edited_orders.iterrows():
                oid = int(row["Order ID"])
                if original.get(oid) != row["Status"]:
                    update_order_status(oid, row["Status"])
                    changed += 1
            st.success(f"Updated {changed} order(s).")
            st.rerun()

# --------------------------------------------------------------------------
# Service Requests tab
# --------------------------------------------------------------------------
with tab_requests:
    st.markdown("### 🧹 Room Service Requests")

    if requests_all.empty:
        st.info("No room service requests yet.")
    else:
        st.markdown("#### ⚡ Quick Actions")
        sel_req_id = st.selectbox(
            "Select Request ID",
            requests_all["Request ID"].tolist(),
            key="request_select",
        )
        rc1, rc2, rc3 = st.columns(3)
        if rc1.button(
            "🕒 Mark as Pending", use_container_width=True, key="req_pending"
        ):
            update_request_status(sel_req_id, "Pending")
            st.rerun()
        if rc2.button(
            "🚧 Mark as In Progress", use_container_width=True, key="req_progress"
        ):
            update_request_status(sel_req_id, "In Progress")
            st.rerun()
        if rc3.button(
            "✅ Mark as Completed", use_container_width=True, key="req_completed"
        ):
            update_request_status(sel_req_id, "Completed")
            st.rerun()

        st.write("")
        st.caption(
            "💡 Edit the status directly in the table below and click 'Save Changes' to update"
        )

        requests_view = apply_filters(requests_all, status_filter, room_filter)
        edited_requests = st.data_editor(
            requests_view,
            column_config={
                "Request ID": st.column_config.NumberColumn(disabled=True),
                "Room": st.column_config.TextColumn(disabled=True),
                "Type": st.column_config.TextColumn(disabled=True),
                "Details": st.column_config.TextColumn(disabled=True, width="large"),
                "Status": st.column_config.SelectboxColumn(
                    "Status", options=REQUEST_STATUSES
                ),
                "Created At": st.column_config.TextColumn(disabled=True),
            },
            hide_index=True,
            use_container_width=True,
            key="requests_editor",
        )

        if st.button("💾 Save Changes", key="save_requests"):
            original = requests_view.set_index("Request ID")["Status"].to_dict()
            changed = 0
            for _, row in edited_requests.iterrows():
                rid = int(row["Request ID"])
                if original.get(rid) != row["Status"]:
                    update_request_status(rid, row["Status"])
                    changed += 1
            st.success(f"Updated {changed} request(s).")
            st.rerun()
