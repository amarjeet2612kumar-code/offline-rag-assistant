import os
import fitz  # pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models.vector_store import add_documents


CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def extract_text(file_path: str) -> str:
    """Extract raw text from PDF or TXT file."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text

    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    else:
        raise ValueError(f"Unsupported file type: {ext}")


def ingest_file(file_path: str) -> int:
    """
    Full ingestion pipeline:
      1. Extract text from file
      2. Split into chunks
      3. Embed and store in ChromaDB

    Returns the number of chunks stored.
    """
    filename = os.path.basename(file_path)

    # Step 1: Extract
    text = extract_text(file_path)

    # Step 2: Chunk
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_text(text)

    if not chunks:
        return 0

    # Step 3: Store
    metadatas = [{"source": filename} for _ in chunks]

    doc_id = filename.replace(".", "_")

    add_documents(doc_id, chunks, metadatas)

    return len(chunks)
