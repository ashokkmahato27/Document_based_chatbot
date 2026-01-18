from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
import json

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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage
vectorstore = None
chat_history = []
sessions = {}

# Models
class QueryRequest(BaseModel):
    question: str
    mode: str  # "document_only" or "hybrid"
    session_id: str

class ChatResponse(BaseModel):
    answer: str
    session_id: str

# Initialize Groq LLM
def get_llm():
    # Replace with your Groq API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    return ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama-3.1-8b-instant",
        temperature=0.7
    )

# Initialize embeddings
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    global vectorstore
    
    try:
        # Save uploaded file temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Load document based on file type
        if file.filename.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file.filename.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
        else:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        documents = loader.load()
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)
        
        # Create vector store
        embeddings = get_embeddings()
        vectorstore = FAISS.from_documents(chunks, embeddings)
        
        # Clean up
        os.remove(file_path)
        
        return {"message": "Document uploaded and processed successfully", "chunks": len(chunks)}
    
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=ChatResponse)
async def query_chatbot(request: QueryRequest):
    global vectorstore, sessions
    
    try:
        llm = get_llm()
        
        # Get or create session
        if request.session_id not in sessions:
            sessions[request.session_id] = {
                "history": [],
                "memory": ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True,
                    output_key="answer"
                )
            }
        
        session = sessions[request.session_id]
        
        if request.mode == "document_only":
            if vectorstore is None:
                raise HTTPException(status_code=400, detail="No document uploaded")
            
            # Document-only mode with retrieval
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=retriever,
                memory=session["memory"],
                return_source_documents=False
            )
            
            response = chain({"question": request.question})
            answer = response["answer"]
        
        else:  # hybrid mode
            if vectorstore is not None:
                # Hybrid: Get context from document + general knowledge
                retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
                docs = retriever.get_relevant_documents(request.question)
                context = "\n".join([doc.page_content for doc in docs])
                
                prompt = f"""Context from document: {context}
                
Question: {request.question}

Please answer using both the document context and your general knowledge."""
            else:
                prompt = request.question
            
            # Get chat history
            history_text = "\n".join([f"Human: {h['question']}\nAI: {h['answer']}" 
                                     for h in session["history"][-3:]])
            
            if history_text:
                full_prompt = f"Previous conversation:\n{history_text}\n\n{prompt}"
            else:
                full_prompt = prompt
            
            response = llm.invoke(full_prompt)
            answer = response.content
        
        # Store in session history
        session["history"].append({
            "question": request.question,
            "answer": answer,
            "timestamp": datetime.now().isoformat(),
            "mode": request.mode
        })
        
        return ChatResponse(answer=answer, session_id=request.session_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    if session_id not in sessions:
        return {"history": []}
    return {"history": sessions[session_id]["history"]}

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"message": "Session cleared"}

@app.get("/")
async def root():
    return {"message": "RAG Chatbot API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)