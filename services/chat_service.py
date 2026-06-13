import opik
from opik import track

from models.database import (
    create_session,
    get_sessions,
    save_message,
    get_messages,
    delete_session,
    get_session,
    update_session_title
)

from services.retriever import retrieve_history, retrieve_context
from services.prompt_builder import build_prompt
from services.llm import ask_llm


# ---------------------------
# Session Operations
# ---------------------------

def new_chat(title="New Chat"):
    return create_session(title)


def list_chats():
    return get_sessions()


def get_chat(session_id):
    return get_session(session_id)


def remove_chat(session_id):
    delete_session(session_id)


# ---------------------------
# Message Operations
# ---------------------------

def add_message(session_id, role, content):
    save_message(session_id, role, content)


def load_messages(session_id):
    return get_messages(session_id)


# ---------------------------
# Core Chat Pipeline
# ---------------------------

@track(project_name="local-ai-assistant", name="process_chat")
def process_chat(session_id: int, question: str):
    """
    Full RAG pipeline tracked end-to-end in Opik:
      1. retrieve_history  — chat memory from SQLite
      2. retrieve_context  — semantic search from ChromaDB (RAG)
      3. build_prompt      — assemble messages list
      4. ask_llm           — call Ollama (tracked as child span)
      5. persist           — save to DB + update session title
    """

    # Step 1: Chat history
    history = _retrieve_history_span(session_id)

    # Step 2: RAG context retrieval
    context = _retrieve_context_span(question)

    # Step 3: Build prompt
    messages = _build_prompt_span(history, question, context)

    # Step 4: LLM call (tracked inside ask_llm via its own @track)
    answer = ask_llm(messages)

    # Step 5: Persist
    add_message(session_id, "user", question)
    add_message(session_id, "assistant", answer)

    # Update session title on first message
    if len(history) == 0:
        title = question[:60]
        update_session_title(session_id, title)
    else:
        session = get_session(session_id)
        title = session[1] if session else question[:60]

    return answer, title


# ---------------------------
# Tracked sub-steps for Opik
# ---------------------------

@track(project_name="local-ai-assistant", name="retrieve_history")
def _retrieve_history_span(session_id: int):
    return retrieve_history(session_id)


@track(project_name="local-ai-assistant", name="retrieve_context")
def _retrieve_context_span(question: str):
    context = retrieve_context(question)
    return context


@track(project_name="local-ai-assistant", name="build_prompt")
def _build_prompt_span(history, question, context):
    return build_prompt(history, question, context=context)
