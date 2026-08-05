# 🏝️ Atrium AI Resort Concierge

<p align="center">

An AI-powered multi-agent resort concierge that automates guest interactions using **Google Gemini**, **LangGraph**, **FastAPI**, **SQLite**, and a **Streamlit Operations Dashboard**.

</p>

---

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue)

![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)

![LangGraph](https://img.shields.io/badge/LangGraph-MultiAgent-orange)

![Gemini](https://img.shields.io/badge/Google-Gemini-red)

![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B)

![SQLite](https://img.shields.io/badge/SQLite-Database-blue)

![License](https://img.shields.io/badge/License-MIT-green)

</p>

---

# 🏨 About the Project

Atrium AI Resort Concierge is a production-style, AI-powered hotel assistant designed to automate guest interactions through a conversational interface.

The system leverages **Google Gemini**, **LangGraph**, **FastAPI**, and **SQLite** to intelligently route guest requests, maintain conversation context, process restaurant orders, handle room service requests, and provide resort information in real time.

Unlike a traditional rule-based chatbot, Atrium uses a **multi-agent architecture** where specialized agents collaborate to provide accurate, context-aware responses while maintaining persistent conversation memory.

Hotel staff can monitor and manage all guest activities through a dedicated **Streamlit Operations Dashboard**, enabling real-time order tracking, room service management, and operational insights.

---

## 🌐 Live Links

- 🚀 Live AI Concierge:
  https://atrium-ai-resort-concierge.onrender.com

- 📊 Operations Dashboard:
  https://atrium-ai-resort-concierge-ywafbm5ey3qxraexab8qwj.streamlit.app

- 📄 Interactive API Documentation:
  https://atrium-ai-resort-concierge.onrender.com/docs

---

## ✨ Why This Project?

Modern hotels receive hundreds of repetitive guest requests every day, such as:

- 🍽 Food ordering
- 🛎 Room service requests
- 🏊 Facility information
- 🏨 Room availability
- ⏰ Check-in & Check-out queries

Atrium AI Concierge automates these interactions using Large Language Models (LLMs), reducing staff workload while improving guest experience through natural language conversations.

---

## 🎯 Key Highlights

- 🤖 Multi-Agent AI Architecture using LangGraph
- 🧠 Persistent Conversation Memory
- 🍽 Multi-turn Food Ordering
- ✅ Order Confirmation Workflow
- 🛎 Room Service Automation
- 🏨 Reception Assistant
- 📊 Live Operations Dashboard
- ⚡ FastAPI REST Backend
- 🗄 SQLite Database
- 🧩 Modular & Extensible Design

# 🚀 Features

Atrium AI Resort Concierge is designed as a modular, multi-agent AI system that automates common hotel guest interactions while providing hotel staff with real-time operational visibility.

---

## 🤖 AI Concierge

The central AI assistant intelligently understands guest requests, maintains conversation context, and routes them to the appropriate department.

### Capabilities

- Multi-agent routing using LangGraph
- Natural language understanding with Google Gemini
- Context-aware conversations
- Persistent conversation memory
- Intelligent department routing
- Modular architecture for future expansion

---

## 🍽 Restaurant Assistant

The Restaurant Agent enables guests to browse the menu, place food orders naturally, and track their orders.

### Features

- Browse complete restaurant menu
- Category-wise menu support
- Multi-turn food ordering
- Add items across multiple messages
- Automatic order confirmation
- Order status tracking
- SQLite order persistence
- Quantity validation
- Menu item validation
- Duplicate item handling

### Example Conversation

```text
Guest:
Show me the menu

↓

2 Butter Naan

↓

1 Dal Makhani

↓

No

↓

YES

↓

Order Placed Successfully
```

---

## 🛎 Room Service Assistant

Guests can request housekeeping services using natural language.

### Supported Requests

- Room Cleaning
- Laundry
- Extra Blanket
- Extra Pillow
- Extra Toiletries
- Toothpaste
- Towels

Every request is automatically stored in the database and becomes instantly visible on the staff dashboard.

---

## 🏨 Reception Assistant

The Reception Agent answers common guest queries including:

- Check-in Time
- Check-out Time
- Gym Information
- Spa Information
- Swimming Pool Details
- Room Availability

The assistant uses backend tools instead of hallucinating responses.

---

## 🧠 Conversation Memory

The assistant remembers the ongoing conversation during an ordering session.

Example

```text
Guest:
2 Butter Naan

Bot:
Added to your order.

Guest:
1 Dal Makhani

Bot:
Added to your order.

Guest:
No

Bot:
Please confirm your order.

Guest:
YES

Bot:
Order placed successfully.
```

This provides a natural conversational ordering experience instead of requiring the guest to specify the complete order in a single message.

---

## 📊 Operations Dashboard

The Streamlit dashboard provides hotel staff with real-time operational insights.

### Dashboard Features

- Live Food Orders
- Room Service Requests
- Order Status Monitoring
- Revenue Tracking
- Interactive Charts
- Pending Orders Overview
- Staff-friendly Management Interface


# 🏗 System Architecture

Atrium AI Resort Concierge follows a modular **multi-agent architecture** where every guest request is routed to a specialized department. This separation keeps the system scalable, maintainable, and easy to extend with additional hotel services.

---

## High-Level Architecture

```text
                          👤 Guest
                             │
                             ▼
                 Floating Chat Widget
                   (HTML • CSS • JS)
                             │
                    REST API Request
                             │
                             ▼
                  FastAPI Backend Server
                             │
                             ▼
                 LangGraph Supervisor Agent
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
 Reception Agent      Restaurant Agent    Room Service Agent
        │                    │                    │
        │                    │                    │
        ▼                    ▼                    ▼
 Reception Tools      Restaurant Tools    Service Tools
        │                    │                    │
        └────────────────────┼────────────────────┘
                             ▼
                     SQLite Database
                  (Orders • Rooms • Menu
                 Facilities • Service Requests)
                             │
                             ▼
                 Streamlit Operations Dashboard
```

---

# 🔄 Request Processing Workflow

Every guest message follows the same processing pipeline.

```text
Guest Message
      │
      ▼
FastAPI API Endpoint
      │
      ▼
LangGraph Supervisor
      │
      ▼
Determine Department
      │
      ├────────► Reception
      │
      ├────────► Restaurant
      │
      └────────► Room Service
                     │
                     ▼
              Execute Backend Tool
                     │
                     ▼
              Store/Retrieve Data
                     │
                     ▼
              Generate AI Response
                     │
                     ▼
              Return Response to Guest
```

---

# 🤖 Multi-Agent Design

The application is divided into three specialized AI agents.

| Agent | Responsibilities |
|-------|------------------|
| 🏨 Reception | Check-in/out, facilities, room availability |
| 🍽 Restaurant | Menu, ordering, order confirmation, order status |
| 🛎 Room Service | Cleaning, laundry, blankets, pillows, toiletries |

Each agent only has access to its own backend tools, reducing unnecessary complexity and preventing cross-department actions.

---

# 🧠 Conversation Memory

The assistant maintains conversational context during ordering sessions.

Example workflow:

```text
Show Menu
      │
      ▼
2 Butter Naan
      │
      ▼
Added to Order
      │
      ▼
1 Dal Makhani
      │
      ▼
Added to Order
      │
      ▼
No
      │
      ▼
Show Confirmation
      │
      ▼
YES
      │
      ▼
Store Order in SQLite
```

Conversation memory enables the assistant to build orders across multiple user messages instead of requiring the complete order in a single prompt.

---

# 🗄 Database Design

The application stores operational data in SQLite.

Main tables include:

- Rooms
- Menu Items
- Facility Information
- Food Orders
- Room Service Requests

The dashboard reads directly from the same database, ensuring hotel staff always view the latest information without additional synchronization.

---

# ⚙ Backend Workflow

```text
User Request
      │
      ▼
FastAPI
      │
      ▼
Supervisor Routing
      │
      ▼
Department Agent
      │
      ▼
Backend Tool
      │
      ▼
SQLite Database
      │
      ▼
AI Response
      │
      ▼
Guest
```

This modular workflow makes it straightforward to add new departments such as Spa Booking, Airport Pickup, Taxi Reservation, or Wake-up Calls without modifying the existing agents.

# 🛠 Tech Stack

| Category | Technologies |
|-----------|--------------|
| **Programming Language** | Python 3.10+ |
| **Backend Framework** | FastAPI |
| **AI Framework** | LangGraph, LangChain |
| **Large Language Model** | Google Gemini 2.5 Flash |
| **Database** | SQLite, SQLAlchemy |
| **Frontend** | HTML, CSS, JavaScript |
| **Dashboard** | Streamlit, Plotly |
| **Configuration** | Python Dotenv |
| **Version Control** | Git, GitHub |

---

# 📂 Project Structure

```text
atrium-ai-resort-concierge/
│
├── backend/
│   ├── checkpointer.py
│   ├── config.py
│   ├── database.py
│   ├── graph.py
│   ├── main.py
│   ├── memory.py
│   ├── models.py
│   ├── seed.py
│   └── tools.py
│
├── data/
│   └── menu.json
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── widget.js
│
├── screenshots/
│   ├── home.png
│   ├── chat.png
│   ├── ordering.png
│   ├── roomservice.png
│   └── dashboard.png
│
├── dashboard.py
├── requirements.txt
├── README.md
├── LICENSE
└── .env.example
```

---

# ⚙ Installation

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/Avisha2803/atrium-ai-resort-concierge.git

cd atrium-ai-resort-concierge
```

---

## 2️⃣ Create a Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Configure Environment Variables

Create a file named

```text
.env
```

Add the following values:

```env
GOOGLE_API_KEY=YOUR_GEMINI_API_KEY

GEMINI_MODEL=gemini-2.5-flash

DATABASE_URL=sqlite:///./resort.db

CHECKPOINT_DB_PATH=./checkpoints.sqlite

LLM_MAX_RETRIES=3

MAX_QTY_PER_ITEM=20

MAX_ITEMS_PER_ORDER=15
```

---

## 5️⃣ Seed the Database

Run:

```bash
python -m backend.seed
```

This command creates:

- Rooms
- Restaurant Menu
- Resort Facilities
- Demo Food Orders
- Demo Room Service Requests

---

## 6️⃣ Run the Backend

```bash
uvicorn backend.main:app --reload
```

Backend URL

```
http://localhost:8000
```

---

## 7️⃣ Run the Dashboard

Open another terminal and execute:

```bash
streamlit run dashboard.py
```

Dashboard URL

```
http://localhost:8501
```

---

# 🌐 Available Services

| Service | Live URL |
|----------|----------|
| 🌐 AI Concierge | https://atrium-ai-resort-concierge.onrender.com |
| 📊 Operations Dashboard | https://atrium-ai-resort-concierge-ywafbm5ey3qxraexab8qwj.streamlit.app |

---

# 🔑 Environment Variables

| Variable | Description |
|----------|-------------|
| GOOGLE_API_KEY | Google Gemini API Key |
| GEMINI_MODEL | Gemini model name |
| DATABASE_URL | SQLite database path |
| CHECKPOINT_DB_PATH | LangGraph conversation memory |
| MAX_QTY_PER_ITEM | Maximum quantity per menu item |
| MAX_ITEMS_PER_ORDER | Maximum unique items per order |
| LLM_MAX_RETRIES | Maximum retries for Gemini API |

---

# 📸 Screenshots

> **Note:** Replace the placeholder images below with actual screenshots after deployment.

## 🏠 Landing Page

The resort landing page with the floating AI concierge widget.

![Landing Page](screenshots/home.png)

🔗 Live Website:
https://atrium-ai-resort-concierge.onrender.com
---

## 💬 AI Concierge Chat

Natural language conversation with the AI concierge.

![Chat](screenshots/chat.png)

---

## 🍽 Multi-turn Restaurant Ordering

Ordering food over multiple conversational turns with confirmation.

![Ordering](screenshots/ordering.png)

---

## 🛎 Room Service Request

Creating room service requests through natural language.

![Room Service](screenshots/roomservice.png)

---

## 📊 Operations Dashboard

Live Streamlit dashboard displaying food orders, room service requests, and operational insights.

![Dashboard](screenshots/dashboard.png)

🔗 Live Dashboard:
https://atrium-ai-resort-concierge-ywafbm5ey3qxraexab8qwj.streamlit.app

---

# 🎥 Demo

## Live Application

| Service | URL |
|----------|-----|
| 🌐 AI Concierge | https://atrium-ai-resort-concierge.onrender.com |
| 📊 Dashboard | https://atrium-ai-resort-concierge-ywafbm5ey3qxraexab8qwj.streamlit.app |
| 📄 API Docs | https://atrium-ai-resort-concierge.onrender.com/docs |
---

## Demo Video

A complete walkthrough demonstrating:

- Guest Chat
- Restaurant Ordering
- Room Service
- Reception Queries
- Operations Dashboard

📹 **Coming Soon**

---

# 🔌 REST API

## Chat

```http
POST /api/chat
```

Example Request

```json
{
    "room_number": "201",
    "message": "Show me the menu"
}
```

---

## Dashboard APIs

Retrieve all food orders

```http
GET /api/dashboard/orders
```

Retrieve room service requests

```http
GET /api/dashboard/service-requests
```

Update food order status

```http
PUT /api/dashboard/orders/{order_id}
```

Update room service request

```http
PUT /api/dashboard/service-requests/{request_id}
```

---

# 💼 Resume Highlights

This project demonstrates experience with:

- ✅ Multi-Agent AI Systems
- ✅ LangGraph Workflows
- ✅ Google Gemini Integration
- ✅ FastAPI REST APIs
- ✅ SQLite Database Design
- ✅ SQLAlchemy ORM
- ✅ Streamlit Dashboard Development
- ✅ Multi-turn Conversational AI
- ✅ Conversation Memory
- ✅ Prompt Engineering
- ✅ Backend System Design
- ✅ Full Stack AI Application Development

---

# 🚀 Future Roadmap

## Version 1.0 ✅

- Multi-Agent AI Concierge
- Restaurant Ordering
- Room Service Automation
- Reception Assistant
- Conversation Memory
- Operations Dashboard

---

## Version 1.1 🚧

- Modify Existing Orders
- Smart Food Recommendations
- Category-wise Menu Browsing
- Fuzzy Menu Search
- Better Natural Language Understanding

---

## Version 2.0 🚀

- Spa Booking
- Restaurant Reservation
- Airport Pickup
- Taxi Booking
- Wake-up Calls
- Late Check-out Requests
- Bill Generation

---

## Version 3.0 🌍

- Voice Assistant
- WhatsApp Integration
- Mobile Application
- PostgreSQL Support
- Redis Memory
- Docker Deployment
- Kubernetes Deployment
- CI/CD Pipeline
- Cloud Monitoring

---

# 🤝 Contributing

Contributions are welcome!

If you have suggestions for improvements or discover any issues, feel free to:

- Open an Issue
- Submit a Pull Request
- Share Feature Requests

---

# 👩‍💻 Author

## Shruti Agarwal

**M.Tech, Biomedical Engineering**  
**Indian Institute of Technology (IIT) Kharagpur**

### Connect with me

**LinkedIn**

https://www.linkedin.com/in/shruti2803/

**GitHub**

https://github.com/Avisha2803

---

# 🙏 Acknowledgements

This project was built using the following open-source technologies:

- FastAPI
- LangGraph
- LangChain
- Google Gemini
- Streamlit
- SQLAlchemy
- Plotly

Special thanks to the open-source community for providing excellent tools and documentation.

---

# ⭐ If you found this project helpful...

Please consider giving it a ⭐ on GitHub!

It helps others discover the project and motivates future improvements.

---

# 📄 License

This project is licensed under the **MIT License**.

See the `LICENSE` file for more details.

