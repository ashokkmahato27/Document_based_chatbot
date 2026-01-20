from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import os, uuid

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# ---------------- SESSION STORE ----------------
sessions = {}  # session_id → memory, vectorstore, history

# ---------------- MODELS ----------------
class QueryRequest(BaseModel):
    question: str
    session_id: str
    mode: str = "document_only"

class ChatResponse(BaseModel):
    answer: str
    session_id: str

# ---------------- HELPERS ----------------
def get_llm():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY missing")
    return ChatGroq(
        groq_api_key=key,
        model_name="llama-3.1-8b-instant",
        temperature=0.6,
    )

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

def load_docs(path):
    ext = path.lower()
    if ext.endswith(".pdf"):
        return PyPDFLoader(path).load()
    if ext.endswith(".docx"):
        return Docx2txtLoader(path).load()
    raise HTTPException(400, "Unsupported file type")

def get_session(session_id: str):
    if session_id not in sessions:
        sessions[session_id] = {
            "memory": ConversationBufferMemory(memory_key="chat_history", return_messages=True),
            "vectorstore": None,
            "history": []
        }
    return sessions[session_id]

# ---------------- UPLOAD DOCUMENT ----------------
@app.post("/upload")
async def upload_document(session_id: str, file: UploadFile = File(...)):
    session = get_session(session_id)

    ext = file.filename.lower()
    if not (ext.endswith(".pdf") or ext.endswith(".docx")):
        raise HTTPException(400, "Only PDF or DOCX supported")

    temp_path = f"tmp_{uuid.uuid4()}_{file.filename}"
    try:
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        docs = load_docs(temp_path)
        if not docs:
            raise HTTPException(400, "Document has no readable text")

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        if not chunks:
            raise HTTPException(400, "Document cannot be split into chunks")

        session["vectorstore"] = FAISS.from_documents(chunks, get_embeddings())
        return {"message": "Document uploaded successfully", "chunks": len(chunks)}

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# ---------------- QUERY ----------------
@app.post("/query", response_model=ChatResponse)
async def query(req: QueryRequest):
    session = get_session(req.session_id)
    question = req.question.strip()
    if not question:
        raise HTTPException(400, "Empty question not allowed")

    llm = get_llm()

    if req.mode == "document_only":
        if not session["vectorstore"]:
            raise HTTPException(400, "No document uploaded for this session")
        retriever = session["vectorstore"].as_retriever(search_kwargs={"k": 3})
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=session["memory"],
            return_source_documents=False
        )
        result = chain({"question": question})
        answer = result["answer"]
    else:
        memory_text = "\n".join(
            [f"Human: {m['question']}\nAI: {m['answer']}" for m in session["history"][-5:]]
        )
        prompt = f"{memory_text}\nHuman: {question}" if memory_text else question
        answer = llm.invoke(prompt).content

    # Save history
    session["history"].append({
        "question": question,
        "answer": answer,
        "time": datetime.utcnow().isoformat(),
        "mode": req.mode
    })

    return ChatResponse(answer=answer, session_id=req.session_id)

# ---------------- HISTORY ----------------
@app.get("/history/{session_id}")
def history(session_id: str):
    session = get_session(session_id)
    return session["history"]

# ---------------- DELETE SESSION ----------------
@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    sessions.pop(session_id, None)
    return {"message": "Session deleted"}

# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "Backend running"}

# ---------------- RUN ----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)
