# Offline RAG Assistant

A fully local AI assistant with Retrieval-Augmented Generation (RAG), built with FastAPI, Ollama, and ChromaDB. No data leaves your machine.

## Features

- 💬 Chat with an LLM running locally via Ollama
- 📄 Upload PDF/TXT files and ask questions about them (RAG)
- 🧠 Semantic search using ChromaDB + nomic-embed-text embeddings
- 🗂️ Persistent chat sessions with history (SQLite)
- 📊 Observability via Opik tracing
- 🎨 Modern frosted-glass UI

## Tech Stack

| Layer | Tool |
|---|---|
| Backend | FastAPI |
| LLM | Ollama (qwen2.5:7b) |
| Embeddings | nomic-embed-text (via Ollama) |
| Vector DB | ChromaDB |
| Chat History | SQLite |
| Observability | Opik |

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/amarjeet2612kumar-code/offline-rag-assistant.git
cd offline-rag-assistant

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install fastapi uvicorn chromadb ollama python-multipart jinja2 pypdf opik python-dotenv

# 4. Pull required Ollama models
ollama pull qwen2.5:7b
ollama pull nomic-embed-text

# 5. Add your Opik API key (optional)
echo "OPIK_API_KEY=your_key_here" > .env

# 6. Run the app
uvicorn app:app --reload
```

Open `http://localhost:8000` in your browser.

## Project Structure

```
├── app.py                  # FastAPI routes
├── models/
│   ├── database.py         # SQLite (chat sessions + history)
│   └── vector_store.py     # ChromaDB (document chunks)
├── services/
│   ├── chat_service.py     # Main pipeline orchestrator
│   ├── ingestor.py         # PDF/TXT → chunks → embeddings
│   ├── retriever.py        # Semantic search
│   ├── prompt_builder.py   # Build LLM prompt with context
│   └── llm.py              # Ollama LLM call
├── static/
│   ├── css/style.css
│   └── js/script.js
└── templates/
    └── index.html
```
