from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from groq import Groq
from rag import vector_store, DocumentProcessor
import hashlib

app = FastAPI(title="RAG Chatbot API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    api_key: Optional[str] = None
    provider: str = "groq"  # groq, openrouter, local
    model: str = "llama-3.3-70b-versatile"

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]

@app.get("/")
def read_root():
    return {"status": "ok", "message": "RAG Chatbot API is running"}

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        content = await file.read()
        file_hash = hashlib.md5(content).hexdigest()
        
        # Process file even if hash exists (in case vector store was cleared)
        text = DocumentProcessor.process_file(file.filename, content)
        if text.startswith("Error") or text.startswith("Unsupported"):
            results.append({"filename": file.filename, "status": "error", "message": text})
        else:
            # Check if already in vector store, if so skip
            if file_hash in vector_store.documents:
                results.append({"filename": file.filename, "status": "already_exists"})
            else:
                vector_store.add_document(file_hash, file.filename, text)
                results.append({"filename": file.filename, "status": "processed"})
            
    return {"results": results}

@app.post("/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    # Use API key from request or environment variable
    api_key = request.api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="Groq API key is required")
    
    # 1. Search for context from uploaded documents
    results = vector_store.search(request.query, top_k=5)
    
    # 2. Prepare context text
    context_text = "\n\n".join([f"Source: {item['filename']}\nContent: {item['content']}" for item in results])
    
    # 3. Generate response using LLM
    if context_text:
        system_prompt = "You are a helpful AI assistant. Use the provided context from uploaded documents to answer the user's question. If the answer is not in the context, say so."
        user_prompt = f"Context from documents:\n{context_text}\n\nQuestion: {request.query}"
    else:
        system_prompt = "You are a helpful AI assistant. The user hasn't uploaded any documents yet, so answer their question directly."
        user_prompt = request.query
    
    answer = ""
    
    try:
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=request.model,
        )
        answer = chat_completion.choices[0].message.content
            
    except Exception as e:
        answer = f"Error generating response: {str(e)}"

    return QueryResponse(answer=answer, sources=results)

@app.get("/documents")
def get_documents():
    docs = vector_store.get_documents()
    return {
        "total_documents": len(docs),
        "total_chunks": len(vector_store.chunks),
        "documents": docs
    }

@app.delete("/clear")
def clear_documents():
    vector_store.clear()
    return {"status": "cleared"}
