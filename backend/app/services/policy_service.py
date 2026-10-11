import re
from app.data.policy_parser import (
    read_policy_file,
    clean_policy_text,
)
from app.data.policy_sections import extract_policy_sections
from app.diff.policy_diff import compare_policy_sections
from app.database.operations import (
    save_policy_version,
    save_policy_changes,
)
from app.database.operations import save_policy_comparison


def extract_effective_date(text: str) -> str | None:
    """Extract the effective date from a policy document."""
    match = re.search(
        r"^Effective Date:\s*(\d{4}-\d{2}-\d{2})$",
        text,
        re.MULTILINE,
    )
    return match.group(1) if match else None

def process_policy_versions(
    policy_name: str,
    old_version: str,
    new_version: str,
    old_file_path: str,
    new_file_path: str,
) -> list[dict[str, str]]:
    """Compare two policy files and save their versions and changes."""

    old_text = clean_policy_text(read_policy_file(old_file_path))
    new_text = clean_policy_text(read_policy_file(new_file_path))

    old_sections = extract_policy_sections(old_text)
    new_sections = extract_policy_sections(new_text)

    old_effective_date = extract_effective_date(old_text)
    new_effective_date = extract_effective_date(new_text)

    changes = compare_policy_sections(old_sections, new_sections)

    save_policy_comparison(
        policy_name=policy_name,
        old_version=old_version,
        old_file_path=old_file_path,
        old_effective_date=old_effective_date,
        new_version=new_version,
        new_file_path=new_file_path,
        new_effective_date=new_effective_date,
        changes=changes,
    )

    return changes