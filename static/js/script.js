let currentSessionId = null;

// =============================================
// Helpers
// =============================================

function showChat() {
    document.getElementById("welcomeScreen").classList.add("hidden");
    document.getElementById("chat").classList.add("active");
}

function showWelcome() {
    document.getElementById("welcomeScreen").classList.remove("hidden");
    document.getElementById("chat").classList.remove("active");
}

function fillQuestion(text) {
    const q = document.getElementById("question");
    q.value = text;
    q.focus();
    autoResize(q);
}

function autoResize(el) {
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 140) + "px";
}

// =============================================
// Create Session
// =============================================

async function createSession() {
    const res = await fetch("/session", { method: "POST" });
    const data = await res.json();
    currentSessionId = data.session_id;
    document.getElementById("chat").innerHTML = "";
    showChat();
    document.getElementById("question").focus();
    await loadSessions();
}

// =============================================
// Load Sessions
// =============================================

async function loadSessions() {
    const res = await fetch("/sessions");
    const sessions = await res.json();
    const list = document.getElementById("sessionList");
    list.innerHTML = "";

    sessions.forEach(session => {
        const item = document.createElement("div");
        item.className = "session-item" + (session.id === currentSessionId ? " active" : "");

        const span = document.createElement("span");
        span.className = "session-title";
        span.innerText = session.title;
        span.onclick = () => loadConversation(session.id);

        const btn = document.createElement("button");
        btn.className = "delete-btn";
        btn.innerText = "✕";
        btn.title = "Delete";
        btn.onclick = async (e) => {
            e.stopPropagation();
            await deleteSession(session.id);
        };

        item.appendChild(span);
        item.appendChild(btn);
        list.appendChild(item);
    });
}

// =============================================
// Load Conversation
// =============================================

async function loadConversation(sessionId) {
    currentSessionId = sessionId;

    const res = await fetch(`/messages/${sessionId}`);
    const messages = await res.json();

    const chat = document.getElementById("chat");
    chat.innerHTML = "";
    showChat();

    messages.forEach(msg => appendMessage(msg.role, msg.content));

    chat.scrollTop = chat.scrollHeight;
    await loadSessions();
}

// =============================================
// Append Message
// =============================================

function appendMessage(role, content) {
    const chat = document.getElementById("chat");

    if (role === "user") {
        chat.innerHTML += `
            <div class="user">
                <div class="bubble">${escapeHtml(content)}</div>
            </div>`;
    } else {
        chat.innerHTML += `
            <div class="ai">
                <div class="ai-avatar">🤖</div>
                <div class="bubble markdown">${marked.parse(content)}</div>
            </div>`;
    }
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

// =============================================
// Delete Session
// =============================================

async function deleteSession(sessionId) {
    await fetch(`/session/${sessionId}`, { method: "DELETE" });
    if (currentSessionId === sessionId) {
        currentSessionId = null;
        document.getElementById("chat").innerHTML = "";
        showWelcome();
    }
    await loadSessions();
}

// =============================================
// Upload Document
// =============================================

async function uploadDocument(file) {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch("/upload", { method: "POST", body: formData });
    const data = await res.json();
    alert(data.message);
    await loadDocuments();
}

// =============================================
// Load Documents
// =============================================

async function loadDocuments() {
    const res = await fetch("/documents");
    const data = await res.json();
    const docList = document.getElementById("docList");
    docList.innerHTML = "";

    if (data.documents.length === 0) return;

    const label = document.createElement("div");
    label.className = "doc-list-label";
    label.innerText = "📚 Knowledge Base";
    docList.appendChild(label);

    for (const doc of data.documents) {
        const detail = await fetch(`/documents/${encodeURIComponent(doc)}`);
        const detailData = await detail.json();

        const row = document.createElement("div");
        row.className = "doc-item";

        const name = document.createElement("span");
        name.className = "doc-name";
        name.title = doc;
        name.innerText = `${doc} · ${detailData.chunk_count} chunks`;

        const btn = document.createElement("button");
        btn.className = "doc-delete-btn";
        btn.innerText = "✕";
        btn.title = "Remove from knowledge base";
        btn.onclick = async () => {
            await fetch(`/documents/${encodeURIComponent(doc)}`, { method: "DELETE" });
            await loadDocuments();
        };

        row.appendChild(name);
        row.appendChild(btn);
        docList.appendChild(row);
    }
}

// =============================================
// Ask LLM
// =============================================

async function ask() {
    const input = document.getElementById("question");
    const question = input.value.trim();
    const sendBtn = document.getElementById("sendBtn");

    if (!question) return;

    if (!currentSessionId) {
        await createSession();
    }

    const chat = document.getElementById("chat");
    const loader = document.getElementById("loader");

    showChat();
    appendMessage("user", question);

    input.value = "";
    input.style.height = "auto";
    sendBtn.disabled = true;
    loader.classList.remove("hidden");

    // Typing indicator
    const typingId = "typing-" + Date.now();
    chat.innerHTML += `
        <div class="ai" id="${typingId}">
            <div class="ai-avatar">🤖</div>
            <div class="bubble">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        </div>`;
    chat.scrollTop = chat.scrollHeight;

    try {
        const res = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: currentSessionId,
                question: question
            })
        });

        const data = await res.json();

        document.getElementById(typingId)?.remove();

        appendMessage("assistant", data.answer);
        chat.scrollTop = chat.scrollHeight;

        await loadSessions();

    } catch (err) {
        console.error(err);
        document.getElementById(typingId)?.remove();
    }

    loader.classList.add("hidden");
    sendBtn.disabled = false;
    input.focus();
}

// =============================================
// Startup
// =============================================

document.addEventListener("DOMContentLoaded", async () => {

    await loadSessions();
    await loadDocuments();

    // File upload
    document.getElementById("fileInput").addEventListener("change", async (e) => {
        const file = e.target.files[0];
        if (file) await uploadDocument(file);
        e.target.value = "";
    });

    // New Chat button
    document.getElementById("newChatBtn").addEventListener("click", () => {
        currentSessionId = null;
        document.getElementById("chat").innerHTML = "";
        showWelcome();
        document.getElementById("question").focus();
    });

    // Textarea enter / shift+enter
    document.getElementById("question").addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            ask();
        }
    });

    // Auto-resize textarea
    document.getElementById("question").addEventListener("input", (e) => {
        autoResize(e.target);
    });
});
