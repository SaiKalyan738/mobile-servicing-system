from backend.database import get_connection

from backend.database import create_table

from backend.seed_data import insert_sample_data

from datetime import date
from uuid import uuid4

from pydantic import BaseModel, Field

from fastapi import FastAPI, HTTPException, Query
from backend.tracking import track_service

from datetime import datetime, timezone

app = FastAPI(
    title="Mobile Servicing API",
    description="API for tracking mobile repair requests",
    version="0.3.0",
)

create_table()
insert_sample_data()


class ServiceRequestCreate(BaseModel):
    case_id: str = Field(min_length=3, max_length=30)
    device_model: str = Field(min_length=2, max_length=100)
    issue_description: str = Field(min_length=5, max_length=500)

@app.get("/")
def home():
    return {"message": "Mobile Servicing API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/track/{identifier}")
def track_mobile_service(identifier: str):
    identifier = identifier.strip()

    if not identifier:
        raise HTTPException(
            status_code=400,
            detail="Service ID or Case ID is required.",
        )

    record = track_service(identifier)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="No matching service request was found.",
        )

    return {
        "message": "Service request found",
        "service": record,
    }


@app.get("/services")
def get_all_services(
    limit: int = Query(default=10, ge=1, le=100)
):
    with get_connection() as connection:
        records = connection.execute(
            """
            SELECT *
            FROM service_requests
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return {
        "count": len(records),
        "services": [dict(record) for record in records],
    }


@app.post("/services", status_code=201)
def create_service_request(request: ServiceRequestCreate):
    case_id = request.case_id.strip()
    device_model = request.device_model.strip()
    issue_description = request.issue_description.strip()

    if not case_id or not device_model or not issue_description:
        raise HTTPException(
            status_code=422,
            detail="All fields must contain non-whitespace text.",
        )

    service_id = (
        f"SRV-{date.today().year}-{uuid4().hex[:8].upper()}"
    )
    received_date = date.today().isoformat()

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM service_requests WHERE case_id = ?",
            (case_id,),
        ).fetchone()

        if existing:
            raise HTTPException(
                status_code=409,
                detail="A service request with this Case ID already exists.",
            )

        connection.execute(
            """
            INSERT INTO service_requests (
                service_id,
                case_id,
                device_model,
                issue_description,
                current_status,
                received_date
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                service_id,
                case_id,
                device_model,
                issue_description,
                "Received",
                received_date,
            ),
        )

        
        connection.execute(
            """
            INSERT INTO service_status_history
            (service_id, old_status, new_status, changed_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                service_id,
                None,
                "Received",
                datetime.now(timezone.utc).isoformat()
            )
        )


    return {
        "message": "Service request created successfully",
        "service": {
            "service_id": service_id,
            "case_id": case_id,
            "device_model": device_model,
            "issue_description": issue_description,
            "current_status": "Received",
            "received_date": received_date,
        },
    }


#@app.patch("/services/{service_id}/status")


# Allowed repair status transitions
STATUS_TRANSITIONS = {
    "Received": ["Diagnosis"],
    "Diagnosis": ["Repair in Progress"],
    "Repair in Progress": ["Ready for Collection"],
    "Ready for Collection": ["Collected"],
    "Collected": []
}


@app.patch("/services/{service_id}/status")
def update_service_status(
    service_id: str,
    new_status: str
):
    # Check whether the requested status exists
    if new_status not in STATUS_TRANSITIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid repair status"
        )

    with get_connection() as connection:

        # Find the service and its current status
        record = connection.execute(
            """
            SELECT current_status
            FROM service_requests
            WHERE service_id = ?
            """,
            (service_id,)
        ).fetchone()

        # Check whether the service exists
        if record is None:
            raise HTTPException(
                status_code=404,
                detail="Service request not found"
            )

        current_status = record["current_status"]

        # Check whether the transition is allowed
        allowed_statuses = STATUS_TRANSITIONS[current_status]

        if new_status not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Cannot change status from "
                    f"{current_status} to {new_status}"
                )
            )

        # Update the status only after validation
        connection.execute(
            """
            UPDATE service_requests
            SET current_status = ?
            WHERE service_id = ?
            """,
            (new_status, service_id)
        )

        connection.execute(
            """
            INSERT INTO service_status_history
            (service_id, old_status, new_status, changed_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                service_id,
                current_status,
                new_status,
                datetime.now(timezone.utc).isoformat()
            )
        )

    return {
        "message": "Service status updated successfully",
        "current_status": new_status
    }

def update_service_status(
    service_id: str,
    new_status: str,
):
    allowed_statuses = {
        "Received",
        "Diagnosis",
        "Repair in Progress",
        "Ready for Collection",
        "Collected",
    }

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid repair status.",
        )

    with get_connection() as connection:
        record = connection.execute(
            "SELECT id FROM service_requests WHERE service_id = ?",
            (service_id,),
        ).fetchone()

        if record is None:
            raise HTTPException(
                status_code=404,
                detail="Service request not found.",
            )

        connection.execute(
            """
            UPDATE service_requests
            SET current_status = ?
            WHERE service_id = ?
            """,
            (new_status, service_id),
        )

    return {
        "message": "Repair status updated successfully",
        "service_id": service_id,
        "current_status": new_status,
    }



@app.get("/services/{service_id}/history")
def get_service_history(service_id: str):

    with get_connection() as connection:

        # Check whether the service exists
        service = connection.execute(
            """
            SELECT service_id
            FROM service_requests
            WHERE service_id = ?
            """,
            (service_id,)
        ).fetchone()

        if service is None:
            raise HTTPException(
                status_code=404,
                detail="Service request not found"
            )

        # Retrieve status history
        records = connection.execute(
            """
            SELECT old_status, new_status, changed_at
            FROM service_status_history
            WHERE service_id = ?
            ORDER BY id ASC
            """,
            (service_id,)
        ).fetchall()

    return {
        "service_id": service_id,
        "history": [dict(record) for record in records]
    }
