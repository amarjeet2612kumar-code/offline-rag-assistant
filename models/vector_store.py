import chromadb
import ollama

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "documents"
EMBED_MODEL = "nomic-embed-text"

# Persistent ChromaDB client
_client = chromadb.PersistentClient(path=CHROMA_PATH)


def get_collection():
    return _client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


def embed(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using Ollama nomic-embed-text."""
    embeddings = []
    for text in texts:
        response = ollama.embed(
            model=EMBED_MODEL,
            input=text
        )
        embeddings.append(response["embeddings"][0])
    return embeddings


def add_documents(
    doc_id: str,
    chunks: list[str],
    metadatas: list[dict]
):
    """Embed and store document chunks in ChromaDB."""
    collection = get_collection()

    embeddings = embed(chunks)

    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )


def search(query: str, n_results: int = 4) -> list[str]:
    """Semantic search — returns top matching text chunks."""
    collection = get_collection()

    if collection.count() == 0:
        return []

    query_embedding = embed([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count())
    )

    return results["documents"][0]


def list_documents() -> list[str]:
    """Return unique document source names stored in the collection."""
    collection = get_collection()

    if collection.count() == 0:
        return []

    results = collection.get(include=["metadatas"])

    sources = set()
    for meta in results["metadatas"]:
        if "source" in meta:
            sources.add(meta["source"])

    return list(sources)


def get_chunks_by_source(source: str) -> list[dict]:
    """Return all stored chunks for a given document source."""
    collection = get_collection()

    if collection.count() == 0:
        return []

    results = collection.get(
        where={"source": source},
        include=["documents", "metadatas"]
    )

    chunks = []
    for i, doc in enumerate(results["documents"]):
        chunks.append({
            "id": results["ids"][i],
            "text": doc,
            "source": results["metadatas"][i].get("source", "")
        })

    return chunks


def delete_document(source: str) -> int:
    """Delete all chunks for a given document source. Returns count deleted."""
    collection = get_collection()

    if collection.count() == 0:
        return 0

    results = collection.get(
        where={"source": source},
        include=["metadatas"]
    )

    ids = results["ids"]
    if ids:
        collection.delete(ids=ids)

    return len(ids)
