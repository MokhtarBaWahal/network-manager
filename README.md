# Unified Network Management Platform

A centralized dashboard for managing and monitoring multiple Starlink dishes and MikroTik routers.

## Features

- **Multi-Device Management**: Control 5-50 Starlink dishes and MikroTik routers from a single dashboard
- **Real-Time Monitoring**: View device status, performance metrics, and connectivity
- **Remote Control**: Restart devices, change WiFi settings, configure routers
- **Automation**: Schedule automated tasks and routine maintenance
- **Historical Data**: Track performance trends and generate reports
- **User Management**: Role-based access control for team members

## Architecture

```
Frontend (React/Vue) → FastAPI Backend → Device Drivers (Starlink/MikroTik)
                                       ↓
                                   Database
```

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy
- **Database**: PostgreSQL/SQLite
- **Frontend**: React/Vue (to be implemented)
- **Deployment**: Docker, Docker Compose

## Project Structure

```
network-manager/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── modules/       # Device drivers (starlink, mikrotik)
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── core/          # Config, database, security
│   │   └── main.py        # FastAPI app
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/              # React/Vue dashboard (to be implemented)
└── docker-compose.yml
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

---

### Option 1: Run with Docker (Recommended)

```bash
docker-compose up --build
```

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

### Option 2: Run Locally

#### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Start the backend
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000
API docs at http://localhost:8000/docs

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Frontend runs at http://localhost:5173

---

### Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./network_manager.db` | Database connection string |
| `SECRET_KEY` | *(change this!)* | JWT signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token expiry in minutes |

For more backend details, see [backend/README.md](./backend/README.md).
