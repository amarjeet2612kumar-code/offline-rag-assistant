from models.database import get_messages
from models.vector_store import search


def retrieve_history(session_id: int, limit: int = 10) -> list[dict]:
    """Fetch recent messages for a session as a list of dicts."""
    rows = get_messages(session_id)
    rows = rows[-limit:]

    return [
        {"role": role, "content": content}
        for role, content, _ in rows
    ]


def retrieve_context(question: str, n_results: int = 4) -> list[str]:
    """
    Semantic search against ChromaDB vector store.
    Returns relevant document chunks for the question.
    Returns empty list if no documents have been ingested.
    """
    return search(question, n_results=n_results)
