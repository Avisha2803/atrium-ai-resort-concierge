const API = "/api";

const launcher = document.getElementById("launcher");
const widget = document.getElementById("widget");
const closeWidget = document.getElementById("closeWidget");
const roomGate = document.getElementById("roomGate");
const chatBody = document.getElementById("chatBody");
const roomInput = document.getElementById("roomInput");
const roomContinue = document.getElementById("roomContinue");
const messagesEl = document.getElementById("messages");
const quickActionsEl = document.getElementById("quickActions");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");

const QUICK_ACTIONS = [
  { icon: "🍽️", label: "Show Menu", prompt: "Show me the menu" },
  { icon: "🛎️", label: "Room Availability", prompt: "What rooms are available?" },
  { icon: "🧹", label: "Room Service", prompt: "I need room service" },
  { icon: "🏊", label: "Facilities", prompt: "Tell me about the resort facilities" },
];

function getRoom() { return localStorage.getItem("atrium_room"); }
function setRoom(r) { localStorage.setItem("atrium_room", r); }

function openWidget() {
  widget.classList.remove("hidden");
  const room = getRoom();
  if (room) {
    showChat(room);
  } else {
    roomGate.classList.remove("hidden");
    chatBody.classList.add("hidden");
  }
}

function closeWidgetFn() {
  widget.classList.add("hidden");
}

function showChat(room) {
  roomGate.classList.add("hidden");
  chatBody.classList.remove("hidden");
  if (messagesEl.childElementCount === 0) {
    addBotMessage(
      `Hello! I am your resort concierge. How can I assist you today, Room ${room}? ` +
      `I can help with room service, restaurant orders, or general inquiries.`
    );
    renderQuickActions();
  }
}

function renderQuickActions() {
  quickActionsEl.innerHTML = "";
  QUICK_ACTIONS.forEach((a) => {
    const btn = document.createElement("button");
    btn.className = "quick-pill";
    btn.innerHTML = `<span>${a.icon}</span><span>${a.label}</span>`;
    btn.addEventListener("click", () => sendMessage(a.prompt));
    quickActionsEl.appendChild(btn);
  });
}

function timeNow() {
  const d = new Date();
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function addUserMessage(text) {
  const row = document.createElement("div");
  row.className = "msg-row user";
  row.innerHTML = `
    <div class="msg-avatar">🧑</div>
    <div>
      <div class="msg-bubble"></div>
      <div class="msg-time" style="text-align:right;">${timeNow()}</div>
    </div>`;
  row.querySelector(".msg-bubble").textContent = text;
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addBotMessage(text) {
  const row = document.createElement("div");
  row.className = "msg-row bot";
  row.innerHTML = `
    <div class="msg-avatar">🤖</div>
    <div>
      <div class="msg-bubble"></div>
      <div class="msg-time">${timeNow()}</div>
    </div>`;
  row.querySelector(".msg-bubble").textContent = text;
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return row;
}

function addTypingIndicator() {
  const row = document.createElement("div");
  row.className = "msg-row bot typing-row";
  row.innerHTML = `<div class="msg-avatar">🤖</div><div class="msg-bubble">Typing…</div>`;
  messagesEl.appendChild(row);
  messagesEl.scrollTop = messagesEl.scrollHeight;
  return row;
}

async function sendMessage(text) {
  const room = getRoom();
  if (!text || !room) return;
  addUserMessage(text);
  chatInput.value = "";

  const typingRow = addTypingIndicator();

  try {
    const res = await fetch(`${API}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ room_number: room, message: text }),
    });
    typingRow.remove();

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      addBotMessage(err.detail || "Something went wrong. Please try again.");
      return;
    }
    const data = await res.json();
    addBotMessage(data.reply);
  } catch (e) {
    typingRow.remove();
    addBotMessage("Could not reach the server. Please try again.");
  }
}

launcher.addEventListener("click", openWidget);
closeWidget.addEventListener("click", closeWidgetFn);

roomContinue.addEventListener("click", () => {
  const room = roomInput.value.trim();
  if (!room) return;
  setRoom(room);
  showChat(room);
});
roomInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") roomContinue.click();
});

sendBtn.addEventListener("click", () => sendMessage(chatInput.value.trim()));
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage(chatInput.value.trim());
});

// Auto-open the widget once, and pre-fill room from a previous visit.
if (getRoom()) {
  roomInput.value = getRoom();
}
