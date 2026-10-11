from app.database.connection import get_connection


def save_policy_version(
    policy_name: str,
    version: str,
    file_path: str,
    effective_date: str | None = None,
) -> int:
    """Save a policy version and return its database ID."""
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO policy_versions (
                policy_name,
                version,
                effective_date,
                file_path
            )
            VALUES (?, ?, ?, ?)
            """,
            (policy_name, version, effective_date, file_path),
        )

        connection.commit()
        return cursor.lastrowid

    finally:
        connection.close()

def get_policy_versions(policy_name: str) -> list[dict]:
    """Retrieve all saved versions of a policy."""
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT id, policy_name, version, effective_date, file_path
            FROM policy_versions
            WHERE policy_name = ?
            ORDER BY version
            """,
            (policy_name,),
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()

def save_policy_changes(
    policy_name: str,
    changes: list[dict[str, str]],
    old_version: str,
    new_version: str,
) -> int:
    """Save detected policy changes and return the number saved."""
    connection = get_connection()

    try:
        connection.executemany(
            """
            INSERT INTO policy_changes (
                policy_name,
                section,
                change_type,
                old_text,
                new_text,
                old_version,
                new_version
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    policy_name,
                    change["section"],
                    change["change_type"],
                    change["old_text"],
                    change["new_text"],
                    old_version,
                    new_version,
                )
                for change in changes
            ],
        )

        connection.commit()
        return len(changes)

    finally:
        connection.close()

def get_policy_changes(
    policy_name: str,
    old_version: str | None = None,
    new_version: str | None = None,
) -> list[dict]:
    """Retrieve saved changes for a policy, optionally filtered by versions."""
    connection = get_connection()

    try:
        query = """
            SELECT
                id,
                policy_name,
                section,
                change_type,
                old_text,
                new_text,
                old_version,
                new_version
            FROM policy_changes
            WHERE policy_name = ?
        """
        parameters = [policy_name]

        if old_version is not None:
            query += " AND old_version = ?"
            parameters.append(old_version)

        if new_version is not None:
            query += " AND new_version = ?"
            parameters.append(new_version)

        query += " ORDER BY id"

        rows = connection.execute(query, parameters).fetchall()
        return [dict(row) for row in rows]

    finally:
        connection.close()

def save_policy_comparison(
    policy_name: str,
    old_version: str,
    old_file_path: str,
    old_effective_date: str | None,
    new_version: str,
    new_file_path: str,
    new_effective_date: str | None,
    changes: list[dict[str, str]],
) -> int:
    """Save both policy versions and their changes atomically."""
    connection = get_connection()

    try:
        with connection:
            connection.execute(
                """
                INSERT INTO policy_versions (
                    policy_name, version, effective_date, file_path
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    policy_name,
                    old_version,
                    old_effective_date,
                    old_file_path,
                ),
            )

            connection.execute(
                """
                INSERT INTO policy_versions (
                    policy_name, version, effective_date, file_path
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    policy_name,
                    new_version,
                    new_effective_date,
                    new_file_path,
                ),
            )

            connection.executemany(
                """
                INSERT INTO policy_changes (
                    policy_name, section, change_type,
                    old_text, new_text, old_version, new_version
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        policy_name,
                        change["section"],
                        change["change_type"],
                        change["old_text"],
                        change["new_text"],
                        old_version,
                        new_version,
                    )
                    for change in changes
                ],
            )

        return len(changes)

    finally:
        connection.close()