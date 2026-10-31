
from backend.database import get_connection


def track_service(identifier):
    identifier = identifier.strip()

    with get_connection() as connection:
        record = connection.execute(
            """
            SELECT *
            FROM service_requests
            WHERE service_id = ? OR case_id = ?
            """,
            (identifier, identifier),
        ).fetchone()

    if record is None:
        return None

    return dict(record)


if __name__ == "__main__":
    search_id = input("Enter Service ID or Case ID: ")
    result = track_service(search_id)

    if result:
        for field, value in result.items():
            print(f"{field}: {value}")
    else:
        print("No matching service request was found.")
