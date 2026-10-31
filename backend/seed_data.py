
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

    print("Sample service records inserted.")


if __name__ == "__main__":
    insert_sample_data()
