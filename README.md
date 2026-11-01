# Mobile Servicing System

A full-stack mobile phone servicing management application built using Python, FastAPI, Streamlit and SQLite.

## 1. Project Overview

The Mobile Servicing System helps manage mobile phone repair requests and track their repair progress.

Customers can track their service requests using a Service ID or Case ID.

The application also maintains a service status history to record changes throughout the repair process.

## 2. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | REST API development |
| Streamlit | Frontend interface |
| SQLite | Database |
| Pydantic | Request data validation |
| Requests | Frontend API communication |
| Pytest | Automated testing |
| Uvicorn | Backend server |

## 3. Main Features

- Create mobile service requests.
- Generate unique Service IDs.
- Track services using Service ID or Case ID.
- View all service requests.
- Update repair status.
- Validate repair status transitions.
- Maintain service status history.
- Display service dashboard information.
- Automated API testing.

## 4. Repair Status Workflow

The application follows this status sequence:

Received → Diagnosis → Repair in Progress → Ready for Collection → Collected

Invalid status transitions are rejected.

## 5. Project Structure

```text
MOBILE SERVICING SYSTEM/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── seed_data.py
│   ├── tracking.py
│   └── mobile_servicing.db
│
├── frontend/
│   └── app.py
│
├── tests/
│   └── test_api.py
│
├── requirements.txt
└── README.md
```

## 6. Installation

Clone or download the project.

Open the project directory in Command Prompt.

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 7. Run the Application

Start the FastAPI backend:

```bash
python -m uvicorn backend.main:app --reload
```

API documentation:

http://127.0.0.1:8000/docs

Start the Streamlit frontend in a second terminal:

```bash
python -m streamlit run frontend/app.py
```

## 8. Database

The project uses SQLite.

Main database tables:

**service_requests**
- Service ID
- Case ID
- Device model
- Issue description
- Current status
- Received date

**service_status_history**
- Service ID
- Old status
- New status
- Changed timestamp

## 9. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API welcome message |
| GET | `/health` | Health check |
| GET | `/track/{identifier}` | Track a service |
| GET | `/services` | View service requests |
| POST | `/services` | Create a service request |
| PATCH | `/services/{service_id}/status` | Update repair status |
| GET | `/services/{service_id}/history` | View service history |

## 10. Automated Testing

Run tests using:

```bash
python -m pytest -v
```

The project currently has 14 passing automated tests.

## 11. Learning Outcomes

Through this project, I practised:

- Python application development.
- REST API development using FastAPI.
- Frontend development using Streamlit.
- SQLite database operations.
- API integration.
- Data validation.
- Status transition validation.
- Audit logging.
- Automated testing using pytest.
- Error handling.

## 12. 🌐 Live Demo

**Try the application here:**

[🚀 Mobile Servicing System – Live Website](https://mobile-servicing-system.streamlit.app/)

**Backend API Documentation:**

[FastAPI Swagger UI](https://mobile-servicing-system-api.onrender.com/docs)

**GitHub Repository:**

[View Source Code](https://github.com/SaiKalyan738/mobile-servicing-system)

> The application is publicly accessible. No login is required. Please note that this is a portfolio demonstration project and uses free-tier hosting.

## 13. 📸 Application Screenshots

Dashboard

Create Service Request

Track Service

Service History

