
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "mobile_servicing.db"


def get_connection(db_path=None):
    if db_path is None:
        db_path = DATABASE_PATH

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row

    return connection


def create_table(db_path=None):
    with get_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS service_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id TEXT UNIQUE NOT NULL,
                case_id TEXT UNIQUE NOT NULL,
                device_model TEXT NOT NULL,
                issue_description TEXT NOT NULL,
                current_status TEXT NOT NULL,
                received_date TEXT NOT NULL
            )
            """
        )
        
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS service_status_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id TEXT NOT NULL,
                old_status TEXT,
                new_status TEXT NOT NULL,
                changed_at TEXT NOT NULL
            )
            """
        )

        


if __name__ == "__main__":
    create_table()
    print("Database and service_requests table are ready.")
