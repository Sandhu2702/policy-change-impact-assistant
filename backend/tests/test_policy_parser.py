from pathlib import Path

import pytest

from app.data.policy_parser import (
    read_policy_file,
    clean_policy_text,
    load_policy_versions,
)


def test_clean_policy_text_removes_blank_lines_and_extra_spaces():
    text = "  Annual Leave Policy  \n\n  Employees get 20 days.  \n"

    result = clean_policy_text(text)

    assert result == "Annual Leave Policy\nEmployees get 20 days."


def test_read_policy_file_reads_text(tmp_path: Path):
    policy_file = tmp_path / "policy.txt"
    policy_file.write_text("Sample policy content", encoding="utf-8")

    result = read_policy_file(str(policy_file))

    assert result == "Sample policy content"


def test_read_policy_file_raises_error_for_missing_file(tmp_path: Path):
    missing_file = tmp_path / "missing.txt"

    with pytest.raises(FileNotFoundError):
        read_policy_file(str(missing_file))


def test_load_policy_versions_reads_actual_leave_policies():
    project_root = Path(__file__).resolve().parents[1]
    policy_folder = project_root / "data" / "policies" / "leave"

    versions = load_policy_versions(str(policy_folder))

    assert "v1" in versions
    assert "v2" in versions
    assert "20 days" in versions["v1"]
    assert "24 days" in versions["v2"]