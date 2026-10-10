import sqlite3

import pytest

from app.database.operations import (
    save_policy_version,
    get_policy_versions,
    save_policy_changes,
    get_policy_changes,
)


@pytest.fixture
def test_database(monkeypatch, tmp_path):
    """Create an isolated temporary database for each test."""
    database_path = tmp_path / "test_policy.db"

    def get_test_connection():
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        return connection

    from app.database import operations

    monkeypatch.setattr(
        operations,
        "get_connection",
        get_test_connection,
    )

    connection = get_test_connection()

    connection.execute("""
        CREATE TABLE policy_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_name TEXT NOT NULL,
            version TEXT NOT NULL,
            effective_date TEXT,
            file_path TEXT NOT NULL,
            UNIQUE(policy_name, version)
        )
    """)

    # NEW TABLE: policy changes
    connection.execute("""
        CREATE TABLE policy_changes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_name TEXT NOT NULL,
            section TEXT NOT NULL,
            change_type TEXT NOT NULL
                CHECK(change_type IN ('ADD', 'MODIFY', 'REMOVE')),
            old_text TEXT NOT NULL DEFAULT '',
            new_text TEXT NOT NULL DEFAULT '',
            old_version TEXT NOT NULL,
            new_version TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def test_save_policy_version_returns_id(test_database):
    record_id = save_policy_version(
        "Annual Leave Policy",
        "v1",
        "data/policies/leave/v1.txt",
        "2025-01-01",
    )

    assert record_id == 1


def test_get_policy_versions_returns_saved_record(test_database):
    save_policy_version(
        "Annual Leave Policy",
        "v1",
        "data/policies/leave/v1.txt",
        "2025-01-01",
    )

    versions = get_policy_versions("Annual Leave Policy")

    assert len(versions) == 1
    assert versions[0]["policy_name"] == "Annual Leave Policy"
    assert versions[0]["version"] == "v1"
    assert versions[0]["effective_date"] == "2025-01-01"


def test_duplicate_policy_version_is_rejected(test_database):
    save_policy_version(
        "Annual Leave Policy",
        "v1",
        "data/policies/leave/v1.txt",
        "2025-01-01",
    )

    with pytest.raises(sqlite3.IntegrityError):
        save_policy_version(
            "Annual Leave Policy",
            "v1",
            "data/policies/leave/v1.txt",
            "2025-01-01",
        )

def test_save_policy_changes_stores_multiple_changes(test_database):
    changes = [
        {
            "section": "Annual Leave Entitlement",
            "change_type": "MODIFY",
            "old_text": "Employees get 20 days.",
            "new_text": "Employees get 24 days.",
        },
        {
            "section": "Leave Carryover",
            "change_type": "ADD",
            "old_text": "",
            "new_text": "Employees may carry over 5 unused days.",
        },
    ]

    saved_count = save_policy_changes(
        policy_name="Annual Leave Policy",
        changes=changes,
        old_version="v1",
        new_version="v2",
    )

    assert saved_count == 2

def test_get_policy_changes_returns_saved_changes(test_database):
    changes = [
        {
            "section": "Annual Leave Entitlement",
            "change_type": "MODIFY",
            "old_text": "Employees get 20 days.",
            "new_text": "Employees get 24 days.",
        },
        {
            "section": "Leave Carryover",
            "change_type": "ADD",
            "old_text": "",
            "new_text": "Employees may carry over 5 unused days.",
        },
    ]

    save_policy_changes(
        policy_name="Annual Leave Policy",
        changes=changes,
        old_version="v1",
        new_version="v2",
    )

    saved_changes = get_policy_changes(
        policy_name="Annual Leave Policy",
        old_version="v1",
        new_version="v2",
    )

    assert len(saved_changes) == 2
    assert saved_changes[0]["change_type"] == "MODIFY"
    assert saved_changes[0]["old_text"] == "Employees get 20 days."
    assert saved_changes[0]["new_text"] == "Employees get 24 days."
    assert saved_changes[1]["change_type"] == "ADD"
    assert saved_changes[1]["new_version"] == "v2"