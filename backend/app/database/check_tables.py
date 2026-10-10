from app.database.connection import get_connection


def check_tables():
    connection = get_connection()

    try:
        query = """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
        """

        tables = connection.execute(query).fetchall()

        print("Tables found in database:")
        for table in tables:
            print(table["name"])

    finally:
        connection.close()


if __name__ == "__main__":
    check_tables()