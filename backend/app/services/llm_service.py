import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors


ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ENV_PATH)

MODEL_NAME = "gemini-3.8-flash"
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 2


def generate_answer(prompt: str) -> str:
    """Generate text using the Gemini API with limited retries."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Check the project root .env file."
        )

    client = genai.Client(api_key=api_key)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )

            if not response.text:
                raise RuntimeError("Gemini returned an empty response.")

            return response.text.strip()

        except errors.APIError as exc:
            # Retry only temporary server-side errors.
            if exc.code not in (429, 500, 502, 503, 504):
                raise

            if attempt == MAX_ATTEMPTS:
                raise

            time.sleep(RETRY_DELAY_SECONDS * attempt)

    raise RuntimeError("Gemini could not generate an answer.")