import streamlit as st
import requests
import uuid
from datetime import datetime

# Configure page
st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="wide")

# Backend API URL
API_URL = "http://localhost:8000"

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "document_uploaded" not in st.session_state:
    st.session_state.document_uploaded = False

# Title
st.title("🤖 RAG Document Chatbot")
st.markdown("Upload a document and ask questions!")

# Sidebar
with st.sidebar:
    st.header("📄 Document Upload")
    
    uploaded_file = st.file_uploader(
        "Upload PDF or DOCX",
        type=["pdf", "docx"],
        help="Upload a document to chat about"
    )
    
    if uploaded_file:
        if st.button("Process Document", type="primary"):
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
    
    st.divider()
    
    # Session management
    st.header("💾 Session")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("New Session"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()
    
    # Show session info
    st.caption(f"Session: {st.session_state.session_id[:8]}...")

# Main chat area
st.header("💬 Chat")

# Display chat history
for message in st.session_state.messages:
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
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
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
                            "session_id": st.session_state.session_id
                        }
                    )
                    
                    if response.status_code == 200:
                        answer = response.json()["answer"]
                        st.markdown(answer)
                        st.caption(f"Mode: {mode}")
                        
                        # Add to messages
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "mode": mode
                        })
                    else:
                        error_msg = response.json()["detail"]
                        st.error(f"Error: {error_msg}")
                
                except Exception as e:
                    st.error(f"Connection error: {str(e)}\n\nMake sure the backend is running on http://localhost:8000")

# Footer
st.divider()
st.caption("Built with Streamlit, LangChain, FastAPI, and Groq")