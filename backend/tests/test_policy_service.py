import sqlite3

from app.database import operations
from app.services.policy_service import process_policy_versions


def test_process_policy_versions_detects_and_saves_changes(
    monkeypatch,
    tmp_path,
):
    database_path = tmp_path / "test_policy.db"

    def get_test_connection():
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        return connection

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

    old_file = tmp_path / "v1.txt"
    new_file = tmp_path / "v2.txt"

    old_file.write_text(
        "Policy: Annual Leave Policy\n"
        "Version: v1\n"
        "Effective Date: 2025-01-01\n\n"
        "1. Annual Leave Entitlement\n"
        "Employees get 20 days of annual leave.\n",
        encoding="utf-8",
    )

    new_file.write_text(
        "Policy: Annual Leave Policy\n"
        "Version: v2\n"
        "Effective Date: 2026-01-01\n\n"
        "1. Annual Leave Entitlement\n"
        "Employees get 24 days of annual leave.\n\n"
        "2. Leave Carryover\n"
        "Employees may carry over 5 unused days.\n",
        encoding="utf-8",
    )

    changes = process_policy_versions(
        policy_name="Annual Leave Policy",
        old_version="v1",
        new_version="v2",
        old_file_path=str(old_file),
        new_file_path=str(new_file),
    )

    assert len(changes) == 2
    assert changes[0]["change_type"] == "MODIFY"
    assert changes[1]["change_type"] == "ADD"

    connection = get_test_connection()

    try:
        versions = connection.execute(
            "SELECT * FROM policy_versions ORDER BY version"
        ).fetchall()

        saved_changes = connection.execute(
            "SELECT * FROM policy_changes ORDER BY id"
        ).fetchall()
    finally:
        connection.close()

    assert len(versions) == 2
    assert versions[0]["effective_date"] == "2025-01-01"
    assert versions[1]["effective_date"] == "2026-01-01"
    assert len(saved_changes) == 2


def test_existing_version_is_reused_when_saving_comparison(
    monkeypatch,
    tmp_path,
):
    from app.database import operations
    from app.database.operations import save_policy_comparison

    database_path = tmp_path / "duplicate_test.db"

    def get_test_connection():
        connection = sqlite3.connect(database_path)
        connection.row_factory = sqlite3.Row
        return connection

    monkeypatch.setattr(
        operations,
        "get_connection",
        get_test_connection,
    )

    connection = get_test_connection()
    connection.executescript("""
        CREATE TABLE policy_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_name TEXT NOT NULL,
            version TEXT NOT NULL,
            effective_date TEXT,
            file_path TEXT NOT NULL,
            UNIQUE(policy_name, version)
        );

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
        );

        INSERT INTO policy_versions (
            policy_name, version, effective_date, file_path
        )
        VALUES (
            'Annual Leave Policy', 'v1', '2025-01-01', 'v1.txt'
        );
    """)
    connection.close()

    saved_count = save_policy_comparison(
        policy_name="Annual Leave Policy",
        old_version="v1",
        old_file_path="v1.txt",
        old_effective_date="2025-01-01",
        new_version="v2",
        new_file_path="v2.txt",
        new_effective_date="2026-01-01",
        changes=[
            {
                "section": "Leave Carryover",
                "change_type": "ADD",
                "old_text": "",
                "new_text": "Carry over 5 days.",
            }
        ],
    )

    assert saved_count == 1

    connection = get_test_connection()
    try:
        versions = connection.execute(
            "SELECT version FROM policy_versions ORDER BY version"
        ).fetchall()

        changes = connection.execute(
            "SELECT * FROM policy_changes"
        ).fetchall()
    finally:
        connection.close()

    assert [row["version"] for row in versions] == ["v1", "v2"]
    assert len(changes) == 1
    assert changes[0]["section"] == "Leave Carryover"