import os
import ollama
import opik
from dotenv import load_dotenv

load_dotenv()

opik.configure(
    use_local=False,
    api_key=os.getenv("OPIK_API_KEY")
)


@opik.track(project_name="local-ai-assistant")
def ask_llm(messages: list[dict]) -> str:
    """
    Send a fully built messages list to the LLM
    and return the response text.
    """

    response = ollama.chat(
        model="qwen2.5:7b",
        messages=messages
    )

    return response["message"]["content"]
