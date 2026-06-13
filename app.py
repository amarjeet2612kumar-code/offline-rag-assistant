from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os

from models.database import create_tables
from services.chat_service import (
    new_chat,
    list_chats,
    load_messages,
    process_chat
)
from services.ingestor import ingest_file
from models.vector_store import list_documents, get_chunks_by_source, delete_document

app = FastAPI()

# Create tables at startup
create_tables()

# Static files
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

# Templates
templates = Jinja2Templates(
    directory="templates"
)

# ---------------------------
# Home Page
# ---------------------------

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# ---------------------------
# Upload Document (RAG)
# ---------------------------

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        upload_path = f"uploads/{file.filename}"
        with open(upload_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        chunk_count = ingest_file(upload_path)

        return JSONResponse({
            "message": f"Ingested '{file.filename}' into {chunk_count} chunks."
        })

    except Exception as e:
        return JSONResponse(
            {"message": f"Error: {str(e)}"},
            status_code=500
        )


# ---------------------------
# List Ingested Documents
# ---------------------------

@app.get("/documents")
async def documents():
    docs = list_documents()
    return {"documents": docs}


# ---------------------------
# View Chunks for a Document
# ---------------------------

@app.get("/documents/{source}")
async def document_chunks(source: str):
    chunks = get_chunks_by_source(source)
    return {
        "source": source,
        "chunk_count": len(chunks),
        "chunks": chunks
    }


# ---------------------------
# Delete a Document from RAG
# ---------------------------

@app.delete("/documents/{source}")
async def remove_document(source: str):
    count = delete_document(source)
    return {"message": f"Deleted {count} chunks for '{source}'"}


# ---------------------------
# Delete Session
# ---------------------------

@app.delete("/session/{session_id}")
async def delete_session(session_id: int):
    from services.chat_service import remove_chat
    remove_chat(session_id)
    return {"status": "deleted"}


# ---------------------------
# Create New Chat Session
# ---------------------------

@app.post("/session")
async def create_session():
    session_id = new_chat("New Chat")
    return {"session_id": session_id}


# ---------------------------
# List Sessions
# ---------------------------

@app.get("/sessions")
async def sessions():

    rows = list_chats()

    return [
        {
            "id": row[0],
            "title": row[1],
            "created_at": row[2]
        }
        for row in rows
    ]


# ---------------------------
# Load Messages
# ---------------------------

@app.get("/messages/{session_id}")
async def messages(session_id: int):

    rows = load_messages(session_id)

    return [
        {
            "role": row[0],
            "content": row[1],
            "created_at": row[2]
        }
        for row in rows
    ]


# ---------------------------
# Chat Endpoint
# ---------------------------

@app.post("/chat")
async def chat(request: Request):

    try:

        data = await request.json()

        session_id = data.get("session_id")
        question = data.get("question", "")

        if not question:
            return JSONResponse(
                {"answer": "Please enter a question."}
            )

        # Full pipeline: retrieve → build → llm → save
        answer, title = process_chat(session_id, question)

        return JSONResponse({
            "answer": answer,
            "title": title
        })

    except Exception as e:

        return JSONResponse(
            {"answer": f"Error: {str(e)}"},
            status_code=500
        )
