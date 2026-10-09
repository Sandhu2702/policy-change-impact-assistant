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

def load_policy_versions(policy_folder: str) -> dict[str, str]:
    """Load all text files from a policy folder."""
    folder = Path(policy_folder)

    if not folder.is_dir():
        raise NotADirectoryError(
            f"Policy folder not found: {folder}"
        )

    policy_versions = {}

    for file_path in sorted(folder.glob("*.txt")):
        policy_versions[file_path.stem] = clean_policy_text(
            read_policy_file(str(file_path))
        )

    return policy_versions