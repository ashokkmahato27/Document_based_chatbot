# 🤖 RAG Document Chatbot

A powerful document-based chatbot application that allows users to upload PDF or DOCX files and ask questions about their content using Retrieval-Augmented Generation (RAG). Built with Streamlit, FastAPI, LangChain, and FAISS.

## ✨ Features

- **Document Upload & Processing**: Support for PDF and DOCX files
- **Multi-Mode Question Answering**:
  - 📄 **Document Only**: Answers based solely on uploaded documents
  - 🌐 **Hybrid**: Combines document knowledge with general AI knowledge
  - 🧠 **Normal**: Standard conversational AI without document context
- **Session Management**: Multiple chat sessions with persistent history
- **Conversation Memory**: Maintains context across messages within a session
- **Vector Search**: Uses FAISS for efficient semantic search across document chunks
- **Modern UI**: Clean, responsive interface built with Streamlit

## 🏗️ Architecture

### Frontend (Streamlit)
- User interface for chat interactions
- Document upload functionality
- Session management and chat history
- Real-time communication with FastAPI backend

### Backend (FastAPI)
- RESTful API endpoints
- Document processing and chunking
- Vector storage with FAISS
- LLM integration via Groq
- Conversation memory management

## 📋 Prerequisites

- Python 3.8+
- Groq API key (for LLM access)
- pip package manager

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd rag-chatbot
```

### 2. Install Dependencies

```bash
pip install streamlit fastapi uvicorn python-multipart
pip install langchain langchain-community langchain-groq langchain-huggingface
pip install faiss-cpu sentence-transformers
pip install pypdf python-docx docx2txt
pip install python-dotenv pydantic
```

Or use a requirements.txt file:

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

To get a Groq API key:
1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key

## 🎮 Usage

### Starting the Application

You need to run both the backend and frontend in separate terminal windows.

#### Terminal 1 - Start the Backend

```bash
uvicorn backend:app --reload
```

The backend API will start at `http://localhost:8000`

#### Terminal 2 - Start the Frontend

```bash
streamlit run frontend.py
```

The Streamlit app will open automatically in your browser at `http://localhost:8501`

### Using the Chatbot

1. **Upload a Document**:
   - Click on the file uploader in the sidebar
   - Select a PDF or DOCX file
   - Click "Process" to upload and process the document

2. **Select Answer Mode**:
   - **Document Only**: Get answers exclusively from your uploaded document
   - **Hybrid**: Combine document context with general knowledge
   - **Normal**: Use general AI knowledge without document context

3. **Ask Questions**:
   - Type your question in the chat input at the bottom
   - Press Enter to submit
   - View the AI's response with the selected mode indicator

4. **Manage Sessions**:
   - Click "➕ New Chat" to start a fresh conversation
   - Switch between previous chats by clicking them in the sidebar
   - Delete unwanted sessions with the 🗑️ button

## 📁 Project Structure

```
rag-chatbot/
├── app.py                   # Streamlit UI application
├── backend.py               # FastAPI server
├── .env                     # Environment variables (create this)
├── chat_sessions.json       # Persistent chat history (auto-generated)
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Configuration

### Backend Configuration

Edit `backend.py` to customize:

- **LLM Model**: Change `model_name` in `get_llm()` function
- **Chunk Size**: Modify `chunk_size` and `chunk_overlap` in the splitter
- **Temperature**: Adjust LLM creativity (0.0-1.0)
- **Retrieval Results**: Change `k` value in retriever configuration

### Frontend Configuration

Edit `frontend.py` to customize:

- **API URL**: Change `API_URL` if backend runs on different host/port
- **Page Title**: Modify `st.set_page_config()` parameters
- **Session Storage**: Change `SESSIONS_FILE` path

## 🛠️ API Endpoints

### POST `/upload`
Upload and process a document for a session.

**Parameters**:
- `session_id` (query): Session identifier
- `file` (form-data): PDF or DOCX file

**Response**:
```json
{
  "message": "Document uploaded successfully",
  "chunks": 42
}
```

### POST `/query`
Ask a question to the chatbot.

**Request Body**:
```json
{
  "question": "What is the main topic?",
  "session_id": "abc-123",
  "mode": "document_only"
}
```

**Response**:
```json
{
  "answer": "The main topic is...",
  "session_id": "abc-123"
}
```

### GET `/history/{session_id}`
Retrieve conversation history for a session.

### DELETE `/session/{session_id}`
Delete a session and its data.

## 🧪 Technologies Used

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **LLM**: Groq (Llama 3.1 8B)
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)
- **Vector Store**: FAISS
- **Framework**: LangChain
- **Document Processing**: PyPDF, python-docx

## 📝 Requirements.txt

```txt
streamlit>=1.28.0
fastapi>=0.104.0
uvicorn>=0.24.0
python-multipart>=0.0.6
langchain>=0.1.0
langchain-community>=0.0.10
langchain-groq>=0.0.1
langchain-huggingface>=0.0.1
faiss-cpu>=1.7.4
sentence-transformers>=2.2.2
pypdf>=3.17.0
python-docx>=1.1.0
docx2txt>=0.8
python-dotenv>=1.0.0
pydantic>=2.5.0
```

## 🐛 Troubleshooting

### Backend won't start
- Ensure GROQ_API_KEY is set in `.env` file
- Check if port 8000 is available
- Verify all dependencies are installed

### Document upload fails
- Check file format (only PDF and DOCX supported)
- Ensure the document contains readable text
- Check backend logs for specific errors

### Connection error in frontend
- Verify backend is running on `http://localhost:8000`
- Check API_URL configuration in frontend.py
- Ensure no firewall blocking local connections

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [FastAPI](https://fastapi.tiangolo.com/)
- Uses [LangChain](https://www.langchain.com/) framework
- LLM by [Groq](https://groq.com/)
- Vector search by [FAISS](https://github.com/facebookresearch/faiss)

---

**Built with ❤️ using Streamlit • FastAPI • LangChain • FAISS**
