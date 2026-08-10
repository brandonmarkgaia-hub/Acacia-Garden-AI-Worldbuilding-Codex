import time
import os
from google.generativeai import GenerativeModel


MODEL = "models/gemini-2.0-flash"


def call(prompt: str, max_retries: int = 5) -> str:
    """
    Centralized Gemini call.
    GUARANTEES a string return (never None).
    """
    if not os.environ.get("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY not set")

    model = GenerativeModel(MODEL)

    last_error = None

    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)

            # Defensive extraction
            text = getattr(response, "text", None)

            if isinstance(text, str) and text.strip():
                return text.strip()

            # Empty or blocked response — retry
            last_error = "Empty or non-text response"
            time.sleep(2 ** attempt)

        except Exception as e:
            last_error = str(e)
            # Backoff on transient errors
            time.sleep(2 ** attempt)

    # Final fallback — never return None
    return (
        "⚠️ The Garden stirred, but no words formed.\n\n"
        f"(Central client fallback after {max_retries} attempts. "
        f"Last error: {last_error})"
    )
