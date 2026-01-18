# 🤖 RAG Document Chatbot

A simple and powerful RAG (Retrieval-Augmented Generation) chatbot that allows you to chat with your documents using AI. Upload PDF or DOCX files and ask questions with ChatGPT-style interface and persistent chat history!

## ✨ Features

- 📄 **Document Upload**: Support for PDF and DOCX files
- 🔍 **Two Answer Modes**:
  - **Document Only**: Answers strictly from uploaded document
  - **Hybrid**: Combines document knowledge + general AI knowledge
- 💬 **Chat Memory**: Remembers conversation context
- 💾 **Persistent Chat History**: ChatGPT-style sidebar with saved conversations
- 🗂️ **Multiple Sessions**: Create, switch, and manage multiple chat sessions
- 🗑️ **Delete Chats**: Remove unwanted conversations
- 📝 **Auto-Naming**: Chats automatically titled from first message
- 🎨 **Clean UI**: Beautiful Streamlit interface
- ⚡ **Fast API Backend**: RESTful API with FastAPI
- 🧠 **Powered by Groq**: Ultra-fast LLM inference

## 🎯 New ChatGPT-Style Features

- **Chat History Sidebar**: All conversations listed in sidebar (most recent first)
- **Quick Navigation**: Click any chat to switch instantly
- **New Chat Button**: Create new conversations with one click
- **Delete Chats**: Remove individual conversations
- **Message Counter**: See message count for each chat
- **Current Chat Indicator**: Active chat highlighted with ▶️
- **Auto-Save**: All chats automatically saved to disk
- **Persistent Storage**: Chats survive app restarts

## 🏗️ Architecture

```
frontend.py (Streamlit) ←→ backend.py (FastAPI) ←→ Groq API
       ↓                           ↓
chat_sessions.json          Vector Store (FAISS)
```

## 📋 Prerequisites

- Python 3.8 or higher
- Groq API Key (free at [console.groq.com](https://console.groq.com))

## 🚀 Quick Start

### 1. Clone/Download the Project

```bash
# Create project directory
mkdir rag-chatbot
cd rag-chatbot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get Your Groq API Key

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **Create API Key**
5. Copy your API key (starts with `gsk_`)

### 4. Set Up API Key

**Option A: Environment Variable (Recommended)**

**Linux/Mac:**
```bash
export GROQ_API_KEY="gsk_your_actual_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set GROQ_API_KEY=gsk_your_actual_api_key_here
```

**Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY="gsk_your_actual_api_key_here"
```

**Option B: Using .env File**

1. Create a `.env` file in the project root:
```
GROQ_API_KEY=gsk_your_actual_api_key_here
```

2. Install python-dotenv:
```bash
pip install python-dotenv
```

3. Add to top of `backend.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

**Option C: Direct in Code (Quick Testing)**

Edit `backend.py` line 45:
```python
groq_api_key = "gsk_your_actual_api_key_here"
```

### 5. Run the Application

**Terminal 1 - Start Backend:**
```bash
python backend.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Start Frontend:**
```bash
streamlit run frontend.py
```

Your browser will open automatically at `http://localhost:8501`

## 📖 How to Use

### Managing Chat Sessions

1. **Create New Chat**
   - Click the "➕ New Chat" button at the top of sidebar
   - New empty chat session created
   - Previous chats saved automatically

2. **Switch Between Chats**
   - Click any chat title in the sidebar
   - Chat loads instantly with full history
   - Current chat highlighted with ▶️

3. **Delete Chats**
   - Click the 🗑️ button next to any chat
   - Chat permanently removed
   - Auto-creates new chat if you delete current one

4. **View Chat Details**
   - Each chat shows its title and message count
   - Sorted by most recent activity

### Chatting with Documents

1. **Upload Document**
   - Click "Browse files" in the sidebar
   - Select a PDF or DOCX file
   - Click "Process Document"
   - Wait for confirmation

2. **Choose Mode**
   - **Document Only**: AI answers only from your document
   - **Hybrid**: AI uses document + its general knowledge

3. **Start Chatting**
   - Type your question in the chat input
   - Press Enter
   - Get instant answers!
   - First message becomes chat title automatically

## 🗂️ Project Structure

```
rag-chatbot/
├── backend.py              # FastAPI backend server
├── frontend.py             # Streamlit frontend UI with chat history
├── requirements.txt        # Python dependencies
├── chat_sessions.json      # Auto-created: Stores all chat sessions
├── README.md              # This file
└── .env                   # API keys (create this)
```

### chat_sessions.json Format

```json
{
  "session-id-1": {
    "title": "What is machine learning?",
    "messages": [
      {"role": "user", "content": "What is machine learning?"},
      {"role": "assistant", "content": "Machine learning is...", "mode": "hybrid"}
    ],
    "created_at": "2024-01-18T10:30:00",
    "last_updated": "2024-01-18T10:35:00"
  }
}
```

## 🔧 Configuration

### Change LLM Model

Edit `backend.py` line 47:
```python
model_name="llama-3.1-70b-versatile"  # Try: llama-3.3-70b-versatile, mixtral-8x7b-32768
```

### Adjust Chunk Size

Edit `backend.py` lines 73-74:
```python
chunk_size=1000,      # Larger = more context
chunk_overlap=200     # Overlap between chunks
```

### Change Retrieval Documents

Edit `backend.py` line 114:
```python
search_kwargs={"k": 3}  # Number of document chunks to retrieve
```

### Modify Chat Title Length

Edit `frontend.py` line 57:
```python
title = first_message[:50] + "..."  # Change 50 to desired length
```

## 🐛 Troubleshooting

### Error: "Invalid API Key"
- Make sure you've set the `GROQ_API_KEY` environment variable
- Verify your API key is correct and active
- Restart the backend after setting the key

### Error: "Connection error"
- Ensure backend is running on `http://localhost:8000`
- Check if port 8000 is available
- Try restarting both backend and frontend

### Error: "No document uploaded"
- Upload a document before using "Document Only" mode
- Or switch to "Hybrid" mode to chat without a document

### Chat History Not Saving
- Check if `chat_sessions.json` file is created in project folder
- Ensure you have write permissions in the directory
- Check console for any JSON serialization errors

### Chat History Not Loading
- Verify `chat_sessions.json` is valid JSON
- Delete the file to reset (backup first if needed)
- Restart Streamlit frontend

### FAISS Installation Issues (Windows)
```bash
# Try with no cache
pip install faiss-cpu --no-cache

# Or use conda
conda install -c conda-forge faiss-cpu
```

## 📚 API Endpoints

### POST /upload
Upload and process a document
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@document.pdf"
```

### POST /query
Ask a question
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this document about?",
    "mode": "document_only",
    "session_id": "session123"
  }'
```

### GET /history/{session_id}
Get chat history
```bash
curl "http://localhost:8000/history/session123"
```

### DELETE /session/{session_id}
Clear session
```bash
curl -X DELETE "http://localhost:8000/session/session123"
```

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **LLM**: Groq (Llama 3.1)
- **Embeddings**: HuggingFace (sentence-transformers)
- **Vector Store**: FAISS
- **Framework**: LangChain
- **Document Processing**: PyPDF, docx2txt
- **Storage**: JSON file-based persistence

## 📝 License

MIT License - feel free to use this project however you want!

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 💡 Tips

- **Chat Management**: Regularly delete old chats to keep sidebar clean
- **Document Quality**: Well-structured documents give better results
- **Mode Selection**: 
  - Use "Document Only" for factual questions about your document
  - Use "Hybrid" mode for questions needing broader context
- **Session Persistence**: All chats are saved automatically - no need to manually save
- **Chat Titles**: First message becomes title - make it descriptive!
- **Performance**: Documents are stored in memory (restart clears them)
- **Backup**: Periodically backup `chat_sessions.json` to save your conversations

## 🎯 Future Enhancements

- [ ] Search within chat history
- [ ] Export individual chats to PDF/TXT
- [ ] Folder organization for chats
- [ ] Multiple document support per chat
- [ ] Persistent document storage
- [ ] User authentication
- [ ] Share chats via link
- [ ] Support for more file types (TXT, CSV, etc.)
- [ ] Cloud storage integration
- [ ] Deploy to cloud (AWS, GCP, Azure)

## 📊 Chat Storage Details

### Storage Location
- All chats saved in `chat_sessions.json` in project root
- Human-readable JSON format
- Automatic backup on each save

### Data Structure
Each session contains:
- **title**: Auto-generated from first message
- **messages**: Full conversation history
- **created_at**: Session creation timestamp
- **last_updated**: Last activity timestamp

### Privacy & Security
- All data stored locally on your machine
- No cloud storage or external servers
- Delete `chat_sessions.json` to clear all history
- Backend API sessions are separate from frontend storage

## 📞 Support

If you encounter any issues:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Ensure your API key is valid
4. Check backend logs for errors
5. Verify `chat_sessions.json` is valid JSON

---

**Built with ❤️ using Streamlit, LangChain, FastAPI, and Groq**

Happy chatting with persistent history! 🚀💬
