from app.data.policy_sections import extract_policy_sections


def test_extract_policy_sections_ignores_metadata_and_extracts_content():
    text = """Policy: Annual Leave Policy
Version: v1
Effective Date: 2025-01-01

1. Annual Leave Entitlement
Full-time employees are entitled to 20 days of annual leave per calendar year.

2. Leave Approval
Employees must obtain manager approval before taking annual leave.
"""

    sections = extract_policy_sections(text)

    assert len(sections) == 2
    assert sections["Annual Leave Entitlement"] == (
        "Full-time employees are entitled to 20 days of annual leave per calendar year."
    )
    assert sections["Leave Approval"] == (
        "Employees must obtain manager approval before taking annual leave."
    )


def test_extract_policy_sections_handles_text_without_numbered_headings():
    text = """Policy: Annual Leave Policy
Version: v1
Effective Date: 2025-01-01
"""