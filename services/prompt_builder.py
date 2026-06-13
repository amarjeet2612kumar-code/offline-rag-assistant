SYSTEM_PROMPT = """
Format answers using markdown.
Use headings, bullets and tables when useful.
"""

SYSTEM_PROMPT_WITH_CONTEXT = """
You are a helpful assistant. Answer the question using the provided context.
If the answer is not in the context, say so and answer from your general knowledge.
Format answers using markdown. Use headings, bullets and tables when useful.
"""


def build_prompt(
    history: list[dict],
    question: str,
    context: list[str] = None
) -> list[dict]:
    """
    Build the full messages list to send to the LLM.

    If context chunks are provided (RAG), inject them into the system prompt.
    Otherwise fall back to plain conversation mode.
    """

    if context:
        context_text = "\n\n".join(context)
        system_content = (
            SYSTEM_PROMPT_WITH_CONTEXT.strip()
            + f"\n\n### Relevant Context:\n{context_text}"
        )
    else:
        system_content = SYSTEM_PROMPT.strip()

    messages = [
        {
            "role": "system",
            "content": system_content
        }
    ]

    messages.extend(history)

    messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    return messages
