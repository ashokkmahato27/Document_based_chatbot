import streamlit as st
import requests, uuid, json, os
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config("RAG Chatbot", "🤖", layout="wide")
API_URL = "http://localhost:8000"
SESSIONS_FILE = "chat_sessions.json"

# ---------------- HELPERS ----------------
def now():
    return datetime.now().isoformat()

def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        try:
            return json.load(open(SESSIONS_FILE))
        except:
            pass
    return {}

def save_sessions():
    json.dump(st.session_state.sessions, open(SESSIONS_FILE, "w"), indent=2)

def new_chat():
    st.session_state.current = str(uuid.uuid4())
    st.session_state.draft = {"messages": [], "title": "New Chat"}
    st.session_state.doc_uploaded = False
    st.rerun()

# ---------------- STATE ----------------
if "sessions" not in st.session_state:
    st.session_state.sessions = load_sessions()

for s in st.session_state.sessions.values():
    s.setdefault("messages", [])
    s.setdefault("title", "New Chat")
    s.setdefault("updated", now())
    s.setdefault("doc_uploaded", False)

if "current" not in st.session_state:
    new_chat()
if "draft" not in st.session_state:
    st.session_state.draft = None
if "doc_uploaded" not in st.session_state:
    st.session_state.doc_uploaded = False

session = st.session_state.sessions.get(st.session_state.current) or st.session_state.draft

# ---------------- UI ----------------
st.title("🤖 RAG Document Chatbot")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    if st.button("➕ New Chat", use_container_width=True):
        new_chat()

    st.divider()
    st.subheader("💬 Chat History")

    valid_sessions = {sid: s for sid, s in st.session_state.sessions.items() if s["messages"]}

    for sid, data in sorted(valid_sessions.items(), key=lambda x: x[1]["updated"], reverse=True):
        c1, c2 = st.columns([5, 1])
        if c1.button(("▶️ " if sid == st.session_state.current else "") + data["title"], key=f"s_{sid}", use_container_width=True):
            st.session_state.current = sid
            st.session_state.draft = None
            st.session_state.doc_uploaded = data.get("doc_uploaded", False)
            st.rerun()
        if c2.button("🗑️", key=f"d_{sid}"):
            del st.session_state.sessions[sid]
            save_sessions()
            new_chat()
        st.caption(f"{len(data['messages'])} messages")

    st.divider()
    st.subheader("📄 Upload Document")

    file = st.file_uploader("PDF or DOCX", type=["pdf", "docx"])
    if file and st.button("Process", use_container_width=True):
        if not st.session_state.current:
            st.error("No active session!")
        else:
            with st.spinner("Processing document..."):
                try:
                    r = requests.post(
                        f"{API_URL}/upload",
                        params={"session_id": st.session_state.current},
                        files={"file": (file.name, file, file.type)}
                    )
                    try:
                        res = r.json()
                    except ValueError:
                        st.error(f"Upload failed: {r.text}")
                        res = None

                    if r.status_code == 200 and res:
                        st.session_state.doc_uploaded = True
                        session["doc_uploaded"] = True
                        st.success(f"Processed successfully ({res['chunks']} chunks)")
                    else:
                        detail = res.get("detail") if res else r.text
                        st.error(f"Upload failed: {detail}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")

    st.divider()
    mode = st.radio(
        "Answer Mode",
        ["document_only", "hybrid", "Normal"],
        format_func=lambda m: {"document_only": "📄 Document Only", "hybrid": "🌐 Hybrid", "Normal": "🧠 Normal"}[m]
    )

    if mode == "document_only" and not st.session_state.doc_uploaded:
        st.warning("Upload a document first")

# ---------------- CHAT HISTORY ----------------
if session and session.get("messages"):
    for msg in session["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "mode" in msg:
                st.caption(f"Mode: {msg['mode']}")

# ---------------- CHAT INPUT ----------------
if prompt := st.chat_input("Ask a question..."):
    if mode == "document_only" and not st.session_state.doc_uploaded:
        st.error("Please upload a document first")
    else:
        if st.session_state.current not in st.session_state.sessions:
            st.session_state.sessions[st.session_state.current] = {
                "title": prompt[:50],
                "messages": [],
                "updated": now(),
                "doc_uploaded": st.session_state.doc_uploaded,
            }
            session = st.session_state.sessions[st.session_state.current]
            st.session_state.draft = None

        session["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    r = requests.post(
                        f"{API_URL}/query",
                        json={
                            "question": prompt,
                            "mode": mode,
                            "session_id": st.session_state.current,
                        },
                    )
                    answer = r.json().get("answer", "Error")
                    st.markdown(answer)
                    st.caption(f"Mode: {mode}")

                    session["messages"].append({"role": "assistant", "content": answer, "mode": mode})
                    session["updated"] = now()
                    save_sessions()
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")

st.divider()
st.caption("Built with Streamlit • FastAPI • LangChain • FAISS")
