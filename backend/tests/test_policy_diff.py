from pathlib import Path

from app.data.policy_parser import load_policy_versions
from app.diff.policy_diff import compare_rules, compare_policy_sections
from app.data.policy_sections import extract_policy_sections


def test_compare_rules_detects_added_rule():
    old_rules = ["Employees get 20 days of annual leave."]
    new_rules = [
        "Employees get 20 days of annual leave.",
        "Employees may carry over 5 unused days.",
    ]

    changes = compare_rules(old_rules, new_rules)

    assert len(changes) == 1
    assert changes[0]["change_type"] == "ADD"


def test_compare_rules_detects_removed_rule():
    old_rules = [
        "Employees get 20 days of annual leave.",
        "Manager approval is required.",
    ]
    new_rules = ["Employees get 20 days of annual leave."]

    changes = compare_rules(old_rules, new_rules)

    assert len(changes) == 1
    assert changes[0]["change_type"] == "REMOVE"


def test_compare_rules_returns_no_changes_for_identical_rules():
    rules = ["Employees get 20 days of annual leave."]

    assert compare_rules(rules, rules) == []


def test_compare_rules_detects_modified_rule():
    old_rules = ["Employees get 20 days of annual leave."]
    new_rules = ["Employees get 24 days of annual leave."]

    changes = compare_rules(old_rules, new_rules)

    assert len(changes) == 1
    assert changes[0]["change_type"] == "MODIFY"
    assert changes[0]["old_text"] == old_rules[0]
    assert changes[0]["new_text"] == new_rules[0]


def test_leave_policy_versions_detect_expected_changes():
    project_root = Path(__file__).resolve().parents[1]
    policy_folder = project_root / "data" / "policies" / "leave"

    versions = load_policy_versions(str(policy_folder))

    changes = compare_rules(
        versions["v1"].splitlines(),
        versions["v2"].splitlines(),
    )

    change_types = [change["change_type"] for change in changes]

    assert "MODIFY" in change_types
    assert "ADD" in change_types

def test_compare_policy_sections_detects_modified_section():
    old_sections = {
        "Annual Leave Entitlement": "Employees get 20 days.",
        "Leave Approval": "Manager approval is required.",
    }
    new_sections = {
        "Annual Leave Entitlement": "Employees get 24 days.",
        "Leave Approval": "Manager approval is required.",
    }

    changes = compare_policy_sections(old_sections, new_sections)

    assert len(changes) == 1
    assert changes[0]["change_type"] == "MODIFY"
    assert changes[0]["section"] == "Annual Leave Entitlement"


def test_compare_policy_sections_detects_added_section():
    old_sections = {
        "Annual Leave Entitlement": "Employees get 20 days."
    }
    new_sections = {
        "Annual Leave Entitlement": "Employees get 24 days.",
        "Leave Carryover": "Up to 5 unused days may be carried over.",
    }

    changes = compare_policy_sections(old_sections, new_sections)

    added = [c for c in changes if c["change_type"] == "ADD"]

    assert len(added) == 1
    assert added[0]["section"] == "Leave Carryover"


def test_compare_policy_sections_detects_removed_section():
    old_sections = {
        "Annual Leave Entitlement": "Employees get 20 days.",
        "Leave Approval": "Manager approval is required.",
    }
    new_sections = {
        "Annual Leave Entitlement": "Employees get 24 days."
    }

    changes = compare_policy_sections(old_sections, new_sections)

    removed = [c for c in changes if c["change_type"] == "REMOVE"]

    assert len(removed) == 1
    assert removed[0]["section"] == "Leave Approval"

def test_real_leave_policies_detect_section_changes():
    project_root = Path(__file__).resolve().parents[1]
    policy_folder = project_root / "data" / "policies" / "leave"

    versions = load_policy_versions(str(policy_folder))

    old_sections = extract_policy_sections(versions["v1"])
    new_sections = extract_policy_sections(versions["v2"])

    changes = compare_policy_sections(old_sections, new_sections)

    entitlement_changes = [
        change
        for change in changes
        if change["section"] == "Annual Leave Entitlement"
    ]
    carryover_changes = [
        change
        for change in changes
        if change["section"] == "Leave Carryover"
    ]

    assert len(entitlement_changes) == 1
    assert entitlement_changes[0]["change_type"] == "MODIFY"
    assert "20 days" in entitlement_changes[0]["old_text"]
    assert "24 days" in entitlement_changes[0]["new_text"]

    assert len(carryover_changes) == 1
    assert carryover_changes[0]["change_type"] == "ADD"