import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ENV_PATH)

MODEL_NAME = "gemini-3.8-flash"


def generate_answer(prompt: str) -> str:
    """Generate text using the Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Check the project root .env file."
        )

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text.strip()