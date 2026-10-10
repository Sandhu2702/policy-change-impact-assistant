import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parents[2] / "policy_assistant.db"


def get_connection():
    """Create and return a connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection