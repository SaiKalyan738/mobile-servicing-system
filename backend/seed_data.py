
from datetime import datetime, timezone

from backend.database import get_connection, create_table


sample_services = [
    (
        "SRV-2026-00125",
        "CASE-1001",
        "Samsung Galaxy A54",
        "Display replacement",
        "Repair in Progress",
        "2026-10-15",
    ),
    (
        "SRV-2026-00126",
        "CASE-1002",
        "iPhone 14",
        "Battery replacement",
        "Diagnosis",
        "2026-10-16",
    ),
    (
        "SRV-2026-00127",
        "CASE-1003",
        "OnePlus 12",
        "Charging issue",
        "Ready for Collection",
        "2026-10-14",
    ),
]


def insert_sample_data():
    create_table()

    with get_connection() as connection:
        connection.executemany(
            """
            INSERT OR IGNORE INTO service_requests (
                service_id,
                case_id,
                device_model,
                issue_description,
                current_status,
                received_date
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            sample_services,
        )

        # Add initial history for demo services if missing.
        for service in sample_services:
            service_id = service[0]
            current_status = service[4]

            existing_history = connection.execute(
                """
                SELECT id FROM service_status_history
                WHERE service_id = ?
                LIMIT 1
                """,
                (service_id,),
            ).fetchone()

            if existing_history is None:
                connection.execute(
                    """
                    INSERT INTO service_status_history
                    (service_id, old_status, new_status, changed_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        service_id,
                        None,
                        current_status,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )

    print("Sample service records are ready.")


if __name__ == "__main__":
    insert_sample_data()
