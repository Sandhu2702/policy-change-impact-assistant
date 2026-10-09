from pathlib import Path


def read_policy_file(file_path: str) -> str:
    """Read a policy document and return its text."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {path}")

    return path.read_text(encoding="utf-8")


def clean_policy_text(text: str) -> str:
    """Normalize whitespace in a policy document."""
    lines = [line.strip() for line in text.splitlines()]
    non_empty_lines = [line for line in lines if line]
    return "\n".join(non_empty_lines)