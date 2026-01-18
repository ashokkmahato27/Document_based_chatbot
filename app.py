import streamlit as st
import requests
import uuid
from datetime import datetime
import json
import os

# Configure page
st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="wide")

# Backend API URL
API_URL = "http://localhost:8000"

# File to save chat sessions
SESSIONS_FILE = "chat_sessions.json"

# Load saved sessions from file
def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

# Save sessions to file
def save_sessions(sessions):
    with open(SESSIONS_FILE, 'w') as f:
        json.dump(sessions, f, indent=2)

# Initialize session state
if "all_sessions" not in st.session_state:
    st.session_state.all_sessions = load_sessions()

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = str(uuid.uuid4())
    st.session_state.all_sessions[st.session_state.current_session_id] = {
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }
    save_sessions(st.session_state.all_sessions)

if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False

# Get current session
def get_current_session():
    return st.session_state.all_sessions.get(st.session_state.current_session_id, {
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    })

# Update session title based on first message
def update_session_title(session_id, first_message):
    if session_id in st.session_state.all_sessions:
        # Create title from first 50 chars of first message
        title = first_message[:50] + "..." if len(first_message) > 50 else first_message
        st.session_state.all_sessions[session_id]["title"] = title
        st.session_state.all_sessions[session_id]["last_updated"] = datetime.now().isoformat()
        save_sessions(st.session_state.all_sessions)

# Create new chat session
def create_new_session():
    new_id = str(uuid.uuid4())
    st.session_state.all_sessions[new_id] = {
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }
    st.session_state.current_session_id = new_id
    save_sessions(st.session_state.all_sessions)
    st.rerun()

# Switch to a different session
def switch_session(session_id):
    st.session_state.current_session_id = session_id
    st.rerun()

# Delete a session
def delete_session(session_id):
    if session_id in st.session_state.all_sessions:
        del st.session_state.all_sessions[session_id]
        save_sessions(st.session_state.all_sessions)
        
        # If deleted current session, create new one
        if session_id == st.session_state.current_session_id:
            create_new_session()
        else:
            st.rerun()

# Title
st.title("🤖 RAG Document Chatbot")

# Sidebar
with st.sidebar:
    # New Chat Button at top
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        create_new_session()
    
    st.divider()
    
    # Chat History Section
    st.header("💬 Chat History")
    
    # Sort sessions by last_updated (most recent first)
    sorted_sessions = sorted(
        st.session_state.all_sessions.items(),
        key=lambda x: x[1].get("last_updated", ""),
        reverse=True
    )
    
    # Display all sessions
    for session_id, session_data in sorted_sessions:
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Highlight current session
            if session_id == st.session_state.current_session_id:
                st.markdown(f"**▶️ {session_data['title']}**")
            else:
                if st.button(
                    session_data['title'],
                    key=f"session_{session_id}",
                    use_container_width=True
                ):
                    switch_session(session_id)
        
        with col2:
            if st.button("🗑️", key=f"delete_{session_id}", help="Delete chat"):
                delete_session(session_id)
        
        # Show message count
        msg_count = len(session_data.get("messages", []))
        st.caption(f"{msg_count} messages")
    
    st.divider()
    
    # Document Upload Section
    st.header("📄 Document Upload")
    
    uploaded_file = st.file_uploader(
        "Upload PDF or DOCX",
        type=["pdf", "docx"],
        help="Upload a document to chat about"
    )
    
    if uploaded_file:
        if st.button("Process Document", type="secondary", use_container_width=True):
            with st.spinner("Processing document..."):
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                try:
                    response = requests.post(f"{API_URL}/upload", files=files)
                    if response.status_code == 200:
                        st.session_state.document_uploaded = True
                        st.success(f"✅ Document processed! ({response.json()['chunks']} chunks)")
                    else:
                        st.error(f"Error: {response.json()['detail']}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
    
    st.divider()
    
    # Mode selection
    st.header("⚙️ Settings")
    mode = st.radio(
        "Answer Mode",
        ["document_only", "hybrid"],
        format_func=lambda x: "📄 Document Only" if x == "document_only" else "🌐 Hybrid (Doc + AI)",
        help="Document Only: Answers only from uploaded document\nHybrid: Uses document + general AI knowledge"
    )
    
    if not st.session_state.document_uploaded and mode == "document_only":
        st.warning("⚠️ Please upload a document first")

# Main chat area
current_session = get_current_session()

# Display chat history for current session
for idx, message in enumerate(current_session.get("messages", [])):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "mode" in message:
            st.caption(f"Mode: {message['mode']}")

# Chat input
if prompt := st.chat_input("Ask a question..."):
    # Check if document is needed
    if mode == "document_only" and not st.session_state.document_uploaded:
        st.error("Please upload a document first for document-only mode!")
    else:
        # Update session title if this is first message
        if len(current_session.get("messages", [])) == 0:
            update_session_title(st.session_state.current_session_id, prompt)
        
        # Add user message
        current_session["messages"].append({"role": "user", "content": prompt})
        st.session_state.all_sessions[st.session_state.current_session_id] = current_session
        save_sessions(st.session_state.all_sessions)
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(
                        f"{API_URL}/query",
                        json={
                            "question": prompt,
                            "mode": mode,
                            "session_id": st.session_state.current_session_id
                        }
                    )
                    
                    if response.status_code == 200:
                        answer = response.json()["answer"]
                        st.markdown(answer)
                        st.caption(f"Mode: {mode}")
                        
                        # Add to messages
                        current_session["messages"].append({
                            "role": "assistant",
                            "content": answer,
                            "mode": mode
                        })
                        
                        # Update session
                        current_session["last_updated"] = datetime.now().isoformat()
                        st.session_state.all_sessions[st.session_state.current_session_id] = current_session
                        save_sessions(st.session_state.all_sessions)
                    else:
                        error_msg = response.json()["detail"]
                        st.error(f"Error: {error_msg}")
                
                except Exception as e:
                    st.error(f"Connection error: {str(e)}\n\nMake sure the backend is running on http://localhost:8000")

# Footer
st.divider()
st.caption("Built with Streamlit, LangChain, FastAPI, and Groq")