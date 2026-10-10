from app.database.connection import get_connection


def create_tables():
    """Create database tables if they do not already exist."""
    connection = get_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS policy_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_name TEXT NOT NULL,
                version TEXT NOT NULL,
                effective_date TEXT,
                file_path TEXT NOT NULL,
                UNIQUE(policy_name, version)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS policy_changes (
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

    finally:
        connection.close()