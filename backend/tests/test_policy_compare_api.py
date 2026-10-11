import sqlite3

from fastapi.testclient import TestClient

from app.database import operations
from app.main import app


def test_compare_policy_versions_api(monkeypatch, tmp_path):
    database_path = tmp_path / "compare_api.db"

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
    """)
    connection.close()

    old_file = tmp_path / "v1.txt"
    new_file = tmp_path / "v2.txt"

    old_file.write_text(
        "Effective Date: 2025-01-01\n\n"
        "1. Annual Leave\n"
        "Employees receive 20 leave days.\n",
        encoding="utf-8",
    )

    new_file.write_text(
        "Effective Date: 2026-01-01\n\n"
        "1. Annual Leave\n"
        "Employees receive 24 leave days.\n\n"
        "2. Leave Carryover\n"
        "Employees may carry over 5 days.\n",
        encoding="utf-8",
    )

    client = TestClient(app)

    response = client.post(
        "/policies/Annual Leave Policy/compare",
        params={
            "old_version": "v1",
            "new_version": "v2",
            "old_file_path": str(old_file),
            "new_file_path": str(new_file),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["policy_name"] == "Annual Leave Policy"
    assert data["old_version"] == "v1"
    assert data["new_version"] == "v2"
    assert data["count"] == 2
    assert data["changes"][0]["change_type"] == "MODIFY"
    assert data["changes"][1]["change_type"] == "ADD"