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

See [backend/README.md](./backend/README.md) for setup instructions.
