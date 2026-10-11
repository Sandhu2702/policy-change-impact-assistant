import sqlite3

from fastapi.testclient import TestClient

from app.database import operations
from app.main import app


def test_get_policy_changes_returns_saved_changes(
    monkeypatch,
    tmp_path,
):
    database_path = tmp_path / "test_policy_api.db"

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

        INSERT INTO policy_changes (
            policy_name, section, change_type,
            old_text, new_text, old_version, new_version
        )
        VALUES (
            'Annual Leave Policy',
            'Annual Leave Entitlement',
            'MODIFY',
            'Employees get 20 days.',
            'Employees get 24 days.',
            'v1',
            'v2'
        );
    """)

    connection.commit()
    connection.close()

    client = TestClient(app)

    response = client.get(
        "/policies/Annual Leave Policy/changes",
        params={
            "old_version": "v1",
            "new_version": "v2",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["policy_name"] == "Annual Leave Policy"
    assert data["count"] == 1
    assert data["changes"][0]["change_type"] == "MODIFY"
    assert data["changes"][0]["old_text"] == "Employees get 20 days."
    assert data["changes"][0]["new_text"] == "Employees get 24 days."